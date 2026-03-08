# Benutzer Dokumentation (V7.10.0)

Diese Seite erklaert alle sichtbaren Funktionen im UI in einfacher Sprache.

## Wo finde ich was?
- URL: `http://localhost:8081`
- Oben rechts im Help-Menue:
  - `Admin Token speichern`
  - `Benutzer Dokumentation` (diese Seite)
  - `Demo Guide`
  - `Admin Docs` (nur Admin)
  - `Release Notes`

## Grundbedienung
- `Record`: startet Mikrofonaufnahme.
- `Stop`: beendet laufende Aufnahme.
- `Send`: sendet die letzte Aufnahme an die API.
- `Clear Session`: startet eine neue Session ohne alten Verlauf.

## Benutzer + Session
- `User` identifiziert den aktuellen Browser-Nutzer.
- `Session` haelt den Gespraechsverlauf.
- Wirkung:
  - gleiche Session: Kontext bleibt erhalten
  - neue Session: frischer Start

## Sprache (neu in V7.10.0)
- Oben rechts gibt es `Lang` mit `de`, `en`, `fr`, `it`, `es`.
- Bei Wechsel wird die UI sofort neu beschriftet.
- Die Auswahl wird pro `user_id` gespeichert.

## Einstellungen fuer Gespraechsfluss
- `Listen Mode`:
  - startet den automatischen Dialog-Loop.
- `Auto-stop on silence`:
  - stoppt Aufnahme automatisch, wenn Stille erkannt wurde.
- `Auto-send after stop`:
  - sendet direkt nach Auto-Stop.
- `Silence threshold (ms)`:
  - Standard: `1300`
  - hoeher = wartet laenger, niedriger = reagiert schneller.
- `Voice threshold (RMS)`:
  - Empfindlichkeit fuer Sprache vs. Hintergrundrauschen.
- `Max recording seconds`:
  - Sicherheitslimit gegen zu lange Aufnahmen.

## TTS-Sprache
- Feld `TTS language`:
  - `Auto`: nutzt erkannte Sprache (oder User-Default)
  - aktiv verfuegbar: `de,en,fr,it,es,sv,no,fi`
- Wirkung:
  - Sie koennen bewusst in einer anderen Sprache ausgeben lassen als gesprochen wurde.

## Admin-only Bereiche
- `CRM Export`: Export fuer Nutzer aktivieren/deaktivieren.
- `Demo Mode`: stabiler Demo-Loop (listen -> send -> speak -> listen).
- `Debug panel`: technische JSON-Ausgabe ein/ausblenden.

## Ergebnisbereich
- `Transcript`: erkannter Text
- `Answer`: Assistentenantwort
- Metadaten: Session, User, Sprache, Backend, Modell
- `Latency`: Audio Read, STT, LLM, TTS, Total
- `Debug JSON`: Rohdaten fuer Technik-Checks

## Statusanzeige
- `idle`, `recording`, `sending`, `thinking`, `speaking`, `listening`
- So sehen Sie immer, was der Agent gerade tut.

## Autoplay-Hinweis
- Manche Browser blockieren automatische Wiedergabe.
- Dann erscheint ein Banner.
- Einmal manuell auf `Play` klicken, danach laeuft der Flow normal.

## Downloads
- Transcript Download (`md/json`, je nach Server-Konfig)
- Protocol Download (strukturierter Export)

## Fehlerverhalten
- API-Fehler kommen als JSON.
- Keine HTML-Fehlerseite im `/api/*`-Pfad.
