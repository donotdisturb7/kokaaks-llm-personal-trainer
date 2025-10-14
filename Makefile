# Makefile pour KovaaK's AI Trainer
# Simplifie les commandes Docker Compose

.PHONY: help build up down restart logs logs-backend logs-frontend clean shell-backend shell-frontend db-migrate db-reset test

# Couleurs pour les messages
GREEN  := \033[0;32m
YELLOW := \033[1;33m
NC     := \033[0m

help: ## Affiche l'aide
	@echo "$(GREEN)KovaaK's AI Trainer - Commandes disponibles:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

build: ## Build les images Docker
	@echo "$(GREEN)🔨 Build des images Docker...$(NC)"
	docker compose build

up: ## Démarre tous les services
	@echo "$(GREEN)🚀 Démarrage de tous les services...$(NC)"
	./docker-start.sh

down: ## Arrête tous les services
	@echo "$(YELLOW)🛑 Arrêt de tous les services...$(NC)"
	docker compose down

restart: down up ## Redémarre tous les services

logs: ## Affiche les logs de tous les services
	docker compose logs -f

logs-backend: ## Affiche les logs du backend
	docker compose logs -f backend

logs-frontend: ## Affiche les logs du frontend
	docker compose logs -f frontend

logs-postgres: ## Affiche les logs de PostgreSQL
	docker compose logs -f postgres

logs-redis: ## Affiche les logs de Redis
	docker compose logs -f redis

clean: ## Arrête et supprime tous les containers et volumes
	@echo "$(YELLOW)🧹 Nettoyage complet...$(NC)"
	docker compose down -v
	docker system prune -f

shell-backend: ## Ouvre un shell dans le container backend
	docker compose exec backend bash

shell-frontend: ## Ouvre un shell dans le container frontend
	docker compose exec frontend sh

shell-postgres: ## Ouvre un shell PostgreSQL
	docker compose exec postgres psql -U kovaaks -d kovaaks_ai

shell-redis: ## Ouvre un shell Redis
	docker compose exec redis redis-cli

db-migrate: ## Lance les migrations Alembic
	@echo "$(GREEN)📊 Exécution des migrations...$(NC)"
	docker compose exec backend alembic upgrade head

db-reset: ## Reset la base de données (ATTENTION: supprime toutes les données!)
	@echo "$(YELLOW)⚠️  Reset de la base de données...$(NC)"
	docker compose down postgres
	docker volume rm kovaaks-postgres-data || true
	docker compose up -d postgres
	@sleep 5
	docker compose exec backend alembic upgrade head

ps: ## Liste les containers en cours
	docker compose ps

stats: ## Affiche les stats des containers
	docker stats

health: ## Vérifie la santé des services
	@echo "$(GREEN)🏥 Vérification de la santé des services:$(NC)"
	@curl -s http://localhost:8000/health | jq '.' || echo "Backend non accessible"
	@curl -s http://localhost:3000 > /dev/null && echo "Frontend: OK" || echo "Frontend: KO"

test-cache: ## Test le système de cache
	@echo "$(GREEN)🧪 Test du cache Redis...$(NC)"
	cd backend && python test_cache_flow.py

dev: ## Démarre en mode développement avec logs
	@echo "$(GREEN)🚀 Démarrage en mode développement...$(NC)"
	./docker-start.sh
	docker compose logs -f


