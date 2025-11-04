"""
Integration tests for RAG API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.integration
@pytest.mark.api
class TestRAGAPI:
    """Test RAG endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_rag_health_endpoint(self, client):
        """Test RAG health check"""
        response = client.get("/api/rag/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "embedding_service" in data
        assert "vector_dimension" in data

        assert data["status"] == "healthy"
        assert data["vector_dimension"] == 384

    def test_rag_query_valid(self, client):
        """Test RAG query with valid input"""
        payload = {
            "query": "How to improve aim?",
            "max_results": 5,
            "safety_level": "general"
        }

        response = client.post("/api/rag/query", json=payload)

        # Will succeed even if no documents (returns empty sources)
        assert response.status_code == 200

        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert "confidence" in data

        assert isinstance(data["sources"], list)
        assert isinstance(data["confidence"], float)

    def test_rag_query_empty_string(self, client):
        """Test RAG query with empty string"""
        payload = {
            "query": "",
            "max_results": 5
        }

        response = client.post("/api/rag/query", json=payload)
        assert response.status_code == 422  # Validation error

    def test_rag_query_too_long(self, client):
        """Test RAG query with text too long"""
        payload = {
            "query": "x" * 1001,  # Exceeds 1000 char limit
            "max_results": 5
        }

        response = client.post("/api/rag/query", json=payload)
        assert response.status_code == 422  # Validation error

    def test_rag_query_invalid_max_results(self, client):
        """Test RAG query with invalid max_results"""
        # Too high
        payload = {"query": "test", "max_results": 100}
        response = client.post("/api/rag/query", json=payload)
        assert response.status_code == 422

        # Too low
        payload = {"query": "test", "max_results": 0}
        response = client.post("/api/rag/query", json=payload)
        assert response.status_code == 422

    def test_rag_query_invalid_safety_level(self, client):
        """Test RAG query with invalid safety level"""
        payload = {
            "query": "test",
            "safety_level": "invalid_level"
        }

        response = client.post("/api/rag/query", json=payload)
        assert response.status_code == 422  # Validation error

        data = response.json()
        assert "detail" in data

    def test_rag_query_with_topics(self, client):
        """Test RAG query with topics filter"""
        payload = {
            "query": "aim training",
            "max_results": 3,
            "topics": ["training", "aim"],
            "safety_level": "training"
        }

        response = client.post("/api/rag/query", json=payload)
        assert response.status_code == 200

    def test_list_documents_empty(self, client):
        """Test listing documents when none exist"""
        response = client.get("/api/rag/documents")
        assert response.status_code == 200

        data = response.json()
        assert "documents" in data
        assert isinstance(data["documents"], list)

    def test_list_documents_with_filters(self, client):
        """Test listing documents with filters"""
        response = client.get("/api/rag/documents?doc_type=guide")
        assert response.status_code == 200

        data = response.json()
        assert "documents" in data

    def test_delete_nonexistent_document(self, client):
        """Test deleting non-existent document"""
        response = client.delete("/api/rag/documents/99999")
        # Should return 404 or 500 depending on implementation
        assert response.status_code in [404, 500]

    @pytest.mark.skip(reason="Requires actual PDF file upload")
    def test_ingest_pdf(self, client):
        """Test PDF ingestion"""
        # This would require creating a test PDF file
        pass

    def test_ingest_invalid_file_type(self, client):
        """Test uploading non-PDF file"""
        files = {"file": ("test.txt", b"not a pdf", "text/plain")}
        data = {
            "title": "Test Doc",
            "doc_type": "document",
            "safety": "general"
        }

        response = client.post("/api/rag/ingest/pdf", files=files, data=data)
        assert response.status_code == 400  # Bad request

    def test_ingest_pdf_invalid_safety_level(self, client):
        """Test PDF upload with invalid safety level"""
        # Create a dummy PDF-like file
        files = {"file": ("test.pdf", b"%PDF-1.4 fake", "application/pdf")}
        data = {
            "title": "Test Doc",
            "safety": "invalid_level"
        }

        response = client.post("/api/rag/ingest/pdf", files=files, data=data)
        assert response.status_code == 400  # Validation error for safety level
