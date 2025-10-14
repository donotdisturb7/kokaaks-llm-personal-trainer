# Frontend - KovaaK's AI Personal Trainer

Interface Next.js 14 pour l'assistant IA d'entraînement aim training.

## Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Radix UI** (composants)

## Installation

```bash
npm install
```

## Démarrage

```bash
# Dev
npm run dev

# Build
npm run build
npm start
```

Le frontend sera disponible sur http://localhost:3000

## Structure

```
src/
├── app/              # Pages et layouts
├── components/
│   ├── chat/        # Interface chat
│   ├── exercises/   # Bibliothèque exercices
│   ├── layout/      # Layout components
│   └── ui/          # UI components
└── lib/             # Utilitaires
```

## Features

- Interface de chat avec l'IA
- Système de tabs (Chat, Exercices, Stats, Paramètres)
- Design moderne et responsive
- Composants réutilisables

## Docker

Le frontend est automatiquement lancé via `docker-compose up`.
