# Benutzer Dokumentation (V8.1.0)

Diese Seite erklaert die Bedienung so, dass auch neue Teammitglieder sofort loslegen koennen.

## Welche Oberflaeche nutze ich?
- Admin UI: `http://localhost:8082`
  - Voller Funktionsumfang fuer Betrieb, Tests und Auswertung.
- Customer UI: `http://localhost:8083`
  - Schlanke Ansicht fuer Gespraech, ohne Admin-Menues.

## Hauptfunktionen im Bildschirm
- `Record`: startet die Mikrofonaufnahme.
- `Stop`: beendet die laufende Aufnahme.
- `Send`: sendet Audio/Text an die API.
- `Clear Session`: startet einen neuen Dialogkontext.
- `Export`/`Protocol`: laedt Gespraechsverlauf herunter (falls aktiviert).

## Einstellungen und Wirkung
- `Backend` / `Model`
  - Waehlt das Sprachmodell fuer Antworten.
  - Kleinere Modelle antworten schneller, groessere oft detailreicher.
- `Auto-stop`
  - Beendet Aufnahme automatisch nach Stille.
- `Auto-send`
  - Sendet nach Auto-Stop direkt, ohne zusaetzlichen Klick.
- `Silence threshold (ms)`
  - Standard: `1300`.
  - Hoeher = laenger warten bis Ende erkannt wird.
  - Niedriger = schnelleres Stoppen, aber hoeheres Risiko fuer zu fruehes Ende.
- `TTS language`
  - Sprache der Sprachausgabe.

## Statusanzeige verstehen
- `idle`: bereit.
- `recording`: Mikrofon aktiv.
- `sending`: Anfrage wird uebertragen.
- `thinking`: Modell berechnet Antwort.
- `speaking`: Audio wird abgespielt.
- `listening`: Listen-Mode aktiv und wartet auf Sprache.

## Help-Menue
- `Admin Token speichern`: speichert Admin-Token lokal im Browser.
- `Benutzer Dokumentation`: diese Seite.
- `Demo Guide`: gefuehrter Vorfuehrablauf mit Story.
- `Admin Docs`: Betriebs- und Testanleitung fuer Admins.
- `Release Notes`: Uebersicht aller Releases ab V7.0.0.

## Typische Probleme
- Keine Antwort: zuerst `http://localhost:8082/api/health` pruefen.
- Kein Audio: Browser-Mikrofonrechte kontrollieren.
- Falsche Sprache: `TTS language` und UI-Sprache pruefen.
