# Release Notes v7.8.0

## Highlights
- Added dedicated Mongo collection `metrics_logs` with TTL retention for performance telemetry.
- Added admin endpoints:
  - `GET /api/admin/metrics/recent`
  - `GET /api/admin/metrics/summary`
- Added admin-only metrics panel in UI for recent logs and 24h summary.

## Added
- Config variable:
  - `METRICS_RETENTION_DAYS` (default `30`)
- UI admin panel:
  - recent entries from `metrics_logs`
  - average latency summary

## Changed
- Telemetry logging now targets `metrics_logs`.
- Config now returns:
  - `metrics_retention_days`
- UI/API version defaults updated to `v7.8.0`.

## Fixed
- Better operational visibility for admins without Mongo shell access.

## Ops / Deployment Notes
- Verify endpoints:
  - `curl -s "http://localhost:8081/api/admin/metrics/recent?user_id=<USER_ID>&limit=20" -H "X-Admin-Token: <TOKEN>"`
  - `curl -s "http://localhost:8081/api/admin/metrics/summary?user_id=<USER_ID>&window=24h" -H "X-Admin-Token: <TOKEN>"`
