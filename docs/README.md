# W2G Platform Docs

Dieses Verzeichnis ist die versionierte, technische Dokumentation des Repositories `studienkolleg-aachen`.

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
3. **Architektur vor Dateilisten**: Seiten sollen mentale Modelle liefern, nicht nur Pfade aufzählen.
4. **Betriebsrelevanz**: Änderungen an Rollen, APIs, Env-Variablen, Datenmodell oder Deploy-Verhalten müssen hier nachvollziehbar sein.
5. **Sichere Inhalte**: Keine echten Secrets, produktiven Zugangsdaten oder sensitiven Betriebswerte dokumentieren.

## Einstieg

- [Repository Map](./00-overview/repository-map.md)
- [System Architecture](./01-architecture/system-architecture.md)
- [User Roles](./02-product/user-roles.md)
- [Backend Domain Map](./03-backend/backend-domain-map.md)
- [Frontend Routing](./04-frontend/frontend-routing.md)
- [Data Model](./05-data/data-model.md)
- [Go-live Checklist](./06-operations/go-live-checklist.md)
- [Docs Maintenance](./07-development/docs-maintenance.md)

## Informationsquellen im aktuellen Repo

Die erste Version dieser Dokumentation basiert insbesondere auf:

- `memory/PRD.md`
- `memory/GO_LIVE_BLOCKERS.md`
- `backend/server.py`
- `backend/config.py`
- `backend/database.py`
- `backend/seed.py`
- `backend/models/schemas.py`
- `frontend/src/App.js`
- `frontend/src/contexts/AuthContext.js`
- `frontend/src/lib/apiClient.js`

## Nächste Ausbaustufen

Die Struktur ist bewusst so angelegt, dass im nächsten Schritt weitere Detailseiten ergänzt werden können, z. B.:

- `03-backend/auth-and-rbac.md`
- `03-backend/applications.md`
- `03-backend/documents.md`
- `03-backend/messaging.md`
- `06-operations/environment-variables.md`
- `06-operations/storage.md`
- `08-decisions/adr-*.md`
