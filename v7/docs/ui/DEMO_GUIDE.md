# UI Demo Guide (V7.0.0)

## 5-minute demo flow
1. Open `http://localhost:8081`.
2. Ask one short question and show transcript + answer blocks.
3. Ask follow-up question to prove session memory.
4. Enable hands-free (`Auto-stop on silence`, optional auto-send).
5. Show protocol/transcript export controls and result.

## Presenter narrative
1. Hook:
   - "V7 is a fully isolated major line with clean port separation."
2. Experience:
   - live voice interaction with readable output and latency transparency.
3. Credibility:
   - Mongo persistence + admin-aware docs in-app.
4. Close:
   - "V7 scaffold is ready as a stable base for next roadmap items."

## Demo checks
- `/api/health` returns `{"status":"ok"}`.
- UI can `Record -> Stop -> Send`.
- Audio reply playback works via Piper sidecar.

## Troubleshooting
- If first request is slow, wait for model warmup and retry.
- If mic fails, verify browser microphone permissions.
