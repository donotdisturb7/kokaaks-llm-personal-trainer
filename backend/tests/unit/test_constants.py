"""
Unit tests for constants module
"""
import pytest
from app.constants import (
    VECTOR_DIMENSION,
    IVFFLAT_LISTS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    AIM_TRAINING_SYSTEM_PROMPT,
    SAFETY_LEVELS,
    DEFAULT_SAFETY_LEVEL,
    DOCUMENT_TYPES,
    DEFAULT_DOCUMENT_TYPE
)


@pytest.mark.unit
class TestConstants:
    """Test constants are properly defined"""

    def test_vector_dimension(self):
        """Test vector dimension is correct for FastEmbed"""
        assert VECTOR_DIMENSION == 384
        assert isinstance(VECTOR_DIMENSION, int)

    def test_ivfflat_lists(self):
        """Test IVFFLAT configuration"""
        assert IVFFLAT_LISTS == 100
        assert isinstance(IVFFLAT_LISTS, int)

    def test_chunk_configuration(self):
        """Test RAG chunk configuration"""
        assert DEFAULT_CHUNK_SIZE == 500
        assert DEFAULT_CHUNK_OVERLAP == 50
        assert DEFAULT_CHUNK_OVERLAP < DEFAULT_CHUNK_SIZE

    def test_aim_training_prompt(self):
        """Test system prompt is defined"""
        assert isinstance(AIM_TRAINING_SYSTEM_PROMPT, str)
        assert len(AIM_TRAINING_SYSTEM_PROMPT) > 0
        assert "KovaaK's" in AIM_TRAINING_SYSTEM_PROMPT
        assert "aim" in AIM_TRAINING_SYSTEM_PROMPT.lower()

    def test_safety_levels(self):
        """Test safety levels are defined"""
        assert isinstance(SAFETY_LEVELS, list)
        assert len(SAFETY_LEVELS) == 3
        assert "medical" in SAFETY_LEVELS
        assert "general" in SAFETY_LEVELS
        assert "training" in SAFETY_LEVELS
        assert DEFAULT_SAFETY_LEVEL in SAFETY_LEVELS

    def test_document_types(self):
        """Test document types are defined"""
        assert isinstance(DOCUMENT_TYPES, list)
        assert len(DOCUMENT_TYPES) > 0
        assert "document" in DOCUMENT_TYPES
        assert DEFAULT_DOCUMENT_TYPE in DOCUMENT_TYPES
