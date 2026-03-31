# Projekt-Historie

> Übersicht: [README](../../README.md) · Changelog: [CHANGELOG.md](../../CHANGELOG.md) · Wiki-Mirror: [docs/wiki/README.md](../wiki/README.md)

## Historischer Verlauf (Dokumentationssicht)

- **2026-03-31:** Einführung einer produktionsfähigen, strukturierten Dokumentationslandschaft (`README`, `docs/`, `CHANGELOG`).
- **2026-03-31:** Verbindliche Wiki-Sync-Governance eingeführt: GitHub-Wiki als verpflichtende Sekundärdoku mit lokaler Spiegelstruktur unter `docs/wiki/`, plus PR-Pflicht zur synchronen Pflege von README, Docs, Wiki, Changelog, Historie und ADR.
- **2026-03-31:** Audit-Reality-Check gegen den tatsächlichen Repo-Stand dokumentiert (`docs/qa-release/reality-check-2026-03-31.md`) und P0-Block 1 umgesetzt (Credential-Redaktion in `test_reports`, Entfernung versionierter `storage/messages`-Artefakte, Ausweitung des Credential-Scans auf alle getrackten Textdateien).

## Warum diese Historie?

Die Projekthistorie gibt einen narrativen Überblick über Strukturentscheidungen, während der Changelog die detaillierte Änderungsliste führt.

## Verknüpfungen

- [Architektur-Überblick](../architecture/overview.md)
- [QA & Release Gates](../qa-release/gates.md)
- [Governance PR-Policy](../governance/pr-policy.md)
- [Wiki-Sync-Policy](../governance/wiki-sync-policy.md)

## Dokumentverantwortung

- **Owner:** Product Operations
- **Update-Prozess:** Bei jeder PR mit relevanter Produkt-, Prozess- oder Governance-Änderung mit Langzeitwirkung; bei Wiki-Sync-pflichtigen Änderungen immer zusammen mit dem Changelog aktualisieren.
