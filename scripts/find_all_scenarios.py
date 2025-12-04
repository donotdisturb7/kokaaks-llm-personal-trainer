#!/usr/bin/env python3
"""
Script pour découvrir tous les scénarios KovaaK's en itérant sur les leaderboardIds
et récupérer le nombre d'entries pour chacun.
"""

import asyncio
import httpx
from typing import Dict, List
import json
from pathlib import Path

KOVAAKS_BACKEND_URL = "https://kovaaks.com/webapp-backend"

async def get_scenario_entries(client: httpx.AsyncClient, leaderboard_id: int) -> Dict:
    """Récupère le nombre d'entries pour un leaderboardId."""
    try:
        response = await client.get(
            f"{KOVAAKS_BACKEND_URL}/leaderboard/scores/global",
            params={"leaderboardId": leaderboard_id, "page": 0, "max": 1},
            timeout=10.0
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)

            # Essayer de trouver le nom du scénario dans les données
            scenario_data = data.get('data', [])
            scenario_name = None

            if total > 0:
                return {
                    'leaderboard_id': leaderboard_id,
                    'entries': total,
                    'status': 'success'
                }
            else:
                return {'leaderboard_id': leaderboard_id, 'entries': 0, 'status': 'empty'}
        else:
            return {'leaderboard_id': leaderboard_id, 'entries': 0, 'status': 'error'}

    except Exception as e:
        return {'leaderboard_id': leaderboard_id, 'entries': 0, 'status': 'error', 'error': str(e)}


async def scan_leaderboard_ids(start_id: int, end_id: int, batch_size: int = 50):
    """Scanne une plage de leaderboardIds."""
    print(f"🔍 Scanning leaderboardIds from {start_id} to {end_id}...")

    scenarios_found = []

    async with httpx.AsyncClient() as client:
        for i in range(start_id, end_id + 1, batch_size):
            batch_end = min(i + batch_size, end_id + 1)
            print(f"   Scanning IDs {i}-{batch_end-1}...")

            # Créer les tâches pour ce batch
            tasks = [get_scenario_entries(client, lid) for lid in range(i, batch_end)]
            results = await asyncio.gather(*tasks)

            # Collecter les scénarios trouvés
            for result in results:
                if result['status'] == 'success' and result['entries'] > 0:
                    scenarios_found.append(result)
                    print(f"      ✓ ID {result['leaderboard_id']}: {result['entries']:,} entries")

            # Petit délai pour ne pas surcharger l'API
            await asyncio.sleep(0.2)

    return scenarios_found


async def main():
    print("🎯 Découverte des scénarios KovaaK's via l'API backend\n")
    print("=" * 70)
    print()

    # Tester quelques IDs d'abord pour comprendre la plage
    print("🧪 Test de quelques IDs pour comprendre la plage...")
    test_ids = [1, 100, 1000, 2803, 5000, 10000, 20000, 50000, 100000]

    async with httpx.AsyncClient() as client:
        for test_id in test_ids:
            result = await get_scenario_entries(client, test_id)
            if result['entries'] > 0:
                print(f"   ✓ ID {test_id}: {result['entries']:,} entries")
            await asyncio.sleep(0.3)

    print()
    print("📊 Les IDs semblent être dans une certaine plage.")
    print("   Je vais scanner une plage raisonnable (1-120000) par batches.")
    print()

    # Scanner une plage raisonnable
    # La plupart des scénarios semblent avoir des IDs < 120000
    scenarios = await scan_leaderboard_ids(1, 120000, batch_size=100)

    print()
    print("=" * 70)
    print(f"✅ Scan terminé ! {len(scenarios)} scénarios trouvés avec des entries > 0")

    # Trier par nombre d'entries
    scenarios_sorted = sorted(scenarios, key=lambda x: x['entries'], reverse=True)

    print()
    print("📈 Top 20 scénarios par nombre d'entries:")
    for i, scenario in enumerate(scenarios_sorted[:20], 1):
        print(f"   {i}. LeaderboardId {scenario['leaderboard_id']}: {scenario['entries']:,} entries")

    # Sauvegarder les résultats
    output_file = Path(__file__).parent.parent / 'scripts' / 'scenarios_leaderboard_ids.json'
    with open(output_file, 'w') as f:
        json.dump(scenarios_sorted, f, indent=2)

    print()
    print(f"💾 Résultats sauvegardés dans: {output_file}")


if __name__ == '__main__':
    asyncio.run(main())
