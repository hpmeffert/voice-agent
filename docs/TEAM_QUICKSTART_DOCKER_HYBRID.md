TEAM QUICKSTART — Docker Hybrid (Host Ollama + Docker API/Piper/Web)

This setup keeps Piper (GPL) separated from the core application while providing a simple web UI for testing.


Key Features (V2/V3)
	•	Conversation Memory (V2): session_id is stored in browser localStorage. Clear resets the session.
	•	Model Switch (V3): Choose backend + model at runtime:
	•	Ollama (local) models: qwen2.5:7b, qwen2.5:3b, mistral:latest
	•	OpenAI (optional) backend (requires OPENAI_API_KEY)
	•	Dynamic model list (V3): UI fetches available Ollama models from GET /api/models (reads OLLAMA_BASE_URL/api/tags).

⸻

Architecture
	•	Ollama runs on the host macOS (best performance and avoids Docker memory limits).
	•	Docker Compose runs:
	•	api (FastAPI): STT (faster-whisper) → LLM (Ollama on host OR OpenAI) → calls piper
	•	piper (FastAPI sidecar): TTS using Piper + voice models mounted from host
	•	web (Nginx): serves UI and proxies /api/* and /tts/*

Web UI: http://localhost:8080

⸻

0) Prerequisites
	•	macOS + Docker Desktop
	•	Homebrew
	•	Ollama installed on host
	•	Piper voice models downloaded on host (NOT stored in this repo)

⸻

1) Host: Start Ollama and ensure models exist

In a terminal on macOS:

ollama serve

In another terminal (pull models you want to offer in the UI):

ollama pull qwen2.5:7b
ollama pull qwen2.5:3b
ollama pull mistral:latest
ollama list
curl http://localhost:11434/api/tags


⸻

2) Voice models on host (Piper)

Put Piper voices on the host at:
	•	$HOME/models/piper-voices

Each voice requires TWO files:
	•	*.onnx
	•	*.onnx.json

Examples:
	•	de_DE-thorsten-medium.onnx (+ .json)
	•	en_GB-northern_english_male-medium.onnx (+ .json) (example)
	•	sv_SE-nst-medium.onnx (+ .json)
	•	no_NO-talesyntese-medium.onnx (+ .json)
	•	fi_FI-harri-medium.onnx (+ .json)

Verify:

ls -la ~/models/piper-voices


⸻

3) Configure optional OpenAI (V3)

**Important (OpenAI Billing/Quota):**
If you see `HTTP 429 insufficient_quota`, your OpenAI project/account has no active billing or has reached its usage limits.
Enable billing / add credits in the OpenAI dashboard, or switch the UI backend to **Ollama (local)**.


If you want to enable OpenAI backend:

Create/update your local .env (do NOT commit):

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5

If OPENAI_API_KEY is missing, the UI may disable OpenAI or API will return an error.

⸻

4) Start the stack (recommended Makefile flow)

From the repository root:

make up-d
make wait

Notes:
	•	First startup can take a bit (Whisper import/model init).
	•	make wait runs health checks with retries.

Manual alternative:

docker compose -f docker/compose.sidecar.yml up -d --build --remove-orphans


⸻

5) Health checks

make health
make ollama-check

Endpoints:

curl -i http://localhost:8000/health
curl -i http://localhost:8080/api/health
curl -i http://localhost:5002/health
curl -s http://localhost:8080/api/models | head


⸻

6) Use the Web UI

Open:
	•	http://localhost:8080

Flow:
	1.	Select Backend (Ollama/OpenAI)
	2.	Select Model (dynamic list for Ollama)
	3.	Record → Stop → Send
You should see JSON (transcript/lang/answer/session_id) and hear the spoken reply.

Conversation Memory:
	•	After you say “My name is …”, you can ask “What is my name?” in the same session.
	•	Use Clear to reset the session.

⸻

Common issues

“Not ready / connection reset” right after start

This is normal during container warm-up. Use:

make wait

If needed:

make logs

Slow responses
	•	Prefer smaller models (qwen2.5:3b) for speed
	•	Reduce response length:
	•	set OLLAMA_NUM_PREDICT=120..160 in docker/compose.sidecar.yml under api.environment
	•	Keep context smaller:
	•	keep num_ctx: 2048 in API options

Piper works but no sound in UI
	•	Check browser autoplay settings
	•	Try pressing play on the reply audio element

Voice model not found
	•	Ensure /voices mount contains *.onnx and *.onnx.json
	•	Verify inside container:

docker compose -f docker/compose.sidecar.yml exec piper ls -la /voices | head


⸻

License separation note

This repo must NOT contain:
	•	Piper binaries/source code
	•	piper-tts as a dependency of the core app
	•	voice models (*.onnx, *.onnx.json)

Piper is provided as a separate Docker sidecar, and voices stay outside the repo.

