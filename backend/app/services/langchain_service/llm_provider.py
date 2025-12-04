"""
LangChain LLM provider factory for unified LLM access.

Replaces the custom Protocol-based provider system with
LangChain's native LLM implementations.
"""

from typing import Optional
from langchain_core.language_models import BaseChatModel, BaseLLM
import logging

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_langchain_llm(
    settings: Optional[Settings] = None,
) -> BaseChatModel | BaseLLM:
    """
    Factory function to create the appropriate LangChain LLM based on configuration.

    Args:
        settings: Application settings. If None, will fetch from get_settings()

    Returns:
        LangChain BaseChatModel or BaseLLM instance

    Raises:
        ValueError: If the provider is not supported
    """
    if settings is None:
        settings = get_settings()

    provider = settings.llm_provider.lower()

    if provider == "groq":
        logger.info(f"Creating Groq LLM with model: {settings.groq_model}")
        from langchain_groq import ChatGroq

        return ChatGroq(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            temperature=0.7,
            timeout=30,
            max_retries=2,
        )

    elif provider == "ollama":
        logger.info(f"Creating Ollama LLM with model: {settings.ollama_model}")
        from langchain_community.llms import Ollama

        return Ollama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.7,
            timeout=30,
        )

    else:
        logger.warning(f"Unknown provider '{provider}', defaulting to Ollama")
        from langchain_community.llms import Ollama

        return Ollama(
            base_url=settings.ollama_base_url
            if hasattr(settings, "ollama_base_url")
            else "http://localhost:11434",
            model=settings.ollama_model
            if hasattr(settings, "ollama_model")
            else "llama2",
            temperature=0.7,
        )


async def health_check_llm(llm: BaseChatModel | BaseLLM) -> bool:
    """
    Check if the LLM is accessible and working.

    Args:
        llm: LangChain LLM instance

    Returns:
        True if healthy, False otherwise
    """
    try:
        if isinstance(llm, BaseChatModel):
            from langchain_core.messages import HumanMessage

            response = await llm.ainvoke([HumanMessage(content="test")])
            return bool(response.content)
        else:
            response = await llm.ainvoke("test")
            return bool(response)
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        return False
