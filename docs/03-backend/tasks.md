# Tasks Domain

## Zweck

Die Tasks-Domäne bildet das operative Aufgabenmanagement der Plattform ab. Sie unterstützt sowohl fallbezogene Arbeit im Staff-Bereich als auch ergänzende interne Zusammenarbeit über Notizen, Anhänge und Verlaufsdaten.

## Produktrolle

Tasks sind ein sekundäres, aber stark operatives Arbeitsobjekt.

Sie dienen dazu:
- konkrete Arbeitsschritte festzuhalten
- Verantwortlichkeiten zuzuweisen
- Fristen und Prioritäten zu steuern
- Zusammenhang zu Applications abzubilden
- Bearbeitungsverlauf nachvollziehbar zu machen

## Zugriff nach Rolle

### Applicant
Applicants sehen nur öffentliche, an ihre eigenen Applications gebundene Tasks.

### Staff
Staff sieht standardmäßig eigene zugewiesene Tasks.

### Admin
Admin kann alle Tasks einsehen.

### Staff / Creator / Assignee
Bei Updates gilt für Nicht-Admins eine zusätzliche Zugriffskontrolle: Bearbeiten darf im Wesentlichen nur der Ersteller oder die zugewiesene Person.

## Hauptfunktionen

### Task-Liste
Die Listenlogik ist rollenabhängig:
- Applicant: öffentliche Tasks der eigenen Applications
- Admin: globale Sicht
- sonstige Staff-Rollen: standardmäßig eigene Zuweisungen
- optional Filter über `application_id`

### Task-Erstellung
Neue Tasks werden typischerweise von Staff angelegt.

Wichtige Eigenschaften:
- Standardstatus `open`
- Zuweisung an aktuellen Nutzer, falls nichts anderes gesetzt ist
- History-Eintrag `created`

### Task-Detail
Die Detailansicht wird um Namen für `assigned_to` und `created_by` angereichert.

### Task-Update
Updatebare Themen sind u. a.:
- Status
- Titel / Beschreibung
- Zuweisung
- Fälligkeit
- Priorität

Wichtige Nebeneffekte:
- `updated_at` / `updated_by`
- History-Einträge für Status-, Zuweisungs- und Prioritätsänderungen

### Task-Delete
Löschen ist Staff-Rollen vorbehalten.

### Task Notes
Tasks besitzen eigene Notizen mit Autor und Zeitstempel.

Die Notizerstellung erzeugt zusätzlich einen History-Eintrag.

### Task Attachments
Tasks unterstützen Anhänge.

Aktueller technischer Charakter:
- Upload über Base64 im Request
- Speicherung direkt in `task_attachments`
- Begrenzung auf 10 MB
- Download über separaten Endpunkt

### Task History
Tasks besitzen eine eigene Verlaufscollection.

Typische Ereignisse:
- created
- status_changed
- reassigned
- priority_changed
- note_added
- attachment_added

## Datenmodell auf hoher Ebene

Ein Task enthält typischerweise:

- `title`
- `description`
- `application_id`
- `assigned_to`
- `due_date`
- `priority`
- `visibility`
- `status`
- `created_by`
- `created_at`
- optionale Update-Metadaten

Angeschlossene Nebenobjekte:
- `task_notes`
- `task_attachments`
- `task_history`

## Besondere Architekturbeobachtung

Im Gegensatz zur Documents-Domäne nutzen Task-Anhänge derzeit keinen separaten Storage-Service, sondern werden als Base64-Daten in der Datenbank gehalten. Das ist funktional einfach, aber architektonisch ein anderer Pfad als bei bewerbungsbezogenen Dokumenten.

## Gekoppelte Systeme

Die Tasks-Domäne hängt eng zusammen mit:

- Applications
- Users
- Staff UI
- Audit-/History-nahem Arbeitskontext

## Typische Änderungsfolgen

Änderungen an Tasks wirken sich häufig aus auf:

- Staff Tasks UI
- Applicant-Sichtbarkeit öffentlicher Tasks
- Workflows im Applicant Detail
- Datenbankgröße bei Attachment-Nutzung
- History-/Nachvollziehbarkeitslogik

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- Sichtbarkeitsregeln geändert werden
- Statusmodell geändert wird
- Attachment-Strategie geändert wird
- Applicant-Zugriff auf Tasks geändert wird
- History- oder Ownership-Verhalten geändert wird
