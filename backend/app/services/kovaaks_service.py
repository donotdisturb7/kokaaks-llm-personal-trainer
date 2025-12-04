import httpx
from typing import Optional, Dict, Any, List
import logging
import os
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class KovaaksService:
    
    def __init__(self):
        # Utiliser le proxy qui utilise le wrapper officiel
        from app.config import settings
        self.base_url = settings.kovaaks_proxy_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.cache = CacheService()
    
    async def __aenter__(self):
        """Context manager entry"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.client.aclose()
    
    async def get_profile_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Récupère le profil d'un utilisateur KovaaK's"""
        # Check cache first
        cached = await self.cache.get_kovaaks_profile(username)
        if cached:
            logger.info(f"Profil {username} récupéré du cache")
            return cached
        
        try:
            # Fetch from proxy (which uses official wrapper)
            response = await self.client.get(
                f"{self.base_url}/api/profile/{username}"
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("success"):
                logger.error(f"Erreur proxy pour le profil {username}: {data.get('error')}")
                return None
            
            profile = data.get("data")
            
            # Cache result
            await self.cache.set_kovaaks_profile(username, profile)
            logger.info(f"Profil {username} récupéré via proxy et mis en cache")
            return profile
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP pour le profil {username}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du profil {username}: {e}")
            return None
    
    async def get_scenarios_played_by_username(
        self, 
        username: str, 
        page: int = 1, 
        max: int = 100,
        sort: str = "plays"
    ) -> Optional[Dict[str, Any]]:
        """Récupère les scénarios joués par un utilisateur"""
        # Check cache first
        cache_key = f"{username}:{page}:{max}:{sort}"
        cached = await self.cache.get(f"kovaaks:scenarios:{cache_key}")
        if cached:
            return cached
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/scenarios/{username}",
                params={"page": page, "max": max, "sort": sort}
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                return None
                
            data = result.get("data")
            
            # Cache result
            await self.cache.set(f"kovaaks:scenarios:{cache_key}", data, self.cache.ttl_stats)
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des scénarios {username}: {e}")
            return None
    
    async def get_recent_high_scores_by_username(self, username: str) -> Optional[List[Dict[str, Any]]]:
        """Récupère les high scores récents d'un utilisateur"""
        # Check cache first
        cached = await self.cache.get_kovaaks_highscores(username)
        if cached:
            return cached
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/highscores/{username}"
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                return None
                
            highscores = result.get("data")
            
            # Cache result
            await self.cache.set_kovaaks_highscores(username, highscores)
            return highscores
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des high scores {username}: {e}")
            return None
    
    async def get_benchmark_progress_for_username(
        self, 
        username: str, 
        page: int = 1, 
        max: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Récupère la progression des benchmarks d'un utilisateur"""
        # Check cache first
        cache_key = f"{username}:{page}:{max}"
        cached = await self.cache.get(f"kovaaks:benchmarks:{cache_key}")
        if cached:
            return cached
        
        try:
            response = await self.client.get(
                f"{self.base_url}/users/benchmark-progress/get",
                params={
                    "webappUsername": username,
                    "page": page,
                    "max": max
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache result
            await self.cache.set(f"kovaaks:benchmarks:{cache_key}", data, self.cache.ttl_stats)
            return data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des benchmarks {username}: {e}")
            return None
    
    async def get_favorite_scenarios_by_username(self, username: str) -> Optional[List[Dict[str, Any]]]:
        """Récupère les scénarios favoris d'un utilisateur"""
        # Check cache first
        cached = await self.cache.get_kovaaks_favorites(username)
        if cached:
            return cached
        
        try:
            response = await self.client.get(
                f"{self.base_url}/users/favorite-scenarios/get",
                params={"webappUsername": username}
            )
            response.raise_for_status()
            favorites = response.json()
            
            # Cache result
            await self.cache.set_kovaaks_favorites(username, favorites)
            return favorites
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des favoris {username}: {e}")
            return None
    
    async def get_last_scores_by_scenario_name(
        self, 
        username: str, 
        scenario_name: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Récupère les derniers scores d'un scénario spécifique"""
        try:
            response = await self.client.get(
                f"{self.base_url}/users/last-scores-by-scenario-name/get",
                params={
                    "webappUsername": username,
                    "scenarioName": scenario_name
                }
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des scores {scenario_name} pour {username}: {e}")
            return None
    
    async def search_scenarios_by_name(
        self, 
        scenario_name: str, 
        page: int = 1, 
        max: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Recherche des scénarios par nom"""
        try:
            response = await self.client.get(
                f"{self.base_url}/scenarios/search-by-name",
                params={
                    "scenarioName": scenario_name,
                    "page": page,
                    "max": max
                }
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de scénarios {scenario_name}: {e}")
            return None
    
    async def get_global_leaderboard(
        self, 
        page: int = 1, 
        max: int = 100
    ) -> Optional[Dict[str, Any]]:
        """Récupère le leaderboard global"""
        try:
            response = await self.client.get(
                f"{self.base_url}/leaderboard/global-scores/get",
                params={"page": page, "max": max}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du leaderboard: {e}")
            return None
    
    async def clear_user_cache(self, username: str):
        """Supprime le cache d'un utilisateur"""
        await self.cache.clear_user_cache(username)
        logger.info(f"Cache supprimé pour l'utilisateur {username}")
    
    async def health_check(self) -> bool:
        """Vérifie si l'API KovaaK's est accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check KovaaK's API échoué: {e}")
            return False


# Fonction utilitaire pour créer une instance du service
def create_kovaaks_service() -> KovaaksService:
    """Crée une instance du service KovaaK's"""
    return KovaaksService()


