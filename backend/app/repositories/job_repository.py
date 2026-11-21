"""Job repository — database access for job listings."""
from typing import Any
from uuid import UUID

from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)

    async def get_by_external_id(self, external_id: str, provider: str) -> Job | None:
        """Find a job by external_id and provider."""
        stmt = select(Job).where(
            Job.external_id == external_id,
            Job.provider == provider,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_or_create_from_external(self, job_data: dict[str, Any]) -> tuple[Job, bool]:
        """
        Get an existing job by (external_id, provider) or create a new one.
        Returns (job, created_flag).
        """
        external_id = str(job_data.get("external_id", ""))
        provider = str(job_data.get("provider", "demo"))

        existing = await self.get_by_external_id(external_id, provider)
        if existing:
            # Optionally update fields if changed
            for key, val in job_data.items():
                if hasattr(existing, key) and val is not None:
                    setattr(existing, key, val)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing, False

        new_job = Job(**job_data)
        self.db.add(new_job)
        await self.db.commit()
        await self.db.refresh(new_job)
        return new_job, True

    async def get_recent_jobs(self, limit: int = 20) -> list[Job]:
        """Fetch the most recently posted active jobs."""
        stmt = (
            select(Job)
            .where(Job.is_active.is_(True))
            .order_by(desc(Job.posted_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def search_jobs(self, filters: Any = None, skip: int = 0, limit: int = 50) -> list[Job]:
        """
        Search jobs based on keyword, location, work_type, is_remote, experience_level, salary_min.
        filters can be a Pydantic model (with getattr/model_dump) or a dictionary.
        """
        stmt = select(Job).where(Job.is_active.is_(True))

        if filters:
            if hasattr(filters, "model_dump"):
                f_data = filters.model_dump(exclude_unset=True)
            elif isinstance(filters, dict):
                f_data = filters
            else:
                f_data = {
                    k: getattr(filters, k)
                    for k in dir(filters)
                    if not k.startswith("_") and getattr(filters, k) is not None
                }

            keyword = f_data.get("query") or f_data.get("keyword") or f_data.get("search")
            if keyword:
                kw_str = f"%{keyword}%"
                stmt = stmt.where(
                    or_(
                        Job.title.ilike(kw_str),
                        Job.company.ilike(kw_str),
                        Job.description.ilike(kw_str),
                    )
                )

            location = f_data.get("location")
            if location:
                stmt = stmt.where(Job.location.ilike(f"%{location}%"))

            is_remote = f_data.get("is_remote")
            if is_remote is not None:
                stmt = stmt.where(Job.is_remote.is_(is_remote))

            work_type = f_data.get("work_type")
            if work_type:
                stmt = stmt.where(Job.work_type.ilike(work_type))

            employment_type = f_data.get("employment_type")
            if employment_type:
                stmt = stmt.where(Job.employment_type.ilike(employment_type))

            experience_level = f_data.get("experience_level")
            if experience_level:
                stmt = stmt.where(Job.experience_level.ilike(experience_level))

            salary_min = f_data.get("salary_min")
            if salary_min:
                stmt = stmt.where(
                    or_(
                        Job.salary_max >= salary_min,
                        Job.salary_min >= salary_min,
                    )
                )

            provider = f_data.get("provider")
            if provider:
                stmt = stmt.where(Job.provider == provider)

            skip = f_data.get("skip", skip)
            limit = f_data.get("limit", limit)

        stmt = stmt.order_by(desc(Job.posted_at)).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
