# UI Demo Guide (V7.1.0)

## 5-minute demo flow
1. Open `http://localhost:8081`.
2. Ask one short question and show transcript + answer blocks.
3. Ask follow-up question to prove session memory.
4. Enable `Listen Mode` and run one full hands-free turn:
   - speak
   - pause
   - show auto-stop + auto-send + auto-resume after speech playback
5. Refresh browser and prove settings persisted (`Listen Mode` + thresholds restored).
6. Show protocol/transcript export controls and result.

## Presenter narrative
1. Hook:
   - "V7 starts cleanly isolated and now reaches true hands-free flow."
2. Experience:
   - live voice interaction with natural turn-taking and zero button clicks during the loop.
3. Credibility:
   - Mongo persistence for sessions, messages, and per-user listen settings.
4. Close:
   - "V7.1.0 gives us a stable, demo-ready base for production conversation UX."

## Demo checks
- `/api/health` returns `{"status":"ok"}`.
- UI can run full `Listen Mode` loop.
- Audio reply playback works via Piper sidecar.

## Troubleshooting
- If first request is slow, wait for model warmup and retry.
- If mic fails, verify browser microphone permissions.
