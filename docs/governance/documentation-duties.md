# Governance: Dokumentationspflichten

> Übersicht: [README](../../README.md) · PR-Policy: [pr-policy.md](pr-policy.md) · Wiki-Sync-Policy: [wiki-sync-policy.md](wiki-sync-policy.md)

## Pflicht zur synchronen Dokumentation

Folgende Änderungen erfordern Doku-Update in derselben PR:

- Architektur-/Integrationsänderungen
- Rollen-/Rechte- oder Routing-Anpassungen
- Workflow-/Task-/Messaging-Änderungen
- AI-Screening-Regeln oder Entscheidungsgrenzen
- Release-/Rollback- und Governance-Prozesse
- Änderungen mit Auswirkungen auf Wiki-Navigation oder Betriebswissen

## Verbindliche Update-Ziele

Bei Pflichtänderungen sind parallel zu aktualisieren:

1. passende Primärdokumente im Repo (`README`, `docs/`)
2. lokale Wiki-Spiegelstruktur (`docs/wiki/`)
3. GitHub-Wiki (`studienkolleg-aachen.wiki.git`)
4. [Changelog](../../CHANGELOG.md)
5. [Project History](../history/project-history.md)
6. ADR oder ADR-Verzichtsbegründung

## Mindeststandard

- Betroffene Doku referenziert den Change bidirektional.
- Owner und Update-Prozess in jedem neuen/angepassten Dokument.
- Changelog-Eintrag bei user-facing oder prozessrelevanten Änderungen.
- Historien-Eintrag bei struktur- oder governance-relevanter Langzeitwirkung.
- ADR-Prüfung bei signifikanten Entscheidungen (Architektur/Provider/Screening/Workflow/Governance).

## AI-Lösungen: zusätzliche Dokumentationspflicht

Jede AI-Lösung oder jeder Agent muss bei relevanten Änderungen:

- Begründung der Änderung dokumentieren,
- betroffene Bereiche benennen,
- Datum, Kontext, Scope und Auswirkungen festhalten,
- Changelog und Historie pflegen,
- ADR-Pflicht aktiv prüfen,
- Wiki und Repo-Doku synchron halten.

## Verknüpfungen

- [Changelog](../../CHANGELOG.md)
- [Project History](../history/project-history.md)
- [ADR Template](../adr/adr-template.md)
- [Wiki-Spiegelstruktur](../wiki/README.md)

## Dokumentverantwortung

- **Owner:** Documentation Steward + Documentation Governance Lead
- **Update-Prozess:** Bei jeder PR mit strukturellen, produktrelevanten oder governance-kritischen Änderungen.
