"""Analytics schemas."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class TimelinePoint(BaseModel):
    date: str
    count: int


class DashboardStatsResponse(BaseModel):
    total_applications: int
    active_applications: int
    interviews_scheduled: int
    offers_received: int
    rejections: int
    response_rate: float
    total_resumes: int
    average_ats_score: float
    saved_jobs_count: int


class ApplicationStatsResponse(BaseModel):
    by_status: List[StatusCount]
    by_date: List[TimelinePoint]
    average_days_to_interview: Optional[float] = None
    interview_conversion_rate: float
    offer_conversion_rate: float


class SkillsAnalyticsResponse(BaseModel):
    top_demanded_skills: List[Dict[str, Any]]
    top_user_skills: List[str]
    skill_gaps: List[Dict[str, Any]]
    readiness_score: float
