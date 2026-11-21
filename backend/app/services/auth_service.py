"""Authentication and user account management service."""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.subscription import SubscriptionPlan, UserSubscription
from app.models.user import User
from app.models.user_profile import UserProfile
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def get_or_create_free_plan(self) -> SubscriptionPlan:
        """Fetch or create the default Free subscription plan."""
        stmt = select(SubscriptionPlan).where(SubscriptionPlan.name == "free")
        res = await self.db.execute(stmt)
        plan = res.scalar_one_or_none()
        if not plan:
            plan = SubscriptionPlan(
                name="free",
                display_name="Free Plan",
                price_monthly=0.0,
                price_yearly=0.0,
                max_resume_uploads=2,
                max_ai_analyses_per_month=5,
                max_cover_letters_per_month=5,
                max_job_matches_per_month=20,
                features=["2 Resume Uploads", "5 AI Analyses/mo", "Basic Tracker"],
                is_active=True,
            )
            self.db.add(plan)
            await self.db.commit()
            await self.db.refresh(plan)
        return plan

    async def register_user(
        self, email: str, password: str, full_name: str
    ) -> dict[str, Any]:
        """
        Register a new user:
        1. Checks uniqueness
        2. Creates User
        3. Creates UserProfile
        4. Creates UserSubscription with Free plan
        Returns user and tokens.
        """
        clean_email = email.lower().strip()
        existing = await self.user_repo.get_by_email(clean_email)
        if existing:
            raise ConflictError(f"User with email '{clean_email}' already exists.")

        hashed_pw = get_password_hash(password)
        user = User(
            email=clean_email,
            hashed_password=hashed_pw,
            full_name=full_name.strip(),
            is_active=True,
            is_verified=False,
        )
        self.db.add(user)
        await self.db.flush()  # assign user.id

        # Create Profile
        profile = UserProfile(
            user_id=user.id,
            preferred_roles=[],
            preferred_locations=[],
            skills=[],
        )
        self.db.add(profile)

        # Ensure default Free subscription plan exists
        free_plan = await self.get_or_create_free_plan()

        # Create Free UserSubscription
        now = datetime.now(timezone.utc)
        sub = UserSubscription(
            user_id=user.id,
            plan_id=free_plan.id,
            status="active",
            current_period_start=now,
            current_period_end=now + timedelta(days=365 * 10),  # perpetual free tier
            payment_provider=None,
        )
        self.db.add(sub)

        await self.db.commit()
        await self.db.refresh(user)

        # Generate tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def authenticate_user(self, email: str, password: str) -> dict[str, Any]:
        """Verify user credentials and return auth tokens."""
        clean_email = email.lower().strip()
        user = await self.user_repo.get_by_email(clean_email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("User account is disabled.")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, str]:
        """Validate refresh token and issue a new access token."""
        user_id_str = verify_token(refresh_token, expected_type="refresh")
        if not user_id_str:
            raise AuthenticationError("Invalid or expired refresh token.")

        user = await self.user_repo.get(UUID(user_id_str))
        if not user or not user.is_active:
            raise AuthenticationError("User not found or disabled.")

        new_access_token = create_access_token(subject=str(user.id))
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    async def request_password_reset(self, email: str) -> str:
        """
        Generate password reset token.
        Returns the reset token (to be sent via email or displayed).
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            # We don't leak user existence in production, but generate a dummy or return token
            return ""

        expire = datetime.now(timezone.utc) + timedelta(hours=2)
        payload = {
            "sub": str(user.id),
            "exp": expire,
            "type": "reset_password",
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using token."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "reset_password":
                raise ValidationError("Invalid reset token type.")
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise ValidationError("Invalid reset token payload.")
        except JWTError:
            raise ValidationError("Invalid or expired reset token.")

        user_id = UUID(user_id_str)
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundError("User not found.")

        hashed_pw = get_password_hash(new_password)
        await self.user_repo.update_password(user_id, hashed_pw)
        return True

    async def generate_email_verification_token(self, user_id: UUID) -> str:
        """Generate email verification JWT token."""
        expire = datetime.now(timezone.utc) + timedelta(days=2)
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "type": "verify_email",
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    async def verify_email(self, token: str) -> bool:
        """Verify user email from verification token."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "verify_email":
                raise ValidationError("Invalid verification token type.")
            user_id_str = payload.get("sub")
            if not user_id_str:
                raise ValidationError("Invalid token.")
        except JWTError:
            raise ValidationError("Invalid or expired verification token.")

        user = await self.user_repo.set_verified(UUID(user_id_str))
        if not user:
            raise NotFoundError("User not found.")
        return True
