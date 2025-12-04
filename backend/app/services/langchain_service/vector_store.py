"""
LangChain PGVector integration for the existing pgvector database.

This wraps the existing PostgreSQL + pgvector setup with LangChain's
PGVector class for seamless integration with chains and retrievers.
"""

from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)


def create_langchain_vector_store(
    embeddings: Embeddings, collection_name: str = "rag_documents"
) -> PGVector:
    """
    Create a LangChain PGVector store connected to the existing database.

    This reuses the existing PostgreSQL + pgvector setup but provides
    a LangChain-compatible interface.

    Args:
        embeddings: LangChain embeddings instance
        collection_name: Name of the collection (table prefix)

    Returns:
        PGVector instance
    """
    settings = get_settings()

    # Build connection string
    connection_string = (
        f"postgresql+psycopg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )

    logger.info(f"Creating PGVector store with collection: {collection_name}")

    try:
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection_string,
            use_jsonb=True,
            async_mode=True,  # Enable async support for aadd_documents
        )

        return vector_store

    except Exception as e:
        logger.error(f"Failed to create PGVector store: {e}")
        raise


async def get_vector_store_with_embeddings(
    embeddings: Optional[Embeddings] = None,
) -> PGVector:
    """
    Convenience function to get a vector store with default embeddings.

    Args:
        embeddings: Optional embeddings instance. If None, creates default.

    Returns:
        PGVector instance ready to use
    """
    if embeddings is None:
        from app.services.langchain.embeddings import create_langchain_embeddings

        embeddings = create_langchain_embeddings()

    return create_langchain_vector_store(embeddings)
