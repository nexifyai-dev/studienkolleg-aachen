"""
Scheduler – Periodische Systemaufgaben.

Laeuft als zweiter Background-Task neben dem Worker.
Fuehrt zeitgesteuerte Aufgaben aus:
- Inaktivitaets-Reminder (taeglich 09:00 UTC)
- Ueberfaellige Aufgaben erkennen (alle 6h)
- Job-Cleanup alter erledigter Jobs (taeglich 03:00 UTC)
- System-Health-Metriken sammeln (alle 5 Minuten)

Alle Aufgaben sind idempotent und audit-geloggt.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from database import get_db

logger = logging.getLogger(__name__)

_scheduler_state = {
    "running": False,
    "started_at": None,
    "last_run": {},
    "runs_total": 0,
    "errors_total": 0,
}

_shutdown_event = asyncio.Event()


def get_scheduler_health() -> dict:
    return {**_scheduler_state, "is_healthy": _scheduler_state["running"]}


async def start_scheduler():
    """Startet den Scheduler als AsyncIO-Task."""
    _scheduler_state["running"] = True
    _scheduler_state["started_at"] = datetime.now(timezone.utc).isoformat()
    logger.info("[SCHEDULER] Gestartet")

    tasks = [
        asyncio.create_task(_run_periodic("inactivity_check", 3600 * 12, _check_inactivity)),
        asyncio.create_task(_run_periodic("overdue_tasks", 3600 * 6, _check_overdue_tasks)),
        asyncio.create_task(_run_periodic("job_cleanup", 3600 * 24, _cleanup_old_jobs)),
        asyncio.create_task(_run_periodic("health_metrics", 300, _collect_health_metrics)),
        asyncio.create_task(_run_periodic("dunning_check", 3600 * 12, _check_dunning)),
        asyncio.create_task(_run_periodic("brain_email_poll", 600, _poll_brain_emails)),
        asyncio.create_task(_run_periodic("nightly_backup", 3600 * 24, _run_nightly_backup)),
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("[SCHEDULER] Gestoppt")
    finally:
        _scheduler_state["running"] = False


async def stop_scheduler():
    _shutdown_event.set()


async def _run_periodic(name: str, interval_seconds: int, func):
    """Fuehrt eine Funktion periodisch aus."""
    # Initiales Delay um Startup nicht zu blockieren
    await asyncio.sleep(30)
    while not _shutdown_event.is_set():
        try:
            await func()
            _scheduler_state["last_run"][name] = datetime.now(timezone.utc).isoformat()
            _scheduler_state["runs_total"] += 1
        except Exception as e:
            _scheduler_state["errors_total"] += 1
            logger.error(f"[SCHEDULER] {name} fehlgeschlagen: {e}")
        try:
            await asyncio.wait_for(_shutdown_event.wait(), timeout=interval_seconds)
            break
        except asyncio.TimeoutError:
            pass


async def _check_inactivity():
    """Prueft Bewerbungen auf Inaktivitaet (>5 Tage keine Aenderung)."""
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(days=5)

    inactive_apps = await db.applications.find({
        "current_stage": {"$in": ["lead_new", "in_review", "pending_docs"]},
        "updated_at": {"$lt": cutoff},
    }, {"_id": 1, "applicant_id": 1, "applicant_email": 1, "applicant_name": 1, "updated_at": 1}).to_list(50)

    if not inactive_apps:
        logger.info("[SCHEDULER] inactivity_check: Keine inaktiven Bewerbungen")
        return

    from services.job_queue import enqueue

    enqueued = 0
    for app in inactive_apps:
        app_id = str(app["_id"])
        days = (datetime.now(timezone.utc) - app.get("updated_at", cutoff)).days

        # Dedupe: Nur alle 5 Tage erinnern
        await enqueue(
            job_type="inactivity_reminder",
            payload={
                "application_id": app_id,
                "applicant_email": app.get("applicant_email", ""),
                "applicant_name": app.get("applicant_name", ""),
                "applicant_id": str(app.get("applicant_id", "")),
                "days_inactive": days,
            },
            dedupe_key=f"inactivity_{app_id}_{days // 5}",
            related_entity_type="application",
            related_entity_id=app_id,
            priority="low",
        )
        enqueued += 1

    logger.info(f"[SCHEDULER] inactivity_check: {enqueued} Reminder enqueued")


async def _check_overdue_tasks():
    """Erkennt ueberfaellige Aufgaben und benachrichtigt zustaendige Staff."""
    db = get_db()
    now = datetime.now(timezone.utc)

    overdue = await db.tasks.find({
        "status": {"$in": ["open", "in_progress"]},
        "due_date": {"$lt": now},
        "_notified_overdue": {"$ne": True},
    }).to_list(50)

    if not overdue:
        return

    from services.notifications import create_notification

    for task in overdue:
        assignee = task.get("assigned_to")
        title = task.get("title", "Aufgabe")

        if assignee:
            await create_notification(
                assignee, "task_overdue",
                f"Aufgabe ueberfaellig: {title}",
                link="/staff/tasks",
                triggered_by="scheduler",
            )

        await db.tasks.update_one(
            {"_id": task["_id"]},
            {"$set": {"_notified_overdue": True}},
        )

    logger.info(f"[SCHEDULER] overdue_tasks: {len(overdue)} Aufgaben ueberfaellig")


async def _cleanup_old_jobs():
    """Loescht erledigte Jobs aelter als 14 Tage."""
    db = get_db()
    cutoff = datetime.now(timezone.utc) - timedelta(days=14)

    result = await db.background_jobs.delete_many({
        "status": {"$in": ["succeeded", "cancelled"]},
        "created_at": {"$lt": cutoff.isoformat()},
    })

    if result.deleted_count > 0:
        logger.info(f"[SCHEDULER] cleanup: {result.deleted_count} alte Jobs geloescht")


async def _check_dunning():
    """Prueft ueberfaellige Rechnungen und versendet Mahnungen."""
    try:
        from services.dunning import check_overdue_invoices
        await check_overdue_invoices()
    except Exception as e:
        logger.error(f"[SCHEDULER] dunning_check fehlgeschlagen: {e}")


async def _collect_health_metrics():
    """Sammelt System-Health-Metriken und speichert sie."""
    db = get_db()
    now = datetime.now(timezone.utc)

    metrics = {
        "timestamp": now,
        "applications_total": await db.applications.count_documents({}),
        "applications_active": await db.applications.count_documents({
            "current_stage": {"$nin": ["enrolled", "declined", "archived"]}
        }),
        "tasks_open": await db.tasks.count_documents({"status": {"$in": ["open", "in_progress"]}}),
        "tasks_overdue": await db.tasks.count_documents({
            "status": {"$ne": "done"}, "due_date": {"$lt": now}
        }),
        "invoices_unpaid": await db.invoices.count_documents({"status": {"$in": ["draft", "sent", "overdue"]}}),
        "documents_pending": await db.documents.count_documents({"status": {"$in": ["uploaded", "needs_review"]}}),
        "jobs_pending": await db.background_jobs.count_documents({"status": "pending"}),
        "jobs_processing": await db.background_jobs.count_documents({"status": "processing"}),
        "jobs_failed_24h": await db.background_jobs.count_documents({
            "status": "failed",
            "created_at": {"$gte": (now - timedelta(hours=24)).isoformat()},
        }),
        "users_total": await db.users.count_documents({}),
    }

    # Nur letzten Eintrag behalten (Rolling Window)
    await db.system_metrics.delete_many({"timestamp": {"$lt": now - timedelta(hours=1)}})
    await db.system_metrics.insert_one(metrics)



async def _poll_brain_emails():
    """Pollt IMAP und importiert neue E-Mails ins Brain-Memory."""
    try:
        from services.email_brain import poll_inbox
        result = await poll_inbox(max_emails=30, since_days=3)
        logger.info(f"[SCHEDULER:brain_email_poll] Ergebnis: {result}")
    except Exception as e:
        logger.error(f"[SCHEDULER:brain_email_poll] Fehler: {e}")


async def _run_nightly_backup():
    """Führt jede Nacht ein MongoDB-Backup durch (Retention 7 Tage)."""
    try:
        from services.backup import run_backup
        result = await run_backup()
        logger.info(f"[SCHEDULER:nightly_backup] Ergebnis: {result.get('status')}")
    except Exception as e:
        logger.error(f"[SCHEDULER:nightly_backup] Fehler: {e}")
