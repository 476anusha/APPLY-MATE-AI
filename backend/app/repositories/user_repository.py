"""User repository — user-specific queries and mutations."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.user_profile import UserProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email address (case-insensitive)."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def create_user(
        self, email: str, hashed_password: str, full_name: str
    ) -> User:
        """Create a new user record."""
        user = User(
            email=email.lower().strip(),
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, user_id: UUID, new_hashed_password: str) -> User | None:
        """Update a user's hashed password."""
        user = await self.get(user_id)
        if not user:
            return None
        user.hashed_password = new_hashed_password
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_with_profile(self, user_id: UUID) -> User | None:
        """Fetch a user and eagerly load their profile."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def set_verified(self, user_id: UUID) -> User | None:
        """Mark a user's email as verified."""
        user = await self.get(user_id)
        if not user:
            return None
        user.is_verified = True
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
