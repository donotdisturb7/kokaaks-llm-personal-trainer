from typing import List
from langchain_core.embeddings import Embeddings

from app.services.embedding_service import EmbeddingService


class LangChainEmbeddingsWrapper(Embeddings):

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed search documents (synchronous wrapper).

        Note: LangChain's base Embeddings class expects sync methods,
        but we can override with async methods for better performance.
        """
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're already in an async context, we need to use run_in_executor
            raise RuntimeError(
                "embed_documents called in async context, use aembed_documents instead"
            )
        return loop.run_until_complete(self.embedding_service.embed_texts(texts))

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query (synchronous wrapper).
        """
        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            raise RuntimeError(
                "embed_query called in async context, use aembed_query instead"
            )
        return loop.run_until_complete(self.embedding_service.embed_text(text))

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Async embed multiple documents.
        """
        return await self.embedding_service.embed_texts(texts)

    async def aembed_query(self, text: str) -> List[float]:
        """
        Async embed a single query.
        """
        return await self.embedding_service.embed_text(text)


def create_langchain_embeddings() -> Embeddings:

    return LangChainEmbeddingsWrapper()
