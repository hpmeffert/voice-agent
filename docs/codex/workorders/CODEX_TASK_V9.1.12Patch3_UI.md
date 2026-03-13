# CODEX_TASK_V9.1.12_PATCH3_UI.md
Project: voice-agent
Release: v9.1.12 Patch 3 (UI Patch)
Scope: Admin Client UX – show opened session conversation transcript in left panel (below Spoken reply), dual-lane rendering.

## 0) NON-NEGOTIABLE GUARDRAILS (Licensing & Commercialization)
- Prefer permissive OSS (MIT/Apache/BSD/ISC).
- Avoid GPL/AGPL inside the core repo/runtime where it would contaminate commercialization.
- If a copyleft component becomes unavoidable: isolate it as an external sidecar service and clearly mark license risks.
- Do NOT add new UI libraries or dependencies unless strictly necessary; if needed, only permissive licenses and document them.

## 1) Documentation Quality Rules (MUST for every change)
- Help menu structure is FIXED and must NEVER regress:
  1) **Admin token speichern**
  2) **Help** → User Documentation (NOT release notes)
  3) **Demo Guide** → ≥ 3 story-based demo scenarios + 1 admin demo
  4) **Admin Docs** → install/start/config/tests/dirs/component checks (Whisper/Piper/DB/Ollama etc.)
  5) **Release Notes** → complete history from V7.0.0 to current
- Version + release must be visible:
  - In page header AND in Help menu (all clients: admin/agent/customer).
- Standard silence threshold remains **1300 ms**.
- All docs written so a **16-year-old** can follow.

## 2) Artifact Policy (Tests & Logs)
- Keep test artifacts under: `v9/artifacts/<timestamp>/...`
- DO NOT commit large artifacts to git.
- Provide a short `SUMMARY.md` + `test-log-*.txt` in the artifact folder.
- Provide a script (or re-use existing) to collect logs and zip them: `artifacts.zip`
- For PR: keep only lightweight logs or references; heavy artifacts remain local.

## 3) Goal of Patch 3
In the **Admin Client**, after a search result is opened via **Open Session**, render the **entire conversation history** in a scrollable panel on the **left side below "Spoken reply (Piper)"**.

Requirements:
- Must render “full conversation” = all messages in the session (latest first or chronological – choose one consistent with admin UX; recommend chronological top→bottom).
- Must show **Dual-Lane** if present:
  - Show **Original** (source language) and **Translation** (target language) in separate blocks.
  - If translation not present, show only the available text (but format consistently).
- Must wrap long lines (no horizontal scrolling).
- Must NOT break:
  - existing admin search
  - existing Open Session behavior
  - existing WS “connected” indicators
  - existing metrics panels

## 4) UI Layout Target (Admin Client)
Current admin UI already has left area with:
- Captured audio
- Spoken reply (Piper)

Add below Spoken reply:
- New panel: **Conversation (Session History)**
  - Scrollable (vertical)
  - Shows messages with role badges (CUSTOMER / AGENT / SYSTEM)
  - Each message block:
    - Timestamp (if available)
    - Role label
    - If dual-lane fields exist:
      - Box A: Original (lang)
      - Box B: Translation (lang)
    - If only one text:
      - single box
- Keep admin controls ergonomically left/center; avoid forcing right scrolling.

## 5) Data Source & Integration
When admin clicks “Open Session” from search results:
- Fetch session history using existing endpoint (or existing API path used by agent view):
  - Example: `GET /api/session/{session_id}?user_id=<...>&limit=<...>` or admin variant.
- If admin is allowed to view any session without user_id constraints, ensure the call works with admin privileges (demo-admin default).
- Store the loaded history in UI state and render into the new panel.

Important:
- Re-use existing renderer/helpers if they exist (e.g., `renderMarkdown`, `renderMessage`, dual-lane formatting already used in agent).
- Avoid duplicating logic 3x; prefer shared helper functions in the admin HTML file.
- Keep it simple: vanilla JS, no new frameworks.

## 6) Dual-Lane Rendering Rules (MUST)
For each message:
- If message is from CUSTOMER:
  - Prefer:
    - `text_original` (or `original_text`) + language field (e.g. `lang_original`)
    - `text_for_agent` / `text_translated` / `translated_text` + `lang_for_agent`
- If message is from AGENT:
  - Prefer:
    - agent original text (agent language)
    - customer-facing translated text (customer language)
- If fields are inconsistent across DB vs WS:
  - Use best-effort mapping:
    - `text_original` OR `original` OR `content`
    - `text_for_agent` OR `text_translated`
    - `text_for_customer` for agent replies when displayed in admin
- IMPORTANT:
  - Do not show raw JSON with `\n` escapes.
  - Render Markdown nicely (like in agent) but ensure TTS sanitizing is not part of this patch.

## 7) Styling / UX
- Add CSS for the new panel:
  - fixed max-height (e.g. 280–420px)
  - `overflow-y: auto`
  - word wrapping: `white-space: pre-wrap; word-break: break-word;`
- Use the same “message bubble” style already present.

## 8) Implementation Steps (Suggested)
1) Locate Admin Client HTML:
   - likely `v9/web-admin/index.html` (or similar path).
2) Add a new DOM section:
   - `<div id="adminConversationPanel"> ... </div>`
3) Add JS state:
   - `let openedSessionHistory = []`
4) Extend the existing “Open Session” click handler:
   - after it sets session_id, call `loadSessionHistory(sessionId)`
5) Implement `loadSessionHistory(sessionId)`:
   - fetch JSON
   - store result
   - call `renderSessionHistory()`
6) Implement `renderSessionHistory()`:
   - clear panel
   - for each message, build DOM:
     - role label + timestamp
     - dual-lane blocks (original + translation) if present
7) Ensure wrap & scroll.

## 9) Tests (MUST) + Test Artifacts
### Automated UI Smoke (no new deps)
- Extend existing UI smoke script (or add a minimal script) to:
  1) Start stack
  2) Call admin search endpoint (if exists) or open admin page is optional
  3) Trigger Open Session via HTTP if available, else call session API directly
  4) Verify HTML contains the new panel element id

### Manual 2-minute Proof (required)
Record a small test protocol in `v9/artifacts/<ts>/test-log-v9.1.12-p3.txt`:

1) Start stack.
2) Open Admin Client.
3) Search for `wallbox*` (mode auto) and click “Open Session”.
4) Expected:
   - New panel “Conversation (Session History)” shows messages.
   - For CUSTOMER messages: Original + Translation blocks if available.
   - No horizontal scroll; text wraps.
   - Scroll works.

### Output files
- `v9/artifacts/<ts>/SUMMARY.md` must include:
  - RESULT: PASS/FAIL
  - Key evidence (session id, screenshot filename optional, notes)
- Zip command included in summary (do not commit zip).

## 10) Definition of Done (DoD)
- Admin search still works.
- “Open Session” loads session history and renders in the new left panel.
- Panel is scrollable and wraps text.
- Dual-lane displayed when available (Original + Translation).
- Version is still visible in header + help.
- UI smoke PASS and manual proof PASS.
- No new non-permissive dependencies.
- No large artifacts committed.

## 11) Branch / PR Instructions
- Branch name:
  - `codex/feature/v9.1.12-p3-admin-conversation-panel`
- Commit structure (small & reviewable):
  1) UI panel + CSS
  2) loadSessionHistory + render logic
  3) tests + artifacts summary template update (no large artifacts)
- Provide PR description with:
  - What changed
  - How to test (manual 2-min proof)
  - Known limitations

END.