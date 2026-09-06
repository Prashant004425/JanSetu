from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    ai_provider: str


class CitizenRequestInput(BaseModel):
    text: str = Field(min_length=5, max_length=2000)
    location: str | None = Field(default=None, max_length=120)
    selected_language: str | None = Field(default=None, max_length=20)


class RequestAnalysis(BaseModel):
    language: str
    translated_text: str
    understanding: str
    categories: list[str]
    category: str
    subcategory: str
    location: str | None
    issue: str
    urgency: str
    severity: str
    confidence: float = Field(ge=0, le=1)
    priority_score: int = Field(ge=0, le=100)
    priority_label: str
    similar_request_count: int = Field(ge=0)


class CitizenRequest(CitizenRequestInput, RequestAnalysis):
    id: int
    request_id: str = ""
    status: str = "pending"
    risk_level: str = "LOW"
    assigned_to: str | None = None
    progress_percent: int = Field(default=0, ge=0, le=100)
    government_notes: str = ""
    completion_notes: str = ""
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RequestStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=30)
    notes: str = Field(default="", max_length=2000)
    progress_percent: int = Field(default=0, ge=0, le=100)


class WorkProgressUpdate(BaseModel):
    progress_percent: int = Field(ge=0, le=100)
    notes: str = Field(default="", max_length=2000)


class WorkAssignmentUpdate(BaseModel):
    assigned_to: str | None = Field(default=None, max_length=120)


class WorkSummary(BaseModel):
    total: int
    pending: int
    in_progress: int
    on_hold: int
    completed: int
    cancelled: int
    high_risk: int
    critical_risk: int
    urgent: int
    completion_rate: float
    average_resolution_days: float | None


class DashboardSummary(BaseModel):
    total_requests: int
    completed_requests: int
    pending_requests: int
    high_priority_requests: int
    active_hotspots: int
    top_category: str
    top_location: str