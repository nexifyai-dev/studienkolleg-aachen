# Dokumentationsarchitektur (Source of Truth)

Stand: 2026-03-30

## Ziel
Diese Struktur stellt sicher, dass Projektwissen versioniert, nachvollziehbar und auditierbar bleibt.

## Bereiche
- `docs/project/` – Projektstatus, Scope, Historie, Governance.
- `docs/architecture/` – Systemarchitektur, Modulgrenzen, Datenflüsse.
- `docs/roles/` – Rollen, Berechtigungen, Sichtbarkeiten, Consent-Grenzen.
- `docs/workflows/` – End-to-End-Prozesse (Bewerbung, Tasks, Messaging, Screening).
- `docs/ai/` – AI-Provider, Screeninglogik, Grenzen, Audit.
- `docs/operations/` – Setup, Environments, Release, Runbook, Blocker.
- `docs/testing/` – Teststrategie, Quality Gates, DoD.
- `docs/adr/` – Architecture Decision Records.

## Source-of-Truth-Regel
Pro Thema gilt genau ein primäres Dokument:
- Projektstatus/Scope: `docs/project/overview.md`
- Architektur: `docs/architecture/overview.md`
- Rollen/Rechte: `docs/roles/roles-and-permissions.md`
- Workflows: `docs/workflows/core-workflows.md`
- AI/Screening: `docs/ai/screening-and-provider.md`
- Betrieb/Release: `docs/operations/release-and-operations.md`
- QA/DoD: `docs/testing/qa-strategy.md`
- Entscheidungen: `docs/adr/*.md`
- Änderungsverlauf: `CHANGELOG.md` + `docs/project/history.md`

## Verhältnis zu Legacy-Dokumenten im Repo-Root
Historische/analytische Root-Dokumente (`01_...md` bis `20_...md`) bleiben erhalten als Referenzmaterial. Operative Wahrheit für laufende Änderungen liegt ab jetzt in `docs/` plus `CHANGELOG.md`.
