# Docs Maintenance

## Zweck

Diese Seite definiert, wie die Projektdokumentation künftig gepflegt werden soll, damit sie nicht vom Code wegdriftet.

## Grundsatz

Dokumentation ist Teil des Systems. Änderungen mit Architektur-, Rollen-, Datenmodell-, API- oder Betriebsfolgen gelten erst dann als vollständig, wenn die betroffenen Docs geprüft wurden.

## Wann Docs aktualisiert werden müssen

Mindestens bei folgenden Änderungen:

### Produkt und Rollen
- neue Rolle
- geänderte Rollenrechte
- neue Produktfläche
- neue User Journey
- veränderte Redirect- oder Routinglogik

### Backend und API
- neuer Router
- geänderte Request-/Response-Struktur
- neues Kernobjekt
- Änderung an Workspace- oder Pipeline-Logik
- Änderung an Auth-/RBAC-Verhalten

### Datenmodell
- neue Collection
- neuer oder entfernter Index
- geänderte Beziehungen zwischen Kernobjekten
- geänderte Seed-Logik

### Betrieb / Security
- neue Env-Variable
- neues externes System
- Änderung an Cookie-, Session- oder Secret-Handling
- Änderung an Storage, E-Mail, Backup oder Deploy
- neue Go-live- oder Compliance-Auswirkungen

## Minimalprozess für Pull Requests

Für relevante Änderungen sollte jede PR mindestens diese Fragen beantworten:

1. Welche Domäne ist betroffen?
2. Welche Nutzerrollen sind betroffen?
3. Ändert sich das Datenmodell?
4. Ändern sich Env-Variablen oder Betriebsannahmen?
5. Welche Docs-Seiten müssen mitgezogen werden?

## Empfohlene PR-Checkliste

```md
- [ ] Rollen / Sichtbarkeit geprüft
- [ ] API-/Schema-Auswirkungen geprüft
- [ ] Env-/Config-Auswirkungen geprüft
- [ ] Docs aktualisiert oder bewusst als nicht notwendig markiert
- [ ] Go-live-/Ops-Auswirkungen geprüft
```

## Ownership-Prinzip

Die Person, die eine strukturelle Änderung einführt, ist verantwortlich für die erste Doku-Aktualisierung. Dokumentation darf nicht an einen undefinierten späteren Schritt delegiert werden.

## Seitenarten im Docs-System

### Überblicksseiten
Erklären das System auf hoher Ebene.

### Domänenseiten
Erklären Fachlogik und technische Zuschnitte pro Bereich.

### Operations-Seiten
Erklären Betrieb, Deploy, Security und Go-live.

### Entscheidungsseiten
Sollten künftig als ADRs gepflegt werden, wenn dauerhafte Architekturentscheidungen getroffen werden.

## Qualitätskriterien guter Docs

Gute Seiten sind:

- aktuell
- knapp, aber nicht leer
- systemisch statt dateilastig
- für Onboarding und Änderungsplanung nutzbar
- frei von Secrets und produktiven Zugangsdaten

## Dinge, die vermieden werden sollen

- vollständige Codekopien
- unkommentierte API-Dumps
- versteckte TODO-Sammlungen ohne Verantwortlichkeit
- veraltete Architekturbehauptungen
- Zugangsdaten oder interne Sicherheitsdetails im Klartext

## Nächste empfohlene Ergänzungen

Sobald das Grundgerüst steht, sollten bevorzugt folgende Detailseiten ergänzt werden:

- `03-backend/auth-and-rbac.md`
- `03-backend/applications.md`
- `03-backend/documents.md`
- `04-frontend/auth-and-session.md`
- `06-operations/environment-variables.md`
- `06-operations/storage.md`
- `08-decisions/adr-0001-docs-as-code.md`
