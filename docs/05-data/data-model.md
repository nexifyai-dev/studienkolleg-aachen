# Data Model

## Zweck

Diese Seite beschreibt das fachliche Datenmodell auf Überblicksebene. Sie ersetzt keine vollständige Schema-Dokumentation, gibt aber ein mentales Modell für die zentralen Objekte und ihre Beziehungen.

## Zentrale Datenobjekte

### Users
Benutzerkonten für interne und externe Rollen.

Typische Attribute:
- E-Mail
- Passwort-Hash
- Rolle
- Name
- Spracheinstellung
- Aktivstatus
- Metadaten wie Erstellungszeitpunkt

Benutzergruppen:
- interne Nutzer
- Bewerber
- Partner
- Seed-/Testkonten

### Workspaces
Workspaces modellieren Produkt- bzw. Geschäftsbereiche.

Typische Attribute:
- Slug
- Name
- Area
- aktiv/inaktiv
- Pipeline-Stages
- verfügbare Kurse

Der Workspace-Kontext ist wichtig für Bewerbungsrouting und fachliche Segmentierung.

### Applications
Zentrales Fallobjekt des Systems.

Typische Inhalte:
- Applicant-Bezug
- Workspace-Bezug
- aktueller Stage/Status
- Zuweisung an Staff
- Priorität
- Bewerbungsnahe Fachattribute
- Notizen und Verlaufskontext

Applications sind der zentrale Knotenpunkt des operativen Systems.

### Leads
Früher Eingangsdatensatz vor oder beim Übergang in eine Application.

Typische Inhalte:
- Personendaten
- Kontaktinformationen
- Interessensbereich
- Kurswunsch
- Sprachstand
- Quelle
- optionale Inline-Dokumente

### Documents
Dokumenten-Metadaten mit Bezug zu Applications.

Typische Inhalte:
- Dokumenttyp
- Status
- Kommentare / Ablehnungsgründe
- Datei-Metadaten
- Storage-Referenzen

### Tasks
Interne Aufgaben zur operativen Bearbeitung.

Typische Inhalte:
- Titel / Beschreibung
- Bezug zu Application
- zugewiesene Person
- Frist
- Priorität
- Status
- Sichtbarkeit

### Messages / Conversations
Kommunikationsobjekte zwischen Beteiligten.

Typische Inhalte:
- Teilnehmer
- Nachrichteninhalt
- Sichtbarkeit
- optionaler Application-Bezug

### Notifications
Systemseitige Benachrichtigungen pro Benutzer.

### Consents
Einwilligungsobjekte.

Typische Inhalte:
- Consent-Typ
- Version
- granted / nicht granted
- Benutzer- und Zeitbezug

### Followups
Wiedervorlagen für operative Nachverfolgung.

Typische Inhalte:
- Application-Bezug
- Fälligkeitsdatum
- Grund
- zugewiesene Person
- Status

### Audit Logs
Nachvollziehbare Systemereignisse.

Typische Inhalte:
- Actor
- Zielobjekt
- Zeitpunkt
- Ereignistyp / Kontext

## Wichtige Beziehungen

### User ↔ Application
- Applicant kann Eigentümer bzw. Bezugsperson einer Application sein.
- Staff kann Applications zugewiesen bekommen.

### Workspace ↔ Application
- Jede Application liegt in einem Workspace-Kontext.
- Pipeline-Stages hängen fachlich am Workspace.

### Application ↔ Document
- Eine Application kann mehrere Dokumente besitzen.

### Application ↔ Task
- Aufgaben können einer Application zugeordnet sein.

### Conversation ↔ Message
- Konversationen gruppieren Nachrichten.

### User ↔ Notification
- Benachrichtigungen sind benutzerbezogen.

### Application ↔ Followup
- Followups hängen an operativen Fällen.

## Index-Relevanz

Die Datenbank legt gezielt Indizes für operative Kernpfade an, insbesondere für:

- Benutzer-E-Mail
- Login-Attempts und Expiry
- Token-Collections mit TTL
- Application-Zugriffe nach Applicant, Workspace und Stage
- Documents / Tasks nach Application
- Messaging / Conversations
- Notifications nach Benutzer
- Audit Logs
- Webhook-Events

## Bootstrap- / Seed-Logik

Beim Start werden mindestens diese Datenbereiche initialisiert:

- Workspaces
- Admin-Account
- optionale Dev-/Test-Accounts

Das bedeutet: Ein Teil des Datenmodells ist nicht nur fachlich, sondern auch bootstrapping-relevant.

## Modellierungsprinzipien

1. **Applications als zentraler operativer Hub**
2. **Workspaces als fachliche Segmentierung**
3. **Users und Rollen als Zugriffsachse**
4. **Documents, Tasks, Messages, Followups als angehängte Arbeitsobjekte**
5. **Audit und Notifications als systemische Begleitobjekte**

## Dokumentationsfolgen

Diese Seite sollte angepasst werden, wenn:

- neue Kernobjekte hinzukommen
- Beziehungen zwischen Objekten strukturell geändert werden
- Collections oder wichtige Indizes ergänzt / entfernt werden
- Seeds neue fachliche Bereiche oder Rollen einführen
- neue Querschnittsobjekte wie Billing, Payments oder Reporting produktiv werden
