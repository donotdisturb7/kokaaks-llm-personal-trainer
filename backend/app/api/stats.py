"""
API endpoints pour les statistiques locales
Gère l'upload CSV et l'affichage des stats locales
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Response
from typing import List, Optional
import logging
import hashlib
import json
from datetime import datetime

from app.database import get_db
from app.services.stats_parser import create_stats_parser
from app.services.cache_service import CacheService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload et parse un fichier CSV de stats KovaaK's"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être un CSV"
        )
    
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Parser le CSV
        parser = create_stats_parser()
        result = await parser.parse_csv_file(content, db)
        
        # Invalider le cache des stats
        cache = CacheService()
        await cache.invalidate_stats_cache()
        
        return {
            "message": f"Fichier uploadé avec succès",
            "filename": file.filename,
            **result
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du traitement du fichier"
        )

@router.get("/history")
async def get_stats_history(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000)
):
    """Récupère l'historique des stats avec pagination"""
    try:
        parser = create_stats_parser()
        summary = await parser.get_stats_summary(db, days=days)
        
        # Pagination des stats récentes
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_stats = summary["recent_stats"][start_idx:end_idx]
        
        return {
            "period_days": days,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": len(summary["recent_stats"]),
                "has_more": end_idx < len(summary["recent_stats"])
            },
            "stats": paginated_stats,
            "summary": summary["summary"]
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des stats"
        )

@router.get("/scenario/{scenario_name}")
async def get_scenario_stats(
    scenario_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Récupère les stats d'un scénario spécifique"""
    try:
        parser = create_stats_parser()
        stats = await parser.get_scenario_stats(scenario_name, db)
        
        return stats
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats du scénario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des stats du scénario"
        )

@router.get("/progress")
async def get_progress(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Récupère la progression"""
    try:
        parser = create_stats_parser()
        summary = await parser.get_stats_summary(db, days=days)
        
        return {
            "period_days": days,
            "progression": summary["progression"],
            "top_scenarios": summary["top_scenarios"],
            "summary": summary["summary"]
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la progression: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de la progression"
        )

@router.get("/best-scores")
async def get_best_scores(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=1, le=100)
):
    """Récupère les meilleurs scores par scénario"""
    try:
        parser = create_stats_parser()
        summary = await parser.get_stats_summary(db, days=365)
        
        # Trier par meilleur score
        best_scores = sorted(
            summary["top_scenarios"], 
            key=lambda x: x["best_score"], 
            reverse=True
        )[:limit]
        
        return {
            "best_scores": best_scores
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des meilleurs scores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des meilleurs scores"
        )

@router.delete("/{stat_id}")
async def delete_stat(
    stat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Supprime une stat spécifique"""
    try:
        from sqlalchemy import select
        from app.models.stats import LocalStats
        
        # Vérifier que la stat existe
        result = await db.execute(
            select(LocalStats).where(LocalStats.id == stat_id)
        )
        stat = result.scalar_one_or_none()
        
        if not stat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stat non trouvée"
            )
        
        await db.delete(stat)
        await db.commit()
        
        return {
            "message": "Stat supprimée avec succès",
            "stat_id": stat_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la stat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de la stat"
        )