"""Application repository — database access for job applications and Kanban."""
from typing import Any
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.application_note import ApplicationNote
from app.repositories.base import BaseRepository

KANBAN_STATUSES = [
    "Interested",
    "Saved",
    "Applied",
    "Assessment",
    "Interview Scheduled",
    "Interview Completed",
    "Offer Received",
    "Rejected",
    "Withdrawn",
]


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: AsyncSession):
        super().__init__(Application, db)

    async def get_by_user(
        self, user_id: UUID, filters: dict[str, Any] | None = None, skip: int = 0, limit: int = 100
    ) -> list[Application]:
        """Fetch applications for a given user with optional status / keyword filters."""
        stmt = (
            select(Application)
            .where(Application.user_id == user_id)
            .options(selectinload(Application.job), selectinload(Application.notes))
        )

        if filters:
            if hasattr(filters, "model_dump"):
                f_data = filters.model_dump(exclude_unset=True)
            elif isinstance(filters, dict):
                f_data = filters
            else:
                f_data = {}

            status = f_data.get("status")
            if status:
                stmt = stmt.where(Application.status == status)

            search = f_data.get("search") or f_data.get("query")
            if search:
                term = f"%{search}%"
                stmt = stmt.where(
                    (Application.company.ilike(term)) | (Application.job_title.ilike(term))
                )

        stmt = stmt.order_by(desc(Application.updated_at)).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_kanban_view(self, user_id: UUID) -> dict[str, list[Application]]:
        """Return applications grouped by application status for Kanban boards."""
        stmt = (
            select(Application)
            .where(Application.user_id == user_id)
            .options(selectinload(Application.job), selectinload(Application.notes))
            .order_by(desc(Application.updated_at))
        )
        res = await self.db.execute(stmt)
        all_apps = list(res.scalars().all())

        kanban_dict: dict[str, list[Application]] = {status: [] for status in KANBAN_STATUSES}
        for app in all_apps:
            if app.status in kanban_dict:
                kanban_dict[app.status].append(app)
            else:
                # Fallback for any custom or unexpected status
                kanban_dict.setdefault(app.status, []).append(app)

        return kanban_dict

    async def get_analytics(self, user_id: UUID) -> dict[str, Any]:
        """Calculate application statistics for user analytics."""
        stmt = (
            select(Application.status, func.count(Application.id))
            .where(Application.user_id == user_id)
            .group_by(Application.status)
        )
        res = await self.db.execute(stmt)
        status_counts = dict(res.all())

        total = sum(status_counts.values())
        applied = (
            status_counts.get("Applied", 0)
            + status_counts.get("Assessment", 0)
            + status_counts.get("Interview Scheduled", 0)
            + status_counts.get("Interview Completed", 0)
            + status_counts.get("Offer Received", 0)
            + status_counts.get("Rejected", 0)
        )
        interviews = (
            status_counts.get("Interview Scheduled", 0)
            + status_counts.get("Interview Completed", 0)
        )
        offers = status_counts.get("Offer Received", 0)
        rejected = status_counts.get("Rejected", 0)
        pending = (
            status_counts.get("Applied", 0)
            + status_counts.get("Assessment", 0)
            + status_counts.get("Interview Scheduled", 0)
        )

        conversion_rate = round((interviews / applied * 100), 1) if applied > 0 else 0.0
        offer_rate = round((offers / applied * 100), 1) if applied > 0 else 0.0

        return {
            "total_applications": total,
            "applied": applied,
            "interviews": interviews,
            "offers": offers,
            "rejected": rejected,
            "pending": pending,
            "conversion_rate": conversion_rate,
            "offer_rate": offer_rate,
            "by_status": status_counts,
        }

    async def add_note(self, application_id: UUID, user_id: UUID, content: str) -> ApplicationNote:
        """Add a note to an application."""
        note = ApplicationNote(
            application_id=application_id,
            user_id=user_id,
            content=content,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

    async def get_notes(self, application_id: UUID) -> list[ApplicationNote]:
        """Get all notes for an application."""
        stmt = (
            select(ApplicationNote)
            .where(ApplicationNote.application_id == application_id)
            .order_by(desc(ApplicationNote.created_at))
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
