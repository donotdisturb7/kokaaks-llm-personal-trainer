from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.sql import func
from app.database import Base

class LocalStats(Base):
    """Modèle pour les statistiques locales (fichiers CSV uploadés)"""
    __tablename__ = "local_stats"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(255), nullable=False, index=True)
    score = Column(Float)
    accuracy = Column(Float)
    kills = Column(Integer)
    avg_ttk = Column(Float)  # Average Time To Kill
    sensitivity = Column(Float)
    fov = Column(Integer)
    cm360 = Column(Float)  # cm/360
    played_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_scenario', 'scenario_name'),
        Index('idx_played_at', 'played_at'),
    )

    def __repr__(self):
        return f"<LocalStats(scenario='{self.scenario_name}', score={self.score})>"

