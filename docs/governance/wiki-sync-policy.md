# Governance: Wiki-Sync-Policy

> Übersicht: [README](../../README.md) · Dokumentationspflichten: [documentation-duties.md](documentation-duties.md) · PR-Policy: [pr-policy.md](pr-policy.md)

## Zweck der Wiki

Die GitHub-Wiki (`https://github.com/nexifyai-dev/studienkolleg-aachen.wiki.git`) ist die navigierbare Außenansicht für Betriebswissen, Onboarding und schnelle Orientierung. Sie ergänzt die Repo-Dokumentation, ersetzt sie aber nicht.

## Abgrenzung: Repo-Doku vs. Wiki

- **Repo-Dokumentation (primär):** reviewbar, versioniert, PR-pflichtig, langfristig auditierbar.
- **GitHub-Wiki (sekundär/operativ):** navigierbare Spiegelung, kuratierte Einstiegssicht, operative Leseführung.
- Bei Konflikten gilt stets zuerst die Repo-Dokumentation als verbindliche Primärbasis.

## Synchronisationspflicht

Jede relevante Änderung muss innerhalb derselben PR/Änderungswelle in allen betroffenen Zielen aktualisiert werden:

1. passende lokale Dokumente unter `docs/`
2. Spiegelstruktur unter `docs/wiki/`
3. GitHub-Wiki
4. `CHANGELOG.md`
5. `docs/history/project-history.md`
6. ADR (wenn Entscheidung langlebig/signifikant ist)

## Owner

- **Wiki Sync Owner:** Documentation Governance Lead
- **Repo Primär-Doku Owner:** Engineering + Architecture Board
- **Freigabe bei AI-/Governance-Themen:** Screening Owner + Engineering Management

## Update-Prozess

1. Änderung analysieren (Produkt, Architektur, Workflow, Governance, QA/Release).
2. Trigger bestimmen (Wiki-/README-/Docs-/History-/ADR-Pflicht).
3. Lokale Primärdoku aktualisieren.
4. Spiegelstruktur in `docs/wiki/` aktualisieren.
5. GitHub-Wiki synchronisieren (gleicher Inhalt oder klarer Referenzzustand).
6. Changelog + Historie ergänzen.
7. ADR erfassen oder ADR-Verzicht explizit dokumentieren.
8. Review mit Doku-Checkliste abschließen.

## Reviewpflicht

Eine PR mit relevanten Änderungen ist erst reviewfähig, wenn ein dokumentierter Wiki-Sync-Nachweis enthalten ist. Ohne diesen Nachweis gilt die PR als unvollständig.

## Pflicht-Trigger für Dokumentationsupdates

Ein Pflicht-Update wird ausgelöst bei Änderungen an:

- Produktumfang, Portal-Flows, Rollen/Rechten
- Architektur, Integrationen, Providern, Datenflüssen
- AI-Screening-Regeln, Entscheidungsgrenzen, Governance
- QA-, Release-, Rollback- oder Go-Live-Prozessen
- Betriebsgrenzen, Compliance-relevanten Standards

## Konfliktmanagement Wiki vs. Repo

- Konflikte werden per PR gegen das Repo gelöst.
- Nach Merge wird die Wiki auf den gemergten Repo-Stand synchronisiert.
- Abweichungen ohne Repo-Änderung sind zu markieren und innerhalb eines Arbeitstags zu beheben.

## Verbot von Schatten-Dokumentation

Die Wiki darf keine unversionierte Schatten-Dokumentation enthalten. Dauerhaft relevantes Wissen muss im Repo nachvollziehbar erfasst sein.

## Verknüpfungen

- [Wiki-Spiegelstruktur](../wiki/README.md)
- [README](../../README.md)
- [Changelog](../../CHANGELOG.md)
- [Project History](../history/project-history.md)
- [ADR-Index](../adr/README.md)

## Dokumentverantwortung

- **Owner:** Documentation Governance Lead (Wiki Sync Owner)
- **Update-Prozess:** Bei jeder PR mit Produkt-, Architektur-, Workflow-, QA-/Release- oder Governance-Relevanz.
