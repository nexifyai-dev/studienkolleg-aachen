# Local Setup

## Zweck

Diese Seite beschreibt einen pragmatischen lokalen Entwicklungsstart für Frontend und Backend.

## Grundstruktur

Das Repository besteht aus zwei Hauptanwendungen:

- `backend/` – FastAPI + MongoDB
- `frontend/` – React-Anwendung

In der lokalen Entwicklung laufen Backend und Frontend typischerweise getrennt.

## Voraussetzungen

Empfohlen:

- Python 3.11+ oder kompatible Projektversion
- Node.js / npm
- lokale oder erreichbare MongoDB
- optional virtuelle Umgebung für Python

## Backend lokal starten

### 1. In das Backend-Verzeichnis wechseln

```bash
cd backend
```

### 2. Virtuelle Umgebung erstellen und aktivieren

```bash
python -m venv .venv
source .venv/bin/activate
```

Unter Windows entsprechend die passende Aktivierungsvariante verwenden.

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen setzen

Mindestens erforderlich:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=w2g_platform
JWT_SECRET=<mindestens 32 Zeichen>
ADMIN_PASSWORD=<sicheres lokales Passwort>
```

Optional, aber lokal oft sinnvoll:

```env
ADMIN_EMAIL=admin@studienkolleg-aachen.de
FRONTEND_URL=http://localhost:3000
APP_URL=http://localhost:8001
COOKIE_SECURE=false
COOKIE_SAMESITE=lax
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=/app/storage
```

Hinweis:
- E-Mail, S3/MinIO und AI-Screening bleiben ohne die jeweiligen Keys deaktiviert.
- `SEED_DEV_PASSWORD` erzeugt zusätzlich Dev-/Testkonten.

### 5. Backend starten

```bash
uvicorn server:app --reload --port 8001
```

Wenn der Start erfolgreich ist, werden Datenbankverbindung, Indexe und Seed-Schritte beim Startup ausgeführt.

## Frontend lokal starten

### 1. In das Frontend-Verzeichnis wechseln

```bash
cd frontend
```

### 2. Abhängigkeiten installieren

```bash
npm install
```

### 3. Frontend starten

```bash
npm start
```

Standardmäßig läuft das Frontend lokal auf Port 3000.

## Zusammenspiel lokal

Typischer lokaler Standard:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8001`

Das Frontend verwendet `REACT_APP_BACKEND_URL` als Basis für API-Requests. Je nach Setup kann dieser Wert leer bleiben oder explizit auf das lokale Backend zeigen.

## Seed-Verhalten

Beim Backend-Start werden automatisch angelegt bzw. sichergestellt:

- Workspaces
- initialer Admin-Account
- optionale Dev-/Test-Accounts, falls `SEED_DEV_PASSWORD` gesetzt ist

## Typische lokale Fehlerquellen

### Backend startet nicht
Prüfen:
- Pflichtvariablen gesetzt?
- MongoDB erreichbar?
- `JWT_SECRET` lang genug?
- Python-Umgebung korrekt aktiviert?

### Login / Session funktioniert nicht
Prüfen:
- Frontend- und Backend-URL stimmen?
- Cookie-Flags lokal passend?
- CORS-/SameSite-Konfiguration passend?

### Dokumente werden nicht wie erwartet gespeichert
Prüfen:
- `STORAGE_BACKEND` korrekt?
- lokaler Pfad beschreibbar?
- ohne S3/MinIO-Konfiguration läuft ggf. nur lokaler oder eingeschränkter Speicherpfad

## Empfohlene nächste Seiten

- [Environment Variables](../06-operations/environment-variables.md)
- [Storage](../06-operations/storage.md)
- [Go-live Checklist](../06-operations/go-live-checklist.md)
