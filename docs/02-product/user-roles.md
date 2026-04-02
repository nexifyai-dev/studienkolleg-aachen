# User Roles

## Zweck

Diese Seite beschreibt die fachlichen Rollen des Systems und ihre primären Produktflächen. Sie ist bewusst fachlich formuliert; technische Enforcement-Details liegen im Code und werden in separaten Backend-/Frontend-Seiten ergänzt.

## Rollenmodell im Überblick

Das System arbeitet mit mehreren klar getrennten Rollen. Die wichtigsten im aktuellen Produktzustand sind:

- `superadmin`
- `admin`
- `staff`
- `accounting_staff`
- `teacher`
- `applicant`
- `affiliate`

Je nach Backend können weitere Rollenvarianten vorkommen. Dokumentiert werden hier die Rollen, die in Frontend, Seed und Produktbeschreibung sichtbar sind.

## Rollen nach Benutzergruppe

### 1. Platform / Internal Operations

#### `superadmin`
Höchste Systemrolle.

Typische Aufgaben:
- Systemverwaltung
- Benutzer- und Rollenverwaltung
- Audit- und Betriebsübersicht
- Zugriff auf Admin-Flächen
- im Zweifel Vollzugriff auf interne Oberflächen

#### `admin`
Administrative Rolle mit Schwerpunkt auf Management und Konfiguration.

Typische Aufgaben:
- Zugriff auf Admin Dashboard
- Benutzerverwaltung
- Audit-Einsicht
- teilweise Zugriff auf Partnerfläche
- Steuerung interner Prozesse

#### `staff`
Operative Kernrolle im Tagesgeschäft.

Typische Aufgaben:
- Bewerbungen prüfen
- Kanban / Pipeline bearbeiten
- Aufgaben verwalten
- Kommunikation mit Bewerbern
- Anwendungsdetails pflegen
- Follow-ups und Fallmanagement

#### `accounting_staff`
Spezialisierte interne Rolle, die im Frontend als Staff-Rolle behandelt wird.

Vermuteter Schwerpunkt:
- finanz- oder abrechnungsnahe Prozesse
- Zugriff auf Staff-Flächen ohne volle Admin-Rechte

Diese Rolle sollte in einer nächsten Ausbaustufe noch gezielt dokumentiert werden.

#### `teacher`
Lehr- bzw. fachbezogene Staff-Unterrolle.

Typische Aufgaben:
- Sicht auf zugewiesene Fälle
- spezielles Dashboard im Staff-Bereich
- eingeschränkter, aber rollenadäquater Zugriff auf Bewerberkontexte

### 2. External / Applicant Side

#### `applicant`
Bewerberrolle für das Applicant Portal.

Typische Aufgaben:
- Dashboard und Status einsehen
- Journey / Fortschritt verfolgen
- Dokumente hochladen und Status prüfen
- Nachrichten lesen und senden
- Einstellungen verwalten
- Consent-Verwaltung

### 3. Partner / Referral Side

#### `affiliate`
Partner- bzw. Vermittlerrolle.

Typische Aufgaben:
- Partnerdashboard nutzen
- Vermittlungen einsehen
- Empfehlungslink verwenden
- Partnerbezogene Einstellungen pflegen

## Zuordnung zu Produktflächen

| Rolle | Primäre Fläche |
|---|---|
| `superadmin` | `/admin`, teils `/staff`, teils `/partner` |
| `admin` | `/admin`, teils `/staff`, teils `/partner` |
| `staff` | `/staff` |
| `accounting_staff` | `/staff` |
| `teacher` | `/staff` mit teacherspezifischem Dashboard |
| `applicant` | `/portal` |
| `affiliate` | `/partner` |

## Routing-Verhalten auf hoher Ebene

- Nicht eingeloggte Nutzer sehen öffentliche Seiten und Auth-Flows.
- Eingeloggte interne Rollen werden auf Staff- oder Admin-Flächen gelenkt.
- Affiliates werden auf die Partnerfläche gelenkt.
- Applicants werden auf das Applicant Portal gelenkt.

## Sicherheits- und Prozessimplikationen

Das Rollenmodell ist ein zentrales Querschnittsthema. Änderungen an Rollen wirken sich typischerweise auf mehrere Ebenen aus:

- Frontend-Routing
- Protected Routes
- Backend-Dependencies / RBAC
- API-Antworten und sichtbare Datenausschnitte
- Seed-Logik und Testkonten
- Audit- und Betriebsverhalten

## Dokumentationsregeln bei Rollenänderungen

Diese Seite muss aktualisiert werden, wenn mindestens einer der folgenden Fälle eintritt:

- neue Rolle eingeführt
- Rolle entfernt oder umbenannt
- Rolle erhält neue Hauptfläche
- Teacher-/Partner-/Accounting-Verhalten ändert sich sichtbar
- neue Berechtigungsgrenzen zwischen Staff, Admin und Applicant entstehen

## Offene Dokumentationslücken

Folgende Punkte sollten später detaillierter dokumentiert werden:

- exakte Backend-Enforcement-Regeln pro Rolle
- Abgrenzung `admin` vs. `superadmin`
- Abgrenzung `staff` vs. `teacher`
- Aufgaben und Grenzen von `accounting_staff`
- Partnerrechte auf Daten- und Fallebene
