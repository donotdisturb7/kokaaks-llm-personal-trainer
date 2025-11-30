"""
API routes pour le chat avec l'IA
Gère les conversations avec différents providers IA (Ollama, Groq) pour l'entraînement de visée
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db

# Plus besoin de dépendances utilisateur
from app.models.conversation import Conversation
from app.services.llm_service import LLMService, create_llm_service
from app.services.llm_context_builder import create_llm_context_builder

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
    include_user_context: bool = True
    conversation_id: Optional[int] = None
    model: Optional[str] = None
    rag_mode: str = "hybrid"  # "off", "hybrid", "only"
    rag_max_results: int = 10  # Increased to capture more context including sharecodes


class ChatResponse(BaseModel):
    """Modèle pour une réponse de chat"""

    message: str
    model_used: str
    response_time: Optional[float] = None
    rag_used: bool = False
    rag_sources: Optional[List[Dict[str, Any]]] = None
    rag_confidence: Optional[float] = None


@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    try:
        async with create_llm_service(settings) as llm:
            health_status = await llm.health_check()
            return health_status
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        raise HTTPException(
            status_code=500, detail=f"Erreur de connexion au provider IA: {str(e)}"
        )


@router.get("/models")
async def get_available_models(settings: Settings = Depends(get_settings)):
    try:
        async with create_llm_service(settings) as llm:
            models = await llm.get_available_models()
            health_status = await llm.health_check()
            return {
                "models": models,
                "default_model": health_status.get("model"),
                "provider": health_status.get("provider"),
            }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des modèles: {e}")
        raise HTTPException(
            status_code=500, detail="Erreur lors de la récupération des modèles"
        )


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    import time

    start_time = time.time()

    try:
        async with create_llm_service(settings) as llm:
            # Vérification de la santé du provider
            health_status = await llm.health_check()
            if health_status["status"] != "healthy":
                raise HTTPException(
                    status_code=503,
                    detail=f"Provider {health_status['provider']} non accessible",
                )

            # Construire le contexte utilisateur si demandé
            system_prompt = None
            context_used = None

            if request.include_user_context:
                context_builder = create_llm_context_builder()
                context = await context_builder.build_context(db)
                system_prompt = context_builder.format_context_for_llm(context)
                context_used = {
                    "trend": context["analysis"]["trend"],
                    "weak_points": context["analysis"]["weak_points"],
                    "strengths": context["analysis"]["strengths"],
                }

            # RAG integration
            rag_context = None
            rag_sources = None
            rag_confidence = None
            rag_used = False

            if request.rag_mode in ["hybrid", "only"]:
                try:
                    from app.services.rag_service import RAGService

                    rag_service = RAGService(db)

                    # Retrieve relevant chunks from PDFs
                    rag_result = await rag_service.query(
                        query=request.message,
                        max_results=request.rag_max_results,
                        safety_level="general",
                    )

                    if rag_result["sources"]:
                        rag_used = True
                        rag_sources = rag_result["sources"]
                        rag_confidence = rag_result["confidence"]
                        rag_context = "\n\n".join(
                            [
                                f"[Source: {s['title']}]\n{s['content']}\n(Relevance: {s['relevance']:.2f})"
                                for s in rag_result["sources"]
                            ]
                        )

                        # Mode hybride : combiner RAG + system_prompt (user stats)
                        if request.rag_mode == "hybrid":
                            if system_prompt:
                                # Combine user stats + RAG documents for personalized advice
                                system_prompt += f"\n\n## Relevant Training Documents:\n{rag_context}"
                            else:
                                system_prompt = f"You are an aim training assistant.\n\n## Relevant Training Documents:\n{rag_context}"

                        # Mode RAG only : remplacer system_prompt
                        elif request.rag_mode == "only":
                            system_prompt = f"""You are an assistant that answers ONLY based on the documents provided below.
If the answer is not in the documents, say so clearly.

## Available Documents:
{rag_context}"""

                except Exception as e:
                    logger.warning(f"RAG query failed: {e}")
                    # Continuer sans RAG en mode hybride, échouer en mode only
                    if request.rag_mode == "only":
                        raise HTTPException(
                            status_code=500, detail="RAG required but failed"
                        )

            # Génération de la réponse spécialisée
            response = await llm.generate_response(
                prompt=request.message, system_prompt=system_prompt
            )

            response_time = time.time() - start_time

            # Sauvegarder la conversation
            await _save_conversation(request.message, response, context_used, db)

            return ChatResponse(
                message=response,
                model_used=request.model or health_status["model"],
                response_time=response_time,
                rag_used=rag_used,
                rag_sources=rag_sources,
                rag_confidence=rag_confidence,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du message: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.post("/conversation")
async def send_conversation(
    messages: List[ChatMessage],
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):

    try:
        async with create_llm_service(settings) as llm:
            health_status = await llm.health_check()
            if health_status["status"] != "healthy":
                raise HTTPException(
                    status_code=503,
                    detail=f"Provider {health_status['provider']} non accessible",
                )

            # Pour l'instant, on prend le dernier message utilisateur
            # TODO: Implémenter la gestion complète de conversation
            last_user_message = None
            for msg in reversed(messages):
                if msg.role == "user":
                    last_user_message = msg.content
                    break

            if not last_user_message:
                raise HTTPException(
                    status_code=400, detail="Aucun message utilisateur trouvé"
                )

            # Construire le contexte utilisateur
            context_builder = create_llm_context_builder()
            context = await context_builder.build_context(db)
            system_prompt = context_builder.format_context_for_llm(context)

            response = await llm.generate_response(
                prompt=last_user_message, system_prompt=system_prompt
            )

            # Sauvegarder la conversation
            await _save_conversation(
                last_user_message,
                response,
                {
                    "trend": context["analysis"]["trend"],
                    "weak_points": context["analysis"]["weak_points"],
                    "strengths": context["analysis"]["strengths"],
                },
                db,
            )

            return ChatResponse(message=response, model_used=health_status["model"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de la conversation: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


async def _save_conversation(
    user_message: str,
    ai_response: str,
    context_used: Optional[Dict[str, Any]],
    db: AsyncSession,
):
    """Sauvegarde une conversation dans la base de données"""
    try:
        conversation = Conversation(
            title=user_message[:50] + "..." if len(user_message) > 50 else user_message,
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat(),
                },
            ],
            context_used=context_used,
        )
        db.add(conversation)
        await db.commit()
        logger.info(f"Conversation sauvegardée")
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la conversation: {e}")
        # Ne pas faire échouer la requête si la sauvegarde échoue
