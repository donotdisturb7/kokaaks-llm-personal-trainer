import pandas as pd
import io
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.stats import LocalStats

logger = logging.getLogger(__name__)

class StatsParser:
    """Service pour parser les fichiers CSV de stats KovaaK's"""
    
    def __init__(self):
        self.expected_columns = [
            'Scenario', 'Score', 'Accuracy', 'Kills', 'Avg TTK', 
            'Sensitivity', 'FOV', 'cm/360', 'Date'
        ]
    
    async def parse_csv_file(
        self, 
        file_content: bytes, 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Parse un fichier CSV et sauvegarde les stats"""
        try:
            # Lire le CSV
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Vérifier les colonnes
            missing_columns = [col for col in self.expected_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Colonnes manquantes: {missing_columns}")
            
            # Nettoyer les données
            df = self._clean_dataframe(df)
            
            # Créer les objets LocalStats
            stats_objects = []
            for _, row in df.iterrows():
                stat = LocalStats(
                    scenario_name=row['Scenario'],
                    score=row['Score'],
                    accuracy=row['Accuracy'],
                    kills=row['Kills'],
                    avg_ttk=row['Avg TTK'],
                    sensitivity=row['Sensitivity'],
                    fov=row['FOV'],
                    cm360=row['cm/360'],
                    played_at=row['Date']
                )
                stats_objects.append(stat)
            
            # Sauvegarder en base
            db.add_all(stats_objects)
            await db.commit()
            
            return {
                "total_entries": len(stats_objects),
                "unique_scenarios": df['Scenario'].nunique(),
                "date_range": {
                    "start": df['Date'].min().isoformat(),
                    "end": df['Date'].max().isoformat()
                }
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Erreur lors du parsing CSV: {e}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie le DataFrame"""
        # Supprimer les lignes vides
        df = df.dropna(subset=['Scenario', 'Score'])
        
        # Convertir les dates
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Supprimer les lignes avec des dates invalides
        df = df.dropna(subset=['Date'])
        
        # Convertir les types numériques
        numeric_columns = ['Score', 'Accuracy', 'Kills', 'Avg TTK', 'Sensitivity', 'FOV', 'cm/360']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    async def get_stats_summary(self, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """Récupère un résumé des stats locales"""
        try:
            # Calculer la date de début
            from datetime import timedelta
            start_date = datetime.now() - timedelta(days=days)
            
            # Récupérer les stats récentes
            result = await db.execute(
                select(LocalStats)
                .where(LocalStats.played_at >= start_date)
                .order_by(LocalStats.played_at.desc())
            )
            recent_stats = result.scalars().all()
            
            # Statistiques générales
            total_result = await db.execute(select(func.count(LocalStats.id)))
            total_entries = total_result.scalar()
            
            unique_scenarios_result = await db.execute(
                select(func.count(func.distinct(LocalStats.scenario_name)))
            )
            unique_scenarios = unique_scenarios_result.scalar()
            
            # Moyennes
            avg_score_result = await db.execute(
                select(func.avg(LocalStats.score))
                .where(LocalStats.played_at >= start_date)
            )
            average_score = avg_score_result.scalar() or 0
            
            avg_accuracy_result = await db.execute(
                select(func.avg(LocalStats.accuracy))
                .where(LocalStats.played_at >= start_date)
            )
            average_accuracy = avg_accuracy_result.scalar() or 0
            
            # Top scénarios par score
            top_scenarios_result = await db.execute(
                select(
                    LocalStats.scenario_name,
                    func.max(LocalStats.score).label('best_score'),
                    func.avg(LocalStats.score).label('avg_score'),
                    func.count(LocalStats.id).label('plays')
                )
                .where(LocalStats.played_at >= start_date)
                .group_by(LocalStats.scenario_name)
                .order_by(func.max(LocalStats.score).desc())
                .limit(10)
            )
            top_scenarios = [
                {
                    "scenario_name": row.scenario_name,
                    "best_score": float(row.best_score),
                    "avg_score": float(row.avg_score),
                    "plays": row.plays
                }
                for row in top_scenarios_result
            ]
            
            # Format des stats récentes
            recent_stats_data = [
                {
                    "id": stat.id,
                    "scenario_name": stat.scenario_name,
                    "score": stat.score,
                    "accuracy": stat.accuracy,
                    "kills": stat.kills,
                    "played_at": stat.played_at.isoformat() if stat.played_at else None
                }
                for stat in recent_stats
            ]
            
            return {
                "total_entries": total_entries,
                "unique_scenarios": unique_scenarios,
                "average_score": float(average_score),
                "average_accuracy": float(average_accuracy),
                "recent_stats": recent_stats_data,
                "top_scenarios": top_scenarios,
                "summary": {
                    "period_days": days,
                    "total_plays": len(recent_stats),
                    "avg_score": float(average_score),
                    "avg_accuracy": float(average_accuracy)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du résumé: {e}")
            raise
    
    async def get_scenario_stats(self, scenario_name: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """Récupère les stats d'un scénario spécifique"""
        try:
            # Récupérer toutes les stats pour ce scénario
            result = await db.execute(
                select(LocalStats)
                .where(LocalStats.scenario_name == scenario_name)
                .order_by(LocalStats.played_at.desc())
            )
            stats = result.scalars().all()
            
            if not stats:
                return None
            
            # Calculer les statistiques
            scores = [stat.score for stat in stats if stat.score is not None]
            accuracies = [stat.accuracy for stat in stats if stat.accuracy is not None]
            
            return {
                "scenario_name": scenario_name,
                "total_plays": len(stats),
                "best_score": max(scores) if scores else 0,
                "average_score": sum(scores) / len(scores) if scores else 0,
                "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
                "scores_history": [
                    {
                        "score": stat.score,
                        "accuracy": stat.accuracy,
                        "played_at": stat.played_at.isoformat() if stat.played_at else None
                    }
                    for stat in stats[:20]  # Limiter à 20 entrées récentes
                ]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats du scénario: {e}")
            raise

def create_stats_parser() -> StatsParser:
    return StatsParser()