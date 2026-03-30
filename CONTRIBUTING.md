# Contributing Guide

## Arbeitsprinzipien
- Stabilisieren vor Erweitern.
- Bestehende Portal-/Routing-Architektur beibehalten.
- Keine regressiven Änderungen an Rollen-/Rechteflüssen.

## Pflicht bei Änderungen
1. Relevante Tests/Checks ausführen und Ergebnis dokumentieren.
2. README/Fachdoku bei Scope- oder Verhaltensänderungen aktualisieren.
3. ADR erstellen, wenn Grundsatzentscheidung betroffen ist.
4. `CHANGELOG.md` aktualisieren.
5. Offene Risiken/Blocker explizit benennen.

## Branch-/PR-Regeln
- Kleine, nachvollziehbare Commits mit fachlichem Kontext.
- PR-Text muss enthalten: Was, Warum, Risiko, Testnachweis, offene Punkte.
- Keine Geheimnisse/Schlüssel im Code oder in der Doku.

## Dokumentations-Referenzen
- `docs/project/documentation_policy.md`
- `docs/adr/README.md`
- `docs/testing/qa-strategy.md`
