# V9.1.7 — Release Notes (EN) — 2026-03-10

## Highlights
- **Auto-upload after recording stops (Customer UI):** once recording ends, the upload/send starts automatically (no extra “Send” click).
- **Default model = qwen2.5:3b:** UI default + backend fallback are aligned to `qwen2.5:3b` (fallback to `qwen2.5:7b` if not available).
- **UX/Robustness:** clearer status + error messages for upload/transcribe/LLM/TTS.

## Detailed Changes
### UI (Customer / Agent)
- Customer: auto-upload triggered from `mediaRecorder.onstop` (or silence-stop if enabled).
- Model dropdown default: prefer `qwen2.5:3b` if present, else fallback to `qwen2.5:7b`.
- Optional: “Auto-send after recording” toggle (default ON for customer client; optional for agent).

### Backend
- Model fallback: if no `model` provided → use `qwen2.5:3b` (if available) else `OLLAMA_MODEL`.
- No changes to dual-lane routing/translation logic (must remain stable).
- **Additional low-risk scope:** TTS text sanitizer at TTS call boundary only (removes markdown/control formatting in spoken output without changing stored conversation content).

## Documentation (Required)
Update **DE + EN**:
- User Guide (DE/EN)
- Demo Guide (DE/EN, min. 3 story-driven scenarios)
- Admin Guide (DE/EN: start/run, tests, parameters, folders, component checks)
- Release Notes history (DE/EN from V7.0.0 to current)
Doc language switching:
- UI language DE → show DE docs
- UI language EN → show EN docs
- any other UI language → show EN docs

## Tests (Required, 2-minute proof)
### Browser Smoke
1) Open Customer (DE) and Agent (EN)
2) Customer speaks → recording stops → **auto-upload starts**
3) Agent receives LIVE: original + translation, optional incoming speak correct
4) Agent replies (EN) → Customer sees/hears (DE)
5) Result: **PASS**

### Automated Script
- Run `run_v9_ws_duallane_tests.sh` + write logs:
  - `artifacts/test-log-v9.1.7.txt`
  - `artifacts/SUMMARY.md`
  - `artifacts/ws_agent_events.jsonl`, `artifacts/ws_customer_events.jsonl`
- Expectation: all scenarios PASS.

## Known Issues / Notes
- Latency depends heavily on STT/LLM hardware (MacBook Pro M1 / 16GB can be limiting). Defaulting to 3B reduces LLM latency.

## License & Commercialization Guardrails
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core; isolate copyleft as external sidecars.
- Explicitly mark license risks.

## Artifact Policy (Tests)
- Store each run outputs in `artifacts/`.
- Before a new run:
  - move to `artifacts/_archive/<timestamp>/` or delete (per policy).
- Never commit `artifacts/` to Git (gitignore).
- Current V9 automation also supports structured run output under `v9/artifacts/<timestamp>/` with retention cleanup.
