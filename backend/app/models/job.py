"""Job model — job listings from external providers."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("external_id", "provider", name="uq_job_external_provider"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # adzuna/remotive/arbeitnow/demo
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    work_type: Mapped[str] = mapped_column(String(20), nullable=False)  # remote/hybrid/onsite
    employment_type: Mapped[str] = mapped_column(String(30), nullable=False)  # full-time/part-time/contract/internship
    experience_level: Mapped[str] = mapped_column(String(20), nullable=False)  # entry/mid/senior
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    responsibilities: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    preferred_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    required_skills: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    benefits: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    company_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    job_matches: Mapped[list["JobMatch"]] = relationship("JobMatch", back_populates="job")
    saved_by: Mapped[list["SavedJob"]] = relationship("SavedJob", back_populates="job")
    applications: Mapped[list["Application"]] = relationship("Application", back_populates="job")
    cover_letters: Mapped[list["CoverLetter"]] = relationship("CoverLetter", back_populates="job")
    resume_versions: Mapped[list["ResumeVersion"]] = relationship("ResumeVersion", back_populates="job")
