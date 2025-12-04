import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict

# Ajouter le dossier backend au path pour importer les modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.stats import LocalStats


# ============================================================================
# Configuration des catégories d'aim
# ============================================================================

AIM_CATEGORIES = {
    'tracking': {
        'keywords': ['track', 'tracking', 'air', 'smooth', 'follow', 'air angelic', 'thin astr', 'voltaic'],
        'description': 'Tracking - Suivi de cibles en mouvement'
    },
    'clicking': {
        'keywords': ['click', 'flick', 'pasu', '1w', 'tile', 'frenzy', 'reflex', 'pokeball'],
        'description': 'Clicking/Flicking - Précision sur cibles statiques/rapides'
    },
    'switching': {
        'keywords': ['switch', 'target switch', 'multiclick', 'jumbo', '6 sphere'],
        'description': 'Target Switching - Changement rapide entre cibles'
    },
    'speed': {
        'keywords': ['speed', 'fast', 'thin', 'kinetic', 'reactive'],
        'description': 'Speed - Vitesse et réactivité'
    },
    'precision': {
        'keywords': ['precision', 'static', 'precise', 'microshot', 'small'],
        'description': 'Precision - Précision pure'
    },
    'evasive': {
        'keywords': ['evasive', 'dodge', 'strafe'],
        'description': 'Evasive - Mouvement et esquive'
    },
    'dynamic': {
        'keywords': ['dynamic', 'close', 'long strafes', 'bounce'],
        'description': 'Dynamic - Scénarios dynamiques mixtes'
    }
}


# ============================================================================
# Utilitaires
# ============================================================================

def categorize_scenario(scenario_name: str) -> str:
    """Catégorise un scénario basé sur son nom."""
    scenario_lower = scenario_name.lower()

    # Chercher la catégorie correspondante
    for category, config in AIM_CATEGORIES.items():
        for keyword in config['keywords']:
            if keyword.lower() in scenario_lower:
                return category

    # Par défaut, catégoriser comme "other"
    return 'other'


def format_playlist_entry(scenario_name: str) -> str:
    """Formate une entrée de playlist KovaaK's."""
    # Format simple: un scénario par ligne
    return scenario_name


def write_playlist_file(filepath: Path, scenarios: List[str], description: str = ""):
    """Écrit un fichier playlist."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        # Header optionnel avec description
        if description:
            f.write(f"# {description}\n")
            f.write(f"# Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Nombre de scénarios: {len(scenarios)}\n")
            f.write("\n")

        # Écrire chaque scénario
        for scenario in scenarios:
            f.write(f"{format_playlist_entry(scenario)}\n")

    print(f"✓ Playlist créée: {filepath.name} ({len(scenarios)} scénarios)")


# ============================================================================
# Requêtes base de données
# ============================================================================

async def get_most_played_scenarios(session: AsyncSession, limit: int = 50) -> List[Tuple[str, int]]:
    """Récupère les scénarios les plus joués."""
    query = (
        select(
            LocalStats.scenario_name,
            func.count(LocalStats.id).label('play_count')
        )
        .group_by(LocalStats.scenario_name)
        .order_by(text('play_count DESC'))
        .limit(limit)
    )

    result = await session.execute(query)
    return [(row.scenario_name, row.play_count) for row in result]


async def get_scenarios_by_category(session: AsyncSession) -> Dict[str, List[Tuple[str, int]]]:
    """Récupère tous les scénarios et les organise par catégorie."""
    # Récupérer tous les scénarios avec leur nombre de parties
    query = (
        select(
            LocalStats.scenario_name,
            func.count(LocalStats.id).label('play_count')
        )
        .group_by(LocalStats.scenario_name)
        .order_by(text('play_count DESC'))
    )

    result = await session.execute(query)
    all_scenarios = [(row.scenario_name, row.play_count) for row in result]

    # Catégoriser les scénarios
    categorized = defaultdict(list)
    for scenario_name, play_count in all_scenarios:
        category = categorize_scenario(scenario_name)
        categorized[category].append((scenario_name, play_count))

    return dict(categorized)


async def get_database_stats(session: AsyncSession) -> Dict:
    """Récupère des statistiques générales."""
    total_scenarios = await session.execute(
        select(func.count(func.distinct(LocalStats.scenario_name)))
    )
    total_plays = await session.execute(
        select(func.count(LocalStats.id))
    )

    return {
        'total_scenarios': total_scenarios.scalar(),
        'total_plays': total_plays.scalar()
    }


# ============================================================================
# Génération des playlists
# ============================================================================

async def generate_playlists(database_url: str, output_dir: Path):
    """Génère toutes les playlists."""
    # Créer le moteur de base de données
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("🎯 Génération des playlists KovaaK's\n")
    print("=" * 60)

    async with async_session_maker() as session:
        # Récupérer les statistiques
        stats = await get_database_stats(session)
        print(f"📊 Statistiques de la base de données:")
        print(f"   - Scénarios uniques: {stats['total_scenarios']}")
        print(f"   - Parties jouées: {stats['total_plays']}")
        print()

        if stats['total_scenarios'] == 0:
            print("⚠️  Aucun scénario trouvé dans la base de données.")
            print("   Uploadez d'abord vos statistiques via l'API /api/stats/upload")
            return

        # 1. Playlist des 50 scénarios les plus joués
        print("📝 Génération de la playlist 'Top 50 Most Played'...")
        most_played = await get_most_played_scenarios(session, limit=50)

        if most_played:
            scenarios = [name for name, _ in most_played]
            description = "Top 50 scénarios les plus joués"
            write_playlist_file(
                output_dir / "top_50_most_played.txt",
                scenarios,
                description
            )

            # Afficher quelques statistiques
            print(f"   Top 3: {most_played[0][0]} ({most_played[0][1]} parties)")
            if len(most_played) > 1:
                print(f"          {most_played[1][0]} ({most_played[1][1]} parties)")
            if len(most_played) > 2:
                print(f"          {most_played[2][0]} ({most_played[2][1]} parties)")
        print()

        # 2. Playlists par catégorie d'aim
        print("📝 Génération des playlists par catégorie d'aim...")
        categorized = await get_scenarios_by_category(session)

        for category, scenarios_data in categorized.items():
            if not scenarios_data:
                continue

            scenarios = [name for name, _ in scenarios_data]

            # Nom de fichier et description
            if category == 'other':
                filename = "other_scenarios.txt"
                description = "Autres scénarios non catégorisés"
            else:
                category_config = AIM_CATEGORIES.get(category, {})
                filename = f"{category}.txt"
                description = category_config.get('description', category.capitalize())

            write_playlist_file(
                output_dir / filename,
                scenarios,
                f"{description} ({len(scenarios)} scénarios)"
            )

    await engine.dispose()

    print()
    print("=" * 60)
    print("✅ Toutes les playlists ont été générées avec succès!")
    print(f"📁 Emplacement: {output_dir}")


# ============================================================================
# Point d'entrée
# ============================================================================

def main():
    """Point d'entrée du script."""
    # Charger les variables d'environnement
    from dotenv import load_dotenv

    # Chercher le fichier .env dans le dossier parent (backend)
    backend_dir = Path(__file__).parent.parent / 'backend'
    env_file = backend_dir / '.env'

    if not env_file.exists():
        # Essayer le .env à la racine du projet
        env_file = Path(__file__).parent.parent / '.env'

    if env_file.exists():
        load_dotenv(env_file)
        print(f"✓ Variables d'environnement chargées depuis: {env_file}")
    else:
        print("⚠️  Fichier .env non trouvé, utilisation des variables d'environnement système")

    # Récupérer l'URL de la base de données
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ Erreur: DATABASE_URL non défini dans les variables d'environnement")
        print("   Créez un fichier .env avec DATABASE_URL ou définissez la variable")
        sys.exit(1)

    # Dossier de sortie des playlists
    output_dir = Path(__file__).parent.parent / 'playlists'

    # Exécuter la génération
    try:
        asyncio.run(generate_playlists(database_url, output_dir))
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération des playlists: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
