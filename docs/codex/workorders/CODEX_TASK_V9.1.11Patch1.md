# CODEX TASK — V9.1.11 — Admin UI Ergonomie & Layout Fixes

## Goal
Improve Admin Client usability/ergonomics:
- Admin page width aligned with Agent page (no horizontal scrolling to reach controls).
- Admin parameters displayed as a clean panel (similar behavior as Agent panel), but in Admin Client.
- Prevent controls from drifting off-screen to the right.
- Wrap long text in Admin Perf Logs so the panel stays readable.
- Keep search always visible.

## Non-goals
- No functional changes to Dual-Lane routing logic (customer/agent lanes).
- No breaking changes to existing endpoints.
- No new external deps unless permissive license (MIT/Apache/BSD). Avoid GPL/AGPL in core.

## Critical Guardrails (Licensing & Commercialization)
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core repo.
- If a component is copyleft (e.g., Piper variants), keep it as isolated sidecar container and never link/merge into core.
- If any license risk is detected, STOP and flag it in PR notes.

## UX Requirements (Admin Client)
### 1) Page width & layout
- Admin client should match Agent layout width (same container width).
- No right-drifting buttons that require horizontal scroll.
- Controls and panels must be reachable at common laptop widths (e.g., 1440px).

### 2) Admin settings panel behavior
- Show admin parameters in a structured panel (drawer/popup/section), but:
  - In Admin Client: default visible is OK, but must be collapsible (toggle).
  - Use dropdowns/toggles wherever possible to prevent invalid input.
- Search bar must remain visible in header at all times.

### 3) Admin metrics display
- Ensure metrics/JSON blocks wrap: NO endless single-line JSON.
- Use `pre-wrap` / `word-break` CSS to avoid wide overflow.
- Keep a compact “headline summary” with key avg metrics at top (if already available).

### 4) Version visibility
- Admin header must show: "Admin Client" + exact version (e.g., v9.1.11).
- Version must also appear in Help menu and Help header.

## Documentation Rules (MUST)
The Help menu structure must ALWAYS be:
1) Admin Token speichern
2) Help (User Guide) — user documentation ONLY, not release notes
3) Demo Guide — at least 3 story-driven scenarios
4) Admin Docs — install/start/config/tests/components checks
5) Release Notes — full history from V7.0.0 → current version

- Docs must be readable for a 16-year-old (clear, step-by-step, examples).
- All new features in this version must update: User Guide, Demo Guide, Admin Docs, Release Notes.
- For DE/EN docs switching: if UI language is DE => show DE docs; if EN => show EN docs; otherwise show EN.

## Tests (Must run + produce artifacts)
### Automated UI smoke
- Start stack
- Open Admin client page
- Verify: controls visible without horizontal scroll (basic DOM checks ok)
- Verify: long metrics text wraps (CSS computed style or simple visual screenshot saved)

### Test artifacts policy
- Save all run artifacts under: `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- Include: docker logs (api/web-agent/web-customer/web-admin/piper), env snapshot, summary.md, test-log.txt
- Old artifacts are not committed. Only commit a short SUMMARY.md + test-log file in repo (if you already do this).
- Ensure a cleanup step exists (do not accidentally commit huge logs/zips).

## Deliverables
- PR-ready branch: `codex/feature/v9.1.11-admin-ui-ergonomics`
- Updated admin UI files
- Updated docs (DE/EN)
- Test artifacts + SUMMARY