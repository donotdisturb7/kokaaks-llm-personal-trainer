# KovaaK's AI Personal Trainer

Assistant IA personnel pour l'entraînement aim training sur KovaaK's FPS Aim Trainer.

## Stack Technique

### Frontend
- Next.js 14 + TypeScript + Tailwind CSS
- Interface de chat avec l'IA
- Système de tabs (Chat, Exercices, Stats)

### Backend
- **FastAPI** (Python) - API REST
- **PostgreSQL** - Base de données
- **Redis** - Cache versionné
- **Alembic** - Migrations DB

### LLM
- **Groq** - LLM cloud ultra-rapide (API)
- **Ollama** - LLM local (optionnel)

### KovaaK's API
- **Proxy Node.js** - Utilise `kovaaks-api-client` (wrapper officiel)
- Récupération profils, stats, leaderboards

## Architecture Docker

```
┌─────────────────────────────────────────────┐
│              kovaaks-network                │
│                                             │
│  Frontend (:3000) ─► Backend (:8000)       │
│                          ↓                  │
│                   KovaaK's Proxy (:9000)   │
│                          ↓                  │
│                   PostgreSQL (:5432)        │
│                          ↓                  │
│                      Redis (:6379)          │
└─────────────────────────────────────────────┘
```

## Démarrage Rapide

### 1. Configuration

```bash
# Copier le fichier d'environnement
cp .env.docker .env

# Éditer .env et ajouter votre clé Groq
GROQ_API_KEY=votre_clé_ici
```

### 2. Lancer avec Docker

```bash
# Méthode 1: Script automatique
./docker-start.sh

# Méthode 2: Make
make up

# Méthode 3: Docker Compose
docker compose up -d
```

### 3. Accéder aux services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **KovaaK's Proxy**: http://localhost:9000

## Commandes Utiles

```bash
# Voir les logs
make logs
docker compose logs -f

# Arrêter
make down
docker compose down

# Migrations DB
make db-migrate
docker compose exec backend alembic upgrade head

# Shell backend
make shell-backend
docker compose exec backend bash

# Nettoyage complet
make clean
```

## Structure du Projet

```
kokaaks-llm-personal-trainer/
├── frontend/           # Next.js app
├── backend/            # FastAPI app
│   ├── app/
│   │   ├── api/       # Endpoints REST
│   │   ├── models/    # Modèles SQLAlchemy
│   │   └── services/  # Services (LLM, Cache, KovaaK's)
│   └── alembic/       # Migrations DB
├── kovaaks-proxy/     # Proxy Node.js pour API KovaaK's
├── test/              # Tests et scripts
└── docker-compose.yml # Configuration Docker
```

## Fonctionnalités

- ✅ Chat avec IA spécialisée aim training
- ✅ Intégration API KovaaK's (profils, stats, leaderboards)
- ✅ Cache Redis versionné
- ✅ Base de données PostgreSQL
- ✅ Système modulaire et scalable
- 🔄 Analyse stats CSV uploadés
- 🔄 Recommandations personnalisées
- 🔄 Fine-tuning du modèle

## Développement

### Backend Python

```bash
cd backend
source env/bin/activate
python run.py
```

### Frontend Next.js

```bash
cd frontend
npm install
npm run dev
```

### Proxy KovaaK's

```bash
cd kovaaks-proxy
npm install
npm run dev
```

## License

MIT
