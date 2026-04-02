# Messaging Domain

## Zweck

Die Messaging-Domäne bildet die fallnahe und supportnahe Kommunikation innerhalb der Plattform ab. Sie verbindet Applicants und interne Nutzer über Conversations, Messages und Anhänge.

## Produktrolle

Messaging ist ein zentraler Teil des operativen Systems, weil es:

- direkte Kommunikation mit Bewerbern ermöglicht
- in Portal und Staff-Fläche sichtbar ist
- an Fallkontexte gekoppelt werden kann
- Support-Konversationen automatisch erzeugt

## Sicherheitsmodell

### Applicant
Applicants dürfen nur Conversations lesen, an denen sie teilnehmen.

### Staff / interne Rollen
Interne Rollen haben deutlich breitere Einsicht in Conversations.

### Nachrichtenvalidierung
- Inhalt darf nicht leer sein
- Nachrichtenlänge ist begrenzt
- Attachments werden validiert und kontrolliert ausgeliefert

## Kernobjekte

### Conversations
Konversationen gruppieren Nachrichten und enthalten u. a.:
- Teilnehmer
- Zeitstempel
- optional `application_id`
- Support-Flag
- letzten Aktivitätszeitpunkt

### Messages
Nachrichten enthalten u. a.:
- `conversation_id`
- `content`
- `sender_id`
- `sender_name`
- `visibility`
- `sent_at`
- `read`
- optional Attachment-Metadaten

## Hauptfunktionen

### Conversations auflisten
Applicants sehen nur eigene Conversations.
Interne Rollen sehen Conversations deutlich breiter.

Die API reichert Conversations zusätzlich an mit:
- Teilnehmernamen
- Teilnehmerrollen
- Vorschau der letzten Nachricht
- Sender der letzten Nachricht

### Support-Conversation erzeugen oder holen
Für Applicants kann automatisch eine Support-Konversation aufgebaut werden.

Verhalten:
- vorhandene Support-Konversation wird wiederverwendet
- sonst wird eine neue Konversation angelegt
- wenn möglich, wird ein aktiver Staff-/Admin-Nutzer als Gegenpart ermittelt

### Nachricht senden
Mögliche Varianten:
- in bestehende Conversation senden
- neue Conversation mit explizitem Empfänger starten
- neue Support-Conversation ohne expliziten Empfänger starten

Wichtige Nebeneffekte:
- `last_message_at` der Conversation wird aktualisiert
- Senderdaten werden mitpersistiert

### Nachrichten abrufen
Applicants dürfen nur Nachrichten in eigenen Conversations abrufen.

### Nachricht als gelesen markieren
Einfacher Read-Status-Endpunkt für einzelne Messages.

### Attachment-Upload
Attachments werden im Messaging-Kontext über den Storage-Service verarbeitet.

Ablauf:
- Conversation-Zugriff prüfen
- Base64 decodieren
- Datei validieren
- Storage-Key intern erzeugen
- Datei speichern
- Nachricht mit Attachment-Metadaten anlegen

Wichtig:
- `storage_key` wird nicht an das Frontend herausgegeben

### Attachment-Download
Der Download läuft serverseitig über authentifizierten Zugriff auf den Storage-Service.

## Architekturbeobachtung

Messaging nutzt für Anhänge denselben Storage-Grundgedanken wie Documents: interne Speicherpfade bleiben serverintern, der Browser erhält keine direkten Storage-Ziele.

## Support- und Rollenlogik

Ein besonderer Aspekt dieser Domäne ist die automatische Zuordnung eines internen Gegenübers. Das macht Messaging nicht nur zu einem Chat-Modul, sondern zu einem operativen Support-Kanal.

## Gekoppelte Systeme

Die Messaging-Domäne hängt eng zusammen mit:

- Users
- Applications
- Storage
- Applicant Portal
- Staff Messaging UI

## Typische Änderungsfolgen

Änderungen an Messaging wirken sich oft aus auf:

- Portal-Kommunikation
- Staff-Kommunikationsoberflächen
- Sichtbarkeits- und Rollenlogik
- Support-Prozesse
- Attachment-Handling

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- Teilnehmer- oder Supportlogik geändert wird
- Attachment-Strategie geändert wird
- Sichtbarkeitsregeln geändert werden
- Conversations stärker an Applications oder Rollen gebunden werden
- Read-/Unread-Logik oder Message-Limits geändert werden
