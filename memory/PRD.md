# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Verbindliche Regeln (dauerhaft)
1. **Preview schlägt Handoff** – sichtbarer Zustand > Code-Annahme
2. **Alle KI im Produkt nur über NSCall/nscale**
3. **Preise individuell** – keine pauschalen Festpreise, einzelfallabhängig (auch für Sub-Agenturen/Partner)
4. **Drive + Mem0** als Projektquellen-of-Truth pro Lauf

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
│   │   ├── applications.py   # Bewerbungs-CRUD
│   │   ├── documents.py      # Dokument-Upload/Review
│   │   ├── tasks.py          # Aufgabenmanagement
│   │   ├── messaging.py      # Nachrichten-System
│   │   ├── consents.py       # DSGVO-Consent-Management
│   │   ├── teacher.py        # Lehrer-Zuweisungen + /list + Schülerzugriff
│   │   ├── ai_screening.py   # AI-Analyse + /ai/model-registry
│   │   └── cost_simulator.py # MOCKED, intern, individuelle Preise
│   └── services/
│       ├── nscale_provider.py # NSCall AI-Provider (4 Task-Modelle)
│       ├── ai_screening.py   # AI-Screening-Logik (nscale)
│       ├── email.py          # Resend
│       └── audit.py          # Audit-Logging
├── frontend/
│   ├── src/
│   │   ├── locales/          # DE/EN (inkl. Pricing-FAQ)
│   │   ├── components/
│   │   │   ├── OnboardingTour.js    # 5-Schritt Bewerber-Onboarding
│   │   │   └── layout/
│   │   │       ├── ApplicantLayout.js  # Portal + Consent-Nav + Onboarding
│   │   │       └── StaffLayout.js      # Staff + Teacher-Modus
│   │   └── pages/
│   │       ├── public/        # 8 Seiten (DE/EN, individuelle Preise)
│   │       ├── portal/        # Bewerber (+ ConsentPage)
│   │       └── staff/         # Staff + TeacherDashboard + ApplicantDetail (+ TeacherAssignmentPanel)
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
- **Individuelle Preisregel systemweit verankert**:
  - AGB §5: Einzelfallabhängig, keine Pauschalpreise, individuelles Angebot
  - AGB §8: Storno "sofern nicht im Einzelfall abweichend vereinbart"
  - AGB §10: Verwaltungspauschale "Im Einzelfall können die tatsächlichen Kosten abweichen"
  - FAQ: Neue Frage "Was kosten die Kurse?" → individuell, kein Festpreis
  - Prozess-Schritt 4: "individuelles Angebot" statt "Zahlung"
  - Cost Simulator: Disclaimer für Einzelfallabhängigkeit + Sub-Agenturen
- **Sub-Agenturen/Partner**: Textlich und architektonisch vorbereitet für individuelle Konditionen
- **Lehrer-Zuweisungs-UI**:
  - TeacherAssignmentPanel in ApplicantDetailPage
  - Staff kann Lehrer zuweisen/entfernen
  - Datenschutz-Hinweis im Panel
  - GET /api/teacher/list für Staff-Zugriff
- **100% Tests**: 23/23 Backend + alle Frontend

## Pending / Backlog

### P1 (Nächste Priorität)
- E-Mail-Templates mehrsprachig (DE/EN)
- Notification-System (Push + In-App)
- Erweiterte Bewerber-Detail-Ansicht für Lehrer
- Staff-Dashboard KPIs / Reporting

### P2 (Zukunft)
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
