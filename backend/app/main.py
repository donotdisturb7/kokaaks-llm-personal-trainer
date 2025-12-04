from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import create_tables, close_connections
from app.api import chat, kovaaks, stats, exercises, llm_context, rag

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
    logger.info("Database tables are managed by Alembic migrations")
    
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

# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    logger.error(f"ValueError on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "type": "ValueError"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "type": type(exc).__name__,
            "message": str(exc) if settings.api_debug else "Internal server error"
        }
    )


# ============================================================================
# Inclusion des routers
# ============================================================================

app.include_router(chat.router)
app.include_router(kovaaks.router)
app.include_router(stats.router)
app.include_router(exercises.router)
app.include_router(llm_context.router)
app.include_router(rag.router)


# ============================================================================
# Root Endpoints
# ============================================================================

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