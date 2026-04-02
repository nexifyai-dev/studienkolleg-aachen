# Repository Map

## Überblick

Das Repository bildet die W2G Platform / Studienkolleg Aachen als mehrflächige Plattform ab.

Es besteht aus drei zentralen Wissensblöcken:

1. **Frontend** – Benutzeroberflächen für Public, Applicant, Staff, Admin und Partner
2. **Backend** – FastAPI-Anwendung mit domänenspezifischen Routern und Services
3. **Projektwissen** – aktuell in `memory/` dokumentierte Produkt- und Go-live-Informationen

## Hauptverzeichnisstruktur

```text
.
├── backend/
├── frontend/
├── memory/
└── docs/
```

## Bedeutung der Hauptbereiche

### `backend/`
Technische Kernlogik der Plattform.

Wichtige Unterbereiche:

- `server.py` – App Factory, Router-Registrierung, Startup/Shutdown
- `config.py` – zentrale Umgebungs- und Feature-Konfiguration
- `database.py` – MongoDB-Verbindung und Index-Setup
- `deps.py` – Auth- und Rollenabhängigkeiten für FastAPI
- `seed.py` – idempotente Seeds für Workspaces, Admin und Dev-Accounts
- `models/` – Pydantic-Schemas
- `routers/` – Domänenmodule wie Auth, Applications, Documents, Tasks usw.
- `services/` – Querschnittslogik wie Storage, E-Mail, Audit, KI-Anbindung

### `frontend/`
React-Anwendung mit mehreren Benutzerflächen.

Wichtige Unterbereiche:

- `src/App.js` – gesamtes Routing und Rollenzuordnung
- `src/contexts/` – Auth- und Session-Logik
- `src/lib/` – API-Client und technische Hilfsmodule
- `src/components/` – Layouts, Shared UI, abstrahierte Komponenten
- `src/pages/` – Seiten nach Produktflächen getrennt
- `src/locales/` – Internationalisierung DE/EN

### `memory/`
Temporäre bzw. vorläufige Wissensquellen im Repo.

Aktuell wichtig:

- `PRD.md` – Produktzustand, Featureübersicht, Architekturzuschnitt
- `GO_LIVE_BLOCKERS.md` – produktionsrelevante Lücken, Betriebs- und Rechtsthemen

Diese Inhalte werden schrittweise in `docs/` überführt.

### `docs/`
Versionierte Projektdokumentation und künftige Source of Truth für erklärende Systemdokumentation.

## Systemische Gliederung statt rein technischer Gliederung

Für die tägliche Arbeit ist das Repo nicht nur nach Pfaden zu lesen, sondern nach diesen Achsen:

- **Rollen und Produktflächen**
- **Domänenobjekte** wie Leads, Applications, Documents, Tasks, Messages, Consents
- **Querschnittsthemen** wie Auth, RBAC, Storage, E-Mail, Audit, AI-Screening
- **Betrieb und Go-live** wie Env, Cookies, HTTPS, Backup und Rechtstexte

## Empfohlene Lese-Reihenfolge

1. `docs/01-architecture/system-architecture.md`
2. `docs/02-product/user-roles.md`
3. `docs/03-backend/backend-domain-map.md`
4. `docs/04-frontend/frontend-routing.md`
5. `docs/05-data/data-model.md`
6. `docs/06-operations/go-live-checklist.md`

## Änderungsrelevanz

Bei Änderungen in folgenden Bereichen sollte die Dokumentation mitgeprüft werden:

- neue oder entfernte Router
- neue Benutzerrollen oder Rollenrechte
- neue Env-Variablen / Feature Flags
- Änderungen am Datenmodell oder an Collections/Indizes
- Änderungen an Routing, Session-Logik oder Auth-Verhalten
- Änderungen mit Go-live- oder Compliance-Relevanz
