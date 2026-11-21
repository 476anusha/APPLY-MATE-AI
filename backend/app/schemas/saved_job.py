"""Saved job schemas."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .job import JobResponse


class SaveJobRequest(BaseModel):
    job_id: uuid.UUID
    notes: Optional[str] = None
    category: Optional[str] = None


class SavedJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    notes: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None
