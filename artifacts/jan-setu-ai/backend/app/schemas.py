from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    ai_provider: str


class CitizenRequestInput(BaseModel):
    text: str = Field(min_length=5, max_length=2000)
    location: str | None = Field(default=None, max_length=120)


class RequestAnalysis(BaseModel):
    language: str
    category: str
    location: str
    issue: str
    confidence: float = Field(ge=0, le=1)
    priority_score: int = Field(ge=0, le=100)
    priority_label: str
    similar_request_count: int = Field(ge=0)


class CitizenRequest(CitizenRequestInput, RequestAnalysis):
    id: int
    status: str
    created_at: datetime


class DashboardSummary(BaseModel):
    total_requests: int
    high_priority_requests: int
    active_hotspots: int
    top_category: str
    top_location: str