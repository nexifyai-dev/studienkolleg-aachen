# Rollback-Strategie

> Übersicht: [README](../../README.md) · Gates: [gates.md](gates.md)

## Ziel

Schnelle und sichere Rücknahme bei regressivem Verhalten in produktionsnahen oder produktiven Umgebungen.

## Rollback-Trigger

- Rollen-/Rechteverletzung
- Entscheidungslogik fehlerhaft (insbesondere AI-Grenzverletzung)
- Datenintegritätsproblem
- kritischer UX-/Routing-Ausfall

## Vorgehen (Kurzform)

1. Incident klassifizieren
2. Feature/Release isolieren
3. Letzten stabilen Stand deployen
4. Datenkonsistenz prüfen
5. Stakeholder informieren
6. RCA und Präventionsmaßnahmen dokumentieren

## Verknüpfungen

- [Go-Live Checklist](../../release/golive_checklist.yaml)
- [Blocking-Kriterien](../governance/blocking-criteria.md)
- [Changelog](../../CHANGELOG.md)

## Dokumentverantwortung

- **Owner:** Release Manager
- **Update-Prozess:** Bei jeder PR mit Migrations-, Deployment-, Datenmodell- oder kritischen Workflow-Änderungen.
