"""Job schemas."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str
    provider: str
    title: str
    company: str
    company_logo_url: Optional[str] = None
    location: str
    is_remote: bool
    work_type: str
    employment_type: str
    experience_level: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    description: str
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    company_description: Optional[str] = None
    application_url: str
    deadline: Optional[datetime] = None
    posted_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime


class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    work_type: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    min_salary: Optional[int] = None
    provider: Optional[str] = None
    page: int = 1
    page_size: int = 20


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class JobMatchRequest(BaseModel):
    job_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None


class JobMatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    resume_id: uuid.UUID
    overall_score: float
    skill_score: float
    experience_score: float
    education_score: float
    keyword_score: float
    matched_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    matched_experience: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    explanation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None
