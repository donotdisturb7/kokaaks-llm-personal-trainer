#!/bin/bash

echo "🚀 Démarrage de KovaaK's AI Trainer"

# 1. Démarrer PostgreSQL et Redis
echo "📦 Démarrage des services Docker..."

docker compose up -d postgres redis

# Attendre que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 10

# 2. Initialiser la base de données
echo "🗄️ Initialisation de la base de données..."
cd backend
source env/bin/activate
python init_db.py

# 3. Créer les migrations
echo "📝 Création des migrations..."
alembic revision --autogenerate -m "Initial schema"

# 4. Appliquer les migrations
echo "🔄 Application des migrations..."
alembic upgrade head

# 5. Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📄 Création du fichier .env..."
    cat > .env << EOF
# Configuration utilisateur
CURRENT_USER_KOVAAKS_USERNAME=
CURRENT_USER_STEAM_ID=

# Configuration LLM
LLM_PROVIDER=ollama
GROQ_API_KEY=

# Configuration base de données
DATABASE_URL=postgresql+asyncpg://kovaaks:kovaaks_pass@localhost:5433/kovaaks_ai
REDIS_URL=redis://localhost:6379/0
EOF
    echo "✅ Fichier .env créé. Veuillez configurer votre username KovaaK's."
fi

echo "✅ Setup terminé !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Éditez backend/.env et ajoutez votre CURRENT_USER_KOVAAKS_USERNAME"
echo "2. Lancez l'API : cd backend && source env/bin/activate && python run.py"
echo "3. Accédez à la documentation : http://localhost:8000/docs"
echo ""
echo "🎯 L'API sera disponible sur http://localhost:8000"
