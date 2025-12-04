#!/usr/bin/env python3
"""
Script pour générer des playlists KovaaK's basées sur les scénarios les plus populaires
(ceux avec le plus d'entries/joueurs dans les leaderboards globaux).

Utilise l'API KovaaK's via le proxy Node.js.
"""

import asyncio
import httpx
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
from collections import defaultdict


# ============================================================================
# Configuration
# ============================================================================

KOVAAKS_PROXY_URL = "http://localhost:9001"
OUTPUT_DIR = Path(__file__).parent.parent / 'playlists'

# Termes de recherche pour couvrir un MAXIMUM de scénarios
# On utilise toutes les lettres, chiffres et quelques termes courts pour maximiser la couverture
SEARCH_TERMS = (
    # Toutes les lettres de l'alphabet (pour capturer un maximum de scénarios)
    list("abcdefghijklmnopqrstuvwxyz") +
    # Tous les chiffres
    list("0123456789") +
    # Termes courants et scénarios connus
    ["VT", "Air", "1w", "tracking", "click", "switch", "tile", "pasu", "aim",
     "Kovaak", "Sandbox", "Intro", "Tutorial", "wall", "target", "flick",
     "voltaic", "angelic", "thin", "bounce", "strafe", "Revolving", "Smoothness"]
)

# Catégories d'aim (mêmes que dans l'ancien script)
AIM_CATEGORIES = {
    'tracking': {
        'aim_types': ['Tracking'],
        'keywords': ['track', 'air', 'smooth', 'follow', 'angelic', 'thin astr', 'voltaic', 'orb'],
        'description': 'Tracking - Suivi de cibles en mouvement'
    },
    'clicking': {
        'aim_types': ['Clicking'],
        'keywords': ['click', 'flick', 'pasu', '1w', 'tile', 'frenzy', 'reflex', 'pokeball', 'static'],
        'description': 'Clicking/Flicking - Précision sur cibles statiques/rapides'
    },
    'switching': {
        'aim_types': ['Target Switching'],
        'keywords': ['switch', 'target switch', 'multiclick', 'jumbo', 'sphere'],
        'description': 'Target Switching - Changement rapide entre cibles'
    },
    'speed': {
        'keywords': ['speed', 'fast', 'kinetic', 'reactive'],
        'description': 'Speed - Vitesse et réactivité'
    },
    'precision': {
        'keywords': ['precision', 'precise', 'microshot', 'small'],
        'description': 'Precision - Précision pure'
    },
    'evasive': {
        'keywords': ['evasive', 'dodge', 'strafe'],
        'description': 'Evasive - Mouvement et esquive'
    },
    'dynamic': {
        'keywords': ['dynamic', 'close', 'long strafes', 'bounce', 'floating'],
        'description': 'Dynamic - Scénarios dynamiques mixtes'
    }
}


# ============================================================================
# Fonctions utilitaires
# ============================================================================

def categorize_scenario(scenario_name: str, aim_type: str = None) -> str:
    """Catégorise un scénario basé sur son nom et son type d'aim."""
    scenario_lower = scenario_name.lower()

    # Chercher d'abord par aim_type si disponible
    if aim_type:
        for category, config in AIM_CATEGORIES.items():
            if 'aim_types' in config and aim_type in config['aim_types']:
                return category

    # Chercher par mots-clés dans le nom
    for category, config in AIM_CATEGORIES.items():
        for keyword in config.get('keywords', []):
            if keyword.lower() in scenario_lower:
                return category

    return 'other'


def write_playlist_file(filepath: Path, scenarios: List[Dict], description: str = ""):
    """Écrit un fichier playlist avec les infos d'entries."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        # Header avec description et stats
        if description:
            f.write(f"# {description}\n")
        f.write(f"# Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Nombre de scénarios: {len(scenarios)}\n")

        if scenarios:
            total_entries = sum(s['entries'] for s in scenarios)
            avg_entries = total_entries // len(scenarios)
            f.write(f"# Total entries: {total_entries:,}\n")
            f.write(f"# Moyenne entries: {avg_entries:,}\n")

        f.write("\n")

        # Liste des scénarios
        for i, scenario in enumerate(scenarios, 1):
            name = scenario['name']
            entries = scenario['entries']
            # Format: nom du scénario (avec commentaire sur le nombre d'entries)
            f.write(f"{name}  # {entries:,} players\n")

    print(f"✓ Playlist créée: {filepath.name} ({len(scenarios)} scénarios)")


# ============================================================================
# Récupération des données via l'API
# ============================================================================

async def search_scenarios(client: httpx.AsyncClient, search_term: str, max_results: int = 100) -> List[Dict]:
    """Recherche des scénarios via l'API KovaaK's."""
    try:
        response = await client.get(
            f"{KOVAAKS_PROXY_URL}/api/search/scenarios",
            params={"name": search_term, "max": max_results},
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()

        if not data.get('success'):
            print(f"⚠️  Échec de la recherche pour '{search_term}'")
            return []

        scenarios = data['data']['data']
        print(f"  '{search_term}': {len(scenarios)} scénarios trouvés")
        return scenarios

    except Exception as e:
        print(f"❌ Erreur lors de la recherche '{search_term}': {e}")
        return []


async def fetch_all_popular_scenarios() -> Dict[str, Dict]:
    """Récupère tous les scénarios populaires via plusieurs recherches."""
    print("🔍 Recherche des scénarios populaires...\n")

    all_scenarios = {}  # Dict[scenario_name, scenario_data]

    async with httpx.AsyncClient() as client:
        # Tester la connexion au proxy
        try:
            health = await client.get(f"{KOVAAKS_PROXY_URL}/health", timeout=5.0)
            if health.status_code != 200:
                raise Exception("Proxy non disponible")
            print("✓ Connexion au proxy KovaaK's établie\n")
        except Exception as e:
            print(f"❌ Impossible de se connecter au proxy KovaaK's: {e}")
            print(f"   Assurez-vous que le proxy tourne sur {KOVAAKS_PROXY_URL}")
            return {}

        # Rechercher avec chaque terme
        for term in SEARCH_TERMS:
            scenarios = await search_scenarios(client, term)

            # Ajouter les scénarios au dictionnaire (dédupliquer)
            for scenario in scenarios:
                name = scenario['scenarioName']
                entries = scenario['counts']['entries']
                plays = scenario['counts']['plays']
                aim_type = scenario['scenario'].get('aimType')

                # Garder le scénario s'il n'existe pas déjà ou s'il a plus d'entries
                if name not in all_scenarios or all_scenarios[name]['entries'] < entries:
                    all_scenarios[name] = {
                        'name': name,
                        'entries': entries,
                        'plays': plays,
                        'aim_type': aim_type,
                        'category': categorize_scenario(name, aim_type)
                    }

            # Petit délai pour ne pas surcharger l'API
            await asyncio.sleep(0.2)

    print(f"\n📊 Total de scénarios uniques trouvés: {len(all_scenarios)}")
    return all_scenarios


# ============================================================================
# Génération des playlists
# ============================================================================

async def generate_playlists():
    """Génère toutes les playlists."""
    print("🎯 Génération des playlists KovaaK's (par popularité)\n")
    print("=" * 70)
    print()

    # Récupérer tous les scénarios
    all_scenarios = await fetch_all_popular_scenarios()

    if not all_scenarios:
        print("\n⚠️  Aucun scénario trouvé. Vérifiez la connexion au proxy.")
        return

    # Convertir en liste et trier par nombre d'entries
    scenarios_list = sorted(
        all_scenarios.values(),
        key=lambda x: x['entries'],
        reverse=True
    )

    print(f"\n📈 Statistiques:")
    print(f"   - Total scénarios: {len(scenarios_list)}")
    print(f"   - Total entries: {sum(s['entries'] for s in scenarios_list):,}")
    print(f"   - Moyenne entries/scénario: {sum(s['entries'] for s in scenarios_list) // len(scenarios_list):,}")
    print()

    # 1. Playlist Top 50 Most Popular
    print("📝 Génération de la playlist 'Top 50 Most Popular'...")
    top_50 = scenarios_list[:50]
    write_playlist_file(
        OUTPUT_DIR / "top_50_most_popular.txt",
        top_50,
        "Top 50 scénarios les plus populaires (par nombre de joueurs)"
    )

    if len(top_50) >= 3:
        print(f"   Top 3:")
        for i, s in enumerate(top_50[:3], 1):
            print(f"      {i}. {s['name']} ({s['entries']:,} joueurs)")
    print()

    # 2. Playlist Top 100
    print("📝 Génération de la playlist 'Top 100 Most Popular'...")
    top_100 = scenarios_list[:100]
    write_playlist_file(
        OUTPUT_DIR / "top_100_most_popular.txt",
        top_100,
        "Top 100 scénarios les plus populaires (par nombre de joueurs)"
    )
    print()

    # 3. Playlists par catégorie d'aim
    print("📝 Génération des playlists par catégorie d'aim...")

    # Grouper par catégorie
    categorized = defaultdict(list)
    for scenario in scenarios_list:
        category = scenario['category']
        categorized[category].append(scenario)

    # Générer une playlist par catégorie
    for category, scenarios in categorized.items():
        if not scenarios:
            continue

        # Trier par entries dans chaque catégorie
        scenarios_sorted = sorted(scenarios, key=lambda x: x['entries'], reverse=True)

        # Limiter à 50 scénarios max par catégorie
        scenarios_top = scenarios_sorted[:50]

        # Nom de fichier et description
        if category == 'other':
            filename = "other_scenarios_popular.txt"
            description = "Autres scénarios populaires non catégorisés"
        else:
            category_config = AIM_CATEGORIES.get(category, {})
            filename = f"{category}_popular.txt"
            description = f"{category_config.get('description', category.capitalize())} - Scénarios populaires"

        write_playlist_file(
            OUTPUT_DIR / filename,
            scenarios_top,
            f"{description} ({len(scenarios_top)} scénarios)"
        )

    print()
    print("=" * 70)
    print("✅ Toutes les playlists ont été générées avec succès!")
    print(f"📁 Emplacement: {OUTPUT_DIR}")
    print()
    print("💡 Astuce: Copiez les fichiers .txt dans votre dossier KovaaK's Playlists:")
    print("   C:\\Program Files (x86)\\Steam\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\Playlists\\")


# ============================================================================
# Point d'entrée
# ============================================================================

def main():
    """Point d'entrée du script."""
    try:
        asyncio.run(generate_playlists())
    except KeyboardInterrupt:
        print("\n\n⚠️  Génération interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors de la génération des playlists: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
