#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$PWD}"
COMPOSE_FILE="v9/docker/compose.dev.yml"
API_BASE="${API_BASE:-http://localhost:8003}"
ADMIN_BASE="${ADMIN_BASE:-http://localhost:8085/api}"
PIPER_BASE="${PIPER_BASE:-http://localhost:5005}"
AUTO_DOWN="${AUTO_DOWN:-0}"

if [[ "${1:-}" == "--down" ]]; then
  AUTO_DOWN=1
fi

cleanup() {
  if [[ "$AUTO_DOWN" == "1" ]]; then
    docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" down --remove-orphans || true
  fi
}
trap cleanup EXIT

docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" up -d --build

for _ in $(seq 1 120); do
  if curl -sf "$API_BASE/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl -sf "$API_BASE/health" >/dev/null
curl -sf "$ADMIN_BASE/health" >/dev/null
curl -sf "$PIPER_BASE/health" >/dev/null
curl -sf "$API_BASE/models" >/dev/null

echo "[SMOKE][OK] API, Admin proxy, Piper and /models are reachable."
