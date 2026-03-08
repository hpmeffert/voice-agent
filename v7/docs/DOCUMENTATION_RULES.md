# Dokumentations-Regeln (verbindlich, V7+)

Diese Regeln gelten fuer alle bestehenden und zukuenftigen V7-Releases.

## Ziel
Jede Version muss so dokumentiert sein, dass auch neue Teammitglieder schnell starten koennen.

## Zielgruppen
- Benutzer (z. B. 16 Jahre, ohne tiefes Technik-Wissen)
- Demonstrator (Praesentationen, Live-Demos)
- Admin (Installation, Betrieb, Test)

## Pflicht bei JEDEM Release
Vor Merge/Tag muessen diese Seiten aktualisiert werden:
- `v7/docs/ui/HELP_USER.md`
- `v7/docs/ui/DEMO_GUIDE.md`
- `v7/docs/admin/HELP_ADMIN.md`
- `v7/docs/RELEASE.md` (konsolidierte Historie von V7.0.0 bis aktuell)

## Schreibstil (einfach und klar)
- Kurze Saetze, klare Begriffe, keine unnötigen Fachwoerter.
- Pro Funktion: "Was ist das?", "Wo finde ich das?", "Welche Wirkung hat das?".
- Admin-Seite immer mit:
  - Installation/Start
  - wichtige ENVs
  - konkrete Testbefehle
- Demo-Guide immer mit Story und Spannungsbogen.

## Qualitaets-Check vor Release
1. Help-Menue zeigt alle 4 Punkte korrekt:
   - Admin Token speichern
   - Benutzer Dokumentation
   - Demo Guide
   - Admin Docs
   - Release Notes
   - (optional nur Admin) Admin Settings
2. Inhalte passen zur aktuellen Version.
3. Release Notes enthalten alle V7-Versionen von `v7.0.0` bis aktuell.
