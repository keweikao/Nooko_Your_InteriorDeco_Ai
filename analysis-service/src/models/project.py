from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentRole(str, Enum):
    CLIENT_MANAGER = "客戶經理"
    CONTRACTOR = "專業統包商"
    DESIGNER = "設計師"
    USER = "使用者"

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
