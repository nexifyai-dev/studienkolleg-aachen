# System Architecture

## Zielbild

Die W2G Platform ist eine mehrflächige Applicant-Management-Plattform für mehrere Geschäftsbereiche und Rollen. Das System kombiniert öffentliche Lead-Erfassung, internes Fallmanagement, Bewerberportal, Partnerfläche und Administrationsfunktionen in einem gemeinsamen Daten- und Auth-Modell.

## Architekturstil

### Frontend
- React Single Page Application
- Routing über `react-router-dom`
- Auth-Zustand über `AuthContext`
- API-Kommunikation über zentralen Axios-Client
- i18n für Deutsch und Englisch

### Backend
- FastAPI als Application Layer
- Router-orientierte Domänentrennung
- MongoDB als primärer Datenspeicher
- Pydantic-Schemas für Request-/Response-Strukturen
- Service-Layer für Querschnittslogik (z. B. Storage, E-Mail, Audit)

### Integrationen
- Resend für E-Mail-Versand
- S3/MinIO oder Local Storage für Dokumente
- nscale für AI-Screening / KI-Inferenz

## High-Level-Fluss

```text
Benutzer / Bewerber / Staff / Partner
        ↓
React Frontend (mehrere Produktflächen)
        ↓
Axios API Client + Cookie-basierte Session
        ↓
FastAPI Router nach Domänen
        ↓
MongoDB + Services + externe Integrationen
```

## Frontend-Flächen

Die Benutzeroberfläche ist nicht als ein einziges Portal, sondern als mehrere Produktflächen organisiert:

- Öffentliche Website
- Auth-Fläche
- Applicant Portal (`/portal`)
- Staff Portal (`/staff`)
- Admin Portal (`/admin`)
- Partner Portal (`/partner`)

Diese Trennung ist wichtig, weil Änderungen selten nur eine einzelne Seite betreffen. Häufig berühren sie Rollenrouting, API-Verhalten, Datenmodell und Betriebslogik gleichzeitig.

## Backend-Zuschnitt

Das Backend bindet Domänenrouter zentral in `server.py` ein. Die wesentlichen Domänen sind:

- Auth / Users
- Workspaces
- Leads
- Applications
- Documents
- Tasks
- Messaging
- Notifications
- AI Screening
- Cost Simulator
- Consents
- Teacher
- Followups
- Export
- Partner
- System / Audit / Dashboard

## Lebenszyklus der Anwendung

### Startup
Beim Start werden folgende Kernschritte ausgeführt:

1. Datenbankverbindung aufbauen
2. Datenbankindizes sicherstellen
3. Workspaces seeden
4. Admin-Account seeden

### Shutdown
Die Datenbankverbindung wird sauber geschlossen.

## Zentrale Architekturentscheidungen

### 1. Cookie-basierte Authentifizierung
Die Plattform verwendet Cookie-basierte JWT-Sessions statt lokaler Token-Speicherung. Dadurch bleiben Tokens aus `localStorage` heraus und Session-Verhalten wird zentralisiert.

### 2. Rollenbasierte Flächentrennung
Die Oberfläche ist nach Rollen und Produktflächen getrennt. Das reduziert UI-Komplexität pro Rolle, erhöht aber die Bedeutung sauberer RBAC-Logik.

### 3. Workspace-/Bereichsorientierung
Das System ist nicht nur auf ein Studienkolleg beschränkt, sondern vorbereitet auf mehrere Bereiche wie Sprachkurse, Pflege und Arbeit/Ausbildung.

### 4. Feature-gesteuerte Aktivierung externer Fähigkeiten
E-Mail, Storage-Backends, AI-Screening und Cost-Simulator sind über Konfiguration und Keys steuerbar. Dadurch kann das System teilweise produktionsnah laufen, obwohl Integrationen noch nicht vollständig aktiviert sind.

## Kritische Querschnittsthemen

Diese Themen müssen bei Architekturänderungen fast immer mitgedacht werden:

- Auth & Session-Verhalten
- Rollen & Berechtigungen
- Workspace-Isolation
- Dokumenten- und Storage-Strategie
- Auditierbarkeit
- API- und UI-Konsistenz
- Go-live-Reifegrad

## Bekannte Spannungsfelder

- Das Produkt ist funktional breit, aber einzelne produktive Integrationen sind noch konfigurationsabhängig.
- `memory/` enthält aktuell noch relevante Wissensartefakte, die in die strukturierte Dokumentation überführt werden müssen.
- Die Architektur ist modular genug für Skalierung, aber Änderungen über mehrere Domänen erfordern gute Dokumentationsdisziplin.

## Dokumentationsfolgen

Architekturänderungen sollten mindestens dann dokumentiert werden, wenn sie eines der folgenden Themen berühren:

- neue Produktfläche oder neue Rolle
- neuer Router oder neue Domäne
- neues externes System / neue Integration
- neues Workspace-Konzept oder neue Pipeline-Stages
- Änderung am Session-, Cookie- oder Sicherheitsmodell
- Änderung an der Speicherstrategie für Dokumente
