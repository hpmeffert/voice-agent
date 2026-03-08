# Security Baseline (macOS Dev) - V8.8.0

## Ziel
Pragmatische Sicherheits-Baseline fuer lokale Entwicklung und Demo-Betrieb.

## 1) Input-Limits (API)
- `MAX_AUDIO_BYTES` (Default: `26214400`) fuer `/api/voice` Uploads
- `MAX_REQUEST_BYTES` (Default: `2097152`) fuer sonstige HTTP Requests
- `MAX_TEXT_CHARS` (Default: `8000`) fuer Textfelder

Erwartetes Verhalten:
- Zu grosse Payload -> `413 Payload too large`
- Zu langer Text -> `400 Text too long`

## 2) Rate-Limit (API)
- In-Memory per IP
- Parameter:
  - `RATE_LIMIT_WINDOW_SEC` (Default: `10`)
  - `RATE_LIMIT_MAX_REQUESTS` (Default: `25`)

Erwartetes Verhalten:
- Bei Request-Flut -> `429 Rate limit exceeded`

## 3) Nginx Security Header
Aktiviert in Admin/Customer/Agent Web:
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options: DENY`
- `Permissions-Policy: microphone=(self)`
- `Content-Security-Policy` (demo-praktisch)

## 4) Verifikation
```bash
curl -I http://localhost:8082/
curl -I http://localhost:8083/
curl -I http://localhost:8084/
```

Rate-Limit Smoke:
```bash
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/api/health; done
```

## 5) Hinweise
- Baseline ist fuer Dev/Demo, nicht vollstaendige Produktiv-Hardening-Strategie.
- Keine Secrets in Git; `.env` bleibt ignoriert.
