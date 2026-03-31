# Governance: Blocking-Kriterien

> Übersicht: [README](../../README.md) · PR-Policy: [pr-policy.md](pr-policy.md)

## Harte Blocker (Merge verboten)

- Fehlende oder rote kritische Tests
- Ungelöste Rollen-/Rechte-Regression
- AI-Entscheidungsgrenzen verletzt
- Fehlende Dokumentation bei Architektur-/Flow-Änderung
- Secrets im Code oder unsichere Konfiguration

## Bedingte Blocker

- Nicht-kritische Testlücken ohne dokumentierten Mitigationsplan
- UX-Inkonsistenz in Kernportalen ohne Follow-up Issue

## Verknüpfungen

- [QA Gates](../qa-release/gates.md)
- [Rollen und Rechte](../roles-and-permissions.md)
- [Entscheidungsgrenzen AI](../ai-screening/decision-boundaries.md)

## Dokumentverantwortung

- **Owner:** Technical Program Management
- **Update-Prozess:** Bei jeder PR mit veränderten Qualitätskriterien, Risikoeinstufung oder Compliance-Anforderungen.
