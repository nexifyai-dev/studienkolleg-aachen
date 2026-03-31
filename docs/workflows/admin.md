# Workflow: Admin

> Übersicht: [README](../../README.md) · Rollen: [docs/roles-and-permissions.md](../roles-and-permissions.md)

## Ziel

Systemweite Steuerung von Nutzern, Richtlinien, Auditierbarkeit und Betriebsstabilität.

## Ablauf

1. Rollen-/Policy-Management
2. Monitoring & Audit
3. Governance-Freigaben
4. Release-Entscheidung anhand Gates
5. Post-Release Kontrolle

## Kritische UX-Punkte

- Konsistente Layout-/Interaktionsmuster zu Staff/Applicant.
- Kein Umgehen von Freigabe- und Auditprozessen.

## Verknüpfungen

- [PR-Policy](../governance/pr-policy.md)
- [QA-Gates](../qa-release/gates.md)
- [ADR-Index](../adr/README.md)

## Dokumentverantwortung

- **Owner:** Platform Admin Lead
- **Update-Prozess:** Bei jeder PR mit Admin-UI, Policy, Audit, Rollen- oder Release-Steuerungsänderung.
