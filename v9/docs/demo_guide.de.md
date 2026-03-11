# Demo Guide (DE) - V9.0.0

## Ziel der Demo
Diese Demo zeigt, wie ein internationales Team Kunden in deren Sprache bedienen kann, ohne dass Agenten ihre Muttersprache verlassen muessen.

## Story-Flow 1: "Kennen Sie das auch?" Kunde DE, Agent EN
Stellen Sie sich vor: Der Kunde spricht nur Deutsch, Ihr Agent ist neu im Team und arbeitet auf Englisch.

### Setup
1. Customer UI (`8086`) starten.
2. Agent UI (`8087`) starten.
3. Agent einstellen:
   - `Demo User = agenten-02 (EN)`
   - `Agent ID = agenten-02`
   - `Agent Sprache = en`
   - `Empfang auf Agent sprechen = ON`
   - `Kunden-Ausgabe auf Agent sprechen = OFF`
   - `Customer output lang = auto`

### Demo-Schritte
1. Kunde sagt/schreibt: "Ich brauche Hilfe mit meiner Rechnung."
2. Agent sieht den Inhalt auf Englisch.
3. Agent antwortet auf Englisch.
4. Kunde bekommt automatisch Deutsch + deutsche Stimme.
5. Agent sieht im Chatfenster:
   - `Original: ...`
   - `Uebersetzung: ...`

### Wirkung fuer Zuschauer
- Der Agent muss kein Deutsch koennen.
- Der Kunde merkt keinen Medienbruch.
- Die Kommunikation bleibt natuerlich.

## Story-Flow 2: "Haben Sie das auch schon erlebt?" Kunde EN, Agent DE
Stellen Sie sich vor: Nachtschicht im Support, Agenten sind deutschsprachig, Kunde ruft aus UK an.

### Setup
1. Agent einstellen:
   - `Demo User = agent-de-01 (DE)`
   - `Agent ID = agent-de-01`
   - `Agent Sprache = de`
   - `Customer output lang = auto`
2. Kunde schreibt/spricht Englisch.

### Demo-Schritte
1. Agent erhaelt Kundentext auf Deutsch (fuer sein Arbeitsprofil).
2. Agent antwortet auf Deutsch.
3. System uebersetzt zurueck auf Englisch.
4. Kunde hoert englische Ausgabe.

### Wirkung fuer Zuschauer
- Deutsche Agenten koennen sofort internationale Anfragen bearbeiten.
- Sprachbarrieren werden technisch entkoppelt.

## Story-Flow 3: Gezielte Sprachsteuerung im Live-Fall
Stellen Sie sich vor: Sie wollen bewusst eine andere Kundensprache ausliefern (z. B. Supervisor-Test).

### Demo-Schritte
1. Kunde startet auf Deutsch.
2. Agent stellt `Customer output lang = en` (manuell).
3. Agent antwortet normal in eigener Sprache.
4. Kunde erhaelt Englisch (Text + Voice), obwohl Ursprung Deutsch war.

### Wirkung fuer Zuschauer
- Der Betrieb kann Sprache bewusst steuern.
- Auto + manuelle Ueberschreibung sind klar getrennt.

## Admin-Demo (Pflichtteil)
1. Admin UI (`8085`) oeffnen.
2. Help-Menue pruefen (Reihenfolge):
   1. Admin Token speichern
   2. Benutzer Handbuch
   3. Demo Guide
   4. Admin Docs
   5. Release Notes
3. Version im Header + Help sichtbar zeigen.
4. Schnelltests:
   - `/api/health`
   - `/api/models`
   - Agent-Sprachtest mit `agenten-02`.

## Moderations-Tipp (Spannungsbogen)
- Starten Sie mit dem Problem (Sprachbarriere).
- Zeigen Sie dann die Loesung live in unter 2 Minuten.
- Schliessen Sie mit dem Business-Nutzen:
  - weniger Wartezeit,
  - weniger Fehlkommunikation,
  - bessere internationale Skalierung.

## V9.1.0 Fokus fuer die Buehne
- Zeigen Sie im Agent-Client sichtbar getrennt:
  - `Original`
  - `Uebersetzung`
- Aktivieren Sie `Empfang auf Agent sprechen`:
  - Es darf nur die Uebersetzung in Agent-Sprache gesprochen werden.
- Lassen Sie den Agenten antworten:
  - Kunde sieht/hoert nur `customer`-Lane in Kundensprache.

## V9.1.1 Demo Fokus
- Zeigen Sie einen Satz mit Markdown-Zeichen (z. B. `**Wichtig**: *Bitte* pruefen`).
- Erwartung: Anzeige bleibt unveraendert, Audio spricht ohne Formatierungszeichen.

## V9.1.2 Demo Fokus
- Zeigen Sie, dass neue Sessions ohne Klick auf `Refresh Inbox` sichtbar werden (Auto-Refresh aktiv).
- Simulieren Sie kurz einen Verbindungsabbruch und zeigen Sie die Rueckkehr von `WS: online`.
- Aktivieren/Deaktivieren Sie `Anzeige bereinigen`, um den Unterschied in der Agent-Textdarstellung zu zeigen.

## V9.1.7 Demo Fokus
- Schalten Sie im Customer-Client `Auto-send after recording` auf AN.
- Sprechen Sie einen kurzen Satz und stoppen Sie die Aufnahme.
- Zeigen Sie dem Publikum: Upload startet direkt ohne zusaetzlichen Klick.
- Erklaeren Sie den Nutzen:
  - weniger Klicks
  - weniger Bedienfehler
  - schnellerer Gespraechsfluss.

## V9.1.8 Demo Fokus
- Admin aktiviert kurz `Perf logging enabled` fuer ein Demo-Fenster.
- Fuehren Sie eine kurze Konversation durch.
- Oeffnen Sie die Admin-Suche:
  - erst Teil-Session-ID (`*`)
  - dann Textfragment.
- Oeffnen Sie den Treffer mit `Open Session` und zeigen Sie den direkten Sprung.
- Danach Logging wieder deaktivieren.

## V9.1.9 Demo Fokus: Clean Agent Desk
1. Zeigen Sie die neue Agent-Oberflaeche mit immer sichtbarem Header.
2. Geben Sie `fe774f*` in die Suche ein (Mode `auto`) und starten Sie die Suche.
3. Oeffnen Sie einen Treffer direkt per Klick aus der Ergebnisliste.
4. Oeffnen Sie `Admin ⚙︎` und zeigen Sie den Drawer:
   - sichere Controls statt Freitext
   - Save/Cancel
   - Quick Link zu Admin Docs
5. Zeigen Sie den Performance-Header (`STT/LLM/Total avg+p95`) und erlaeutern Sie den Nutzen fuer Live-Betrieb.

## V9.1.11 Demo Fokus: Agent/Admin sauber getrennt
1. Agent-Client oeffnen:
   - zeigen, dass der Button `Agent Settings ⚙︎` heisst
   - zeigen, dass keine globalen Admin-Settings mehr sichtbar sind
2. Admin-Client oeffnen:
   - Header-Suche (`q` + `mode`) vorfuehren
   - Perf-Badges fuer STT/LLM/TTS/Total zeigen
3. Dual-Lane kurz live pruefen:
   - Kunde DE Voice -> Agent EN (Original + Uebersetzung sichtbar)
   - Agent EN -> Kunde DE
