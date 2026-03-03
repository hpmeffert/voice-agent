# Makefile — convenience commands for the hybrid docker setup

COMPOSE_FILE = docker/compose.sidecar.yml


.PHONY: up-d wait - up down restart logs ps rebuild web-rebuild api-rebuild piper-rebuild health

up-d:
	docker compose -f $(COMPOSE_FILE) up -d --build --remove-orphans

wait:
	@$(MAKE) health

down:
	docker compose -f $(COMPOSE_FILE) down

open:
	open http://localhost:8080

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
	@echo "Checking services (retry up to 30x)..."
	@sleep 2
	@for i in $$(seq 1 30); do \
	  ok=1; \
	  curl -fsS --max-time 2 http://localhost:8000/health >/dev/null || ok=0; \
	  curl -fsS --max-time 2 http://localhost:8080/api/health >/dev/null || ok=0; \
	  curl -fsS --max-time 2 http://localhost:5002/health >/dev/null || ok=0; \
	  if [ $$ok -eq 1 ]; then echo "OK"; exit 0; fi; \
	  echo "Not ready yet ($$i/30) ..."; sleep 1; \
	done; \
	echo "Health check failed"; \
	echo "--- docker ps ---"; docker compose -f $(COMPOSE_FILE) ps || true; \
	echo "--- endpoints ---"; \
	curl -i http://localhost:8000/health || true; \
	curl -i http://localhost:8080/api/health || true; \
	curl -i http://localhost:5002/health || true; \
	exit 1
	

ollama-check:
	@echo "Checking host Ollama on http://localhost:11434 ..."
	@curl -sS http://localhost:11434/api/tags | head -c 400 || true
	@echo ""