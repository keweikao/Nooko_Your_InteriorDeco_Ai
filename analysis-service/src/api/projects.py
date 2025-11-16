from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional, AsyncGenerator
from pydantic import BaseModel
import uuid
from datetime import datetime
import io
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

from src.agents.client_manager_v2 import ClientManagerAgentV2, QuestionCategory
from src.agents.construction_translator import ConstructionTranslator
from src.services.pdf_service import generate_pdf_report
from src.services.llm_service import mock_llm_service

router = APIRouter()

# Initialize agents
client_manager = ClientManagerAgentV2()
translator = ConstructionTranslator()

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
    agent_name: str = "Stephen" # Add agent_name

class AnswerRequest(BaseModel):
    question_id: str
    answer: Any

class AnswerResponse(BaseModel):
    accepted: bool
    next_question: Optional[Dict[str, Any]]
    is_complete: bool
    message: Optional[str]
    agent_name: str = "Stephen" # Add agent_name

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

# In-memory storage (will be replaced with Firestore)
projects_db: Dict[str, Dict[str, Any]] = {}
conversations_db: Dict[str, Dict[str, Any]] = {}

@router.post("/projects", response_model=CreateProjectResponse)
async def create_project() -> CreateProjectResponse:
    """Create new project"""
    project_id = str(uuid.uuid4())

    projects_db[project_id] = {
        "id": project_id,
        "status": "created",
        "created_at": datetime.utcnow().isoformat(),
        "questionnaire_state": None,
        "answers": {}
    }

    return CreateProjectResponse(
        project_id=project_id,
        status="created",
        created_at=projects_db[project_id]["created_at"],
        welcome_message="歡迎來到 Nooko 裝潢 AI 夥伴！讓我們一起規劃您的理想空間。"
    )

@router.get("/projects/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    """Get project details"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    return projects_db[project_id]

@router.post("/projects/{project_id}/conversation/start", response_model=StartConversationResponse)
async def start_conversation(project_id: str) -> StartConversationResponse:
    """Start V2 questionnaire conversation"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

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

    projects_db[project_id]["questionnaire_state"] = {
        "current_question_id": first_question.id,
        "answered_questions": [],
        "current_category": first_question.category,
        "manager": manager  # Store manager instance
    }

    progress = {
        "total_required": 10,  # Approximate
        "answered": 0,
        "percentage": 0
    }

    return StartConversationResponse(
        project_id=project_id,
        current_question=first_question_dict,
        progress=progress,
        agent_name="Stephen"
    )

@router.post("/projects/{project_id}/conversation/answer", response_model=AnswerResponse)
async def submit_answer(project_id: str, answer_request: AnswerRequest) -> AnswerResponse:
    """Submit answer and get next question"""
    if project_id not in projects_db:
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
        agent_name="Stephen"
    )

@router.post("/projects/{project_id}/translate-need")
async def translate_consumer_need(
    project_id: str,
    request: TranslateNeedRequest
) -> Dict[str, Any]:
    """Translate consumer need into construction plan"""
    if project_id not in projects_db:
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
    if project_id not in projects_db:
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
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    pdf_bytes = generate_pdf_report(request.analysis_data)

    return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf")


# ============================================================================
# Plan B: Real Conversation System - SSE Endpoints
# ============================================================================

@router.post("/projects/{project_id}/conversation/init", response_model=InitConversationResponse)
async def init_conversation(project_id: str) -> InitConversationResponse:
    """初始化真實對話 - Initialize real conversation with Agent1"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    # 創建新的對話會話
    conversation_id = f"conv-{uuid.uuid4()}"

    conversations_db[conversation_id] = {
        "id": conversation_id,
        "project_id": project_id,
        "messages": [],
        "stage": "greeting",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "answers": {}
    }

    # Agent 信息 - Stephen (客戶經理)
    agent = {
        "name": "Stephen",
        "avatar": "👨‍💼",
        "status": "idle"
    }

    # 初始問候消息
    initial_message = """Hi! I'm Stephen, your dedicated project manager.

I'm here to understand your interior design vision and ensure we create a space that's perfect for you.

What are the main areas you'd like to renovate? Kitchen, bathroom, bedroom, or the entire space?"""

    return InitConversationResponse(
        conversationId=conversation_id,
        agent=agent,
        initialMessage=initial_message,
        timestamp=int(datetime.utcnow().timestamp() * 1000)
    )


async def generate_agent_response(message: str, conversation_id: str) -> AsyncGenerator[str, None]:
    """Generate Agent response with streaming - 生成 Agent 回應流

    Uses mock_llm_service to generate intelligent responses based on user input.
    This can be replaced with real LLM service integration (e.g., Gemini API).
    """

    # Use mock LLM service to generate a contextual response
    prompt = f"As Stephen, a professional interior design project manager, respond to the client's message in a friendly and professional way. Be conversational and ask relevant follow-up questions to understand their needs better.\n\nClient message: {message}\n\nRespond naturally:"

    try:
        # Call mock LLM service to get a response
        response = await mock_llm_service.generate_response(
            prompt=prompt,
            context={"conversation_id": conversation_id, "role": "stephen"}
        )

        # Get response text
        if isinstance(response, dict):
            response_text = response.get("summary", str(response))
        else:
            response_text = str(response)

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        response_text = "I appreciate you sharing that information. Could you tell me more about your renovation goals and preferences?"

    # Stream response character by character
    for char in response_text:
        yield char
        await asyncio.sleep(0.01)  # Adjust streaming speed


@router.post("/projects/{project_id}/conversation/message-stream")
async def send_message_stream(
    project_id: str,
    message: str = Query(...),
) -> StreamingResponse:
    """發送消息並通過 SSE 流式接收 Agent 回應 - Send message and receive streaming response"""

    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    async def event_generator():
        try:
            # 生成 Agent 回應
            response_text = ""
            async for char in generate_agent_response(message, project_id):
                response_text += char

                # 每 3 個字符發送一次事件
                if len(response_text) % 3 == 0:
                    event_data = {
                        "chunk": response_text[-3:] if len(response_text) >= 3 else response_text,
                        "isComplete": False,
                        "metadata": {
                            "stage": "assessment",
                            "progress": 25
                        }
                    }
                    yield f"event: message_chunk\n"
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0)

            # 發送最後的部分
            remaining = response_text[-(len(response_text) % 3):] if len(response_text) % 3 != 0 else ""
            if remaining:
                event_data = {
                    "chunk": remaining,
                    "isComplete": False,
                    "metadata": {
                        "stage": "assessment",
                        "progress": 25
                    }
                }
                yield f"event: message_chunk\n"
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

            # 發送完成事件
            complete_event = {
                "chunk": "",
                "isComplete": True,
                "metadata": {
                    "stage": "assessment",
                    "progress": 25
                }
            }
            yield f"event: message_chunk\n"
            yield f"data: {json.dumps(complete_event, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"Error in stream: {e}")
            error_event = {
                "error": str(e),
                "isComplete": True
            }
            yield f"event: error\n"
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@router.post("/projects/{project_id}/conversation/complete", response_model=CompleteConversationResponse)
async def complete_conversation(project_id: str) -> CompleteConversationResponse:
    """完成對話並返回總結 - Complete conversation and return summary"""

    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")

    # 獲取或創建 Manager
    project = projects_db[project_id]
    manager = project["questionnaire_state"].get("manager")
    if not manager:
        manager = ClientManagerAgentV2()

    # 生成總結
    summary = """基於我們的對話，我已經了解了您的需求。以下是我的專業建議：

1. **空間規劃**：根據您提到的區域，我建議優先處理濕區防水。
2. **材料選擇**：在您的預算範圍內，我推薦性價比最高的材料組合。
3. **施工順序**：建議先完成隱蔽工程，再進行裝飾工程。
4. **時間安排**：預計整個項目需要 3-4 週完成。

接下來，我會為您生成詳細的設計方案和規格書。"""

    # 創建簡報數據
    briefing = {
        "project_id": project_id,
        "user_profile": {
            "communication_style": "professional",
            "budget_conscious": True,
            "timeline_important": True
        },
        "style_preferences": ["modern", "practical"],
        "key_requirements": [
            "防水處理",
            "安全電氣",
            "通風系統",
            "材料質量"
        ],
        "completed_at": datetime.utcnow().isoformat()
    }

    # 分析結果
    analysis = {
        "summary": summary,
        "key_insights": [
            "用戶對質量有高要求",
            "預算有限制，需要合理分配",
            "多個區域需要關注防水"
        ],
        "recommendations": [
            "優先安排隱蔽工程檢查",
            "選擇高品質防水材料",
            "建議分階段施工以控制成本"
        ],
        "next_steps": [
            "生成詳細設計圖",
            "準備完整規格書",
            "安排現場丈量"
        ]
    }

    return CompleteConversationResponse(
        summary=summary,
        briefing=briefing,
        analysis=analysis
    )
