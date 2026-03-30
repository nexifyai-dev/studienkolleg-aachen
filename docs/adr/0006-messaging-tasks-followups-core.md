# ADR-0006: Messaging, Tasks und Follow-ups als CRM-Kern

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Bewerbungsbearbeitung erfordert koordinierte Kommunikation und Aufgabensteuerung.

## Problem
Ohne Historie/Zuweisung/Fälligkeit gehen Fälle operativ verloren.

## Entscheidung
Tasks, Messaging und Follow-ups als erstklassige Kernmodule inkl. Historisierung und Anhängen.

## Begründung
Operative Nachvollziehbarkeit und Teamarbeit auf Fallbasis.

## Alternativen
Nur Kanban-Status ohne Aufgabensystem (abgelehnt).

## Auswirkungen
Mehr Collections/States, aber belastbarer CRM-Betrieb.

## Betroffene Dateien/Bereiche
`backend/routers/tasks.py`, Messaging-/Follow-up-Router, Staff-UI.

## Risiken / Folgeaufgaben
Performance bei großen Verläufen beobachten.
