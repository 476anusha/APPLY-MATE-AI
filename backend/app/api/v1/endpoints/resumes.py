"""Resume management endpoints — file upload, parsing, analysis."""
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()

# Directory where uploaded resumes are stored locally
UPLOAD_DIR = Path(__file__).resolve().parents[5] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "doc",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ExtractedDataSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    soft_skills: List[str] = []
    education: List[dict] = []
    experience: List[dict] = []
    projects: List[dict] = []
    certifications: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []
    raw_text: Optional[str] = None


class ResumeAnalysisResponse(BaseModel):
    resume_id: str
    score: int
    summary: str
    strengths: List[str] = []
    improvements: List[str] = []
    missing_keywords: List[str] = []
    section_scores: dict = {}


class ResumeSummary(BaseModel):
    id: str
    title: str
    file_name: str
    file_url: str
    file_type: str
    file_size: int
    is_default: bool
    is_parsed: bool
    parse_status: str
    overall_score: Optional[int] = None
    parsed_skills: List[str] = []
    extracted_data: Optional[ExtractedDataSchema] = None
    analysis: Optional[ResumeAnalysisResponse] = None
    created_at: str
    updated_at: str


class ResumeUpdateRequest(BaseModel):
    title: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resume_to_dict(resume: Any, extracted: Any = None) -> ResumeSummary:
    skills: List[str] = []
    ext_schema: Optional[ExtractedDataSchema] = None
    analysis_schema: Optional[ResumeAnalysisResponse] = None

    if extracted:
        raw_skills = extracted.technical_skills or []
        skills = list(raw_skills) if isinstance(raw_skills, (list, tuple)) else []
        ext_schema = ExtractedDataSchema(
            full_name=extracted.full_name,
            email=extracted.email,
            phone=extracted.phone,
            summary=extracted.summary,
            skills=skills,
            soft_skills=list(extracted.soft_skills or []),
            education=list(extracted.education or []),
            experience=list(extracted.experience or []),
            projects=list(extracted.projects or []),
            certifications=list(extracted.certifications or []),
            achievements=list(extracted.achievements or []),
            languages=[],
            raw_text=extracted.raw_text,
        )

        if extracted.overall_score is not None:
            analysis_schema = ResumeAnalysisResponse(
                resume_id=str(resume.id),
                score=int(extracted.overall_score),
                summary="Resume analysis complete.",
                strengths=list(extracted.strengths or []),
                improvements=list(extracted.suggestions or extracted.weaknesses or []),
                missing_keywords=list(extracted.missing_keywords or []),
                section_scores=dict(extracted.section_scores or {}),
            )

    created_str = resume.created_at.isoformat() if hasattr(resume.created_at, "isoformat") else str(resume.created_at)
    updated_str = resume.updated_at.isoformat() if hasattr(resume.updated_at, "isoformat") else str(resume.updated_at)

    return ResumeSummary(
        id=str(resume.id),
        title=resume.title,
        file_name=resume.file_name,
        file_url=resume.file_url,
        file_type=resume.file_type,
        file_size=resume.file_size,
        is_default=resume.is_default,
        is_parsed=resume.is_parsed,
        parse_status=resume.parse_status,
        overall_score=getattr(extracted, "overall_score", None) if extracted else None,
        parsed_skills=skills,
        extracted_data=ext_schema,
        analysis=analysis_schema,
        created_at=created_str,
        updated_at=updated_str,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/upload", response_model=ResumeSummary, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    title: str = Form(default=""),
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Upload a new resume (PDF or DOCX). Validates type and size."""
    from app.models.resume import Resume

    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF and DOCX files are allowed.",
        )

    # Read contents and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File size exceeds the 10 MB limit.",
        )

    file_ext = ALLOWED_TYPES[content_type]
    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}.{file_ext}"
    dest = UPLOAD_DIR / safe_name

    # Save to disk
    with open(dest, "wb") as f:
        f.write(contents)

    effective_title = title.strip() or (file.filename or "My Resume").rsplit(".", 1)[0]

    resume = Resume(
        id=file_id,
        user_id=str(current_user.id),
        title=effective_title,
        file_name=file.filename or safe_name,
        file_url=f"/uploads/{safe_name}",
        file_type=file_ext,
        file_size=len(contents),
        is_default=False,
        is_parsed=False,
        parse_status="pending",
    )

    # If this is the user's first resume, make it default
    result = await db.execute(
        select(Resume).where(Resume.user_id == str(current_user.id)).limit(1)
    )
    if result.scalar_one_or_none() is None:
        resume.is_default = True

    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return _resume_to_dict(resume)


@router.get("", response_model=List[ResumeSummary])
async def list_resumes(
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all resumes for the current user with extracted data."""
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData

    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == str(current_user.id))
        .order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()

    output = []
    for r in resumes:
        ext_result = await db.execute(
            select(ExtractedResumeData).where(ExtractedResumeData.resume_id == r.id)
        )
        extracted = ext_result.scalar_one_or_none()
        output.append(_resume_to_dict(r, extracted))

    return output


@router.get("/{resume_id}", response_model=ResumeSummary)
async def get_resume(
    resume_id: str,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get a specific resume by ID."""
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    ext_result = await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
    )
    extracted = ext_result.scalar_one_or_none()

    return _resume_to_dict(resume, extracted)


@router.put("/{resume_id}", response_model=ResumeSummary)
async def update_resume(
    resume_id: str,
    req: ResumeUpdateRequest,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update resume metadata (e.g., title)."""
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData

    try:
        rid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Resume not found")

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    if req.title is not None:
        resume.title = req.title

    await db.commit()
    await db.refresh(resume)

    ext_result = await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
    )
    extracted = ext_result.scalar_one_or_none()

    return _resume_to_dict(resume, extracted)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a resume (file + DB record). Ownership verified."""
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData

    try:
        rid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Resume not found")

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Delete extracted data first
    ext_result = await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
    )
    extracted = ext_result.scalar_one_or_none()
    if extracted:
        await db.delete(extracted)

    # Delete file from disk
    file_path = UPLOAD_DIR / os.path.basename(resume.file_url)
    if file_path.exists():
        file_path.unlink()

    was_default = resume.is_default
    await db.delete(resume)
    await db.commit()

    # If deleted resume was default, assign default to next available
    if was_default:
        next_result = await db.execute(
            select(Resume)
            .where(Resume.user_id == str(current_user.id))
            .order_by(Resume.created_at.desc())
            .limit(1)
        )
        next_resume = next_result.scalar_one_or_none()
        if next_resume:
            next_resume.is_default = True
            await db.commit()


@router.post("/{resume_id}/set-default", response_model=ResumeSummary)
async def set_default_resume(
    resume_id: str,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Mark a resume as the user's default resume."""
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData

    try:
        rid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Clear existing default
    all_result = await db.execute(
        select(Resume).where(Resume.user_id == str(current_user.id))
    )
    for r in all_result.scalars().all():
        r.is_default = False

    # Set new default
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    resume.is_default = True
    await db.commit()
    await db.refresh(resume)

    ext_result = await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
    )
    extracted = ext_result.scalar_one_or_none()

    return _resume_to_dict(resume, extracted)


@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: str,
    force: bool = False,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Parse file text, extract structured data via AI, then score the resume.
    If already analyzed and force=False, returns saved analysis immediately.
    """
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData
    from app.utils.file_parser import extract_text_from_file
    from app.integrations.ai.factory import get_ai_provider

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Check if already analyzed — return existing data instantly if force is False
    ext_result = await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
    )
    extracted = ext_result.scalar_one_or_none()

    if not force and extracted and extracted.overall_score is not None:
        resume.is_parsed = True
        resume.parse_status = "completed"
        await db.commit()
        return ResumeAnalysisResponse(
            resume_id=resume_id,
            score=int(extracted.overall_score),
            summary="Resume analysis complete.",
            strengths=list(extracted.strengths or []),
            improvements=list(extracted.suggestions or extracted.weaknesses or []),
            missing_keywords=list(extracted.missing_keywords or []),
            section_scores=dict(extracted.section_scores or {}),
        )

    # Update parse status to processing
    resume.parse_status = "processing"
    await db.commit()

    file_path = UPLOAD_DIR / os.path.basename(resume.file_url)

    try:
        # Extract raw text (reuse cached text if available)
        if extracted and extracted.raw_text:
            raw_text = extracted.raw_text
        elif file_path.exists():
            raw_text = extract_text_from_file(str(file_path), resume.file_type)
        else:
            raw_text = f"[File not found on disk: {resume.file_url}]"

        ai = get_ai_provider()
        parse_result = ai.analyze_resume(raw_text)
        analysis = ai.score_resume(parse_result)

        # Upsert ExtractedResumeData
        ext_result = await db.execute(
            select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
        )
        extracted = ext_result.scalar_one_or_none()

        if extracted is None:
            extracted = ExtractedResumeData(
                id=str(uuid.uuid4()),
                resume_id=resume_id,
                user_id=str(current_user.id),
            )
            db.add(extracted)

        extracted.full_name = parse_result.get("full_name")
        extracted.email = parse_result.get("email")
        extracted.phone = parse_result.get("phone")
        extracted.summary = parse_result.get("summary")
        extracted.technical_skills = parse_result.get("technical_skills", parse_result.get("skills", []))
        extracted.soft_skills = parse_result.get("soft_skills", [])
        extracted.education = parse_result.get("education", [])
        extracted.experience = parse_result.get("experience", [])
        extracted.projects = parse_result.get("projects", [])
        extracted.certifications = parse_result.get("certifications", [])
        extracted.achievements = parse_result.get("achievements", [])
        extracted.raw_text = raw_text
        extracted.overall_score = analysis.get("overall_score", analysis.get("score", 75))
        extracted.ats_score = analysis.get("ats_score")
        extracted.section_scores = analysis.get("section_scores", {})
        extracted.strengths = analysis.get("strengths", [])
        extracted.weaknesses = analysis.get("weaknesses", [])
        extracted.suggestions = analysis.get("suggestions", [])
        extracted.missing_keywords = analysis.get("missing_keywords", [])

        resume.is_parsed = True
        resume.parse_status = "completed"
        await db.commit()
        await db.refresh(extracted)

        improvements_list = list(extracted.suggestions or extracted.weaknesses or [])
        return ResumeAnalysisResponse(
            resume_id=resume_id,
            score=int(extracted.overall_score or 75),
            summary=analysis.get("summary", analysis.get("disclaimer", "Resume analysis complete.")),
            strengths=list(extracted.strengths or []),
            improvements=improvements_list,
            missing_keywords=list(extracted.missing_keywords or []),
            section_scores=dict(extracted.section_scores or {}),
        )

    except Exception as exc:
        resume.parse_status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume analysis failed: {str(exc)}",
        )


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: str,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get already calculated analysis for a resume without re-running."""
    from app.models.resume import Resume
    from app.models.extracted_resume_data import ExtractedResumeData

    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == str(current_user.id))
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    ext_result = await db.execute(
        select(ExtractedResumeData).where(ExtractedResumeData.resume_id == resume_id)
    )
    extracted = ext_result.scalar_one_or_none()
    if not extracted or extracted.overall_score is None:
        raise HTTPException(status_code=404, detail="Resume has not been analyzed yet")

    return ResumeAnalysisResponse(
        resume_id=resume_id,
        score=int(extracted.overall_score),
        summary="Resume analysis complete.",
        strengths=list(extracted.strengths or []),
        improvements=list(extracted.suggestions or extracted.weaknesses or []),
        missing_keywords=list(extracted.missing_keywords or []),
        section_scores=dict(extracted.section_scores or {}),
    )
