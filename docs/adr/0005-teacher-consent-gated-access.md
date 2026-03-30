# ADR-0005: Teacher-Zugriff nur assignment- und consent-gated

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Lehrkräfte benötigen begrenzte Einsicht in betreute Fälle.

## Problem
Ungefilterter Lehrerzugriff wäre datenschutzrechtlich riskant.

## Entscheidung
Teacher erhält Zugriff nur bei aktiver Zuweisung und Consent; Datenscope bleibt reduziert.

## Begründung
Need-to-know und Zweckbindung werden technisch erzwingbar.

## Alternativen
Globaler Teacher-Read-Access (abgelehnt).

## Auswirkungen
Zusätzliche Prüfpfade in Backend und UI-Hinweise bei gesperrten Fällen.

## Betroffene Dateien/Bereiche
Teacher-Router, Consent-Flow, Rollenmatrix.

## Risiken / Folgeaufgaben
Consent-Widerruf muss sofortige Entzugseffekte garantieren.
