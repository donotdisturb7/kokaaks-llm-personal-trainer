# Architecture de la Base de Données

## Vue d'ensemble

Ce projet utilise deux systèmes de stockage distincts pour des besoins différents :
- **PostgreSQL** : Stockage persistant des données personnelles
- **Redis** : Cache temporaire pour les appels API externes

## PostgreSQL - Stockage Persistant

### 1. Système RAG (Retrieval Augmented Generation)

**Tables** : `rag_documents`, `rag_document_chunks`

Le système RAG permet d'ingérer des documents PDF et de les rendre interrogeables via recherche vectorielle. Chaque document est découpé en chunks, transformé en embeddings (vecteurs 384D via FastEmbed), et stocké avec un index pgvector ivfflat pour la recherche par similarité.

**Workflow** :
```
Upload PDF → Découpage en chunks → Génération embeddings → Stockage PostgreSQL
                                                          ↓
Question utilisateur → Embedding query → Recherche similarité → Contexte pour LLM
```

**Cas d'usage** :
- Guides d'entraînement personnalisés
- Documentation technique
- Conseils médicaux / posture
- Ressources d'apprentissage

### 2. Historique des Conversations

**Table** : `conversations`

Stockage de l'historique complet des interactions avec l'IA. Chaque conversation contient les messages (format JSONB), le contexte utilisé, et les métadonnées temporelles.

**Structure** :
```json
{
  "id": 123,
  "title": "Session d'entraînement tracking",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "context_used": {...},
  "created_at": "2025-11-03T10:30:00",
  "updated_at": "2025-11-03T11:45:00"
}
```

**Utilité** :
- Persistance entre sessions
- Analyse des interactions
- Contexte conversationnel
- Export des données

### 3. Statistiques Locales

**Table** : `local_stats`

Stockage des statistiques détaillées uploadées via CSV. Contrairement à l'API KovaaK's qui fournit des données récentes et publiques, cette table permet de stocker et analyser l'historique complet des performances.

**Colonnes principales** :
- scenario_name
- score, accuracy, kills
- avg_ttk (average time to kill)
- sensitivity, fov, cm360 (config matérielle)
- played_at, created_at

**Différence avec API KovaaK's** :
- API : Données récentes, limitées, publiques
- Base locale : Historique complet, analyse long terme, données personnelles

### 4. Fine-tuning (Prévu)

**Tables** : `training_examples`, `datasets`, `dataset_examples`

Système de curation pour entraîner un modèle LLM personnalisé. Permet de collecter des paires question/réponse de qualité pour le fine-tuning.

**Status** : Non implémenté (v0.4+)

## Redis - Cache Temporaire

**Utilisation** : Cache des appels à l'API KovaaK's externe

**Données cachées** :
- Profils joueurs (TTL: 1h)
- Scénarios joués (TTL: 30min)
- Highscores récents (TTL: 15min)
- Benchmarks (TTL: 1h)
- Leaderboards (TTL: 5min)

**Objectif** : Réduire la charge sur l'API KovaaK's et améliorer les temps de réponse.

## Schéma des Données

```
┌─────────────────────────────────────────────────────────┐
│                    PostgreSQL                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  RAG System                                             │
│  ├── rag_documents                                      │
│  └── rag_document_chunks (avec embeddings pgvector)    │
│                                                         │
│  Chat                                                   │
│  └── conversations                                      │
│                                                         │
│  Stats Personnelles                                     │
│  └── local_stats                                        │
│                                                         │
│  Fine-tuning (futur)                                    │
│  ├── training_examples                                  │
│  ├── datasets                                           │
│  └── dataset_examples                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                       Redis                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Cache API KovaaK's                                     │
│  ├── profile:{username} (TTL: 1h)                       │
│  ├── scenarios:{username} (TTL: 30min)                  │
│  ├── highscores:{username} (TTL: 15min)                 │
│  └── leaderboard:global (TTL: 5min)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Flux de Données

### Données Externes (API KovaaK's)
```
Request → Vérif Redis → [HIT] Return cached data
                      ↓ [MISS]
                      Appel API KovaaK's → Cache Redis → Return data
```

### Données Internes (PostgreSQL)
```
Upload PDF → Processing → PostgreSQL (RAG)
Chat message → Generate response → PostgreSQL (conversations)
CSV stats → Parse → PostgreSQL (local_stats)
```

## Justification des Choix

### PostgreSQL pour RAG
- pgvector pour recherche vectorielle native
- Index ivfflat optimisé pour 384 dimensions
- ACID compliance pour intégrité des données
- Support JSONB pour métadonnées flexibles

### Redis pour Cache API
- Performances excellentes (in-memory)
- TTL natif pour expiration automatique
- Simplicité pour cas d'usage cache

### Séparation des Responsabilités
- PostgreSQL : Données propres au projet, persistantes
- Redis : Données externes, temporaires, volatiles
- Pas de duplication : chaque donnée a une source unique

## Migrations Alembic

Les migrations sont gérées via Alembic avec un système idempotent :

1. `fe222be65e91_initial_schema.py` : Schéma initial (obsolète)
2. `c433b61fb4de_reset_schema_to_new_structure.py` : Refonte architecture
3. `0a2f121dc56d_add_rag_tables_and_vector_extension.py` : Ajout système RAG

Le script `startup.sh` garantit :
- Création extension pgvector
- Exécution migrations si nécessaire
- Idempotence (pas d'erreur si déjà appliqué)

## Évolution Prévue

### v0.4
- Implémentation système fine-tuning
- Collection training examples depuis conversations
- Export datasets pour entraînement modèle

### v0.5
- Optimisation index pgvector (test HNSW vs ivfflat)
- Ajout métriques performance recherche
- Dashboard analytics PostgreSQL

## Notes Techniques

- Vector dimension: 384 (FastEmbed BAAI/bge-small-en-v1.5)
- Index type: ivfflat avec 100 lists
- Distance metric: cosine similarity
- Chunk size: 500 caractères (overlap: 50)
- PostgreSQL version: 16 avec pgvector
- Redis version: 7
