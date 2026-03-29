# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Core Requirements
- Multi-tenant Workspace-basiertes Lead-/Bewerbermanagement
- Öffentliche Website mit Kurs-, Service- und Kontaktseiten
- Bewerbungsformular mit Dokumenten-Upload
- Staff-Portal: Kanban-Board, Dokumentenprüfung, Aufgaben, Nachrichten
- Bewerber-Portal: Status, Dokumente, Nachrichten
- AI-gestütztes Screening (GPT-basiert)
- E-Mail-Benachrichtigungen (Resend)
- DSGVO-konforme Datenhaltung

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend**: FastAPI, Motor (async MongoDB), bcrypt, PyJWT
- **Database**: MongoDB
- **Email**: Resend (Domain: send.nexify-automate.com)
- **AI**: Emergent LLM Key (GPT für Screening)
- **i18n**: react-i18next mit localStorage-Persistenz

## Architecture
```
/app/
├── backend/
│   ├── config.py         # Zentrale Konfiguration (ENV-basiert)
│   ├── server.py         # FastAPI App + Router-Registration
│   ├── seed.py           # Idempotente Datenbank-Seeds (Admin + Dev-Accounts)
│   ├── deps.py           # Auth-Dependencies + Rollengruppen
│   ├── database.py       # MongoDB-Verbindung
│   ├── models/schemas.py # Pydantic-Schemas
│   ├── routers/          # API-Endpunkte
│   │   ├── auth.py       # Login, Register, Invite, Password Reset
│   │   ├── leads.py      # Lead-Ingest, Pipeline
│   │   ├── applications.py # Bewerbungs-CRUD
│   │   ├── documents.py  # Dokument-Upload/Review
│   │   ├── tasks.py      # Aufgabenmanagement
│   │   ├── messaging.py  # Nachrichten-System
│   │   ├── consents.py   # DSGVO-Consent-Management
│   │   ├── teacher.py    # Lehrer-Zuweisungen + Schülerzugriff
│   │   ├── ai_screening.py # AI-Bewerbungsanalyse
│   │   └── cost_simulator.py # Preiskalkulator (MOCKED)
│   └── services/
│       ├── email.py      # Resend-Integration
│       └── audit.py      # Audit-Logging
├── frontend/
│   ├── src/
│   │   ├── locales/de/translation.json  # Deutsche Übersetzungen
│   │   ├── locales/en/translation.json  # Englische Übersetzungen
│   │   ├── i18n.js        # i18n-Konfiguration
│   │   ├── App.js         # Routing + Auth-Guards
│   │   ├── pages/public/  # Öffentliche Seiten
│   │   ├── pages/staff/   # Staff-Dashboard
│   │   ├── pages/portal/  # Bewerber-Portal
│   │   └── components/    # Shared Components
│   └── .env              # REACT_APP_BACKEND_URL
└── memory/
    ├── PRD.md            # Dieses Dokument
    ├── ROLES_MATRIX.md   # Rollen-/Rechtematrix
    └── test_credentials.md # Test-Zugangsdaten
```

## Implemented Features (by Phase)

### Phase 1-2: Core Platform (DONE)
- Multi-Workspace Architecture
- JWT Auth mit Brute-Force-Schutz
- Lead-Ingest + Pipeline-Management
- Dokumenten-Upload + Review-Workflow
- Staff Kanban-Board
- Bewerber-Portal
- Aufgaben-/Messaging-System
- AI-Screening Integration

### Phase 3.0-3.5: Public Website (DONE)
- Homepage mit Hero, Kurse, Services, Prozess, FAQ, CTA
- Courses-Seite mit Schwerpunktkursen + Sprachkursen
- Services-Seite mit Prozess-Timeline
- Kontaktseite mit Standort, WhatsApp, CTA
- Bewerbungsformular mit 3-Schritt-Flow + Dokument-Upload
- Login/Register-Seiten

### Phase 3.6: Legal Pages (DONE)
- Impressum mit korrekter Adresslogik (Gesellschaftssitz vs. Unterrichtsstandort)
- AGB mit Leistungsbeschreibung
- Datenschutzerklärung (DSGVO-konform)
- Entfernung aller Staging-Hinweise

### Phase 3.7b: i18n + Teacher + Consent (DONE - 2026-03-29)
- **Systemweite Mehrsprachigkeit DE/EN** für alle 8 Public-Seiten
- **Sprachumschalter** in Desktop- UND Mobile-Navigation
- **EN-Disclaimer** auf allen Rechtsseiten (nicht nur AGB/Privacy)
- **Resend-Domain** auf send.nexify-automate.com umgestellt
- **4 Test-Accounts**: Admin, Staff, Teacher, Applicant (env-gesteuert)
- **Teacher-Rolle**: assignment-basiert, consent-gated, purpose-limited
- **Consent-Modell**: DSGVO-konforme Einwilligungslogik für Lehrerzugriff
- **Rollen-/Rechtematrix**: Dokumentiert in ROLES_MATRIX.md

## Pending / Backlog

### P0 (Blocker)
- Keine aktuell

### P1 (Nächste Priorität)
- WhatsApp Business QR-Kopplung auf Kontaktseite (keine Nummer freigegeben)
- Teacher-Frontend-Dashboard (Backend-APIs vorhanden)
- Consent-UI im Bewerber-Portal (Backend-APIs vorhanden)

### P2 (Zukunft)
- Preiskalkulator (aktuell MOCKED)
- Partner-Portal für Agenturen
- Pflegefachschule & Arbeit/Ausbildung Workspaces aktivieren
- E-Mail-Templates mehrsprachig (DE/EN basierend auf user.language_pref)
- Export-Funktionalität für Bewerberdaten

### Offene rechtliche Punkte
- Finale juristische Prüfung aller Rechtstexte vor Go-Live
- Aufbewahrungsfristen / Löschkonzept definieren
- Recht auf Datenportabilität: Export-Format spezifizieren
- Prüfung: Lehrzugriff als Auftragsverarbeitung?

## Mocked/Placeholder
- Preiskalkulator (intern): COST_SIMULATOR_ENABLED=false
