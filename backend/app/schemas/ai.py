"""AI generation, agent, chat, and prep schemas."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class AIMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class AIConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[AIMessageResponse]] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[uuid.UUID] = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message: str
    role: str = "assistant"
    metadata: Optional[Dict[str, Any]] = None


class TailorResumeRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    job_description: Optional[str] = None
    target_role: Optional[str] = None


class TailorResumeResponse(BaseModel):
    version_id: uuid.UUID
    resume_id: uuid.UUID
    title: str
    tailored_content: Dict[str, Any]
    improvements: List[str]
    matched_keywords: List[str]
    diff_summary: Optional[str] = None


class CoverLetterRequest(BaseModel):
    job_id: Optional[uuid.UUID] = None
    resume_id: Optional[uuid.UUID] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    tone: str = "professional"  # professional, confident, enthusiastic, concise


class CoverLetterResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    tone: str
    company: Optional[str] = None
    job_title: Optional[str] = None


class InterviewPrepRequest(BaseModel):
    job_id: Optional[uuid.UUID] = None
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    resume_id: Optional[uuid.UUID] = None


class InterviewPrepResponse(BaseModel):
    job_title: str
    company: Optional[str] = None
    technical_questions: List[Dict[str, Any]]
    behavioral_questions: List[Dict[str, Any]]
    company_insights: Optional[Dict[str, Any]] = None
    preparation_tips: List[str]
