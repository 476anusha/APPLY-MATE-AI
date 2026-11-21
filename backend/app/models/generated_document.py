"""GeneratedDocument model — AI-generated documents (cover letters, tailored resumes, interview prep)."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # cover_letter/tailored_resume/interview_prep
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    doc_metadata: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="generated_documents")
