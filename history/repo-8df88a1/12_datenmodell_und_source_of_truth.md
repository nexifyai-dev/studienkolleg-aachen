# 12_datenmodell_und_source_of_truth.md

## Architekturprinzip

Das Modell trennt strikt:
- **Identity**: Wer ist die Person?
- **Context**: In welchem Workspace/Bereich ist sie aktiv?
- **State**: In welchem Status befindet sich der Vorgang?
- **Evidence**: Welche Dokumente, Nachrichten, Zahlungen, Audit-Ereignisse belegen den Prozess?

## Hauptobjekte

### 1. organizations
Mandanten / Partnerstrukturen.
- Typen: internal, agency
- enthält Branding-Grundlagen und Abrechnungsreferenzen.

### 2. profiles
Globale Personenidentität.
- Auth-Referenz
- Rolle
- primäre Organisation
- Sprache
- Affiliate-/Referral-Bezug
- globale Stammdaten

### 3. workspaces
Fachliche Kontexte / Bereiche.
- Studienkolleg
- Sprachschule
- Pflege
- Arbeit/Ausbildung
- ggf. Partner-/Mandantenkontexte

### 4. workspace_members
Verknüpfung von Profil und Bereich.
- workspace_id
- profile_id
- rolle im Workspace
- status

### 5. pipelines
Konfiguration der Prozessstufen je Bereich.

### 6. applications
Operativer Vorgang je Bewerber und Bereich.
- applicant_id
- workspace_id
- current_stage
- assigned_staff_id
- priority
- strukturierte Kernfelder + flexible Zusatzdaten

### 7. documents / document_requests / document_versions
Dokumentenanforderung, Upload, Prüfstatus und Historie.

### 8. conversations / messages
Kommunikationsverlauf über Kanäle.

### 9. invoices / transactions
Rechnungen und Zahlungen mit Ledger-Logik.

### 10. tasks
interne und applicant-seitige Aufgaben.

### 11. notifications / notification_preferences / notification_templates / notification_logs
Benachrichtigungssteuerung und Nachweis.

### 12. appointments
Terminbuchungen und Erinnerungen.

### 13. courses / lms_providers / course_enrollments / course_access_credentials / course_release_rules
Kurskatalog, Freigabe und Zugriffsbereitstellung.

### 14. audit_logs / automation_runs / webhook_events / user_consents
Governance-, Debugging- und Compliance-Layer.

### 15. affiliate_links / affiliate_clicks / commissions
Attribution und Provisionslogik.

## Relationen

- profile 1:n workspace_members
- workspace 1:n workspace_members
- profile 1:n applications
- workspace 1:n applications
- application 1:n documents
- application 1:n tasks
- application 1:n invoices
- application 1:n conversations
- conversation 1:n messages
- application n:1 assigned_staff(profile)
- application n:1 agency / organization (je Modell)
- profile 1:n appointments
- profile 1:n course_enrollments
- course 1:n course_enrollments
- invoice 1:n transactions

## Pflichtfelder

### profiles
- id
- email
- role
- language_pref
- created_at

### applications
- id
- applicant_id
- workspace_id
- current_stage
- organization_id bzw. tenant context
- created_at
- last_activity_at

### documents
- id
- application_id
- document_type
- status
- storage_path
- uploaded_by
- uploaded_at

### invoices
- id
- application_id
- amount_total
- currency
- status
- due_at
- created_at

## Statusfelder

### application
- lead_new
- qualified
- docs_requested
- docs_received
- docs_review
- invoice_open
- payment_received
- process_next
- completed
- dormant
- archived

### document
- missing
- uploaded
- in_review
- approved
- rejected
- superseded

### invoice
- draft
- open
- partially_paid
- paid
- void
- refunded
- uncollectible

### task
- open
- in_progress
- done
- blocked
- overdue

## Integritätsregeln

1. Eine Person erhält nur **ein** globales Profil je Tenant.
2. Ein Bereichsprozess ist eine **Application**, nicht ein neues Profil.
3. Dokumentzugriff erbt Rechte der Application.
4. Rechnungsstatus wird nicht frei editiert, sondern aus Ledger und definierten Aktionen abgeleitet.
5. Statuswechsel müssen validiert werden.
6. Webhooks sind idempotent.
7. Audit Logs sind append-only.
8. Soft Delete statt Hard Delete im Produktivpfad.

## Source-of-Truth-Matrix

| Bereich | Source of Truth | Nicht zulässig als führende Quelle |
|---|---|---|
| Applicant Identity | profiles + auth.users | Excel, Mail-Postfach, Chatverläufe |
| Bereichsstatus | applications | manuelle Listen, Slack-/Mail-Notizen |
| Rollen und Rechte | profiles + workspace_members + RLS policies | nur Frontend-Routing |
| Dokumente | documents + private storage | E-Mail-Anhänge als Primärablage |
| Rechnungen | invoices | manuelle PDF-Ordner |
| Zahlungen | transactions + provider webhooks / manuelle Bestätigung | loses Bank-Monitoring ohne Systembuchung |
| Nachrichten | conversations/messages | verstreute Postfächer ohne Ingestion |
| Benachrichtigungspräferenzen | notification_preferences | lokale UI-Schalter ohne Persistenz |
| Kurse / Zugänge | courses + enrollments + provisioning layer | externe LMS-Zugänge ohne Rückfluss |
| Consent | user_consents | informelle Mailzustimmungen |
| Audit / Nachweise | audit_logs | Freitextnotizen |
| Reporting | abgeleitete Dashboard-/Snapshot-Daten | spontane Excel-Auswertungen |
| Public Pricing | freigegebene Commercial Config | Styleguide-Samples / alte FAQ |
| Legal Content | freigegebener Legal-CMS-Stand | Footer-Freiformtexte |

## Verbotene Parallelquellen

1. Bewerberstatus gleichzeitig in Excel und Plattform pflegen.
2. Dokumente in E-Mail-Postfächern als „eigentliche“ Arbeitsversion verwenden.
3. Preis- oder Refundtexte gleichzeitig aus FAQ, Styleguide und Web-Footer ziehen.
4. Partner- oder Provisionsstände außerhalb des Systems nachhalten.
5. manuelle Nachrichtenverläufe ohne CRM-Eintrag.

## Sensible Datenbereiche

- Ausweis-/Passdokumente
- Zeugnisse / Lebensläufe
- Visa- und Aufenthaltsinformationen
- Zahlungsdaten
- Kommunikationsinhalte
- Consent- und Auditdaten
- externe Zugangsdaten für LMS-Provisioning

## Datenmodell-Entscheidungen

### Verifiziert
- PostgreSQL/Supabase ist das Zielmodell.
- RLS ist Pflicht.
- Multi-Workspace ist nötig.
- JSONB wird für flexible Formulardaten genutzt.

### Plausibel abgeleitet
- JSONB darf nur für Zusatzfelder dienen; zentrale Filterfelder gehören in eigene Spalten.
- Document Versioning wird ab Release 1 als strukturierte Historie empfohlen, auch wenn MVP minimal starten kann.
- comments mit `visibility = internal/public` sind Pflicht.

## Minimaler Tabellenkern Release 1

1. organizations
2. profiles
3. workspaces
4. workspace_members
5. pipelines
6. applications
7. application_activities
8. documents
9. document_requests
10. comments
11. invoices
12. transactions
13. conversations
14. messages
15. tasks
16. notifications
17. notification_preferences
18. audit_logs
19. automation_runs
20. webhook_events
21. user_consents
22. appointments
23. affiliate_links
24. commissions
