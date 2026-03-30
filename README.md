# Studienkolleg Aachen / Way2Germany Platform

Zentrale Bewerbungs- und CRM-Plattform für die W2G Academy GmbH (Studienkolleg Aachen). Das System verbindet öffentliche Lead-Erfassung, Applicant Self-Service, Staff-/Teacher-Bearbeitung, Partner-Referrals und Admin-Governance in einer konsistenten Multi-Portal-Architektur.

## Zweck des Systems
- Bewerberprozesse von Erstkontakt bis Einschreibung strukturiert führen.
- Rollen- und datenschutzkonforme Zusammenarbeit zwischen Applicant, Staff, Teacher, Partner und Admin ermöglichen.
- Operatives CRM mit Aufgaben, Nachrichten, Dokumenten und Follow-ups bereitstellen.
- KI-gestützte Vorprüfung als Entscheidungshilfe anbieten (nicht als finale Entscheidung).

## Betreiber, Marke, Geschäftsmodell
- **Betreiber:** W2G Academy GmbH, Aachen.
- **Markenlogik:** Studienkolleg Aachen / Way2Germany.
- **Projekttyp:** Applicant Management + CRM + Portal-System.
- **Zielbild:** auditierbare, rollenklare, skalierbare Plattform für D/A/CH-konformen Studienkolleg-Betrieb.

## Systemübersicht
- **Public:** Marketing-Seiten + Bewerbungsformular.
- **Applicant Portal (`/portal`):** Journey, Dokumente, Nachrichten, Consent, Einstellungen.
- **Staff Portal (`/staff`):** Kanban, Aufgaben, Applicant-Detail, Messaging, AI-Screening.
- **Teacher View (`/staff`, Rolle `teacher`):** zugewiesene Fälle, consent-gated Zugriff.
- **Admin (`/admin`):** Dashboard, Nutzer, Audit.
- **Partner (`/partner`):** Referral-Link, Vermittlungen, Partner-Einstellungen.

## Hauptmodule
- Auth, RBAC, Consent, Applications, Documents, Tasks, Messaging, Follow-ups, AI Screening, Notifications, Export, Partner.

## Rollenüberblick
- `superadmin`, `admin`, `staff`, `accounting_staff`, `teacher`, `applicant`, `affiliate` (+ dokumentierte Partner-Varianten in Memory).
- Details in `docs/roles/roles-and-permissions.md`.

## Tech-Stack
- **Frontend:** React (CRA), React Router 6, Tailwind, i18next.
- **Backend:** FastAPI, Motor/MongoDB, Pydantic.
- **AI:** DeepSeek via zentraler Provider-Schicht.
- **Storage:** lokal oder S3/MinIO abstrahiert.
- **Mail:** Resend (abhängig von verifizierter Domain/API Key).

## Architektur-Kurzüberblick
- API Entry in `backend/server.py`; Business-Logik in Routern/Services.
- Frontend-Routing zentral in `frontend/src/App.js` mit rollenbasierten Protected Routes.
- Source-of-Truths dokumentiert in `docs/architecture/overview.md`.

## Lokale Entwicklung
### Voraussetzungen
- Python 3.11+
- Node.js 20+
- MongoDB erreichbar

### Backend starten
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

### Frontend starten
```bash
cd frontend
npm install
npm start
```

## Environment-Variablen (Auszug)
Pflicht: `MONGO_URL`, `DB_NAME`, `JWT_SECRET`, `ADMIN_PASSWORD`.
Wichtige optionale/umgebungsabhängige Variablen:
- `FRONTEND_URL`, `APP_URL`
- `COOKIE_SECURE`, `COOKIE_SAMESITE`
- `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`
- `RESEND_API_KEY`, `EMAIL_FROM`
- `STORAGE_BACKEND`, `LOCAL_STORAGE_PATH`, `S3_*`

Vollständige Betriebslogik: `docs/operations/release-and-operations.md`.

## Build / Test / Run
```bash
# Backend Syntax-Check
python -m compileall backend

# Backend Tests
cd backend && pytest

# Frontend Build
cd frontend && npm run build

# Frontend Tests
cd frontend && npm test -- --watchAll=false
```

## Ordnerstruktur (vereinfacht)
```text
backend/           FastAPI API, Router, Services, Tests
frontend/          React App mit Public/Portal/Staff/Admin/Partner
memory/            PRD, Blocker, Fehlerregister, Rollen-/Kommunikations-Memory
docs/              verbindliche Projektdokumentation (Architektur, ADR, Workflows ...)
CHANGELOG.md       versionierte Änderungsübersicht
CONTRIBUTING.md    Beitrags- und Dokumentationsregeln
AGENTS.md          verbindliche Agentenrichtlinie
```

## Dokumentationsstruktur
Siehe `docs/README.md` für Navigation und Source-of-Truth-Definition pro Bereich.

## AI-/Screening-Überblick
- Produktiv ausschließlich DeepSeek.
- Trennung von `completeness`, `formal_precheck`, `ai_recommendation`, `staff_decision` ist verpflichtend.
- Keine finale Zulassungsentscheidung durch KI.
- Details: `docs/ai/screening-and-provider.md`.

## Daten-, Rollen- und Sicherheitsprinzipien
- RBAC + Need-to-know.
- Teacher nur consent- und assignment-basiert.
- Bewerber sieht nur eigene Daten.
- Audit-Logging für kritische Aktionen.

## Aktueller Projektstatus (2026-03-30)
- Kernplattform funktionsfähig, aber Go-Live noch blockiert durch externe Themen (Rechtstexte, Mail-Domain, Backup, TLS/Deploy-Härtung).
- DeepSeek-Migration für AI-Screening aktiv; Legacy-nscale nur als Kompatibilitäts-Shim ohne produktive Nutzung.

## Bekannte externe Blocker
- Rechtsprüfung Impressum/Datenschutz/AGB.
- Resend-Domain-Verifizierung.
- Produktions-Backup-Strategie MongoDB.
- Finale TLS/HTTPS-Produktionskonfiguration.

## Beitrag-, Branch- und PR-Regeln
- Keine stillen Änderungen ohne Dokumentation.
- Relevante Architektur-/Workflow-/Provider-/Security-Entscheidungen nur mit ADR.
- Changelog-Pflicht für relevante Änderungen.
- Tests und Grenzen müssen im PR-Nachweis stehen.
- Details: `CONTRIBUTING.md`, `AGENTS.md`, `docs/project/documentation_policy.md`.

## Dokumentationspflicht
Dieses Repository folgt einer verbindlichen Dokumentationspflicht für Menschen und AI-Agenten. Jede relevante Änderung muss begründet, versioniert, testbar und auditierbar dokumentiert sein.

## Weiterführende Dokumente
- Dokumentationsindex: `docs/README.md`
- Projektüberblick: `docs/project/overview.md`
- Architektur: `docs/architecture/overview.md`
- Workflows: `docs/workflows/core-workflows.md`
- Rollen/Rechte: `docs/roles/roles-and-permissions.md`
- AI-Screening: `docs/ai/screening-and-provider.md`
- Operations/Release: `docs/operations/release-and-operations.md`
- QA/Teststrategie: `docs/testing/qa-strategy.md`
- ADR-Verzeichnis: `docs/adr/README.md`
- Historie: `docs/project/history.md`
- Changelog: `CHANGELOG.md`
