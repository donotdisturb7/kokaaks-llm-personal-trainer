"""
Modèle pour les conversations avec le LLM
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class Conversation(Base):
    """Modèle pour les conversations avec l'IA"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text)
    messages = Column(JSONB, nullable=False)  # Liste de {role, content, timestamp}
    context_used = Column(JSONB)  # Contexte stats utilisé pour cette conversation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_created', 'created_at'),
        # Index GIN pour JSON - spécifier l'opérateur pour PostgreSQL 15
        Index('idx_messages', 'messages', postgresql_using='gin', postgresql_ops={'messages': 'jsonb_ops'}),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"

