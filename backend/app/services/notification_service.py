"""Notification service for user alerts and activity tracking."""
from uuid import UUID

from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.notification import Notification


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: UUID,
        type: str,
        title: str,
        message: str,
        action_url: str | None = None,
        metadata: dict | None = None,
    ) -> Notification:
        """Create a notification for a user."""
        notif = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            action_url=action_url,
            notif_metadata=metadata,
            is_read=False,
        )
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def get_unread_notifications(
        self, user_id: UUID, limit: int = 20
    ) -> list[Notification]:
        """Fetch all unread notifications for a user."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .order_by(desc(Notification.created_at))
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_all_notifications(
        self, user_id: UUID, skip: int = 0, limit: int = 50
    ) -> list[Notification]:
        """Fetch all notifications for a user with pagination."""
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(desc(Notification.created_at))
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        """Mark a single notification as read."""
        stmt = select(Notification).where(Notification.id == notification_id)
        res = await self.db.execute(stmt)
        notif = res.scalar_one_or_none()
        if not notif:
            raise NotFoundError("Notification not found.")
        if notif.user_id != user_id:
            raise PermissionDeniedError("Access denied.")

        notif.is_read = True
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications for a user as read. Returns count updated."""
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount  # type: ignore
