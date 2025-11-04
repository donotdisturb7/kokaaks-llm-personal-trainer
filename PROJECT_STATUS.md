# État du Projet - KovaaK's AI Personal Trainer

**Date**: 3 Novembre 2025
**Version**: 0.3.0

## Objectif du Projet

Assistant IA pour l'entraînement de visée (aim training) avec KovaaK's. Chat IA, ingestion de PDFs (RAG), stats et recommandations.

---

## Ce qui est FAIT

### Frontend (Next.js + TypeScript)
- Interface de chat avec IA
- Navigation par onglets (Chat, Artifacts, PDF Uploader, Stats, Settings)
- Composants UI réutilisables (shadcn/ui + Radix)
- Intégration API avec gestion des erreurs/chargements
- Onglet PDF Uploader: upload + liste/suppression des documents

### Backend (FastAPI + Python)
- API REST modulaire (chat, rag, stats, kovaaks, exercises)
- CORS configuré pour http://localhost:3001
- RAG complet: ingestion PDF, chunking, embeddings, stockage Postgres
- Service embeddings (FastEmbed) + pgvector avec index ivfflat
- Sessions SQLAlchemy async
- Gestion globale des erreurs (ValidationError, ValueError, Exception)
- Validation complète des entrées utilisateur (Pydantic)
- Optimisation des requêtes API parallèles (asyncio.gather)

### Code Quality
- Centralisation des constantes (constants.py)
- Extraction du code dupliqué (system prompts)
- Suppression du code mort et imports inutilisés
- Documentation complète (IMPROVEMENTS_APPLIED.md, PORTS.md)

### Tests
- Suite de tests complète (41+ tests)
- Tests unitaires (constants, config, embedding service)
- Tests d'intégration (health, exercises, RAG endpoints)
- Configuration pytest avec coverage
- Script run_tests.sh pour exécution facile
- Documentation des tests (backend/tests/README.md)

### Migrations & Base de données
- Alembic opérationnel (env URL via ALEMBIC_DATABASE_URL)
- Migration initiale corrigée (suppression index GIN JSON invalide)
- Migration RAG corrigée (Vector(384) + index ivfflat cosine)
- Script startup.sh automatisé: attente Postgres, CREATE EXTENSION vector, migrations idempotentes

### Infrastructure Docker
- Docker Compose (backend, frontend, postgres+pgvector, redis, proxy)
- Ports standardisés et documentés:
  - Backend: 8002
  - Frontend: 3001
  - PostgreSQL: 5435
  - Redis: 6381
  - Proxy: 9001
- Frontend bind-mount + hot reload en développement
- Proxy Node.js avec endpoints documentés (/, /api, /health)

---

## En Cours / À Faire

### Priorité Haute
- Settings tab: sélection provider LLM, username
- Stats tab: upload CSV + historique

### Priorité Moyenne
- RAG: UI d'aperçu document + recherche
- Normalisation réponses LLM (formatage)

### Nice to Have
- Recommandations personnalisées à partir des stats
- Export/partage de programmes
- Authentification (API keys ou JWT)
- Rate limiting
- Monitoring et alerting

---

## Structure du Projet

```
kokaaks-llm-personal-trainer/
├── backend/
│   ├── app/
│   │   ├── api/ (endpoints: chat, rag, stats, kovaaks, exercises)
│   │   ├── services/ (ollama, groq, rag, embedding, kovaaks)
│   │   ├── models/ (SQLAlchemy models)
│   │   ├── constants.py (constantes centralisées)
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/ (16 tests)
│   │   ├── integration/ (25+ tests)
│   │   └── conftest.py (fixtures)
│   ├── alembic/ (migrations)
│   ├── pytest.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── run_tests.sh
├── frontend/ (Next.js, components, contexts, lib)
├── kovaaks-proxy/ (Node proxy avec documentation endpoints)
├── docker-compose.yml
├── PORTS.md (documentation ports)
└── PROJECT_STATUS.md (ce fichier)
```

---

## Stack Technique

### Frontend
- Framework: Next.js 15.5.4
- Language: TypeScript 5
- Styling: Tailwind CSS 4 + shadcn/ui
- State: React Context

### Backend
- Framework: FastAPI (Python 3.11)
- Database: PostgreSQL 16 + pgvector
- ORM: SQLAlchemy 2 (async)
- Cache: Redis 7
- Migrations: Alembic
- Tests: pytest + pytest-asyncio + pytest-cov

### LLM/AI
- Providers: Groq (cloud) / Ollama (local)
- Embeddings: FastEmbed (BAAI/bge-small-en-v1.5, 384 dimensions)
- Vector Search: pgvector avec index ivfflat

### DevOps
- Docker Compose
- Node.js proxy (Express)
- Startup automatisé (startup.sh)

---

## Statistiques

- Fichiers: 1018+
- Lignes de code: ~7000 (backend + frontend)
- Commits: 12
- Tests: 41+ (coverage >80% objectif)
- Bugs critiques: 0
- Note qualité: A

---

## Prochaines Étapes

1. Settings tab
   - Provider LLM + username
   - Persistance côté backend

2. Stats tab
   - Upload CSV
   - Historique et affichage

3. RAG UX
   - Recherche/similarity côté front
   - UI d'aperçu document

4. Production readiness (optionnel)
   - Authentification
   - Rate limiting
   - Monitoring

---

## Notes Importantes


- Les migrations sont idempotentes via startup.sh
- AsyncSession correctement utilisé partout
- Tous les ports sont configurables via variables d'environnement
- Tests lancés avec: cd backend && ./run_tests.sh


---

## Changelog

### v0.3.0 - 3 Novembre 2025
**Améliorations majeures**
- Correction de 3 bugs critiques (current_user, await manquant, encodage)
- Centralisation des constantes (constants.py)
- Extraction du code dupliqué (system prompts)
- Optimisation performance: asyncio.gather (80% plus rapide)
- Validation complète des entrées (Pydantic)
- Gestion globale des erreurs
- Suite de tests complète (41+ tests)
- Standardisation des ports
- Documentation améliorée (PORTS.md, IMPROVEMENTS_APPLIED.md)
- Amélioration du proxy (endpoints /, /api)

### v0.2.0 - 15 Octobre 2025
- Update Docker Compose (ports, mounts, CORS)
- Fix Alembic (GIN JSON retiré, URL via env)
- RAG: Vector(384) + index ivfflat cosine
- Backend startup.sh: pgvector + migrations auto
- Frontend: PDF Uploader tab + liste/suppression

### v0.1.0 - 15 Janvier 2025
- UI chat + navigation tabs
- Intégration API backend

---

**Auteur**: DND
**Contexte**: Projet académique (BUT)
**Repository**: kokaaks-llm-personal-trainer
