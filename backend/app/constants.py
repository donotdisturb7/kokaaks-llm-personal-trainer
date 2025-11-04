"""
Application-wide constants
Centralized location for magic numbers and reusable strings
"""

# ============================================================================
# Vector Database Constants
# ============================================================================

VECTOR_DIMENSION = 384  # FastEmbed BAAI/bge-small-en-v1.5 dimension

# IVFFLAT index configuration
IVFFLAT_LISTS = 100  # Number of lists for IVFFlat index

# RAG chunk configuration
DEFAULT_CHUNK_SIZE = 500  # Characters per chunk
DEFAULT_CHUNK_OVERLAP = 50  # Character overlap between chunks


# ============================================================================
# LLM System Prompts
# ============================================================================

AIM_TRAINING_SYSTEM_PROMPT = """Tu es un expert en entraînement de visée et un coach spécialisé dans KovaaK's FPS Aim Trainer.

Ton rôle est d'aider les joueurs à améliorer leur précision et leurs performances. Tu connais:
- Les différents types d'aim (tracking, flicking, target switching)
- Les exercices KovaaK's les plus efficaces
- Les techniques de placement de souris et de posture
- L'analyse des statistiques de performance
- La progression et l'entraînement structuré

Réponds de manière concise, pratique et motivante. Donne des conseils concrets et des exercices spécifiques."""


# ============================================================================
# Safety Levels
# ============================================================================

SAFETY_LEVELS = ["medical", "general", "training"]
DEFAULT_SAFETY_LEVEL = "general"


# ============================================================================
# Document Types
# ============================================================================

DOCUMENT_TYPES = ["guide", "tutorial", "reference", "exercise", "document"]
DEFAULT_DOCUMENT_TYPE = "document"


# ============================================================================
# Performance Analysis
# ============================================================================

# Trend detection thresholds
TREND_IMPROVING_THRESHOLD = 0.05  # 5% improvement
TREND_DECLINING_THRESHOLD = -0.05  # 5% decline
