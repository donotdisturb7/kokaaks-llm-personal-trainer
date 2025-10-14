"""
Service LLM Manager - Gère le choix entre Ollama et Groq
Interface unifiée pour interagir avec différents providers IA
"""
from typing import Dict, Any, Optional, List, Protocol
import logging

from app.config import Settings
from app.services.ollama_service import OllamaService, create_ollama_service
from app.services.groq_service import GroqService, create_groq_service

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocol pour définir l'interface des providers IA"""
    
    async def health_check(self) -> bool:
        """Vérifie si le provider est accessible"""
        ...
    
    async def get_available_models(self) -> List[str]:
        """Récupère la liste des modèles disponibles"""
        ...
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        ...
    
    async def generate_aim_training_advice(
        self, 
        user_question: str,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """Génère des conseils spécialisés en entraînement de visée"""
        ...
    
    async def close(self):
        """Ferme la connexion"""
        ...


class LLMService:
    """Service manager pour gérer les différents providers IA"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider_name = settings.llm_provider.lower()
        self._provider: Optional[LLMProvider] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self._provider = self._create_provider()
        if hasattr(self._provider, '__aenter__'):
            await self._provider.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._provider and hasattr(self._provider, '__aexit__'):
            await self._provider.__aexit__(exc_type, exc_val, exc_tb)
    
    def _create_provider(self) -> LLMProvider:
        """Crée l'instance du provider basé sur la configuration"""
        if self.provider_name == "groq":
            logger.info("Utilisation du provider Groq")
            return create_groq_service(self.settings)
        elif self.provider_name == "ollama":
            logger.info("Utilisation du provider Ollama")
            return create_ollama_service(self.settings)
        else:
            logger.warning(f"Provider '{self.provider_name}' non reconnu, utilisation d'Ollama par défaut")
            return create_ollama_service(self.settings)
    
    @property
    def provider(self) -> LLMProvider:
        """Accède au provider actuel"""
        if self._provider is None:
            self._provider = self._create_provider()
        return self._provider
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé du provider actuel
        Retourne des informations sur le provider et son état
        """
        is_healthy = await self.provider.health_check()
        return {
            "provider": self.provider_name,
            "status": "healthy" if is_healthy else "unhealthy",
            "model": self._get_current_model()
        }
    
    def _get_current_model(self) -> str:
        """Récupère le modèle actuellement utilisé"""
        if self.provider_name == "groq":
            return self.settings.groq_model
        else:
            return self.settings.ollama_model
    
    async def get_available_models(self) -> List[str]:
        """Récupère la liste des modèles disponibles pour le provider actuel"""
        return await self.provider.get_available_models()
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        return await self.provider.generate_response(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt
        )
    
    async def generate_aim_training_advice(
        self, 
        user_question: str,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """Génère des conseils spécialisés en entraînement de visée"""
        return await self.provider.generate_aim_training_advice(
            user_question=user_question,
            user_stats=user_stats
        )
    
    async def close(self):
        """Ferme la connexion du provider"""
        if self._provider:
            await self._provider.close()


def create_llm_service(settings: Settings) -> LLMService:
    """Crée une instance du service LLM"""
    return LLMService(settings)


