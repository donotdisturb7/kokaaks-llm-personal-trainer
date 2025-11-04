"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.config import get_settings
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    """Get application settings"""
    return get_settings()


@pytest.fixture(scope="session")
async def test_engine(settings):
    """
    Create a test database engine
    Uses a separate test database to avoid affecting dev data
    """
    # Replace database name with test version
    test_db_url = settings.database_url.replace("/kovaaks_ai", "/kovaaks_ai_test")

    engine = create_async_engine(
        test_db_url,
        poolclass=NullPool,  # Disable connection pooling for tests
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test
    Rolls back after each test to keep tests isolated
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        async with session.begin():
            yield session
            await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for FastAPI tests"""
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture
def test_app(override_get_db):
    """FastAPI test application with overridden dependencies"""
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_user_data():
    """Mock user data for testing"""
    return {
        "kovaaks_username": "test_user",
        "email": "test@example.com",
        "created_at": "2024-01-01T00:00:00"
    }


@pytest.fixture
def mock_exercise_data():
    """Mock exercise data for testing"""
    return {
        "id": 1,
        "name": "1w6ts reload",
        "aim_type": "clicking",
        "difficulty": "medium",
        "description": "Static clicking exercise",
        "recommended_for": ["static_clicking", "precision"],
        "scenario_name": "1w6ts reload"
    }


@pytest.fixture
def mock_rag_query():
    """Mock RAG query for testing"""
    return {
        "query": "How to improve aim?",
        "max_results": 5,
        "topics": ["training", "aim"],
        "safety_level": "general"
    }


@pytest.fixture
def mock_conversation_data():
    """Mock conversation data for testing"""
    return {
        "id": "conv-123",
        "title": "Test Conversation",
        "messages": [
            {
                "id": "msg-1",
                "content": "Hello",
                "is_user": True,
                "created_at": "2024-01-01T00:00:00"
            },
            {
                "id": "msg-2",
                "content": "Hi! How can I help?",
                "is_user": False,
                "created_at": "2024-01-01T00:00:01"
            }
        ]
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "message": "This is a test response from the LLM",
        "model_used": "test-model",
        "response_time": 0.5
    }
