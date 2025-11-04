"""
RAG Service - Orchestrates retrieval and generation
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.models.rag import Document, DocumentChunk
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import create_llm_service
from app.config import settings


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.llm_service = create_llm_service(settings)
    
    async def query(
        self,
        query: str,
        max_results: int = 5,
        topics: Optional[List[str]] = None,
        safety_level: str = "general"
    ) -> Dict[str, Any]:
        """
        Main RAG query: retrieve relevant chunks and generate answer
        
        Returns:
        {
            "answer": "Generated response with citations",
            "sources": [{"title": "...", "chunk": "...", "relevance": 0.95}],
            "confidence": 0.87
        }
        """
        # 1. Generate embedding for query
        query_embedding = await self.embedding_service.embed_text(query)
        
        # 2. Retrieve relevant chunks using vector similarity
        relevant_chunks = await self._retrieve_chunks(
            query_embedding, max_results, topics, safety_level
        )
        
        if not relevant_chunks:
            return {
                "answer": "I don't have relevant information to answer your question. Please try rephrasing or check if relevant documents have been ingested.",
                "sources": [],
                "confidence": 0.0
            }
        
        # 3. Compose context from chunks
        context = self._compose_context(relevant_chunks)
        
        # 4. Generate answer using LLM
        answer = await self.llm_service.generate_rag_response(
            query=query,
            context=context,
            safety_level=safety_level
        )
        
        # 5. Calculate confidence based on chunk relevance
        confidence = sum(chunk.get("relevance", 0) for chunk in relevant_chunks) / len(relevant_chunks)
        
        return {
            "answer": answer,
            "sources": relevant_chunks,
            "confidence": confidence
        }
    
    async def _retrieve_chunks(
        self,
        query_embedding: List[float],
        max_results: int,
        topics: Optional[List[str]] = None,
        safety_level: str = "general"
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant chunks using vector similarity"""
        
        # Build SQL query with vector similarity
        sql = """
        SELECT 
            dc.id,
            dc.content,
            dc.chunk_metadata,
            d.title,
            d.doc_type,
            d.topics,
            d.safety,
            1 - (dc.embedding <=> %s) as relevance
        FROM rag_document_chunks dc
        JOIN rag_documents d ON dc.document_id = d.id
        WHERE d.safety = %s
        """
        
        params = [query_embedding, safety_level]
        
        # Add topic filtering if specified
        if topics:
            sql += " AND d.topics ?| %s"
            params.append(topics)
        
        sql += " ORDER BY dc.embedding <=> %s LIMIT %s"
        params.extend([query_embedding, max_results])

        result = await self.db.execute(text(sql), params)
        chunks = []

        for row in result:
            chunks.append({
                "id": row.id,
                "content": row.content,
                "title": row.title,
                "doc_type": row.doc_type,
                "topics": row.topics,
                "relevance": float(row.relevance)
            })
        
        return chunks
    
    def _compose_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Compose context from retrieved chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n"
                f"{chunk['content']}\n"
                f"Relevance: {chunk['relevance']:.2f}\n"
            )
        
        return "\n".join(context_parts)
    
    async def ingest_document(
        self,
        title: str,
        source: str,
        doc_type: str,
        topics: List[str],
        safety: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ingest a document with its chunks and embeddings"""
        
        # Create document
        document = Document(
            title=title,
            source=source,
            doc_type=doc_type,
            topics=topics,
            safety=safety
        )
        self.db.add(document)
        await self.db.flush()  # Get the ID after INSERT
        
        # Process chunks
        chunk_objects = []
        for i, chunk_data in enumerate(chunks):
            # Generate embedding for chunk
            embedding = await self.embedding_service.embed_text(chunk_data["content"])
            
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_data["content"],
                chunk_metadata=chunk_data.get("metadata", {}),
                embedding=embedding
            )
            chunk_objects.append(chunk)
        
        self.db.add_all(chunk_objects)
        await self.db.commit()
        
        return {
            "document_id": document.id,
            "chunks_created": len(chunk_objects)
        }
    
    async def list_documents(
        self,
        doc_type: Optional[str] = None,
        topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List documents with optional filtering"""
        
        stmt = select(Document)
        
        if doc_type:
            stmt = stmt.where(Document.doc_type == doc_type)
        
        if topics:
            stmt = stmt.where(Document.topics.op('?|')(topics))
        
        result = await self.db.execute(stmt)
        documents = result.scalars().all()
        
        return [
            {
                "id": doc.id,
                "title": doc.title,
                "source": doc.source,
                "doc_type": doc.doc_type,
                "topics": doc.topics or [],
                "safety": doc.safety,
                "created_at": doc.created_at.isoformat()
            }
            for doc in documents
        ]
    
    async def delete_document(self, document_id: int):
        """Delete document and all its chunks (CASCADE)"""
        stmt = select(Document).where(Document.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()
        
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        await self.db.delete(document)
        await self.db.commit()
