#!/bin/bash
# Script de démarrage complet pour le projet KovaaK's AI Trainer

set -e

echo "🚀 Démarrage de KovaaK's AI Trainer"
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Arrêter les containers existants
echo -e "${BLUE}📦 Arrêt des containers existants...${NC}"
docker compose down 2>/dev/null || true

# Nettoyer les anciennes images si demandé
if [ "$1" == "--clean" ]; then
    echo -e "${YELLOW}🧹 Nettoyage des images...${NC}"
    docker compose down -v
    docker system prune -f
fi

# Build des images
echo -e "${BLUE}🔨 Build des images Docker...${NC}"
docker compose build

# Démarrer les services de base (postgres, redis)
echo -e "${BLUE}🗄️  Démarrage de PostgreSQL et Redis...${NC}"
docker compose up -d postgres redis

# Attendre que postgres soit prêt
echo -e "${BLUE}⏳ Attente de PostgreSQL...${NC}"
sleep 5

# Vérifier la santé de postgres
until docker compose exec postgres pg_isready -U kovaaks > /dev/null 2>&1; do
    echo -e "${YELLOW}   Postgres n'est pas encore prêt, attente...${NC}"
    sleep 2
done
echo -e "${GREEN}✓ PostgreSQL est prêt!${NC}"

# Vérifier la santé de Redis
echo -e "${BLUE}⏳ Vérification de Redis...${NC}"
until docker compose exec redis redis-cli ping > /dev/null 2>&1; do
    echo -e "${YELLOW}   Redis n'est pas encore prêt, attente...${NC}"
    sleep 2
done
echo -e "${GREEN}✓ Redis est prêt!${NC}"

# Lancer le backend
echo -e "${BLUE}🐍 Démarrage du backend...${NC}"
docker compose up -d backend

# Attendre que le backend soit prêt
echo -e "${BLUE}⏳ Attente du backend...${NC}"
sleep 5
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    echo -e "${YELLOW}   Backend n'est pas encore prêt, attente...${NC}"
    sleep 2
done
echo -e "${GREEN}✓ Backend est prêt!${NC}"

# Lancer le frontend
echo -e "${BLUE}⚛️  Démarrage du frontend...${NC}"
docker compose up -d frontend

echo ""
echo -e "${GREEN}✅ Tous les services sont démarrés!${NC}"
echo ""
echo "📊 Services disponibles:"
echo "  - Frontend:     http://localhost:3000"
echo "  - Backend API:  http://localhost:8000"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - PostgreSQL:   localhost:5433 (kovaaks/kovaaks_pass)"
echo "  - Redis:        localhost:6379"
echo ""
echo "📝 Commandes utiles:"
echo "  - Voir les logs:        docker compose logs -f"
echo "  - Arrêter:              docker compose down"
echo "  - Redémarrer:           docker compose restart"
echo "  - Shell backend:        docker compose exec backend bash"
echo "  - Migrations:           docker compose exec backend alembic upgrade head"
echo ""
echo "🎯 Pour voir les logs en temps réel:"
echo "   docker compose logs -f"


