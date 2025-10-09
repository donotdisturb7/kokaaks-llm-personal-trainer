"""
Service Ollama - Connexion modulaire pour localhost ou IP
Gère la communication avec l'API Ollama pour l'IA
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

from app.config import Settings

logger = logging.getLogger(__name__)


class OllamaMessage(BaseModel):
    """Modèle pour un message dans la conversation"""
    role: str  # "user" ou "assistant"
    content: str


class OllamaRequest(BaseModel):
    """Modèle pour une requête à Ollama"""
    model: str
    messages: List[OllamaMessage]
    stream: bool = False
    options: Optional[Dict[str, Any]] = None


class OllamaResponse(BaseModel):
    """Modèle pour la réponse d'Ollama"""
    model: str
    created_at: str
    message: OllamaMessage
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None


class OllamaService:
    """Service pour interagir avec Ollama - connexion modulaire"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = httpx.AsyncClient(timeout=settings.ollama_timeout)
        self.base_url = settings.ollama_base_url
        
    async def __aenter__(self):
        """Context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """
        Vérifie si Ollama est accessible
        Retourne True si la connexion fonctionne
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erreur de connexion Ollama: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """
        Récupère la liste des modèles disponibles
        Retourne une liste des noms de modèles
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Génère une réponse à partir d'un prompt
        Utilise le modèle spécifié ou le modèle par défaut
        """
        model = model or self.settings.ollama_model
        
        # Construction des messages
        messages = []
        if system_prompt:
            messages.append(OllamaMessage(role="system", content=system_prompt))
        messages.append(OllamaMessage(role="user", content=prompt))
        
        request_data = OllamaRequest(
            model=model,
            messages=messages,
            stream=False
        )
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=request_data.dict()
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                logger.error(f"Erreur Ollama: {response.status_code} - {response.text}")
                return "Désolé, une erreur est survenue lors de la génération de la réponse."
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {e}")
            return "Désolé, je ne peux pas me connecter au service d'IA pour le moment."
    
    async def generate_aim_training_advice(
        self, 
        user_question: str,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Génère des conseils spécialisés en entraînement de visée
        Utilise un prompt système spécialisé pour KovaaK's
        """
        system_prompt = """Tu es un expert en entraînement de visée et un coach spécialisé dans KovaaK's FPS Aim Trainer. 
        
Ton rôle est d'aider les joueurs à améliorer leur précision et leurs performances. Tu connais:
- Les différents types d'aim (tracking, flicking, target switching)
- Les exercices KovaaK's les plus efficaces
- Les techniques de placement de souris et de posture
- L'analyse des statistiques de performance
- La progression et l'entraînement structuré

Réponds de manière concise, pratique et motivante. Donne des conseils concrets et des exercices spécifiques."""

        # Ajout des stats utilisateur si disponibles
        if user_stats:
            stats_context = f"\n\nStatistiques du joueur: {user_stats}"
            user_question += stats_context
        
        return await self.generate_response(
            prompt=user_question,
            system_prompt=system_prompt
        )
    
    async def close(self):
        """Ferme la connexion HTTP"""
        await self.client.aclose()


# Fonction utilitaire pour créer une instance du service
def create_ollama_service(settings: Settings) -> OllamaService:
    """Crée une instance du service Ollama"""
    return OllamaService(settings)
