# Contributing

Danke für Beiträge an diesem Repository.

Diese Plattform ist funktional und architektonisch bereits breit aufgestellt. Deshalb sind Änderungen dann am wertvollsten, wenn sie nicht nur Code, sondern auch Rollen-, Daten-, Architektur- und Betriebsfolgen sauber mitdenken.

## Grundprinzipien

1. **Code und Docs gehören zusammen**
   Änderungen an Architektur, Rollen, Datenmodell, Env, Routing oder Betrieb müssen die Dokumentation in `docs/` mitprüfen.

2. **Sichere Entwicklung vor bequemer Entwicklung**
   Keine Secrets, produktiven Zugangsdaten oder sensiblen Betriebswerte committen.

3. **Kleine, nachvollziehbare Änderungen bevorzugen**
   Große, unstrukturierte Sammeländerungen erschweren Review, Doku und Betrieb.

4. **Systemische Folgen prüfen**
   Viele Änderungen betreffen mehr als eine Datei. Bitte Auswirkungen auf Frontend, Backend, Rollen, Workspaces, Storage und Ops mitdenken.

## Vor dem Start

Bitte vor strukturellen Änderungen mindestens diese Seiten lesen:

- `README.md`
- `docs/README.md`
- `docs/01-architecture/system-architecture.md`
- `docs/03-backend/auth-and-rbac.md`
- `docs/07-development/docs-maintenance.md`

## Lokale Entwicklung

Siehe:

- `docs/07-development/local-setup.md`
- `docs/06-operations/environment-variables.md`
- `docs/06-operations/storage.md`

## Was bei Änderungen mitgeprüft werden sollte

### Produkt und Rollen
- neue Rolle?
- geänderte Sichtbarkeit?
- neue Produktfläche?
- Redirect-/Routing-Änderung?

### Backend und API
- neuer Router?
- neue Kernlogik?
- geänderte Request-/Response-Struktur?
- neue oder geänderte Automationspfade?

### Datenmodell
- neue Collection?
- neuer Index?
- geänderte Beziehungen zwischen Kernobjekten?
- Seed-/Workspace-Auswirkungen?

### Betrieb
- neue Env-Variable?
- Cookie-/HTTPS-/Origin-Folgen?
- Storage-/E-Mail-/Backup-Auswirkungen?
- Go-live-Folgen?

## Dokumentationspflicht

Die Dokumentation in `docs/` sollte aktualisiert werden, wenn eine Änderung mindestens eines der folgenden Themen berührt:

- Architektur
- Rollen / RBAC
- Routing / Session
- Datenmodell
- Workspaces / Pipeline-Stages
- Env / Deploy / Security
- Go-live-relevante Prozesse

## Pull Requests

Bitte nutze das PR-Template und beantworte die Fragen ehrlich. Besonders wichtig sind:

- welche Domäne betroffen ist
- ob Docs aktualisiert wurden
- ob Env-/Ops-Auswirkungen existieren
- ob Rollen-/Sichtbarkeitsänderungen enthalten sind

## Nicht committen

- echte `.env`-Dateien mit Secrets
- produktive Zugangsdaten
- API Keys
- Klartext-Passwörter
- sensible Kunden- oder Bewerberdaten

## Bevorzugter Doku-Ausbau

Wenn du bei einer Änderung merkst, dass Systemwissen fehlt, erweitere bevorzugt:

- `docs/03-backend/`
- `docs/04-frontend/`
- `docs/06-operations/`
- `docs/08-decisions/`

## Architekturentscheidungen

Dauerhafte, wichtige Richtungsentscheidungen bitte zusätzlich als ADR unter `docs/08-decisions/` dokumentieren.
