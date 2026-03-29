# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Verbindliche Regeln (dauerhaft)
1. **Preview schlägt Handoff** – sichtbarer Zustand > Code-Annahme
2. **Alle KI im Produkt nur über NSCall/nscale**
3. **Preise individuell** – keine pauschalen Festpreise, einzelfallabhängig
4. **Drive + Mem0** als Projektquellen-of-Truth pro Lauf
5. **Keine "Potenzielle Verbesserungen"** am Ende jedes Laufs
6. **Cookie-Consent** vor Go-Live eingerichtet + nachträglich bearbeitbar
7. **Fehlerregister** in Mem0 führen und vor jedem Run prüfen

## Tech Stack
- **Frontend**: React 18, Tailwind CSS, Shadcn/UI, react-i18next
- **Backend**: FastAPI, Motor (async MongoDB), bcrypt, PyJWT, OpenAI SDK (nscale)
- **Database**: MongoDB
- **Email**: Resend (Domain: send.nexify-automate.com, Reply-To: info@stk-aachen.de)
- **AI Provider**: nscale (NSCall) – OpenAI-kompatible API
- **i18n**: react-i18next mit localStorage-Persistenz

## Architecture
```
/app/
├── backend/
│   ├── config.py, server.py, seed.py, deps.py
│   ├── routers/ (auth, leads, applications, documents, tasks, messaging, consents, teacher, notifications, ai_screening, cost_simulator)
│   └── services/ (nscale_provider, ai_screening, email, notifications, automation, audit)
├── frontend/
│   ├── src/
│   │   ├── locales/ (de/en)
│   │   ├── components/
│   │   │   ├── shared/ (CookieBanner, NotificationBell)
│   │   │   └── layout/ (PublicNav, PublicFooter, StaffLayout, ApplicantLayout)
│   │   └── pages/ (public/, portal/, staff/)
│   └── .env
└── memory/
    ├── PRD.md
    ├── FEHLERREGISTER.md
    └── test_credentials.md
```

## Implemented Features (by Phase)

### Phase 1-2: Core Platform (DONE)
- Multi-Workspace, JWT Auth, Lead-Ingest, Pipeline, Kanban, Docs, Tasks, Messaging

### Phase 3.0-3.6: Public Website + Legal (DONE)
- 8 öffentliche Seiten, Bewerbungsformular, Login/Register, Impressum/AGB/Datenschutz

### Phase 3.7b: i18n + Teacher Backend + Consent Backend (DONE)
- Systemweite DE/EN, Resend-Domain, 4 Test-Accounts

### Phase 3.7c: NSCall-AI + Teacher-Frontend + Consent-UI (DONE)
- NSCall-only AI, Teacher-Dashboard, Consent-UI, Onboarding-Tour

### Phase 3.7d: Individuelle Preisregel + Lehrer-Zuweisungs-UI (DONE)
- Individuelle Preisregel systemweit, TeacherAssignmentPanel

### Phase 3.7e: E-Mail-Templates DE/EN + Notification-System (DONE)
- 7 mehrsprachige E-Mail-Templates, In-App Notification-System, Trigger-Verkabelung

### Phase 3.7f: Cookie-Management + Staging-Bereinigung + Mobile-Header (DONE)
- Cookie-Banner DE/EN, Staging-Hinweise entfernt, Mobile-Header optimiert

### Phase 3.7g: Cookie-Manage-Modus + Fehlerregister (DONE - 2026-03-29)
- **Cookie nachträglich bearbeitbar**:
  - "Cookie-Einstellungen" Link im Footer (DE/EN)
  - Manage-Modus zeigt aktuellen Consent-Status und erlaubt Änderungen
  - Schließbar via ×-Button oder Backdrop
  - "Änderungen speichern" + "Alle akzeptieren" im Manage-Modus
  - Datenschutz Sektion 9 referenziert Footer-Link
- **Fehlerregister**: 8 Lessons Learned in /app/memory/FEHLERREGISTER.md
  - Prüfcheckliste vor jedem Run
- **100% Tests**: 18/18 Backend + alle Frontend (iteration_10.json)

## Intern dokumentierte Go-Live-Blocker
- Widerspruch info@stk-aachen.de vs info@cd-stk.com klären
- DSB-Kontaktdaten final bestätigen
- Drittanbieter-Liste prüfen
- Preisangaben final verifizieren
- Juristische Endprüfung aller Rechtstexte

## Backlog

### P1
- Erweiterte Bewerber-Detail-Ansicht für Lehrer
- Staff-Dashboard KPIs / Reporting

### P2
- Payment-Freischaltung
- Partner-/Sub-Agentur-Portal
- Exportfunktionen
- PWA

## MOCKED
- Preiskalkulator: intern, feature-flagged, NICHT entmocken ohne Freigabe
- Zahlungsmodul: "in Vorbereitung"
