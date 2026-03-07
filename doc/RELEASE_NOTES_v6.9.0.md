# Voice Agent v6.9.0

Date: 2026-03-07  
PR: #TBD  
Base Branch: `release/v5.4-azure-stable`

## Summary
Adds protocol template v1 with repo-owned MIT template and runtime path override.

## Highlights
- New template file: `v6/templates/protocol_template.md` (repo-owned, text/markdown only).
- New endpoint: `GET /api/export/protocol?user_id=...&session_id=...`.
- New env config: `PROTOCOL_TEMPLATE_PATH` (default `/app/templates/protocol_template.md`).
- Runtime override possible via mounted template path (no code change required).

## Scope and Compatibility
- Changes are isolated to `v6/` plus release notes.
- Existing protocol endpoint `/api/protocol/{session_id}` remains available.
- No new services and no port changes.

## Validation
```bash
docker compose -f v6/docker/compose.dev.yml up -d --build
curl -L -o protocol_v1.md "http://localhost:8080/api/export/protocol?user_id=<USER_ID>&session_id=<SESSION_ID>"
```

Override test:
```bash
PROTOCOL_TEMPLATE_PATH=/runtime-templates/protocol_template_custom.md \
docker compose -f v6/docker/compose.dev.yml up -d --build api
curl -L -o protocol_v1_custom.md "http://localhost:8080/api/export/protocol?user_id=<USER_ID>&session_id=<SESSION_ID>"
```

## Licensing / Commercialization Note
- No new runtime dependencies.
- Template is repo-authored and MIT-owned (no external assets/code copied).
