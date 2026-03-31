# Changelog

Alle relevanten Änderungen an Produkt, Prozessen und Governance werden hier dokumentiert.

## [Unreleased]

### Added

- Produktionsfähige Root-Einstiegsdokumentation mit Systemüberblick, Rollen/Portale, Betriebsgrenzen und Release-Status.
- Neue `docs/`-Struktur für Architektur, Rollen/Rechte, Workflows, AI-Screening, QA/Release, Governance und ADR.
- Projekthistorie unter `docs/history/project-history.md`.
- Neue verbindliche Wiki-Sync-Policy unter `docs/governance/wiki-sync-policy.md`.
- Lokale Wiki-Spiegelstruktur unter `docs/wiki/` mit Seiten für System Overview, Workflows, Roles & Rights, AI Screening, Operations und Release/Go-Live.
- ADR zur Verankerung von Wiki-Sync und Repo-Primärdoku-Prinzip hinzugefügt.

### Changed

- Dokumentationssystem auf bidirektionale Verlinkung ausgerichtet, um Parallel-Truth zu verhindern.
- README um verbindliche Wiki-Sync-Regeln und Mirror-Verweise erweitert.
- Governance-Dokumente (`documentation-duties`, `pr-policy`) um verpflichtende Sync- und Review-Regeln ergänzt.
- Historie um Synchronisationspflicht und Governance-Entscheidung erweitert.

## Verknüpfungen

- [README](README.md)
- [Project History](docs/history/project-history.md)
- [Wiki Mirror](docs/wiki/README.md)
- [Go-Live Checklist](release/golive_checklist.yaml)

## Dokumentverantwortung

- **Owner:** Release & Documentation Management
- **Update-Prozess:** Bei jeder PR mit user-facing Änderung, Architektur-/Prozessänderung oder Release-relevantem Fix; bei wiki-relevanten Änderungen immer synchron mit Wiki-Mirror und GitHub-Wiki.
