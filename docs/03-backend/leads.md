# Leads Domain

## Zweck

Die Leads-Domäne bildet den öffentlichen Einstieg in das System. Sie nimmt unautorisierte Bewerbungs- bzw. Interessentenanfragen entgegen und überführt sie – abhängig vom Kontext – in Benutzer-, Application- und Dokumentobjekte.

## Besondere Rolle im System

Leads sind die Brücke zwischen öffentlicher Website und internem Fallmanagement.

Die Domäne übernimmt mehrere Aufgaben in einem Schritt:

- öffentliche Datenerfassung ohne Login
- Duplicate Detection über E-Mail / bestehendes Konto
- optionale Kontoerstellung für Bewerber
- Workspace-Zuordnung anhand des Interessensbereichs
- Anlage einer Application
- optionale Inline-Dokumentenverarbeitung
- Trigger für Automationen und Folgekommunikation

## Zugriff und Sicherheitsmodell

Der Lead-Ingest-Endpunkt ist bewusst öffentlich erreichbar.

Wichtige Sicherungen:
- Datenvalidierung über `LeadIngest`
- Duplicate Detection statt blindem Neuanlegen
- Passwort-Hashing nur bei gültigem Passwortkontext
- Upload-Validierung bei Inline-Dokumenten
- Audit Logging für relevante Ereignisse

## Ingest-Flow auf hoher Ebene

### 1. Eingang des Formulars
Der öffentliche Ingest akzeptiert persönliche Daten, Interessensbereich, Bewerbungsdaten und optional Dokumente.

### 2. Benutzerprüfung
Anhand der E-Mail wird geprüft, ob bereits ein Benutzer existiert.

Mögliche Folgen:
- bestehender Benutzer → Duplicate-Flag
- neues Konto → Applicant wird angelegt
- bestehendes Konto ohne Passwort → Konto kann im Rahmen des Flows „geclaimt“ werden

### 3. Workspace-Auflösung
`area_interest` wird auf einen Workspace gemappt.

Verhalten:
- bevorzugte Auflösung über `area`
- Fallback auf den Studienkolleg-Workspace, falls kein direkter Treffer gefunden wird

### 4. Application-Erstellung
Wenn noch keine aktive Application für den Nutzer im passenden Workspace existiert, wird eine neue Application erzeugt.

Die Application startet mit:
- `current_stage = lead_new`
- fachlichen Feldern aus dem Formular
- Duplicate-Flag
- Zeit- und Aktivitätsmetadaten

### 5. Inline-Dokumente
Falls Dokumente mitgesendet werden:
- Base64-Decoding
- Upload-Validierung
- interner Storage-Key
- Persistenz in `documents`
- Audit Log je Dokument

### 6. Automationen und Kommunikation
Nach erfolgreicher Anlage können ausgelöst werden:
- Eingangsbestätigung der Bewerbung
- Hinweis auf fehlende Dokumente
- Welcome-E-Mail bei Kontoanlage

### 7. Optionale Session-Erzeugung
Wenn im Formular ein Passwort gesetzt wurde, kann direkt ein Bewerberkonto aktiviert und per Cookie-basierter Session eingeloggt werden.

## Duplicate Handling

Die Domäne behandelt Dubletten pragmatisch:

- vorhandene E-Mail erzeugt `duplicate_flag`
- bestehende aktive Application im Workspace verhindert Doppelanlage
- bestehender Nutzer kann teilweise angereichert werden, statt neu angelegt zu werden

Das ist fachlich wichtig, weil der Lead-Flow nicht nur Marketing-Formular ist, sondern der operative Eintrittspunkt in die Plattform.

## Gekoppelte Systeme

Die Leads-Domäne hängt eng an:

- Users
- Workspaces
- Applications
- Documents
- Storage
- Audit
- Automation
- Email
- Auth / Cookie-Session

## Typische Änderungsfolgen

Änderungen im Lead-Flow wirken sich oft aus auf:

- öffentliche Bewerbungsseite
- Applicant-Onboarding
- Duplicate Handling
- Workspace-Zuordnung
- Dokumentanforderungen
- Automations- und Mail-Logik
- Datenschutz / Consent-Kontext

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- Lead-Formularfelder geändert werden
- Duplicate-Logik geändert wird
- Workspace-Mapping geändert wird
- Direct-Account-Creation-Verhalten geändert wird
- Inline-Dokumente oder Pflichtdokumentlogik geändert werden
- Automations- oder Eingangskommunikation geändert wird
