# CODEX TASK — V9.1.12 Patch 2
## Title
Customer Client: Help (❓) + UI Language Dropdown + DB-backed UI translations + persisted preference

## Context
We have 3 browser UIs (admin, agent, customer). In this patch we improve the **Customer UI** usability:
- Add a **Help button (❓)** with a dedicated Customer Help page/modal describing voice/chat usage step-by-step.
- Add a **UI language dropdown** for the Customer UI labels (NOT the spoken customer language, NOT TTS language).
- Store UI language preference per user in DB (and keep localStorage fallback).
- Store UI translation strings in DB so we can extend languages without code changes.

Important: This is **UI text language**, independent from:
- detected customer language (input language)
- TTS output language
- translation lanes logic

We will roll DB-driven UI translations for agent/admin later (planned V9.1.16). For now implement for Customer UI only, but design schema reusable.

## Must-have Requirements
1) Customer UI Help (❓)
- Add a visible Help icon/button in header (top bar).
- Clicking opens a Help view (modal/drawer or dedicated section) containing:
  - What the customer client is
  - Step-by-step “Voice mode” flow
  - Step-by-step “Chat mode” flow
  - Explanations of toggles: speak on/off, auto-send-after-silence, etc.
  - Explain “silence threshold 1300ms” in simple language (16-year-old level).
- The Help content must be available in **EN and DE** at least.
- Help should render as **formatted Markdown** (NOT a single serialized line).
- For Customer UI: if UI language is `de` show German help; if `en` show English help; for any other UI language show English help.

2) Customer UI language dropdown (UI labels only)
- Add a dropdown in header allowing to change UI language for Customer UI labels.
- Default UI language:
  - from DB preference if exists
  - else from localStorage
  - else from config default (env/config)
  - else fallback `en`
- On change: update labels dynamically (no refresh required).
- Save preference:
  - store to localStorage immediately
  - and persist to DB via API endpoint (best-effort; UI still works if DB is unreachable).

3) DB-backed translation strings
- Introduce Mongo collection for UI strings, e.g. `ui_i18n_strings`.
- Structure example:
  - { scope: "customer", key: "btn_record", lang: "en", text: "Record" }
  - { scope: "customer", key: "btn_record", lang: "de", text: "Aufnehmen" }
- Provide a small seed set for customer UI:
  - header/title labels
  - button texts
  - toggle labels
  - status texts (Idle/Recording/Uploading/…)
  - help menu labels
- Provide API endpoint to fetch i18n strings:
  - GET /i18n?scope=customer&lang=de
  - Returns { lang, scope, strings: { key: text, ... } }
- Implement caching in API for performance (in-memory cache with TTL e.g. 60s) to avoid DB query per render.

4) DB-backed user preferences
- Introduce collection `user_prefs` (or reuse existing users collection if present, but keep it clean).
- Must store:
  - user_id
  - customer_ui_lang (e.g. "en", "de", …)
  - updated_at
- Provide endpoint:
  - POST /prefs/ui_lang
    body: { user_id, scope:"customer", ui_lang:"de" }
  - Validate ui_lang is allowed (at least en/de; allow future languages if strings exist).
- Make sure demo user stays admin elsewhere (do not add real auth here).

## Non-goals (Explicit)
- Do not change translation lane algorithms (dual-lane).
- Do not change TTS language selection.
- Do not add real authentication/user management (planned v14.x).
- Do not implement agent/admin UI DB-i18n in this patch (plan for v9.1.16).

## UX Rules
- Header shows version consistently:
  - In page header AND in help menu area.
- Customer Help is accessible via ❓ icon, and must be readable (proper headings, lists, spacing).
- UI language dropdown affects:
  - label texts
  - help content language
  - not the chat content language itself (messages remain as-is)

## Security & Reliability
- Input validation for endpoints.
- No secrets in client code.
- Graceful failure: If i18n fetch fails, fallback to built-in English strings.

## Open-Source / Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL inside core.
- If any copyleft component is required, isolate it as an external sidecar service.
- Mark license risks explicitly in docs/notes.
- For this patch: do NOT add any new dependency with unclear license. If you consider adding a library, verify license and document it.

## Artifact Policy (MANDATORY)
- Create artifacts under: v9/artifacts/<timestamp>/
- Keep only the latest 3 runs by default; older runs can be zipped or deleted (configurable).
- Artifacts must include:
  - SUMMARY.md (PASS/FAIL, timings, environment)
  - docker logs (api/web-customer/web-agent/web-admin/piper if relevant)
  - minimal http/ws traces if used
- Do not commit huge artifacts to git unless explicitly requested; store locally and summarize in SUMMARY.md.

## Implementation Plan
A) API
1. Add Mongo collections:
   - ui_i18n_strings
   - user_prefs
2. Implement:
   - GET /i18n?scope=customer&lang=xx
   - POST /prefs/ui_lang
3. Add seeding logic:
   - On startup, ensure i18n keys exist for customer scope for en/de.
   - Do NOT overwrite if already present (idempotent).
4. Cache:
   - In-memory cache key: (scope, lang) -> dict(strings)
   - TTL 60 seconds; invalidate on prefs set optional.

B) Customer UI
1. Add UI language dropdown to header:
   - Values: at least ["en","de"], future-ready.
   - Load preference:
     - from DB (optional fetch once on load, best-effort)
     - else localStorage
2. Add ❓ help button:
   - Opens modal/drawer.
   - Content is Markdown rendered (use existing safe markdown renderer if present; otherwise implement minimal safe markdown -> HTML).
3. Apply strings dynamically:
   - Introduce i18n mapping: key -> element text
   - On language change: re-render labels and help content
4. Persist preference:
   - localStorage
   - POST /prefs/ui_lang

C) Docs
- Update release notes for v9.1.12 Patch 2 in DE and EN.
- Ensure Help menu structure rules remain consistent.
- Add small demo guide snippet: “Customer changes UI language while speaking another language; system remains correct.”

## Tests
1) Automated smoke tests (scriptable)
- Start stack
- GET /api/health, /api/i18n?scope=customer&lang=en, /api/i18n?scope=customer&lang=de
- Set ui_lang preference via POST /prefs/ui_lang; re-fetch and verify response
2) Browser manual checklist (2 minutes)
- Open customer UI
- Switch UI language DE -> labels and help change to DE
- Switch UI language EN -> labels and help change to EN
- Confirm chat/voice language behavior unaffected (speak DE while UI labels EN; still works)
3) Logging
- Write SUMMARY.md with PASS/FAIL and include screenshots optional references

## DoD
- Customer UI has ❓ help button, shows formatted Markdown in EN/DE.
- Customer UI language dropdown works, persists preference, dynamic update without refresh.
- i18n strings stored in DB and retrievable via API.
- No changes to dual-lane logic or TTS routing.
- All tests green; artifacts generated.