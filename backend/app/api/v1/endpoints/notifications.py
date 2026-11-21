"""Notifications endpoint."""
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()


@router.get("/")
async def list_notifications(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.notification import Notification
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == str(current_user.id))
        .order_by(Notification.is_read.asc(), Notification.created_at.desc())
        .limit(50)
    )
    notifs = result.scalars().all()
    return [
        {
            "id": str(n.id), "type": n.type, "title": n.title,
            "message": n.message, "is_read": n.is_read,
            "action_url": n.action_url, "created_at": str(n.created_at),
        }
        for n in notifs
    ]


@router.put("/{notif_id}/read")
async def mark_read(
    notif_id: str,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.notification import Notification
    try:
        uid = uuid.UUID(notif_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Notification not found")
    result = await db.execute(
        select(Notification).where(
            Notification.id == uid, Notification.user_id == str(current_user.id)
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    return {"id": notif_id, "is_read": True}


@router.put("/read-all")
async def mark_all_read(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    from app.models.notification import Notification
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == str(current_user.id), Notification.is_read == False
        )
    )
    notifs = result.scalars().all()
    for n in notifs:
        n.is_read = True
    await db.commit()
    return {"marked_read": len(notifs)}
