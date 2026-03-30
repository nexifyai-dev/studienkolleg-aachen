# ADR-0011: Notification-/E-Mail-Strategie mit In-App-first + Resend

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Kommunikation muss intern nachvollziehbar und extern zustellbar sein.

## Problem
Externe Zustellung ist provider- und domainabhängig.

## Entscheidung
In-App-Notifications als stabile Basis, E-Mail über Resend als externe Zustellungsschicht.

## Begründung
Interne Nachvollziehbarkeit bleibt auch bei externen Providerproblemen erhalten.

## Alternativen
E-Mail-only (abgelehnt), sofortige komplexe IMAP-Synchronisierung (verschoben).

## Auswirkungen
Go-Live-Abhängigkeit von Resend-Domain-Verifizierung.

## Betroffene Dateien/Bereiche
Notification-/Email-Services, Operations-Doku, Kommunikationsarchitektur.

## Risiken / Folgeaufgaben
Domain-Verifizierung und Monitoring der Delivery-Raten.
