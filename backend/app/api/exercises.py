"""
API endpoints pour les exercices KovaaK's
Gère les exercices recommandés et les suggestions personnalisées
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
import logging

from app.database import get_db
from app.services.llm_context_builder import create_llm_context_builder
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/exercises", tags=["exercises"])

# Seed data pour les exercices KovaaK's
EXERCISES_DATA = [
    {
        "id": 1,
        "name": "1w6ts reload",
        "aim_type": "clicking",
        "difficulty": "medium",
        "description": "Exercice de clicking statique avec des cibles qui apparaissent et disparaissent rapidement",
        "recommended_for": ["static_clicking", "precision", "reaction_time"],
        "scenario_name": "1w6ts reload",
        "target_skills": ["Precision", "Réactivité", "Contrôle de la souris"]
    },
    {
        "id": 2,
        "name": "1w4ts reload",
        "aim_type": "clicking",
        "difficulty": "easy",
        "description": "Version plus facile de 1w6ts avec des cibles plus grandes",
        "recommended_for": ["static_clicking", "beginners"],
        "scenario_name": "1w4ts reload",
        "target_skills": ["Precision", "Contrôle de base"]
    },
    {
        "id": 3,
        "name": "Close Fast Strafes Easy",
        "aim_type": "tracking",
        "difficulty": "easy",
        "description": "Tracking de cibles qui bougent rapidement à courte distance",
        "recommended_for": ["tracking", "beginners", "close_range"],
        "scenario_name": "Close Fast Strafes Easy",
        "target_skills": ["Tracking", "Prédiction", "Contrôle fluide"]
    },
    {
        "id": 4,
        "name": "Close Fast Strafes",
        "aim_type": "tracking",
        "difficulty": "medium",
        "description": "Version plus difficile du tracking rapide",
        "recommended_for": ["tracking", "intermediate", "close_range"],
        "scenario_name": "Close Fast Strafes",
        "target_skills": ["Tracking avancé", "Réactivité", "Prédiction"]
    },
    {
        "id": 5,
        "name": "FuglaaXYLongstrafes",
        "aim_type": "tracking",
        "difficulty": "medium",
        "description": "Tracking de longues strafes avec mouvement XY",
        "recommended_for": ["tracking", "long_range", "smooth_tracking"],
        "scenario_name": "FuglaaXYLongstrafes",
        "target_skills": ["Tracking fluide", "Contrôle long terme", "Prédiction"]
    },
    {
        "id": 6,
        "name": "Tile Frenzy - Strafing - 01",
        "aim_type": "clicking",
        "difficulty": "easy",
        "description": "Clicking rapide sur des tuiles qui bougent",
        "recommended_for": ["clicking", "beginners", "speed"],
        "scenario_name": "Tile Frenzy - Strafing - 01",
        "target_skills": ["Vitesse", "Précision", "Réactivité"]
    },
    {
        "id": 7,
        "name": "Target Switching 360",
        "aim_type": "target_switching",
        "difficulty": "hard",
        "description": "Changement de cible avec mouvement 360°",
        "recommended_for": ["target_switching", "advanced", "movement"],
        "scenario_name": "Target Switching 360",
        "target_skills": ["Changement de cible", "Mouvement", "Situational awareness"]
    },
    {
        "id": 8,
        "name": "Pasu Track",
        "aim_type": "tracking",
        "difficulty": "hard",
        "description": "Tracking de cibles qui changent de direction rapidement",
        "recommended_for": ["tracking", "advanced", "reactive_tracking"],
        "scenario_name": "Pasu Track",
        "target_skills": ["Tracking réactif", "Prédiction", "Contrôle avancé"]
    },
    {
        "id": 9,
        "name": "Bounce 180",
        "aim_type": "clicking",
        "difficulty": "medium",
        "description": "Clicking avec mouvement 180° et rebond",
        "recommended_for": ["clicking", "movement", "intermediate"],
        "scenario_name": "Bounce 180",
        "target_skills": ["Clicking en mouvement", "Contrôle spatial", "Précision"]
    },
    {
        "id": 10,
        "name": "Smoothbot",
        "aim_type": "tracking",
        "difficulty": "medium",
        "description": "Tracking de cibles qui bougent de manière fluide",
        "recommended_for": ["tracking", "smooth_tracking", "intermediate"],
        "scenario_name": "Smoothbot",
        "target_skills": ["Tracking fluide", "Contrôle précis", "Consistance"]
    }
]

@router.get("/")
async def get_exercises(
    aim_type: Optional[str] = Query(None, regex="^(clicking|tracking|target_switching)$"),
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    limit: int = Query(50, ge=1, le=100)
):
    """Récupère la liste des exercices avec filtres optionnels"""
    exercises = EXERCISES_DATA.copy()
    
    # Appliquer les filtres
    if aim_type:
        exercises = [ex for ex in exercises if ex["aim_type"] == aim_type]
    
    if difficulty:
        exercises = [ex for ex in exercises if ex["difficulty"] == difficulty]
    
    # Limiter les résultats
    exercises = exercises[:limit]
    
    return {
        "exercises": exercises,
        "total": len(exercises),
        "filters": {
            "aim_type": aim_type,
            "difficulty": difficulty
        }
    }

@router.get("/{exercise_id}")
async def get_exercise_details(exercise_id: int):
    """Récupère les détails d'un exercice spécifique"""
    exercise = next((ex for ex in EXERCISES_DATA if ex["id"] == exercise_id), None)
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercice non trouvé"
        )
    
    return {
        "exercise": exercise
    }

@router.get("/recommendations")
async def get_personalized_recommendations(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(5, ge=1, le=20)
):
    """Récupère des exercices recommandés basés sur les stats de l'utilisateur"""
    try:
        # Construire le contexte utilisateur
        context_builder = create_llm_context_builder()
        context = await context_builder.build_context(db)
        
        analysis = context["analysis"]
        weak_points = analysis["weak_points"]
        strengths = analysis["strengths"]
        trend = analysis["trend"]
        
        # Logique de recommandation basée sur l'analyse
        recommendations = []
        
        # Recommandations basées sur les points faibles
        if weak_points:
            for weak_point in weak_points[:3]:
                # Trouver des exercices qui correspondent aux points faibles
                matching_exercises = [
                    ex for ex in EXERCISES_DATA
                    if any(skill.lower() in ex["name"].lower() or 
                          skill.lower() in ex["description"].lower()
                          for skill in weak_point.split())
                ]
                if matching_exercises:
                    recommendations.extend(matching_exercises[:2])
        
        # Recommandations basées sur la tendance
        if trend == "declining":
            # Recommander des exercices faciles pour reprendre confiance
            easy_exercises = [ex for ex in EXERCISES_DATA if ex["difficulty"] == "easy"]
            recommendations.extend(easy_exercises[:2])
        elif trend == "improving":
            # Recommander des exercices plus difficiles pour continuer la progression
            hard_exercises = [ex for ex in EXERCISES_DATA if ex["difficulty"] == "hard"]
            recommendations.extend(hard_exercises[:2])
        
        # Recommandations basées sur les forces (pour les maintenir)
        if strengths:
            for strength in strengths[:2]:
                matching_exercises = [
                    ex for ex in EXERCISES_DATA
                    if any(skill.lower() in ex["name"].lower() or 
                          skill.lower() in ex["description"].lower()
                          for skill in strength.split())
                ]
                if matching_exercises:
                    recommendations.extend(matching_exercises[:1])
        
        # Si pas assez de recommandations, ajouter des exercices populaires
        if len(recommendations) < limit:
            popular_exercises = [ex for ex in EXERCISES_DATA if ex["difficulty"] == "medium"]
            recommendations.extend(popular_exercises[:limit - len(recommendations)])
        
        # Supprimer les doublons et limiter
        seen_ids = set()
        unique_recommendations = []
        for ex in recommendations:
            if ex["id"] not in seen_ids:
                seen_ids.add(ex["id"])
                unique_recommendations.append(ex)
                if len(unique_recommendations) >= limit:
                    break
        
        return {
            "user": current_user.kovaaks_username,
            "recommendations": unique_recommendations,
            "analysis": {
                "trend": trend,
                "weak_points": weak_points,
                "strengths": strengths,
                "reasoning": _generate_recommendation_reasoning(analysis, unique_recommendations)
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération des recommandations: {e}")
        # Fallback: retourner des exercices populaires
        popular_exercises = [ex for ex in EXERCISES_DATA if ex["difficulty"] == "medium"][:limit]
        return {
            "user": current_user.kovaaks_username,
            "recommendations": popular_exercises,
            "analysis": {
                "trend": "unknown",
                "weak_points": [],
                "strengths": [],
                "reasoning": "Recommandations par défaut (analyse indisponible)"
            }
        }

def _generate_recommendation_reasoning(analysis: Dict[str, Any], recommendations: List[Dict[str, Any]]) -> str:
    """Génère une explication des recommandations"""
    reasoning_parts = []
    
    if analysis["trend"] == "declining":
        reasoning_parts.append("Votre performance semble en baisse, nous recommandons des exercices plus faciles pour reprendre confiance.")
    elif analysis["trend"] == "improving":
        reasoning_parts.append("Excellente progression ! Nous recommandons des exercices plus difficiles pour continuer à progresser.")
    
    if analysis["weak_points"]:
        reasoning_parts.append(f"Concentrez-vous sur vos points faibles: {', '.join(analysis['weak_points'][:3])}")
    
    if analysis["strengths"]:
        reasoning_parts.append(f"Maintenez vos forces: {', '.join(analysis['strengths'][:2])}")
    
    if not reasoning_parts:
        reasoning_parts.append("Exercices recommandés pour un entraînement équilibré.")
    
    return " ".join(reasoning_parts)


