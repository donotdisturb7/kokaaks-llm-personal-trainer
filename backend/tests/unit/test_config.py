"""
Unit tests for configuration
"""
import pytest
from app.config import get_settings, Settings


@pytest.mark.unit
class TestSettings:
    """Test application settings"""

    def test_get_settings(self):
        """Test settings can be retrieved"""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_settings_has_required_fields(self):
        """Test settings has all required configuration"""
        settings = get_settings()

        # LLM configuration
        assert hasattr(settings, 'llm_provider')
        assert settings.llm_provider in ['groq', 'ollama']

        # Database configuration
        assert hasattr(settings, 'database_url')
        assert isinstance(settings.database_url, str)
        assert 'postgresql' in settings.database_url

        # Redis configuration
        assert hasattr(settings, 'redis_url')
        assert isinstance(settings.redis_url, str)
        assert 'redis' in settings.redis_url

        # API configuration
        assert hasattr(settings, 'api_host')
        assert hasattr(settings, 'api_port')
        assert hasattr(settings, 'api_debug')

        # CORS configuration
        assert hasattr(settings, 'cors_origins')
        assert isinstance(settings.cors_origins, list)

    def test_settings_defaults(self):
        """Test default values are reasonable"""
        settings = get_settings()

        # API defaults
        assert settings.api_host == "0.0.0.0"
        assert isinstance(settings.api_port, int)
        assert 1000 < settings.api_port < 65535

        # Redis defaults
        assert hasattr(settings, 'redis_cache_ttl')
        assert settings.redis_cache_ttl > 0

    def test_cors_origins_is_list(self):
        """Test CORS origins is properly formatted"""
        settings = get_settings()
        assert isinstance(settings.cors_origins, list)

        # Should contain localhost origins
        has_localhost = any('localhost' in origin for origin in settings.cors_origins)
        assert has_localhost, "CORS should include localhost for development"
