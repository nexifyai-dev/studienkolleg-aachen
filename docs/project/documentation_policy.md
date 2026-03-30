# Verbindliche Dokumentationsrichtlinie

Gültig ab: 2026-03-30

## Zweck
Jede relevante Änderung muss nachvollziehbar, begründet, versioniert und überprüfbar dokumentiert werden – für Menschen und AI-Agenten.

## Pflichtregeln
1. Keine relevante Änderung ohne Begründung (Warum + Auswirkungen).
2. ADR-Pflicht für Architektur-, Workflow-, Rollen-, Provider-, Security- und UI-Grundsatzentscheidungen.
3. Changelog-Pflicht für relevante funktionale/operative Änderungen.
4. README-/Fachdoku-Pflicht bei neuen Modulen, Flows oder Betriebsänderungen.
5. Test-/Validierungsnachweise müssen dokumentiert werden.
6. Datum, Scope und Kontext jeder relevanten Änderung erfassen.
7. Keine stillen Repo-Änderungen.
8. Keine halben Implementierungen ohne dokumentierte Grenzen/Risiken.
9. Keine Widersprüche zwischen Code, README, PRD, Memory und Fehlerregister stehen lassen.
10. Auswirkungen auf Rollen, Daten, Prozesse und UI immer mitprüfen.

## Source-of-Truth-Regeln
- `docs/` enthält die operative Dokumentationswahrheit.
- `CHANGELOG.md` enthält versionierte Änderungsereignisse.
- `docs/adr/` enthält Entscheidungsbegründungen.
- `memory/` bleibt als historische Arbeitsreferenz, darf operative Wahrheit nicht widersprechen.

## AI-spezifische Zusatzpflichten
- Keine Behauptung ungeprüfter Fakten.
- Keine finale Entscheidungsbehauptung bei KI-Vorprüfungen.
- Providerwechsel oder Modelländerung nur mit ADR + Changelog + Migrationshinweis.

## Compliance-/Audit-Readiness
Dokumentation muss den Zustand so abbilden, dass ein externer Reviewer ohne implizites Teamwissen Architektur, Entscheidungen und Betriebszustand nachvollziehen kann.
