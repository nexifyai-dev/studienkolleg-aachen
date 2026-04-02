# W2G Platform Docs

Dieses Verzeichnis ist die kanonische, versionierte Dokumentation des Repositories `studienkolleg-aachen`.

## Ziel

Die Dokumentation soll das System entlang seiner echten Wissensachsen erklären:

- Produkt- und Rollenverständnis
- Frontend- und Backend-Architektur
- Datenmodell und Betriebslogik
- Go-live-, Security- und Operations-Themen
- Regeln zur Pflege der Dokumentation

## Dokumentationsprinzipien

1. **Docs-as-code**: Die Dokumentation lebt im Repository und wird zusammen mit Codeänderungen gepflegt.
2. **Code bleibt die Primärquelle**: Die Docs erklären Zusammenhänge, sie duplizieren nicht jede Implementierungszeile.
3. **Architektur vor Dateilisten**: Seiten sollen mentale Modelle liefern.
4. **Betriebsrelevanz**: Änderungen an Rollen, APIs, Env-Variablen, Datenmodell oder Deploy-Verhalten müssen hier nachvollziehbar sein.
5. **Sichere Inhalte**: Keine echten Secrets, produktiven Zugangsdaten oder sensitiven Betriebswerte dokumentieren.

## Einstieg

### Überblick

- [Product Overview](./00-overview/product-overview.md)
- [Repository Map](./00-overview/repository-map.md)
- [System Architecture](./01-architecture/system-architecture.md)
- [User Roles](./02-product/user-roles.md)

### Backend

- [Backend Domain Map](./03-backend/backend-domain-map.md)
- [Auth and RBAC](./03-backend/auth-and-rbac.md)
- [Applications Domain](./03-backend/applications.md)
- [Documents Domain](./03-backend/documents.md)
- [Leads Domain](./03-backend/leads.md)
- [Tasks Domain](./03-backend/tasks.md)
- [Messaging Domain](./03-backend/messaging.md)
- [Workspaces Domain](./03-backend/workspaces.md)

### Frontend

- [Frontend Routing](./04-frontend/frontend-routing.md)
- [Frontend Auth and Session](./04-frontend/auth-and-session.md)

### Daten und Betrieb

- [Data Model](./05-data/data-model.md)
- [Environment Variables](./06-operations/environment-variables.md)
- [Storage](./06-operations/storage.md)
- [Deployment](./06-operations/deployment.md)
- [Go-live Checklist](./06-operations/go-live-checklist.md)

### Entwicklung und Governance

- [Local Setup](./07-development/local-setup.md)
- [Docs Maintenance](./07-development/docs-maintenance.md)
- [ADR-0001: Docs-as-code](./08-decisions/adr-0001-docs-as-code.md)
- [Contributing](../CONTRIBUTING.md)

## Übergangsstatus von `memory/`

Die Dateien unter `memory/` bleiben vorerst als historische bzw. Übergangsquellen erhalten. Die langfristige Source of Truth ist jedoch `docs/`.

## Weiterer sinnvoller Ausbau

Sinnvolle nächste Ergänzungen:

- tiefere Domänenseiten für Notifications, Partner, Teacher, Followups, Export
- Deployment-/Release-Dokumentation mit realer Zielumgebung
- weitere ADRs für Auth, Storage, Partner- und Workspace-Strategie
- ggf. später ein gerendertes Doku-Frontend auf Basis derselben Markdown-Struktur
