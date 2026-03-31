# AI-Screening: Regelbasis

> Übersicht: [README](../../README.md) · Architektur: [docs/architecture/overview.md](../architecture/overview.md)

## Zweck

Die Regelbasis definiert, welche Kriterien technisch vorprüfbar sind und welche ausschließlich als Empfehlung ausgegeben werden.

## Regelklassen

1. **Vollständigkeit**
   - Pflichtdokumente vorhanden/nicht vorhanden
   - Fehlende Metadaten
2. **Formale Vorprüfung**
   - Dateiformate, Lesbarkeit, formale Gültigkeitsfenster
3. **KI-Empfehlung**
   - Mustererkennung und Risikohinweise
4. **Staff-Entscheidung**
   - final und begründungspflichtig

## Verbotene Ableitung

Aus einem bloßen Upload darf keine fachliche Anerkennung oder automatische Zulassung abgeleitet werden.

## Verknüpfungen

- [Entscheidungsgrenzen](decision-boundaries.md)
- [Evidenzmodell](evidence-model.md)
- [Staff-Workflow](../workflows/staff.md)

## Dokumentverantwortung

- **Owner:** AI Screening Product Owner
- **Update-Prozess:** Bei jeder PR mit Regelmatrix-, Provider-, Prompt-, Validierungs- oder Scoring-Änderung.
