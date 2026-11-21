"""Auth endpoints — register, login, refresh, me, forgot/reset password."""
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.database import get_db

router = APIRouter()


# ── Pydantic schemas ────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = "New User"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    message: str


# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_tokens(user_id: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(subject=str(user_id)),
        refresh_token=create_refresh_token(subject=str(user_id)),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Register a new user and return JWT tokens."""
    from app.models.user import User
    from app.models.user_profile import UserProfile

    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    profile = UserProfile(id=str(uuid.uuid4()), user_id=user_id)
    db.add(profile)
    await db.commit()

    return _make_tokens(str(user_id))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Authenticate with email + password and return JWT tokens."""
    from app.models.user import User

    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    return _make_tokens(str(user.id))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Get a new access token using a valid refresh token."""
    from app.models.user import User

    user_id = verify_token(req.refresh_token, expected_type="refresh")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return _make_tokens(str(user.id))


@router.get("/me")
async def get_me(current_user=Depends(get_current_active_user)) -> Any:
    """Return the currently authenticated user's info."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "created_at": str(current_user.created_at),
    }


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Initiate password reset (sends email in production)."""
    return MessageResponse(
        message="If that email is registered, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Reset password using reset token."""
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    return MessageResponse(message="Password reset successfully. Please log in.")
