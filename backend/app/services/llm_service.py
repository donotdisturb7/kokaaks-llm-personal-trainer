"""
LLM Service - Simplified version using LangChain providers

This service now uses LangChain's native LLM providers instead of
custom Protocol-based wrappers, reducing code by ~120 lines.
"""

from typing import Dict, Any, Optional, List
import logging

from app.config import Settings, get_settings
from app.services.langchain_service.llm_provider import (
    create_langchain_llm,
    health_check_llm,
)
from langchain_core.language_models import BaseChatModel, BaseLLM
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service manager for LLM operations using LangChain.

    This replaces the old Protocol-based system with LangChain's native providers.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider_name = settings.llm_provider.lower()
        self._llm: Optional[BaseChatModel | BaseLLM] = None

    async def __aenter__(self):
        """Context manager entry"""
        self._llm = create_langchain_llm(self.settings)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # LangChain LLMs don't need explicit cleanup
        pass

    @property
    def llm(self) -> BaseChatModel | BaseLLM:
        """Get or create the LLM instance"""
        if self._llm is None:
            self._llm = create_langchain_llm(self.settings)
        return self._llm

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the LLM provider is healthy.

        Returns:
            {"provider": "groq", "status": "healthy", "model": "mixtral-8x7b-32768"}
        """
        is_healthy = await health_check_llm(self.llm)
        return {
            "provider": self.provider_name,
            "status": "healthy" if is_healthy else "unhealthy",
            "model": self._get_current_model(),
        }

    def _get_current_model(self) -> str:
        """Get the currently configured model name"""
        if self.provider_name == "groq":
            return self.settings.groq_model
        else:
            return self.settings.ollama_model

    async def get_available_models(self) -> List[str]:
        """
        Get available models for the current provider.

        Note: This is provider-specific and may not be supported by all LangChain LLMs.
        """
        # For now, return the configured model
        # LangChain doesn't have a standard interface for listing models
        return [self._get_current_model()]

    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a response from a prompt.

        Args:
            prompt: User prompt
            model: Optional model override (not implemented in LangChain wrapper)
            system_prompt: Optional system prompt to prepend

        Returns:
            Generated response string
        """
        try:
            if isinstance(self.llm, BaseChatModel):
                # Chat model - use messages
                messages = []
                if system_prompt:
                    messages.append(SystemMessage(content=system_prompt))
                messages.append(HumanMessage(content=prompt))

                response = await self.llm.ainvoke(messages)
                return response.content
            else:
                # Regular LLM - use string prompt
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"

                response = await self.llm.ainvoke(full_prompt)
                return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def generate_aim_training_advice(
        self, user_question: str, user_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate specialized aim training advice.

        This method includes a specialized system prompt for aim training.
        """
        system_prompt = """You are a specialized aim training coach for KovaaK's FPS Aim Trainer.
You help players improve their accuracy and performance.

Provide clear, actionable advice that:
- Is specific and practical
- References established aim training techniques
- Considers the user's current skill level
- Is encouraging but realistic
"""

        # If user stats provided, add to system prompt
        if user_stats:
            system_prompt += f"\n\nUser Statistics:\n{self._format_stats(user_stats)}"

        return await self.generate_response(
            prompt=user_question, system_prompt=system_prompt
        )

    async def generate_rag_response(
        self, query: str, context: str, safety_level: str = "general"
    ) -> str:
        """
        Generate a RAG response based on provided context.

        Note: This is kept for backward compatibility with the old RAG service.
        New code should use the LangChain RAG chains directly.
        """
        system_prompt = self._build_rag_system_prompt(safety_level)

        prompt = f"""Context provided:
{context}

User question: {query}

CRITICAL INSTRUCTIONS:
- Answer precisely and helpfully based ONLY on the provided context above
- INCLUDE ALL relevant information from the context in your answer
- QUOTE EXACTLY sharecodes, routine names, and instructions without modifying them
- If the context contains a sharecode, YOU MUST include it in your response
- Do NOT tell users to "check the PDF" or "refer to the document"
"""

        return await self.generate_response(prompt=prompt, system_prompt=system_prompt)

    def _build_rag_system_prompt(self, safety_level: str) -> str:
        """Build RAG system prompt based on safety level"""
        base_prompt = """You are an AI assistant specialized in aim training and gaming injury prevention.
You provide advice based on reliable sources and are always cautious with medical recommendations.

CRITICAL - KovaaK's Sharecode Format:
- Sharecodes are LONG alphanumeric codes after the word "Sharecode"
- The sharecode is what users copy-paste into KovaaK's Playlist tab"""

        if safety_level == "medical":
            return (
                base_prompt
                + "\n\nIMPORTANT: Always recommend consulting a healthcare professional for medical concerns."
            )
        elif safety_level == "training":
            return (
                base_prompt
                + "\n\nFocus on training and performance improvement techniques."
            )
        else:  # general
            return base_prompt

    def _format_stats(self, stats: Dict[str, Any]) -> str:
        """Format user stats for inclusion in prompts"""
        lines = []
        for key, value in stats.items():
            if isinstance(value, (int, float, str)):
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    async def close(self):
        """Close the LLM service (for backward compatibility)"""
        # LangChain LLMs don't need explicit cleanup
        pass


def create_llm_service(settings: Optional[Settings] = None) -> LLMService:
    """
    Factory function to create an LLM service.

    Args:
        settings: Optional settings. If None, uses get_settings()

    Returns:
        LLMService instance
    """
    if settings is None:
        settings = get_settings()
    return LLMService(settings)
