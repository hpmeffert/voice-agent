# TEAM QUICKSTART — Docker Hybrid (Host Ollama + Docker API/Piper/Web)

This setup keeps **Piper (GPL)** separated from the core application while providing a simple web UI for testing.

## Architecture
- **Ollama** runs on the **host macOS** (best performance and avoids Docker memory limits).
- **Docker Compose** runs:
  - `api` (FastAPI): STT (faster-whisper) → LLM (Ollama on host) → calls `piper`
  - `piper` (FastAPI sidecar): TTS using Piper + voice models mounted from host
  - `web` (Nginx): serves UI and proxies `/api/*` and `/tts/*`

Web UI: `http://localhost:8080`

---

## 0) Prerequisites
- macOS + Docker Desktop
- Homebrew
- Ollama installed on host
- Piper voice models downloaded on host (NOT stored in this repo)

---

## 1) Host: Start Ollama and ensure the model exists
In a terminal on macOS:

```bash
ollama serve
```

In another terminal:

```bash
ollama pull qwen2.5:7b
ollama list
curl http://localhost:11434/api/tags
```

You should see `qwen2.5:7b` listed.

---

## 2) Voice models on host (Piper)
Put Piper voices on the host at:

- `$HOME/models/piper-voices`

Each voice requires TWO files:
- `*.onnx`
- `*.onnx.json`

Examples:
- `de_DE-thorsten-medium.onnx` (+ `.json`)
- `en_US-lessac-medium.onnx` (+ `.json`)
- `sv_SE-nst-medium.onnx` (+ `.json`)
- `no_NO-talesyntese-medium.onnx` (+ `.json`)
- `fi_FI-harri-medium.onnx` (+ `.json`)

Verify:

```bash
ls -la ~/models/piper-voices
```

---

## 3) Start the stack
From the repository root:

```bash
docker compose -f docker/compose.sidecar.yml up --build
```

Health checks:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8080/api/health
curl -i http://localhost:5002/health
```

---

## 4) Use the Web UI
Open:

- `http://localhost:8080`

Record → Stop → Send  
You should see JSON (transcript/lang/answer) and hear the spoken reply.

---

## Common issues

### Slow responses
- Reduce response length:
  - set `OLLAMA_NUM_PREDICT=120..160` in `docker/compose.sidecar.yml` under `api.environment`
- Keep context smaller:
  - set `num_ctx: 2048` in `docker/api/app.py` (Ollama options)

### Piper works but no sound in UI
- Check your browser autoplay settings
- Try pressing play on the reply audio element

### Voice model not found
- Ensure `/voices` mount contains the `*.onnx` and `*.onnx.json` files
- Verify inside the container:
  ```bash
  docker compose -f docker/compose.sidecar.yml exec piper ls -la /voices | head
  ```

---

## License separation note
This repo must NOT contain:
- Piper binaries/source code
- `piper-tts` as a dependency of the core app
- voice models (`*.onnx`, `*.onnx.json`)

Piper is provided as a separate Docker sidecar (or local installation), and voices stay outside the repo.
