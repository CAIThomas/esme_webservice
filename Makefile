# 📦 Variables
PROJECT_NAME = flask_app
DOCKER_COMPOSE = docker-compose
APP_CONTAINER_NAME = flask_app_esme
PYTHON = python3
OS := $(shell uname -s)

# 🐳 Commandes Docker
docker-build:
	@echo "🐳 Construction et démarrage des conteneurs Docker..."
	$(DOCKER_COMPOSE) up --build -d

docker-up:
	@echo "📦 Démarrage des conteneurs Docker..."
	$(DOCKER_COMPOSE) up -d

docker-down:
	@echo "🛑 Arrêt et suppression des conteneurs Docker..."
	$(DOCKER_COMPOSE) down

docker-clean:
	@echo "🧹 Nettoyage des images et volumes Docker inutilisés..."
	docker system prune -af

# 🛢 Commandes Base de Données
db-init:
	@echo "📊 Initialisation de la base de données (flask db init)..."
	docker exec -it $(APP_CONTAINER_NAME) flask db init

db-migrate:
	@echo "📈 Création d'une migration (flask db migrate)..."
	docker exec -it $(APP_CONTAINER_NAME) flask db migrate

db-upgrade:
	@echo "⬆️ Application des migrations (flask db upgrade)..."
	docker exec -it $(APP_CONTAINER_NAME) flask db upgrade

db-reset:
	@echo "♻️ Réinitialisation complète de la base de données..."
ifeq ($(OS), Windows_NT)
	@docker exec -it $(APP_CONTAINER_NAME) cmd /C "rmdir /S /Q migrations"
	@docker exec -it $(APP_CONTAINER_NAME) flask db init
	@docker exec -it $(APP_CONTAINER_NAME) flask db migrate
	@docker exec -it $(APP_CONTAINER_NAME) flask db upgrade
else
	@docker exec -it $(APP_CONTAINER_NAME) bash -c "rm -rf migrations && flask db init && flask db migrate && flask db upgrade"
endif

# 🆘 Aide
help:
	@echo "💡 Liste des commandes disponibles :"
	@echo "  make docker-build   -> Construire et démarrer les conteneurs Docker"
	@echo "  make docker-up      -> Démarrer l'application avec Docker"
	@echo "  make docker-down    -> Arrêter et supprimer les conteneurs"
	@echo "  make docker-clean   -> Nettoyer les images Docker inutilisées"
	@echo "  make db-init        -> Initialiser la base de données (flask db init)"
	@echo "  make db-migrate     -> Créer une nouvelle migration"
	@echo "  make db-upgrade     -> Appliquer les migrations à la base"
	@echo "  make db-reset       -> Réinitialiser complètement la base de données"
	@echo "  make help           -> Afficher cette aide"