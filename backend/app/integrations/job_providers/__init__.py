"""Job provider integrations."""
from app.integrations.job_providers.adzuna import AdzunaJobProvider
from app.integrations.job_providers.arbeitnow import ArbeitnowJobProvider
from app.integrations.job_providers.base import BaseJobProvider
from app.integrations.job_providers.demo_provider import DemoJobProvider
from app.integrations.job_providers.remotive import RemotiveJobProvider

__all__ = [
    "BaseJobProvider",
    "RemotiveJobProvider",
    "ArbeitnowJobProvider",
    "AdzunaJobProvider",
    "DemoJobProvider",
]
