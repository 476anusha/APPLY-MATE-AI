"""Job discovery, provider aggregation, and sync service."""
import asyncio
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.integrations.job_providers.adzuna import AdzunaJobProvider
from app.integrations.job_providers.arbeitnow import ArbeitnowJobProvider
from app.integrations.job_providers.demo_provider import DemoJobProvider
from app.integrations.job_providers.remotive import RemotiveJobProvider
from app.models.job import Job
from app.repositories.job_repository import JobRepository

logger = logging.getLogger(__name__)


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.providers = [
            RemotiveJobProvider(),
            ArbeitnowJobProvider(),
            AdzunaJobProvider(),
        ]
        self.demo_provider = DemoJobProvider()

    async def get_demo_jobs(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return realistic demo jobs explicitly labeled with provider='demo'."""
        return await self.demo_provider.fetch_jobs(limit=limit)

    async def get_job_detail(self, job_id: UUID) -> Job:
        """Fetch detailed information for a specific job."""
        job = await self.job_repo.get(job_id)
        if not job:
            raise NotFoundError(f"Job with ID {job_id} not found.")
        return job

    async def sync_jobs_from_providers(
        self, query: str = "", location: str = "", limit_per_provider: int = 15
    ) -> dict[str, int]:
        """
        Fetch fresh job listings from active providers, upsert into DB, and return count.
        """
        stats: dict[str, int] = {}
        for provider in self.providers:
            try:
                listings = await provider.fetch_jobs(
                    query=query, location=location, limit=limit_per_provider
                )
                upserted = 0
                for item in listings:
                    _, created = await self.job_repo.get_or_create_from_external(item)
                    if created:
                        upserted += 1
                stats[provider.provider_name] = upserted
            except Exception as e:
                logger.error(f"Error syncing from {provider.provider_name}: {e}")
                stats[provider.provider_name] = 0

        return stats

    async def search_jobs(
        self, filters: Any = None, user_id: UUID | None = None
    ) -> list[Job]:
        """
        Search jobs in the database.
        If database has very few jobs (< 5), automatically populates demo jobs so the UI is immediately usable.
        """
        db_jobs = await self.job_repo.search_jobs(filters)

        # If DB is empty, seed demo jobs into DB so users have real data to view/save/track
        if len(db_jobs) < 5:
            demo_jobs = await self.demo_provider.fetch_jobs(limit=30)
            for d in demo_jobs:
                await self.job_repo.get_or_create_from_external(d)
            # Re-query
            db_jobs = await self.job_repo.search_jobs(filters)

        return db_jobs
