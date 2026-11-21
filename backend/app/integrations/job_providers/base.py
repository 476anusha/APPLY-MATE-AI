"""Abstract base class for job providers."""
from abc import ABC, abstractmethod
from typing import Any


class BaseJobProvider(ABC):
    """Abstract interface that all external job providers must implement."""

    provider_name: str = "base"

    @abstractmethod
    async def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        limit: int = 20,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Fetch job listings and return normalized job dictionaries conforming to Job model.
        Normalized dict keys:
            - external_id: str
            - provider: str (e.g. remotive/arbeitnow/adzuna/demo)
            - title: str
            - company: str
            - company_logo_url: str | None
            - location: str
            - is_remote: bool
            - work_type: str ("remote", "hybrid", "onsite")
            - employment_type: str ("full-time", "part-time", "contract", "internship")
            - experience_level: str ("entry", "mid", "senior")
            - salary_min: int | None
            - salary_max: int | None
            - salary_currency: str | None
            - description: str
            - requirements: list[str] | dict | None
            - required_skills: list[str] | None
            - application_url: str
            - posted_at: datetime
        """
        pass
