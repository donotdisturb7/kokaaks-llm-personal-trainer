from typing import List, Optional
import asyncio
from fastembed import TextEmbedding
import numpy as np


class EmbeddingService:
    def __init__(self):
        self.model = None
        self._model_loaded = False
    
    async def _ensure_model_loaded(self):
        """Lazy load the embedding model"""
        if not self._model_loaded:
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                None, 
                lambda: TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            )
            self._model_loaded = True
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        await self._ensure_model_loaded()
        
        # Run embedding in thread pool
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: list(next(self.model.embed([text])))
        )
        
        return embedding
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch)"""
        await self._ensure_model_loaded()
        
        # Run embedding in thread pool
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: [list(emb) for emb in self.model.embed(texts)]
        )
        
        return embeddings
    
    async def health_check(self) -> bool:
        """Check if embedding service is working"""
        try:
            test_embedding = await self.embed_text("test")
            return len(test_embedding) == 384  # bge-small dimension
        except Exception:
            return False
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return 384  # BAAI/bge-small-en-v1.5 dimension
