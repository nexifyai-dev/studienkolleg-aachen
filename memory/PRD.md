# W2G Platform – PRD / Memory

**Stand:** 29. März 2026  
**Projekt:** Studienkolleg Aachen / Way2Germany – Mehrmandantenfähige Plattform

---

## Original Problemstellung
Produktionsreife, skalierbare, mehrmandantenfähige Plattform für Studienkolleg Aachen / Way2Germany.
Saubere Trennung: Public Website, Applicant Portal, Staff/Admin-Bereich, Datenmodell, Rollen/Rechte,
Dokumentenlogik, Automationen, Auditfähigkeit, i18n-fähig.

Studienkolleg-first im MVP, aber Architektur nicht als One-Off.

---

## Verbindliche User-Entscheidungen
- **Auth:** JWT Custom Auth (Email + Passwort), kein Google OAuth
- **Sprachen:** Mehrsprachig, Deutsch primär, i18n-Struktur von Beginn an
- **E-Mail:** Resend (RESEND_API_KEY noch nicht konfiguriert – Feature-Gate)
- **DB:** MongoDB (projektspezifische Abweichung von Supabase-Empfehlung im Repo)
- **Design:** Live-Seite als Referenz, modernisiert, #113655 primär, #B3CDE1 akzent

---

## Architektur

### Stack
- **Backend:** FastAPI + Motor (async MongoDB) + PyJWT + bcrypt
- **Frontend:** React 18 + Tailwind CSS 3 + react-router-dom + i18next + lucide-react
- **DB:** MongoDB lokal, DB_NAME = w2g_platform
- **Dienste:** Supervisor managed (backend:8001, frontend:3000, nginx proxy)

### Verzeichnisstruktur
```
/app/
├── backend/
│   ├── server.py           # FastAPI Monolith MVP (856 Zeilen – Split nach v1.1)
│   ├── .env                # MONGO_URL, DB_NAME, JWT_SECRET, ADMIN_*, RESEND_API_KEY
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js          # Routing (Public/Auth/Portal/Staff/Admin)
│   │   ├── i18n.js         # i18next Konfiguration
│   │   ├── contexts/AuthContext.js
│   │   ├── lib/utils.js    # Stage Labels, Colors, Roles, Format-Helpers
│   │   ├── locales/de/translation.json
│   │   ├── locales/en/translation.json
│   │   ├── components/layout/  # PublicNav, PublicFooter, ApplicantLayout, StaffLayout, AdminLayout
│   │   └── pages/
│   │       ├── public/     # HomePage, ApplyPage, CoursesPage, ServicesPage, ContactPage, LegalPage
│   │       ├── auth/       # LoginPage, RegisterPage, ForgotPasswordPage
│   │       ├── portal/     # DashboardPage, JourneyPage, DocumentsPage, MessagesPage, FinancialsPage, SettingsPage
│   │       ├── staff/      # StaffDashboard, KanbanPage, ApplicantDetailPage
│   │       └── admin/      # AdminDashboard, UsersPage, AuditPage
│   ├── tailwind.config.js  # Farben: primary #113655, accent #B3CDE1
│   └── .env                # REACT_APP_BACKEND_URL
└── memory/
    ├── PRD.md              # Dieses Dokument
    └── test_credentials.md
```

---

## Datenmodell (MongoDB Collections)

| Collection | Zweck |
|---|---|
| users | Alle Nutzer (alle Rollen) |
| workspaces | Bereiche (studienkolleg, sprachkurse, pflege, arbeit) |
| workspace_members | Rollenzuweisung pro Workspace |
| applications | Bewerbungen (Lead → Completed) |
| application_activities | Stage-Change-Historie |
| documents | Dokumente (metadata, nicht binary) |
| conversations | Messaging-Threads |
| messages | Nachrichten |
| tasks | Aufgaben |
| audit_logs | Systemaudit (append-only) |
| notifications | Push-Notifications |
| user_consents | DSGVO-Consent-Tracking |
| invite_tokens | Einladungslinks (TTL: 7d) |
| password_reset_tokens | Reset-Links (TTL: 1h) |
| login_attempts | Brute-Force-Tracking |
| webhook_events | (vorbereitet) |
| automation_runs | (vorbereitet) |
| comments | Interne Kommentare |
| invoices | (vorbereitet – Payment Gate) |

---

## Rollen
superadmin → admin → staff / accounting_staff → agency_admin → agency_agent → affiliate → applicant

---

## Was implementiert ist (v1.0 MVP Foundation)

### Backend (DONE)
- [x] JWT Auth: Login, Register (mit Lead-Claiming-Flow), Logout, Me, Refresh
- [x] Invite-Flow: Admin generiert Token → Nutzer registriert sich
- [x] Forgot/Reset Password
- [x] Brute-Force-Schutz (5 Versuche, 15min Lockout)
- [x] Workspace Seeding (studienkolleg, sprachkurse, pflege, arbeit)
- [x] Admin Auto-Seed
- [x] Lead Ingest (POST /api/leads/ingest) mit Duplicate-Flag
- [x] Applications CRUD + Stage-Wechsel
- [x] Documents Upload/Review-Status
- [x] Tasks CRUD
- [x] Conversations + Messages
- [x] Notifications (list)
- [x] Consent Capture
- [x] Audit Logs (list)
- [x] Dashboard Stats
- [x] Health Check
- [x] Alle Indexes

### Frontend (DONE)
- [x] i18n DE/EN mit Sprachschalter
- [x] Tailwind Design System (#113655, #B3CDE1)
- [x] PublicNav (responsive, mobile burger menu)
- [x] PublicFooter
- [x] Homepage (Hero, Trust-Bar, Courses, Process, FAQ, CTA-Banner)
- [x] ApplyPage (Formular → /api/leads/ingest)
- [x] CoursesPage (T/M/W/MT)
- [x] ServicesPage
- [x] ContactPage
- [x] LegalPage (Impressum, Datenschutz, AGB – alle mit [OFFEN]-Markierung)
- [x] LoginPage
- [x] RegisterPage (inkl. Invite-Token-Flow)
- [x] ForgotPasswordPage
- [x] ApplicantLayout (Sidebar)
- [x] Portal: Dashboard, Journey (Timeline), Documents (Upload/List), Messages, Financials, Settings
- [x] StaffLayout
- [x] Staff: Dashboard (Stats + Tabelle), Kanban Board (Stage-Advance), ApplicantDetail
- [x] AdminLayout
- [x] Admin: Dashboard, UsersPage (Einladungslink-Generator), AuditPage
- [x] Protected Routes (nach Rolle)
- [x] Auth Context + Auto-Redirect nach Login

---

## Offene Punkte / [OFFEN]-Markierungen

| # | Punkt | Priorität | Blocker |
|---|---|---|---|
| 1 | Adresse (Theaterstraße 24 vs. 30-32) | HOCH | Vor Go-Live klären |
| 2 | Preislogik (5500+500 vs. 6000 vs. 3500+3000) | HOCH | Vor Payment-Gate |
| 3 | Arboria Weblizenz | MITTEL | Inter als Fallback aktiv |
| 4 | Steuer/VAT/Refund-Logik | HOCH | Payment-Gate blockiert |
| 5 | RESEND_API_KEY | MITTEL | Email nicht aktiv |
| 6 | Vollständiges Impressum (HR-Nr., GF) | HOCH | Vor Go-Live |
| 7 | AGB + Datenschutz (rechtlich geprüft) | HOCH | Vor Go-Live |
| 8 | WhatsApp Budget Policy | NIEDRIG | Nicht Go-Live-Blocker |
| 9 | Token Auto-Refresh Frontend | MITTEL | UX-Issue bei langen Sessions |

---

## Prioritized Backlog

### P0 (vor Go-Live)
- Offene Rechtsangaben klären (Adresse, Impressum, AGB, Datenschutz)
- RESEND_API_KEY konfigurieren + E-Mail-Templates (Willkommen, Bewerbung eingegangen, Dokument angefordert)
- Preislogik finalisieren und Payment-Gate öffnen
- Datei-Upload (echte Binärdateien) via MinIO/S3/GridFS statt Metadaten-Only
- Token Auto-Refresh Frontend

### P1 (v1.1 Post-Launch)
- server.py aufteilen in Routen-Module
- Echtzeit-Notifications (WebSocket oder Polling)
- Agency-Portal (agency_admin / agency_agent Views)
- Affiliate-Tracking (referral_code)
- Vollständiges Rechnungsmodul
- E-Mail-Templates vollständig implementieren
- CMS für Public-Page-Inhalte
- OCR-Dokumentvalidierung

### P2 (v2.0 / Multi-Tenant-Ausbau)
- White-Label-Subdomains
- Weitere Verticals (Pflege, Arbeit)
- Mobile PWA-Optimierung
- Google Analytics / Matomo
- Webhook-System (vollständig)
- Automatisierungsregeln

---

## Projektspezifische Abweichungen vom Repo
- **Supabase → MongoDB**: Alle RLS-Anforderungen werden via FastAPI-Middleware abgebildet
- **Supabase Auth → Custom JWT**: Gleiche Sicherheitslogik, andere Implementierung
- **Supabase Storage → Metadaten-Only (MVP)**: Echte Binärdaten in P0 über S3/MinIO

---

## Testing Status
- Backend: 100% (11/11 Tests bestanden, Testing Agent v1)
- Frontend: 95% (alle Kernflows funktionieren, 2 Minor-Issues dokumentiert)
- Credentials: admin@studienkolleg-aachen.de / Admin@2026!
