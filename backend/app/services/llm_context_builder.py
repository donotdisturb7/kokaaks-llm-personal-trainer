"""
Service pour construire le contexte pour le LLM
Agrège les données KovaaK's API et stats locales
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.stats import LocalStats
from app.services.cache_service import CacheService
from app.services.kovaaks_service import create_kovaaks_service
from app.config import get_settings

logger = logging.getLogger(__name__)

class LLMContextBuilder:
    """Service pour construire le contexte pour le LLM"""

    def __init__(self):
        self.settings = get_settings()
        self.cache = CacheService()
    
    async def build_context(
        self, 
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """Construit le contexte complet pour le LLM"""
        logger.info("Construction du contexte pour le LLM")
        
        # Récupérer les données en parallèle
        local_stats = await self._get_local_stats(db, days)
        kovaaks_data = await self._get_kovaaks_data()
        
        # Construire le contexte
        context = {
            "local_stats": local_stats,
            "kovaaks_api_data": kovaaks_data,
            "analysis": self._analyze_performance(local_stats, kovaaks_data)
        }
        
        return context
    
    async def _get_local_stats(self, db: AsyncSession, days: int) -> Dict[str, Any]:
        """Récupère les stats locales"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Stats récentes
            result = await db.execute(
                select(LocalStats)
                .where(LocalStats.played_at >= start_date)
                .order_by(LocalStats.played_at.desc())
                .limit(100)
            )
            recent_stats = result.scalars().all()
            
            # Statistiques générales
            total_result = await db.execute(select(func.count(LocalStats.id)))
            total_entries = total_result.scalar()
            
            avg_score_result = await db.execute(
                select(func.avg(LocalStats.score))
                .where(LocalStats.played_at >= start_date)
            )
            average_score = avg_score_result.scalar() or 0
            
            # Top scénarios
            top_scenarios_result = await db.execute(
                select(
                    LocalStats.scenario_name,
                    func.max(LocalStats.score).label('best_score'),
                    func.avg(LocalStats.score).label('avg_score'),
                    func.count(LocalStats.id).label('plays')
                )
                .where(LocalStats.played_at >= start_date)
                .group_by(LocalStats.scenario_name)
                .order_by(func.max(LocalStats.score).desc())
                .limit(10)
            )
            top_scenarios = [
                {
                    "scenario_name": row.scenario_name,
                    "best_score": float(row.best_score),
                    "avg_score": float(row.avg_score),
                    "plays": row.plays
                }
                for row in top_scenarios_result
            ]
            
            return {
                "total_entries": total_entries,
                "recent_entries": len(recent_stats),
                "average_score": float(average_score),
                "top_scenarios": top_scenarios,
                "recent_stats": [
                    {
                        "scenario_name": stat.scenario_name,
                        "score": stat.score,
                        "accuracy": stat.accuracy,
                        "played_at": stat.played_at.isoformat() if stat.played_at else None
                    }
                    for stat in recent_stats[:20]
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats locales: {e}")
            return {"error": str(e)}
    
    async def _get_kovaaks_data(self) -> Dict[str, Any]:
        """Récupère les données de l'API KovaaK's"""
        if not self.settings.kovaaks_username:
            return {"error": "Nom d'utilisateur KovaaK's non configuré"}
        
        try:
            async with create_kovaaks_service() as kovaaks_service:
                # Récupérer le profil
                profile = await kovaaks_service.get_profile_by_username(self.settings.kovaaks_username)

                # Récupérer les scénarios joués
                scenarios = await kovaaks_service.get_scenarios_played_by_username(
                    self.settings.kovaaks_username,
                    max=50
                )

                # Récupérer les scores récents
                recent_scores = await kovaaks_service.get_recent_high_scores_by_username(
                    self.settings.kovaaks_username
                )

                return {
                    "profile": profile,
                    "scenarios_played": scenarios,
                    "recent_scores": recent_scores
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données KovaaK's: {e}")
            return {"error": str(e)}
    
    def _analyze_performance(self, local_stats: Dict[str, Any], kovaaks_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse les performances et identifie les points d'amélioration"""
        analysis = {
            "trend": "stable",
            "strengths": [],
            "weak_points": [],
            "recommendations": []
        }
        
        # Analyser les stats locales
        if "error" not in local_stats:
            avg_score = local_stats.get("average_score", 0)
            top_scenarios = local_stats.get("top_scenarios", [])
            
            # Identifier les forces
            if top_scenarios:
                best_scenario = top_scenarios[0]
                analysis["strengths"].append(f"Meilleur scénario: {best_scenario['scenario_name']} (score: {best_scenario['best_score']})")
            
            # Identifier les faiblesses
            if avg_score < 50:
                analysis["weak_points"].append("Score moyen faible - besoin d'amélioration générale")
            
            # Recommandations
            if len(top_scenarios) < 5:
                analysis["recommendations"].append("Jouer plus de scénarios variés pour améliorer la polyvalence")
        
        # Analyser les données KovaaK's
        if "error" not in kovaaks_data:
            scenarios_played = kovaaks_data.get("scenarios_played", {})
            if scenarios_played and scenarios_played.get("total", 0) < 20:
                analysis["recommendations"].append("Explorer plus de scénarios sur KovaaK's pour diversifier l'entraînement")
        
        return analysis
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Formate le contexte pour le LLM"""
        system_prompt = """You are a specialized aim training coach for KovaaK's FPS Aim Trainer.
You help players improve their accuracy and performance.

USER CONTEXT:
"""

        # Prioritize KovaaK's API data over local stats
        kovaaks_data = context.get("kovaaks_api_data", {})
        if "error" not in kovaaks_data and kovaaks_data.get("scenarios_played"):
            scenarios_data = kovaaks_data["scenarios_played"]
            profile = kovaaks_data.get("profile", {})

            # Extract scenarios from nested data structure
            scenarios = scenarios_data.get("data", []) if isinstance(scenarios_data, dict) else scenarios_data

            system_prompt += f"""
KOVAAK'S API DATA (Live from user account):
- Username: {profile.get('webapp', {}).get('username', 'Unknown') if isinstance(profile, dict) else 'Unknown'}
- Total scenarios played: {scenarios_data.get('total', len(scenarios)) if isinstance(scenarios_data, dict) else len(scenarios)}

TOP SCENARIOS (by plays):
"""
            for scenario in scenarios[:5]:
                scenario_name = scenario.get('scenarioName', scenario.get('name', 'Unknown'))
                plays = scenario.get('counts', {}).get('plays', scenario.get('plays', 0))
                best_score = scenario.get('score', scenario.get('highScore', 0))
                system_prompt += f"- {scenario_name}: {plays} plays, Best: {best_score:.1f}\n"

            if kovaaks_data.get("recent_scores"):
                system_prompt += f"\nRECENT HIGH SCORES:\n"
                for score in kovaaks_data["recent_scores"][:3]:
                    system_prompt += f"- {score.get('scenarioName', 'Unknown')}: {score.get('score', 0):.1f}\n"

        # Fallback to local stats if KovaaK's API data not available
        elif "error" not in context.get("local_stats", {}):
            local_stats = context["local_stats"]
            system_prompt += f"""
LOCAL STATS (recent entries):
- Average score: {local_stats.get('average_score', 0):.1f}
- Total entries: {local_stats.get('total_entries', 0)}
- Recent entries: {local_stats.get('recent_entries', 0)}

TOP SCENARIOS:
"""
            for scenario in local_stats.get("top_scenarios", [])[:5]:
                system_prompt += f"- {scenario['scenario_name']}: Best score {scenario['best_score']:.1f}, Average {scenario['avg_score']:.1f}, {scenario['plays']} plays\n"

        # Ajouter l'analyse
        analysis = context.get("analysis", {})
        if analysis.get("strengths"):
            system_prompt += f"\nSTRENGTHS: {', '.join(analysis['strengths'])}\n"

        if analysis.get("weak_points"):
            system_prompt += f"AREAS TO IMPROVE: {', '.join(analysis['weak_points'])}\n"

        if analysis.get("recommendations"):
            system_prompt += f"RECOMMENDATIONS: {', '.join(analysis['recommendations'])}\n"

        system_prompt += """
INSTRUCTIONS:
- Provide personalized advice based on the user's stats above
- When the user asks for routine recommendations, combine their stats with the training documents
- Suggest specific exercises that target their weak points
- Explain improvement techniques clearly
- Be encouraging but realistic
- Use appropriate technical terms for KovaaK's
- If training documents are provided, prioritize routines that match the user's skill level and weaknesses
"""

        return system_prompt

def create_llm_context_builder() -> LLMContextBuilder:
    return LLMContextBuilder()