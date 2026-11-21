"""Saved Jobs endpoints — real DB implementation."""
import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class SaveJobRequest(BaseModel):
    job_id: str
    notes: Optional[str] = None
    category: Optional[str] = None


class SavedJobItem(BaseModel):
    id: str
    job_id: str
    notes: Optional[str] = None
    category: Optional[str] = None
    created_at: str
    # Flattened job fields for display
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    work_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    experience_level: Optional[str] = None
    apply_url: Optional[str] = None
    skills_required: List[str] = []
    is_demo: bool = False


class MoveToTrackerRequest(BaseModel):
    notes: Optional[str] = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _saved_job_to_dict(saved: Any, job: Any) -> SavedJobItem:
    created_str = saved.created_at.isoformat() if hasattr(saved.created_at, "isoformat") else str(saved.created_at)
    return SavedJobItem(
        id=str(saved.id),
        job_id=str(saved.job_id),
        notes=saved.notes,
        category=saved.category,
        created_at=created_str,
        title=getattr(job, "title", None) if job else None,
        company=getattr(job, "company", None) if job else None,
        location=getattr(job, "location", None) if job else None,
        employment_type=getattr(job, "employment_type", None) if job else None,
        work_type=getattr(job, "work_type", None) if job else None,
        salary_min=getattr(job, "salary_min", None) if job else None,
        salary_max=getattr(job, "salary_max", None) if job else None,
        salary_currency=getattr(job, "salary_currency", "USD") if job else None,
        experience_level=getattr(job, "experience_level", None) if job else None,
        apply_url=getattr(job, "application_url", None) if job else None,
        skills_required=list(getattr(job, "required_skills", None) or []) if job else [],
        is_demo=getattr(job, "provider", "") == "demo" if job else False,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[SavedJobItem])
async def list_saved_jobs(
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """List all jobs saved by the current user."""
    from app.models.saved_job import SavedJob
    from app.models.job import Job

    result = await db.execute(
        select(SavedJob)
        .where(SavedJob.user_id == str(current_user.id))
        .order_by(SavedJob.created_at.desc())
    )
    saved_jobs = result.scalars().all()

    output = []
    for sj in saved_jobs:
        job_result = await db.execute(select(Job).where(Job.id == sj.job_id))
        job = job_result.scalar_one_or_none()
        output.append(_saved_job_to_dict(sj, job))

    return output


@router.post("", response_model=SavedJobItem, status_code=status.HTTP_201_CREATED)
async def save_job(
    req: SaveJobRequest,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Save a job for future reference. Prevents duplicate saves."""
    from app.models.saved_job import SavedJob
    from app.models.job import Job

    try:
        job_uuid = uuid.UUID(req.job_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid job_id format")

    # Verify job exists
    job_result = await db.execute(select(Job).where(Job.id == job_uuid))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check for duplicate
    existing = await db.execute(
        select(SavedJob).where(
            SavedJob.user_id == str(current_user.id),
            SavedJob.job_id == job_uuid,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is already saved",
        )

    saved = SavedJob(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        job_id=job_uuid,
        notes=req.notes,
        category=req.category,
    )
    db.add(saved)
    await db.commit()
    await db.refresh(saved)

    return _saved_job_to_dict(saved, job)


@router.delete("/{saved_job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_job(
    saved_job_id: str,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a job from saved list (ownership checked)."""
    from app.models.saved_job import SavedJob

    try:
        sid = uuid.UUID(saved_job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Saved job not found")

    result = await db.execute(
        select(SavedJob).where(SavedJob.id == sid, SavedJob.user_id == str(current_user.id))
    )
    saved = result.scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")

    await db.delete(saved)
    await db.commit()


@router.post("/{saved_job_id}/move-to-tracker", status_code=status.HTTP_201_CREATED)
async def move_to_tracker(
    saved_job_id: str,
    req: MoveToTrackerRequest,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Create an Application record from a saved job and optionally remove it from saved."""
    from app.models.saved_job import SavedJob
    from app.models.job import Job
    from app.models.application import Application

    try:
        sid = uuid.UUID(saved_job_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Saved job not found")

    result = await db.execute(
        select(SavedJob).where(SavedJob.id == sid, SavedJob.user_id == str(current_user.id))
    )
    saved = result.scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")

    # Check if already tracked
    existing_app = await db.execute(
        select(Application).where(
            Application.user_id == str(current_user.id),
            Application.job_id == saved.job_id,
        )
    )
    if existing_app.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application for this job already exists in tracker",
        )

    # Fetch job details
    job_result = await db.execute(select(Job).where(Job.id == saved.job_id))
    job = job_result.scalar_one_or_none()

    application = Application(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        job_id=saved.job_id,
        status="Interested",
        # Snapshot job info in case the job record is later removed
        job_title=getattr(job, "title", "Unknown Position") if job else "Unknown Position",
        company=getattr(job, "company", "Unknown Company") if job else "Unknown Company",
        job_url=getattr(job, "application_url", None) if job else None,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    return {
        "message": "Job moved to application tracker",
        "application_id": str(application.id),
        "status": application.status,
    }
