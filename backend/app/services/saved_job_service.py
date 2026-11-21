"""Saved jobs management service."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.models.application import Application
from app.models.job import Job
from app.models.saved_job import SavedJob


class SavedJobService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_saved_jobs(self, user_id: UUID) -> list[SavedJob]:
        """Get all jobs saved/bookmarked by the user."""
        stmt = (
            select(SavedJob)
            .options(selectinload(SavedJob.job))
            .where(SavedJob.user_id == user_id)
            .order_by(SavedJob.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def save_job(
        self,
        user_id: UUID,
        job_id: UUID,
        notes: str | None = None,
        category: str | None = None,
    ) -> SavedJob:
        """
        Save/bookmark a job for the user, preventing duplicates.
        """
        # Verify job exists
        job_stmt = select(Job).where(Job.id == job_id)
        job_res = await self.db.execute(job_stmt)
        job = job_res.scalar_one_or_none()
        if not job:
            raise NotFoundError("Job not found.")

        # Check duplicate
        stmt = select(SavedJob).where(
            SavedJob.user_id == user_id,
            SavedJob.job_id == job_id,
        )
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            # If already saved, update notes / category
            if notes is not None:
                existing.notes = notes
            if category is not None:
                existing.category = category
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        saved = SavedJob(
            user_id=user_id,
            job_id=job_id,
            notes=notes,
            category=category,
        )
        self.db.add(saved)
        await self.db.commit()
        await self.db.refresh(saved)
        return saved

    async def remove_saved_job(self, user_id: UUID, saved_job_id: UUID) -> bool:
        """Remove a job from saved jobs."""
        stmt = select(SavedJob).where(SavedJob.id == saved_job_id)
        res = await self.db.execute(stmt)
        saved = res.scalar_one_or_none()
        if not saved:
            raise NotFoundError("Saved job not found.")
        if saved.user_id != user_id:
            raise PermissionDeniedError("Access denied.")

        await self.db.delete(saved)
        await self.db.commit()
        return True

    async def move_to_tracker(
        self, user_id: UUID, saved_job_id: UUID, initial_status: str = "Saved"
    ) -> Application:
        """
        Move a saved job directly into the Application Tracker.
        Creates an Application record prefilled with company and job title.
        """
        stmt = (
            select(SavedJob)
            .options(selectinload(SavedJob.job))
            .where(SavedJob.id == saved_job_id)
        )
        res = await self.db.execute(stmt)
        saved = res.scalar_one_or_none()
        if not saved:
            raise NotFoundError("Saved job not found.")
        if saved.user_id != user_id:
            raise PermissionDeniedError("Access denied.")

        job = saved.job
        company = job.company if job else "Unknown Company"
        title = job.title if job else "Position"
        url = job.application_url if job else None

        app = Application(
            user_id=user_id,
            job_id=saved.job_id,
            company=company,
            job_title=title,
            job_url=url,
            status=initial_status,
        )
        self.db.add(app)
        # Delete from saved jobs once moved to tracker
        await self.db.delete(saved)
        await self.db.commit()
        await self.db.refresh(app)
        return app
