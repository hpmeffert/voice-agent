# Demo Guide (V7.10.0)

Ziel: in 6-10 Minuten einen klaren Spannungsbogen zeigen, der Technik UND Business-Nutzen sichtbar macht.

## Story-Start
Stellen Sie sich vor, ein Kunde spricht spontan auf Deutsch, wechselt dann ins Franzoesische und erwartet trotzdem sofort eine flussige Antwort.

## Demo-Flow mit Spannungsbogen
1. Einstieg (Neugier)
- Satzvorschlag: "Was waere, wenn ein Agent mehrsprachig zuhoert und sofort passend antwortet?"
- Zeigen Sie das UI kurz: User, Session, Listen Mode, TTS language, Help-Menue.

2. Aha-Moment (Hands-free)
- `Listen Mode` aktivieren.
- Kurz sprechen, dann Pause.
- Sichtbar machen: Auto-Stop -> Auto-Send -> Antwort wird gesprochen -> Auto-Resume.

3. Mehrsprachigkeit (V7.10.0 Kernfeature)
- `Lang` auf `fr` stellen (UI-Beschriftung wechselt sofort).
- Eine kurze franzoesische Frage sprechen.
- Ergebnis zeigen: Transcript + Antwort + TTS in `fr`.
- Dasselbe mit `it` und `es` wiederholen.

4. Transparenz (Performance)
- Unter `Result` die Latenzwerte erklaeren:
  - `Audio Read`, `STT`, `LLM`, `TTS`, `Total`.
- Satzvorschlag: "So sehen wir live, wo Zeit verloren geht, statt nur zu raten."

5. Betriebssicherheit (Admin)
- Als Admin `Admin Metrics` oeffnen und `Refresh` klicken.
- Zeigen, dass Requests mit Zeitwerten protokolliert werden.
- Optional: `Admin Settings` oeffnen und einen Wert speichern.

6. Abschluss (Nutzen)
- Satzvorschlag: "Das ist kein Einzel-Chat, sondern ein kontrollierbarer, dokumentierbarer Gespraechsfluss fuer den echten Betrieb."

## Drei kurze Sprach-Mini-Demos
1. FR
- UI Lang: `fr`
- Prompt: "Bonjour, peux-tu resumer ma demande en une phrase ?"
- Erwartung: FR Transcript, FR Antwort, FR TTS.

2. IT
- UI Lang: `it`
- Prompt: "Ciao, dammi una risposta breve e chiara."
- Erwartung: IT Transcript, IT Antwort, IT TTS.

3. ES
- UI Lang: `es`
- Prompt: "Hola, explica en una frase lo que entendiste."
- Erwartung: ES Transcript, ES Antwort, ES TTS.

## Checkliste vor Publikum
- `curl -s http://localhost:8081/api/health` liefert `{"status":"ok"}`.
- Mikrofonfreigabe im Browser ist erlaubt.
- Piper-Voices vorhanden (`/tts/voices`).
- Ein konstanter Demo-User bleibt waehrend der gesamten Demo aktiv.
