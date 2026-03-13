# CODEX_TASK_V9.1.7.md
Project: voice-agent
Version: V9.1.7
Branch: feature/v9.1.7-auto-upload-3b-sanitize
Base: current v9.x mainline (latest stable tag/branch used by team)

## Goal
Improve live usability and demo smoothness:
1) Customer voice recording should auto-upload immediately after recording stops (hands-free conversation feel).
2) Default Ollama model should be qwen2.5:3b (faster on MacBook Pro M1 16GB).
3) TTS should NOT speak markdown/control characters; sanitize only at the TTS callsite (low-risk isolated patch).

Must NOT break:
- Dual-lane language routing (agent/customer lanes)
- WS delivery stability
- Existing endpoints and DB schema
- Existing docs menu structure and rules

## Licensing & Commercialization Guardrails (MUST FOLLOW)
- Prefer permissive OSS licenses (MIT/Apache/BSD). Avoid GPL/AGPL in core.
- If a copyleft component is required (e.g., Piper), keep it isolated as an external sidecar (no linking/copying into core).
- Do not introduce new dependencies without checking license compatibility.
- Explicitly call out any license risk in PR notes.

## Artifact Policy (MUST FOLLOW)
- Test artifacts are generated under ./artifacts/ with timestamped subfolders.
- Keep only the latest 3 runs by default; older runs are deleted automatically by the test script.
- NEVER commit large artifacts into git. Only commit small text logs (summary + failing excerpts).
- Always produce:
  - artifacts/<ts>/SUMMARY.md
  - artifacts/<ts>/test-log-v9.1.7.txt
  - artifacts/<ts>/docker-logs-api.txt (tail)
  - artifacts/<ts>/docker-logs-web-agent.txt (tail)
  - artifacts/<ts>/docker-logs-web-customer.txt (tail)

## UX Requirements
### A) Customer: Auto-upload after recording stop
- When customer stops recording (manual stop or silence-stop if present), automatically call the existing /api/voice endpoint.
- Keep "Send" button as fallback (enabled when a blob exists), but default flow is auto-send.
- Add a user-visible toggle in Customer UI:
  - "Auto-send after recording" (default ON)
  - Persist in localStorage.
- If auto-send fails, show a clear error, keep the recorded audio playable, and allow manual Send retry.

### B) Default Model = qwen2.5:3b
- Default should be qwen2.5:3b for Ollama in:
  - API default model fallback (if env not set)
  - UI dropdown default selection (if model list contains it)
  - Compose defaults where appropriate
- Do NOT remove 7b; keep it selectable.

### C) TTS Markdown Sanitizer (low-risk, isolated)
- Implement sanitize_tts_text(text: str) in API backend.
- Apply it ONLY immediately before making TTS audio calls (piper or any TTS endpoint).
- Conservative rules:
  - Remove/neutralize markdown formatting tokens like **, *, _, backticks when used as formatting.
  - Normalize repeated whitespace/newlines.
  - Do not reorder content; do not translate; do not remove punctuation that changes meaning.
- Fail-safe:
  - If sanitizer errors, fall back to original text for TTS (do not abort request).

## Files / Components (expected)
- v9/docker/api/app.py
  - add sanitize_tts_text()
  - ensure default model fallback includes qwen2.5:3b
  - ensure dual-lane fields unchanged
- v9/web-customer/index.html (or current customer UI path)
  - auto-send toggle + implementation
  - default model selection prefers qwen2.5:3b
- compose files (only if needed)
  - keep ports stable, avoid orphan/port conflicts

## Documentation (MUST UPDATE EVERY RELEASE)
- Help menu structure MUST always be:
  1) Admin token speichern
  2) Help (User Documentation) — NOT Release Notes
  3) Demo Guide — at least 3 story-driven scenarios + 1 admin demo
  4) Admin Docs — install/start/tests/parameters/dirs/component checks (Whisper/Piper/DB/Ollama)
  5) Release Notes — full history from V7.0.0 to current
- Language rules:
  - If UI language = DE => show German docs
  - If UI language = EN => show English docs
  - All other UI languages => show English docs
- Docs must be written for a 16-year-old: clear, step-by-step, with examples.
- Update docs to mention:
  - Auto-send after recording (Customer)
  - Default model 3B rationale and switching
  - Sanitized TTS behavior (what gets removed and why)

## Definition of Done (DoD)
- Customer voice: record -> stop => automatically uploads and returns response (no manual click required) when toggle ON.
- Customer toggle OFF => old behavior preserved (manual send).
- Default model selection is qwen2.5:3b wherever possible.
- TTS speaks clean text without reading markdown markers in typical answers.
- Dual-lane translation correctness preserved (no regressions).
- Test suite produces artifacts and summary.
- Docs updated (DE/EN per rule) and menu structure verified.
- No new license risks introduced.

## Tests (Automate + Manual)
### Automated (Codex should run and store artifacts)
1) Smoke HTTP:
   - /api/health, /api/models
2) Dual-lane regression:
   - run existing v9 dual-lane tests (scenario1..3) and confirm PASS
3) Sanitizer unit-like checks:
   - Input: "**Wichtig**: *Bitte* prüfen `code`"
   - Expected sanitized: "Wichtig: Bitte prüfen code"
   - Ensure sanitizer does not remove numbers/IDs
4) Customer auto-send:
   - Simulate: customer UI logic should send request on stop event.
   - If full browser automation is heavy, add a small JS test harness function callable from console that triggers send() after stop with a mock blob, and log success/fail.

### Manual 2-minute proof checklist (must pass)
- Customer UI:
  - Toggle Auto-send ON
  - Record short sentence, press Stop => upload starts automatically, response appears
- Agent/Customer language:
  - Agent EN, Customer DE => translation visible correctly, TTS speaks correct lane
- Sanitizer:
  - Ask model to respond with a markdown list and bold words => spoken audio should not say "asterisk" or read raw markdown tokens.

## Output required from Codex
- PR-ready branch with commits.
- artifacts/<ts>/SUMMARY.md with PASS/FAIL per test block.
- artifacts/<ts>/test-log-v9.1.7.txt with commands executed and key excerpts.
- Release notes draft (DE+EN).