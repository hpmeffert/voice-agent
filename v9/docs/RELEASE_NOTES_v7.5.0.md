# Release Notes v7.5.0

## Highlights
- New admin-only `Demo Mode` for one-click hands-free demo loops.
- New admin-only `Debug panel` toggle to hide/show technical JSON during presentations.
- CRM export toggle is now admin-only in the UI.

## Added
- `Demo Mode` toggle in the main UI:
  - forces Listen Mode ON
  - keeps auto-stop and auto-send enabled
  - shows a visible demo guidance banner
- `Debug panel` toggle for controlling `Debug JSON` visibility.

## Changed
- Admin-only visibility rules now apply to:
  - CRM Export toggle
  - Demo Mode toggle
  - Debug panel toggle
- UI version defaults updated to `v7.5.0`.

## Fixed
- Better presenter flow: less accidental UI misconfiguration during live demos.

## Ops / Deployment Notes
- Start:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- For demo admin behavior:
  - ensure `ADMIN_DEV_MODE=1` in `v7/docker/compose.dev.yml` (default for local demo).
