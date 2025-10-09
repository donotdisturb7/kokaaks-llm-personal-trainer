"""
Application principale FastAPI
Point d'entrée pour l'API backend de KovaaK's AI Personal Trainer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn

from app.config import Settings, get_settings
from app.api.chat import router as chat_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="KovaaK's AI Personal Trainer API",
    description="API backend pour l'assistant IA d'entraînement de visée",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
def setup_cors(app: FastAPI, settings: Settings):
    """Configure CORS pour permettre les requêtes du frontend"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Configuration des routes
def setup_routes(app: FastAPI):
    """Configure les routes de l'API"""
    app.include_router(chat_router)

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire d'erreurs global pour l'API"""
    logger.error(f"Erreur non gérée: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne du serveur"}
    )

# Routes de base
@app.get("/")
async def root():
    """Route racine - informations sur l'API"""
    return {
        "message": "KovaaK's AI Personal Trainer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check(settings: Settings = get_settings()):
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "ollama_config": {
            "host": settings.ollama_host,
            "port": settings.ollama_port,
            "model": settings.ollama_model
        }
    }

# Configuration de l'application
def create_app() -> FastAPI:
    """Crée et configure l'application FastAPI"""
    settings = get_settings()
    
    # Configuration CORS
    setup_cors(app, settings)
    
    # Configuration des routes
    setup_routes(app)
    
    logger.info(f"Application configurée - Ollama: {settings.ollama_host}:{settings.ollama_port}")
    
    return app

# Point d'entrée pour le développement
if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )
