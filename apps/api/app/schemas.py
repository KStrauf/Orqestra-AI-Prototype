from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    role: str

class BusinessTaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str | None = None
    work_type: str | None = None
    business_area: str | None = None
    priority: str = 'NORMAL'

class BusinessTaskView(BaseModel):
    id: int
    title: str
    description: str | None
    work_type: str | None
    business_area: str | None
    status: str
    priority: str
    risk_level: str
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = {'from_attributes': True}

class AssignmentCreate(BaseModel):
    task_id: int
    assigned_to_user_id: int
    due_date: date | None = None
    priority: str = 'NORMAL'

class AssignmentComplete(BaseModel):
    completion_notes: str | None = None

class AssignmentView(BaseModel):
    id: int
    task_id: int
    assigned_to_user_id: int
    assigned_by_user_id: int
    due_date: date | None
    status: str
    priority: str
    completed_at: datetime | None
    completion_notes: str | None
    model_config = {'from_attributes': True}

class AIAnalyzeRequest(BaseModel):
    task_id: int

class AIAnalysisView(BaseModel):
    id: int
    task_id: int
    category: str
    risk_level: str
    urgency: str
    recommended_priority: str
    recommended_owner: str
    next_action: str
    reasoning_summary: str
    confidence_score: float
    guardrail_passed: bool
    human_review_required: bool
    created_at: datetime
    model_config = {'from_attributes': True}
