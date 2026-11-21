"""User and UserProfile schemas."""
import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    experience_level: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    education: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[int] = None
    experience_level: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    expected_salary_min: Optional[int] = None
    expected_salary_max: Optional[int] = None
    skills: Optional[List[str]] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: Optional[UserProfileResponse] = None
