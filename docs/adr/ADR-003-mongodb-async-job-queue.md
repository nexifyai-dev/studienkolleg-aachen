# ADR-003: MongoDB-basierte Async-Job-Queue

## Status
Akzeptiert (2026-04-03)

## Kontext
Die Plattform verarbeitet geschaeftskritische Hintergrundprozesse
(KI-Screening, E-Mail-Versand, Delta-Re-Screening, Notifications)
bisher synchron im Request-Thread. Bei Last drohen Timeouts und
Instabilitaet.

## Entscheidung
MongoDB-basierte Async-Job-Queue statt Redis+ARQ/Celery.

### Begruendung
1. Redis ist in der Deployment-Umgebung nicht verfuegbar
2. MongoDB ist bereits primaerer Datastore (kein neuer Infra-Overhead)
3. Atomare findOneAndUpdate-Operationen fuer Job-Claiming
4. TTL-Indexes fuer automatisches Cleanup
5. Single-Process AsyncIO Worker passt zum FastAPI-Deployment-Modell
6. Kein Distributed-Worker-Bedarf bei aktueller Last

### Trade-offs
- Polling statt Push (3s Intervall, akzeptabel fuer aktuelle Last)
- Kein Multi-Node-Worker (bei Skalierung: Migration zu Redis+ARQ)
- MongoDB-Write-Last durch Job-Collection (minimal bei aktuellem Volumen)

## Komponenten
- `services/job_queue.py`: Enqueue, Claim, Complete, Fail, Retry, Stats
- `services/worker.py`: AsyncIO Background Worker mit Recovery
- `services/job_handlers.py`: Handler-Registry pro Job-Typ
- `routers/jobs.py`: Admin-API fuer Monitoring/Retry/Cancel
- Collection: `background_jobs` mit Indexes

## Status-Maschine
```
queued -> running -> succeeded
                 -> failed -> retry_scheduled -> queued (begrenzt)
                           -> dead_letter (max_retries erreicht)
queued -> cancelled
```

## Folgen
- E-Mail, Screening, Notifications nicht mehr synchron blockierend
- Retry mit exponentiellem Backoff (30s, 2min, 10min)
- Idempotenz via dedupe_key
- Dead-Letter-Sichtbarkeit fuer Admin
- Payload-Sanitization (keine Secrets in Jobs)
- Stale-Job-Recovery alle 60s
