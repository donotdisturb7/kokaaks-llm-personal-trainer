# 📊 État du Projet - KovaaK's AI Personal Trainer

**Date**: 15 Octobre 2025
**Version**: 0.2.0

## 🎯 Objectif du Projet

Assistant IA pour l'entraînement de visée (aim training) avec KovaaK's. Chat IA, ingestion de PDFs (RAG), stats et recommandations.

---

## ✅ Ce qui est FAIT

### Frontend (Next.js + TypeScript)
- ✅ Interface de chat avec IA
- ✅ Navigation par onglets (Chat, Artifacts, PDF Uploader, Stats, Settings)
- ✅ Composants UI réutilisables (shadcn/ui + Radix)
- ✅ Intégration API (`/api/...`), gestion des erreurs/chargements
- ✅ Onglet PDF Uploader: upload + liste/suppression des documents

### Backend (FastAPI + Python)
- ✅ API REST modulaire (chat, rag, stats, kovaaks)
- ✅ CORS configuré pour `http://localhost:3001`
- ✅ RAG: ingestion PDF, chunking, embeddings, stockage Postgres
- ✅ Service embeddings (FastEmbed) + pgvector
- ✅ Sessions SQLAlchemy async et corrections AsyncSession

### Migrations & Données
- ✅ Alembic opérationnel (env URL via `ALEMBIC_DATABASE_URL`)
- ✅ Migration initiale corrigée (suppression index GIN JSON invalide)
- ✅ Migration RAG corrigée (`Vector(384)` + index ivfflat cosine)
- ✅ Script `startup.sh` automatise: attente Postgres, `CREATE EXTENSION vector`, migrations (stamp auto si tables déjà présentes)

### Infra Docker
- ✅ Docker Compose (backend, frontend, postgres+pgvector, redis, proxy)
- ✅ Ports sans conflit: backend 8002, frontend 3001, postgres 5435, redis 6381, proxy 9001
- ✅ Frontend bind-mount + hot reload (polling) en dev

---

## 🚧 En Cours / À Faire

### 🔴 Priorité Haute
- ⏳ Settings tab: sélection provider LLM, username
- ⏳ Stats tab: upload CSV + historique

### 🟡 Priorité Moyenne
- ⏳ RAG: UI d’aperçu document + recherche
- ⏳ Normalisation réponses LLM (formatage)

### 🟢 Nice to Have
- ⏳ Recos personnalisées à partir des stats
- ⏳ Export/partage de programmes

---

## 📁 Structure du Projet

```
kokaaks-llm-personal-trainer/
├── backend/ (FastAPI, Alembic, services)
├── frontend/ (Next.js, components, contexts, lib)
├── kovaaks-proxy/ (Node proxy)
├── docker-compose.yml
└── test/
```

---

## 🔧 Stack Technique

### Frontend
- **Framework**: Next.js
- **Language**: TypeScript
- **Styling**: Tailwind + shadcn/ui
- **State**: React Context

### Backend
- **Framework**: FastAPI (Python 3.11)
- **DB**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2 (async)
- **Cache**: Redis
- **Migrations**: Alembic

### LLM/AI
- **Providers**: Groq (cloud) / Ollama (local)
- **Embeddings**: FastEmbed

### DevOps
- **Docker/Compose**, **Node proxy**, **startup.sh** (DB + migrations)

---

## 📊 Statistiques

- **Fichiers**: 1 018
- **Lignes de code**: 610 758
- **Commits**: 9
- **Tests**: N/A

---

## 🚀 Prochaines Étapes

1. Settings tab
   - Provider LLM + username
   - Persistance côté backend

2. Stats tab
   - Upload CSV
   - Historique et affichage

3. RAG UX
   - Recherche/similarity côté front
   - UI d’aperçu document

---

## 💡 Notes Importantes

- 🔒 Pas de clés API committées (utiliser env vars). `GROQ_API_KEY` requis si Groq.
- ⚠️ Les migrations sont désormais idempotentes via `startup.sh`.
- 🧩 AsyncSession corrigé (plus d'appels `.query` sync).

---

## 📝 Changelog

### v0.2.0 - 15 Octobre 2025
- Update Docker Compose (ports, mounts, CORS)
- Fix Alembic (GIN JSON retiré, URL via env)
- RAG: `Vector(384)` + index ivfflat cosine
- Backend startup.sh: pgvector + migrations auto
- Frontend: PDF Uploader tab + liste/suppression

### v0.1.0 - 15 Janvier 2025
- UI chat + navigation tabs
- Intégration API backend

---

**Auteur**: DND
**Contexte**: Projet académique (BUT)
**Repository**: kokaaks-llm-personal-trainer