"""Adzuna API job provider (requires ADZUNA_APP_ID and ADZUNA_API_KEY)."""
import logging
import os
from datetime import datetime, timezone
from typing import Any
import httpx

from app.integrations.job_providers.base import BaseJobProvider

logger = logging.getLogger(__name__)


class AdzunaJobProvider(BaseJobProvider):
    provider_name = "adzuna"
    BASE_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"

    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID", "").strip()
        self.app_key = os.getenv("ADZUNA_API_KEY", "").strip()

    async def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 20,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch jobs from Adzuna API, or return empty list if API keys are not configured."""
        if not self.app_id or not self.app_key:
            logger.info("Adzuna API credentials not configured; skipping Adzuna job search.")
            return []

        params: dict[str, Any] = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": min(limit, 50),
            "content-type": "application/json",
        }
        if query:
            params["what"] = query
        if location:
            params["where"] = location

        jobs: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL, params=params)
                if resp.status_code != 200:
                    logger.warning(f"Adzuna API returned HTTP {resp.status_code}: {resp.text}")
                    return []

                data = resp.json()
                results = data.get("results", [])
                for item in results:
                    ext_id = str(item.get("id"))
                    created_raw = item.get("created")
                    posted_at = datetime.now(timezone.utc)
                    if created_raw:
                        try:
                            posted_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                        except Exception:
                            pass

                    company_info = item.get("company") or {}
                    company_name = company_info.get("display_name") or "Hiring Company"
                    loc_info = item.get("location") or {}
                    loc_display = loc_info.get("display_name") or "United States"

                    sal_min = item.get("salary_min")
                    sal_max = item.get("salary_max")

                    normalized: dict[str, Any] = {
                        "external_id": ext_id,
                        "provider": self.provider_name,
                        "title": item.get("title") or "Software Engineer",
                        "company": company_name,
                        "company_logo_url": None,
                        "location": loc_display,
                        "is_remote": "remote" in (item.get("title") or "").lower() or "remote" in loc_display.lower(),
                        "work_type": "remote" if "remote" in loc_display.lower() else "onsite",
                        "employment_type": "full-time",
                        "experience_level": "mid",
                        "salary_min": int(sal_min) if sal_min else None,
                        "salary_max": int(sal_max) if sal_max else None,
                        "salary_currency": "USD",
                        "description": item.get("description") or "",
                        "requirements": [],
                        "required_skills": [],
                        "preferred_skills": [],
                        "application_url": item.get("redirect_url") or "",
                        "posted_at": posted_at,
                        "is_active": True,
                    }
                    jobs.append(normalized)
        except Exception as e:
            logger.error(f"Error fetching jobs from Adzuna: {e}")

        return jobs
