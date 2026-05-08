# 2026-04-03 – Async Job Queue / Worker-Architektur

## Kontext
Synchrone Verarbeitung von KI-Screening, E-Mail-Versand und Folgeprozessen
fuehrte zu Timeout-Risiken und mangelnder Fehlerbehandlung. Die Plattform
benoetigt eine belastbare asynchrone Verarbeitungsarchitektur.

## Architekturentscheidung (ADR-003)
MongoDB-basierte Async-Job-Queue statt Redis+ARQ/Celery.
Begruendung: Redis nicht verfuegbar, MongoDB bereits Datastore,
atomare findOneAndUpdate fuer Job-Claiming.

## Neue Dateien
- /app/backend/services/job_queue.py (Kern-Queue: Enqueue/Claim/Complete/Fail/Retry/Stats)
- /app/backend/services/worker.py (AsyncIO Worker mit Recovery)
- /app/backend/services/job_handlers.py (Handler-Registry pro Job-Typ)
- /app/backend/routers/jobs.py (Admin-API: Stats/Health/List/Retry/Cancel)
- /app/frontend/src/pages/admin/AdminJobsPage.js (Monitoring Dashboard)
- /app/docs/adr/ADR-003-mongodb-async-job-queue.md

## Geaenderte Dateien
- /app/backend/server.py (Worker-Start/Stop, Router-Registrierung)
- /app/backend/routers/ai_screening.py (Neuer Endpoint: ai-screen-async)
- /app/backend/routers/documents.py (Re-Screening ueber Queue statt asyncio.ensure_future)
- /app/backend/services/automation.py (E-Mail-Versand ueber Queue)
- /app/frontend/src/App.js (AdminJobsPage Route)
- /app/frontend/src/components/layout/AdminLayout.js (Jobs Nav-Eintrag)

## Asynchron umgestellte Prozesse
1. Delta Re-Screening nach Dokument-Upload
2. E-Mail: Bewerbungseingang
3. E-Mail: Dokumentennachforderung
4. E-Mail: Status-Aenderung
5. KI-Screening (optionaler async Endpoint)

## Testing
- Iteration 41: 100% Backend (29/29), 100% Frontend
