# Makefile — convenience commands for the hybrid docker setup

COMPOSE_FILE = docker/compose.sidecar.yml

.PHONY: up down restart logs ps rebuild web-rebuild api-rebuild piper-rebuild health

up:
	docker compose -f $(COMPOSE_FILE) up --build

down:
	docker compose -f $(COMPOSE_FILE) down

restart:
	docker compose -f $(COMPOSE_FILE) down
	docker compose -f $(COMPOSE_FILE) up --build

ps:
	docker compose -f $(COMPOSE_FILE) ps

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

rebuild:
	docker compose -f $(COMPOSE_FILE) build --no-cache
	docker compose -f $(COMPOSE_FILE) up

web-rebuild:
	docker compose -f $(COMPOSE_FILE) build --no-cache web
	docker compose -f $(COMPOSE_FILE) up -d

api-rebuild:
	docker compose -f $(COMPOSE_FILE) build --no-cache api
	docker compose -f $(COMPOSE_FILE) up -d

piper-rebuild:
	docker compose -f $(COMPOSE_FILE) build --no-cache piper
	docker compose -f $(COMPOSE_FILE) up -d

health:
	curl -i http://localhost:8000/health || true
	curl -i http://localhost:8080/api/health || true
	curl -i http://localhost:5002/health || true
