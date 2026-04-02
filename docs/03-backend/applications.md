# Applications Domain

## Zweck

Applications sind das operative Kernobjekt der Plattform. Sie verbinden Bewerber, Workspaces, Prozessstatus und angeschlossene Arbeitsobjekte wie Dokumente, Aufgaben, Nachrichten, Notizen und Follow-ups.

## Warum diese Domäne zentral ist

Fast jede relevante Bearbeitung im System hängt direkt oder indirekt an einer Application:

- Lead wird in einen bearbeitbaren Fall überführt
- Staff bearbeitet Status, Notizen und Kommunikation
- Documents hängen an der Application
- Tasks und Follow-ups hängen an der Application
- Audit und Activity History werden am Fall sichtbar

## Hauptverantwortung des Routers

Der Applications-Router deckt derzeit mehrere Aufgabenklassen ab:

- Listen und Filtern von Applications
- Erstellen neuer Applications
- Detailansicht einzelner Applications
- Status-/Stage-Änderungen
- Pflegen operativer Fallattribute
- Case Notes
- Activity History
- Profiländerungen des Bewerbers aus dem Fallkontext
- Ad-hoc-E-Mail aus dem Fallkontext

## Zugriff nach Rolle

### Applicant
- sieht nur eigene Applications
- darf keine fremden Fälle lesen oder bearbeiten

### Partnerrollen
- werden über `organization_id` gescopet
- sehen nur Applications ihrer Organisation

### Staff-Rollen
- können Applications breit einsehen
- können optional nach `workspace_id` und `stage` filtern
- dürfen Applications aktualisieren

## Listenlogik

Die Listenlogik variiert bewusst nach Rolle:

- Applicant: Filter auf eigene `applicant_id`
- Partner: Filter auf `organization_id`
- Staff: optional nach `workspace_id`, sonst breite Sicht für Dashboard/Kanban

Für Staff wird die Antwort zusätzlich angereichert:
- Applicant-Basisdaten
- Workspace-Name

## Erzeugung einer Application

Beim Erstellen gilt:

- Nicht-Staff-Nutzer können keine beliebige `applicant_id` setzen.
- Der Workspace muss existieren.
- Neue Applications starten mit `current_stage = lead_new`.
- Es werden Metadaten wie `created_at`, `last_activity_at`, `created_by` gesetzt.
- Die Erstellung wird audit-geloggt.

## Update-Logik

Updates sind Staff-Rollen vorbehalten.

Typische änderbare Felder:
- `current_stage`
- `assigned_staff_id`
- `priority`
- `notes`
- fachliche Fallattribute wie Kurs-/Start-/Sprach- und Herkunftsdaten

### Besondere Bedeutung von Stage-Änderungen
Stage-Wechsel sind kein normaler Feldwechsel, sondern ein prozesskritisches Ereignis.

Deshalb passieren zusätzlich:
- Audit Log
- Eintrag in `application_activities`
- Versuch einer Automationskette für Statusänderungen
- Aktualisierung von `last_activity_at`

## Case Notes

Applications unterstützen interne bzw. geteilte Fallnotizen.

Wesentliche Eigenschaften:
- Autor, Rolle und Zeitstempel werden gespeichert
- Visibility kann intern oder geteilt sein
- Applicants sehen nur `shared` Notes
- Notizerstellung erzeugt Aktivitäts- und Audit-Spuren

## Activity History

Die Activity-Historie aggregiert mehrere Quellen:

- `application_activities`
- `audit_logs`
- `email_events`

Damit entsteht ein vereinheitlichter Verlauf pro Fall. Diese Historie ist operativ wertvoll, weil sie Statuswechsel, Notizen, Audit-Ereignisse und aus dem Fall versendete E-Mails zusammenführt.

## Profilpflege aus dem Fallkontext

Staff kann bestimmte Bewerber-Profildaten direkt aus der Application heraus aktualisieren.

Aktuell relevante Felder:
- `full_name`
- `phone`
- `country`
- `date_of_birth`
- `email`

Auch diese Änderungen erzeugen Aktivitäts- und Audit-Spuren.

## Ad-hoc-E-Mail aus dem Fallkontext

Der Router erlaubt den Versand von Einzelfall-E-Mails an den Bewerber.

Dabei passieren typischerweise:
- Empfängerermittlung aus Applicant-Kontext
- Versand über Email-Service
- Protokollierung in `email_events`
- Aktivitätseintrag
- Audit Log

## Gekoppelte Systeme

Die Applications-Domäne hängt eng an:

- Users
- Workspaces
- Documents
- Tasks
- Messaging
- Followups
- Audit
- Email
- Automation

## Typische Änderungsfolgen

Änderungen an Applications haben oft Auswirkungen auf:

- Staff UI / Applicant Detail
- Kanban / Dashboard
- Notifications und Automationen
- Auditierbarkeit
- Reporting / Export
- Workspace- und Rollenlogik

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- Stages oder Workflow-Logik geändert werden
- neue Application-Felder hinzukommen
- Ownership-/Partner-/Staff-Sichtbarkeiten geändert werden
- Activity- oder Audit-Modell angepasst wird
- Fallnahe Kommunikation oder Automationen geändert werden
