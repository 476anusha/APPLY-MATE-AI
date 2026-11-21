"""Notification schemas."""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    message: str
    is_read: bool
    action_url: Optional[str] = None
    notif_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class MarkNotificationReadRequest(BaseModel):
    is_read: bool = True
