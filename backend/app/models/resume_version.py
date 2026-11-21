"""ResumeVersion model — AI-tailored resume versions."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)  # structured resume content
    file_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    version_type: Mapped[str] = mapped_column(String(20), nullable=False)  # original/tailored/optimized
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="versions")
    user: Mapped["User"] = relationship("User", back_populates="resume_versions")
    job: Mapped["Job | None"] = relationship("Job")
