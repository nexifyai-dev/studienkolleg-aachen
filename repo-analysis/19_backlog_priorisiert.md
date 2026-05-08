# 19_backlog_priorisiert.md

## Epics, Tasks und Subtasks

## Epic 1 – Governance & Klärung
**Priorität:** Muss  
**Owner:** Projektleitung / Admin / Legal / Commercial

### Task 1.1 – Preis-/Refund-SOT finalisieren
- Preisquellen konsolidieren
- Raten-/Gesamtpreis definieren
- Refund-/Visa-/Storno-Regeln finalisieren
- Abnahme: ein freigegebener Commercial-Stand vorhanden

### Task 1.2 – Legal-/Kontaktkonsistenz herstellen
- Impressum, Datenschutz, Footer, Kontaktseite abgleichen
- juristische Betreiber- und Adressdaten finalisieren
- Abnahme: keine Widersprüche mehr auf Public Pages

### Task 1.3 – Dokumentenmatrix finalisieren
- je Bereich und Stage Pflicht-/Soll-Dokumente definieren
- Blocker vs. optional markieren
- Abnahme: maschinenlesbare Matrix vorhanden

## Epic 2 – Architektur & Datenfundament
**Priorität:** Muss  
**Owner:** Technical Lead

### Task 2.1 – Monorepo anlegen
### Task 2.2 – Supabase Projekt konfigurieren
### Task 2.3 – Migrationen aufsetzen
### Task 2.4 – organizations/profiles/workspaces/workspace_members
### Task 2.5 – pipelines/applications
### Task 2.6 – audit_logs/webhook_events/automation_runs/user_consents

**Akzeptanzkriterien**
- Migrationen versioniert
- ERD konsistent
- Seed-/Mockdaten nicht im Produktivpfad

## Epic 3 – Rechte und Sicherheit
**Priorität:** Muss  
**Owner:** Security + Backend

### Task 3.1 – Rollenmodell final implementieren
### Task 3.2 – RLS Policies pro Tabelle
### Task 3.3 – Storage Policies
### Task 3.4 – RLS-/Security-Tests
### Task 3.5 – MFA-/Secret-/Webhook-Security

**Done-Kriterien**
- unberechtigter Zugriff technisch ausgeschlossen
- Tests grün
- Audit-Logs schreiben Rollenänderungen

## Epic 4 – Lead- und CRM-Core
**Priorität:** Muss  
**Owner:** Backend + Product

### Task 4.1 – lead_ingest
### Task 4.2 – duplicate detection
### Task 4.3 – source mapping
### Task 4.4 – auto assignment
### Task 4.5 – application activity logging

## Epic 5 – Applicant Portal Core
**Priorität:** Muss  
**Owner:** Frontend + UX

### Task 5.1 – Login / invite / onboarding
### Task 5.2 – dashboard
### Task 5.3 – journey / status view
### Task 5.4 – profile/settings
### Task 5.5 – workspace switcher (multi-workspace case)

## Epic 6 – Dokumentenmodul
**Priorität:** Muss  
**Owner:** Frontend + Backend

### Task 6.1 – document_requests
### Task 6.2 – secure uploads
### Task 6.3 – reviewer UI
### Task 6.4 – rejection reason flow
### Task 6.5 – reminders
### Task 6.6 – internal/public comments

## Epic 7 – Kommunikationshub
**Priorität:** Muss  
**Owner:** Backend + Frontend

### Task 7.1 – conversations/messages
### Task 7.2 – portal inbox UI
### Task 7.3 – e-mail sending
### Task 7.4 – provider delivery callbacks
### Task 7.5 – notification preferences

## Epic 8 – Finance Core
**Priorität:** Muss  
**Owner:** Finance + Backend

### Task 8.1 – invoice model
### Task 8.2 – transaction ledger
### Task 8.3 – invoice PDF generation
### Task 8.4 – payment webhook processing
### Task 8.5 – partially_paid/refund logic
### Task 8.6 – dunning flow

## Epic 9 – Public Website / Conversion
**Priorität:** Muss  
**Owner:** Content + Design + Frontend

### Task 9.1 – ecosystem homepage
### Task 9.2 – Studienkolleg pages
### Task 9.3 – Sprachkurs pages
### Task 9.4 – FAQ/Knowledge
### Task 9.5 – Bewerbungs-/Kontaktflows
### Task 9.6 – legal pages
### Task 9.7 – claim review

## Epic 10 – Task- und Terminmodul
**Priorität:** Soll  
**Owner:** Product + Ops

### Task 10.1 – task engine
### Task 10.2 – applicant tasks UI
### Task 10.3 – staff task management
### Task 10.4 – calendly sync
### Task 10.5 – appointment reminders

## Epic 11 – Agency / Affiliate
**Priorität:** Soll  
**Owner:** Partner Ops + Backend

### Task 11.1 – agency roles and dashboard
### Task 11.2 – candidate submission
### Task 11.3 – affiliate links/clicks
### Task 11.4 – commissions
### Task 11.5 – restricted partner reporting

## Epic 12 – LMS / Course Layer
**Priorität:** Soll  
**Owner:** Education + Product + Backend

### Task 12.1 – course catalog
### Task 12.2 – enrollments
### Task 12.3 – internal video access
### Task 12.4 – course release rules
### Task 12.5 – applicant learning center
### Task 12.6 – external provider step 1

## Epic 13 – Reporting / Monitoring
**Priorität:** Soll  
**Owner:** Admin + DevOps

### Task 13.1 – KPI dashboard
### Task 13.2 – queue/webhook monitoring
### Task 13.3 – audit investigation UI
### Task 13.4 – exports

## Epic 14 – Skalierung und Härtung
**Priorität:** Kann/Soll je Last | **Owner:** DevOps

### Task 14.1 – partitioning
### Task 14.2 – read replicas prep
### Task 14.3 – image/storage tiering
### Task 14.4 – performance optimization
### Task 14.5 – PWA hardening

## Akzeptanzkriterien (Auszug)

- Jeder Epic-Block muss mindestens einen real durchgespielten E2E-Flow enthalten.
- Jede kritische Änderung braucht Audit-Event.
- Jede externe Integration braucht Webhook-/Retry-/Error-Nachweis.
- Jede Public-Seite braucht Copy-Compiler- und Claim-Review.
- Jede Rolle braucht positiven und negativen Zugriffstest.

## Done-Kriterien (global)

1. fachlich korrekt
2. technisch stabil
3. rechtekonform
4. auditierbar
5. barrierearm
6. inhaltlich freigegeben
7. mit Rollback und Monitoring abgesichert
