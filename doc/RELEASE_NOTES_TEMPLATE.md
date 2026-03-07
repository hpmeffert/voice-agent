# Voice Agent vX.Y.Z

Date: YYYY-MM-DD  
PR: #<number>  
Base Branch: `release/v5.4-azure-stable`

## Summary
Short summary of the release goal and scope.

## Highlights
- Item 1
- Item 2
- Item 3

## Scope and Compatibility
- Changes are isolated under `v6/` (if applicable).
- No unexpected service/port/compose changes.
- Backward compatibility notes.

## Technical Changes
- API:
  - Endpoints added/changed.
  - Data model changes.
- Frontend:
  - UX changes.
  - Settings/toggles.
- Infrastructure:
  - Compose/runtime updates.

## How to Run
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

## Validation
- Manual UI checks:
  - Check 1
  - Check 2
- API checks:
  - Check 1
  - Check 2
- Data checks:
  - Check 1

## Known Limitations
- Limitation 1
- Limitation 2
