"""
API endpoints pour le contexte LLM
Expose le contexte utilisateur formaté pour le LLM
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any
import logging

from app.database import get_db
from app.services.llm_context_builder import create_llm_context_builder
from app.services.cache_service import CacheService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm-context"])

@router.get("/context")
async def get_user_context(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
) -> Dict[str, Any]:
    """Récupère le contexte complet pour le LLM"""
    try:
        context_builder = create_llm_context_builder()
        context = await context_builder.build_context(db, days=days)
        
        return {
            "context": context
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la construction du contexte: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la construction du contexte"
        )

@router.get("/context/formatted")
async def get_formatted_context(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
) -> Dict[str, str]:
    """Récupère le contexte formaté pour le system prompt du LLM"""
    try:
        context_builder = create_llm_context_builder()
        context = await context_builder.build_context(db, days=days)
        formatted_context = context_builder.format_context_for_llm(context)
        
        return {
            "system_prompt": formatted_context,
            "context_summary": {
                "trend": context["analysis"]["trend"],
                "weak_points": context["analysis"]["weak_points"],
                "strengths": context["analysis"]["strengths"],
                "total_plays": context["analysis"]["total_plays"]
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du formatage du contexte: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du formatage du contexte"
        )

@router.post("/context/refresh")
async def refresh_context_cache() -> Dict[str, str]:
    """Force le refresh du cache de contexte"""
    try:
        cache = CacheService()
        await cache.invalidate_stats_cache()
        
        return {
            "message": "Cache de contexte rafraîchi"
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du refresh du cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du refresh du cache"
        )

@router.get("/analysis")
async def get_performance_analysis(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
) -> Dict[str, Any]:
    """Récupère l'analyse de performance"""
    try:
        context_builder = create_llm_context_builder()
        context = await context_builder.build_context(db, days=days)
        
        return {
            "period_days": days,
            "analysis": context["analysis"],
            "top_scenarios": context["top_scenarios"][:10],
            "recent_stats_count": len(context["recent_stats"])
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de performance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'analyse de performance"
        )


