# 18_umsetzungsroadmap.md

## Phasenplan

## Phase 0 – Klärung und Freigabe
**Ziel:** offene Blocker schließen, bevor gebaut wird.

### Muss
- Commercial/Legal SOT für Preise, Refunds, Kontakt-/Legal-Daten
- RLS-Matrix
- finale MVP-Bereichsgrenze
- Dokumentenmatrix je Kernpipeline
- Payment-/VAT-Entscheidung
- WhatsApp-Policy
- Kalendermodell

## Phase 1 – Fundament
**Ziel:** Identity, Tenant/Workspace, Sicherheit, Grundobjekte.

### Deliverables
- Supabase Setup
- Auth / profiles / organizations / workspaces / workspace_members
- pipelines / applications
- RLS Grundpolicies
- audit_logs / webhook_events / automation_runs / user_consents
- Monorepo + CI Basis
- Applicant/Public Skeleton

## Phase 2 – CRM Core
**Ziel:** operativer Studienkolleg-Prozess.

### Deliverables
- lead_ingest
- duplicate flow
- auto assignment
- staff kanban
- applicant dashboard
- task engine
- basic messaging layer

## Phase 3 – Dokumente und Applicant Journey
**Ziel:** sichere Dokumentenlogik und echte Applicant-Selbstbedienung.

### Deliverables
- private-documents bucket
- documents + requests + comments
- applicant uploads
- staff review UI
- reminder automation
- journey/timeline

## Phase 4 – Finance Core
**Ziel:** Rechnung, Zahlung, Statusfortschritt.

### Deliverables
- invoices + transactions
- invoice PDF
- provider integration
- webhook idempotency
- payment status logic
- Mahnlogik in MVP-Tiefe

**Gate:** nur starten, wenn Tax-/Refundlogik schriftlich geklärt.

## Phase 5 – Public Web und Content-Härtung
**Ziel:** vertrauensfähige Conversion-Ebene.

### Deliverables
- Home / Studienkolleg / Sprachkurse / FAQ / Contact / Legal
- Claim-Policy Umsetzung
- konsistente Legal/Commercial Inhalte
- Beratung / Bewerbung / Reservierung
- Analytics-Grundlage

## Phase 6 – Agency / Affiliate / Reporting
**Ziel:** Partner- und Steuerungsfunktionen.

### Deliverables
- agency dashboard
- affiliate links / commissions
- partnerbezogene Sichtbarkeit
- management dashboards
- exporte

## Phase 7 – LMS / Course Layer
**Ziel:** Sprachkurs und Schulungsmodul produktiv anbinden.

### Deliverables
- course catalog
- enrollment
- internal video access
- release rules
- applicant learning center
- optional external LMS step 1/2

## Phase 8 – Skalierung und Härtung
**Ziel:** Betriebssicherheit und Ausbau.

### Deliverables
- queueing vertiefen
- partitioning
- read-models / snapshots
- advanced monitoring
- white-label basics
- PWA-Härtung

## Kritischer Pfad

1. Klärung Payment/Legal
2. Identity / Workspace / RLS
3. Application Model
4. Lead Ingest
5. Applicant Portal Basis
6. Dokumentenprozess
7. Rechnungslogik
8. Public Conversion / Legal Konsistenz
9. Partner-/Kursausbau

## Priorisierung nach Muss / Soll / Kann

### Muss
- Phase 0 bis 5 in tragfähiger Tiefe
- ohne diese Phasen kein belastbarer Go-Live

### Soll
- Phase 6 und 7 direkt anschließen, aber nicht als MVP-Blocker

### Kann
- White-Label-Subdomains, native App, OCR, Matching

## Umsetzungslogik für den AI-Agenten

1. Nicht mit Design, sondern mit Daten- und Rechtefundament starten.
2. Keine Public Pages produktiv stellen, bevor Legal/Commercial konsistent sind.
3. Jede neue Funktion auf Funnel, Rolle, Datenobjekt, Event, Audit und QA zurückführen.
4. Jede Automation nur mit Trigger, Idempotenz, Retry und Log.
5. Keine Phase freigeben, wenn der nächste Bereich auf instabilem Fundament aufsetzt.

## Milestones

| Milestone | Ergebnis |
|---|---|
| M1 | Architektur, ERD, RLS-Matrix, offene Punkte freigegeben |
| M2 | Identity/Workspace/Application Core steht |
| M3 | Applicant- und Staff-Kernflows laufen im Staging |
| M4 | Dokumentenprozess produktionsreif |
| M5 | Payment-Modul freigegeben |
| M6 | Public Website rechtlich und inhaltlich konsistent |
| M7 | MVP Go-Live Studienkolleg |
| M8 | Sprachkurs-/Partnerausbau |
