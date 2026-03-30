# ADR-0003: JWT-Cookie-Auth mit Same-Origin-Fokus

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Portalbetrieb erfordert Session-Sicherheit und rollenbasierte Navigation.

## Problem
Cross-Origin-Konfigurationen führten historisch zu Deploy-Problemen.

## Entscheidung
JWT in HttpOnly-Cookies, Same-Origin-API-Nutzung bevorzugt, produktiv HTTPS + `COOKIE_SECURE=true`.

## Begründung
Reduziert Client-Leak-Risiko und CORS-Komplexität.

## Alternativen
LocalStorage-Token (abgelehnt), komplett stateless Header-only ohne Cookies.

## Auswirkungen
Umgebungskonfiguration kritisch; TLS-Pflicht für produktive Sicherheit.

## Betroffene Dateien/Bereiche
`backend/config.py`, Auth-Router, Frontend API-Client.

## Risiken / Folgeaufgaben
Fehlkonfiguration von SameSite/Secure kann Login brechen.
