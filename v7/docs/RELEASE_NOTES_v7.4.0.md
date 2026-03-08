# Release Notes v7.4.0

## Highlights
- CRM transcript export is now centered on repo-owned MIT templates in `v7/templates/exports/`.
- Export flow remains stable for both Markdown and JSON output.

## Added
- New export template folder:
  - `v7/templates/exports/transcript_default.md.tpl`
  - `v7/templates/exports/transcript_default.json.schema.json`
- Template usage guide:
  - `v7/templates/exports/README.md`

## Changed
- API default `CRM_EXPORT_TEMPLATE_MD` now points to:
  - `/app/templates/exports/transcript_default.md.tpl`
- Compose default updated to the same path.

## Fixed
- Removed ambiguity around template lookup paths for CRM markdown export.

## Ops / Deployment Notes
- Start:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- Download export:
  - `curl -L -o transcript.md "http://localhost:8081/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=md"`
  - `curl -L -o transcript.json "http://localhost:8081/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=json"`
