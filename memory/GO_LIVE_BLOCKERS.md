## Go-Live Blocker – W2G Platform

Stand: 03. April 2026
Status: Foundation live, Governance-Dokumentation erstellt. NICHT produktionsreif ohne Aufloesung der Blocker unten.

---

### GOVERNANCE / DOKUMENTATION (Neu – 03.04.2026)

| # | Thema | Status |
|---|---|---|
| G1 | Agent Memory & Writeback Policy | ERLEDIGT |
| G2 | ADR-001 Architekturabweichung dokumentiert | ERLEDIGT |
| G3 | DEPLOYMENT.md erstellt | ERLEDIGT |
| G4 | RUNBOOK.md erstellt | ERLEDIGT |
| G5 | Wiki-Spiegelung erstellt | ERLEDIGT |
| G6 | README.md vollstaendig | ERLEDIGT |
| G7 | History-Eintrag fuer Governance-Block | ERLEDIGT |

---

### REPO-HYGIENE (Neu – Phase 3.8a)

| # | Thema | Status |
|---|---|---|
| H1 | .gitignore vollständig (storage, test_reports, __pycache__, etc.) | ERLEDIGT |
| H2 | Klartext-Credentials aus test_reports entfernt | ERLEDIGT |
| H3 | Klartext-Credentials aus Backend-Tests entfernt (→ env vars) | ERLEDIGT |
| H4 | storage/messages aus Git-Tracking entfernt | ERLEDIGT |
| H5 | Secret-Scan-Script + Pre-Commit-Hook | ERLEDIGT |
| H6 | Git-History enthält noch alte Credentials (git filter-branch nötig) | OFFEN / OPERATIV ERFORDERLICH |
| H7 | Echte Credential-Rotation (Passwörter, API-Keys) nach History-Bereinigung | OFFEN / OPERATIV ERFORDERLICH |

> **Hinweis H6/H7**: Die aktuellen Commits enthalten keine Klartext-Credentials mehr. Die Git-History enthält jedoch noch alte Versionen mit Credentials. Vor Production-Push auf öffentliches Repo muss entweder `git filter-branch` / BFG Repo Cleaner laufen ODER ein frischer Repo-Start erfolgen, gefolgt von echter Credential-Rotation bei allen betroffenen Services (Passwörter, Resend-Key, Emergent-Key, NSCall-Key).

---

### TECHNIK

| # | Blocker | Aufwand | Status |
|---|---|---|---|
| T1 | `COOKIE_SECURE=true` setzen (HTTPS-Pflicht in Prod) | .env ändern | Bereit, warten auf HTTPS-Bestätigung |
| T2 | `RESEND_API_KEY` konfigurieren + verifizierte Absender-Domain | .env + Resend-Setup | [OFFEN] |
| T3 | Echten Datei-Upload aktivieren: S3/MinIO Credentials (`S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `S3_BUCKET`) | .env + ggf. `pip install boto3` | [OFFEN] |
| T4 | `JWT_SECRET` produktionstauglichen Wert setzen (min. 64 Zeichen, zufällig) | .env ändern | Bereit |
| T5 | `ADMIN_PASSWORD` nach erstem Login rotieren oder initialen Admin deaktivieren | Prozess | Bereit |
| T6 | MongoDB-Sicherung und Backup-Routine | Infra | [OFFEN] |
| T7 | HTTPS / TLS für Produktion sicherstellen (Cookie `secure=True` hängt davon ab) | Infra/Deploy | [OFFEN] |

### RECHT

| # | Blocker | Status |
|---|---|---|
| R1 | Adresse im Impressum verifizieren (Theaterstraße 24 oder 30-32?) | [OFFEN] |
| R2 | Vollständiges Impressum (GF-Name, HR-Gericht, HR-Nr., USt-IdNr.) | [OFFEN] |
| R3 | Datenschutzerklärung rechtlich geprüft und finalisiert | [OFFEN] |
| R4 | AGB rechtlich geprüft und finalisiert | [OFFEN] |
| R5 | Preisangaben auf der Website: keine falschen/widersprüchlichen Angaben vor Go-Live | [OFFEN] |

### BETRIEB

| # | Blocker | Status |
|---|---|---|
| B1 | Staff-Onboarding: mindestens 1 Mitarbeiter-Account angelegt + getestet | [OFFEN] |
| B2 | Testbewerbung von außen durchgeführt | [OFFEN] |
| B3 | E-Mail-Delivery getestet (Willkommen, Bewerbung eingegangen) | [OFFEN – abhängig von T2] |

---

### ENV-Variablen-Übersicht

```
# Pflichtfelder (fehlen → Server startet nicht)
MONGO_URL=mongodb://...
DB_NAME=w2g_platform
JWT_SECRET=<min. 64 zufällige Zeichen>
ADMIN_PASSWORD=<sicheres Passwort>

# Sicherheit
COOKIE_SECURE=false           # → true in Production (HTTPS!)
COOKIE_SAMESITE=lax

# Token-TTL
ACCESS_TOKEN_TTL_MINUTES=60
REFRESH_TOKEN_TTL_DAYS=7

# Admin Seed
ADMIN_EMAIL=admin@studienkolleg-aachen.de

# App URLs
FRONTEND_URL=https://...
APP_URL=https://...

# E-Mail [OFFEN]
RESEND_API_KEY=                     # Leer = E-Mail deaktiviert, kein Fehler
EMAIL_FROM=noreply@studienkolleg-aachen.de

# Storage [OFFEN]
STORAGE_BACKEND=local               # local | s3 | minio
LOCAL_STORAGE_PATH=/app/storage     # nur bei STORAGE_BACKEND=local
S3_ENDPOINT=                        # Leer = S3/MinIO nicht aktiv
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_BUCKET=w2g-documents
S3_REGION=eu-central-1
```

---

### Systemzustand

```
PRODUKTIONSREIF:
  ✓ JWT Auth (Login, Register, Logout, Refresh, Invite, Reset)
  ✓ Brute-Force-Schutz (5 Versuche, 15 min Lockout)
  ✓ RBAC (8 Rollen, Middleware-basiert)
  ✓ Horizontale Isolation (Applicant sieht nur eigene Daten)
  ✓ Audit Logging (append-only)
  ✓ Lead Ingest + Duplicate Detection
  ✓ Application Pipeline (11 Stages)
  ✓ Document Metadata Management
  ✓ Task Management
  ✓ Messaging
  ✓ Invoice Management (CRUD, RBAC, Audit, Staff+Applicant UI)
  ✓ Invoice Numbering (konfigurierbares Präfix/Start/Suffix: W2G-YYYYMM-XXXX-AC)
  ✓ DeepSeek AI Integration (deepseek-chat + deepseek-reasoner)
  ✓ i18n (DE/EN)
  ✓ Modular Backend (server.py < 120 Zeilen)

VORBEREITET, ABER NICHT AKTIV:
  ○ E-Mail-Delivery (Code bereit, RESEND_API_KEY fehlt)
  ○ Binäre Datei-Uploads (Code bereit, Storage-Credentials fehlen)
  ○ S3/MinIO Backend (Code bereit, boto3 bei Bedarf installieren)
  ○ HTTPS/Secure-Cookies (COOKIE_SECURE=false, änderbar per .env)

EXPLIZIT BLOCKIERT (kein Go-Live):
  ✗ Preislogik (widersprüchliche Angaben, nicht verifiziert)
  ✗ Rechtstexte (Impressum/AGB/Datenschutz unfertig)
  ✗ MongoDB-Backup (keine Routine konfiguriert)
```
