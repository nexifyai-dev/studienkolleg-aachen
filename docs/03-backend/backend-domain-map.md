# Backend Domain Map

## Zweck

Diese Seite ordnet das Backend nicht nur nach Dateien, sondern nach fachlichen Domänen und Querschnittsthemen. Sie dient als Einstieg für Änderungen, Reviews und Impact-Analysen.

## Backend-Kernstruktur

Das Backend ist als FastAPI-Anwendung mit klarer Router-Aufteilung aufgebaut.

Zentrale Einstiegspunkte:

- `server.py` – App Factory und Router-Bindung
- `config.py` – zentrale Konfiguration
- `database.py` – Verbindung und Indexe
- `deps.py` – Auth-/RBAC-Abhängigkeiten
- `seed.py` – Seed- und Bootstrap-Logik
- `models/schemas.py` – Pydantic-Eingabe- und Hilfsschemas

## Domänenübersicht

### Auth & Identity
Zuständig für Anmeldung, Registrierung, Session-Wiederherstellung, Invite- und Passwort-Workflows.

Typische Auswirkungen auf andere Bereiche:
- Frontend Session-Verhalten
- Protected Routes
- Rollenmodell
- E-Mail-Flows

### Users
Verwaltung von Benutzerprofilen und administrativen Benutzeränderungen.

Typische Verknüpfungen:
- Rollen
- Spracheinstellungen
- Aktivierungsstatus
- Admin-Flächen

### Workspaces
Abbildung der produktseitigen Bereiche und organisatorischen Einheiten.

Wichtig, weil Workspaces definieren:
- fachlichen Bereich
- verfügbare Pipeline-Stages
- verfügbare Kurse
- mögliche Segmentierung von Bewerbungen

### Leads
Öffentliche bzw. externe Eingangsdaten für neue Kontakte und Bewerbungen.

Typische Verantwortung:
- Lead-Erfassung
- Duplicate Detection
- Übergang in Application-Kontext
- optionale Inline-Dokumente

### Applications
Kernobjekt des operativen Case Managements.

Typische Verantwortung:
- Status / Stage-Führung
- Zuweisung an Staff
- fachliche Fallattribute
- Verbindung zu Dokumenten, Aufgaben, Nachrichten und Follow-ups

### Documents
Dokumenten-Metadaten und Upload-/Prüflogik.

Typische Verantwortung:
- Uploads
- Statuswechsel (z. B. approved / rejected)
- Bezug zu Applications
- Storage-Anbindung

### Tasks
Operative Aufgabenverwaltung für Staff.

Typische Verantwortung:
- Erstellung und Zuweisung
- Status, Priorität, Fristen
- Bezug zu Anwendungen
- interne Sichtbarkeit

### Messaging
Kommunikation zwischen Beteiligten.

Typische Verantwortung:
- Konversationen
- Nachrichten
- Sichtbarkeitslogik
- potenziell Anwendungsbezug

### Notifications
Benachrichtigungsbezogene Systemlogik.

### System / Audit / Dashboard
Querschnittsdomäne für Betriebs- und Übersichtslogik.

Typische Verantwortung:
- Audit Logs
- Dashboard-Aggregationen
- systemweite Endpunkte

### Consents
Einwilligungs- und Zustimmungsverwaltung.

Wichtig für:
- Datenschutzkontext
- Portalnutzung
- Nachvollziehbarkeit von Einwilligungen

### AI Screening
KI-gestützte Prüf- oder Vorschlagslogik.

Wichtig, weil diese Domäne von externer Konfiguration abhängt und deshalb technisch vorhanden, aber nicht immer aktiv ist.

### Cost Simulator
Feature-Flag-abhängige Kosten-/Preislogik.

### Teacher
Lehrrollenspezifische Funktionalität.

### Followups
Wiedervorlagen und operative Nachverfolgung.

### Export
Ausgabe von Daten, z. B. CSV-Export.

### Partner
Partner- und Vermittlerlogik.

## Querschnittsservices

Neben den Routern gibt es Services, die mehrere Domänen gleichzeitig betreffen.

### Storage Service
Relevanz für:
- Dokumente
- Upload-Flows
- Download/Presigned URLs
- lokale und objektbasierte Speicherstrategien

### Audit Service
Relevanz für:
- Nachvollziehbarkeit
- Admin-Sichtbarkeit
- Compliance-nahe Änderungen

### Email Service
Relevanz für:
- Auth-Flows
- Bewerberkommunikation
- Betriebsreife / Go-live

### AI / Provider Services
Relevanz für:
- Screening
- externe Modellanbindung
- Feature-Schaltung über API-Keys

## Änderungsstrategie im Backend

Bei Änderungen sollte zuerst geklärt werden, ob der Task:

1. **domänenspezifisch** ist – nur ein Router / ein Objekt betroffen
2. **querschnittlich** ist – z. B. Rollen, Storage, Messaging, Notifications
3. **betriebsrelevant** ist – Env, Sicherheit, Deploy, Backup, E-Mail, Go-live

## Impact-Checkliste für Backend-Änderungen

Vor größeren Änderungen prüfen:

- Welche Router sind direkt betroffen?
- Welche Datenobjekte ändern sich?
- Müssen Seeds / Workspaces angepasst werden?
- Sind Frontend-Routen oder UI-Komponenten mitbetroffen?
- Ändern sich Rollenrechte?
- Ändert sich Auditierbarkeit?
- Sind Env-Variablen oder Feature Flags betroffen?
- Muss Dokumentation in `docs/` ergänzt werden?

## Empfohlene nächste Detailseiten

Als nächstes sinnvoll auszubauen:

- `auth-and-rbac.md`
- `applications.md`
- `documents.md`
- `tasks.md`
- `messaging.md`
- `storage.md`
- `environment-variables.md`
