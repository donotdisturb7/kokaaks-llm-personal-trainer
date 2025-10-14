# Backend - KovaaK's AI Personal Trainer

Backend FastAPI pour l'assistant IA d'entraînement aim training.

## Stack

- **FastAPI** (Python 3.11+)
- **PostgreSQL** - Base de données
- **Redis** - Cache
- **Alembic** - Migrations
- **Groq/Ollama** - LLM

## Installation

```bash
# Créer l'environnement virtuel
python -m venv env
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

```bash
cp env.example .env
```

Éditer `.env`:
```env
# Base de données
DATABASE_URL=postgresql+asyncpg://kovaaks:kovaaks_pass@localhost:5433/kovaaks_ai
REDIS_URL=redis://localhost:6379/0

# LLM
LLM_PROVIDER=groq  # ou ollama
GROQ_API_KEY=votre_clé_ici

# API
API_DEBUG=true
API_PORT=8000
```

## Démarrage

```bash
# Démarrer les services (PostgreSQL, Redis)
# Via Docker ou local

# Migrations
alembic upgrade head

# Lancer l'API
python run.py
```

API disponible sur http://localhost:8000  
Documentation: http://localhost:8000/docs

## Structure

```
app/
├── api/              # Endpoints REST
│   ├── chat.py      # Chat avec IA
│   ├── stats.py     # Stats KovaaK's
│   ├── exercises.py # Exercices
│   └── llm_context.py
├── models/          # Modèles SQLAlchemy
├── services/        # Services
│   ├── llm_service.py
│   ├── cache_service.py
│   └── kovaaks_service.py
└── database.py      # Configuration DB
```

## Endpoints

- `POST /api/chat/message` - Chat avec l'IA
- `POST /api/stats/upload` - Upload CSV stats
- `GET /api/stats/history` - Historique stats
- `GET /api/exercises` - Liste exercices
- `GET /api/kovaaks/profile/:username` - Profil KovaaK's
- `GET /health` - Santé de l'API

## Migrations

```bash
# Créer une migration
alembic revision -m "description"

# Appliquer
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Docker

Le backend est automatiquement lancé via `docker-compose up`.
