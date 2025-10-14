"""
Configuration de la base de données PostgreSQL et Redis
Gère les connexions async et les sessions
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import asyncio as aioredis
from app.config import Settings

settings = Settings()

# PostgreSQL async - Lazy initialization
engine = None
AsyncSessionLocal = None
Base = declarative_base()

def get_engine():
    global engine
    if engine is None:
        engine = create_async_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_size=10,
            max_overflow=20
        )
    return engine

def get_session_local():
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        AsyncSessionLocal = sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return AsyncSessionLocal

# Redis async
redis_client = None

async def get_redis():
    """Récupère le client Redis async"""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    return redis_client

async def get_db():
    """Dependency pour récupérer une session de base de données"""
    session_local = get_session_local()
    async with session_local() as session:
        yield session

async def create_tables():
    """Crée toutes les tables dans la base de données"""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_connections():
    """Ferme les connexions à la base de données et Redis"""
    global redis_client, engine
    if redis_client:
        await redis_client.close()
    if engine:
        await engine.dispose()

