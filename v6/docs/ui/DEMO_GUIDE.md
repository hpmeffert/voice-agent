# UI Demo Guide (V6.10.0)

## Quick walkthrough
1. Open UI: `http://localhost:8080`
2. Run one short voice request.
3. Run a follow-up to show session memory.
4. Switch model (`qwen2.5:3b` vs `qwen2.5:7b`) and compare behavior.
5. Show transcript export.
6. Show protocol v1 export via API (`/api/export/protocol`).

## Hands-free recording (new in V6.8.0)
- Controls in main panel:
  - `Auto-stop on silence` (default ON)
  - `Auto-send after stop` (default ON)
  - `Silence threshold (ms)` (default `1100`)
  - `Max recording seconds` (default `45`)
- Demo flow:
  1. Keep `Auto-stop on silence` enabled.
  2. Click `Record`, speak one sentence, then stay silent.
  3. Recording should stop automatically after silence window.
  4. If `Auto-send after stop` is enabled, request is sent immediately.
  5. Disable `Auto-stop on silence` and verify manual `Stop` + `Send` still works.

## Mic permission quirks
- First run may require microphone permission in browser settings.
- If mic permission is blocked, UI shows `Mic error`.
- Very noisy environments may need a higher silence threshold.

## Performance section (new in V6.7.0)
- The Result panel now shows latency breakdown:
  - `STT` ms
  - `LLM` ms
  - `TTS` ms
  - `Total` ms
- `/api/voice` JSON includes:
  - `stt_ms`, `llm_ms`, `tts_ms`, `total_ms`
  - `metrics` object with the same values
- Recent metrics endpoint:
  - `GET /api/metrics/recent?user_id=<USER_ID>&limit=20`

## Tuning tips
- Use smaller LLM model for lower latency (for example `qwen2.5:3b`).
- Lower `OLLAMA_NUM_PREDICT` to reduce generation time.
- Use smaller Whisper model (`WHISPER_MODEL`) for faster STT.
- Warm up the stack before demo starts (`/api/health`, `/api/models`).

## Story arc for live demos (recommended)
1. Opening (trust):
   - "This is a local-first voice agent with persistent memory and controllable exports."
2. Experience (wow):
   - hands-free auto-stop + auto-send in one smooth turn.
3. Transparency (confidence):
   - show readable transcript/answer and latency breakdown.
4. Operational readiness (credibility):
   - show protocol export endpoint and mention template override for team-specific formats.
5. Close (action):
   - "Same stack can be tailored per customer process without changing core code."

## Help menu demo moment (V6.10.0)
1. Open top-right `Help` menu.
2. Open `Help` and show user guidance in-app.
3. Open `Demo Guide` and show runbook consistency.
4. Enter admin token, reload menu state, and show `Admin Docs` appears.
5. Mention server gate:
   - UI visibility is client convenience.
   - actual access is verified by `/api/whoami` and protected admin docs endpoint.
