# Release Notes v7.9.0

## Highlights
- Added persistent `admin_settings` store in Mongo (`admin_settings` collection).
- Added admin endpoints:
  - `GET /api/admin/settings`
  - `POST /api/admin/settings`
- Added Admin Settings UI panel for runtime configuration.

## Added
- Admin-configurable runtime settings:
  - metrics retention days
  - listen defaults (silence ms, threshold)
  - CRM export template path
  - feature toggles (`crm_export_enabled`, `crm_protocol_enabled`, `debug_panel_default`)
- Admin Settings screen in the menu (`Admin Settings`).

## Changed
- Runtime config now reads effective values from `admin_settings` (with safe defaults fallback).
- `/api/config` includes `admin_settings`.
- UI/API version defaults updated to `v7.9.0`.

## Fixed
- Settings now persist across restart and can be managed without manual DB edits.

## Ops / Deployment Notes
- Verify:
  - `curl -s "http://localhost:8081/api/admin/settings?user_id=<USER_ID>" -H "X-Admin-Token: <TOKEN>"`
  - `curl -s -X POST "http://localhost:8081/api/admin/settings" -H "Content-Type: application/json" -H "X-Admin-Token: <TOKEN>" -d '{"user_id":"<USER_ID>","retention_days":45}'`
