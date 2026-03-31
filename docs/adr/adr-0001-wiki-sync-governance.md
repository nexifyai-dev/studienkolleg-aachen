# ADR-0001: Wiki-Sync-Governance und Repo als Primärdokumentation

- **Status:** Accepted
- **Datum:** 2026-03-31
- **Entscheider:** Architecture Board, Documentation Governance Lead

## Kontext

Die Projektdokumentation war lokal strukturiert, aber die GitHub-Wiki war nicht verbindlich als synchronisierte Außensicht im Prozess verankert. Dadurch bestand Risiko für Wissensinseln und Divergenzen zwischen Repo-Dokumentation, Wiki und operativer Kommunikation.

## Entscheidung

1. Die GitHub-Wiki (`https://github.com/nexifyai-dev/studienkolleg-aachen.wiki.git`) wird als verpflichtende Sekundärdokumentation geführt.
2. Das Repo bleibt Primärbasis für reviewbare, versionierte und auditierbare Dokumentation.
3. Eine lokale Spiegelstruktur unter `docs/wiki/` wird verbindlich eingeführt.
4. Relevante Änderungen müssen synchron in README, Docs, Wiki-Mirror, GitHub-Wiki, Changelog, Historie und ggf. ADR gepflegt werden.
5. Konflikte zwischen Wiki und Repo werden immer zugunsten des Repo-Standes aufgelöst.

## Konsequenzen

- PRs erhalten eine explizite Dokumentations- und Wiki-Sync-Pflicht.
- Governance- und Review-Prozess werden um einen dokumentierten Sync-Nachweis erweitert.
- Schatten-Dokumentation in der Wiki ohne Repo-Pendant ist nicht zulässig.

## Betroffene Bereiche

- Governance-Dokumente (`docs/governance/*`)
- Einstieg und Navigationsdokumente (`README.md`, `docs/wiki/*`)
- Nachvollziehbarkeit (`CHANGELOG.md`, `docs/history/project-history.md`)

## Verknüpfungen

- [Wiki-Sync-Policy](../governance/wiki-sync-policy.md)
- [Dokumentationspflichten](../governance/documentation-duties.md)
- [PR-Policy](../governance/pr-policy.md)
- [Changelog](../../CHANGELOG.md)
- [Project History](../history/project-history.md)
