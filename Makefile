# Makefile — convenience commands for legacy hybrid + V7 automation

COMPOSE_FILE = docker/compose.sidecar.yml
V7_COMPOSE_FILE = v7/docker/compose.dev.yml
PROJECT_DIR = $(CURDIR)
BASE_BRANCH = release/v5.4-azure-stable


.PHONY: up-d wait - up down restart logs ps rebuild web-rebuild api-rebuild piper-rebuild health
.PHONY: v7-up v7-down v7-restart v7-ps v7-logs v7-health v7-smoke v7-test
.PHONY: v7-pr v7-tag v7-release v7-post-merge

up-d:
	docker compose --env-file .env -f $(COMPOSE_FILE) up -d --build --remove-orphans

wait:
	@$(MAKE) health

down:
	docker compose -f $(COMPOSE_FILE) down

open:
	open http://localhost:8080

restart:
	docker compose --env-file .env -f $(COMPOSE_FILE) down --remove-orphans
	docker compose --env-file .env -f $(COMPOSE_FILE) up -d --build --remove-orphans

ps:
	docker compose --env-file .env -f $(COMPOSE_FILE) ps

logs:
	docker compose --env-file .env -f $(COMPOSE_FILE) logs -f --tail=200

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

# ----------------------------
# V7 automation
# ----------------------------
v7-up:
	docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) up -d --build

v7-down:
	docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) down --remove-orphans

v7-restart:
	docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) down --remove-orphans
	docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) up -d --build

v7-ps:
	docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) ps

v7-logs:
	docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) logs -f --tail=200

v7-health:
	@echo "Checking V7 endpoints (retry up to 45x)..."
	@for i in $$(seq 1 45); do \
	  ok=1; \
	  curl -fsS --max-time 2 http://localhost:8001/health >/dev/null || ok=0; \
	  curl -fsS --max-time 2 http://localhost:8081/api/health >/dev/null || ok=0; \
	  curl -fsS --max-time 2 http://localhost:5003/health >/dev/null || ok=0; \
	  if [ $$ok -eq 1 ]; then echo "V7 OK"; exit 0; fi; \
	  echo "V7 not ready ($$i/45) ..."; sleep 1; \
	done; \
	echo "V7 health check failed"; \
	echo "--- docker ps ---"; docker compose --project-directory "$(PROJECT_DIR)" -f $(V7_COMPOSE_FILE) ps || true; \
	echo "--- endpoints ---"; \
	curl -i http://localhost:8001/health || true; \
	curl -i http://localhost:8081/api/health || true; \
	curl -i http://localhost:5003/health || true; \
	exit 1

v7-smoke:
	@curl -sS http://localhost:8081/api/health
	@curl -sS http://localhost:8081/api/config
	@curl -sS -F "file=@/dev/null;filename=empty.webm" http://localhost:8081/api/voice

v7-test: v7-up v7-health v7-smoke

# Usage:
# make v7-pr VERSION=7.3.0
v7-pr:
	@test -n "$(VERSION)" || (echo "VERSION is required, e.g. make v7-pr VERSION=7.3.0"; exit 1)
	gh pr create \
	  --base $(BASE_BRANCH) \
	  --head "$$(git branch --show-current)" \
	  --title "V$(VERSION): automated release from Makefile" \
	  --body-file "v7/docs/RELEASE_NOTES_v$(VERSION).md"

# Usage:
# make v7-tag VERSION=7.3.0
v7-tag:
	@test -n "$(VERSION)" || (echo "VERSION is required, e.g. make v7-tag VERSION=7.3.0"; exit 1)
	git tag -a "v$(VERSION)" -m "Voice Agent V$(VERSION)"
	git push origin "v$(VERSION)"

# Usage:
# make v7-release VERSION=7.3.0
v7-release:
	@test -n "$(VERSION)" || (echo "VERSION is required, e.g. make v7-release VERSION=7.3.0"; exit 1)
	gh release create "v$(VERSION)" \
	  --title "Voice Agent v$(VERSION)" \
	  --notes-file "v7/docs/RELEASE_NOTES_v$(VERSION).md"

# Usage (after PR merge):
# make v7-post-merge VERSION=7.3.0
v7-post-merge:
	@test -n "$(VERSION)" || (echo "VERSION is required, e.g. make v7-post-merge VERSION=7.3.0"; exit 1)
	git checkout $(BASE_BRANCH)
	git pull
	$(MAKE) v7-tag VERSION=$(VERSION)
	$(MAKE) v7-release VERSION=$(VERSION)
