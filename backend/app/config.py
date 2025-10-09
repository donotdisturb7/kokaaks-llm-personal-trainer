"""
Configuration de l'application
Gère les variables d'environnement et la configuration Ollama
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    # Configuration Ollama - modulaire pour localhost ou IP
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "llama2"
    ollama_timeout: int = 30
    
    # Configuration Base de données
    database_url: str = "postgresql://user:password@localhost:5432/kovaaks_ai"
    database_echo: bool = False
    
    # Configuration Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Configuration API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    
    # Configuration CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Configuration KovaaK's API
    kovaaks_api_base_url: str = "https://api.kovaaks.com"
    kovaaks_api_key: Optional[str] = None
    
    # Configuration Logs
    log_level: str = "INFO"
    log_format: str = "json"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
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
