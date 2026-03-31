# Studienkolleg Aachen Platform — Produktionsdokumentation

Diese Einstiegsdokumentation ist die **Single Source of Truth** für Systemüberblick, Rollen, Betriebsgrenzen und Release-Reifegrad.

## 1) Systemüberblick

Die Plattform deckt den vollständigen CRM- und Bewerbungsprozess für Studienkolleg-Interessierte ab:

- **Public Portal**: Information, Kursübersicht, Kontakt, Bewerbungseintritt.
- **Applicant Portal**: Status, Dokumente, Nachrichten, Journey und Einstellungen.
- **Staff Portal**: Fallbearbeitung, Kanban, Messaging, Aufgaben und operative Entscheidungen.
- **Admin Portal**: Governance, Nutzerverwaltung, Audit und Systemaufsicht.
- **Partner Portal**: Referral-Flows und Partner-spezifische Verwaltung.

Weitere Architekturdetails: [docs/architecture/overview.md](docs/architecture/overview.md)

## 2) Architekturdiagramme

Architekturdiagramme und Datenflussdarstellung sind zentral in der Architektur-Doku gepflegt:

- [Systemkontext & Container-Sicht](docs/architecture/overview.md#systemkontext-und-containersicht)
- [Rollen- und Berechtigungsfluss](docs/architecture/overview.md#rollen--rechtefluss)
- [AI-Screening-Entscheidungspfad](docs/architecture/overview.md#ai-screening-entscheidungsfluss)

## 3) Rollen, Portale und Berechtigungen

Verbindliche Rollen- und Rechtebasis:

- [Rollen- und Berechtigungsmatrix](docs/roles-and-permissions.md)
- Rollen-Workflows:
  - [Applicant](docs/workflows/applicant.md)
  - [Staff](docs/workflows/staff.md)
  - [Admin](docs/workflows/admin.md)
  - [Partner](docs/workflows/partner.md)
  - [Teacher](docs/workflows/teacher.md)

## 4) Lokale Entwicklung

### Voraussetzungen

- Python 3.11+
- Node.js 20+
- npm 10+

### Backend starten

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

### Frontend starten

```bash
cd frontend
npm ci
npm start
```

### Relevante Prüfungen

```bash
cd backend && pytest -q
cd frontend && npm test -- --watch=false
```

Release-Gates und Teststrategie: [docs/qa-release/gates.md](docs/qa-release/gates.md)

## 5) Betriebsgrenzen (Operational Boundaries)

- **AI-Screening ist assistiv, nicht final entscheidend.**
- Aus Uploads oder vorhandenen Dateien darf **keine faktische Annahme** automatisch als Entscheidung gelten.
- Entscheidungsebenen sind strikt getrennt:
  1. Vollständigkeit
  2. Formale Vorprüfung
  3. KI-Empfehlung
  4. Staff-Entscheidung
- Rollen- und Portalgrenzen dürfen nicht regressieren.
- Änderungen an Architektur/Flows benötigen Doku-Update in derselben PR.

Details: [docs/ai-screening/decision-boundaries.md](docs/ai-screening/decision-boundaries.md), [docs/governance/pr-policy.md](docs/governance/pr-policy.md)

## 6) Release-Status

Aktueller Release-Rahmen und Artefakte:

- [QA & Release Gates](docs/qa-release/gates.md)
- [Rollback-Strategie](docs/qa-release/rollback.md)
- [Release-Artefakt: Go-Live Checklist](release/golive_checklist.yaml)
- [Changelog](CHANGELOG.md)
- [Projekthistorie](docs/history/project-history.md)

## 7) Dokumentations-Navigation (bidirektional)

- Architektur ↔ Rollen/Flows ↔ AI-Screening ↔ QA/Release ↔ Governance sind gegenseitig verlinkt.
- ADR-Entscheidungen sind zentral indiziert unter [docs/adr/README.md](docs/adr/README.md).
- Historische Änderungen sind in [CHANGELOG.md](CHANGELOG.md) und [docs/history/project-history.md](docs/history/project-history.md) zu pflegen.

## Dokumentverantwortung

- **Owner:** Platform Architecture + Engineering Lead
- **Update-Prozess:** Bei jeder PR mit Architektur-, Rollen-, Flow-, QA- oder Governance-Auswirkung muss README gegengeprüft und bei Bedarf aktualisiert werden.
