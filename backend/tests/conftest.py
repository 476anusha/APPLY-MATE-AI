"""Pytest configuration and async test fixtures."""
import asyncio
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.security import create_access_token, get_password_hash
from app.database import Base
from app.main import app
from app.models.user import User
from app.models.user_profile import UserProfile

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test async engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a test database session."""
    session_factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient for FastAPI endpoint testing."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in database."""
    user = User(
        id=uuid4(),
        email="testuser@example.com",
        hashed_password=get_password_hash("SecretPassword123!"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    profile = UserProfile(
        user_id=user.id,
        skills=["Python", "FastAPI", "React"],
        preferred_roles=["Software Engineer"],
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """Generate JWT access token for test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def auth_headers(test_user_token: str) -> dict[str, str]:
    """Return headers with Bearer token."""
    return {"Authorization": f"Bearer {test_user_token}"}
