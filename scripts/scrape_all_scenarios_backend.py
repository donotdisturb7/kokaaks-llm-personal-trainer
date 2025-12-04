#!/usr/bin/env python3
"""
Script pour récupérer TOUS les scénarios KovaaK's via le backend API
en itérant sur les leaderboardIds et en récupérant les noms via le proxy.
"""

import asyncio
import httpx
from typing import Dict, List
from pathlib import Path
from collections import defaultdict
from datetime import datetime

KOVAAKS_BACKEND = "https://kovaaks.com/webapp-backend"
KOVAAKS_PROXY = "http://localhost:9001"
OUTPUT_DIR = Path(__file__).parent.parent / 'playlists'

# Catégories d'aim
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
}


def categorize_scenario(scenario_name: str, aim_type: str = None) -> str:
    """Catégorise un scénario."""
    scenario_lower = scenario_name.lower()

    if aim_type:
        for category, config in AIM_CATEGORIES.items():
            if 'aim_types' in config and aim_type in config['aim_types']:
                return category

    for category, config in AIM_CATEGORIES.items():
        for keyword in config.get('keywords', []):
            if keyword.lower() in scenario_lower:
                return category

    return 'other'


def write_playlist_file(filepath: Path, scenarios: List[Dict], description: str = ""):
    """Écrit un fichier playlist."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
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

        for scenario in scenarios:
            name = scenario['name']
            entries = scenario['entries']
            f.write(f"{name}  # {entries:,} players\n")

    print(f"✓ Playlist créée: {filepath.name} ({len(scenarios)} scénarios)")


async def main():
    print("🎯 Récupération de TOUS les scénarios KovaaK's via backend API\n")
    print("=" * 70)
    print()

    # Étape 1: Scanner les leaderboardIds pour obtenir les entries
    print("📊 Étape 1: Scan des leaderboardIds (1-20000)...")
    print("   Cela peut prendre 5-10 minutes...")
    print()

    scenarios_by_id = {}

    async with httpx.AsyncClient() as client:
        for i in range(1, 20001, 100):
            batch_end = min(i + 100, 20001)

            tasks = []
            for lid in range(i, batch_end):
                async def get_entries(leaderboard_id):
                    try:
                        resp = await client.get(
                            f"{KOVAAKS_BACKEND}/leaderboard/scores/global",
                            params={"leaderboardId": leaderboard_id, "page": 0, "max": 1},
                            timeout=10.0
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            total = data.get('total', 0)
                            if total > 0:
                                return (leaderboard_id, total)
                    except:
                        pass
                    return None

                tasks.append(get_entries(lid))

            results = await asyncio.gather(*tasks)

            for result in results:
                if result:
                    lid, entries = result
                    scenarios_by_id[lid] = {'entries': entries, 'name': None}

            if i % 1000 == 1:
                print(f"   Scanned IDs {i}-{batch_end-1}... ({len(scenarios_by_id)} scénarios trouvés)")

            await asyncio.sleep(0.1)

    print(f"\n✅ {len(scenarios_by_id)} scénarios trouvés avec entries > 0\n")

    # Étape 2: Récupérer les noms via le proxy (recherches exhaustives)
    print("📝 Étape 2: Récupération des noms via recherches...")

    search_terms = list("abcdefghijklmnopqrstuvwxyz0123456789") + \
                   ["VT", "aim", "tracking", "click", "switch", "wall", "target"]

    async with httpx.AsyncClient() as client:
        for term in search_terms:
            try:
                resp = await client.get(
                    f"{KOVAAKS_PROXY}/api/search/scenarios",
                    params={"name": term, "max": 100},
                    timeout=30.0
                )

                if resp.status_code == 200:
                    data = resp.json()
                    scenarios_data = data['data']['data']

                    for scenario in scenarios_data:
                        lid = scenario['leaderboardId']
                        if lid in scenarios_by_id:
                            scenarios_by_id[lid]['name'] = scenario['scenarioName']
                            scenarios_by_id[lid]['aim_type'] = scenario['scenario'].get('aimType')

                await asyncio.sleep(0.2)

            except Exception as e:
                print(f"   Erreur pour '{term}': {e}")

    # Compter combien ont un nom
    with_name = sum(1 for s in scenarios_by_id.values() if s['name'])
    print(f"\n✅ {with_name}/{len(scenarios_by_id)} scénarios avec un nom\n")

    # Étape 3: Générer les playlists
    print("🎯 Étape 3: Génération des playlists...")

    # Filtrer seulement ceux avec un nom
    scenarios_with_name = [
        {
            'name': data['name'],
            'entries': data['entries'],
            'leaderboard_id': lid,
            'category': categorize_scenario(data['name'], data.get('aim_type'))
        }
        for lid, data in scenarios_by_id.items()
        if data['name']
    ]

    # Trier par entries
    scenarios_sorted = sorted(scenarios_with_name, key=lambda x: x['entries'], reverse=True)

    print(f"\n📈 Top 10 scénarios:")
    for i, s in enumerate(scenarios_sorted[:10], 1):
        print(f"   {i}. {s['name']}: {s['entries']:,} entries")

    # Top 50 et 100
    write_playlist_file(
        OUTPUT_DIR / "top_50_most_popular.txt",
        scenarios_sorted[:50],
        "Top 50 scénarios les plus populaires (par nombre de joueurs)"
    )

    write_playlist_file(
        OUTPUT_DIR / "top_100_most_popular.txt",
        scenarios_sorted[:100],
        "Top 100 scénarios les plus populaires (par nombre de joueurs)"
    )

    # Par catégorie
    categorized = defaultdict(list)
    for scenario in scenarios_sorted:
        category = scenario['category']
        categorized[category].append(scenario)

    for category, scenarios in categorized.items():
        if not scenarios:
            continue

        scenarios_top = scenarios[:50]

        if category == 'other':
            filename = "other_scenarios_popular.txt"
            description = "Autres scénarios populaires"
        else:
            category_config = AIM_CATEGORIES.get(category, {})
            filename = f"{category}_popular.txt"
            description = category_config.get('description', category.capitalize())

        write_playlist_file(
            OUTPUT_DIR / filename,
            scenarios_top,
            f"{description} - Scénarios populaires ({len(scenarios_top)} scénarios)"
        )

    print()
    print("=" * 70)
    print("✅ Playlists générées avec succès!")
    print(f"📁 Emplacement: {OUTPUT_DIR}")


if __name__ == '__main__':
    asyncio.run(main())
