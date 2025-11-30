from openai import AsyncOpenAI
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

from app.config import Settings
from app.constants import AIM_TRAINING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GroqMessage(BaseModel):
    """Modèle pour un message dans la conversation"""
    role: str  # "user", "assistant" ou "system"
    content: str


class GroqService:
    """Service pour interagir avec Groq via OpenAI SDK"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = settings.groq_model
        
    async def __aenter__(self):
        """Context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.client.close()
    
    async def health_check(self) -> bool:
        """
        Vérifie si Groq est accessible
        Retourne True si la connexion fonctionne
        """
        try:
            # Test avec un prompt simple
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion Groq: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:

        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """
        Génère une réponse à partir d'un prompt
        Utilise le modèle spécifié ou le modèle par défaut
        """
        model = model or self.model
        
        # Construction des messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération Groq: {e}")
            return "Désolé, une erreur est survenue lors de la génération de la réponse."
    
    async def generate_aim_training_advice(
        self,
        user_question: str,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Génère des conseils spécialisés en entraînement de visée
        Utilise un prompt système spécialisé pour KovaaK's
        """
        # Ajout des stats utilisateur si disponibles
        if user_stats:
            stats_context = f"\n\nStatistiques du joueur: {user_stats}"
            user_question += stats_context

        return await self.generate_response(
            prompt=user_question,
            system_prompt=AIM_TRAINING_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=1024
        )
    
    async def close(self):
        """Ferme la connexion HTTP"""
        await self.client.close()


# Fonction utilitaire pour créer une instance du service
def create_groq_service(settings: Settings) -> GroqService:
    """Crée une instance du service Groq"""
    return GroqService(settings)


