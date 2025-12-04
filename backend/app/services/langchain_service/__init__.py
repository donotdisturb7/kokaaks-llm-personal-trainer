"""
LangChain integration package for RAG, embeddings, LLM providers, and chains.
"""

from .embeddings import create_langchain_embeddings
from .llm_provider import create_langchain_llm, health_check_llm
from .vector_store import (
    create_langchain_vector_store,
    get_vector_store_with_embeddings,
)
from .chains import (
    create_rag_chain,
    create_context_chain,
    create_conversational_chain,
    format_context_for_prompt,
)

__all__ = [
    "create_langchain_embeddings",
    "create_langchain_llm",
    "health_check_llm",
    "create_langchain_vector_store",
    "get_vector_store_with_embeddings",
    "create_rag_chain",
    "create_context_chain",
    "create_conversational_chain",
    "format_context_for_prompt",
]
