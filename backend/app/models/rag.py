from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base


EMBEDDING_DIM = 384  # Dimension par défaut (FastEmbed bge-small)


class Document(Base):
    __tablename__ = "rag_documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(255), nullable=True)  # chemin/url
    doc_type = Column(String(50), nullable=True)  # guideline, review, blog, pdf
    topics = Column(JSONB, nullable=True)  # ["wrist", "shoulder", ...]
    safety = Column(String(50), nullable=True)  # medical, general, training
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_rag_docs_title", "title"),
        Index("idx_rag_docs_type", "doc_type"),
    )


class DocumentChunk(Base):
    __tablename__ = "rag_document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("rag_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_rag_chunks_doc_idx", "document_id", "chunk_index"),
        Index("idx_rag_chunks_embedding", "embedding", postgresql_using="ivfflat"),
    )


