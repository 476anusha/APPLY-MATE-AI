"""Profile endpoints — real DB implementation."""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.database import get_db

router = APIRouter()


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    education: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    education: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    experience_level: Optional[str] = None
    skills: List[str] = []
    preferred_roles: List[str] = []
    preferred_locations: List[str] = []
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# ── Helper ────────────────────────────────────────────────────────────────────

def _build_profile_response(user: Any, profile: Any) -> ProfileResponse:
    """Merge User + UserProfile ORM objects into a ProfileResponse."""
    return ProfileResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        phone=getattr(profile, "phone", None) if profile else None,
        location=getattr(profile, "location", None) if profile else None,
        bio=getattr(profile, "bio", None) if profile else None,
        education=getattr(profile, "education", None) if profile else None,
        university=getattr(profile, "university", None) if profile else None,
        graduation_year=getattr(profile, "graduation_year", None) if profile else None,
        experience_level=getattr(profile, "experience_level", None) if profile else None,
        skills=list(getattr(profile, "skills", None) or []) if profile else [],
        preferred_roles=list(getattr(profile, "preferred_roles", None) or []) if profile else [],
        preferred_locations=list(getattr(profile, "preferred_locations", None) or []) if profile else [],
        expected_salary_min=getattr(profile, "expected_salary_min", None) if profile else None,
        expected_salary_max=getattr(profile, "expected_salary_max", None) if profile else None,
        linkedin_url=getattr(profile, "linkedin_url", None) if profile else None,
        github_url=getattr(profile, "github_url", None) if profile else None,
        portfolio_url=getattr(profile, "portfolio_url", None) if profile else None,
        avatar_url=getattr(profile, "avatar_url", None) if profile else None,
    )


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retrieve the current user's full profile (User + UserProfile joined)."""
    from app.models.user_profile import UserProfile

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == str(current_user.id))
    )
    profile = result.scalar_one_or_none()
    return _build_profile_response(current_user, profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: Any = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Update the current user's profile. Creates UserProfile row if absent."""
    from app.models.user import User
    from app.models.user_profile import UserProfile
    import uuid

    # Update full_name on User record if provided
    if req.full_name is not None and req.full_name != current_user.full_name:
        result_user = await db.execute(select(User).where(User.id == current_user.id))
        db_user = result_user.scalar_one()
        db_user.full_name = req.full_name
        await db.flush()

    # Fetch or create UserProfile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == str(current_user.id))
    )
    profile = result.scalar_one_or_none()

    if profile is None:
        profile = UserProfile(id=str(uuid.uuid4()), user_id=str(current_user.id))
        db.add(profile)

    # Apply updates from request
    update_fields = {
        "phone": req.phone,
        "location": req.location,
        "bio": req.bio,
        "education": req.education,
        "university": req.university,
        "graduation_year": req.graduation_year,
        "experience_level": req.experience_level,
        "skills": req.skills,
        "preferred_roles": req.preferred_roles,
        "preferred_locations": req.preferred_locations,
        "expected_salary_min": req.expected_salary_min,
        "expected_salary_max": req.expected_salary_max,
        "linkedin_url": req.linkedin_url,
        "github_url": req.github_url,
        "portfolio_url": req.portfolio_url,
    }
    for field, value in update_fields.items():
        if value is not None:
            setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    # Refresh user to get latest full_name
    result_user = await db.execute(select(User).where(User.id == current_user.id))
    fresh_user = result_user.scalar_one()

    return _build_profile_response(fresh_user, profile)
