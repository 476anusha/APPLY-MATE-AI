"""User model."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False)
    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="user")
    resume_versions: Mapped[list["ResumeVersion"]] = relationship("ResumeVersion", back_populates="user")
    job_matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="user")
    saved_jobs: Mapped[list["SavedJob"]] = relationship("SavedJob", back_populates="user")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="user")
    cover_letters: Mapped[list["CoverLetter"]] = relationship("CoverLetter", back_populates="user")
    generated_documents: Mapped[list["GeneratedDocument"]] = relationship("GeneratedDocument", back_populates="user")
    ai_conversations: Mapped[list["AIConversation"]] = relationship("AIConversation", back_populates="user")
    agent_tasks: Mapped[list["AgentTask"]] = relationship("AgentTask", back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")
    subscriptions: Mapped[list["UserSubscription"]] = relationship("UserSubscription", back_populates="user")
    usage_records: Mapped[list["UsageRecord"]] = relationship("UsageRecord", back_populates="user")
