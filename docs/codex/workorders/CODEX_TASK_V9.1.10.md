# CODEX_TASK_V9.1.10 — UI Role Separation + Admin Console parity + Dual-Lane Always

## Context
We are working on the Voice Agent platform (v9 tree). Current status: v9.1.9 is PASS (dual-lane live + history works after recent fixes).  
However, we need to correct role separation: the Admin Panel/drawer was added to the Agent Client, but we need:
- Agent Client: only **agent-relevant** settings (no global admin settings)
- Admin Client: the place for **global admin settings** and **admin metrics summary**, plus search tooling.

We must keep licensing/commercialization guardrails (MIT/Apache/BSD preferred, avoid GPL/AGPL in core, isolate copyleft as sidecars). No new license traps.

## Goals (V9.1.10)
1) **Agent Client UI cleanup**
   - Keep header always visible:
     - Left: "Voice Agent Agent Client vX.Y.Z", WS status, Version badge
     - Middle/Right: unified Search field + filter dropdown (auto | session_id | user_id | text)
     - Right: "Agent Settings ⚙︎" toggle (NOT full Admin)
   - Agent Settings Drawer contents (agent-scoped only):
     - backend/model selection (only affects this agent UI behavior or request params)
     - agent language selection
     - toggles: Incoming speak, customer speak on agent, show/hide debug panels, show/hide perf metrics
     - local actions: reset current view/session selection, clear local storage (agent only)
   - Remove/disable any **global admin** settings controls from Agent Client.

2) **Admin Client gets the real Admin Panel**
   - Admin UI must have:
     - same performance summary badges in the header area (avg/p95 STT/LLM/TTS/Total) as currently shown in Agent UI
     - Admin Settings panel (global):
       - All admin-configurable parameters must be visible here and documented in Admin Docs
       - Settings are persisted in DB (existing pattern from v9.1.8)
       - Show Save / Cancel / Close
     - Admin search: unified single input supports wildcard `*` at end and filter dropdown:
       - auto | session_id | user_id | text
       - results show sessions + snippet context; click loads session history
     - Ensure Admin-only endpoints are used from Admin client (not exposed in Customer UI)
   - During testing: demo user is admin (no real user management until v14).

3) **Dual-Lane Always**
   - Ensure agent view renders dual-lane consistently:
     - Live WS events: show Original + Translation when present
     - History after reload: must also show Original + Translation
   - If DB records do not have lane fields for older messages, do NOT break; show best effort:
     - If lane fields missing, show only original (but do not regress current behavior)
     - Avoid expensive on-demand translation calls unless explicitly required (keep this release low risk)

4) **Version consistency**
   - All UIs (admin, agent, customer) must show exact same `v9.1.10` in:
     - page header
     - Help menu "Version" line
   - No mismatching versions across clients.

5) **Docs discipline (DE/EN)**
   - Keep the help menu structure stable:
     1) Save Admin Token
     2) Help (User Guide) — NOT Release Notes
     3) Demo Guide — min 3 story-driven scenarios
     4) Admin Docs — install/start, config, testing routines, directories, component checks (Whisper/Piper/DB/Ollama), parameters
     5) Release Notes — full history from V7.0.0 to current
   - For DE/EN switching: if UI language is DE => show German docs; if EN => show English docs; other languages => show English docs.
   - Update docs to reflect V9.1.10 changes.

6) Defaults
   - Silence threshold default remains 1300ms (do not change).

## Non-Goals
- No new authentication/user management (planned for v14)
- No large refactor of translation pipeline
- No new external dependencies unless necessary; prefer stdlib

## Deliverables
- Code changes committed on a new branch: `codex/feature/v9.1.10-admin-agent-separation`
- Updated docs (DE/EN) with above menu structure
- Updated smoke tests + quick browser proof steps
- Test artifacts captured under `v9/artifacts/<timestamp>/` (see policy below)

## Artifact Policy (must follow)
- Keep artifacts under `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- Include: SUMMARY.md, ENV_SNAPSHOT.txt, docker-logs-*.txt, ws_agent_events.jsonl, ws_customer_events.jsonl, test-log-*.txt
- Do NOT commit large artifacts by default.
  - Commit only SUMMARY.md + small test-log file if needed.
  - Zip full artifacts optionally but keep untracked unless explicitly requested.
- Update `.gitignore` or repo policy docs if required.

## Tests (Codex must run and record)
### A) UI Smoke
- Start stack
- Open Admin/Agent/Customer pages
- Verify version string `v9.1.10` appears in header + help menu
- Verify Agent Settings drawer exists and contains only agent-scoped controls
- Verify Admin Console shows global settings panel + performance badges

### B) Dual-Lane Proof (2 min)
Scenario: Customer DE (Voice) -> Agent EN; Agent EN (Chat) -> Customer DE
- Agent: language=en, Incoming Speak ON, Customer output on agent OFF, Auto-refresh ON
- Customer: language=de, Customer speak ON
Assertions:
- Agent sees CUSTOMER message with two blocks: Original(de) + Translation(en)
- Optional: Agent speaks EN lane only (if enabled)
- Customer receives agent reply spoken/seen in DE
Record result in `test-log-v9.1.10.txt`

### C) Search
- In Admin client search using:
  - session_id fragment with wildcard like `fe774f*`
  - text fragment search (e.g. "Wallbox")
- Ensure results list appears and clicking loads the session history.

## Commands
Provide exact commands in SUMMARY.md:
- how to run stack
- how to run automated probes/scripts (if any)
- where artifacts are stored

## DoD (Definition of Done)
- All tests A/B/C PASS
- No regression in existing dual-lane behavior
- Admin settings are not exposed in Agent Client
- Docs not empty; menu structure correct; DE/EN switching works
- No new licensing risks introduced

## Notes
If any conflict arises (e.g., older DB messages missing lane fields), handle gracefully without breaking current flows. Prefer minimal safe changes.