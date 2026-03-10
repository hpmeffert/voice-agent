# V9 Dual-Lane Live Testprotokoll (WS + Chat + Voice)

Version: v9.1.x  
Zielgruppe: Admin, QA, Demo-Team, Entwickler  
Sprache: Deutsch (einfach, klar, reproduzierbar)

---

## 1) Ziel dieses Dokuments
Dieses Protokoll sorgt dafür, dass wir Sprachrouting-Fehler **eindeutig finden und reproduzierbar beheben**.

Wir prüfen drei Dinge:
1. Live-Events kommen zuverlässig per WebSocket (ohne Browser-Reload).
2. Übersetzung läuft pro Empfänger korrekt (Dual-Lane):
   - Agent sieht/hört Agentensprache.
   - Kunde sieht/hört Kundensprache.
3. TTS verwendet nur die richtigen Lane-Felder (keine falsche Sprache mit falscher Stimme).

---

## 2) Kurz erklärt: Dual-Lane
Jede Nachricht hat:
- `text_original`, `lang_original` (Originaltext + Originalsprache)
- Agent-Lane: `text_for_agent`, `lang_for_agent`
- Customer-Lane: `text_for_customer`, `lang_for_customer`
- TTS:
  - Agent: `tts.agent_text`, `tts.agent_lang`
  - Kunde: `tts.customer_text`, `tts.customer_lang`

Merksatz:
- Agent darf nur Agent-Lane sprechen.
- Kunde darf nur Customer-Lane sprechen.
- Originaltext ist Anzeige/Debug, nicht TTS-Quelle.

---

## 3) Voraussetzungen

### 3.1 Dienste starten
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml up -d --build api web-agent web-customer piper mongo valkey
```

### 3.2 Health prüfen
```bash
curl -s http://localhost:8003/health
curl -s http://localhost:8087/api/health
curl -s http://localhost:8086/api/health
```

Erwartung: `{"status":"ok", ...}`

### 3.3 Test-URLs
- Agent UI: `http://localhost:8087`
- Customer UI: `http://localhost:8086`
- API direkt: `http://localhost:8003`

---

## 4) Pflicht-Konfiguration für Tests

### Agent UI
- Agent ID: `agenten-02`
- Agent Sprache: `en`
- Empfang auf Agent sprechen: `AN` (für Audio-Checks)
- Kunden-Ausgabe auf Agent sprechen: `AUS`
- Auto-Refresh: `AN`

### Customer UI
- Kundensprache: `de`
- TTS (Kunde): `de` oder `auto` (je Testfall)
- Session-ID notieren

---

## 5) Testmatrix (muss jede Runde durchlaufen)

## 5.1 Szenario A (Chat): Customer DE -> Agent EN -> Customer DE
1. Kunde schreibt: `Meine Wallbox geht immer aus. Was kann ich tun?`
2. Agent muss live sehen:
   - Original: Deutsch
   - Übersetzung: Englisch
3. Agent antwortet auf Englisch.
4. Kunde muss Antwort auf Deutsch sehen/hören.

PASS-Kriterien:
- Agent-Lane übersetzt (`text_for_agent` != `text_original` bei DE->EN)
- `lang_for_agent=en`
- `tts.agent_lang=en` (wenn Incoming Speak an)
- Kunde: `lang_for_customer=de`, `tts.customer_lang=de`

## 5.2 Szenario B (Voice): Customer DE (gesprochen) -> Agent EN
1. Kunde spricht: `Meine Wallbox geht immer aus. Was kann ich tun?`
2. Agent sieht live Original + EN-Übersetzung.
3. Wenn Agent-Incoming-Speak an: Agent hört nur EN-Text.

PASS-Kriterien:
- Event vorhanden (`message.created`, `from=customer`)
- `source_lang` plausibel (`de` bei explizitem `customer_lang=de`)
- `text_for_agent` englisch, nicht deutscher Originalsatz
- `tts.agent_lang=en`

## 5.3 Szenario C (Rückrichtung): Agent EN -> Customer DE
1. Agent sendet: `Please check the power supply and breaker. What model is it?`
2. Kunde bekommt Antwort in Deutsch (Text + Voice).

PASS-Kriterien:
- Event auf Customer-WS vorhanden (`message.created`, `from=agent`)
- `text_for_customer` deutsch
- `lang_for_customer=de`
- `tts.customer_lang=de`

## 5.4 Szenario D (Sprachwechsel): Customer EN -> Agent SV
- Agent Sprache: `sv`
- Kundensprache: `en`
- Prüfen: Agent bekommt schwedische Lane, Kunde englische Lane.

---

## 6) Automatisierter Lauf (Artefakte)

## 6.1 Runner
```bash
bash scripts/run_v9_ws_duallane_tests.sh --agent_url http://localhost:8087 --customer_url http://localhost:8086 --out artifacts
```

## 6.2 Erwartete Ausgaben
Der Runner schreibt 6 Kernzeilen:
- `COMMIT`
- `RESULT`
- `SCENARIO1`
- `SCENARIO2`
- `SCENARIO3`
- `P95_MS`

Zusätzlich im Log:
- `VOICE_SCENARIO: PASS|FAIL (...)`

## 6.3 Pflicht-Artefakte
Im Laufordner `artifacts/v9_ws_<timestamp>/`:
- `SUMMARY.md`
- `test-log-v9.1.5.txt`
- `ws_probe_status.json`
- `events-agent.jsonl`
- `events-customer.jsonl`
- `http-probes.json`
- `http_requests.log`
- `ENV_SNAPSHOT.txt`
- `session_dump.json`
- `docker-logs-api.txt`
- `docker-logs-web-agent.txt`
- `docker-logs-web-customer.txt`
- `artifacts.zip`

---

## 7) Event-Checkliste (JSON)
Bei einem Customer->Agent Event muss im Payload mindestens vorhanden sein:
- `text_original`
- `text_for_agent`
- `lang_for_agent`
- `text_for_customer`
- `lang_for_customer`
- `lane.agent.lang`
- `lane.agent.has_translation`
- `lane.agent.text_preview`
- `lane.customer.lang`
- `lane.customer.has_translation`
- `lane.customer.text_preview`
- `tts.agent_text`
- `tts.agent_lang`

Bei Agent->Customer entsprechend:
- `text_for_customer`
- `lang_for_customer`
- `tts.customer_text`
- `tts.customer_lang`

---

## 8) Troubleshooting-Entscheidungsbaum

## 8.1 Agent sieht keine Übersetzung
Prüfen:
1. Ist `agent_lang` im WS-Connect gesetzt?
2. Event enthält `text_for_agent`?
3. Ist `source_lang` korrekt?
4. Ist `lane.agent.has_translation` bei Sprachunterschied `true`?

Wenn `source_lang` falsch (z. B. `en` bei deutschem Text):
- Prüfen, ob `customer_lang` explizit gesetzt war.
- Prüfen, ob `debug.source_lang_effective` vorhanden/plausibel ist.

## 8.2 Kunde sieht Agent-Antwort, aber falsche Sprache
Prüfen:
1. `text_for_customer` und `lang_for_customer`
2. `tts.customer_lang`
3. Customer UI-Language und Session-Meta (`customer_lang_ui_last`)

## 8.3 Events kommen nur nach Reload
Prüfen:
1. WS-Status im Agent (`online`)
2. `ws_probe_status.json`
3. API- und Web-Logs auf Reconnect/Proxy-Fehler

## 8.4 Test ist rot nur wegen Zeit
- `fast_delivery_ok` ist Info (Performance)
- `eventual_delivery_ok` ist Stabilitätskriterium
- Wenn Eventual > Ziel: Infrastruktur/LLM-Latenz prüfen, nicht sofort Routing als defekt markieren.

---

## 9) Standardisierte Fehlermeldungen (für Reports)
Bei FAIL immer exakt nennen:
- `missing customer->agent event`
- `missing agent->customer message.created`
- `translation_not_applied_when_langs_differ`
- `lang_for_agent_not_en`
- `lang_for_customer_not_de`
- `tts_agent_lang_not_en`
- `tts_customer_lang_not_de`
- `eventual_delivery_failed`

Damit bleiben alle Reports vergleichbar.

---

## 10) Release-Gate (vor Merge)
Ein Build darf erst gemerged werden, wenn:
1. Chat-Szenarien grün sind.
2. Voice-Szenario mindestens 1x reproduzierbar grün ist.
3. Artefakte vollständig sind.
4. Doku aktualisiert ist:
   - User Guide
   - Demo Guide
   - Admin Docs
   - Release Notes
5. Help-Menüstruktur korrekt bleibt:
   1) Admin Token speichern
   2) Benutzer Handbuch
   3) Demo Guide
   4) Admin Docs
   5) Release Notes

---

## 11) Vorlage für jeden Testlauf (Copy/Paste)

```md
# Testlauf v9.x.y
- Datum/Zeit:
- Commit:
- Umgebung:
- Agent-Sprache:
- Kunden-Sprache:

## Ergebnisse
- Szenario A (Chat): PASS/FAIL
- Szenario B (Voice): PASS/FAIL
- Szenario C (Agent->Kunde): PASS/FAIL
- Szenario D (Sprachwechsel): PASS/FAIL

## Timing
- fast_delivery_ok:
- eventual_delivery_ok:
- P95_MS:

## Artefakte
- Pfad:
- SUMMARY.md:
- test-log:
- events-agent/customer:

## Befunde
- Root Cause (wenn FAIL):
- Geplanter Fix:
- Re-Test geplant am:
```

---

## 12) Aktueller Stand (wichtig)
- Chat-Pfad ist stabil grün in den Kernfällen.
- Voice-Pfad wurde im Backend so gehärtet, dass explizites `customer_lang` als effektive Quellen-Sprache genutzt werden kann (wichtig für DE->EN Agent-Lane).
- Zusätzliche Debugfelder im Payload helfen jetzt, STT-Erkennung vs. effektive Routing-Sprache sauber zu trennen.

