# ADR-0002: Rollenmodell und serverseitiges RBAC

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Mehrere Nutzergruppen benötigen unterschiedliche Sichtbarkeit und Bearbeitungsrechte.

## Problem
Clientseitige Einschränkungen allein reichen nicht für Datenschutz und Betriebssicherheit.

## Entscheidung
Serverseitige Rollenprüfung (`require_roles`) plus objektspezifische Ownership-/Assignment-Checks.

## Begründung
Durchsetzung kritischer Rechte unabhängig vom Frontendzustand.

## Alternativen
Nur UI-basierte Checks (abgelehnt), extrem feingranulares ABAC in v1 (zu komplex).

## Auswirkungen
Stabilere Zugriffskontrolle, zusätzlicher Implementierungsaufwand je Endpunkt.

## Betroffene Dateien/Bereiche
`backend/deps.py`, Router mit Zugriffskontrollen, Rollen-Dokumentation.

## Risiken / Folgeaufgaben
Laufende Matrixpflege bei neuen Rollen/Funktionen.
