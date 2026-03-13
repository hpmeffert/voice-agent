# CODEX WORKORDER — V9.2.1 (Analytics/Reporting Module: KPIs + Dashboards + Export Pipelines)

Date: 2026-03-12
Base: develop/v9.1 (after v9.2.0 is merged)
Target branch: codex/feature/v9.2.1-analytics-dashboard

## Guardrails (must copy into every task)
### Licensing & Commercialization Guardrails
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core.
- Isolate copyleft as sidecar if needed, mark license risk.

### Artifact Policy
- Never commit artifacts.
- Write test outputs to `v9/artifacts/runs/<run-id>/`.
- Must pass `scripts/check_no_artifacts_tracked.sh`.

### Documentation Rules
- Help menu fixed structure:
  1) Admin Token speichern
  2) Help (User Doc)
  3) Demo Guide
  4) Admin Docs
  5) Release Notes (v7.0.0 -> current)
- Version visible in header and in help.
- Silence threshold default 1300ms.
- Explain docs like for a 16-year-old.
- Update docs each release with new features.

## Goal
Add an "Analytics/Reporting" module that is:
- opened via its own menu entry
- shown as popup/overlay (similar to docs UI)
- shows conversation KPIs and performance dashboards
- supports export pipelines (downloadable exports)
- uses thresholds with traffic light indicators (green/yellow/red)
- refreshable and/or auto-refresh (configurable)

## Scope
### 1) Data sources
Use the existing performance logs + metrics DB:
- compute aggregates:
  - avg/median/p95 for stt_ms, llm_ms, tts_ms, total_ms
  - WS RTT (avg/p95)
  - counts per time bucket (per minute/hour/day)
  - error rates (5xx, timeouts if present)
- retention already enforced elsewhere (do not change retention in this release)

### 2) UI module
- Add menu item "Analytics / Reporting" (visible to Admin only).
- Opens popup/overlay with scrollable sections:
  - KPI summary tiles (today/last 24h/last 7d)
  - time-series line charts for key metrics
  - thresholds:
    - green in norm
    - yellow near limit
    - red anomaly
- Provide refresh button and optional auto-refresh toggle (default OFF).
- No heavy JS frameworks; keep it lightweight (vanilla JS + simple chart lib only if permissive license; otherwise implement minimal SVG/Canvas charts yourself).

### 3) Threshold configuration
- Read thresholds from Admin Settings (DB).
- Provide defaults if not set.
- Document every KPI and how it is computed.

### 4) Export pipelines
- Allow exporting aggregated data:
  - JSON
  - CSV
  - optionally Markdown summary
- Exports must be generated server-side and downloaded via endpoint.
- Exports must not be committed.

## Endpoints
Add admin-only endpoints:
- GET `/admin/analytics/summary?range=24h|7d|30d`
- GET `/admin/analytics/timeseries?metric=stt_ms|llm_ms|tts_ms|total_ms|ws_rtt_ms&bucket=5m|1h|1d&range=...`
- GET `/admin/analytics/export?range=...&format=csv|json`

## Tests
- Add `scripts/run_v9_2_1_analytics_tests.sh`
  - starts stack (or assumes running)
  - hits endpoints
  - validates response schemas
  - writes artifacts + a `SUMMARY.md`
- Add UI smoke that:
  - ensures menu exists
  - popup opens
  - at least one chart renders
  - refresh works

## Documentation
- Update Admin Docs (DE/EN) with:
  - what KPIs mean
  - thresholds and impact
  - how to use exports
- Update Demo Guide with at least one Analytics story scenario
- Update Release Notes (DE/EN)

## DoD
- Analytics popup works in Admin UI
- Endpoints return data with sane defaults
- Exports download successfully
- Tests PASS and create traceable SUMMARY artifact
- No artifacts committed, licensing guardrails respected