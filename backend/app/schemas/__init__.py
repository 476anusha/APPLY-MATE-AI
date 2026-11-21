"""Pydantic schemas package exports."""
from .auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from .user import (
    UpdateProfileRequest,
    UserProfileResponse,
    UserResponse,
)
from .resume import (
    ExtractedDataResponse,
    ResumeAnalysisResponse,
    ResumeResponse,
    ResumeUploadResponse,
)
from .job import (
    JobListResponse,
    JobMatchRequest,
    JobMatchResponse,
    JobResponse,
    JobSearchRequest,
)
from .saved_job import (
    SavedJobResponse,
    SaveJobRequest,
)
from .application import (
    ApplicationNoteResponse,
    ApplicationResponse,
    CreateApplicationNoteRequest,
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from .ai import (
    AIConversationResponse,
    AIMessageResponse,
    ChatRequest,
    ChatResponse,
    CoverLetterRequest,
    CoverLetterResponse,
    InterviewPrepRequest,
    InterviewPrepResponse,
    TailorResumeRequest,
    TailorResumeResponse,
)
from .analytics import (
    ApplicationStatsResponse,
    DashboardStatsResponse,
    SkillsAnalyticsResponse,
)
from .notification import (
    MarkNotificationReadRequest,
    NotificationResponse,
)
from .subscription import (
    PlanResponse,
    SubscriptionResponse,
    UsageResponse,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UserResponse",
    "UserProfileResponse",
    "UpdateProfileRequest",
    "ResumeResponse",
    "ResumeUploadResponse",
    "ExtractedDataResponse",
    "ResumeAnalysisResponse",
    "JobResponse",
    "JobSearchRequest",
    "JobListResponse",
    "JobMatchRequest",
    "JobMatchResponse",
    "SavedJobResponse",
    "SaveJobRequest",
    "ApplicationResponse",
    "CreateApplicationRequest",
    "UpdateApplicationRequest",
    "ApplicationNoteResponse",
    "CreateApplicationNoteRequest",
    "AIMessageResponse",
    "AIConversationResponse",
    "ChatRequest",
    "ChatResponse",
    "TailorResumeRequest",
    "TailorResumeResponse",
    "CoverLetterRequest",
    "CoverLetterResponse",
    "InterviewPrepRequest",
    "InterviewPrepResponse",
    "DashboardStatsResponse",
    "ApplicationStatsResponse",
    "SkillsAnalyticsResponse",
    "NotificationResponse",
    "MarkNotificationReadRequest",
    "PlanResponse",
    "SubscriptionResponse",
    "UsageResponse",
]
