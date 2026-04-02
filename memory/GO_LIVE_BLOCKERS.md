# Hinweis

Dieses Dokument bleibt vorerst als historisches / Übergangsartefakt im Repository.

Die laufend gepflegte operative Dokumentation liegt jetzt primär unter:

- `docs/06-operations/go-live-checklist.md`
- `docs/06-operations/environment-variables.md`
- `docs/06-operations/storage.md`
- `docs/07-development/local-setup.md`

Der Inhalt unten bleibt als Zustandsdokument erhalten.

---

## Go-Live Blocker – W2G Platform

Stand: 29. März 2026
Status: Foundation live, NICHT produktionsreif ohne Auflösung der Blocker unten.

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
  ✓ i18n (DE/EN)
  ✓ Modular Backend (server.py < 70 Zeilen)

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
