"""ExtractedResumeData model — AI-parsed resume content and scores."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ExtractedResumeData(Base):
    __tablename__ = "extracted_resume_data"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    education: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of {degree, university, year, gpa}
    experience: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of {title, company, duration, description, bullets}
    projects: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of {name, description, tech_stack, url}
    technical_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of strings
    soft_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of strings
    certifications: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of {name, issuer, year}
    achievements: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # list of strings
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0-100
    ats_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    section_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {education: 80, experience: 70, ...}
    strengths: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weaknesses: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    suggestions: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    missing_keywords: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="extracted_data")
    user: Mapped["User"] = relationship("User")
