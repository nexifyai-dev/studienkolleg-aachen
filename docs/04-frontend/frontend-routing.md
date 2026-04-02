# Frontend Routing

## Zweck

Diese Seite beschreibt die Routing- und Session-Logik des React-Frontends auf Systemebene.

## Router-Struktur

Das Frontend ist in mehrere Flächen mit klar getrennten Einstiegspfaden aufgeteilt:

- `/` – öffentliche Startseite
- `/apply` – Bewerbung / Lead-Ingest
- `/contact`, `/courses`, `/services` – öffentliche Informationsseiten
- `/legal`, `/privacy`, `/agb` – rechtliche Seiten
- `/auth/*` – Login / Registrierung / Passwort-Reset
- `/portal/*` – Bewerberportal
- `/staff/*` – interne Staff-Fläche
- `/admin/*` – Admin-Fläche
- `/partner/*` – Partner-/Affiliate-Fläche

## Routing-Prinzipien

### 1. Öffentliche Seiten sind frei erreichbar
Die Public Pages können ohne Login aufgerufen werden.

### 2. Geschützte Produktflächen verwenden `ProtectedRoute`
Zugriff auf `portal`, `staff`, `admin` und `partner` wird über Rollenlisten abgesichert.

### 3. Auth-Seiten verwenden `PublicRoute`
Bereits eingeloggte Nutzer werden aktiv in ihre primäre Fläche weitergeleitet.

## Flächen nach Rolle

### Applicant
Pfad: `/portal`

Unterseiten:
- Dashboard
- Journey
- Documents
- Messages
- Financials
- Settings
- Consents

### Staff
Pfad: `/staff`

Unterseiten:
- Dashboard bzw. Teacher-Dashboard
- Kanban
- Tasks
- Messaging
- Applicant/Application Detail

### Admin
Pfad: `/admin`

Unterseiten:
- Dashboard
- Users
- Audit

### Partner
Pfad: `/partner`

Unterseiten:
- Dashboard
- Referrals
- Link
- Settings

## Sonderfall Teacher

`teacher` wird innerhalb der Staff-Fläche technisch als Staff-Zugang behandelt, erhält aber auf der Index-Route ein spezielles Dashboard. Das bedeutet:

- gleicher Oberflächenbereich wie Staff
- anderer Startpunkt / Fokus
- potenziell differenzierte Rechte im Backend

## Authentifizierungsmodell im Frontend

### AuthContext
`AuthContext` verwaltet:
- aktuellen Benutzer
- Ladezustand beim Initial-Check
- Login
- Logout
- User-Refresh
- Synchronisation der Spracheinstellung

### API-Client
`apiClient` verwendet:
- `withCredentials: true`
- zentrale 401-Behandlung
- Refresh-Versuch über `/api/auth/refresh`
- Redirect auf `/auth/login`, wenn Refresh scheitert

### Wichtige Konsequenz
Das Frontend speichert keine Tokens in `localStorage`. Dadurch ist die Session-Logik stärker an Cookies und Backend-Verhalten gekoppelt.

## Routing-Implikationen für Änderungen

Änderungen an einer Rolle oder Produktfläche betreffen oft mehr als nur eine neue Route. Zu prüfen sind häufig auch:

- Navigation / Layout
- Redirect-Verhalten
- Session-/Refresh-Verhalten
- Backend-RBAC
- API-Endpunkte
- i18n-Texte
- Sichtbarkeit in Menüs und Dashboards

## Typische Fehlerquellen

- Rolle im Frontend ergänzt, aber Backend-RBAC nicht angepasst
- Route sichtbar, aber Datenendpunkte nicht freigeschaltet
- Redirect-Schleifen bei Auth-Änderungen
- Uneinheitliche Behandlung von `teacher`, `affiliate` oder `accounting_staff`
- Fehlende Doku bei neuen Produktflächen

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- eine neue Hauptfläche entsteht
- neue geschützte Routen hinzukommen
- Rollen an andere Flächen gebunden werden
- Auth-/Refresh-Verhalten geändert wird
- Layouts oder Index-Redirects pro Rolle angepasst werden
