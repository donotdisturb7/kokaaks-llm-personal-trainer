# Scripts - KovaaK's LLM Personal Trainer

Ce dossier contient des scripts utilitaires pour le projet.

## generate_popular_playlists.py ⭐ (RECOMMANDÉ)

Script Python pour générer automatiquement des playlists KovaaK's basées sur les **scénarios les plus populaires globalement** (ceux avec le plus d'entries/joueurs dans les leaderboards).

### Fonctionnalités

1. **Playlist Top 50** : Les 50 scénarios les plus populaires globalement
2. **Playlist Top 100** : Les 100 scénarios les plus populaires globalement
3. **Playlists par catégorie** : Scénarios populaires organisés par type d'aim

### Utilisation

```bash
# Depuis le dossier scripts/
cd scripts
python3 generate_popular_playlists.py

# Ou depuis la racine du projet
cd kokaaks-llm-personal-trainer
python3 scripts/generate_popular_playlists.py
```

### Prérequis

- Le proxy KovaaK's doit être actif (port 9001)
- Connexion Internet pour accéder à l'API KovaaK's

### Sortie

Les playlists sont générées dans le dossier `playlists/` :

```
playlists/
├── top_50_most_popular.txt       # Top 50 scénarios populaires
├── top_100_most_popular.txt      # Top 100 scénarios populaires
├── tracking_popular.txt           # Scénarios de tracking populaires
├── clicking_popular.txt           # Scénarios de clicking populaires
├── switching_popular.txt          # Scénarios de target switching populaires
├── speed_popular.txt              # Scénarios de vitesse populaires
├── precision_popular.txt          # Scénarios de précision populaires
├── evasive_popular.txt            # Scénarios d'esquive populaires
├── dynamic_popular.txt            # Scénarios dynamiques populaires
└── other_scenarios_popular.txt    # Autres scénarios populaires
```

### Format des playlists

Chaque playlist contient des statistiques détaillées :

```
# Top 50 scénarios les plus populaires (par nombre de joueurs)
# Généré le 2025-11-05 14:38:34
# Nombre de scénarios: 50
# Total entries: 913,412
# Moyenne entries: 18,268

VT 1w2ts Horizontal Small  # 23,007 players
VT 1w2ts Advanced S5  # 22,736 players
VT Snake Track Advanced S5  # 22,037 players
...
```

### Exemple d'exécution

```
🎯 Génération des playlists KovaaK's (par popularité)

======================================================================

🔍 Recherche des scénarios populaires...

✓ Connexion au proxy KovaaK's établie

  'VT': 100 scénarios trouvés
  'Air': 100 scénarios trouvés
  ...

📊 Total de scénarios uniques trouvés: 2100

📈 Statistiques:
   - Total scénarios: 2100
   - Total entries: 5,596,361
   - Moyenne entries/scénario: 2,664

📝 Génération de la playlist 'Top 50 Most Popular'...
✓ Playlist créée: top_50_most_popular.txt (50 scénarios)
   Top 3:
      1. VT 1w2ts Horizontal Small (23,007 joueurs)
      2. VT 1w2ts Advanced S5 (22,736 joueurs)
      3. VT Snake Track Advanced S5 (22,037 joueurs)

📝 Génération de la playlist 'Top 100 Most Popular'...
✓ Playlist créée: top_100_most_popular.txt (100 scénarios)

📝 Génération des playlists par catégorie d'aim...
✓ Playlist créée: clicking_popular.txt (50 scénarios)
✓ Playlist créée: tracking_popular.txt (50 scénarios)
...

======================================================================
✅ Toutes les playlists ont été générées avec succès!
📁 Emplacement: /path/to/playlists
```

---

## generate_playlists.py

Script Python pour générer automatiquement des playlists KovaaK's basées sur **vos statistiques locales personnelles**.

### Fonctionnalités

1. **Playlist Top 50** : Génère une playlist des 50 scénarios les plus joués
2. **Playlists par catégorie** : Génère des playlists organisées par type d'aim :
   - **Tracking** : Suivi de cibles en mouvement (air, smooth tracking, etc.)
   - **Clicking** : Précision sur cibles statiques/rapides (flicking, tile frenzy, etc.)
   - **Switching** : Changement rapide entre cibles (target switching, multiclick, etc.)
   - **Speed** : Vitesse et réactivité (speed training, fast scenarios)
   - **Precision** : Précision pure (microshot, static dots, etc.)
   - **Evasive** : Mouvement et esquive (evasive scenarios)
   - **Dynamic** : Scénarios dynamiques mixtes

### Prérequis

1. Avoir uploadé vos statistiques KovaaK's via l'API :
   ```bash
   # Via l'interface web sur http://localhost:3001
   # Ou via l'API directement
   curl -X POST http://localhost:8002/api/stats/upload \
     -F "file=@votre_fichier_stats.csv"
   ```

2. La base de données PostgreSQL doit être accessible

### Utilisation

```bash
# Depuis le dossier scripts/
cd scripts
../backend/env/bin/python generate_playlists.py

# Ou depuis la racine du projet
cd kokaaks-llm-personal-trainer
backend/env/bin/python scripts/generate_playlists.py
```

### Configuration

Le script utilise automatiquement le fichier `.env` du backend pour se connecter à la base de données. Assurez-vous que `DATABASE_URL` est correctement configuré :

```bash
DATABASE_URL=postgresql+asyncpg://kovaaks:kovaaks_pass@localhost:5435/kovaaks_ai
```

### Sortie

Les playlists sont générées dans le dossier `playlists/` à la racine du projet :

```
playlists/
├── top_50_most_played.txt      # Top 50 scénarios les plus joués
├── tracking.txt                 # Scénarios de tracking
├── clicking.txt                 # Scénarios de clicking/flicking
├── switching.txt                # Scénarios de target switching
├── speed.txt                    # Scénarios de vitesse
├── precision.txt                # Scénarios de précision
├── evasive.txt                  # Scénarios d'esquive
├── dynamic.txt                  # Scénarios dynamiques
└── other_scenarios.txt          # Autres scénarios non catégorisés
```

### Format des playlists

Les playlists sont au format texte simple, un scénario par ligne :

```
# Top 50 scénarios les plus joués
# Généré le 2025-11-05 14:30:00
# Nombre de scénarios: 50

1w6ts reload
Thin Astr Long Invincible
Air Angelic 4
...
```

### Utilisation dans KovaaK's

1. Copiez le fichier de playlist dans votre dossier KovaaK's :
   ```
   C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Playlists\
   ```

2. Redémarrez KovaaK's ou rechargez les playlists

3. La playlist apparaîtra dans le menu Playlists de KovaaK's

### Catégorisation

Le script catégorise automatiquement les scénarios basé sur leurs noms. Les mots-clés utilisés :

- **Tracking** : track, tracking, air, smooth, follow, air angelic, thin astr, voltaic
- **Clicking** : click, flick, pasu, 1w, tile, frenzy, reflex, pokeball
- **Switching** : switch, target switch, multiclick, jumbo, 6 sphere
- **Speed** : speed, fast, thin, kinetic, reactive
- **Precision** : precision, static, precise, microshot, small
- **Evasive** : evasive, dodge, strafe
- **Dynamic** : dynamic, close, long strafes, bounce

Si un scénario ne correspond à aucune catégorie, il sera placé dans `other_scenarios.txt`.

### Exemple de sortie

```
🎯 Génération des playlists KovaaK's

============================================================
📊 Statistiques de la base de données:
   - Scénarios uniques: 127
   - Parties jouées: 3842

📝 Génération de la playlist 'Top 50 Most Played'...
✓ Playlist créée: top_50_most_played.txt (50 scénarios)
   Top 3: 1w6ts reload (342 parties)
          Thin Astr Long Invincible (298 parties)
          Air Angelic 4 (276 parties)

📝 Génération des playlists par catégorie d'aim...
✓ Playlist créée: tracking.txt (23 scénarios)
✓ Playlist créée: clicking.txt (31 scénarios)
✓ Playlist créée: switching.txt (18 scénarios)
✓ Playlist créée: speed.txt (15 scénarios)
✓ Playlist créée: precision.txt (12 scénarios)
✓ Playlist créée: dynamic.txt (9 scénarios)
✓ Playlist créée: other_scenarios.txt (19 scénarios)

============================================================
✅ Toutes les playlists ont été générées avec succès!
📁 Emplacement: /path/to/playlists
```

### Dépannage

**Erreur: DATABASE_URL non défini**
- Vérifiez que le fichier `.env` existe dans le dossier `backend/`
- Assurez-vous que `DATABASE_URL` est correctement configuré

**Erreur de connexion à la base de données**
- Vérifiez que PostgreSQL est démarré : `docker ps | grep postgres`
- Vérifiez le port dans `.env` (devrait être 5435 en local, ou selon votre docker-compose)

**Aucun scénario trouvé**
- Uploadez d'abord vos statistiques via l'API `/api/stats/upload`
- Vérifiez que l'upload a réussi dans les logs du backend

### Personnalisation

Pour ajouter ou modifier les catégories, éditez la constante `AIM_CATEGORIES` dans le script :

```python
AIM_CATEGORIES = {
    'ma_categorie': {
        'keywords': ['mot1', 'mot2', 'mot3'],
        'description': 'Description de ma catégorie'
    },
    # ...
}
```
