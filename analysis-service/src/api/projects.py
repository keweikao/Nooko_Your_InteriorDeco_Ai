from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional, AsyncGenerator, Tuple
from pydantic import BaseModel
import os
import uuid
from datetime import datetime, timezone
import io
import asyncio
import json
import logging
import re
from pathlib import Path

from google.cloud import storage, pubsub_v1, firestore
import openpyxl
import PyPDF2

logger = logging.getLogger(__name__)

# Configuration for GCS and Pub/Sub
GCS_BUCKET_NAME = os.getenv("GCS_UPLOAD_BUCKET", "houseiq-project-quotes")
PUBSUB_TOPIC_ID = os.getenv("PUBSUB_PROCESSING_TOPIC", "quote-analysis-requests")
GCP_PROJECT_ID = os.getenv("PROJECT_ID", "houseiq-yourinteriordeco-ai")

from src.agents.client_manager_v2 import ClientManagerAgentV2, QuestionCategory
from src.agents.construction_translator import ConstructionTranslator
from src.agents.contractor_agent import ContractorAgent
from src.agents.designer_agent import DesignerAgent
from src.services.pdf_service import generate_pdf_report
from src.services.llm_service import mock_llm_service
from src.services.gemini_service import gemini_service
from src.models.project import (
    ConversationState,
    ConversationMessage,
    ExtractedSpecifications,
    ConversationStage,
    ProjectBrief,
    Booking,
)
from src.services.conversation_service import ConversationService
from src.services.spec_tracking import SpecTracker
from src.services.database_service import db_service

router = APIRouter()

# Initialize agents
client_manager = ClientManagerAgentV2()
translator = ConstructionTranslator()
conversation_service = ConversationService()
spec_tracker = SpecTracker()
contractor_agent = ContractorAgent()
designer_agent = DesignerAgent()

UPLOAD_ROOT = Path(os.getenv("QUOTE_UPLOAD_DIR", "./uploaded_quotes"))
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
# Request/Response Models
class CreateProjectResponse(BaseModel):
    project_id: str
    status: str
    created_at: str
    welcome_message: str

class StartConversationResponse(BaseModel):
    project_id: str
    current_question: Dict[str, Any]
    progress: Dict[str, Any]
    agent_name: str = "HouseIQ" # Add agent_name

class AnswerRequest(BaseModel):
    question_id: str
    answer: Any

class AnswerResponse(BaseModel):
    accepted: bool
    next_question: Optional[Dict[str, Any]]
    is_complete: bool
    message: Optional[str]
    agent_name: str = "HouseIQ" # Add agent_name

class TranslateNeedRequest(BaseModel):
    consumer_need: str
    context: Optional[Dict[str, Any]] = None

# 新增模型定義
class InitConversationResponse(BaseModel):
    conversationId: str
    agent: Dict[str, Any]
    initialMessage: str
    timestamp: int

class MessageChunkEvent(BaseModel):
    chunk: str
    isComplete: bool
    metadata: Optional[Dict[str, Any]] = None

class CompleteConversationResponse(BaseModel):
    summary: str
    briefing: Dict[str, Any]
    analysis: Dict[str, Any]

class BookingRequest(BaseModel):
    name: str
    phone: str
    region: Optional[str] = None # 新增 region 欄位

class FeedbackRequest(BaseModel):
    satisfaction_score: int
    helpfulness_score: int

@router.post("/projects/{project_id}/feedback")
async def submit_feedback(project_id: str, request: FeedbackRequest) -> Dict[str, Any]:
    """
    接收使用者對互動和規格書的滿意度回饋。
    Input: projectId + FeedbackRequest；Output: 成功訊息。
    """
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    conversation = await conversation_service.get_project_conversation(project_id)
    if conversation:
        await conversation_service.log_event(
            conversation["conversation_id"],
            "user_feedback_submitted",
            description="User submitted feedback scores.",
            payload={
                "satisfaction_score": request.satisfaction_score,
                "helpfulness_score": request.helpfulness_score
            }
        )
    
    # 儲存回饋到 project document 或單獨的 collection
    await db_service.update_project(
        project_id,
        {
            "feedback": {
                "satisfaction_score": request.satisfaction_score,
                "helpfulness_score": request.helpfulness_score,
                "timestamp": firestore.SERVER_TIMESTAMP
            }
        }
    )

    return {
        "status": "success",
        "message": f"Feedback submitted for project {project_id}"
    }



@router.post("/projects", response_model=CreateProjectResponse)
async def create_project() -> CreateProjectResponse:
    """Create new project"""
    project_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    await conversation_service.create_project_in_db(project_id)

    return CreateProjectResponse(
        project_id=project_id,
        status="created",
        created_at=created_at,
        welcome_message="歡迎來到 HouseIQ 裝潢 AI 夥伴！讓我們一起規劃您的理想空間。"
    )

@router.get("/projects/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    """Get project details"""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Since project data is now in Firestore, we can return a simplified response
    # or fetch the details from Firestore if needed.
    return {"project_id": project_id, "status": "found_in_db"}

@router.post("/projects/{project_id}/book")
async def book_measurement(project_id: str, request: BookingRequest) -> Dict[str, Any]:
    """
    簡化預約 API：前端提交姓名、電話和地區，後端將資料寫入 Firestore (db_service)。
    Input: projectId + BookingRequest；Output: 成功訊息與保存的資料。
    """
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    booking = Booking(project_id=project_id, name=request.name, contact=request.phone, region=request.region)
    await db_service.save_booking(booking)

    conversation = await conversation_service.get_project_conversation(project_id)
    if conversation:
        await conversation_service.log_event(
            conversation["conversation_id"],
            "booking_created",
            description="User requested onsite measurement.",
            payload={"name": request.name, "phone": request.phone, "region": request.region}
        )

    return {
        "status": "success",
        "message": f"Booking confirmed for project {project_id}",
        "booking": booking.model_dump()
    }


@router.post("/projects/{project_id}/upload")
async def upload_quote(project_id: str, file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Receives a user-uploaded quote, performs a quick validation, saves it to GCS,
    and dispatches a message to Pub/Sub for background processing.
    """
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Supported content types
    supported_types = {
        "application/pdf",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/jpeg",
        "image/png",
    }
    if file.content_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.content_type}")

    contents = await file.read()
    await file.seek(0) # Reset file pointer after reading

    # --- Quick Pre-flight Check ---
    try:
        if file.content_type == "application/pdf":
            # Try to read the PDF metadata
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF file is empty or corrupted.")
        elif "spreadsheetml" in file.content_type or "ms-excel" in file.content_type:
            # Try to load the workbook
            openpyxl.load_workbook(io.BytesIO(contents))
    except Exception as e:
        logger.warning(f"Pre-flight check failed for {file.filename}: {e}")
        raise HTTPException(status_code=400, detail="File appears to be corrupted or is an invalid format.")

    # --- Upload to GCS ---
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        
        safe_name = file.filename or "upload"
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        destination_blob_name = f"{project_id}/{timestamp}_{safe_name}"
        
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(contents, content_type=file.content_type)
        gcs_uri = f"gs://{GCS_BUCKET_NAME}/{destination_blob_name}"
        logger.info(f"File {file.filename} for project {project_id} uploaded to {gcs_uri}")
    except Exception as e:
        logger.error(f"Failed to upload to GCS for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not save file to cloud storage.")

    # --- Dispatch to Pub/Sub ---
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(GCP_PROJECT_ID, PUBSUB_TOPIC_ID)
        
        message_data = {
            "project_id": project_id,
            "gcs_uri": gcs_uri,
            "original_filename": safe_name,
            "content_type": file.content_type,
            "size_bytes": len(contents),
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        future = publisher.publish(topic_path, data=json.dumps(message_data).encode("utf-8"))
        future.result()  # Wait for publish to complete
        logger.info(f"Message published to {topic_path} for project {project_id}")
    except Exception as e:
        logger.error(f"Failed to publish to Pub/Sub for project {project_id}: {e}")
        # Here we might want to add cleanup logic, e.g., delete the file from GCS
        raise HTTPException(status_code=500, detail="Could not dispatch file for analysis.")

    # --- Log Event and Return Success ---
    conversation = await conversation_service.get_project_conversation(project_id)
    if conversation:
        await conversation_service.log_event(
            conversation["conversation_id"],
            "quote_upload_queued",
            description=f"User uploaded file {safe_name} for background analysis.",
            payload={"gcs_uri": gcs_uri}
        )

    return {"message": "檔案上傳成功，排隊分析中..."}

@router.post("/projects/{project_id}/conversation/start", response_model=StartConversationResponse)
async def start_conversation(project_id: str) -> StartConversationResponse:
    """Start V2 questionnaire conversation"""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # NOTE: The following logic is part of the old V1 questionnaire flow
    # and still relies on an in-memory-like structure.
    # This should be refactored if V1 is to be fully supported with Firestore.

    # Create new client manager for this project
    manager = ClientManagerAgentV2()

    # Get first question
    first_question = manager.get_next_question({})

    if not first_question:
        raise HTTPException(status_code=500, detail="Failed to initialize questionnaire")

    # Convert Question object to dict
    first_question_dict = {
        "id": first_question.id,
        "category": first_question.category,
        "question_text": first_question.question_text,
        "question_type": first_question.question_type,
        "options": first_question.options,
        "visual_references": [
            {
                "image_url": vr.image_url,
                "description": vr.description,
                "style_tags": vr.style_tags,
                "price_indicator": vr.price_indicator
            }
            for vr in (first_question.visual_references or [])
        ],
        "why_we_ask": first_question.why_we_ask,
        "helper_text": first_question.helper_text,
        "empathy_message": first_question.empathy_message,
        "can_skip": first_question.can_skip,
        "skip_suggestion": first_question.skip_suggestion
    }

    # This part is problematic as it tries to write to a non-existent in-memory db
    # projects_db[project_id]["questionnaire_state"] = {
    #     "current_question_id": first_question.id,
    #     "answered_questions": [],
    #     "current_category": first_question.category,
    #     "manager": manager  # Store manager instance
    # }

    progress = {
        "total_required": 10,  # Approximate
        "answered": 0,
        "percentage": 0
    }

    return StartConversationResponse(
        project_id=project_id,
        current_question=first_question_dict,
        progress=progress,
        agent_name="HouseIQ"
    )

@router.post("/projects/{project_id}/conversation/answer", response_model=AnswerResponse)
async def submit_answer(project_id: str, answer_request: AnswerRequest) -> AnswerResponse:
    """Submit answer and get next question"""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]

    # Store answer
    project["answers"][answer_request.question_id] = answer_request.answer

    # Update answered questions list
    if answer_request.question_id not in project["questionnaire_state"]["answered_questions"]:
        project["questionnaire_state"]["answered_questions"].append(answer_request.question_id)

    # Get manager instance
    manager = project["questionnaire_state"].get("manager")
    if not manager:
        manager = ClientManagerAgentV2()
        project["questionnaire_state"]["manager"] = manager

    # Update manager's answers
    manager.answers[answer_request.question_id] = answer_request.answer

    # Get next question
    next_question = manager.get_next_question(manager.answers)

    is_complete = next_question is None

    # Convert next question to dict if exists
    next_question_dict = None
    if next_question:
        next_question_dict = {
            "id": next_question.id,
            "category": next_question.category,
            "question_text": next_question.question_text,
            "question_type": next_question.question_type,
            "options": next_question.options,
            "visual_references": [
                {
                    "image_url": vr.image_url,
                    "description": vr.description,
                    "style_tags": vr.style_tags,
                    "price_indicator": vr.price_indicator
                }
                for vr in (next_question.visual_references or [])
            ],
            "why_we_ask": next_question.why_we_ask,
            "helper_text": next_question.helper_text,
            "empathy_message": next_question.empathy_message,
            "can_skip": next_question.can_skip,
            "skip_suggestion": next_question.skip_suggestion
        }

        project["questionnaire_state"]["current_question_id"] = next_question.id
        project["questionnaire_state"]["current_category"] = next_question.category

    return AnswerResponse(
        accepted=True,
        next_question=next_question_dict,
        is_complete=is_complete,
        message="感謝您的回答！" if not is_complete else "問卷已完成，正在為您準備裝修建議...",
        agent_name="HouseIQ"
    )

@router.post("/projects/{project_id}/translate-need")
async def translate_consumer_need(
    project_id: str,
    request: TranslateNeedRequest
) -> Dict[str, Any]:
    """Translate consumer need into construction plan"""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Get construction plan
    plan = translator.translate(
        consumer_need=request.consumer_need,
        context=request.context or {}
    )

    # Convert to dict for JSON response
    return {
        "consumer_request": plan.consumer_request,
        "translated_items": [
            {
                "name": item.name,
                "why_needed": item.why_needed,
                "must_do": item.must_do,
                "alternatives": item.alternatives,
                "dependencies": item.dependencies,
                "risks_if_skip": item.risks_if_skip,
                "professional_tips": item.professional_tips
            }
            for item in plan.translated_items
        ],
        "construction_sequence": plan.construction_sequence,
        "important_notes": plan.important_notes,
        "budget_factors": plan.budget_factors,
        "timeline_factors": plan.timeline_factors
    }

@router.post("/projects/{project_id}/generate-spec")
async def generate_construction_spec(project_id: str) -> Dict[str, Any]:
    """Generate full construction specification from questionnaire answers"""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    project = projects_db[project_id]
    answers = project.get("answers", {})

    # Get manager instance
    manager = project["questionnaire_state"].get("manager")
    if not manager:
        raise HTTPException(status_code=400, detail="Questionnaire not started")

    # Generate summary
    summary = manager.generate_questionnaire_summary(answers)

    # Translate to construction spec
    construction_spec = manager.translate_to_construction_spec(answers)

    return {
        "project_id": project_id,
        "questionnaire_summary": summary,
        "construction_spec": construction_spec,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.get("/projects/{project_id}/analysis-messages")
async def get_analysis_messages(project_id: str) -> List[str]:
    """Returns a list of messages to display during AI analysis."""
    # For POC, return static messages. In a real scenario, these might be dynamic.
    return [
        "正在為您交叉比對超過 5,000 項工種的市場均價...",
        "檢查您的報價單中是否存在常見的工程遺漏項目...",
        "根據您的需求，智慧分析最適合的材料與工法...",
        "評估潛在風險，確保您的裝潢過程順利無憂...",
        "生成客製化的設計建議與風格參考圖...",
        "整合專業統包商與設計師的建議，為您打造專屬藍圖..."
    ]

class ReportRequest(BaseModel):
    analysis_data: Dict[str, Any]

@router.post("/projects/{project_id}/generate-pdf-report")
async def generate_pdf_report_endpoint(project_id: str, request: ReportRequest):
    """Generate and return a PDF report."""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    pdf_bytes = generate_pdf_report(request.analysis_data)

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")


# ============================================================================
# Plan B: Real Conversation System - SSE Endpoints
# ============================================================================

@router.post("/projects/{project_id}/conversation/init", response_model=InitConversationResponse)
async def init_conversation(project_id: str) -> InitConversationResponse:
    """
    Purpose: Initialize or resume a conversation for a project.
             If a quote has been uploaded and processed, it triggers an analysis and
             returns a tailored initial message. Otherwise, it returns a generic welcome.

    Input:
        project_id (str): The unique identifier for the project.

    Output:
        InitConversationResponse: Contains the conversation ID, agent info, and the initial message.
    """
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Create a new conversation session
    conversation_id = f"conv-{uuid.uuid4()}"
    await conversation_service.create_conversation(conversation_id, project_id)
    await conversation_service.log_event(
        conversation_id,
        "conversation_initialized",
        description="Conversation created via init endpoint."
    )
    
    # Initialize spec tracking in Firestore
    await conversation_service.update_extracted_specs(conversation_id, spec_tracker.empty_state())
    await conversation_service.update_missing_fields(conversation_id, spec_tracker.initial_missing_fields())
    await conversation_service.update_conversation_stage(conversation_id, "greeting", 0)

    # Agent Information
    agent = {
        "name": "HouseIQ",
        "avatar": "👨‍💼",
        "status": "idle"
    }

    initial_message = ""
    
    # Check if processed quote content exists
    project_data = await db_service.get_project(project_id)
    quote_content = project_data.get("original_quote_content")

    if quote_content:
        logger.info(f"Found original_quote_content for project {project_id}. Analyzing...")
        # If quote exists, analyze it to generate the first message
        analysis_result = await gemini_service.analyze_quote_and_generate_initial_response(quote_content)
        
        if analysis_result and "analysis" in analysis_result:
            # Save the analysis to the project
            await db_service.update_project(project_id, {"quote_analysis": analysis_result["analysis"]})
            initial_message = analysis_result.get("initial_response", "")
            await conversation_service.log_event(
                conversation_id,
                "quote_analysis_completed",
                description="Initial quote analysis successful.",
                payload=analysis_result["analysis"]
            )
        else:
            logger.warning(f"Quote analysis failed for project {project_id}. Falling back.")
            initial_message = "抱歉，分析您的報價單時發生了點問題。不過沒關係，我們可以先從聊聊您的需求開始嗎？"

    if not initial_message:
        # Fallback for when there's no quote or analysis fails
        initial_message = "哈囉！我是 HouseIQ，很高興協助您規劃空間。可以先跟我分享這次想改善哪些區域或期待的重點嗎？我會一步步了解您的想法，並告知哪些資訊還需要補充。"

    return InitConversationResponse(
        conversationId=conversation_id,
        agent=agent,
        initialMessage=initial_message,
        timestamp=int(datetime.utcnow().timestamp() * 1000)
    )


async def generate_agent_response(
    message: str,
    conversation_id: str,
    conversation_history: List[Dict[str, Any]] = None,
    extracted_specs: Dict[str, Any] = None
) -> AsyncGenerator[Tuple[str, Optional[Dict[str, Any]]], None]:
    """
    Purpose: 使用 Gemini LLM 生成 Agent 回應，並支援流式輸出。
             此函式整合了 Gemini API 進行智慧對話和規格提取。
             它會將 AI 的回應分塊 (chunk) 傳回，並可能包含規格更新。

    Input:
        message (str): 使用者當前輸入的訊息。
        conversation_id (str): 當前對話的唯一識別碼。
        conversation_history (List[Dict[str, Any]], optional): 過去的對話歷史，用於提供上下文給 LLM。
                                                                來源為 Firestore。
        extracted_specs (Dict[str, Any], optional): 已從對話中提取的規格，用於引導 LLM。
                                                     來源為 Firestore。

    Output:
        AsyncGenerator[Tuple[str, Optional[Dict[str, Any]]], None]:
            一個非同步生成器，每次產生一個元組 (text_chunk, spec_update)。
            text_chunk (str): AI 回應的文字片段。
            spec_update (Dict[str, Any], optional): 從 AI 回應中提取的潛在規格更新。
            此輸出會被 `send_message_stream` 函式消費，並透過 SSE 傳送給前端。
    """

    if conversation_history is None:
        conversation_history = []
    if extracted_specs is None:
        extracted_specs = {}

    try:
        # Call Gemini service to generate a response with streaming
        context = {
            "conversation_id": conversation_id,
            "role": "houseiq",
            "extracted_specs": extracted_specs
        }

        # Use Gemini service streaming response
        async for text_chunk, spec_update in gemini_service.generate_response_stream(
            message=message,
            conversation_history=conversation_history,
            context=context
        ):
            yield (text_chunk, spec_update)

    except Exception as e:
        logger.error(f"Error generating response with Gemini: {e}")
        # Fallback to mock response if Gemini fails
        fallback_msg = "抱歉，暫時無法連接到 AI 服務。請稍後再試。"
        for char in fallback_msg:
            yield (char, None)
            await asyncio.sleep(0.01)


@router.get("/projects/{project_id}/conversation/message-stream")
async def send_message_stream(
    project_id: str,
    message: str = Query(...),
) -> StreamingResponse:
    """
    Purpose: Establishes a Server-Sent Events (SSE) endpoint to handle real-time,
             bidirectional conversation between the user and the AI agent.
    Input:
        project_id (str): The project's unique identifier.
        message (str): The user's message.
    Output:
        StreamingResponse: A stream of events including text chunks, spec updates, and image URLs.
    """
    conversation = await conversation_service.get_project_conversation(project_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found for this project")
    
    conversation_id = conversation["conversation_id"]

    async def event_generator():
        try:
            # Initial setup
            conversation_history = await conversation_service.get_conversation_history(conversation_id)
            extracted_specs = await conversation_service.get_current_specs(conversation_id) or {}
            tracking_snapshot = spec_tracker.evaluate(extracted_specs)
            current_stage = tracking_snapshot["stage"]
            current_progress = tracking_snapshot["progress"]
            current_missing_fields = tracking_snapshot["missing_fields"]

            # Save user message
            await conversation_service.save_message(conversation_id, "user", message)
            await conversation_service.log_event(
                conversation_id, "user_message_received", source="user", description=message[:200]
            )

            # Generate and stream agent response
            response_text = ""
            await conversation_service.log_event(
                conversation_id, "agent_stream_started", source="agent", payload={"model": getattr(gemini_service, "model_name", "unknown")}
            )
            
            context = {
                "project_id": project_id,
                "conversation_id": conversation_id,
                "role": "houseiq",
                "extracted_specs": extracted_specs
            }

            async for text_chunk, spec_update in gemini_service.generate_response_stream(
                message=message,
                conversation_history=conversation_history,
                context=context
            ):
                if text_chunk:
                    response_text += text_chunk
                    event_data = {
                        "chunk": text_chunk, "isComplete": False,
                        "metadata": {"stage": current_stage, "progress": current_progress, "missingFields": current_missing_fields[:3]}
                    }
                    yield f"event: message_chunk\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

                if spec_update:
                    # --- Handle Image Generation Event (Task 2.3.3) ---
                    image_url = spec_update.pop("generated_image_url", None)
                    if image_url:
                        await conversation_service.save_message(
                            conversation_id, "agent", image_url, message_type="image"
                        )
                        await conversation_service.log_event(
                            conversation_id, "agent_generated_image", source="agent", payload={"url": image_url}
                        )

                    # --- Handle other spec updates ---
                    if spec_update: # If there are still items left after popping the image url
                        tracking_snapshot = spec_tracker.merge(extracted_specs, spec_update)
                        if tracking_snapshot["changed"]:
                            extracted_specs = tracking_snapshot["state"]
                            current_stage = tracking_snapshot["stage"]
                            current_progress = tracking_snapshot["progress"]
                            current_missing_fields = tracking_snapshot["missing_fields"]
                            await conversation_service.update_extracted_specs(conversation_id, extracted_specs)
                            await conversation_service.update_missing_fields(conversation_id, current_missing_fields)
                            await conversation_service.update_conversation_stage(conversation_id, current_stage, current_progress)
                            await conversation_service.log_event(
                                conversation_id, "spec_updated", source="agent", payload={"fields": list(spec_update.keys())}
                            )

            # Save the full text response (cleaned of any commands)
            final_response_text = re.sub(r'\[GENERATE_IMAGE:.*?\]', '', response_text).strip()
            if final_response_text:
                await conversation_service.save_message(conversation_id, "agent", final_response_text)

            # Send completion event
            final_snapshot = spec_tracker.evaluate(extracted_specs)
            complete_event = {
                "chunk": "", "isComplete": True,
                "metadata": {
                    "stage": final_snapshot["stage"], "progress": final_snapshot["progress"],
                    "missingFields": final_snapshot["missing_fields"], "extracted_specs": extracted_specs or {}
                }
            }
            yield f"event: message_chunk\n"
            yield f"data: {json.dumps(complete_event, ensure_ascii=False)}\n\n"
            await conversation_service.log_event(
                conversation_id, "agent_stream_completed", source="agent", payload={"response_length": len(final_response_text)}
            )

        except Exception as e:
            logger.error(f"Error in stream: {e}")
            # Error handling...

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"})


@router.post("/projects/{project_id}/conversation/complete", response_model=CompleteConversationResponse)
async def complete_conversation(project_id: str) -> CompleteConversationResponse:
    """
    Purpose: Finalize the conversation, generate all analysis, and return the complete solution package.
    Input: project_id (str)
    Output: CompleteConversationResponse containing summary, brief, and the full analysis.
    """
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    conversation = await conversation_service.get_project_conversation(project_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found for this project")

    conversation_id = conversation["conversation_id"]
    
    # Fetch all necessary data from Firestore
    project_data = await db_service.get_project(project_id)
    specs = project_data.get("extracted_specs", {})
    quote_analysis = project_data.get("quote_analysis", {})

    # Validate conversation completion
    evaluation = spec_tracker.evaluate(specs)
    if evaluation["missing_fields"]:
        raise HTTPException(
            status_code=400,
            detail={"message": "對話尚未完成，仍有關鍵資訊缺失。", "missing_fields": evaluation["missing_fields"]}
        )

    # Build the main project brief and summary
    briefing_model = _build_project_brief(project_id, specs)
    summary = _build_summary_from_brief(briefing_model)
    analysis = _build_analysis_from_brief(briefing_model)
    analysis["original_quote_analysis"] = quote_analysis # Add initial quote analysis to the final package

    # --- Generate Budget Trade-off Suggestions (Task 2.2) ---
    budget_suggestions = await gemini_service.generate_budget_tradeoff_suggestions(
        extracted_specs=specs,
        quote_analysis=quote_analysis
    )
    if budget_suggestions:
        analysis["budget_tradeoffs"] = budget_suggestions
        await conversation_service.log_event(
            conversation_id,
            "budget_analysis_completed",
            description="Budget trade-off suggestions generated."
        )

    # Update project with the core brief and summary first
    await db_service.update_project(
        project_id,
        {
            "project_brief": briefing_model.model_dump(),
            "conversation_summary": summary,
            "budget_tradeoff_analysis": budget_suggestions or {}
        }
    )

    # --- Multi-Agent Collaboration ---
    await conversation_service.log_event(
        conversation_id,
        "handoff_started",
        description="Dispatching project brief to contractor/designer agents."
    )
    contractor_quote = await contractor_agent.run(briefing_model)
    designer_output = await designer_agent.run(briefing_model)

    # Update project with agent outputs
    await db_service.update_project_with_quote(project_id, contractor_quote)
    await db_service.update_project_with_rendering(project_id, designer_output.get("image_url", ""))

    # Add agent outputs to the final analysis package
    analysis["quote"] = contractor_quote.model_dump()
    analysis["rendering_url"] = designer_output.get("image_url")

    await conversation_service.log_event(
        conversation_id,
        "conversation_completed",
        description="Conversation marked as complete and all analyses generated."
    )

    return CompleteConversationResponse(
        summary=summary,
        briefing=briefing_model.model_dump(),
        analysis=analysis
    )

def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 string to datetime with timezone awareness."""
    if not value:
        return None
    try:
        normalized = value.strip()
        if normalized.endswith("Z"):
            normalized = normalized.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid 'since' timestamp. Use ISO 8601 format.")


@router.get("/projects/{project_id}/conversation/{conversation_id}/events")
async def get_conversation_events(
    project_id: str,
    conversation_id: str,
    limit: int = 50,
    severity: Optional[str] = None,
    since: Optional[str] = None
) -> Dict[str, Any]:
    """取得指定對話的事件日誌"""
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    conversation = await conversation_service.get_conversation(conversation_id)
    if not conversation or conversation.get("project_id") != project_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    since_dt = _parse_iso_datetime(since)
    events = await conversation_service.get_events(
        conversation_id,
        limit=min(max(limit, 1), 200),
        severity=severity,
        since=since_dt
    )

    serialized_events = []
    for event in events:
        timestamp = event.get("timestamp")
        if isinstance(timestamp, datetime):
            ts = timestamp.astimezone(timezone.utc).isoformat()
        else:
            ts = None
        serialized_events.append({
            "id": event.get("id"),
            "type": event.get("type"),
            "severity": event.get("severity"),
            "source": event.get("source"),
            "description": event.get("description"),
            "payload": event.get("payload"),
            "timestamp": ts
        })

    return {
        "conversationId": conversation_id,
        "projectId": project_id,
        "events": serialized_events
    }


def _spec_value(specs: Dict[str, Any], field_id: str, default=None):
    entry = specs.get(field_id)
    if isinstance(entry, dict):
        return entry.get("value", default)
    return entry or default

def _ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v not in (None, "")]
    return [str(value)]


def _build_project_brief(project_id: str, specs: Dict[str, Any]) -> ProjectBrief:
    style_pref = _ensure_list(_spec_value(specs, "style_preference"))
    if not style_pref:
        style_pref = ["待定風格"]
    key_requirements = (
        _ensure_list(_spec_value(specs, "focus_areas"))
        + _ensure_list(_spec_value(specs, "special_requirements"))
        + _ensure_list(_spec_value(specs, "risk_flags"))
    )
    if not key_requirements:
        key_requirements = ["持續補充需求資訊"]

    user_profile = {
        "name": _spec_value(specs, "user_name"),
        "house_type": _spec_value(specs, "project_type"),
        "space_usage": _spec_value(specs, "space_usage"),
        "family_profile": _spec_value(specs, "family_profile"),
        "house_condition": _spec_value(specs, "house_condition"),
        "focus_areas": _ensure_list(_spec_value(specs, "focus_areas")),
        "total_area": _spec_value(specs, "total_area"),
        "budget": _spec_value(specs, "budget_range"),
        "timeline": _spec_value(specs, "timeline"),
    }

    brief = ProjectBrief(
        project_id=project_id,
        user_profile=user_profile,
        style_preferences=style_pref,
        key_requirements=key_requirements,
        original_quote_analysis={}
    )
    return brief


def _build_summary_from_brief(brief: ProjectBrief) -> str:
    profile = brief.user_profile or {}
    name = profile.get("name") or "客戶"
    scope = profile.get("house_type") or "裝修專案"
    areas = profile.get("focus_areas") or ["多個區域"]
    budget = profile.get("budget") or "尚未確認"
    style_pref = ", ".join(brief.style_preferences) if brief.style_preferences else "待定風格"

    return (
        f"{name}，感謝您提供的資訊。我已整理出此次 {scope} 的重點：\n"
        f"- 主要施作區域：{', '.join(areas)}\n"
        f"- 預算範圍：{budget}\n"
        f"- 偏好風格：{style_pref}\n\n"
        "接下來我會把這份需求交給統包與設計師團隊，產出完整報價與概念渲染圖。"
    )


def _build_analysis_from_brief(brief: ProjectBrief) -> Dict[str, Any]:
    profile = brief.user_profile or {}
    key_requirements = brief.key_requirements or []

    key_insights = []
    if profile.get("timeline"):
        key_insights.append("對時程有明確期待，需要妥善控管工期。")
    if any("風險" in req for req in key_requirements):
        key_insights.append("偵測到潛在風險，需要在施工前評估。")
    if brief.style_preferences:
        key_insights.append(f"風格主軸為 {', '.join(brief.style_preferences)}，需統一材質與色系。")

    recommendations = [
        "完成統包與設計師的產出後，與客戶再次複盤重點需求。",
        "安排現場丈量，以確認坪數與現況細節。"
    ]

    next_steps = [
        "整合統包報價與設計渲染圖",
        "輸出可分享的專案簡報",
        "啟動丈量與後續溝通"
    ]

    return {
        "summary": "依據目前資訊已完成專案簡報雛型，可進入統包與設計師協作階段。",
        "key_insights": key_insights,
        "recommendations": recommendations,
        "next_steps": next_steps
    }


@router.get("/projects/{project_id}/analysis-result")
async def get_analysis_result(project_id: str) -> Dict[str, Any]:
    """
    整合前端成果頁需要的資料來源。
    Input: projectId。
    Output: quote/rendering_url/summary，資料來自 db_service（Firestore 或 mock）。
    """
    if not await conversation_service.project_exists(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    project_record = await db_service.get_project(project_id)
    if not project_record:
        raise HTTPException(status_code=404, detail="Result not found")

    quote = project_record.get("generated_quote")
    rendering_url = project_record.get("final_rendering_url")
    summary = project_record.get("conversation_summary")

    if not any([quote, rendering_url, summary]):
        raise HTTPException(status_code=404, detail="Analysis result not available yet")

    return {
        "project_id": project_id,
        "quote": quote,
        "rendering_url": rendering_url,
        "summary": summary
    }
