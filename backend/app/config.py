"""
Configuration de l'application
Gère les variables d'environnement et la configuration Ollama
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices, field_validator
from typing import List, Optional
import os
import json


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # Configuration du provider IA (ollama ou groq)
    llm_provider: str = "ollama"  # "ollama" ou "groq"
    
    # Configuration Ollama - modulaire pour localhost ou IP
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "llama2"
    ollama_timeout: int = 30
    
    # Configuration Groq
    groq_api_key: Optional[str] = None
    groq_model: str = "openai/gpt-oss-120b"
    
    # Configuration utilisateur KovaaK's (pour l'API)
    # Supporte les deux variables d'env: KOVAAKS_USERNAME ou CURRENT_USER_KOVAAKS_USERNAME
    kovaaks_username: str = Field(
        default="",
        validation_alias=AliasChoices("KOVAAKS_USERNAME", "CURRENT_USER_KOVAAKS_USERNAME"),
    )
    
    # Configuration Base de données
    database_url: str = "postgresql+asyncpg://kovaaks:kovaaks_pass@localhost:5434/kovaaks_ai"
    database_echo: bool = False
    
    # Configuration Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Configuration API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # Configuration CORS
    cors_origins: List[str] = ["http://localhost:3001", "http://127.0.0.1:3001"]

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from JSON string if needed"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as a single origin
                return [v]
        return v

    # Configuration KovaaK's Proxy
    kovaaks_proxy_url: str = "http://localhost:9000"
    
    # Configuration Redis Cache TTL
    redis_cache_ttl: int = 300  # 5 minutes par défaut
    redis_stats_ttl: int = 3600  # 1 heure pour les stats
    
    # Configuration Logs
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # ignore unknown env variables (e.g., legacy keys)
    )
    
    @property
    def ollama_base_url(self) -> str:
        """URL de base pour Ollama - modulaire localhost/IP"""
        return f"http://{self.ollama_host}:{self.ollama_port}"
    
    @property
    def ollama_generate_url(self) -> str:
        """URL pour la génération de texte avec Ollama"""
        return f"{self.ollama_base_url}/api/generate"
    
    @property
    def ollama_models_url(self) -> str:
        """URL pour lister les modèles Ollama"""
        return f"{self.ollama_base_url}/api/tags"


# Instance globale des paramètres
settings = Settings()


def get_settings() -> Settings:
    """Fonction pour obtenir les paramètres (pour l'injection de dépendance)"""
    return settings
