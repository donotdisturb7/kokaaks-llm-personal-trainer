"""
Modèles pour le fine-tuning et la curation de datasets
Permet de collecter et organiser des exemples d'entraînement
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class TrainingExample(Base):
    """
    Modèle pour les exemples d'entraînement collectés depuis diverses sources
    Utilisé pour préparer des datasets de fine-tuning
    """
    __tablename__ = "training_examples"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(20), nullable=False)  # 'conversation', 'csv', 'manual'
    input_text = Column(Text, nullable=False)  # Texte d'entrée (prompt)
    target_text = Column(Text, nullable=False)  # Texte cible (réponse attendue)
    meta = Column(JSONB)  # Métadonnées additionnelles (tags, quality_score, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("source IN ('conversation', 'csv', 'manual')", name='check_source'),
        Index('idx_training_source', 'source'),
        Index('idx_training_meta', 'meta', postgresql_using='gin', postgresql_ops={'meta': 'jsonb_ops'}),
    )

    def __repr__(self):
        return f"<TrainingExample(id={self.id}, source='{self.source}')>"


class Dataset(Base):
    """
    Modèle pour regrouper des exemples d'entraînement en datasets
    Permet d'organiser les exemples pour différents usages de fine-tuning
    """
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}')>"


class DatasetExample(Base):
    """
    Table de jonction entre datasets et exemples d'entraînement
    Permet à un exemple d'appartenir à plusieurs datasets
    """
    __tablename__ = "dataset_examples"

    dataset_id = Column(Integer, ForeignKey('datasets.id', ondelete='CASCADE'), primary_key=True)
    example_id = Column(Integer, ForeignKey('training_examples.id', ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return f"<DatasetExample(dataset_id={self.dataset_id}, example_id={self.example_id})>"

