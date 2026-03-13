# Voice Agent – Standard Test Runbook (applies to every release)
Version: <fill by release, e.g. v9.1.16>
Date: <YYYY-MM-DD>
Owner: <name>
Scope: Admin (8085), Customer (8086), Agent (8087)

## Goals (Definition of “green”)
This runbook proves (in <5 minutes):
1) Stack boots cleanly (health endpoints OK)
2) Dual-Lane works for Chat + Voice:
   - Customer -> Agent: Agent sees Original + Translation (agent language)
   - Agent -> Customer: Customer sees/hears in customer language
3) WS live events arrive (no "refresh required")
4) Help menu structure is correct and docs are not empty
5) Silence threshold default is 1300ms
6) Search works (admin + agent where applicable)
7) No artifacts were committed

---

## Preconditions
- Repo branch: <develop/v9.1 or release/v9.1>
- Docker running
- Ports in use:
  - Admin: 8085
  - Customer: 8086
  - Agent: 8087
- ENV: ensure local .env is present and valid (no secrets in repo)

---

## A) Boot / Health (Automatable)
### A1: Start stack
Command:
- (example) `docker compose -f v9/docker/compose.dev.yml up -d --build`

### A2: Health endpoints
Expected: status ok + correct version on all ports.
Commands:
- `curl -s http://localhost:8085/api/health`
- `curl -s http://localhost:8086/api/health`
- `curl -s http://localhost:8087/api/health`

PASS if:
- `"status":"ok"` and `"version":"<release>"` matches all 3.

---

## B) Dual-Lane – Manual Browser Proof (Required)
### B1: Open UIs
- Admin:    http://localhost:8085
- Customer: http://localhost:8086
- Agent:    http://localhost:8087

### B2: Setup toggles
Agent (8087):
- Agent UI Language: `en`
- Incoming speak: ON (optional for proof)
- Customer output on agent: OFF
- Auto-refresh: ON
Customer (8086):
- Customer UI Language: `de`
- Customer speak: ON

### B3: CHAT test (must pass)
1) Customer types German text in chat:
   - "Meine Wallbox geht immer aus. Was kann ich tun?"
2) Expected on Agent:
   - Original block in DE
   - Translation block in EN (visible)
   - If Incoming speak ON: Agent voice speaks EN only
3) Agent types English reply:
   - "Please check the breaker and power cycle the wallbox. What model is it?"
4) Expected on Customer:
   - Reply shown in DE (translated)
   - Customer speaks DE (if enabled)

PASS/FAIL notes:
- <fill>

### B4: VOICE test (must pass)
1) Customer speaks German (short sentence) and stops speaking.
2) Expected:
   - Upload auto-starts after recording stops (if feature enabled)
   - Agent shows Original DE + Translation EN
   - Agent hears EN only (if Incoming speak enabled)
3) Agent replies in English (chat)
4) Customer sees/hears German.

PASS/FAIL notes:
- <fill>

---

## C) Help Menu & Docs (Manual quick check, Required)
### C1: Help menu structure must be EXACTLY:
1) Admin token speichern
2) Help (User Documentation)
3) Demo Guide
4) Admin Docs
5) Release Notes (history from V7.0.0 to current)

PASS if:
- Each menu item loads content (not empty)
- Markdown is rendered formatted (not one long line)
- Version is visible in header + help

---

## D) Silence Threshold Default
PASS if:
- Default silence threshold = 1300ms (visible or in config)
- Voice flow stops on silence reliably

---

## E) Search (Admin & Agent)
### E1: Admin search
- Search input supports wildcard `*` suffix:
  - `wallbox*`
  - `fe77*` (partial user_id/session_id)
PASS if:
- Results show sessions + context
- Clicking result opens session and shows full conversation (original + translation)

### E2: Agent search (if present)
- Same rules as admin
PASS if:
- Finds by session_id/user_id/text fragments

---

## F) Artifact Hygiene (Automatable)
PASS if:
- No artifacts/logs/exports are committed
- Any generated artifacts are stored under artifacts/ (ignored by git)

---

## G) Attachments / Evidence
Attach:
- `SUMMARY.md`
- `docker-logs-*.txt`
- `ENV_SNAPSHOT.txt` (no secrets)
- `test-log-<release>.txt`
- optional screenshots