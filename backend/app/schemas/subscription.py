"""Subscription, billing and usage schemas."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    display_name: str
    price_monthly: float
    price_yearly: float
    max_resume_uploads: int
    max_ai_analyses_per_month: int
    max_cover_letters_per_month: int
    max_job_matches_per_month: int
    features: List[str]
    is_active: bool


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    plan_id: uuid.UUID
    status: str
    current_period_start: datetime
    current_period_end: datetime
    payment_provider: Optional[str] = None
    plan: Optional[PlanResponse] = None


class UsageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action_type: str
    used: int
    limit: int
    period_start: datetime
    period_end: datetime
