

## Configuration

### Variables d'environnement (.env)

```bash
# Backend API
API_PORT=8002

# Frontend (dans docker-compose.yml ou .env local)
FRONTEND_HOST_PORT=3001

# Database
POSTGRES_HOST_PORT=5435
DATABASE_URL=postgresql+asyncpg://kovaaks:kovaaks_pass@localhost:5435/kovaaks_ai

# Redis
REDIS_HOST_PORT=6381
REDIS_URL=redis://localhost:6381/0

# KovaaK's Proxy
KOVAAKS_PROXY_PORT=9001
KOVAAKS_PROXY_URL=http://localhost:9001

# CORS (Frontend URLs)
CORS_ORIGINS=["http://localhost:3001", "http://127.0.0.1:3001"]
```




---

##  Accès depuis les Containers Docker

Les services communiquent entre eux via le réseau Docker interne avec les noms de services :

```yaml
# Depuis le backend vers postgres
DATABASE_URL=postgresql+asyncpg://kovaaks:kovaaks_pass@postgres:5432/kovaaks_ai

# Depuis le backend vers redis
REDIS_URL=redis://redis:6379/0

# Depuis le backend vers proxy
KOVAAKS_PROXY_URL=http://kovaaks-proxy:9000
```


## Mapping des Ports

```
Host Machine          Docker Network
--------------        ---------------
localhost:3001   →    frontend:3000
localhost:8002   →    backend:8000
localhost:5435   →    postgres:5432
localhost:6381   →    redis:6379
localhost:9001   →    kovaaks-proxy:9000
```

---

## Démarrage

```bash
# 1. Copier le fichier d'exemple
cp .env.example .env

# 2. (Optionnel) Modifier les ports dans .env

# 3. Démarrer les services
docker-compose up -d

# 4. Vérifier que tout fonctionne
curl http://localhost:8002/health
curl http://localhost:3001
```

---

