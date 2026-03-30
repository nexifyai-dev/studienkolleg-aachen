# ADR-0008: Vier-Schichten-Modell für Screeningentscheidungen

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
KI-Ausgaben können operativ fälschlich als Endentscheidung interpretiert werden.

## Problem
Rechtlich und fachlich muss Finalentscheidung beim Staff verbleiben.

## Entscheidung
Verpflichtende Trennung in `completeness`, `formal_precheck`, `ai_recommendation`, `staff_decision`.

## Begründung
Klare Verantwortlichkeit, weniger Fehlinterpretation, bessere Auditspur.

## Alternativen
Ein einzelnes KI-Gesamtergebnis (abgelehnt).

## Auswirkungen
Mehr strukturierte Felder in Screening-Ausgaben und UI.

## Betroffene Dateien/Bereiche
`backend/services/ai_screening.py`, Staff Applicant Detail, AI-Dokumentation.

## Risiken / Folgeaufgaben
Staff muss Bedeutung der Ebenen kennen (Onboarding/Training).
