# ADR-0001: Multi-Portal-Architektur mit gemeinsamem Frontend

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Plattform bedient öffentliche Besucher, Bewerber, Staff/Teacher, Admin und Partner mit unterschiedlichen Anforderungen.

## Problem
Einheitliche Codebasis sollte konsistente UX ermöglichen, ohne rollenfremde Daten freizugeben.

## Entscheidung
Ein React-Frontend mit klar getrennten Portal-Routen (`/`, `/portal`, `/staff`, `/admin`, `/partner`) und rollenbasierten Protected Routes.

## Begründung
Wiederverwendung von Komponenten + zentrale Navigation bei gleichzeitig klaren Zugriffspfaden.

## Alternativen
- Separate Frontend-Apps je Rolle (höherer Wartungsaufwand).
- Monolithische Route ohne Portaltrennung (hohes Sicherheits-/UX-Risiko).

## Auswirkungen
Klare Benutzerführung, geringerer Wartungsaufwand, höhere RBAC-Anforderungen in API.

## Betroffene Dateien/Bereiche
`frontend/src/App.js`, Layout-Komponenten, AuthContext, Backend-RBAC.

## Risiken / Folgeaufgaben
Rollenregressionen bei Routingänderungen; Portaltests obligatorisch.
