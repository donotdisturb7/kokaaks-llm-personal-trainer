"""
API routes pour le chat avec l'IA
Gère les conversations avec Ollama pour l'entraînement de visée
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from app.config import Settings, get_settings
from app.services.ollama_service import OllamaService, create_ollama_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Modèle pour un message de chat"""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    """Modèle pour une requête de chat"""
    message: str
    user_stats: Optional[Dict[str, Any]] = None
    model: Optional[str] = None


class ChatResponse(BaseModel):
    """Modèle pour une réponse de chat"""
    message: str
    model_used: str
    response_time: Optional[float] = None


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """
    Vérifie la santé de la connexion Ollama
    Retourne True si Ollama est accessible
    """
    try:
        async with create_ollama_service(settings) as ollama:
            is_healthy = await ollama.health_check()
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "ollama_host": settings.ollama_host,
                "ollama_port": settings.ollama_port,
                "ollama_model": settings.ollama_model
            }
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        raise HTTPException(status_code=500, detail="Erreur de connexion Ollama")


@router.get("/models")
async def get_available_models(settings: Settings = Depends(get_settings)):
    """
    Récupère la liste des modèles Ollama disponibles
    """
    try:
        async with create_ollama_service(settings) as ollama:
            models = await ollama.get_available_models()
            return {
                "models": models,
                "default_model": settings.ollama_model
            }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des modèles")


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    settings: Settings = Depends(get_settings)
):
    """
    Envoie un message à l'IA et récupère la réponse
    Spécialisé pour l'entraînement de visée
    """
    import time
    start_time = time.time()
    
    try:
        async with create_ollama_service(settings) as ollama:
            # Vérification de la santé d'Ollama
            if not await ollama.health_check():
                raise HTTPException(
                    status_code=503, 
                    detail=f"Ollama non accessible sur {settings.ollama_host}:{settings.ollama_port}"
                )
            
            # Génération de la réponse spécialisée
            response = await ollama.generate_aim_training_advice(
                user_question=request.message,
                user_stats=request.user_stats
            )
            
            response_time = time.time() - start_time
            
            return ChatResponse(
                message=response,
                model_used=request.model or settings.ollama_model,
                response_time=response_time
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.post("/conversation")
async def send_conversation(
    messages: List[ChatMessage],
    user_stats: Optional[Dict[str, Any]] = None,
    settings: Settings = Depends(get_settings)
):
    """
    Envoie une conversation complète à l'IA
    Utile pour maintenir le contexte de la conversation
    """
    try:
        async with create_ollama_service(settings) as ollama:
            if not await ollama.health_check():
                raise HTTPException(
                    status_code=503, 
                    detail=f"Ollama non accessible sur {settings.ollama_host}:{settings.ollama_port}"
                )
            
            # Conversion des messages pour Ollama
            ollama_messages = []
            for msg in messages:
                ollama_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Pour l'instant, on prend le dernier message utilisateur
            # TODO: Implémenter la gestion complète de conversation
            last_user_message = None
            for msg in reversed(messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break
            
            if not last_user_message:
                raise HTTPException(status_code=400, detail="Aucun message utilisateur trouvé")
            
            response = await ollama.generate_aim_training_advice(
                user_question=last_user_message,
                user_stats=user_stats
            )
            
            return ChatResponse(
                message=response,
                model_used=settings.ollama_model
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la conversation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
