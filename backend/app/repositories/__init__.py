"""Repositories package."""
from app.repositories.application_repository import ApplicationRepository
from app.repositories.base import BaseRepository
from app.repositories.job_repository import JobRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ResumeRepository",
    "JobRepository",
    "ApplicationRepository",
]
