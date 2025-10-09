# Aim Training AI

An AI-powered aim training assistant that provides personalized coaching, exercise recommendations, and progress tracking.

## Features

- **AI Chatbot**: Fine-tuned LLM for aim training expertise
- **Exercise Library**: Curated collection of aim training exercises
- **Stats Integration**: KovaaK's API integration for progress tracking
- **Personalized Training**: AI-driven recommendations based on your performance

## Tech Stack

### Frontend
- Next.js 14 with App Router
- TypeScript
- Tailwind CSS
- Radix UI components

### Backend (Planned)
- FastAPI
- PostgreSQL
- Ollama (Local LLM)
- Hugging Face Transformers

### Data Sources
- KovaaK's API
- Aim training documentation
- User statistics and progress

## Project Structure

```
finetune-project/
├── frontend/                 # Next.js application
├── backend/                  # FastAPI application (planned)
├── ml/                      # ML models and fine-tuning (planned)
├── data/                    # Training datasets (planned)
└── docs/                    # Documentation
```

## Getting Started

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Development Status

- ✅ Project structure
- ✅ Frontend setup with Next.js
- ✅ Chatbot interface with black theme
- ✅ Tab system (Chat, Exercises, Stats, Settings)
- ✅ Exercise library with sample data
- 🔄 Backend API integration (planned)
- 🔄 LLM fine-tuning pipeline (planned)
- 🔄 KovaaK's API integration (planned)

## Next Steps

1. Set up backend API with FastAPI
2. Integrate Ollama for local LLM hosting
3. Implement KovaaK's API integration
4. Create fine-tuning pipeline for aim training data
5. Add user authentication and data persistence
# kokaaks-llm-personal-trainer
