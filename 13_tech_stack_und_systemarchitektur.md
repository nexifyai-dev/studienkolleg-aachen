# 13_tech_stack_und_systemarchitektur.md

## Architekturprinzip

Die Architektur folgt **Template first + DOS first + Datenbank first**:
- offene, skalierbare Standardbausteine,
- klare Zuständigkeiten,
- austauschbare Schichten,
- keine Frontend-Sicherheitsillusionen,
- Queueing und Auditierbarkeit als Grundprinzip.

## Empfohlener Stack

## Frontend

### Public Web
- **Next.js App Router**
- **Tailwind CSS**
- **shadcn/ui**
- **next-intl** für Mehrsprachigkeit

**Begründung:** SEO-fähig, schnell, DOS-konform, guter Fit für Marketing- und Portaloberflächen.

### Applicant / Staff / Agency Portal
- ebenfalls **Next.js App Router**
- gemeinsames **UI-Paket**
- TanStack Query / Server Components für effiziente Datenabfragen

### Mobile Strategie
- **Release 1:** responsive Web-App / PWA
- **später:** React Native / Expo für native Push und Store-Distribution

**Begründung:** entspricht der Quellenlage und reduziert initiale Komplexität.

## Backend

### Kern
- **Supabase / PostgreSQL**
- **Supabase Auth**
- **Supabase Edge Functions**
- **RLS**
- **Supabase Storage**

**Begründung:** projekt- und DOS-konform, schneller Start, starke RLS-Integration, geringer Infrastruktur-Overhead.

### Queue / Async
- **pg_mq** oder vergleichbare Postgres-Queue
- langfristig erweiterbar um dedizierte Worker

**Pflichtfälle für Queueing:**
- PDF-Generierung,
- Webhook-Nachverarbeitung,
- Massenbenachrichtigungen,
- LMS-Provisioning,
- Retry-Jobs.

## CMS / Content

### Empfohlen
- **MDX/Git-basiert** für Marketingseiten und Knowledge Base in Release 1,
- optional **Directus oder Strapi** später für nichttechnische Redaktion und komplexere Content-Workflows.

**Einstufung:** plausibel abgeleitet aus DOS-Standard und Projektfit.

## Datenbank

### Basis
- PostgreSQL 15+
- Supabase managed
- Extensions:
  - uuid-ossp
  - pg_net
  - pg_cron
  - pgvector (vorbereitet)
  - optional pg_trgm / pg_partman

### Begründung
- relationale Integrität,
- JSONB-Flexibilität,
- RLS,
- spätere Volltext-/Ähnlichkeitssuche,
- Partitionierung möglich.

## Auth

- E-Mail / Passwort
- Magic Link / Invite Flows
- optionale 2FA/MFA
- tenant- und workspace-bezogene Claims / Kontextprüfung

## Storage

### Buckets
- public-assets
- private-documents
- private-invoices
- course-assets (privat oder semi-privat, je Modell)

### Regeln
- niemals öffentliche sensible Dokumente,
- Zugriff nur via Signed URLs und DB-Rechte,
- Lifecycle-Policies für Archivierung.

## APIs

### Stil
- Edge-Function-Endpunkte für:
  - lead-ingest
  - auto-assign
  - send-notification
  - generate-invoice-pdf
  - stripe-webhook
  - calendly-sync
  - course-provisioning
  - consent-capture
  - export jobs

### API-Design
- versioniert,
- idempotent bei Webhooks,
- Input-/Output-Schemas validiert,
- trigger_source dokumentiert.

## Jobs / Automationen

### Transaktionale Automationen
- direkt über DB-Trigger + Edge Functions + Queue

### Orchestrierung / Low-Code
- **n8n** als empfohlene Ergänzung für bereichsübergreifende, nichtkritische oder integrationslastige Workflows
  - Reporting
  - interne Alerts
  - Batch-Synchronisationen
  - Marketing-Workflows

**Einstufung:** plausibel abgeleitet aus DOS-Standard; transaktionale Kernlogik bleibt im kontrollierten Backend.

## Tracking

### Event-System
- zentrales Event-Schema
- Basisevents:
  - page_view
  - cta_click
  - form_start
  - form_submit
  - form_error
  - pricing_view
  - plan_select
  - search_internal
  - login_success
  - document_uploaded
  - invoice_created
  - invoice_paid
  - course_unlocked

### Regeln
- keine Klartext-PII in Events,
- Schema-Versionierung,
- append-only.

## Analytics

### Empfohlen
- **PostHog** oder **Plausible** für Web-/Produktanalyse
- **Microsoft Clarity** für qualitative UX-Signale
- optional GA4 nur, wenn datenschutzrechtlich sauber freigegeben

## Monitoring

- **Sentry** für Frontend + Edge Functions
- Uptime Monitoring
- Queue-Lag Monitoring
- Slow Query Monitoring
- failed webhook / automation dashboard

## CI/CD

### Repository-Strategie
Monorepo:
- apps/web
- apps/mobile (später)
- packages/ui
- packages/content
- packages/events
- packages/config
- supabase/functions
- supabase/migrations
- ops/ci
- ops/policies

### Pipeline
- lint
- typecheck
- unit tests
- build
- dependency audit
- secret scan
- RLS-/integration tests
- content checks
- smoke tests
- staging deploy
- production release via Tag/Gate

## Security

1. TLS überall
2. CSP
3. serverseitige Rechteprüfung
4. MFA für Admin/CI/Cloud
5. Secrets nur in Secret Store
6. Storage-Policies
7. Audit Logs
8. Webhook-Signaturprüfung
9. Signed URLs
10. Backup-/Restore-Konzept

## Integrationen

### Release 1
- Formularquellen / Landingpages
- Resend oder vergleichbarer Mail-Provider
- Stripe
- PayPal (wenn wirtschaftlich freigegeben)
- Calendly
- WhatsApp/Twilio optional nach Budgetfreigabe

### Später
- externe LMS
- zusätzliche Messaging-Kanäle
- DATEV-/Steuerexport
- Embassy Monitoring

## Bot-/Sync-/Job-Logik

### MVP
- keine dekorativen Bots,
- nur nützliche Assistenz:
  - FAQ-/Wissensverweise,
  - kontextbezogene Hilfe,
  - keine generischen Antworten.

### Sync-/Job-Grundsätze
- jeder Job protokolliert,
- Retry/Backoff,
- Idempotenz,
- manuelle Wiederholung möglich,
- klare Fehlersicht.

## Architekturentscheidung

### Verifiziert
- Supabase, Next.js, RLS, Storage, Edge Functions und Queue-Ansatz passen zur Projektlage.
- Applicant Portal, Staff Portal und Public Site gehören in eine konsistente, geteilte Codebasis.

### Plausibel abgeleitet
- Release 1 als ein Monorepo mit einer Web-App und klarer Route-/Role-Struktur,
- PWA statt nativer App,
- CMS zunächst schlank, später redaktionell ausbaubar,
- n8n nur ergänzend, nicht als Kernlogik.

## No-Go-Punkte

1. UI-only access control
2. synchrone PDF-/Provider-Calls im Nutzerrequest
3. Zahlungslogik ohne Ledger
4. Multi-Workspace ohne saubere RLS-Tests
5. operative SOT außerhalb der Plattform
