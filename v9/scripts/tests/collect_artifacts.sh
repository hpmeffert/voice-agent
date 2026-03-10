#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:-}"
if [[ -z "$RUN_DIR" ]]; then
  echo "Usage: $0 <run_dir>" >&2
  exit 2
fi

mkdir -p "$RUN_DIR"

COMPOSE_FILE="v9/docker/compose.dev.yml"
PROJECT_DIR="${PROJECT_DIR:-$PWD}"

# Per-service logs for quick triage.
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --no-color api > "$RUN_DIR/docker-logs-api.txt" || true
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --no-color web-agent > "$RUN_DIR/docker-logs-web-agent.txt" || true
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --no-color web-customer > "$RUN_DIR/docker-logs-web-customer.txt" || true

# Optional piper log for voice path troubleshooting.
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --no-color piper > "$RUN_DIR/docker-logs-piper.txt" || true

# Full stack snapshot.
docker compose --project-directory "$PROJECT_DIR" -f "$COMPOSE_FILE" logs --no-color > "$RUN_DIR/docker-logs.txt" || true

# Optional WS event captures from caller-provided paths.
if [[ -n "${WS_AGENT_EVENTS_FILE:-}" && -f "${WS_AGENT_EVENTS_FILE}" ]]; then
  cp -f "${WS_AGENT_EVENTS_FILE}" "$RUN_DIR/ws_agent_events.jsonl" || true
fi
if [[ -n "${WS_CUSTOMER_EVENTS_FILE:-}" && -f "${WS_CUSTOMER_EVENTS_FILE}" ]]; then
  cp -f "${WS_CUSTOMER_EVENTS_FILE}" "$RUN_DIR/ws_customer_events.jsonl" || true
fi

# Optional screenshots folder (headless/browser captures).
if [[ -n "${SCREENSHOT_DIR:-}" && -d "${SCREENSHOT_DIR}" ]]; then
  mkdir -p "$RUN_DIR/screenshots"
  find "${SCREENSHOT_DIR}" -maxdepth 1 -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" \) -exec cp -f {} "$RUN_DIR/screenshots/" \; || true
fi

# Environment snapshot without obvious secrets.
(
  env | grep -E 'VOICE|LANG|TTS|OLLAMA|OPENAI|MONGO|VALKEY|REDIS|RETENTION|MODEL|BACKEND' \
    | sed -E 's/(TOKEN|KEY|SECRET|PASSWORD)=.*/\1=<redacted>/I'
) > "$RUN_DIR/ENV_SNAPSHOT.txt" || true

if [[ ! -s "$RUN_DIR/ENV_SNAPSHOT.txt" ]]; then
  echo "No matching non-secret environment variables exported in shell context." > "$RUN_DIR/ENV_SNAPSHOT.txt"
fi

echo "Collected artifacts into: $RUN_DIR"
