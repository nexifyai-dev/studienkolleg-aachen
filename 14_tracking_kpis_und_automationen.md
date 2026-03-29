# 14_tracking_kpis_und_automationen.md

## Event-Taxonomie

## Pflicht-Events (Baseline)

| Event | Zweck | Pflichtfelder |
|---|---|---|
| page_view | Funnel- und Navigationsanalyse | url, referrer, locale, timestamp |
| cta_click | Conversion-Signale | cta_id, location, label, destination |
| form_start | Formularinteresse | form_id, source, workspace_hint |
| form_submit | Lead-Erzeugung | form_id, success, source, area |
| form_error | UX-Optimierung | form_id, field, error_type |
| search_internal | Suchnutzung | query, context |
| login_success | Aktivierung | user_type, workspace_count |
| document_uploaded | Prozessfortschritt | application_id, document_type, source |
| document_reviewed | Prüfentscheid | application_id, document_type, outcome |
| invoice_created | Finance-Fortschritt | invoice_id, amount, area |
| invoice_paid | Finanzielle Conversion | invoice_id, provider, amount |
| appointment_booked | Termin-Conversion | appointment_id, source |
| course_visible | Cross-Sell-Signal | course_id, trigger |
| course_booked | Kurs-Conversion | course_id, price, source |
| course_unlocked | Zugang bereitgestellt | course_id, provider_type |
| message_received | operative Reaktionspflicht | channel, conversation_id |
| stage_changed | Kernprozesssteuerung | application_id, old_stage, new_stage, trigger_source |

## Zusatz-Events je Geschäftsmodell

### B2B / Partner
- agency_candidate_created
- affiliate_link_clicked
- affiliate_conversion_confirmed
- commission_created

### Operations
- duplicate_flagged
- duplicate_resolved
- task_created
- task_overdue
- webhook_failed
- automation_failed

### LMS
- video_started
- lesson_completed
- exam_booked
- external_access_provisioned
- access_revoked

## Event-Felder

### Allgemein
- event_id
- occurred_at
- actor_type
- actor_id (pseudonymisiert wo nötig)
- workspace_id
- organization_id
- source
- trigger_source
- schema_version

## KPI-System

## Funnel-KPIs
1. Visit → Lead
2. Lead → Portalaktivierung
3. Portalaktivierung → Dokumentenvollständigkeit
4. Dokumentenvollständigkeit → Rechnung
5. Rechnung → Zahlung
6. Zahlung → nächster Prozessschritt / Kursfreigabe
7. Start → Abschluss / Archiv

## Operations-KPIs
1. offene Dubletten
2. Stage-Durchlaufzeit
3. überfällige Fälle
4. Antwortzeit Kommunikation
5. Dokumentenprüfzeit
6. offene Aufgaben je Mitarbeiter
7. Reaktivierungsquote inaktiver Leads

## Finance-KPIs
1. offene Rechnungen
2. Zahlungsquote
3. Mahnquote
4. Refund-/Chargeback-Quote
5. Umsatz nach Bereich
6. Provisionen / Auszahlungen

## Growth-/Partner-KPIs
1. Leads je Quelle
2. Leads je Agentur / Affiliate
3. Conversion je Quelle
4. Kurs-Upsell-Quote
5. Partnerperformance

## Thresholds

| KPI | Threshold | Aktion |
|---|---|---|
| Portalaktivierungsrate < Zielwert | gelb | Onboarding prüfen |
| Dokumentenabbruch > Zielwert | gelb | Reminder / UX Review |
| Form Abandonment > 60 % | rot | Formular-Review |
| Stage-Dauer > Maximalzeit | rot | Eskalation an Teamlead |
| Invoice Aging > definierter Rahmen | rot | Mahnworkflow |
| Webhook Failure Rate > 0 | rot | Incident / Retry |
| Queue Lag > definierter Puffer | rot | Worker/Backlog prüfen |
| CTA Click Rate < 2 % | gelb | Copy-/CTA-Test |
| LCP > 3.0s | rot | Performance-Sprint |
| WhatsApp delivery failure erhöht | gelb/rot | Kanal-/Kostenprüfung |

## Trigger → Auto-Action-Mapping

### Lead / Activation
- form_submit → lead_create → duplicate_check → assignment → invite_send
- login_missing_day_3 → reminder_email + staff_task

### Dokumente
- required_doc_pending_day_2 → reminder_email
- required_doc_pending_day_5 → reminder_email + portal_notice
- required_doc_pending_day_10 → escalation + optional WhatsApp
- document_rejected → applicant_notice + reupload_request

### Rechnungen / Zahlungen
- invoice_created → email + portal_notice
- invoice_overdue_day_1 → reminder
- invoice_overdue_day_7 → warning
- invoice_paid → receipt + stage_advance + staff_notice
- chargeback / refund → access_review + finance_task

### Termine
- appointment_booked → confirmations
- appointment_t_minus_24h → reminder
- appointment_completed → staff_followup_task

### Kurse
- payment_success_course → enrollment_create → unlock_notice
- status_change_language_needed → course_recommendation
- chargeback_course → revoke_access

### Inaktivität
- no_activity_14d → nurture_email
- no_activity_30d → stronger reminder
- no_activity_60d → dormant + sales_task

## Reporting-/Dashboard-Logik

### Applicant Success Dashboard
- Aktivierung
- Dokumentenfortschritt
- Payment-Funnel
- Stage-Delays
- Abschlussquote

### Operations Dashboard
- offene Dubletten
- Fälle je Mitarbeiter
- überfällige Tasks
- dokumentenbezogene Wartezeiten
- offene Webhook-/Automation-Fehler

### Partner Dashboard
- Leads
- statusbezogene Kandidaten
- Conversions
- Provisionen

### Management Dashboard
- Leads nach Quelle/Bereich
- Umsatz / offene Forderungen
- Durchlaufzeiten
- Mitarbeiterlast
- Cross-Sell Kursmodule

## CRM-/Mail-/Reminder-Logik

### Pflicht
- Templates versionieren,
- Kanalpräferenzen beachten,
- Security/Invoice notfalls übersteuern,
- Delivery-Status loggen,
- Retry + Fehlernachweis.

## n8n-/Workflow-Struktur

### Empfohlene Nutzung
- periodische Reports,
- Slack-/Teams-/Mail-Alerts,
- CRM-Batch-Prozesse,
- nichtkritische Marketing-Sequenzen,
- externe Daten-Synchronisationen.

### Nicht als primäre Logik
- RLS,
- Kernstatuswechsel,
- Rechnungsbuchung,
- Webhook-Wahrheit,
- sicherheitskritische Freigaben.

## Automations-Go-Live-Check

1. Trigger dokumentiert?
2. Input-/Output-Schema klar?
3. Idempotenz vorhanden?
4. Retry-Strategie definiert?
5. Logging vorhanden?
6. User- und Staff-Kommunikation sauber?
7. Rollback oder manuelle Korrektur möglich?
