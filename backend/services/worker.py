"""
Background Worker – AsyncIO-basierter Job-Processor.

Laeuft als Background-Task im FastAPI-Prozess.
Pollt MongoDB periodisch nach ausfuehrbaren Jobs.
Verarbeitet Jobs ueber die registrierten Handler.

Features:
- Graceful Shutdown via Event
- Stale-Job-Recovery
- Konfigurierbares Poll-Intervall
- Strukturiertes Logging ohne Secrets
- Health-Check Endpunkt
"""
import asyncio
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Worker-Status
_worker_state = {
    "running": False,
    "started_at": None,
    "last_poll": None,
    "jobs_processed": 0,
    "jobs_failed": 0,
    "last_error": None,
    "current_job": None,
}

# Shutdown Event
_shutdown_event = asyncio.Event()

POLL_INTERVAL_SECONDS = 3
RECOVERY_INTERVAL_SECONDS = 60
MAX_CONSECUTIVE_ERRORS = 10


def get_worker_health() -> dict:
    """Gibt den aktuellen Worker-Zustand fuer Health-Checks zurueck."""
    return {
        **_worker_state,
        "is_healthy": _worker_state["running"] and (
            _worker_state.get("consecutive_errors", 0) < MAX_CONSECUTIVE_ERRORS
        ),
    }


async def start_worker():
    """Startet den Background-Worker als AsyncIO-Task."""
    from services.job_queue import ensure_indexes
    await ensure_indexes()

    _worker_state["running"] = True
    _worker_state["started_at"] = datetime.now(timezone.utc).isoformat()

    logger.info("[WORKER] Background-Worker gestartet")

    # Importiere Handler-Modul damit alle Handler registriert werden
    import services.job_handlers  # noqa: F401

    # Starte Worker-Loop und Recovery parallel
    loop_task = asyncio.create_task(_worker_loop())
    recovery_task = asyncio.create_task(_recovery_loop())

    try:
        await asyncio.gather(loop_task, recovery_task)
    except asyncio.CancelledError:
        logger.info("[WORKER] Worker gestoppt")
    finally:
        _worker_state["running"] = False


async def stop_worker():
    """Signalisiert dem Worker, sich sauber zu beenden."""
    _shutdown_event.set()
    logger.info("[WORKER] Shutdown signalisiert")


async def _worker_loop():
    """Haupt-Verarbeitungsschleife: Pollt und verarbeitet Jobs."""
    from services.job_queue import claim_next, complete_job, fail_job
    from services.job_handlers import HANDLER_REGISTRY

    consecutive_errors = 0

    while not _shutdown_event.is_set():
        try:
            job = await claim_next()
            _worker_state["last_poll"] = datetime.now(timezone.utc).isoformat()

            if not job:
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                continue

            job_id = job.get("job_id", "?")
            job_type = job.get("job_type", "unknown")
            _worker_state["current_job"] = {"job_id": job_id, "job_type": job_type}

            handler = HANDLER_REGISTRY.get(job_type)
            if not handler:
                await fail_job(job_id, f"Kein Handler fuer Job-Typ '{job_type}'", retry=False)
                _worker_state["jobs_failed"] += 1
                _worker_state["current_job"] = None
                continue

            try:
                result = await asyncio.wait_for(handler(job), timeout=300)
                await complete_job(job_id, result)
                _worker_state["jobs_processed"] += 1
                consecutive_errors = 0
            except asyncio.TimeoutError:
                await fail_job(job_id, "Handler-Timeout nach 300s")
                _worker_state["jobs_failed"] += 1
            except Exception as e:
                error_msg = str(e)[:500]
                logger.error(f"[WORKER] Job {job_id} ({job_type}) fehlgeschlagen: {error_msg}")
                await fail_job(job_id, error_msg)
                _worker_state["jobs_failed"] += 1
                consecutive_errors += 1

            _worker_state["current_job"] = None
            _worker_state["consecutive_errors"] = consecutive_errors

            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                logger.critical(f"[WORKER] {MAX_CONSECUTIVE_ERRORS} Fehler in Folge – Worker pausiert 30s")
                _worker_state["last_error"] = "Zu viele Fehler in Folge"
                await asyncio.sleep(30)
                consecutive_errors = 0

        except Exception as e:
            logger.error(f"[WORKER] Loop-Fehler: {e}")
            _worker_state["last_error"] = str(e)[:200]
            await asyncio.sleep(POLL_INTERVAL_SECONDS * 2)


async def _recovery_loop():
    """Periodische Recovery: Stale Jobs zuruecksetzen."""
    from services.job_queue import recover_stale_jobs

    while not _shutdown_event.is_set():
        try:
            await asyncio.sleep(RECOVERY_INTERVAL_SECONDS)
            count = await recover_stale_jobs()
            if count > 0:
                logger.info(f"[WORKER] Recovery: {count} stale Jobs zurueckgesetzt")
        except Exception as e:
            logger.error(f"[WORKER] Recovery-Fehler: {e}")
