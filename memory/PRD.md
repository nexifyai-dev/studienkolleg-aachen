# W2G Platform – PRD / Memory

**Stand:** 29. März 2026 (Update: Hardening Phase)
**Version:** 1.1.0
**Projekt:** Studienkolleg Aachen / Way2Germany – Mehrmandantenfähige Plattform

---

## Original Problemstellung
Produktionsreife, skalierbare, mehrmandantenfähige Plattform für Studienkolleg Aachen / Way2Germany.
Saubere Trennung: Public Website, Applicant Portal, Staff/Admin-Bereich, Datenmodell, Rollen/Rechte,
Dokumentenlogik, Automationen, Auditfähigkeit, i18n-fähig.

---

## Verbindliche User-Entscheidungen
- **Auth:** JWT Custom Auth (Email + Passwort), kein Google OAuth
- **Sprachen:** Mehrsprachig, Deutsch primär, i18n-Struktur von Beginn an
- **E-Mail:** Resend (RESEND_API_KEY noch nicht konfiguriert – Feature-Gate aktiv)
- **DB:** MongoDB (projektspezifische Abweichung von Supabase-Empfehlung)
- **Design:** #113655 primär, #B3CDE1 akzent, Inter/Arboria, live-site-abgeleitet

---

## Architektur (v1.1.0)

### Backend-Struktur
```
/app/backend/
├── server.py           # App Factory only (~70 lines)
├── config.py           # All env vars – fails fast if required vars missing
├── database.py         # MongoDB client + all indexes
├── deps.py             # get_current_user, require_roles, role groups
├── seed.py             # Idempotent workspace + admin seeding
├── models/
│   └── schemas.py      # All Pydantic schemas (no role injection possible)
├── routers/
│   ├── auth.py         # Login, Register (+ Lead-Claiming), Invite, Reset
│   ├── users.py        # User CRUD (field-level access control)
│   ├── workspaces.py   # Workspace management
│   ├── leads.py        # Public lead ingest (no auth required)
│   ├── applications.py # Application CRUD + stage pipeline
│   ├── documents.py    # Upload/Download/Review (storage abstraction)
│   ├── tasks.py        # Task management (ownership-checked updates)
│   ├── messaging.py    # Conversations + Messages (participant-scoped)
│   └── system.py       # Audit logs, Dashboard stats, Notifications, Health
├── services/
│   ├── audit.py        # Append-only audit logging (never raises)
│   ├── email.py        # Resend with feature flag (no-op without API key)
│   └── storage.py      # LocalStorage / S3 / MinIO abstraction
└── .env                # All config, fully documented
```

### Frontend-Struktur
```
/app/frontend/src/
├── App.js              # Routing (Public/Auth/Portal/Staff/Admin)
├── i18n.js             # i18next (DE/EN)
├── lib/
│   ├── utils.js        # Stage labels, colors, role labels, formatters
│   └── apiClient.js    # Axios + auto-refresh interceptor (no localStorage)
├── contexts/AuthContext.js  # Auth state, login/logout/refresh
├── locales/de/ + en/   # Translation files
├── components/layout/  # PublicNav, PublicFooter, ApplicantLayout, StaffLayout, AdminLayout
└── pages/
    ├── public/         # Home, Apply, Courses, Services, Contact, Legal
    ├── auth/           # Login, Register, ForgotPassword
    ├── portal/         # Dashboard, Journey, Documents, Messages, Financials, Settings
    ├── staff/          # StaffDashboard, KanbanPage, ApplicantDetailPage
    └── admin/          # AdminDashboard, UsersPage, AuditPage
```

---

## Security-Audit-Ergebnisse (v1.1.0)

| # | Finding | Severity | Status |
|---|---|---|---|
| S1 | ADMIN_PASSWORD Default-Wert im Code | CRITICAL | **BEHOBEN** – jetzt required in .env |
| S2 | Cookie `secure=false` fest kodiert | HIGH | **BEHOBEN** – COOKIE_SECURE in .env |
| S3 | Staff ohne workspace_id sieht alle Applicant-Daten | MEDIUM | **BEHOBEN** – explizit dokumentiert als intentional für Kanban |
| S4 | `update_task` kein Ownership-Check | MEDIUM | **BEHOBEN** – owner + creator check |
| S5 | Message: Empfänger-ID nicht validiert | MEDIUM | **BEHOBEN** – recipient existence check |
| S6 | Brute-Force-IP hinter K8s-Proxy falsch | CRITICAL | **BEHOBEN** – X-Forwarded-For |
| S7 | Timezone-naive vs aware Vergleich in Lockout | HIGH | **BEHOBEN** – explicit UTC |
| S8 | JWT Secret Stärke-Check fehlt | LOW | **BEHOBEN** – config._validate() |
| S9 | Document Storage Key nie zum Client | HIGH | **BEHOBEN** – key aus allen Responses entfernt |
| S10 | Token Blacklisting nicht implementiert | LOW | **BEKANNT/AKZEPTIERT** – 60-min TTL + active-Flag als Mitigation |

### Horizontale Isolation (verifiziert)
- Applicant → Audit Logs: 403 ✓
- Applicant → User List: 403 ✓
- Applicant → Other User Update: 403 ✓
- Unauthenticated → Workspace Create: 401 ✓
- Applicant → fremde Bewerbung: 403 ✓

---

## Was implementiert ist (v1.1.0 Hardening)

### Backend (DONE)
- [x] Vollständige Modularisierung (server.py = App Factory, 9 Router, 3 Services)
- [x] config.py (alle ENV-Vars, fail-fast, kein Passwort-Default)
- [x] database.py (MongoDB + Indexes)
- [x] deps.py (RBAC-Dependencies, Role Groups)
- [x] seed.py (idempotent, kommentiert)
- [x] services/audit.py (append-only, non-blocking)
- [x] services/email.py (Resend + Feature-Flag + 5 Templates)
- [x] services/storage.py (Local + S3 + MinIO + Metadata-Only + Validation)
- [x] routers/auth.py (Brute-Force-Fix, X-Forwarded-For, timezone-aware)
- [x] routers/documents.py (server-side download, storage_key nie exposed)
- [x] routers/tasks.py (Ownership-Check)
- [x] routers/messaging.py (Participant-Check, Recipient-Validation)
- [x] .env vollständig dokumentiert

### Frontend (DONE)
- [x] lib/apiClient.js (axios + auto-refresh interceptor + logout-on-failure)
- [x] AuthContext.js (verwendet apiClient)
- [x] Alle Portal/Staff/Admin-Pages auf apiClient migriert
- [x] Kein Token in localStorage (nur httpOnly cookies)

---

## Offene Punkte (explizit markiert)

| # | Punkt | Go-Live-Blocker |
|---|---|---|
| 1 | Adresse (Theaterstraße 24 vs. 30-32) | **JA** |
| 2 | Preislogik widersprüchlich | **JA** |
| 3 | Impressum (GF, HR-Nr.) | **JA** |
| 4 | AGB + Datenschutz rechtlich geprüft | **JA** |
| 5 | RESEND_API_KEY | Nein (Feature-Gate aktiv) |
| 6 | S3/MinIO Storage-Credentials | Nein (Local-Fallback aktiv) |
| 7 | COOKIE_SECURE=true (nur HTTPS) | Nein (per .env) |
| 8 | MongoDB-Backup | **JA** |
| 9 | Token Blacklisting | Nein (60-min TTL akzeptiert) |

---

## Prioritized Backlog (P0 = vor Go-Live)

### P0
- Rechtsangaben klären (Adresse, Impressum, AGB, Datenschutz)
- RESEND_API_KEY beschaffen + Resend-Domain verifizieren
- MongoDB-Backup-Routine
- COOKIE_SECURE=true + HTTPS sicherstellen
- JWT_SECRET auf 64+ Zeichen rotieren

### P1
- S3/MinIO: S3_ENDPOINT + Credentials konfigurieren + `pip install boto3`
- Agency-Portal (Views für agency_admin / agency_agent)
- Vollständiges Rechnungsmodul (nach Preisklärung)
- PWA-Manifest + Service Worker
- Applicant Calculator (nach Preisklärung)
- Webhook-System vollständig

### P2
- OCR-Dokumentvalidierung
- White-Label-Subdomains
- Weitere Verticals (Pflege, Arbeit)
- Native Mobile App

---

## Testing Status (v1.1.0)
- Backend: 92% (Security-Hardening-Tests: 12/14, Brute-Force nach Fix: ✓)
- Frontend: 100%
- Security Checks: Alle kritischen RBAC-Checks bestanden

## Projektspezifische Abweichungen vom Repo
- Supabase → MongoDB (RBAC via FastAPI-Middleware)
- Supabase Auth → Custom JWT
- Supabase Storage → Local/S3/MinIO Abstraction
