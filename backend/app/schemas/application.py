"""Application schemas."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from .job import JobResponse


class ApplicationNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: datetime
    updated_at: datetime


class CreateApplicationNoteRequest(BaseModel):
    content: str


class CreateApplicationRequest(BaseModel):
    job_id: Optional[uuid.UUID] = None
    resume_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None
    company: str
    job_title: str
    job_url: Optional[str] = None
    status: str = "Interested"
    applied_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    salary_offered: Optional[int] = None
    notes: Optional[str] = None


class UpdateApplicationRequest(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    salary_offered: Optional[int] = None
    resume_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    resume_id: Optional[uuid.UUID] = None
    cover_letter_id: Optional[uuid.UUID] = None
    company: str
    job_title: str
    job_url: Optional[str] = None
    status: str
    applied_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    interview_date: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    salary_offered: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None
    notes: Optional[List[ApplicationNoteResponse]] = None
