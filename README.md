# W2G Platform – Studienkolleg Aachen / Way2Germany / W2G Academy

Zentrale Plattform fuer die Verwaltung von Studienkolleg-Bewerbungen, Dokumenten, Kommunikation, Rechnungen und KI-gestuetztem Screening.

## Tech Stack

| Schicht | Technologie |
|---------|-------------|
| Frontend | React 18 + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python) |
| Datenbank | MongoDB 7.x |
| Auth | JWT (Cookie-basiert, httpOnly) |
| AI/KI | nscale API (deepseek-chat / deepseek-reasoner) |
| PDF | ReportLab (serverseitig) |
| E-Mail | IMAP/SMTP (Strato) + Resend (transaktional, vorbereitet) |
| i18n | react-i18next (DE/EN) |

Zur Begruendung der Architekturabweichung vom Gesamtkonzept (Supabase/Next.js) siehe [ADR-001](docs/adr/ADR-001-mongodb-fastapi-statt-supabase-nextjs.md).

## Portale

| Portal | Rollen | URL-Prefix |
|--------|--------|------------|
| Public | Alle | `/` |
| Applicant | applicant | `/portal` |
| Staff | staff, accounting_staff | `/staff` |
| Teacher | teacher | `/staff` |
| Admin | superadmin, admin | `/admin` |
| Partner | affiliate, agency_admin, agency_agent | `/partner` |

## Projektstruktur

```
/app/
├── backend/
│   ├── config.py          # Zentrale Konfiguration (ENV-Variablen)
│   ├── server.py          # FastAPI App-Factory
│   ├── database.py        # MongoDB-Verbindung
│   ├── seed.py            # Idempotenter Admin-/Workspace-Seed
│   ├── routers/           # API-Endpunkte nach Domaene
│   ├── services/          # Business-Logik (Audit, Email, Storage, AI)
│   └── models/            # Pydantic-Schemas
├── frontend/
│   ├── src/
│   │   ├── pages/         # Seitenkomponenten nach Portal
│   │   ├── components/    # UI-Komponenten (layout, shared, ui)
│   │   ├── contexts/      # React Context (Auth)
│   │   └── locales/       # Uebersetzungen (DE/EN)
├── docs/
│   ├── adr/               # Architecture Decision Records
│   ├── governance/        # Projekt- und Memory-Regeln
│   ├── qa-release/        # Deployment, Runbook
│   ├── history/           # Chronologische Aenderungshistorie
│   └── wiki/              # Wiki-taugliche Kurzfassungen
├── memory/
│   ├── PRD.md             # Produktanforderungen und Backlog
│   ├── CHANGELOG.md       # Feature-Chronologie
│   ├── FEHLERREGISTER.md  # Bekannte Fehler und Muster
│   ├── GO_LIVE_BLOCKERS.md# Produktionsblocker
│   └── ROLES_MATRIX.md   # Rollenmodell
└── scripts/               # Hilfsskripte (pre-commit, secret-scan)
```

## Dokumentation

| Dokument | Pfad | Inhalt |
|----------|------|--------|
| Governance-Policy | `docs/governance/agent_memory_and_writeback_policy.md` | Memory-Regeln, Recall/Writeback, Definition of Done |
| ADR-001 | `docs/adr/ADR-001-mongodb-fastapi-statt-supabase-nextjs.md` | Architekturabweichung |
| Deployment | `docs/qa-release/DEPLOYMENT.md` | ENV-Gruppen, Start-Reihenfolge, Health-Checks |
| Runbook | `docs/qa-release/RUNBOOK.md` | Incident-Triage, Fehlerbilder, Eskalation |
| Gesamtkonzept | `/app/01-20_*.md` | Extrahierte Kapitel aus Gesamtkonzept_2026 |

## Schnellstart (Entwicklung)

```bash
# Services starten (Emergent-Umgebung)
sudo supervisorctl start mongodb backend frontend

# Health-Check
curl http://localhost:8001/api/health

# API-Docs
# Browser: http://localhost:8001/api/docs
```

Fuer Deployment-Details siehe [DEPLOYMENT.md](docs/qa-release/DEPLOYMENT.md).  
Fuer Incident-Handling siehe [RUNBOOK.md](docs/qa-release/RUNBOOK.md).

## Sicherheitshinweise

- Keine Secrets in Code oder Git-History (siehe [GO_LIVE_BLOCKERS.md](memory/GO_LIVE_BLOCKERS.md))
- `.env`-Dateien sind in `.gitignore` und werden nicht committed
- Pre-Commit-Hook fuer Secret-Scanning: `scripts/pre-commit`
