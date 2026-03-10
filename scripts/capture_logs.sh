#!/usr/bin/env bash
set -euo pipefail

ART_DIR="${1:-test_artifacts/v9.1x}"
mkdir -p "$ART_DIR"

COMPOSE_FILE="v9/docker/compose.dev.yml"
PROJECT_DIR="$PWD"

docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --tail=300 api > "$ART_DIR/docker-logs-api.txt" || true
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --tail=200 web-agent > "$ART_DIR/docker-logs-web-agent.txt" || true
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --tail=200 web-customer > "$ART_DIR/docker-logs-web-customer.txt" || true
