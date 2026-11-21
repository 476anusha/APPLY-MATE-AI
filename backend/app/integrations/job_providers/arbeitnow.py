"""Arbeitnow API job provider (free, European & remote jobs)."""
import logging
from datetime import datetime, timezone
from typing import Any
import httpx

from app.integrations.job_providers.base import BaseJobProvider

logger = logging.getLogger(__name__)


class ArbeitnowJobProvider(BaseJobProvider):
    provider_name = "arbeitnow"
    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    async def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 20,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch jobs from the free Arbeitnow API."""
        jobs: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL)
                if resp.status_code != 200:
                    logger.warning(f"Arbeitnow API returned status {resp.status_code}")
                    return []

                data = resp.json()
                raw_jobs = data.get("data", [])

                for item in raw_jobs:
                    if len(jobs) >= limit:
                        break

                    title = item.get("title") or ""
                    desc = item.get("description") or ""
                    tags = item.get("tags") or []

                    # Filter by query if specified
                    if query and query.lower() not in title.lower() and query.lower() not in desc.lower():
                        continue

                    # Filter by location if specified
                    job_loc = item.get("location") or "Remote"
                    if location and location.lower() not in job_loc.lower():
                        continue

                    is_remote = bool(item.get("remote", False))
                    created_at_raw = item.get("created_at")
                    posted_at = datetime.now(timezone.utc)
                    if isinstance(created_at_raw, (int, float)):
                        try:
                            posted_at = datetime.fromtimestamp(created_at_raw, tz=timezone.utc)
                        except Exception:
                            pass

                    job_types = item.get("job_types") or []
                    emp_type = "full-time"
                    if "part-time" in [t.lower() for t in job_types]:
                        emp_type = "part-time"

                    normalized: dict[str, Any] = {
                        "external_id": item.get("slug") or str(hash(title + item.get("company_name", ""))),
                        "provider": self.provider_name,
                        "title": title or "Software Position",
                        "company": item.get("company_name") or "Tech Company",
                        "company_logo_url": None,
                        "location": job_loc,
                        "is_remote": is_remote,
                        "work_type": "remote" if is_remote else "hybrid",
                        "employment_type": emp_type,
                        "experience_level": "mid",
                        "salary_min": None,
                        "salary_max": None,
                        "salary_currency": "EUR",
                        "description": desc,
                        "requirements": tags,
                        "required_skills": tags,
                        "preferred_skills": [],
                        "application_url": item.get("url") or "",
                        "posted_at": posted_at,
                        "is_active": True,
                    }
                    jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error fetching jobs from Arbeitnow: {e}")

        return jobs
