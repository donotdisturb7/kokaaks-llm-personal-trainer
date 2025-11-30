from typing import Dict, Any, Optional, List, Protocol
import logging

from app.config import Settings
from app.services.ollama_service import OllamaService, create_ollama_service
from app.services.groq_service import GroqService, create_groq_service

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocol pour définir l'interface des providers IA"""
    
    async def health_check(self) -> bool:
        """Vérifie si le provider est accessible"""
        ...
    
    async def get_available_models(self) -> List[str]:
        """Récupère la liste des modèles disponibles"""
        ...
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        ...
    
    async def generate_aim_training_advice(
        self, 
        user_question: str,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """Génère des conseils spécialisés en entraînement de visée"""
        ...
    
    async def close(self):
        """Ferme la connexion"""
        ...


class LLMService:
    """Service manager pour gérer les différents providers IA"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider_name = settings.llm_provider.lower()
        self._provider: Optional[LLMProvider] = None
        
    async def __aenter__(self):
        """Context manager entry"""
        self._provider = self._create_provider()
        if hasattr(self._provider, '__aenter__'):
            await self._provider.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._provider and hasattr(self._provider, '__aexit__'):
            await self._provider.__aexit__(exc_type, exc_val, exc_tb)
    
    def _create_provider(self) -> LLMProvider:
        """Crée l'instance du provider basé sur la configuration"""
        if self.provider_name == "groq":
            logger.info("Utilisation du provider Groq")
            return create_groq_service(self.settings)
        elif self.provider_name == "ollama":
            logger.info("Utilisation du provider Ollama")
            return create_ollama_service(self.settings)
        else:
            logger.warning(f"Provider '{self.provider_name}' non reconnu, utilisation d'Ollama par défaut")
            return create_ollama_service(self.settings)
    
    @property
    def provider(self) -> LLMProvider:
        """Accède au provider actuel"""
        if self._provider is None:
            self._provider = self._create_provider()
        return self._provider
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé du provider actuel
        Retourne des informations sur le provider et son état
        """
        is_healthy = await self.provider.health_check()
        return {
            "provider": self.provider_name,
            "status": "healthy" if is_healthy else "unhealthy",
            "model": self._get_current_model()
        }
    
    def _get_current_model(self) -> str:
        """Récupère le modèle actuellement utilisé"""
        if self.provider_name == "groq":
            return self.settings.groq_model
        else:
            return self.settings.ollama_model
    
    async def get_available_models(self) -> List[str]:
        """Récupère la liste des modèles disponibles pour le provider actuel"""
        return await self.provider.get_available_models()
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        return await self.provider.generate_response(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt
        )
    
    async def generate_aim_training_advice(
        self, 
        user_question: str,
        user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """Génère des conseils spécialisés en entraînement de visée"""
        return await self.provider.generate_aim_training_advice(
            user_question=user_question,
            user_stats=user_stats
        )
    
    async def generate_rag_response(
        self,
        query: str,
        context: str,
        safety_level: str = "general"
    ) -> str:
        """Génère une réponse RAG basée sur le contexte fourni"""
        system_prompt = self._build_rag_system_prompt(safety_level)
        
        prompt = f"""Context provided:
{context}

User question: {query}

CRITICAL INSTRUCTIONS:
- Answer precisely and helpfully based ONLY on the provided context above
- INCLUDE ALL relevant information from the context in your answer - do NOT tell users to "check the PDF" or "refer to the document"
- QUOTE EXACTLY sharecodes, routine names, and instructions without modifying them
- When providing routines, ALWAYS include:
  * The complete sharecode (the long alphanumeric code after "Sharecode")
  * All scenarios/exercises with their exact names and durations
  * Any specific instructions or focus points mentioned
- If the context contains a sharecode, YOU MUST include it in your response
- Do NOT rephrase codes, numbers, or identifiers - copy them exactly as they appear
- When listing scenarios/exercises, preserve the exact format, numbering, and details from the source
- If the context doesn't contain sufficient information, say so clearly"""
        
        return await self.provider.generate_response(
            prompt=prompt,
            system_prompt=system_prompt
        )
    
    def _build_rag_system_prompt(self, safety_level: str) -> str:
        """Construit le prompt système pour RAG selon le niveau de sécurité"""
        base_prompt = """You are an AI assistant specialized in aim training and gaming injury prevention.
You provide advice based on reliable sources and are always cautious with medical recommendations.

CRITICAL - KovaaK's Sharecode Format:
- Sharecodes are LONG alphanumeric codes that appear AFTER the word "Sharecode" in the documents
- Format: "ROUTINE_NAME Sharecode LONGCODE"
- Example: "HAUNTR TRACK Sharecode KOVAAKSCLIPPINGCAFFEINATEDCASH" → sharecode is KOVAAKSCLIPPINGCAFFEINATEDCASH
- Another example: "Smoothness & Precision Easy Sharecode KOVAAKSBOOMSTICKINGFASTGULAG" → sharecode is KOVAAKSBOOMSTICKINGFASTGULAG
- The sharecode is what users copy-paste into KovaaK's Playlist tab
- Short codes (4-5 chars) before routine names are NOT sharecodes, they are routine IDs/tags"""
        
        if safety_level == "medical":
            return base_prompt + """
IMPORTANT: You're dealing with medical information. Always recommend consulting a healthcare professional
for any health concerns. Never provide medical diagnosis or treatment."""
        elif safety_level == "training":
            return base_prompt + """
You focus on training and performance improvement.
Be precise about recommended techniques and exercises."""
        else:  # general
            return base_prompt + """
You provide general advice on training and gaming.
For any medical advice, recommend consulting a healthcare professional."""
    
    async def close(self):
        """Ferme la connexion du provider"""
        if self._provider:
            await self._provider.close()


def create_llm_service(settings: Settings) -> LLMService:
    """Crée une instance du service LLM"""
    return LLMService(settings)


