"""Resume repository — resume-specific queries and mutations."""
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resume import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    def __init__(self, db: AsyncSession):
        super().__init__(Resume, db)

    async def get_by_user(self, user_id: UUID) -> list[Resume]:
        """Return all resumes belonging to a user, newest first."""
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_extracted_data(self, resume_id: UUID) -> Resume | None:
        """Fetch a resume and eagerly load its extracted data."""
        result = await self.db.execute(
            select(Resume)
            .options(selectinload(Resume.extracted_data))
            .where(Resume.id == resume_id)
        )
        return result.scalar_one_or_none()

    async def set_default(self, user_id: UUID, resume_id: UUID) -> Resume | None:
        """
        Set one resume as the default for a user.
        Clears is_default on all other resumes for the same user.
        """
        # Clear all existing defaults for user
        await self.db.execute(
            update(Resume)
            .where(Resume.user_id == user_id)
            .values(is_default=False)
        )
        # Set new default
        resume = await self.get(resume_id)
        if not resume or resume.user_id != user_id:
            return None
        resume.is_default = True
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def get_default_resume(self, user_id: UUID) -> Resume | None:
        """Return the user's default resume, or None if unset."""
        result = await self.db.execute(
            select(Resume).where(
                Resume.user_id == user_id,
                Resume.is_default == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()
