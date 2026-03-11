# Kunden Handbuch (DE) - Voice Agent V9

## Was macht der Kunden-Client?
Der Kunden-Client ist die Seite fuer Endkunden. Du kannst dort:
- per **Sprache** sprechen (Record / Listen Mode),
- per **Chat** schreiben,
- Antworten als **Text + Audio** bekommen.

Das Ziel: Du kannst mit dem System sprechen oder schreiben, ohne Technikdetails kennen zu muessen.

## Oberflaeche im Ueberblick
- URL: `http://localhost:8086`
- Kopfzeile:
  - `Voice Agent Customer <Version>`
  - Status (`idle`, `recording`, `uploading`, `speaking`)
  - `UI` Dropdown fuer Oberflaechensprache (`de`/`en`)
  - `?` Button = diese Hilfe
- Eingabebereich:
  - `User` und `Session`
  - `Record`, `Stop`, `Send Audio`
  - `Auto-send after recording`
  - `Listen Mode`
  - `Kundensprache`
  - `TTS`
- Chatfeld:
  - Text eingeben
  - `Send Text`

## Schritt fuer Schritt: Voice (Sprechen)
1. Oeffne den Kunden-Client.
2. Pruefe `Kundensprache`:
   - `auto` (empfohlen) oder manuell `de/en/no/sv/fi`.
3. Klicke `Record`.
4. Sprich deinen Satz deutlich.
5. Klicke `Stop` (oder nutze Listen Mode mit automatischem Stop).
6. Bei `Auto-send after recording = AN` wird direkt gesendet.
   - Sonst manuell `Send Audio` klicken.
7. Warte auf die Antwort:
   - Text erscheint im Verlauf.
   - Audio wird ueber den Player abgespielt.

## Schritt fuer Schritt: Chat (Schreiben)
1. Text im Feld `Text eingeben und senden...` eingeben.
2. `Send Text` klicken.
3. Antwort lesen und optional als Audio hoeren.

## Wichtige Einstellungen einfach erklaert
- `UI`:
  - Aendert nur die Oberflaechentexte im Kunden-Client.
  - Aendert **nicht** die erkannte Eingabesprache oder TTS-Lane-Logik.
- `Kundensprache`:
  - `auto` = System erkennt Sprache selbst.
  - Manuell = feste Kundensprache.
- `TTS`:
  - Steuert die Ausgabesprache fuer gesprochene Antworten.
  - `auto` nutzt das erkannte Profil.
- `Auto-send after recording`:
  - AN = schneller Ablauf ohne zusaetzlichen Klick.
- `Listen Mode`:
  - Dauerbetrieb: aufnehmen, bei Stille stoppen, senden.
  - Standard-Stillewert ist `1300 ms`.

## Typischer Ablauf (Beispiel)
1. Kunde spricht auf Deutsch.
2. System verarbeitet die Eingabe.
3. Agent antwortet intern in seiner Sprache.
4. Kunde bekommt die Antwort wieder in Kundensprache (Text + Stimme).

## Fehlerbehebung (kurz)
- Kein Mikrofon:
  - Browser-Mikrofonrechte erlauben.
- Kein Ton:
  - Lautstaerke und Browser-Autoplay pruefen.
- Keine Antwort:
  - Statuszeile pruefen, ggf. neue Session starten.
- Falsche Sprache:
  - `Kundensprache` und `TTS` pruefen.
