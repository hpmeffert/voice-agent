# CODEX TASK — Voice Agent V6.2.0 (Mac-first, Mongo, CRM transcript payload)

## 🚨 Licensing & Commercialization Guardrails (MUST FOLLOW)

Goal: This project must remain commercially distributable by Topcom/LEKAB without forcing source disclosure.

### Allowed licenses for core code (preferred)
- MIT, Apache-2.0, BSD-2/3, ISC (permissive)

### Restricted / default-deny for core integration
- GPL, AGPL (strong copyleft) → DO NOT integrate into core codebase
- LGPL (weak copyleft) → avoid by default; only acceptable with explicit approval and clean dynamic-linking compliance

### “Sidecar rule” for copyleft or unclear license
If a component is GPL/AGPL/LGPL or license is unclear:
- DO NOT embed, vendor, or link it directly into the core application.
- Implement it as an external sidecar service (Docker container / separate process) accessed via HTTP/gRPC.
- Keep binaries/models outside the repo (no .onnx/.gguf weights, no large model files).
- Document in PR: component name, license, and isolation approach.

### Dependency hygiene (mandatory in PR)
- For every new dependency: record name + license in PR notes (or /docs/licenses.md).
- Prefer alternatives with permissive licenses if available.
- Never commit secrets (.env, API keys). Ensure .gitignore covers these.

If unsure: STOP and ask for explicit guidance before proceeding.

## Goal
Implement **V6.2.0** on top of **tag `v6.1.0`** with the focus on:
1) Mongo-backed persistence **stable + testable**  
2) **CRM-ready structured transcript payload** + export templates  
3) zero regressions in Docker/Compose (avoid orphan/port pitfalls)

> IMPORTANT: V7.x will handle the full “hands-free listening loop”. Do **not** implement that in V6.2.0.

---

## Repo/Branch rules
- New branch: `feature/v6.2.0-crm-transcript`
- Keep all V6 work **strictly inside** `v6/` (no runtime changes to V5 paths).
- Compose must be runnable from repo root with deterministic project dir:
  - `docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build`
- Avoid hard-coded global container names; use compose project scoping.
- No new host-level dependencies.

---

## Functional requirements (V6.2.0)

### A) Structured transcript payload (CRM-ready)
Add/extend export functionality so a session can be exported as a structured payload suitable for CRM ingestion.

#### Endpoint
- `GET /api/session/{session_id}/export`
  - query params:
    - `user_id` (required)
    - `format=json|md`
    - **NEW** `template=default|crm`
    - `include_meta=1|0`
    - `limit` (default 200, hard-cap 500)
- Behavior:
  - `template=crm` returns JSON (content-type `application/json`)
  - Use `Content-Disposition` filename: `session_<session_id>_crm.json`

#### CRM JSON schema (minimum)
```json
{
  "schema_version": "1.0",
  "exported_at": "ISO-8601",
  "tenant": "default",
  "user": { "user_id": "..." },
  "session": {
    "session_id": "...",
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601",
    "language": "de|en|...",
    "backend": "ollama|openai",
    "model": "qwen2.5:7b|gpt-5|...",
    "tags": ["optional"]
  },
  "summary": {
    "title": "short subject (heuristic)",
    "short_summary": "3-6 concise sentences",
    "sentiment": "neutral|positive|negative|unknown",
    "action_items": [
      { "text": "…", "owner": "user|agent|unknown", "due": null }
    ]
  },
  "transcript": [
    { "t": "ISO-8601", "role": "user|assistant", "text": "..." }
  ],
  "raw": {
    "messages_count": 12,
    "audio": { "input_format": "webm|wav|...", "stt_model": "small", "stt_compute": "int8" }
  }
}
```

Notes:
- Produce `summary` via selected backend/model (cheap: cap tokens/num_predict).
- If summary generation fails, still return transcript and set `sentiment="unknown"`.

### B) MongoDB hardening
- Ensure indexes exist (idempotent):
  - TTL indexes (`expires_at`) for `messages`, `sessions`
  - Index: `messages.session_id + t`
  - Index: `sessions.user_id`
- Fix update conflicts:
  - `updated_at` only in `$set`
  - `created_at` only in `$setOnInsert`

### C) Markdown export improvements
For `format=md` + `template=crm`, output a readable “CRM note”:
- Session meta header
- Summary + action items
- Timestamped transcript

### D) Validation & ownership
- Reject export if session not owned by `user_id` (403)
- Keep/maximize input validation:
  - `MAX_AUDIO_BYTES`, `MAX_TEXT_CHARS`

---

## Files to change (expected)
- `v6/docker/api/app.py`
- `v6/docker/api/requirements.txt` (prefer stdlib; add only if truly needed)
- `v6/docs/TEAM_QUICKSTART_V6_MAC.md` (add export usage)
- `v6/web/index.html` (optional: add export buttons)

---

## Acceptance tests
1) Bring up stack:
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

2) Create a session (UI or curl), then export CRM JSON:
```bash
curl -s "http://localhost:8080/api/session/<ID>/export?user_id=<UID>&format=json&template=crm&include_meta=1" | jq .
```

3) TTL fields exist on inserted docs; delete endpoints still work.

---

## Deliverables
- Branch `feature/v6.2.0-crm-transcript`
- Updated docs
- Draft release notes using `/RELEASE_NOTES_TEMPLATE.md`
