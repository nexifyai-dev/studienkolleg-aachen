# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Verbindliche Regeln (dauerhaft)
1. **Preview schlägt Handoff** – sichtbarer Zustand > Code-Annahme
2. **Alle KI im Produkt nur über NSCall/nscale**
3. **Preise individuell** – keine pauschalen Festpreise, einzelfallabhängig (auch für Sub-Agenturen/Partner)
4. **Drive + Mem0** als Projektquellen-of-Truth pro Lauf
5. **Keine "Potenzielle Verbesserungen"** am Ende jedes Laufs

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend**: FastAPI, Motor (async MongoDB), bcrypt, PyJWT, OpenAI SDK (nscale)
- **Database**: MongoDB
- **Email**: Resend (Domain: send.nexify-automate.com, Reply-To: info@stk-aachen.de)
- **AI Provider**: nscale (NSCall) – OpenAI-kompatible API
  - Screening: Qwen/Qwen3-235B-A22B-Instruct-2507
  - Klassifikation: meta-llama/Llama-3.3-70B-Instruct
  - Zusammenfassung: Qwen/Qwen3-32B
  - Empfehlung: Qwen/Qwen3-235B-A22B-Instruct-2507
- **i18n**: react-i18next mit localStorage-Persistenz
- **WhatsApp**: +49 1520 8496876

## Architecture
```
/app/
├── backend/
│   ├── config.py             # Zentrale Konfiguration
│   ├── server.py             # FastAPI App
│   ├── seed.py               # 4 Rollen-Seeds (Admin, Staff, Teacher, Applicant)
│   ├── deps.py               # Auth + Rollengruppen (TEACHING_ROLES, TEACHER_ROLES)
│   ├── routers/
│   │   ├── auth.py           # Login, Register, Invite, Password Reset
│   │   ├── leads.py          # Lead-Ingest, Pipeline
│   │   ├── applications.py   # Bewerbungs-CRUD + Status-Change-Trigger
│   │   ├── documents.py      # Dokument-Upload/Review + Upload-Trigger
│   │   ├── tasks.py          # Aufgabenmanagement
│   │   ├── messaging.py      # Nachrichten-System
│   │   ├── consents.py       # DSGVO-Consent + Consent-Change-Trigger
│   │   ├── teacher.py        # Lehrer-Zuweisungen + Assignment-Trigger
│   │   ├── notifications.py  # In-App Notification CRUD (NEU Phase 3.7e)
│   │   ├── ai_screening.py   # AI-Analyse + /ai/model-registry
│   │   └── cost_simulator.py # MOCKED, intern, individuelle Preise
│   └── services/
│       ├── nscale_provider.py # NSCall AI-Provider (4 Task-Modelle)
│       ├── ai_screening.py   # AI-Screening-Logik (nscale)
│       ├── email.py          # Resend – 7 DE/EN Templates
│       ├── notifications.py  # Notification-Service (8 Typen, DE/EN)
│       ├── automation.py     # Workflow-Trigger (E-Mail + Notification)
│       └── audit.py          # Audit-Logging
├── frontend/
│   ├── src/
│   │   ├── locales/          # DE/EN (inkl. Pricing-FAQ)
│   │   ├── components/
│   │   │   ├── OnboardingTour.js    # 5-Schritt Bewerber-Onboarding
│   │   │   ├── shared/
│   │   │   │   └── NotificationBell.js  # Glocke + Dropdown (NEU Phase 3.7e)
│   │   │   └── layout/
│   │   │       ├── ApplicantLayout.js  # Portal + Consent-Nav + Onboarding + Bell
│   │   │       └── StaffLayout.js      # Staff + Teacher-Modus + Bell
│   │   └── pages/
│   │       ├── public/        # 8 Seiten (DE/EN, individuelle Preise)
│   │       ├── portal/        # Bewerber (+ ConsentPage)
│   │       └── staff/         # Staff + TeacherDashboard + ApplicantDetail
│   └── .env
└── memory/
    ├── PRD.md
    ├── ROLES_MATRIX.md
    └── test_credentials.md
```

## Implemented Features (by Phase)

### Phase 1-2: Core Platform (DONE)
- Multi-Workspace, JWT Auth, Lead-Ingest, Pipeline, Kanban, Docs, Tasks, Messaging

### Phase 3.0-3.6: Public Website + Legal (DONE)
- 8 öffentliche Seiten, Bewerbungsformular, Login/Register, Impressum/AGB/Datenschutz

### Phase 3.7b: i18n + Teacher Backend + Consent Backend (DONE)
- Systemweite DE/EN, Resend-Domain, 4 Test-Accounts, Teacher-Rolle Backend, Consent Backend

### Phase 3.7c: NSCall-AI + Teacher-Frontend + Consent-UI (DONE)
- NSCall-only AI, Teacher-Dashboard, Consent-UI, Onboarding-Tour, WhatsApp +49 1520 8496876

### Phase 3.7d: Individuelle Preisregel + Lehrer-Zuweisungs-UI (DONE - 2026-03-29)
- Individuelle Preisregel systemweit verankert (AGB, FAQ, Prozess, Cost Simulator)
- Sub-Agenturen/Partner: Textlich und architektonisch vorbereitet
- Lehrer-Zuweisungs-UI (TeacherAssignmentPanel)

### Phase 3.7e: E-Mail-Templates DE/EN + Notification-System (DONE - 2026-03-29)
- **7 mehrsprachige E-Mail-Templates (DE/EN)**:
  - send_welcome, send_application_received, send_document_requested,
  - send_status_changed, send_password_reset, send_invite, send_teacher_assigned
  - Alle ohne Festpreise, professionelle D/A/CH-konforme Sprache
  - W2G Academy GmbH korrekt referenziert, Reply-To: info@stk-aachen.de
- **In-App Notification-System**:
  - 8 Notification-Typen mit DE/EN-Templates
  - 4 API-Endpunkte: GET list, GET unread-count, PATCH read, PATCH read-all
  - NotificationBell-Komponente in Staff- und Applicant-Layout
  - Unread-Badge, Dropdown, Mark-as-Read, Mark-All-Read
  - Auto-Polling alle 30 Sekunden
- **Trigger-Verkabelung an Kernflows**:
  - Statuswechsel → E-Mail + Notification an Bewerber
  - Teacher-Zuweisung → E-Mail + Notification an Bewerber + Lehrer
  - Consent Grant/Revoke → Notification an zugewiesenen Lehrer
  - Dokument-Upload → Notification an Staff/Admin
- **100% Tests**: 23/23 Backend + alle Frontend (iteration_8.json)

## Pending / Backlog

### P1 (Nächste Priorität)
- Erweiterte Bewerber-Detail-Ansicht für Lehrer
- Staff-Dashboard KPIs / Reporting

### P2 (Zukunft)
- Payment-Freischaltung
- Preiskalkulator entmocken (erst nach freigegebener Preislogik)
- Partner-/Sub-Agentur-Portal (individuelle Konditionen)
- Pflegefachschule & Arbeit/Ausbildung Workspaces
- Export-Funktionalität
- PWA

### Offene rechtliche Punkte
- Finale juristische Prüfung vor Go-Live
- Aufbewahrungsfristen / Löschkonzept
- Lehrzugriff als Auftragsverarbeitung?
- Preislogik finale Freigabe
- Sub-Agentur-Vertragsmuster

## MOCKED
- Preiskalkulator: intern, feature-flagged, individuelle Preise, NICHT entmocken ohne Freigabe
