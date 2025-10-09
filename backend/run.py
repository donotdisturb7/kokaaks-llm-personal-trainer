#!/usr/bin/env python3
"""
Script de lancement pour le backend
Permet de démarrer l'API facilement
"""
import uvicorn
from app.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    print(f"🚀 Démarrage de l'API KovaaK's AI Personal Trainer")
    print(f"📍 Host: {settings.api_host}:{settings.api_port}")
    print(f"🤖 Ollama: {settings.ollama_host}:{settings.ollama_port}")
    print(f"📚 Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print("-" * 60)
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )
