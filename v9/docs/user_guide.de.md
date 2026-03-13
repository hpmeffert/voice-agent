# Benutzer Handbuch (DE, Agent View) - V9.1.17

## Was macht der Voice Agent?
Der Voice Agent verbindet Sprache und Text in einem durchgehenden Ablauf:
1. Kunde spricht oder schreibt.
2. System erkennt die Kundensprache.
3. Agent arbeitet in seiner eigenen Sprache.
4. System uebersetzt zurueck in die Kundensprache.
5. Kunde hoert die Antwort mit passendem Voice-Profil.

Das Ziel: Beide Seiten sprechen in ihrer bevorzugten Sprache, trotzdem versteht sich jeder.

## Oberflaechen (Agent-Flow)
- Kunden UI: `http://localhost:8086`
- Agent UI: `http://localhost:8087`

## Wichtig: Agenten-Sprache oben im Agent Client
Oben im Agent Client gibt es:
- `Demo User` (Dropdown fuer schnelle Agent-Auswahl)
- `Agent ID`
- `Agent Sprache` (`de`, `en`, `no`, `sv`, `fi`)
- `Empfang auf Agent sprechen` (an/aus)
- `Kunden-Ausgabe auf Agent sprechen` (an/aus, Standard AUS)
- `Customer output lang`

### Was bedeutet `Agent Sprache`?
`Agent Sprache` ist die Muttersprache des Agenten.
- Eingehende Kundennachrichten werden fuer den Agenten in diese Sprache gebracht.
- Agent Voice spricht in dieser Sprache.
- Die Einstellung wird pro Agent-ID gespeichert.

Beispiel:
- Agent `agenten-02` setzt `Agent Sprache = en`.
- Kunde schreibt Deutsch.
- Agent sieht/hoert die Nachricht auf Englisch.

## Original + Uebersetzung im Agent-Fenster
Der Agent sieht jetzt beides:
- `Original`: Eingangstext in der Ursprungssprache.
- `Uebersetzung`: Text in der Agent-Sprache.

So kann der Agent immer kontrollieren, was genau gesagt wurde.

## Customer output lang (im Agent Client)
`Customer output lang` steuert die Ausgabesprache fuer den Kunden.

Optionen:
- `auto (detected customer profile)`
  - Empfohlen.
  - System nimmt die erkannte Kundensprache + Kunden-Voice-Profil aus der Session.
- Manuell (`de`, `en`, `no`, `sv`, `fi`)
  - Erzwingt eine feste Kundenausgabe.

### Regel im Auto-Modus
Wenn Kundensprache erkannt wurde, wird genau diese als Antwortsprache und Voice-Profil genutzt.

## Ablauf der Uebersetzung (einfach erklaert)
1. Kunde spricht/schreibt in Sprache A.
2. System erkennt Sprache A und speichert sie als Kundenprofil.
3. Agent arbeitet in Sprache B (seine eingestellte Agent Sprache).
4. Agentnachricht wird vor Auslieferung nach Sprache A uebersetzt.
5. Kunde bekommt Text + Sprache in Sprache A.

## Listen Mode (Kunde)
- Automatisch aufnehmen, bei Stille stoppen, senden.
- Standard Stillewert: `1300 ms`.

## Drei klare Beispiele

### Beispiel 1: Kunde DE, Agent EN
- Kunde: Deutsch
- Agent Sprache: `en`
- Customer output lang: `auto`
- Ergebnis:
  - Agent arbeitet auf Englisch.
  - Kunde bekommt Deutsch (Text + deutsche Stimme).
  - Agent sieht im Chatfenster sowohl Original (DE) als auch Uebersetzung (EN).

### Beispiel 2: Kunde EN, Agent DE
- Kunde: Englisch
- Agent Sprache: `de`
- Customer output lang: `auto`
- Ergebnis:
  - Agent sieht/hoert Englisch auf Deutsch uebersetzt.
  - Kunde bekommt Englisch (Text + englische Stimme).

### Beispiel 3: Manuelle Ueberschreibung
- Kunde spricht Deutsch.
- Agent setzt `Customer output lang = en`.
- Ergebnis:
  - Kunde bekommt Antwort auf Englisch (Text + englische Stimme), auch wenn er Deutsch gestartet hat.

## Fehlerbilder (kurz)
- Falsche Ausgabe-Sprache beim Kunden:
  - Pruefe im Agent Client `Customer output lang`.
  - Fuer automatische Zuordnung: auf `auto` stellen.
- Agent hoert nicht in eigener Sprache:
  - `Agent Sprache` pruefen.
  - `Empfang auf Agent sprechen` aktivieren.
- Zwei Stimmen gleichzeitig:
  - `Kunden-Ausgabe auf Agent sprechen` auf AUS lassen (Standard).
- Kein Audio:
  - Browser-Autoplay erlauben.
  - Bei Ausfall den technischen Support informieren.

## Neu in V9.1.0: Dual-Lane (Original + Zieltext)
- Jede eingehende Kundennachricht hat jetzt 2 Ansichten im Agent-Client:
  - `Original (lang_original)`
  - `Uebersetzung (Agent Sprache)`
- Die Sprachausgabe beim Agenten nutzt nur noch `tts.agent_text`.
- Die Sprachausgabe beim Kunden nutzt nur noch `tts.customer_text`.
- Dadurch wird verhindert, dass z. B. deutscher Originaltext mit englischer Stimme gesprochen wird.

## Neu in V9.1.1: TTS Cleanup
- TTS entfernt jetzt Markdown-Formatierungszeichen (z. B. `*`, `**`, Backticks) vor der Sprachausgabe.
- Das betrifft nur Audio-Ausgabe, nicht gespeicherten oder angezeigten Text.

## Neu in V9.1.2: Agent-Inbox Auto-Refresh + Anzeige-Bereinigung
- Der Agent-Client hat jetzt `Auto-Refresh` fuer die Inbox (Standard: an, 5 Sekunden).
- Wenn eine Session neue Aktivitaet hat, wird sie schneller in der Inbox sichtbar.
- Neuer Schalter: `Anzeige bereinigen (Sonderzeichen ausblenden)`.
  - Nur die Chat-Anzeige wird bereinigt.
  - Routing, Uebersetzung, gespeicherte Daten und TTS-Felder bleiben unveraendert.

## Neu in V9.1.5-fix-voice-duallane: Voice = Chat (Paritaetsfix)
- Voice-Eingaben nutzen jetzt denselben `message.created`-Live-Vertrag wie Chat.
- Bei unterschiedlicher Sprache bekommt der Agent garantiert die Agent-Lane-Uebersetzung.
- TTS bleibt strikt lane-gebunden:
  - Agent spricht nur `tts.agent_*`
  - Kunde spricht nur `tts.customer_*`
- Fuer Debugging gibt es zusaetzlich klare Felder wie `source_lang_effective` im Event-Debug.

### Schnelltest (2 Minuten)
1. Agent: Sprache `en`, Incoming Speak `AN`.
2. Kunde: Sprache `de`, spricht den Satz zur Wallbox.
3. Erwartung:
   - Agent sieht `Original (DE)` + `Uebersetzung (EN)` live.
   - Agent hoert EN.
4. Agent antwortet EN.
5. Kunde sieht/hoert DE.

## Neu in V9.1.7: Auto-Upload + schnelleres Standardmodell
- Customer-Client hat jetzt den Schalter `Auto-send after recording` (Standard: AN).
- Wenn die Aufnahme endet, wird bei aktivem Schalter automatisch gesendet, ohne extra Klick auf `Send Audio`.
- Standardmodell ist jetzt `qwen2.5:3b` (mit Fallback auf `qwen2.5:7b`, falls 3b nicht verfuegbar ist).
- TTS bleibt lane-gebunden und bereinigt Markdown-/Control-Zeichen nur fuer Audio.

### Beispiel
1. Kunde spricht auf Deutsch und stoppt die Aufnahme.
2. Auto-send ist AN.
3. Upload startet automatisch.
4. Agent bekommt die Nachricht live im Agent-Lane-Text (z. B. Englisch), Kunde bekommt Antwort in Kundensprache.

## Neu in V9.1.8: Stabilerer Betrieb im Hintergrund
- Fuer Benutzer bleibt der Ablauf gleich.
- Im Hintergrund kann ein Admin jetzt Diagnosen gezielt ein-/ausschalten und Sessions schneller finden.
- Vorteil fuer Nutzer:
  - schnellere Fehleranalyse bei Stoerungen
  - weniger Unterbrechungen im Live-Betrieb.

## Neu in V9.1.11: Agent/Admin sauber getrennt
- Der Agent hat jetzt oben immer denselben klaren Kopfbereich:
  - Verbindungsstatus + Version
  - Suche (`q` + Modus)
  - `Agent Settings ⚙︎`
- Die Suche ist immer sichtbar und nutzt `/api/agent/search` (kein Admin-Endpoint im Agenten).
- Der Drawer enthaelt nur agentenspezifische Einstellungen:
  - Backend/Model (lokal fuer den Agenten)
  - Agent-Sprache
  - Incoming-Speak, Customer-Speak-on-Agent, Debug/Metrics, Auto-Refresh
- Performance wird kompakt gezeigt (lokale Zusammenfassung):
  - `STT avg/p95`
  - `LLM avg/p95`
  - `Total avg/p95`

### Beispiel
1. Agent gibt in die Suche `fe774f*` ein und waehlt `auto`.
2. Trefferliste zeigt Session-ID, Kontext-Snippet und Zeit.
3. Klick auf Treffer oeffnet direkt die Session.
4. Bei Bedarf `Agent Settings ⚙︎` oeffnen und Einstellungen speichern.

## Neu in V9.1.14: Stabilere Performance-Beobachtung (Admin-seitig)
- Fuer Agent/Kunde bleibt die Bedienung gleich.
- Admin kann jetzt Performance-Logging gezielt ein-/ausschalten.
- Vorteil fuer Benutzer:
  - Stoerungen werden schneller analysiert
  - weniger Trial-and-Error im Live-Betrieb
  - klare Export-Datei fuer Team-Analyse

## Neu in V9.1.15: Performance Dashboard (nur Admin)
- Admin kann jetzt direkt im Admin-Client sehen:
  - Summary Cards
  - Worst Spikes
  - Perf-Suche
- Fuer Kunde und Agent aendert sich dadurch nichts an der normalen Bedienung.

## Patch V9.1.15-p1: Stabilerer Chat fuer den Agenten
- Wenn ein Kunde jetzt schreibt, bekommt der Agent dieselbe klare Dual-Lane wie bei Voice:
  - `Original`
  - `Uebersetzung`
- Das gilt auch nach einem Reload des Agent-Clients.
- `Backend/Model` sind im Agent-Client nicht mehr veraenderbar, damit Agent und Admin nicht gegeneinander arbeiten.

## Patch V9.1.15-p3: WS RTT + Anzeige-Sicherheit
- Oben im Header von Admin, Agent und Kunde sehen Sie jetzt zusaetzlich `WS RTT: <ms>`.
- Diese Zahl zeigt die ungefaehre Hin-und-zurueck-Laufzeit der WebSocket-Verbindung.
- Wenn die Verbindung getrennt ist, steht dort `WS RTT: -`.
- Fuer den Agenten gilt jetzt noch strenger:
  - Bei Kundennachrichten mit anderer Sprache muessen `Original` und `Uebersetzung` sichtbar sein.
  - Wenn `Empfang auf Agent sprechen` AN ist, wird nur die Agent-Sprache gesprochen.

## Neu in V9.1.17: Schnelleres Default-Modell + stabilere Regressionstests
- Das Standardmodell bleibt jetzt klar auf `qwen2.5:3b`.
- Vorteil:
  - kuerzere Antwortzeiten im Demo-Betrieb
  - weniger Wartezeit bei Search-, Chat- und Voice-Tests
- Wenn ein Benutzer schon bewusst ein anderes Modell gespeichert hat, bleibt diese Auswahl erhalten.
- Nur bei leerer oder neuer Auswahl wird automatisch `qwen2.5:3b` gesetzt.

### Was bedeutet das fuer den Agenten?
1. Sie starten den Agent-Client neu.
2. Wenn noch keine eigene Modellwahl gespeichert ist, arbeitet das System mit `qwen2.5:3b`.
3. Admin kann spaeter weiter auf ein anderes Modell umstellen.

### Regressionstest fuer V9.1.17
- Technischer Gesamtstart:
  - `bash scripts/run_v9_1_17_full_regression.sh`
- Enthalten:
  - Artifact-Guard
  - Doc-Check
  - Syntax-Check
  - Search-Test
  - WS-Regression
  - UI-Smoke

### 2-Minuten-Proof
1. Agent auf `en` stellen.
2. Kunde auf `de` stellen und einen deutschen Chat- oder Voice-Text senden.
3. Pruefen:
   - Agent sieht `Original (de)` + `Uebersetzung (en)`.
   - `WS RTT` zeigt nach wenigen Sekunden einen ms-Wert.
4. Agent antwortet auf Englisch.
5. Kunde sieht/hoert die deutsche Ausgabe.

## Neu in V9.1.16: Suche mit Wildcards und sicherem Oeffnen
- Die Suche im Agent-Client versteht jetzt Wildcards wie `fe77*`, `*wallbox*` und `*c8e9`.
- `auto` erkennt id-aehnliche Suchbegriffe selbst, sonst wird als Text gesucht.
- Treffer zeigen jetzt mehrere Kontext-Snippets statt nur einer einzelnen Zeile.
- Ein Klick auf einen Treffer laedt die komplette Session mit `Original + Uebersetzung`.

### Beispiel
1. Geben Sie `*wallbox*` in die Suche ein.
2. Waehlen Sie `text` oder lassen Sie `auto`.
3. In der Trefferliste sehen Sie Session-ID, Zeit und Textausschnitte.
4. Klicken Sie auf einen Treffer, um den kompletten Verlauf im Agent-Client zu oeffnen.

## Patch V9.1.16: Voice und Chat wieder gleich sichtbar
- Wenn der Kunde spricht, sieht der Kunde jetzt wieder:
  - den eigenen Transcript-Eintrag
  - die Antwort im selben Chatverlauf
- Im Agent-Client sehen Sie jetzt auch fuer die generierte Antwort wieder:
  - `Original`
  - `Uebersetzung`

### 2-Minuten-Proof
1. Kunde auf `de`, Agent auf `en`.
2. Kunde spricht Deutsch.
3. Pruefen:
   - Kunde sieht Transcript + Antwort.
   - Agent sieht fuer den Kundentext `Original (de) + Uebersetzung (en)`.
   - Agent sieht fuer die generierte Antwort ebenfalls `Original + Uebersetzung`.
4. Verlauf neu laden.
5. Dasselbe Bild muss erhalten bleiben.
