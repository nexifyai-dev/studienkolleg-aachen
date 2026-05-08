# Deployment-Dokumentation – W2G Platform

**Version:** 1.0  
**Datum:** 2026-04-03  
**Status:** VERIFIZIERT (Preview), OFFEN (Produktion)

---

## 1. Zielumgebungen

| Umgebung | Plattform | Status |
|----------|-----------|--------|
| Preview / Staging | Emergent Platform (Kubernetes-Container) | AKTIV |
| Produktion | Emergent Platform (geplant) oder Self-Hosted | OFFEN – Plattform-seitiger Registry-Fehler blockiert Deployment |

---

## 2. Systemarchitektur im Deployment

```
                    ┌─────────────────────────────────┐
                    │     Kubernetes Ingress (nginx)   │
                    │  /api/* → Backend (Port 8001)    │
                    │  /*     → Frontend (Port 3000)   │
                    └─────────┬───────────┬────────────┘
                              │           │
                    ┌─────────▼───┐  ┌────▼──────────┐
                    │  FastAPI    │  │  React (CRA)   │
                    │  Port 8001  │  │  Port 3000     │
                    │  uvicorn    │  │  yarn start    │
                    └──────┬──────┘  └────────────────┘
                           │
                    ┌──────▼──────┐
                    │  MongoDB    │
                    │  Port 27017 │
                    └─────────────┘
```

---

## 3. ENV-Variablen-Gruppen

### 3.1 Backend (`/app/backend/.env`)

**Pflicht (Server startet nicht ohne diese):**

| Variable | Zweck | Sicherheitsstufe |
|----------|-------|------------------|
| `MONGO_URL` | MongoDB Connection String | GEHEIM |
| `DB_NAME` | Datenbankname | INTERN |
| `JWT_SECRET` | JWT-Signierung (min. 32 Zeichen) | GEHEIM |

**Sicherheit:**

| Variable | Zweck | Default |
|----------|-------|---------|
| `COOKIE_SECURE` | true in Produktion (HTTPS) | false |
| `COOKIE_SAMESITE` | Cookie SameSite-Attribut | lax |
| `ACCESS_TOKEN_TTL_MINUTES` | Access-Token Lebensdauer | 60 |
| `REFRESH_TOKEN_TTL_DAYS` | Refresh-Token Lebensdauer | 7 |

**Admin-Seed:**

| Variable | Zweck |
|----------|-------|
| `ADMIN_EMAIL` | E-Mail des initialen Admin-Accounts |
| `ADMIN_PASSWORD` | Passwort des initialen Admin-Accounts |

**App-URLs:**

| Variable | Zweck |
|----------|-------|
| `FRONTEND_URL` | URL des Frontends (fuer CORS, E-Mail-Links) |
| `APP_URL` | URL des Backends (fuer interne Referenzen) |

**E-Mail (optional, deaktiviert wenn leer):**

| Variable | Zweck |
|----------|-------|
| `RESEND_API_KEY` | Resend-API-Key fuer Transaktions-E-Mails |
| `EMAIL_FROM` | Absenderadresse |
| `REPLY_TO` | Reply-To-Adresse |

**IMAP/SMTP (optional):**

| Variable | Zweck |
|----------|-------|
| `IMAP_HOST` | IMAP-Server |
| `IMAP_PORT` | IMAP-Port (993) |
| `SMTP_HOST` | SMTP-Server |
| `SMTP_PORT` | SMTP-Port (465) |
| `EMAIL_USER` | E-Mail-Konto |
| `EMAIL_PASSWORD` | E-Mail-Passwort |

**Storage (optional):**

| Variable | Zweck | Default |
|----------|-------|---------|
| `STORAGE_BACKEND` | local / s3 / minio | local |
| `LOCAL_STORAGE_PATH` | Pfad fuer lokalen Storage | /app/storage |
| `S3_ENDPOINT` | S3-Endpunkt | (leer) |
| `S3_ACCESS_KEY` | S3 Access Key | (leer) |
| `S3_SECRET_KEY` | S3 Secret Key | (leer) |
| `S3_BUCKET` | S3 Bucket-Name | w2g-documents |
| `S3_REGION` | S3 Region | eu-central-1 |

**AI/KI:**

| Variable | Zweck |
|----------|-------|
| `NSCALE_API_KEY` | nscale API fuer AI-Screening |

### 3.2 Frontend (`/app/frontend/.env`)

| Variable | Zweck |
|----------|-------|
| `REACT_APP_BACKEND_URL` | Backend-URL fuer API-Aufrufe (NICHT aendern) |

---

## 4. Sichere Konfigurationsregeln

1. **Keine Secrets im Code oder in Git.** Alle Credentials kommen aus `.env`-Dateien oder Secret-Managern.
2. **`.env`-Dateien niemals committen.** `.gitignore` enthaelt bereits `.env`-Eintraege.
3. **`COOKIE_SECURE=true` in Produktion setzen.** Nur bei HTTPS.
4. **`JWT_SECRET` muss min. 32 zufaellige Zeichen haben.** In Produktion min. 64 empfohlen.
5. **`ADMIN_PASSWORD` nach erstem Login rotieren** oder initialen Admin deaktivieren.
6. **CORS:** Keine Wildcards (`*`) in Produktion. `CORS_ORIGINS` explizit setzen oder `FRONTEND_URL` nutzen.

---

## 5. Start- und Deploy-Reihenfolge

### Lokale Entwicklung / Preview

```
1. MongoDB starten (supervisord)
2. Backend starten: supervisorctl start backend
   → lädt .env, verbindet MongoDB, fuehrt Seed aus
3. Frontend starten: supervisorctl start frontend
   → liest REACT_APP_BACKEND_URL aus .env
```

### Produktion

```
1. MongoDB sicherstellen (managed oder self-hosted, mit Auth und Backup)
2. .env-Dateien konfigurieren (alle Pflichtfelder setzen)
3. Backend deployen und Health-Check pruefen
4. Frontend deployen
5. Smoke-Tests ausfuehren (siehe Abschnitt 8)
```

---

## 6. Abhaengigkeiten

### Datenbank
- **MongoDB 7.x**: Verbindung ueber `MONGO_URL`, Datenbank `DB_NAME`
- Indizes werden beim Startup automatisch erstellt
- Seed-Daten (Workspaces, Admin, Anabin-Knowledge) werden idempotent angelegt

### Storage
- **Lokal:** `/app/storage` (nur fuer Preview/Entwicklung)
- **S3/MinIO:** Erfordert gesetzte `S3_*`-Variablen (OFFEN fuer Produktion)

### E-Mail
- **Transaktional:** Resend (`RESEND_API_KEY`) – OFFEN
- **Sync:** IMAP/SMTP (Strato) – architektonisch vorbereitet

### AI/KI
- **nscale API:** Screening-Funktionen (`NSCALE_API_KEY`)
- Ohne Key: AI-Features deaktiviert, kein Fehler

---

## 7. Bekannte externe Blocker

| Blocker | Status | Auswirkung |
|---------|--------|------------|
| Emergent-Platform Registry-Fehler ("deployment not found") | OFFEN | Produktions-Deployment blockiert |
| Git-History enthaelt alte Credentials | OFFEN | Vor Public-Push: filter-branch oder Fresh-Start |
| Credential-Rotation nach History-Bereinigung | OFFEN | Alle betroffenen Services muessen neue Keys erhalten |
| Impressum/AGB/Datenschutz nicht finalisiert | OFFEN | Rechtliche Go-Live-Voraussetzung |

---

## 8. Health-Checks und Smoke-Tests

### Health-Check

```bash
curl -s $BACKEND_URL/api/health
# Erwartete Antwort: {"status":"ok","service":"W2G Platform API","version":"1.1.0",...}
```

### Smoke-Test nach Deployment

```bash
# 1. Health-Check
curl -s $URL/api/health | python3 -c "import sys,json; d=json.load(sys.stdin); assert d['status']=='ok'"

# 2. Login
curl -s -c /tmp/cookies -X POST "$URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"<ADMIN_EMAIL>","password":"<ADMIN_PASSWORD>"}'

# 3. Auth-Check
curl -s -b /tmp/cookies "$URL/api/auth/me"

# 4. Dashboard-Daten
curl -s -b /tmp/cookies "$URL/api/dashboard/stats"

# 5. Frontend erreichbar
curl -s -o /dev/null -w "%{http_code}" "$URL/"
# Erwartung: 200
```

---

## 9. Minimale Rollback-Strategie

### Code-Rollback
- Emergent-Plattform bietet Rollback auf vorherige Checkpoints
- Alternativ: Git-basierter Rollback auf letzten stabilen Commit

### Daten-Rollback
- **OFFEN:** Keine automatische MongoDB-Backup-Routine konfiguriert
- Empfehlung: `mongodump` vor jedem groesseren Release
- Bei Seed-Aenderungen: Seed-Skripte sind idempotent, kein destruktiver Effekt

### Notfall-Massnahmen
1. Backend stoppen: `supervisorctl stop backend`
2. Letzten stabilen Stand wiederherstellen (Git oder Emergent-Rollback)
3. Backend neu starten: `supervisorctl start backend`
4. Smoke-Tests ausfuehren

---

## 10. Offene Punkte

| Punkt | Prioritaet | Abhaengigkeit |
|-------|------------|---------------|
| MongoDB-Backup-Routine | HOCH | Infra-Entscheidung (managed vs. self-hosted) |
| S3/MinIO-Storage produktiv | HOCH | Credentials und Bucket-Setup |
| HTTPS / TLS | HOCH | Deployment-Plattform oder Reverse-Proxy |
| Resend verifizierte Domain | MITTEL | DNS-Konfiguration |
| Monitoring / Alerting | MITTEL | Sentry oder vergleichbar |
| CI/CD-Pipeline | MITTEL | GitHub Actions oder Emergent-Pipeline |
