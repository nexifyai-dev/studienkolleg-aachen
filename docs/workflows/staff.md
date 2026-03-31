# Workflow: Staff

> Übersicht: [README](../../README.md) · Rollen: [docs/roles-and-permissions.md](../roles-and-permissions.md)

## Ziel

Operative Fallbearbeitung mit vollständigem Kontext (Historie, Anhänge, Aufgaben, AI-Hinweise).

## Ablauf

1. Intake-Queue / Kanban-Sichtung
2. Vollständigkeitsprüfung
3. Formale Vorprüfung
4. AI-Empfehlung prüfen
5. Staff-Entscheidung dokumentieren
6. Rückfragen/Kommunikation
7. Übergabe oder Abschluss

## Kritische UX-Punkte

- Quick Actions für wiederkehrende Aktionen.
- Such-/Filter-/Selektionslogik ohne Datenverlust.
- Historie revisionssicher halten.

## Verknüpfungen

- [Evidenzmodell](../ai-screening/evidence-model.md)
- [Rollback-Strategie](../qa-release/rollback.md)
- [Blocking-Kriterien](../governance/blocking-criteria.md)

## Dokumentverantwortung

- **Owner:** Operations Lead
- **Update-Prozess:** Bei jeder PR mit Staff-Queue, Kanban, Tasks, Messaging, Entscheidungslogik oder Detailansicht.
