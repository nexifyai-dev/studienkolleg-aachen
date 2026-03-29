# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Core Requirements
- Multi-tenant Workspace-basiertes Lead-/Bewerbermanagement
- Öffentliche Website mit Kurs-, Service- und Kontaktseiten (DE/EN)
- Bewerbungsformular mit Dokumenten-Upload
- Staff-Portal: Kanban-Board, Dokumentenprüfung, Aufgaben, Nachrichten
- Bewerber-Portal: Status, Dokumente, Nachrichten, Einwilligungen, Onboarding
- Lehrer-Portal: Zugewiesene Lernende, datenschutzkonformer Zugriff
- AI-gestütztes Screening (nscale/NSCall)
- E-Mail-Benachrichtigungen (Resend via send.nexify-automate.com)
- DSGVO-konforme Datenhaltung + Consent-Management

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

## Architecture
```
/app/
├── backend/
│   ├── config.py           # Zentrale Konfiguration (ENV-basiert)
│   ├── server.py           # FastAPI App + Router-Registration
│   ├── seed.py             # Idempotente Seeds (Admin + Dev-Accounts)
│   ├── deps.py             # Auth-Dependencies + Rollengruppen (inkl. TEACHING_ROLES)
│   ├── database.py         # MongoDB-Verbindung
│   ├── models/schemas.py   # Pydantic-Schemas (inkl. ConsentCapture)
│   ├── routers/
│   │   ├── auth.py         # Login, Register, Invite, Password Reset
│   │   ├── leads.py        # Lead-Ingest, Pipeline
│   │   ├── applications.py # Bewerbungs-CRUD
│   │   ├── documents.py    # Dokument-Upload/Review
│   │   ├── tasks.py        # Aufgabenmanagement
│   │   ├── messaging.py    # Nachrichten-System
│   │   ├── consents.py     # DSGVO-Consent-Management
│   │   ├── teacher.py      # Lehrer-Zuweisungen + Schülerzugriff
│   │   ├── ai_screening.py # AI-Bewerbungsanalyse + /ai/model-registry
│   │   └── cost_simulator.py
│   └── services/
│       ├── nscale_provider.py  # NSCall AI-Inferenzschicht
│       ├── ai_screening.py     # AI-Screening-Logik (nscale)
│       ├── email.py            # Resend-Integration
│       └── audit.py            # Audit-Logging
├── frontend/
│   ├── src/
│   │   ├── locales/         # DE/EN Übersetzungen
│   │   ├── i18n.js          # i18n-Konfiguration
│   │   ├── App.js           # Routing + Auth-Guards + StaffDashboardOrTeacher
│   │   ├── components/
│   │   │   ├── OnboardingTour.js     # 5-Schritt Onboarding für Bewerber
│   │   │   └── layout/
│   │   │       ├── ApplicantLayout.js  # Portal-Layout (+ Consent-Nav + Onboarding)
│   │   │       ├── StaffLayout.js      # Staff-Layout (Teacher-Modus limitiert)
│   │   │       └── AdminLayout.js
│   │   ├── pages/
│   │   │   ├── public/       # 8 öffentliche Seiten (DE/EN)
│   │   │   ├── portal/       # Bewerber-Portal (inkl. ConsentPage)
│   │   │   ├── staff/        # Staff + TeacherDashboard
│   │   │   └── admin/        # Admin-Panel
│   │   └── contexts/AuthContext.js
│   └── .env
└── memory/
    ├── PRD.md
    ├── ROLES_MATRIX.md
    └── test_credentials.md
```

## Implemented Features (by Phase)

### Phase 1-2: Core Platform (DONE)
- Multi-Workspace Architecture, JWT Auth, Lead-Ingest, Pipeline, Kanban, Docs, Tasks, Messaging, AI-Screening

### Phase 3.0-3.6: Public Website + Legal (DONE)
- 8 öffentliche Seiten, Bewerbungsformular, Login/Register, Impressum/AGB/Datenschutz

### Phase 3.7b: i18n + Teacher-Rolle + Consent (DONE - 2026-03-29)
- Systemweite DE/EN für alle Public-Seiten, Resend auf send.nexify-automate.com, 4 Test-Accounts, Teacher-Rolle Backend, Consent-Backend

### Phase 3.7c: NSCall-AI + Teacher-Frontend + Consent-UI (DONE - 2026-03-29)
- **NSCall-only AI-Strategie**: Alle KI-Funktionen über nscale API
  - Screening: Qwen/Qwen3-235B-A22B-Instruct-2507
  - Klassifikation: meta-llama/Llama-3.3-70B-Instruct
  - Zusammenfassung: Qwen/Qwen3-32B
  - Modell-Registry-API: /api/ai/model-registry (auditierbar)
- **Teacher-Dashboard**: Zugewiesene Lernende, Datenschutzhinweis, Stats, E-Mail/Telefon-Kontakt
- **Consent-UI**: Bewerber-Portal mit Erteilen/Widerrufen, Scope-Anzeige, Ausschlüsse, Historie
- **Onboarding-Tour**: 5-Schritt-Modal für neue Bewerber (DE/EN, localStorage-Persistenz)
- **WhatsApp**: Nummer aktualisiert auf +49 1520 8496876
- **Tests**: 100% Backend (19/19) + Frontend

## Pending / Backlog

### P1 (Nächste Priorität)
- E-Mail-Templates mehrsprachig (DE/EN basierend auf user.language_pref)
- Notification-System (Push + In-App)
- Staff-seitige Lehrer-Zuweisungs-UI (aktuell nur API)
- Erweiterte Bewerber-Detail-Ansicht für Lehrer

### P2 (Zukunft)
- Preiskalkulator (MOCKED) entmocken
- Partner-Portal für Agenturen
- Pflegefachschule & Arbeit/Ausbildung Workspaces aktivieren
- Export-Funktionalität für Bewerberdaten
- PWA / Offline-Modus

### Offene rechtliche Punkte
- Finale juristische Prüfung aller Rechtstexte vor Go-Live
- Aufbewahrungsfristen / Löschkonzept definieren
- Prüfung: Lehrzugriff als Auftragsverarbeitung?
- Recht auf Datenportabilität: Export-Format spezifizieren

## Mocked/Placeholder
- Preiskalkulator (intern): COST_SIMULATOR_ENABLED=false
