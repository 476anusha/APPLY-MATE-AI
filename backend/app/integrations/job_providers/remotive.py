"""Remotive API job provider (free, public remote jobs)."""
import logging
from datetime import datetime, timezone
from typing import Any
import httpx

from app.integrations.job_providers.base import BaseJobProvider

logger = logging.getLogger(__name__)


class RemotiveJobProvider(BaseJobProvider):
    provider_name = "remotive"
    BASE_URL = "https://remotive.com/api/remote-jobs"

    async def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 20,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch listings from the Remotive remote jobs API."""
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["search"] = query

        jobs: list[dict[str, Any]] = []
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL, params=params)
                if resp.status_code != 200:
                    logger.warning(f"Remotive API returned status {resp.status_code}")
                    return []

                data = resp.json()
                raw_jobs = data.get("jobs", [])

                for item in raw_jobs[:limit]:
                    try:
                        ext_id = str(item.get("id"))
                        pub_date_str = item.get("publication_date")
                        posted_at = datetime.now(timezone.utc)
                        if pub_date_str:
                            try:
                                posted_at = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                            except Exception:
                                pass

                        job_type_str = (item.get("job_type") or "full_time").lower().replace("_", "-")
                        if job_type_str not in {"full-time", "part-time", "contract", "internship"}:
                            job_type_str = "full-time"

                        tags = item.get("tags") or []

                        normalized: dict[str, Any] = {
                            "external_id": ext_id,
                            "provider": self.provider_name,
                            "title": item.get("title") or "Remote Position",
                            "company": item.get("company_name") or "Remote Company",
                            "company_logo_url": item.get("company_logo"),
                            "location": item.get("candidate_required_location") or "Worldwide",
                            "is_remote": True,
                            "work_type": "remote",
                            "employment_type": job_type_str,
                            "experience_level": "mid",
                            "salary_min": None,
                            "salary_max": None,
                            "salary_currency": "USD",
                            "description": item.get("description") or "",
                            "requirements": tags,
                            "required_skills": tags,
                            "preferred_skills": [],
                            "application_url": item.get("url") or "",
                            "posted_at": posted_at,
                            "is_active": True,
                        }
                        jobs.append(normalized)
                    except Exception as parse_err:
                        logger.debug(f"Failed to parse Remotive job item: {parse_err}")
                        continue
        except Exception as e:
            logger.error(f"Error fetching jobs from Remotive: {e}")

        return jobs
