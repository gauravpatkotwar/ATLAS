import pytest
import pytest_asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import Settings, DatabaseSettings
from app.core.database import Base, db
from app.modules.auth.domain.entities import User, Tenant, UserStatus, UserRole


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        environment="testing",
        debug=True,
        database=DatabaseSettings(
            host="localhost",
            port=5432,
            username="postgres",
            password="postgres",
            name="atlas_test",
        ),
    )


@pytest.fixture(scope="session")
def test_engine(test_settings):
    engine = create_async_engine(
        test_settings.database.async_url,
        poolclass=NullPool,
        echo=False,
    )
    yield engine


@pytest.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_tenant_repo():
    return AsyncMock()


@pytest.fixture
def mock_session_repo():
    return AsyncMock()


@pytest.fixture
def mock_api_key_repo():
    return AsyncMock()


@pytest.fixture
def mock_role_repo():
    return AsyncMock()


@pytest.fixture
def sample_tenant():
    return Tenant(
        id=uuid4(),
        name="Test Company",
        slug="test-company",
        is_active=True,
        subscription_plan="free",
    )


@pytest.fixture
def sample_user(sample_tenant):
    return User(
        id=uuid4(),
        tenant_id=sample_tenant.id,
        email="test@example.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        status=UserStatus.ACTIVE,
        roles=[UserRole.RECRUITER],
    )