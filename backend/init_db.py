#!/usr/bin/env python3
"""
Script pour initialiser la base de données
"""
import asyncio
import asyncpg
from app.config import settings

async def init_database():
    """Initialise la base de données PostgreSQL"""
    # Connexion à PostgreSQL sans spécifier de base de données
    conn = await asyncpg.connect(
        host="localhost",
        port=5433,
        user="kovaaks",
        password="kovaaks_pass",
        database="postgres"  # Connexion à la base par défaut
    )
    
    try:
        # Vérifier si la base de données existe
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", 
            "kovaaks_ai"
        )
        
        if not result:
            print("Création de la base de données 'kovaaks_ai'...")
            await conn.execute('CREATE DATABASE kovaaks_ai')
            print("✅ Base de données créée avec succès")
        else:
            print("✅ Base de données 'kovaaks_ai' existe déjà")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
