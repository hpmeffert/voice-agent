#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-qwen2.5:7b}"
CID="$(docker compose -f docker/compose.sidecar.yml ps -q ollama)"
echo "Ollama container: $CID"
docker exec -it "$CID" ollama pull "$MODEL"
docker exec -it "$CID" ollama list
