# V9 Dual‑Lane & Translation – Test Runbook (2–5 min)

Ziel: In **jedem** Client wird **nur** die Sprache gesprochen, die für diesen Client eingestellt ist.  
Zusätzlich: Live‑Events kommen **ohne Reload** an (WebSocket), und Übersetzungen sind korrekt.

---

## A) Schnelltest im Browser (2 Minuten)

### Setup
1. **Agent UI** öffnen: `http://localhost:8087`
2. **Customer UI** öffnen: `http://localhost:8086`
3. In beiden Tabs **Hard Reload** (Cmd+Shift+R).

### Agent Einstellungen
- Auto‑Refresh: **ON**
- Incoming speak (Kunden‑Eingang vorlesen): **ON** *(optional; zum Beweis ON)*
- Customer‑Ausgabe am Agenten sprechen: **OFF**

### Szenario 1 – Customer=DE, Agent=EN
1. Customer: Sprache **DE** (oder Auto + erster Input DE). Sende/spreche:  
   `Meine Wallbox geht immer aus. Was kann ich tun?`
2. Erwartung (Agent):
   - **Sofort** sichtbar (ohne Reload): Nachricht erscheint.
   - Anzeige **2‑spurig**: `Original (de)` + `For Agent (en)`
   - **Audio am Agent**: **EN** (wenn Incoming speak ON)
3. Agent antwortet **EN**:  
   `Let's check the power supply and the firmware version.`
4. Erwartung (Customer):
   - **Audio am Customer**: **DE**
   - Anzeige: `Original (en)` + `For Customer (de)` (oder nur Customer‑Lane; je nach UI)

✅ PASS, wenn in beiden Richtungen **korrekte Sprache** + **kein Reload** nötig.

### Szenario 2 – Customer=EN, Agent=SV (oder EN)
Analog, aber Customer spricht/ tippt EN. Agent UI Sprache SV/EN.  
✅ PASS, wenn Agent Audio/Anzeige in Agent‑Sprache, Customer Audio/Anzeige in Customer‑Sprache.

### Szenario 3 – Auto‑Language Stabilität
Customer auf Auto, 1. Nachricht EN → später DE.  
✅ PASS, wenn die Lane‑Logik „Auto‑Init einmal“ sauber bleibt (je nach Spezifikation).

---

## B) Was ich als Ergebnis brauche (Evidence Pack)

Bitte nach jedem Testlauf die folgenden Dateien erzeugen und **als ZIP** bereitstellen:

1. `ENV_SNAPSHOT.txt` (env + git sha + docker ps)
2. `docker-logs-api.txt`
3. `docker-logs-web-agent.txt`
4. `docker-logs-web-customer.txt`
5. `ws_agent_events.jsonl`
6. `ws_customer_events.jsonl`
7. `session_dump.json` (Session‑Meta + letzte Messages)
8. `test-log-v9.1x.txt` (Zusammenfassung PASS/FAIL + Zeiten)

---

## C) 1‑Command Evidence Pack (für Codex)

> Erwartung: Codex legt **alle Artefakte** in `artifacts/<timestamp>/` ab und zipped sie.

```bash
bash ./scripts/run_v9_ws_duallane_tests.sh \
  --agent_url http://localhost:8087 \
  --customer_url http://localhost:8086 \
  --out artifacts
```

Falls das Script bereits existiert: es soll zusätzlich:
- **2s‑Timing** als WARN statt FAIL ausgeben (wenn UI‑Reload‑Bug behoben ist, dürfen Events trotzdem mal >2s sein – das ist oft LLM‑/STT‑Zeit)
- Übersetzungs‑Assertions erzwingen:
  - `customer->agent`: `agent.text` Sprache == agent_lang
  - `agent->customer`: `customer.text` Sprache == customer_lang
- `message.created` in beiden Richtungen in den WS‑Events finden.

---

## D) Pass/Fail Kriterien (knallhart)

PASS nur wenn:
- Agent sieht **ohne Reload** Customer‑Events.
- **Agent‑Audio** verwendet **nur** Agent‑Lane Text.
- **Customer‑Audio** verwendet **nur** Customer‑Lane Text.
- Bei unterschiedlichen Sprachen ist `text_for_agent != text_for_customer` (oder zumindest `lang_for_*` korrekt) und Übersetzungs‑Flags stimmen.
