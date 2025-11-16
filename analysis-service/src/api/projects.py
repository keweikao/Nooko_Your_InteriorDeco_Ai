from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from src.agents.client_manager_v2 import ClientManagerAgentV2, QuestionCategory
from src.agents.construction_translator import ConstructionTranslator

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

class AnswerRequest(BaseModel):
    question_id: str
    answer: Any

class AnswerResponse(BaseModel):
    accepted: bool
    next_question: Optional[Dict[str, Any]]
    is_complete: bool
    message: Optional[str]

class TranslateNeedRequest(BaseModel):
    consumer_need: str
    context: Optional[Dict[str, Any]] = None

# In-memory storage (will be replaced with Firestore)
projects_db: Dict[str, Dict[str, Any]] = {}

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
        progress=progress
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
        message="感謝您的回答！" if not is_complete else "問卷已完成，正在為您準備裝修建議..."
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
