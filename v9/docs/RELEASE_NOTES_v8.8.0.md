# V8.8.0 - Security baseline: headers, rate limits, input limits

## Neue Funktionalitaet

### 1) API Input-Limits
- Neu:
  - Request-Size-Grenze fuer allgemeine Requests
  - Audio-Upload-Limit fuer `/api/voice`
  - Textlaengen-Limits werden konsistent erzwungen
- Wofuer gut:
  - Schutz vor uebergrossen Requests und unnoetiger Last
- Relevante Parameter:
  - `MAX_AUDIO_BYTES`
  - `MAX_REQUEST_BYTES`
  - `MAX_TEXT_CHARS`
- Vorteil:
  - stabilerer Betrieb bei fehlerhaften oder aggressiven Clients

### 2) Einfaches per-IP Rate-Limit
- Neu:
  - API-Middleware mit per-IP Request-Limit in Zeitfenstern
- Wofuer gut:
  - Daempft Spam/Request-Stürme in Dev- und Demo-Umgebungen
- Relevante Parameter:
  - `RATE_LIMIT_WINDOW_SEC`
  - `RATE_LIMIT_MAX_REQUESTS`
- Vorteil:
  - bessere Verfuegbarkeit bei Lastspitzen

### 3) Security Header in Web-Nginx
- Neu in Admin/Customer/Agent-Web:
  - `X-Content-Type-Options`
  - `Referrer-Policy`
  - `X-Frame-Options`
  - `Permissions-Policy`
  - `Content-Security-Policy` (praktische Demo-Baseline)
- Wofuer gut:
  - reduziert typische Browser-Angriffsoberflaechen
- Relevante Dateiorte:
  - `v8/docker/web/nginx.conf`
  - `v8/docker/web-customer/nginx.conf`
  - `v8/docker/web-agent/nginx.conf`
- Vorteil:
  - konsistentes Mindestniveau fuer Browser-Sicherheit

### 4) Admin Security Checklist
- Neu:
  - `v8/docs/SECURITY_BASELINE_MAC.md`
- Wofuer gut:
  - klare Test-/Betriebsanleitung fuer Security-Checks
- Vorteil:
  - schnellere, reproduzierbare Sicherheits-Smoketests im Team

## Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
```

Manuell:
1. Uebergrossen Upload testen -> `413`
2. 30 schnelle Requests -> `429` sichtbar
3. `curl -I` auf 8082/8083/8084 -> Security Header vorhanden

## Lizenzhinweis
- Keine neuen Dependencies eingefuehrt.
- Keine GPL/AGPL-Erweiterung im Core.
