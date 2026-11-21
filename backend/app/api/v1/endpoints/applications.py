"""Applications endpoint — full CRUD + Kanban. All IDs as plain strings for SQLite."""
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()

APPLICATION_STATUSES = [
    "Interested", "Saved", "Applied", "Assessment",
    "Interview Scheduled", "Interview Completed",
    "Offer Received", "Rejected", "Withdrawn",
]


class CreateApplicationRequest(BaseModel):
    company: str
    job_title: str
    job_url: Optional[str] = None
    job_id: Optional[str] = None
    status: str = "Interested"
    applied_date: Optional[str] = None
    deadline: Optional[str] = None
    interview_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    salary_offered: Optional[int] = None
    notes: Optional[str] = None


class UpdateApplicationRequest(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    job_url: Optional[str] = None
    status: Optional[str] = None
    applied_date: Optional[str] = None
    deadline: Optional[str] = None
    interview_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    salary_offered: Optional[int] = None


class StatusUpdateRequest(BaseModel):
    status: str


class NoteRequest(BaseModel):
    content: str


@router.get("")
@router.get("/")
async def list_applications(
    status: Optional[str] = None,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    stmt = select(Application).where(Application.user_id == str(current_user.id))
    if status:
        stmt = stmt.where(Application.status == status)
    stmt = stmt.order_by(Application.created_at.desc())
    result = await db.execute(stmt)
    apps = result.scalars().all()
    return [_serialize_app(a) for a in apps]


@router.get("/kanban")
async def get_kanban(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    result = await db.execute(
        select(Application).where(Application.user_id == str(current_user.id))
    )
    apps = result.scalars().all()
    kanban: dict = {s: [] for s in APPLICATION_STATUSES}
    for a in apps:
        if a.status in kanban:
            kanban[a.status].append(_serialize_app(a))
    return kanban


@router.post("", status_code=201)
@router.post("/", status_code=201)
async def create_application(
    req: CreateApplicationRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application import Application
    if req.status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {APPLICATION_STATUSES}")

    app_obj = Application(
        id=str(uuid.uuid4()),
        user_id=str(current_user.id),
        company=req.company,
        job_title=req.job_title,
        job_url=req.job_url,
        status=req.status,
        applied_date=datetime.fromisoformat(req.applied_date) if req.applied_date else None,
        deadline=datetime.fromisoformat(req.deadline) if req.deadline else None,
        interview_date=datetime.fromisoformat(req.interview_date) if req.interview_date else None,
        recruiter_name=req.recruiter_name,
        recruiter_email=req.recruiter_email,
        salary_offered=req.salary_offered,
    )
    db.add(app_obj)
    await db.commit()
    await db.refresh(app_obj)
    return _serialize_app(app_obj)


@router.get("/{app_id}")
async def get_application(
    app_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    app_obj = await _get_app_or_404(app_id, str(current_user.id), db)
    return _serialize_app(app_obj)


@router.put("/{app_id}")
async def update_application(
    app_id: str,
    req: UpdateApplicationRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    app_obj = await _get_app_or_404(app_id, str(current_user.id), db)
    for field, value in req.model_dump(exclude_none=True).items():
        if field in ("applied_date", "deadline", "interview_date") and value:
            value = datetime.fromisoformat(value)
        setattr(app_obj, field, value)
    await db.commit()
    await db.refresh(app_obj)
    return _serialize_app(app_obj)


@router.patch("/{app_id}/status")
async def update_status(
    app_id: str,
    req: StatusUpdateRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    if req.status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    app_obj = await _get_app_or_404(app_id, str(current_user.id), db)
    app_obj.status = req.status
    await db.commit()
    return {"id": str(app_obj.id), "status": app_obj.status}


@router.delete("/{app_id}", status_code=204)
async def delete_application(
    app_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    app_obj = await _get_app_or_404(app_id, str(current_user.id), db)
    await db.delete(app_obj)
    await db.commit()


@router.post("/{app_id}/notes", status_code=201)
async def add_note(
    app_id: str,
    req: NoteRequest,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application_note import ApplicationNote
    await _get_app_or_404(app_id, str(current_user.id), db)
    note = ApplicationNote(
        id=str(uuid.uuid4()),
        application_id=app_id,
        user_id=str(current_user.id),
        content=req.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return {"id": str(note.id), "content": note.content, "created_at": str(note.created_at)}


@router.get("/{app_id}/notes")
async def list_notes(
    app_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.application_note import ApplicationNote
    await _get_app_or_404(app_id, str(current_user.id), db)
    result = await db.execute(
        select(ApplicationNote).where(ApplicationNote.application_id == app_id)
    )
    notes = result.scalars().all()
    return [{"id": str(n.id), "content": n.content, "created_at": str(n.created_at)} for n in notes]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_app_or_404(app_id: str, user_id: str, db: AsyncSession):
    from app.models.application import Application
    result = await db.execute(
        select(Application).where(
            Application.id == app_id,
            Application.user_id == user_id,
        )
    )
    app_obj = result.scalar_one_or_none()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


def _serialize_app(app) -> dict:
    return {
        "id": str(app.id),
        "user_id": str(app.user_id),
        "company": app.company,
        "job_title": app.job_title,
        "job_url": app.job_url,
        "status": app.status,
        "applied_date": str(app.applied_date) if app.applied_date else None,
        "deadline": str(app.deadline) if app.deadline else None,
        "interview_date": str(app.interview_date) if app.interview_date else None,
        "recruiter_name": app.recruiter_name,
        "recruiter_email": app.recruiter_email,
        "salary_offered": app.salary_offered,
        "created_at": str(app.created_at),
    }
