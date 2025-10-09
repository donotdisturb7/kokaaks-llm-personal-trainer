# Tests KovaaK's API

Ce dossier contient les tests et expérimentations avec l'API KovaaK's en TypeScript.

## Structure

- `api-test/` - Tests de l'API KovaaK's
- `data-samples/` - Données d'exemple pour les tests
- `scripts/` - Scripts de test et d'expérimentation

## Installation

```bash
npm install
```

## Configuration

Copiez `env.example` vers `.env` et configurez les chemins:

```bash
cp env.example .env
```

## Scripts disponibles

- `npm run test:api` - Test de l'API KovaaK's
- `npm run test:ai` - Test d'analyse IA
- `npm run build` - Compilation TypeScript
- `npm run dev` - Mode développement

## Objectifs des tests

1. **Connexion à l'API** - Vérifier que l'API fonctionne
2. **Récupération des stats** - Tester la récupération des données
3. **Parsing des données** - Analyser la structure des données
4. **Intégration IA** - Tester l'analyse des données par l'IA

## Utilisation

```bash
# Test de l'API
npm run test:api

# Test d'analyse IA
npm run test:ai
```

## Dépendances

- `kovaaks-api-client` - Client API KovaaK's
- `typescript` - Compilateur TypeScript
- `ts-node` - Exécution TypeScript directe
- `@types/node` - Types Node.js
