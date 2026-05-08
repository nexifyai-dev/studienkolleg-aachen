# 06_informationsarchitektur.md

## Ziel-IA

Die Soll-Architektur trennt strikt zwischen:
1. **öffentlicher Website-/Funnel-Ebene**,
2. **Applicant Portal**,
3. **Agency/Affiliate Layer**,
4. **Staff/Admin Layer**,
5. **Dokumenten-, Kommunikations- und Kursmodulen**.

## Vollständige Seiten- und Modulstruktur

## A. Public Web

### 1. Entry / Start
- Startseite / Ökosystem-Übersicht
- Segmentwahl: Studienkolleg, Sprachkurse, Pflege, Arbeit/Ausbildung, Partner
- Free Consultation
- zentrale Vertrauenssektionen
- Footer mit konsolidierten Legal-/Kontaktangaben

### 2. Solutions / Angebotslogik
- Studienkolleg
  - Überblick
  - T-Course
  - M-Course
  - W-Course
  - M/T-Course, falls final bestätigt
- Sprachkurse
  - A1
  - A2
  - B1
  - Intensiv / Online / vor Ort
  - Prüfungen / ÖSD / TestAS-Relevanz
- Pflegefachschule
- Arbeit / Ausbildung
- Unterkunft / Stay in Aachen
- Guidance / Visa / Bewerbungsbegleitung
- Partner / Agenturen / Affiliates

### 3. Trust / Company
- Über uns
- Warum Deutschland?
- Warum Aachen?
- Team / Ansprechpartner
- Qualitäts- und Prozesslogik
- Sicherheit / Datenschutz / Dokumentenschutz
- ggf. Unterkunftspartner

### 4. Resources
- FAQ
- Wissensdatenbank
- Dokumenten-Checklisten
- Sprach-/Kursinformationen
- Visa-Guidelines
- Blog / News / Updates (später)

### 5. Conversion
- strukturierte Bewerbung
- offenes Kontaktformular
- Terminbuchung
- Sprachkursbuchung
- Platzreservierung
- Partneranfrage

### 6. Rechtliche Seiten
- Impressum
- Datenschutz
- AGB
- Consent-/Cookie-Information
- KI-/Kommunikationshinweise
- Refund-/Cancellation-Hinweise, sofern rechtlich final freigegeben

## B. Applicant Portal

### Hauptnavigation
1. Dashboard
2. My Journey / Bewerbungsstatus
3. Documents
4. Messages / Inbox
5. Financials
6. Learning / Kurse / Prüfungen
7. Appointments
8. Help / Knowledge Base
9. Profile & Settings

### Bereichszwecke und Hauptaktionen

| Bereich | Zweck | Hauptaktion | Sekundäraktion | Datenquellen | Rechte | Mobile |
|---|---|---|---|---|---|---|
| Dashboard | nächster Schritt sichtbar | offene Aufgabe starten | Status überblicken | applications, tasks, notifications | applicant | Pflicht |
| Journey | Status- und Prozesssicht je Bereich | Bereich öffnen | weiteren Bereich hinzufügen lassen | applications, pipelines, workspace_members | applicant | Pflicht |
| Documents | Upload, Prüfung, Nachbesserung | Dokument hochladen | Kommentar lesen | documents, document_requests | applicant | Pflicht |
| Messages | Kommunikation bündeln | Nachricht senden | Verlauf lesen | conversations, messages | applicant | Pflicht |
| Financials | Rechnungen / Zahlungen | Rechnung öffnen / bezahlen | Verlauf einsehen | invoices, transactions | applicant | Pflicht |
| Learning | freigeschaltete Kurse nutzen | Kurs starten | Prüfung buchen | courses, enrollments | applicant | hoch |
| Appointments | Termine sehen | Termin öffnen | Termin buchen / ändern | appointments | applicant | hoch |
| Settings | Präferenzen und Stammdaten | Kanalpräferenzen setzen | Sprache ändern | profiles, notification_preferences | applicant | Pflicht |

## C. Agency / Affiliate Layer

### Agency Dashboard
- Dashboard
- Meine Bewerber
- Kandidat anlegen
- Dokumente / Status
- Kommunikation
- Provisionen
- Team / Rollen
- Branding-Grundlagen (später vertieft)

### Affiliate Dashboard
- Dashboard
- Tracking-Links
- vermittelte Leads
- Status / Conversions
- Provisionen
- Profil / Einstellungen

## D. Staff / Admin Struktur

### Staff Portal
- Dashboard / Kanban
- Bewerberübersicht
- Bewerberprofil 360°
- Aufgaben
- Dokumentenprüfung
- Kommunikation
- Rechnungen
- Termine
- Kurse / Freigaben
- Reports (rollenbasiert)
- offene Sonderfälle / Dubletten

### Admin Portal
- Systemdashboard
- Workspaces / Bereiche
- Nutzer und Rollen
- Agenturen / Affiliates
- Content / Templates / Standardtexte
- Pipelines / Dokumentenmatrizen / Regeln
- Monitoring / Webhooks / Automation Logs
- Audit / Security / Compliance
- Finanzen / Export
- White-Label-Settings
- Knowledge Base / SEO / Legal Content

## E. Dokumentenstruktur

### Dokumentbereiche
- Identität
- Schulabschluss / Zeugnisse
- Sprachzertifikate
- Bewerbungsunterlagen
- Pflege-/Berufsnachweise
- Visadokumente
- Rechnungen / Zahlungsbelege
- Kurs-/Prüfungsnachweise
- interne Anhänge / Behördenexporte

### Dokumentmetadaten
- Dokumenttyp
- zugehöriger Bereich / Workspace
- Owner
- Upload-Kanal
- Status
- Version / Revision
- Sichtbarkeit
- Prüfer
- Kommentar / Ablehnungsgrund
- Frist / Erforderlichkeit

## Navigationslogik

### Applicant
- Single-Workspace: direkter Einstieg in aktiven Bereich.
- Multi-Workspace: Home mit Bereichskarten und Status.
- Tiefe Navigation reduziert; Bottom Navigation mobil, Sidebar desktop.

### Staff/Admin
- Workspace-Switcher oben links.
- globale Suche nach Bewerbern, Rechnungen, Dokumenten, Nachrichten.
- Kontextpaneel für „Other Applications / Other Workspaces“.

## Interne Verlinkung

### Public Web
- Studienkolleg-Seiten ↔ Sprachkurs-Seiten ↔ FAQ ↔ Beratung.
- FAQ ↔ AGB/Datenschutz nur dort, wo rechtlich relevant.
- Sprachkurse ↔ Prüfungen ↔ Bewerberprozess.
- Unterkunft / Stay in Aachen nur als klar gekennzeichneter Service-Baustein.

### Plattform
- Bewerberprofil ist der zentrale Einstiegspunkt:
  - Dokumente,
  - Nachrichten,
  - Rechnungen,
  - Aufgaben,
  - Termine,
  - Kurse,
  - andere Workspaces.

## Such- und Filterlogik

### Staff/Admin
- Volltextsuche über Name, E-Mail, Telefon, Bewerber-ID, Application-ID.
- Filter nach:
  - Bereich / Workspace,
  - Stage,
  - Dokumentenstatus,
  - Zahlungsstatus,
  - zugewiesenem Mitarbeiter,
  - Agentur / Affiliate,
  - Land / Sprache,
  - Aktivität / Inaktivität.

### Agency
- nur eigene Kandidaten
- Filter nach Status, Verantwortlichem, offenen Dokumenten, offenen Zahlungen

## Empty States

### Applicant
- „Aktuell keine offene Aufgabe. Wir informieren dich, sobald der nächste Schritt ansteht.“
- „Noch keine Nachricht vorhanden.“
- „Noch kein Kurs freigeschaltet.“

### Staff
- „Keine offenen Fälle in diesem Filter.“
- „Kein Mitarbeiter zugewiesen – bitte Zuweisung prüfen.“
- „Keine Dokumente in Prüfung.“

## Error States

### Applicant
- Upload fehlgeschlagen → klare Ursache + Retry.
- Zahlung aktuell nicht verfügbar → alternative Kontakt-/Hinweislogik.
- Zugriff auf Bereich nicht erlaubt → Supporthinweis statt technischer Fehlermeldung.

### Staff/Admin
- Webhook-/Provider-Fehler → Loglink + Retry + Incident Flag.
- RLS-/Berechtigungsfehler → Security Event + Supporthinweis.
- Dublettenblocker → Freigabeworkflow statt stilles Scheitern.

## Mobile Nutzbarkeit

### Pflicht
- 375 px optimiert.
- Dokumentupload mit Kamera-/Dateimanager-Unterstützung.
- große Touch-Ziele.
- Drawer/Sheet statt komplexer Desktop-Tabellen.
- Timeline vertikal mobil, horizontal erst ab größerem Breakpoint.
