# UI Demo Guide (V6.8.0)

## Quick walkthrough
1. Open UI: `http://localhost:8080`
2. Run one short voice request.
3. Run a follow-up to show session memory.
4. Switch model (`qwen2.5:3b` vs `qwen2.5:7b`) and compare behavior.
5. Show transcript export.

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
