# W2G Platform / Studienkolleg Aachen

Versionierte Produkt-, Architektur- und Betriebsbasis für die mehrflächige Applicant-Management-Plattform von Studienkolleg Aachen / Way2Germany.

## Was dieses Repository enthält

Dieses Repository bildet die Plattform als zusammenhängendes System ab:

- **Frontend** in React für Public, Applicant, Staff, Admin und Partner
- **Backend** in FastAPI mit domänenspezifischen Routern und Services
- **MongoDB-basiertes Datenmodell** für Leads, Applications, Documents, Tasks, Messaging und mehr
- **Versionierte Dokumentation** unter `docs/` als primäre Wissensbasis

## Systemcharakter

Die Plattform ist keine einzelne Website, sondern ein kombiniertes Produkt aus:

- öffentlicher Website mit Bewerbungseinstieg
- Bewerberportal
- interner Staff-Oberfläche
- Admin-Oberfläche
- Partner-/Affiliate-Oberfläche
- Betriebs- und Go-live-Logik

## Repository-Struktur

```text
.
├── backend/
├── frontend/
├── memory/
└── docs/
```

### Kurz erklärt

- `backend/` – FastAPI, Router, Services, Konfiguration, Seeds, Datenbankzugriff
- `frontend/` – React-App mit Routing, Layouts, AuthContext und Produktseiten
- `memory/` – ältere Wissensartefakte, die schrittweise in `docs/` überführt werden
- `docs/` – kanonische Dokumentation für Architektur, Rollen, Datenmodell, Operations und Entwicklung

## Einstieg für neue Entwickler

### 1. System verstehen

- [Docs Startseite](docs/README.md)
- [Product Overview](docs/00-overview/product-overview.md)
- [Repository Map](docs/00-overview/repository-map.md)
- [System Architecture](docs/01-architecture/system-architecture.md)
- [User Roles](docs/02-product/user-roles.md)

### 2. Lokal starten

- [Local Setup](docs/07-development/local-setup.md)
- [Environment Variables](docs/06-operations/environment-variables.md)
- [Storage](docs/06-operations/storage.md)

### 3. Operative / produktionsnahe Themen

- [Go-live Checklist](docs/06-operations/go-live-checklist.md)
- [Auth and RBAC](docs/03-backend/auth-and-rbac.md)
- [Applications Domain](docs/03-backend/applications.md)
- [Documents Domain](docs/03-backend/documents.md)

## Lokaler Schnellstart

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

Mindestens erforderliche Variablen:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=w2g_platform
JWT_SECRET=<mindestens 32 Zeichen>
ADMIN_PASSWORD=<sicheres lokales Passwort>
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Weitere Details: [Local Setup](docs/07-development/local-setup.md)

## Dokumentationsmodell

Die primäre Dokumentation liegt im Repository unter `docs/`.

Das bedeutet:

- Doku ist versioniert
- Doku wird mit Code zusammen gepflegt
- Architektur- und Betriebswissen driftet weniger leicht auseinander
- `memory/` ist nur noch Übergangsbestand und nicht mehr die langfristige Source of Truth

Siehe auch: [ADR-0001: Docs-as-code](docs/08-decisions/adr-0001-docs-as-code.md)

## Wichtige Hinweise

- Keine Secrets oder produktiven Zugangsdaten ins Repository schreiben
- Änderungen an Rollen, Env, Routing, Datenmodell oder Betriebslogik sollten die Docs mitziehen
- `memory/PRD.md` und `memory/GO_LIVE_BLOCKERS.md` bleiben vorerst erhalten, werden aber durch `docs/` abgelöst

## Nächste sinnvolle Doku-Ausbaustufen

- Leads, Tasks, Messaging und Workspaces als weitere Domänenseiten
- Deployment-Dokumentation
- ADRs für Auth-/Storage-/Partnermodell
- PR-Checklisten für Doku-Pflege
