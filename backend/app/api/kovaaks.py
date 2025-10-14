"""
API endpoints pour l'intégration KovaaK's
Expose les données KovaaK's avec cache Redis
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
import logging

# from app.dependencies import get_current_user, get_current_kovaaks_username
# from app.models.user import User
from app.services.kovaaks_service import create_kovaaks_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kovaaks", tags=["kovaaks"])

@router.get("/profile/{username}")
async def get_profile(username: str):
    """Récupère le profil d'un utilisateur KovaaK's"""
    async with create_kovaaks_service() as kovaaks:
        profile = await kovaaks.get_profile_by_username(username)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profil non trouvé pour l'utilisateur {username}"
            )
        
        return {
            "username": username,
            "profile": profile,
            "cached": True  # Toujours true car on utilise le cache
        }

@router.get("/scenarios/{username}")
async def get_scenarios(
    username: str,
    page: int = Query(1, ge=1),
    max: int = Query(100, ge=1, le=1000),
    sort: str = Query("plays", regex="^(plays|score|accuracy)$")
):
    """Récupère les scénarios joués par un utilisateur"""
    async with create_kovaaks_service() as kovaaks:
        scenarios = await kovaaks.get_scenarios_played_by_username(
            username, page=page, max=max, sort=sort
        )
        
        if not scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scénarios non trouvés pour l'utilisateur {username}"
            )
        
        return scenarios

@router.get("/highscores/{username}")
async def get_highscores(username: str):
    """Récupère les high scores récents d'un utilisateur"""
    async with create_kovaaks_service() as kovaaks:
        highscores = await kovaaks.get_recent_high_scores_by_username(username)
        
        if not highscores:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"High scores non trouvés pour l'utilisateur {username}"
            )
        
        return {
            "username": username,
            "highscores": highscores
        }

@router.get("/benchmarks/{username}")
async def get_benchmarks(
    username: str,
    page: int = Query(1, ge=1),
    max: int = Query(100, ge=1, le=1000)
):
    """Récupère la progression des benchmarks d'un utilisateur"""
    async with create_kovaaks_service() as kovaaks:
        benchmarks = await kovaaks.get_benchmark_progress_for_username(
            username, page=page, max=max
        )
        
        if not benchmarks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benchmarks non trouvés pour l'utilisateur {username}"
            )
        
        return benchmarks

@router.get("/favorites/{username}")
async def get_favorites(username: str):
    """Récupère les scénarios favoris d'un utilisateur"""
    async with create_kovaaks_service() as kovaaks:
        favorites = await kovaaks.get_favorite_scenarios_by_username(username)
        
        if not favorites:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Favoris non trouvés pour l'utilisateur {username}"
            )
        
        return {
            "username": username,
            "favorites": favorites
        }

@router.get("/summary/{username}")
async def get_summary(username: str):
    """Récupère un résumé complet des stats d'un utilisateur"""
    async with create_kovaaks_service() as kovaaks:
        # Récupérer toutes les données en parallèle
        profile = await kovaaks.get_profile_by_username(username)
        scenarios = await kovaaks.get_scenarios_played_by_username(username, max=50)
        highscores = await kovaaks.get_recent_high_scores_by_username(username)
        benchmarks = await kovaaks.get_benchmark_progress_for_username(username)
        favorites = await kovaaks.get_favorite_scenarios_by_username(username)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utilisateur {username} non trouvé"
            )
        
        # Calculer des statistiques
        total_scenarios = len(scenarios.get("data", [])) if scenarios else 0
        total_highscores = len(highscores) if highscores else 0
        total_benchmarks = len(benchmarks.get("data", [])) if benchmarks else 0
        total_favorites = len(favorites) if favorites else 0
        
        return {
            "username": username,
            "profile": profile,
            "statistics": {
                "total_scenarios_played": total_scenarios,
                "recent_highscores": total_highscores,
                "benchmarks_completed": total_benchmarks,
                "favorite_scenarios": total_favorites
            },
            "recent_activity": {
                "scenarios": scenarios.get("data", [])[:10] if scenarios else [],
                "highscores": highscores[:5] if highscores else [],
                "favorites": favorites[:5] if favorites else []
            }
        }

@router.post("/refresh-cache/{username}")
async def refresh_cache(username: str):
    """Force le refresh du cache pour un utilisateur"""
    async with create_kovaaks_service() as kovaaks:
        await kovaaks.clear_user_cache(username)
        
        # Recharger les données
        profile = await kovaaks.get_profile_by_username(username)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utilisateur {username} non trouvé"
            )
        
        return {
            "message": f"Cache rafraîchi pour l'utilisateur {username}",
            "profile_updated": True
        }

@router.get("/health")
async def health_check():
    """Vérifie la santé de l'API KovaaK's"""
    async with create_kovaaks_service() as kovaaks:
        is_healthy = await kovaaks.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "api_url": kovaaks.base_url
        }


