# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Verbindliche Regeln (dauerhaft)
1. **Preview schlägt Handoff** – sichtbarer Zustand > Code-Annahme
2. **Alle KI im Produkt nur über NSCall/nscale**
3. **Preise individuell** – keine pauschalen Festpreise, einzelfallabhängig (auch für Sub-Agenturen/Partner)
4. **Drive + Mem0** als Projektquellen-of-Truth pro Lauf
5. **Keine "Potenzielle Verbesserungen"** am Ende jedes Laufs
6. **Cookie-Consent** vor Go-Live eingerichtet

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend**: FastAPI, Motor (async MongoDB), bcrypt, PyJWT, OpenAI SDK (nscale)
- **Database**: MongoDB
- **Email**: Resend (Domain: send.nexify-automate.com, Reply-To: info@stk-aachen.de)
- **AI Provider**: nscale (NSCall) – OpenAI-kompatible API
- **i18n**: react-i18next mit localStorage-Persistenz
- **WhatsApp**: +49 1520 8496876

## Architecture
```
/app/
├── backend/
│   ├── config.py             # Zentrale Konfiguration
│   ├── server.py             # FastAPI App
│   ├── seed.py               # 4 Rollen-Seeds (Admin, Staff, Teacher, Applicant)
│   ├── deps.py               # Auth + Rollengruppen
│   ├── routers/
│   │   ├── auth.py           # Login, Register, Invite, Password Reset
│   │   ├── leads.py          # Lead-Ingest, Pipeline
│   │   ├── applications.py   # Bewerbungs-CRUD + Status-Change-Trigger
│   │   ├── documents.py      # Dokument-Upload/Review + Upload-Trigger
│   │   ├── tasks.py          # Aufgabenmanagement
│   │   ├── messaging.py      # Nachrichten-System
│   │   ├── consents.py       # DSGVO-Consent + Consent-Change-Trigger
│   │   ├── teacher.py        # Lehrer-Zuweisungen + Assignment-Trigger
│   │   ├── notifications.py  # In-App Notification CRUD
│   │   ├── ai_screening.py   # AI-Analyse + /ai/model-registry
│   │   └── cost_simulator.py # MOCKED
│   └── services/
│       ├── nscale_provider.py # NSCall AI-Provider
│       ├── ai_screening.py   # AI-Screening-Logik
│       ├── email.py          # Resend – 7 DE/EN Templates
│       ├── notifications.py  # Notification-Service (8 Typen, DE/EN)
│       ├── automation.py     # Workflow-Trigger (E-Mail + Notification)
│       └── audit.py          # Audit-Logging
├── frontend/
│   ├── src/
│   │   ├── locales/          # DE/EN
│   │   ├── components/
│   │   │   ├── shared/
│   │   │   │   ├── CookieBanner.js    # Cookie-Consent (NEU Phase 3.7f)
│   │   │   │   └── NotificationBell.js
│   │   │   └── layout/
│   │   │       ├── PublicNav.js        # Mobile-optimiert (NEU Phase 3.7f)
│   │   │       ├── ApplicantLayout.js
│   │   │       └── StaffLayout.js
│   │   └── pages/
│   │       ├── public/        # 8 Seiten + Legal (bereinigt, keine Staging-Hinweise)
│   │       ├── portal/        # Bewerber
│   │       └── staff/         # Staff + Teacher
│   └── .env
└── memory/
    ├── PRD.md
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
- NSCall-only AI, Teacher-Dashboard, Consent-UI, Onboarding-Tour

### Phase 3.7d: Individuelle Preisregel + Lehrer-Zuweisungs-UI (DONE)
- Individuelle Preisregel systemweit, Lehrer-Zuweisungs-UI (TeacherAssignmentPanel)

### Phase 3.7e: E-Mail-Templates DE/EN + Notification-System (DONE)
- 7 mehrsprachige E-Mail-Templates, In-App Notification-System, Trigger-Verkabelung

### Phase 3.7f: Cookie-Management + Staging-Bereinigung + Mobile-Header (DONE - 2026-03-29)
- **Cookie-Management-System**:
  - CookieBanner-Komponente mit DE/EN-Texten
  - 2 Kategorien: Technisch notwendig (immer aktiv) + Funktional (Toggle)
  - 3 Aktionsoptionen: Alle akzeptieren, Auswahl bestätigen, Nur notwendige
  - Consent in localStorage (w2g_cookie_consent) mit Zeitstempel + Version
  - Details-Panel mit aufgelisteten Cookies pro Kategorie
  - W2G Academy GmbH-Hinweis + Link zur Datenschutzerklärung
- **Staging-Hinweise entfernt**:
  - 7 [OFFEN]-Blöcke aus Impressum/AGB/Datenschutz entfernt
  - 1 [HINWEIS]-Block aus Datenschutz entfernt
  - AccordionSection rendert keine Warn-Boxen mehr
  - review_note aus DE/EN-Locale geleert
  - [OFFEN] aus FinancialsPage durch "in Vorbereitung" ersetzt
- **Datenschutz Sektion 9** aktualisiert: beschreibt jetzt das echte Cookie-Management-System
- **Mobile-Header optimiert**:
  - h-14 statt h-16, kompaktere Abstände (px-3)
  - DE/EN-Switcher im Header sichtbar (nicht mehr im Burger-Menü versteckt)
  - min-w-[40px] min-h-[40px] Touch-Targets für Burger
  - Logo-Text ab min-[420px] sichtbar (vorher sm:block = 640px)
  - Mobile-Menü: größere Tap-Targets (py-2.5), aktive Seite hervorgehoben
  - Apply-CTA als volle Breite im Mobile-Menü
- **Test-Logins verifiziert**: Alle 4 Rollen funktionieren
- **100% Tests**: 13/13 Backend + alle Frontend (iteration_9.json)

## Drive-Gegenprüfung (Phase 3.7f)
- Ordnerstruktur geprüft: 22+ Dokumente + Projektdaten
- Verifiziert: Statuslogik, Rollen, Docs, Consent, Notification, Cookie/DSGVO
- Anfrage-/Bearbeitungslogik: CRUD, Statuswechsel, Suche, Filter, Zuweisung, Historie vorhanden
- Offene Punkte intern dokumentiert (siehe Backlog)

## Intern dokumentierte Go-Live-Blocker
(Aus den entfernten sichtbaren Hinweisen – intern weitergeführt)
- Widerspruch info@stk-aachen.de vs info@cd-stk.com als Kontakt-E-Mail klären
- Vollständige Kontaktdaten des Datenschutzbeauftragten final bestätigen
- Vollständige Drittanbieter-Liste prüfen und dokumentieren
- Preisangaben final verifizieren
- Finale juristische Prüfung aller Rechtstexte

## Backlog

### P1 (Nächste Priorität)
- Erweiterte Bewerber-Detail-Ansicht für Lehrer
- Staff-Dashboard KPIs / Reporting

### P2 (Zukunft)
- Payment-Freischaltung
- Partner-/Sub-Agentur-Portal
- Exportfunktionen
- PWA

## MOCKED
- Preiskalkulator: intern, feature-flagged, NICHT entmocken ohne Freigabe
- Zahlungsmodul: "in Vorbereitung", erst nach Steuer-/Refund-Logik-Klärung
