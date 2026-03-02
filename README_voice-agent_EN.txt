# Voice Agent (macOS) — Local STT + Local LLM (Ollama) + External TTS (Piper)

This repository provides a reproducible local voice-agent setup:

- **STT**: `faster-whisper` (local)
- **LLM**: **Ollama** (local) — default: `qwen2.5:7b`
- **TTS**: **Piper** (external, installed separately for license separation)
- Languages supported via Piper voices: **DE / EN / SV / NO / FI**

> **License separation goal:** This repo must remain independent from Piper (GPL).  
> Piper binaries/source/packages and voice models **must not** be committed into this repository.

---

## Quickstart (Local Dev: Bring Your Own Piper)

### Prerequisites
- macOS (Apple Silicon recommended)
- Homebrew
- Python 3.9+ (3.10/3.11 recommended)
- VS Code (optional)
- Microphone permission enabled for the app you run Python from (VS Code or Terminal)

### 1) System dependencies
```bash
brew install ffmpeg ollama
```

Start Ollama and pull the model:
```bash
ollama serve
ollama pull qwen2.5:7b
ollama list
```

### 2) Clone and setup the repo venv
```bash
git clone git@github.com:hpmeffert/voice-agent.git
cd voice-agent
git checkout Piper-MIT

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Install Piper separately (outside this repo)
> Install Piper in a separate folder to keep the repo license-clean.

```bash
mkdir -p ~/tools/piper-tts
cd ~/tools/piper-tts
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install piper-tts pathvalidate
piper --help
```

### 4) Download voice models (outside this repo)
Create the voices folder:
```bash
mkdir -p ~/models/piper-voices
```

For each voice, you need **two** files:
- `*.onnx`
- `*.onnx.json`

Example voices used:
- `de_DE-thorsten-medium.onnx` (+ `.json`)
- `en_US-lessac-medium.onnx` (+ `.json`)
- `sv_SE-nst-medium.onnx` (+ `.json`)
- `no_NO-talesyntese-medium.onnx` (+ `.json`)
- `fi_FI-harri-medium.onnx` (+ `.json`)

Verify:
```bash
ls -la ~/models/piper-voices
```

### 5) Create local `.env`
Copy the template:
```bash
cp .env.example .env
```

### 6) Run smoke tests
TTS test:
```bash
source .venv/bin/activate
python tts_test.py
```

Run the full voice loop:
```bash
python main.py
```

---

## Quickstart (Docker Sidecar: API + Piper Service + Ollama)

> This is the recommended structure for SaaS/on-prem deployments.  
> Piper runs as a separate sidecar service, and your core app communicates via HTTP.

### Prerequisites
- Docker Desktop

### Start
```bash
docker compose -f docker/compose.sidecar.yml up --build
```

### Notes
- Voices are **not** stored in this repo.
- Voices are mounted into the Piper container (read-only) under `/voices`.
- The core service calls Piper via `http://piper:5002/tts`.

---

## License Separation Policy (Short)

Non-negotiables:
1. Do not commit **Piper binaries/source** or any **piper-tts** dependency into this repo.
2. Do not commit **voice models** (`*.onnx`, `*.onnx.json`) into this repo.
3. Communicate with Piper only via:
   - CLI process boundary (local dev), or
   - HTTP sidecar boundary (docker/saaS)
4. Never commit `.env` or any virtual environments (`.venv/`, `venv/`, `env/`).
5. Run the preflight check before every push.

Preflight:
```bash
bash scripts/check_repo_clean.sh
```

---

## Common Issues

### Piper not found / `$HOME` not expanded
- This project supports `$HOME`/`~` in `.env` by expanding paths in the Piper adapter.
- Ensure `.env` is present and correct.
- Verify Piper exists:
```bash
ls -la ~/tools/piper-tts/.venv/bin/piper
```

### Microphone returns silence (RMS 0.0)
- Check macOS microphone permissions: System Settings → Privacy & Security → Microphone
- Enable for VS Code and/or Terminal and restart the app

### Ollama not responding
- Ensure `ollama serve` is running
- Check:
```bash
curl http://localhost:11434/api/tags
ollama list
```

---

## Repository Hygiene

Required `.gitignore` entries:
- `.env`
- `.venv/` (and `venv/`, `env/`)
- `*.onnx`, `*.onnx.json`
- `.DS_Store`

Before pushing:
```bash
bash scripts/check_repo_clean.sh
```
