"""
Integration tests for exercises API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.integration
@pytest.mark.api
class TestExercisesAPI:
    """Test exercises endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_get_all_exercises(self, client):
        """Test retrieving all exercises"""
        response = client.get("/api/exercises/")
        assert response.status_code == 200

        data = response.json()
        assert "exercises" in data
        assert "total" in data
        assert isinstance(data["exercises"], list)
        assert data["total"] > 0

        # Check exercise structure
        if len(data["exercises"]) > 0:
            exercise = data["exercises"][0]
            assert "id" in exercise
            assert "name" in exercise
            assert "aim_type" in exercise
            assert "difficulty" in exercise

    def test_get_exercises_with_aim_type_filter(self, client):
        """Test filtering exercises by aim type"""
        response = client.get("/api/exercises/?aim_type=clicking")
        assert response.status_code == 200

        data = response.json()
        assert "exercises" in data
        assert "filters" in data
        assert data["filters"]["aim_type"] == "clicking"

        # All exercises should be clicking type
        for exercise in data["exercises"]:
            assert exercise["aim_type"] == "clicking"

    def test_get_exercises_with_difficulty_filter(self, client):
        """Test filtering exercises by difficulty"""
        response = client.get("/api/exercises/?difficulty=easy")
        assert response.status_code == 200

        data = response.json()
        assert data["filters"]["difficulty"] == "easy"

        # All exercises should be easy
        for exercise in data["exercises"]:
            assert exercise["difficulty"] == "easy"

    def test_get_exercises_with_invalid_aim_type(self, client):
        """Test invalid aim_type filter"""
        response = client.get("/api/exercises/?aim_type=invalid")
        # Should return 422 validation error
        assert response.status_code == 422

    def test_get_exercises_with_limit(self, client):
        """Test limiting number of results"""
        response = client.get("/api/exercises/?limit=3")
        assert response.status_code == 200

        data = response.json()
        assert len(data["exercises"]) <= 3

    def test_get_specific_exercise(self, client):
        """Test retrieving a specific exercise by ID"""
        response = client.get("/api/exercises/1")
        assert response.status_code == 200

        data = response.json()
        assert "exercise" in data
        exercise = data["exercise"]
        assert exercise["id"] == 1
        assert "name" in exercise
        assert "aim_type" in exercise

    def test_get_nonexistent_exercise(self, client):
        """Test retrieving non-existent exercise"""
        response = client.get("/api/exercises/99999")
        assert response.status_code == 404

    def test_get_recommendations(self, client):
        """Test recommendations endpoint"""
        response = client.get("/api/exercises/recommendations")
        assert response.status_code == 200

        data = response.json()
        assert "user" in data
        assert "recommendations" in data
        assert "analysis" in data

        # Check recommendations structure
        assert isinstance(data["recommendations"], list)

        # Check analysis structure
        analysis = data["analysis"]
        assert "trend" in analysis
        assert "weak_points" in analysis
        assert "strengths" in analysis
        assert "reasoning" in analysis

    def test_get_recommendations_with_limit(self, client):
        """Test recommendations with custom limit"""
        response = client.get("/api/exercises/recommendations?limit=3")
        assert response.status_code == 200

        data = response.json()
        assert len(data["recommendations"]) <= 3

    def test_get_recommendations_invalid_limit(self, client):
        """Test recommendations with invalid limit"""
        # Limit too high
        response = client.get("/api/exercises/recommendations?limit=100")
        assert response.status_code == 422

        # Limit too low
        response = client.get("/api/exercises/recommendations?limit=0")
        assert response.status_code == 422
