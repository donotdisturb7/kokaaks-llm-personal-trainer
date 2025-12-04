"""Services package - Core business logic and integrations"""

# LangChain integration services
from app.services.langchain_service import (
    create_langchain_embeddings,
    create_langchain_llm,
    create_langchain_vector_store,
    create_rag_chain,
    create_context_chain,
    create_conversational_chain,
)

# Core services
from app.services.llm_service import LLMService, create_llm_service
from app.services.llm_context_builder import (
    LLMContextBuilder,
    create_llm_context_builder,
)
from app.services.rag_service import RAGService
from app.services.embedding_service import EmbeddingService
from app.services.cache_service import CacheService
from app.services.kovaaks_service import KovaaksService, create_kovaaks_service
from app.services.pdf_service import PDFService
from app.services.stats_parser import StatsParser

__all__ = [
    # LangChain
    "create_langchain_embeddings",
    "create_langchain_llm",
    "create_langchain_vector_store",
    "create_rag_chain",
    "create_context_chain",
    "create_conversational_chain",
    # Core services
    "LLMService",
    "create_llm_service",
    "LLMContextBuilder",
    "create_llm_context_builder",
    "RAGService",
    "EmbeddingService",
    "CacheService",
    "KovaaksService",
    "create_kovaaks_service",
    "PDFService",
    "StatsParser",
]
