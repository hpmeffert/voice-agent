# ADMIN (V6.8.1)

## Telemetry logs overview
V6.8.1 adds a dedicated Mongo collection: `telemetry_logs`.

Every `/api/voice` request writes one telemetry record with:
- `created_at`, `expires_at` (TTL)
- `user_id`, `session_id`
- `backend`, `model`, `lang`
- `metrics.audio_read_ms`, `metrics.stt_ms`, `metrics.llm_ms`, `metrics.tts_ms`, `metrics.total_ms`
- `transcript`, `answer`
- `status` (`ok` or `error`)
- `error_code`, `error_detail` (when available)

Telemetry write failures are fail-safe and do not break request responses.

## Retention
Set API env:
- `TELEMETRY_RETENTION_DAYS` (default: `30`)

Mongo TTL index:
- `telemetry_logs.expires_at` with `expireAfterSeconds: 0`

## Mongo inspection commands
Open Mongo shell:
```bash
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh
use voice_agent
```

Last 50 telemetry entries:
```javascript
db.telemetry_logs.find().sort({created_at:-1}).limit(50).pretty()
```

Latest errors only:
```javascript
db.telemetry_logs.find({status:"error"}).sort({created_at:-1}).limit(50).pretty()
```

Slowest calls by total latency:
```javascript
db.telemetry_logs.find(
  {"metrics.total_ms": {$exists: true}},
  {created_at:1, user_id:1, session_id:1, status:1, backend:1, model:1, "metrics.total_ms":1}
).sort({"metrics.total_ms":-1}).limit(20).pretty()
```

Recent calls for a single user:
```javascript
db.telemetry_logs.find(
  {user_id:"<USER_ID>"},
  {created_at:1, session_id:1, status:1, "metrics.total_ms":1, error_code:1}
).sort({created_at:-1}).limit(50).pretty()
```

Verify TTL index:
```javascript
db.telemetry_logs.getIndexes()
```
