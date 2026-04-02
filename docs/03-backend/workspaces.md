# Workspaces Domain

## Zweck

Die Workspaces-Domäne modelliert die fachlichen Bereiche bzw. Produktsegmente der Plattform. Sie ist die wichtigste Segmentierungsachse oberhalb einzelner Applications.

## Produktbedeutung

Workspaces definieren, in welchem fachlichen Kontext ein Fall bearbeitet wird.

Sie beeinflussen unter anderem:
- Bereich / Angebot
- verfügbare Pipeline-Stages
- verfügbare Kurse
- spätere Segmentierung von Daten und Prozessen

## Aktueller Systemcharakter

Das System ist bereits auf mehrere Bereiche vorbereitet, nicht nur auf das Studienkolleg. Seed-seitig existieren u. a. Bereiche für:

- Studienkolleg
- Sprachkurse
- Pflege
- Arbeit & Ausbildung

Dabei sind nicht alle Bereiche gleich aktiv, aber die Plattformstruktur ist bereits multibereichsfähig angelegt.

## Hauptfunktionen

### Workspaces auflisten
Authentifizierte Nutzer können Workspaces abrufen.

### Workspace anlegen
Das Anlegen ist Admin-Rollen vorbehalten.

Beim Erstellen werden u. a. gesetzt:
- `name`
- `area`
- `description`
- `slug`
- `active = true`
- ein Standardset an Pipeline-Stages
- `created_by`
- `created_at`

## Workspace-Felder auf hoher Ebene

Typischerweise enthalten Workspaces:

- `slug`
- `name`
- `area`
- `description`
- `active`
- `pipeline_stages`
- ggf. `available_courses`
- Erstellungsmetadaten

## Beziehung zu anderen Domänen

### Workspaces ↔ Applications
Applications gehören fachlich in einen Workspace. Dadurch wird festgelegt, in welchem Angebots- und Prozesskontext der Fall bearbeitet wird.

### Workspaces ↔ Leads
Der Lead-Ingest versucht, einen Workspace aus `area_interest` aufzulösen. Damit beginnt die fachliche Einordnung bereits im öffentlichen Eingang.

### Workspaces ↔ Staff-Oberflächen
Filter, Kanban und operative Übersichten können Workspaces als Segmentierungsachse nutzen.

## Zwei Quellen der Workspace-Realität

Derzeit kommen Workspaces aus zwei Richtungen:

1. **Seed-Logik** mit produktnahen vordefinierten Bereichen
2. **Admin-Create-Flow** mit einem generischeren Standard-Stage-Set

Das ist funktional sinnvoll, kann aber mittelfristig zu Drift führen, wenn Seed-Definitionen und manuell angelegte Workspaces unterschiedliche Prozessmodelle bekommen.

## Architekturbeobachtung

Workspaces sind fachlich eine Kernachse, aber aktuell noch vergleichsweise leichtgewichtig im Router. Der eigentliche semantische Wert steckt weniger im CRUD selbst als in ihrer Wirkung auf Leads, Applications und Prozesslogik.

## Typische Änderungsfolgen

Änderungen an Workspaces wirken sich häufig aus auf:

- Lead-Zuordnung
- Application-Erstellung
- Pipeline-Logik
- Kanban und Dashboard-Sichten
- Admin-Konfiguration
- Reporting / Segmentierung

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- neue Workspace-Bereiche eingeführt werden
- `area`-Mapping geändert wird
- Pipeline-Stages je Workspace geändert werden
- `available_courses`-Logik geändert wird
- Workspace-Sichtbarkeit oder Admin-Create-Regeln geändert werden
