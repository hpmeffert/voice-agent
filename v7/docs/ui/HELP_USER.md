# Benutzer Dokumentation (V7.9.0)

Diese Dokumentation erklaert die Funktionen im UI und welche Wirkung jede Einstellung hat.

## Einstieg
- URL: `http://localhost:8081`
- Oben rechts im Help-Menue:
  - `Admin Token speichern`
  - `Benutzer Dokumentation` (diese Seite)
  - `Demo Guide`
  - `Admin Docs` (nur sichtbar bei Admin)
  - `Release Notes`

## Hauptfunktionen im UI
- `Record`: startet die Mikrofonaufnahme manuell.
- `Stop`: stoppt die laufende Aufnahme.
- `Send`: sendet die letzte Aufnahme an `/api/voice`.
- `Clear Session`: setzt lokale Session zurueck und startet neuen Konversationskontext.

## Identitaet und Kontext
- `User`: wird in localStorage gespeichert und identifiziert den Browser-Nutzer.
- `Session`: wird in localStorage gespeichert und erhaelt den Gespraechsverlauf.
- Wirkung:
  - gleiche Session => Folgefragen mit Verlauf
  - neue Session => frischer Kontext

## Einstellungen fuer Gespraechsfluss
- `Listen Mode`:
  - Wirkung: startet Aufnahme automatisch, stoppt bei Stille, sendet automatisch und startet nach TTS erneut.
- `Auto-stop on silence`:
  - Wirkung: Aufnahme stoppt automatisch nach Stillefenster.
- `Auto-send after stop`:
  - Wirkung: sendet automatisch nach Auto-Stop.
- `Silence threshold (ms)`:
  - Standard: `1300`
  - Wirkung: hoeherer Wert = wartet laenger auf weitere Sprache, niedriger = reagiert frueher.
- `Voice threshold (RMS)`:
  - Wirkung: Empfindlichkeit fuer Sprachbeginn/Sprachende.
  - Hoeher = weniger empfindlich gegen Hintergrundgeraeusche.
- `Max recording seconds`:
  - Wirkung: Sicherheitslimit fuer lange Aufnahmen.
- `TTS language`:
  - `Auto`: nutzt erkannte Sprache.
  - `de/en/sv/no/fi`: erzwingt die Sprechsprache.
  - `fr/it/es`: vorbereitet (coming soon).

## Admin-only Demo Steuerung
- `Demo Mode` (nur Admin):
  - Wirkung: startet einen stabilen Demo-Loop (`listen -> send -> speak -> listen`).
  - Listen Mode wird dabei automatisch erzwungen.
- `Debug panel` (nur Admin):
  - Wirkung: blendet `Debug JSON` ein/aus, damit Demos fuer Publikum sauberer wirken.
- `CRM Export` Toggle (nur Admin):
  - Wirkung: steuert Transcript-Exportfahigkeit fuer den User.

## Ergebnisbereich
- `Transcript`: erkannter gesprochener Text.
- `Answer`: Antwort des Assistenten.
- Metadaten: Session, User, Sprache, Backend, Modell.
- Latenzpanel: Audio Read, STT, LLM, TTS, Total.
- `Debug JSON`: technische Rohantwort fuer Analyse.
- Wirkung:
  - Im Alltag lesen Sie nur `Transcript` und `Answer`.
  - Fuer Technik-Checks nutzen Sie `Debug JSON` und die Latenzen.

## Status-Phasen (V7.6.0)
- `idle`: bereit, keine aktive Aufnahme.
- `recording`: Mikrofonaufnahme laeuft.
- `sending`: Audio wird an die API gesendet.
- `thinking`: STT/LLM verarbeitet die Anfrage.
- `speaking`: TTS-Antwort wird abgespielt.
- `listening`: wartet auf naechste Spracheingabe.

## Autoplay-Hinweis
- Manche Browser blockieren Auto-Play.
- Dann erscheint ein Banner mit Hinweis auf manuellen `Play`-Klick.
- Nach einem erfolgreichen manuellen Klick verschwindet der Hinweis.

## Exportfunktionen
- `CRM Export` Toggle:
  - Wirkung: aktiviert/deaktiviert Transcript-Export pro User.
- `Download Transcript`:
  - Format waehlbar (md/json je nach Serverkonfiguration).
- `Download Protocol`:
  - laedt strukturierten Protokoll-Export.

## Audio-Zuverlaessigkeit (V7.2.0)
- Browser nutzt bevorzugt `audio/webm;codecs=opus`.
- Server konvertiert Uploads mit ffmpeg in stabiles `16kHz mono WAV` vor Whisper.
- Wirkung: deutlich weniger STT-Decode-Fehler wie `EOFError: End of file`.

## Fehlerverhalten
- API-Fehler kommen als JSON.
- Auch bei API-Upstream-Problemen liefert `/api/*` JSON statt HTML-Seite.

## Hinweis fuer laufende Releases
- Bei jeder neuen V7-Version werden drei Help-Menue-Dokumente aktualisiert:
  - Benutzer Dokumentation
  - Demo Guide
  - Release Notes
