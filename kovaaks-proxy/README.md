# KovaaK's API Proxy

Proxy Node.js qui utilise le wrapper officiel `kovaaks-api-client` pour communiquer avec l'API KovaaK's.

## Pourquoi ce proxy?

Le wrapper officiel est en TypeScript. Ce service expose une API REST simple que le backend Python peut appeler.

## Installation

```bash
npm install
```

## Démarrage

```bash
# Dev
npm run dev

# Production
npm run build
npm start
```

## Endpoints

Tous retournent `{success: true/false, data: {...}}`:

- `GET /health` - Santé du service
- `GET /api/profile/:username` - Profil utilisateur
- `GET /api/scenarios/:username` - Scénarios joués
- `GET /api/highscores/:username` - High scores récents
- `GET /api/benchmarks/:username` - Benchmarks
- `GET /api/favorites/:username` - Favoris
- `GET /api/leaderboard/global` - Leaderboard global

## Configuration

- `PORT` - Port du serveur (défaut: 9000)

## Docker

Le service est automatiquement lancé via `docker-compose up`.

