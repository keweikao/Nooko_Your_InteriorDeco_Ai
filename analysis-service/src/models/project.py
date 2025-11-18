from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentRole(str, Enum):
    CLIENT_MANAGER = "客戶經理"
    CONTRACTOR = "專業統包商"
    DESIGNER = "設計師"
    USER = "使用者"

class ConversationStage(str, Enum):
    """Conversation progress stages"""
    GREETING = "greeting"  # Initial greeting
    ASSESSMENT = "assessment"  # Understanding needs
    CLARIFICATION = "clarification"  # Asking clarifying questions
    SUMMARY = "summary"  # Summarizing understanding
    COMPLETE = "complete"  # Conversation complete

class ConversationMessage(BaseModel):
    """Single message in the conversation"""
    id: str
    sender: str  # "user" or "agent"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None  # For extracted specs, progress, etc.

class ExtractedSpecifications(BaseModel):
    """Specifications extracted from conversation"""
    # Basic Info
    project_id: str

    # Design Requirements
    project_type: Optional[str] = None  # 全屋翻新, 局部改造
    style_preference: Optional[str] = None  # 現代, 北歐, 日式, 古典, etc.

    # Budget & Timeline
    budget_range: Optional[str] = None  # e.g., "500,000-1,000,000"
    timeline: Optional[str] = None  # e.g., "3 months"

    # Space Info
    total_area: Optional[float] = None  # Square meters
    focus_areas: Optional[List[str]] = None  # 廚房, 浴室, 臥室, 客廳, etc.

    # Materials & Quality
    material_preference: Optional[str] = None
    quality_level: Optional[str] = None  # 經濟, 標準, 高端

    # Additional Requirements
    special_requirements: Optional[List[str]] = None

    # Confidence & Completeness
    completeness_score: float = 0.0  # 0-1, how much info we have
    confidence_scores: Dict[str, float] = Field(default_factory=dict)  # Per-field confidence

    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class ConversationState(BaseModel):
    """Overall state of a conversation session"""
    # Identifiers
    conversation_id: str
    project_id: str

    # Messages
    messages: List[ConversationMessage] = []

    # Extracted Information
    extracted_specs: Optional[ExtractedSpecifications] = None

    # Progress
    stage: ConversationStage = ConversationStage.GREETING
    progress: int = 0  # 0-100

    # Agent Info
    agent_name: str = "Stephen"
    agent_status: str = "idle"  # idle, typing, analyzing

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Configuration
    max_messages: int = 100
    model_temperature: float = 0.7

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class Interaction(BaseModel):
    """Represents a single turn in the conversation."""
    agent: AgentRole
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None  # For images, etc.

class LineItem(BaseModel):
    """Represents a single line item in a quote."""
    item_name: str
    spec: Optional[str] = None
    quantity: float
    unit: str
    unit_price: float
    total_price: float
    is_suggestion: bool = False # True if this was added by our AI

class Quote(BaseModel):
    """Represents a quote, either original or generated."""
    source: str  # e.g., "original_upload", "generated_by_contractor_agent"
    line_items: List[LineItem]
    total_price: float

class ProjectBrief(BaseModel):
    """The structured data passed from Agent 1 to Agents 2 & 3."""
    project_id: str
    user_profile: Dict[str, Any] # e.g., house_type, budget, family_size
    style_preferences: List[str]
    key_requirements: List[str]
    original_quote_analysis: Dict[str, Any]

class Booking(BaseModel):
    """Represents a booking for a physical measurement."""
    project_id: str
    name: str
    contact: str
    region: Optional[str] = None # 新增 region 欄位
    booked_at: datetime = Field(default_factory=datetime.utcnow)

class Project(BaseModel):
    """The main data model for a single user journey."""
    id: str = Field(alias="_id") # For MongoDB or other DBs that use _id
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    original_quote_gcs_path: Optional[str] = None
    
    interactions: List[Interaction] = []
    
    project_brief: Optional[ProjectBrief] = None
    
    generated_quote: Optional[Quote] = None
    final_rendering_url: Optional[str] = None
    
    booking: Optional[Booking] = None
    status: str = "ongoing" # e.g., ongoing, completed, booked

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
