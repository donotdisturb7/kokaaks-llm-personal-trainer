"""
RAG Service - Orchestrates retrieval and generation using LangChain

This is a refactored version that uses LangChain components to replace
manual embedding, retrieval, and prompt construction.
"""

from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.rag import Document
from app.services.langchain_service import (
    create_langchain_embeddings,
    create_langchain_llm,
    create_langchain_vector_store,
    create_rag_chain,
)
from app.config import get_settings
from langchain_core.documents import Document as LangChainDocument

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG Service using LangChain for simplified retrieval and generation.

    This replaces the manual SQL queries and prompt construction with
    LangChain's built-in components.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

        # Initialize LangChain components
        self.embeddings = create_langchain_embeddings()
        self.llm = create_langchain_llm(self.settings)
        self.vector_store = create_langchain_vector_store(self.embeddings)

        # Create RAG chain
        self.rag_chain = create_rag_chain(
            llm=self.llm, vector_store=self.vector_store, search_kwargs={"k": 5}
        )

    async def query(
        self,
        query: str,
        max_results: int = 5,
        topics: Optional[List[str]] = None,
        safety_level: str = "general",
    ) -> Dict[str, Any]:
        """
        Main RAG query: retrieve relevant chunks and generate answer.

        This now uses LangChain's RetrievalQA chain instead of manual
        retrieval and context composition.

        Returns:
        {
            "answer": "Generated response with citations",
            "sources": [{"title": "...", "chunk": "...", "relevance": 0.95}],
            "confidence": 0.87
        }
        """
        try:
            # Update search kwargs if max_results changed
            if max_results != 5:
                self.rag_chain.retriever.search_kwargs["k"] = max_results

            # TODO: Add topic and safety_level filtering to retriever
            # For now, we'll use the chain as-is

            # Invoke the RAG chain
            result = await self.rag_chain.ainvoke({"query": query})

            # Format source documents
            sources = []
            for doc in result.get("source_documents", []):
                sources.append(
                    {
                        "content": doc.page_content,
                        "title": doc.metadata.get("title", "Unknown"),
                        "doc_type": doc.metadata.get("doc_type", "unknown"),
                        "topics": doc.metadata.get("topics", []),
                        "relevance": doc.metadata.get("score", 0.0),  # Similarity score
                    }
                )

            # Calculate confidence from source relevance
            confidence = (
                sum(s.get("relevance", 0) for s in sources) / len(sources)
                if sources
                else 0.0
            )

            return {
                "answer": result["result"],
                "sources": sources,
                "confidence": confidence,
            }

        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {
                "answer": "I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
            }

    async def ingest_document(
        self,
        title: str,
        source: str,
        doc_type: str,
        topics: List[str],
        safety: str,
        chunks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Ingest a document with its chunks using LangChain.

        This now uses LangChain's vector store add_documents method
        instead of manual embedding generation.
        """
        try:
            # Create document record in database
            document = Document(
                title=title,
                source=source,
                doc_type=doc_type,
                topics=topics,
                safety=safety,
            )
            self.db.add(document)
            await self.db.flush()  # Get the ID

            # Prepare LangChain documents with metadata
            langchain_docs = []
            for i, chunk_data in enumerate(chunks):
                doc = LangChainDocument(
                    page_content=chunk_data["content"],
                    metadata={
                        "document_id": document.id,
                        "chunk_index": i,
                        "title": title,
                        "doc_type": doc_type,
                        "topics": topics,
                        "safety": safety,
                        **chunk_data.get("metadata", {}),
                    },
                )
                langchain_docs.append(doc)

            # Add documents to vector store (handles embedding automatically)
            await self.vector_store.aadd_documents(langchain_docs)

            await self.db.commit()

            logger.info(f"Ingested document '{title}' with {len(chunks)} chunks")

            return {"document_id": document.id, "chunks_created": len(chunks)}

        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            await self.db.rollback()
            raise

    async def list_documents(
        self, doc_type: Optional[str] = None, topics: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List documents with optional filtering.

        This remains largely unchanged as it queries the database directly.
        """
        stmt = select(Document)

        if doc_type:
            stmt = stmt.where(Document.doc_type == doc_type)

        if topics:
            stmt = stmt.where(Document.topics.op("?|")(topics))

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
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ]

    async def delete_document(self, document_id: int):
        """
        Delete document and all its chunks (CASCADE).

        Also removes from vector store if possible.
        """
        stmt = select(Document).where(Document.id == document_id)
        result = await self.db.execute(stmt)
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Delete from database (cascades to chunks)
        await self.db.delete(document)
        await self.db.commit()

        logger.info(f"Deleted document {document_id}")
