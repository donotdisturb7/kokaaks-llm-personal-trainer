"""
Application FastAPI principale
Point d'entrée pour l'API KovaaK's AI Trainer
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import create_tables, close_connections
from app.api import chat, kovaaks, stats, exercises, llm_context

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logger.info("Starting KovaaK's AI Trainer API...")
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down KovaaK's AI Trainer API...")
    await close_connections()
    logger.info("Database connections closed")

# Création de l'application FastAPI
app = FastAPI(
    title="KovaaK's AI Trainer API",
    description="API pour l'entraînement personnalisé KovaaK's avec IA",
    version="1.0.0",
    debug=settings.api_debug,
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(chat.router)
app.include_router(kovaaks.router)
app.include_router(stats.router)
app.include_router(exercises.router)
app.include_router(llm_context.router)

@app.get("/")
async def root():
    """Point d'entrée racine de l'API"""
    return {
        "message": "KovaaK's AI Trainer API",
        "version": "1.0.0",
        "status": "running",
        "llm_provider": settings.llm_provider
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "database_configured": bool(settings.database_url),
        "redis_configured": bool(settings.redis_url),
        "kovaaks_username_configured": bool(settings.kovaaks_username)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )