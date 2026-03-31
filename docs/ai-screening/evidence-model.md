# AI-Screening: Evidenzmodell

> Übersicht: [README](../../README.md) · QA/Release: [docs/qa-release/test-strategy.md](../qa-release/test-strategy.md)

## Ziel

Jede Entscheidung muss auf nachvollziehbaren, prüfbaren Evidenzbausteinen basieren.

## Evidenzklassen

- **E1: Rohdaten** — Uploads, Metadaten, Zeitstempel
- **E2: Formale Checks** — Validierungs- und Vollständigkeitsergebnisse
- **E3: KI-Hinweise** — Empfehlungen inkl. Konfidenz-/Unsicherheitsindikator
- **E4: Menschliche Begründung** — Staff-Entscheidnotiz und ggf. Admin-Freigabe

## Mindestanforderung für finale Entscheidungen

- Mindestens E2 + E4
- Bei KI-Nutzung zusätzlich E3 inkl. Unsicherheitsbehandlung

## Verknüpfungen

- [Regelbasis](rule-basis.md)
- [Entscheidungsgrenzen](decision-boundaries.md)
- [Rollback-Strategie](../qa-release/rollback.md)

## Dokumentverantwortung

- **Owner:** Quality Engineering + Admissions Operations
- **Update-Prozess:** Bei jeder PR mit Änderungen an Audit, Decision Logging, AI-Ausgabeformat oder Statusübergängen.
