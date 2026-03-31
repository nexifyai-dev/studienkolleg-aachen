# Governance: PR-Policy

> Übersicht: [README](../../README.md) · QA Gates: [docs/qa-release/gates.md](../qa-release/gates.md) · Wiki-Sync: [wiki-sync-policy.md](wiki-sync-policy.md)

## Pflichtinhalte jeder PR

- Problem und Root Cause
- Konkrete Änderung mit betroffenen Modulen
- Risikoanalyse und Seiteneffekte
- Testnachweise (ausgeführt, Ergebnis)
- Doku-Updates (falls Architektur/Flow/Rechte betroffen)

## Pflicht-Update bei Produkt-/Architektur-/Prozess-Relevanz

In derselben PR müssen aktualisiert werden:

- `README.md` (Einstieg/Scope/Setup/Betriebsgrenzen, falls betroffen)
- passende lokale Doku unter `docs/`
- lokale Wiki-Spiegelung unter `docs/wiki/`
- GitHub-Wiki
- `CHANGELOG.md`
- `docs/history/project-history.md`
- ADR (bei signifikanter Entscheidung) oder ADR-Verzichtsbegründung

Ohne diese Aktualisierungen gilt die PR als nicht mergefähig.

## Review-Anforderungen

- Mindestens ein technisches Review
- Bei Rollen-/Rechteänderung zusätzlich Security/Compliance-Review
- Bei AI-Änderung zusätzlich Screening-Owner-Review
- Bei Wiki-Sync-pflichtigen Änderungen zusätzlicher Doku-Review (Wiki Sync Owner oder Vertretung)

## Verknüpfungen

- [Blocking-Kriterien](blocking-criteria.md)
- [Dokumentationspflichten](documentation-duties.md)
- [Wiki-Sync-Policy](wiki-sync-policy.md)
- [ADR-Index](../adr/README.md)

## Dokumentverantwortung

- **Owner:** Engineering Management
- **Update-Prozess:** Bei jeder PR mit Prozessänderung, Review-Regeländerung oder neuen Qualitätsanforderungen.
