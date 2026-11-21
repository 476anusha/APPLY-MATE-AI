"""Job application tracking and Kanban workflow service."""
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from app.models.application import Application
from app.models.application_note import ApplicationNote
from app.repositories.application_repository import KANBAN_STATUSES, ApplicationRepository


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.app_repo = ApplicationRepository(db)

    async def get_applications(
        self, user_id: UUID, filters: dict[str, Any] | None = None
    ) -> list[Application]:
        """Get all applications for user with optional filtering."""
        return await self.app_repo.get_by_user(user_id, filters)

    async def get_application(self, application_id: UUID, user_id: UUID) -> Application:
        """Get single application and verify ownership."""
        stmt = (
            select(Application)
            .options(
                selectinload(Application.job),
                selectinload(Application.notes),
                selectinload(Application.resume),
                selectinload(Application.cover_letter),
            )
            .where(Application.id == application_id)
        )
        res = await self.db.execute(stmt)
        app = res.scalar_one_or_none()
        if not app:
            raise NotFoundError("Application not found.")
        if app.user_id != user_id:
            raise PermissionDeniedError("Access denied.")
        return app

    async def create_application(self, user_id: UUID, data: Any) -> Application:
        """Create a new job application."""
        if hasattr(data, "model_dump"):
            payload = data.model_dump(exclude_unset=True)
        elif isinstance(data, dict):
            payload = dict(data)
        else:
            payload = {}

        payload["user_id"] = user_id
        if "status" not in payload:
            payload["status"] = "Interested"

        app = Application(**payload)
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def update_application(
        self, application_id: UUID, user_id: UUID, data: Any
    ) -> Application:
        """Update an existing application."""
        app = await self.get_application(application_id, user_id)

        if hasattr(data, "model_dump"):
            payload = data.model_dump(exclude_unset=True)
        elif isinstance(data, dict):
            payload = dict(data)
        else:
            payload = {}

        # Disallow changing user_id
        payload.pop("user_id", None)

        for key, val in payload.items():
            if hasattr(app, key):
                setattr(app, key, val)

        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def update_status(
        self, application_id: UUID, user_id: UUID, new_status: str
    ) -> Application:
        """Update application status (e.g., drag and drop in Kanban board)."""
        if new_status not in KANBAN_STATUSES:
            raise ValidationError(
                f"Invalid status '{new_status}'. Allowed statuses: {', '.join(KANBAN_STATUSES)}"
            )

        app = await self.get_application(application_id, user_id)
        app.status = new_status
        self.db.add(app)
        await self.db.commit()
        await self.db.refresh(app)
        return app

    async def delete_application(self, application_id: UUID, user_id: UUID) -> bool:
        """Delete an application."""
        app = await self.get_application(application_id, user_id)
        await self.db.delete(app)
        await self.db.commit()
        return True

    async def add_note(
        self, application_id: UUID, user_id: UUID, content: str
    ) -> ApplicationNote:
        """Add a note to an application."""
        # Ensure application exists and belongs to user
        await self.get_application(application_id, user_id)
        return await self.app_repo.add_note(application_id, user_id, content)

    async def get_notes(
        self, application_id: UUID, user_id: UUID
    ) -> list[ApplicationNote]:
        """Get all notes for an application."""
        await self.get_application(application_id, user_id)
        return await self.app_repo.get_notes(application_id)

    async def get_kanban_board(self, user_id: UUID) -> dict[str, list[Application]]:
        """Return applications grouped by Kanban status."""
        return await self.app_repo.get_kanban_view(user_id)

    async def get_application_analytics(self, user_id: UUID) -> dict[str, Any]:
        """Return high-level application conversion analytics."""
        return await self.app_repo.get_analytics(user_id)
