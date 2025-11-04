"""
Integration tests for health check endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.integration
@pytest.mark.api
class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint returns correct info"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert "llm_provider" in data

        assert data["status"] == "running"
        assert data["llm_provider"] in ["groq", "ollama"]

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

        # Check configuration flags
        assert "llm_provider" in data
        assert "database_configured" in data
        assert "redis_configured" in data
        assert "kovaaks_username_configured" in data

        assert isinstance(data["database_configured"], bool)
        assert isinstance(data["redis_configured"], bool)
