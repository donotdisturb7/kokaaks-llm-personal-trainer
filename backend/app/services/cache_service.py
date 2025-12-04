from typing import Optional, Any
import json
import logging
from redis import asyncio as aioredis
from app.database import get_redis

logger = logging.getLogger(__name__)

class CacheService:
    """Service de gestion du cache Redis"""
    
    def __init__(self):
        self.ttl_context = 300      # 5 min pour contexte LLM
        self.ttl_stats = 3600       # 1h pour stats KovaaK's
        self.ttl_profile = 7200     # 2h pour profil
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        try:
            redis = await get_redis()
            value = await redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du cache {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int):
        """Stocke une valeur dans le cache avec TTL"""
        try:
            redis = await get_redis()
            await redis.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"Erreur lors du stockage en cache {key}: {e}")
    
    async def delete(self, key: str):
        """Supprime une clé du cache"""
        try:
            redis = await get_redis()
            await redis.delete(key)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du cache {key}: {e}")
    
    async def delete_pattern(self, pattern: str):
        """Supprime toutes les clés correspondant au pattern"""
        try:
            redis = await get_redis()
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du pattern {pattern}: {e}")
    
    # Cache contexte LLM
    async def get_user_context(self, user_id: int) -> Optional[dict]:
        """Récupère le contexte utilisateur du cache"""
        return await self.get(f"llm:context:{user_id}")
    
    async def set_user_context(self, user_id: int, context: dict):
        """Stocke le contexte utilisateur dans le cache"""
        await self.set(f"llm:context:{user_id}", context, self.ttl_context)
    
    async def delete_user_context(self, user_id: int):
        """Supprime le contexte utilisateur du cache"""
        await self.delete(f"llm:context:{user_id}")
    
    # Cache stats KovaaK's
    async def get_kovaaks_profile(self, username: str) -> Optional[dict]:
        """Récupère le profil KovaaK's du cache"""
        return await self.get(f"kovaaks:profile:{username}")
    
    async def set_kovaaks_profile(self, username: str, profile: dict):
        """Stocke le profil KovaaK's dans le cache"""
        await self.set(f"kovaaks:profile:{username}", profile, self.ttl_profile)
    
    async def get_kovaaks_scenarios(self, username: str) -> Optional[list]:
        """Récupère les scénarios KovaaK's du cache"""
        return await self.get(f"kovaaks:scenarios:{username}")
    
    async def set_kovaaks_scenarios(self, username: str, scenarios: list):
        """Stocke les scénarios KovaaK's dans le cache"""
        await self.set(f"kovaaks:scenarios:{username}", scenarios, self.ttl_stats)
    
    async def get_kovaaks_highscores(self, username: str) -> Optional[list]:
        """Récupère les high scores KovaaK's du cache"""
        return await self.get(f"kovaaks:highscores:{username}")
    
    async def set_kovaaks_highscores(self, username: str, highscores: list):
        """Stocke les high scores KovaaK's dans le cache"""
        await self.set(f"kovaaks:highscores:{username}", highscores, self.ttl_stats)
    
    async def get_kovaaks_benchmarks(self, username: str) -> Optional[list]:
        """Récupère les benchmarks KovaaK's du cache"""
        return await self.get(f"kovaaks:benchmarks:{username}")
    
    async def set_kovaaks_benchmarks(self, username: str, benchmarks: list):
        """Stocke les benchmarks KovaaK's dans le cache"""
        await self.set(f"kovaaks:benchmarks:{username}", benchmarks, self.ttl_stats)
    
    async def get_kovaaks_favorites(self, username: str) -> Optional[list]:
        """Récupère les favoris KovaaK's du cache"""
        return await self.get(f"kovaaks:favorites:{username}")
    
    async def set_kovaaks_favorites(self, username: str, favorites: list):
        """Stocke les favoris KovaaK's dans le cache"""
        await self.set(f"kovaaks:favorites:{username}", favorites, self.ttl_stats)
    
    # Cache stats summary avec versioning
    async def get_stats_version(self) -> int:
        """Récupère la version actuelle du contexte stats"""
        try:
            redis = await get_redis()
            version = await redis.get("stats:ctxVersion")
            return int(version) if version else 1
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la version: {e}")
            return 1
    
    async def increment_stats_version(self) -> int:
        """Incrémente la version du contexte stats (appelé après upload CSV)"""
        try:
            redis = await get_redis()
            new_version = await redis.incr("stats:ctxVersion")
            logger.info(f"Version stats incrémentée à {new_version}")
            return new_version
        except Exception as e:
            logger.error(f"Erreur lors de l'incrémentation de version: {e}")
            return 1
    
    async def get_stats_summary(self, days: int = 30) -> Optional[dict]:
        """Récupère le summary des stats avec cache versionné"""
        try:
            version = await self.get_stats_version()
            key = f"stats:summary:v{version}:days{days}"
            return await self.get(key)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du summary: {e}")
            return None
    
    async def set_stats_summary(self, summary: dict, days: int = 30, ttl: int = 300):
        """Stocke le summary des stats avec version"""
        try:
            version = await self.get_stats_version()
            key = f"stats:summary:v{version}:days{days}"
            await self.set(key, summary, ttl)
        except Exception as e:
            logger.error(f"Erreur lors du stockage du summary: {e}")
    
    async def invalidate_stats_cache(self):
        """Invalide tout le cache des stats en incrémentant la version"""
        await self.increment_stats_version()
        # Optionnel: nettoyer les anciennes clés de cache
        await self.delete_pattern("stats:summary:v*")
    
    # Méthodes de nettoyage
    async def clear_user_cache(self, username: str):
        """Supprime tout le cache d'un utilisateur"""
        await self.delete_pattern(f"kovaaks:*:{username}")
    
    async def clear_all_cache(self):
        """Supprime tout le cache (attention!)"""
        await self.delete_pattern("llm:*")
        await self.delete_pattern("kovaaks:*")


