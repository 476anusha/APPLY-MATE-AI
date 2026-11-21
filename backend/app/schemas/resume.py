"""Resume and parsing schemas."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ExtractedDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    resume_id: uuid.UUID
    user_id: uuid.UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    technical_skills: Optional[List[str]] = None
    soft_skills: Optional[List[str]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    achievements: Optional[List[str]] = None
    overall_score: Optional[float] = None
    ats_score: Optional[float] = None
    section_scores: Optional[Dict[str, Any]] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    raw_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    is_default: bool
    is_parsed: bool
    parse_status: str
    created_at: datetime
    updated_at: datetime
    extracted_data: Optional[ExtractedDataResponse] = None


class ResumeUploadResponse(BaseModel):
    id: uuid.UUID
    title: str
    file_name: str
    file_url: str
    parse_status: str
    message: str = "Resume uploaded successfully"


class ResumeAnalysisResponse(BaseModel):
    resume_id: uuid.UUID
    overall_score: float
    ats_score: float
    section_scores: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    missing_keywords: List[str]
