"""
Unit tests for embedding service
"""
import pytest
from app.services.embedding_service import EmbeddingService
from app.constants import VECTOR_DIMENSION


@pytest.mark.unit
class TestEmbeddingService:
    """Test embedding service functionality"""

    @pytest.fixture
    def embedding_service(self):
        """Create embedding service instance"""
        return EmbeddingService()

    def test_service_initialization(self, embedding_service):
        """Test service can be initialized"""
        assert embedding_service is not None
        assert hasattr(embedding_service, 'model')

    @pytest.mark.asyncio
    async def test_embed_text_returns_correct_dimension(self, embedding_service):
        """Test embedding returns correct vector dimension"""
        text = "This is a test sentence for embedding"
        embedding = await embedding_service.embed_text(text)

        assert isinstance(embedding, list)
        assert len(embedding) == VECTOR_DIMENSION
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_embed_empty_text(self, embedding_service):
        """Test embedding empty text"""
        embedding = await embedding_service.embed_text("")

        # Should still return a valid embedding (zero vector or similar)
        assert isinstance(embedding, list)
        assert len(embedding) == VECTOR_DIMENSION

    @pytest.mark.asyncio
    async def test_embed_multiple_texts(self, embedding_service):
        """Test embedding multiple different texts"""
        texts = [
            "How to improve aim?",
            "Best exercises for tracking",
            "KovaaK's training guide"
        ]

        embeddings = [await embedding_service.embed_text(text) for text in texts]

        # All should have correct dimension
        assert all(len(emb) == VECTOR_DIMENSION for emb in embeddings)

        # Embeddings should be different (not all zeros)
        assert embeddings[0] != embeddings[1]
        assert embeddings[1] != embeddings[2]

    @pytest.mark.asyncio
    async def test_embedding_consistency(self, embedding_service):
        """Test same text produces same embedding"""
        text = "consistent text for testing"

        embedding1 = await embedding_service.embed_text(text)
        embedding2 = await embedding_service.embed_text(text)

        # Should be very close (allowing for floating point differences)
        assert len(embedding1) == len(embedding2)
        for i in range(len(embedding1)):
            assert abs(embedding1[i] - embedding2[i]) < 0.0001

    @pytest.mark.asyncio
    async def test_embed_long_text(self, embedding_service):
        """Test embedding long text"""
        long_text = "This is a very long text. " * 100  # ~600 words

        embedding = await embedding_service.embed_text(long_text)

        assert isinstance(embedding, list)
        assert len(embedding) == VECTOR_DIMENSION
