# Teststrategie

> Übersicht: [README](../../README.md) · Gates: [gates.md](gates.md)

## Testpyramide

- Unit Tests für Kernlogik (inkl. AI-Regelpfade)
- Integrationstests für API, Auth, Tasks, Messaging
- UI-/Workflow-Tests für Rollenportale
- Smoke-Checks vor Release

## Pflicht-Checks pro Änderungsart

- **Backend:** Syntax/Imports + gezielte Feature-Tests
- **Frontend:** Build + relevante Komponenten-/Flow-Tests
- **Routing/Layout/Auth/i18n/AI/Tasks/Messaging:** immer gezielt regressionsprüfen

## Evidenzpflicht

Alle Release-Entscheidungen müssen mit Testreferenzen und bekannten Restrisiken dokumentiert sein.

## Verknüpfungen

- [Rollback](rollback.md)
- [Evidenzmodell](../ai-screening/evidence-model.md)
- [Projekt-Historie](../history/project-history.md)

## Dokumentverantwortung

- **Owner:** Test Engineering Owner
- **Update-Prozess:** Bei jeder PR mit neuem Risiko, Testlücke, neuer Testart oder geänderter Definition of Done.
