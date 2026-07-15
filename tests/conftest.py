import pytest
from typing import AsyncGenerator, Dict, Any, List
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from atlas.database.models import Base
from atlas.database.session import get_db
from atlas.main import app
from atlas.ai.base import AIProvider, EmbeddingProvider

# Test database using SQLite memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Mock AI providers to avoid running Ollama in pipeline tests


class MockAIProvider(AIProvider):
    async def extract_candidate_data(self, resume_text: str) -> Dict[str, Any]:
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "location": "San Francisco, CA",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "education": [
                {
                    "institution": "Stanford",
                    "degree": "MS Computer Science",
                    "year": "2022",
                }
            ],
            "experience": [
                {
                    "company": "Tech Corp",
                    "role": "Backend Engineer",
                    "duration": "2 years",
                    "description": "Developed async python web applications.",
                }
            ],
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "portfolio": "https://johndoe.dev",
            "summary": "Experienced Python developer.",
        }

    async def generate_summary(self, resume_text: str) -> str:
        return "Experienced Python developer specializing in FastAPI, clean code, and database design."

    async def chat_copilot(self, query: str, history: List[Dict[str, str]]) -> str:
        return f"Mock Copilot response for query: {query}"

    async def explain_recommendation(
        self, candidate_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> str:
        return "Matches requirements: strong Python background and experience building REST APIs."


class MockEmbeddingProvider(EmbeddingProvider):
    async def generate_embedding(self, text: str) -> List[float]:
        # Return mock 768-dimension vector
        return [0.05] * 768


@pytest.fixture(scope="function", autouse=True)
async def init_db() -> AsyncGenerator[None, None]:
    """Startup table generation and teardown cleanup."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Retrieves isolated DB session for tests."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client with mocked DB session injector."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
def mock_ai_factory(monkeypatch):
    """Mocks AI provider singletons inside the factory."""
    from atlas.ai.factory import AIProviderFactory

    mock_ai = MockAIProvider()
    mock_embed = MockEmbeddingProvider()

    AIProviderFactory._ai_cache["ollama"] = mock_ai
    AIProviderFactory._embed_cache["ollama"] = mock_embed
    yield
