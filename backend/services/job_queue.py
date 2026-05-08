"""
Background Job Queue – MongoDB-basierte asynchrone Verarbeitung.

Architekturentscheidung (ADR-003):
- MongoDB als Job-Store statt Redis+ARQ/Celery
- Begruendung: Redis nicht verfuegbar, MongoDB bereits primaerer Datastore,
  atomare findOneAndUpdate-Operationen fuer Job-Claiming,
  TTL-Indexes fuer Cleanup, Single-Process AsyncIO Worker

Job-Statusmaschine:
  queued -> running -> succeeded
                   -> failed -> retry_scheduled -> queued (begrenzt)
                             -> dead_letter (max_retries erreicht)
  queued -> cancelled

Idempotenz:
- dedupe_key verhindert Duplikate innerhalb eines Zeitfensters
- Erneuter Trigger mit gleichem dedupe_key aktualisiert statt dupliziert
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

# Konfiguration
DEFAULT_MAX_RETRIES = 3
RETRY_DELAYS = [30, 120, 600]  # Sekunden: 30s, 2min, 10min
DEDUPE_WINDOW_HOURS = 1
JOB_TIMEOUT_MINUTES = 10

VALID_STATUSES = (
    "queued", "running", "succeeded", "failed",
    "retry_scheduled", "dead_letter", "cancelled",
)

JOB_TYPES = (
    "ai_screening", "delta_rescreening", "email_send",
    "notification_create", "document_validation",
    "queue_followup", "inactivity_reminder",
    "pdf_export", "cleanup", "batch_screening",
)


async def ensure_indexes():
    """Erstellt Indexes fuer die background_jobs Collection."""
    db = get_db()
    await db.background_jobs.create_index("status")
    await db.background_jobs.create_index("job_type")
    await db.background_jobs.create_index("dedupe_key")
    await db.background_jobs.create_index("created_at")
    await db.background_jobs.create_index("scheduled_at")
    await db.background_jobs.create_index(
        [("status", 1), ("scheduled_at", 1), ("priority_order", 1)],
        name="idx_claim_queue",
    )
    logger.info("[JOB_QUEUE] Indexes erstellt")


async def enqueue(
    job_type: str,
    payload: dict,
    dedupe_key: Optional[str] = None,
    related_entity_type: str = "",
    related_entity_id: str = "",
    actor_id: str = "system",
    workspace_id: str = "",
    priority: str = "normal",
    max_retries: int = DEFAULT_MAX_RETRIES,
    delay_seconds: int = 0,
) -> dict:
    """
    Erstellt einen neuen Job in der Queue.

    Idempotenz: Wenn dedupe_key gesetzt und ein offener/laufender Job
    mit gleichem Key existiert, wird kein neuer erstellt.

    Returns: {"job_id": ..., "status": "queued"|"dedupe_skipped", ...}
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    # Deduplikation
    if dedupe_key:
        cutoff = now - timedelta(hours=DEDUPE_WINDOW_HOURS)
        existing = await db.background_jobs.find_one({
            "dedupe_key": dedupe_key,
            "status": {"$in": ["queued", "running", "retry_scheduled"]},
            "created_at": {"$gte": cutoff.isoformat()},
        })
        if existing:
            logger.info(f"[JOB_QUEUE] Dedupe: Job {dedupe_key} existiert bereits")
            return {
                "job_id": str(existing.get("job_id", "")),
                "status": "dedupe_skipped",
                "existing_status": existing.get("status"),
            }

    priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}.get(priority, 2)
    scheduled_at = (now + timedelta(seconds=delay_seconds)).isoformat() if delay_seconds > 0 else now.isoformat()

    job_id = str(uuid.uuid4())[:12]
    correlation_id = str(uuid.uuid4())[:8]

    # Payload sanitizen: keine Secrets
    safe_payload = _sanitize_payload(payload)

    job = {
        "job_id": job_id,
        "job_type": job_type,
        "status": "queued",
        "priority": priority,
        "priority_order": priority_order,
        "dedupe_key": dedupe_key or "",
        "related_entity_type": related_entity_type,
        "related_entity_id": related_entity_id,
        "actor_id": actor_id,
        "workspace_id": workspace_id,
        "payload": safe_payload,
        "result": None,
        "error_summary": None,
        "retry_count": 0,
        "max_retries": max_retries,
        "correlation_id": correlation_id,
        "created_at": now.isoformat(),
        "queued_at": now.isoformat(),
        "scheduled_at": scheduled_at,
        "started_at": None,
        "finished_at": None,
        "failed_at": None,
        "cancelled_at": None,
        "duration_ms": None,
    }

    await db.background_jobs.insert_one(job)
    logger.info(f"[JOB_QUEUE] Enqueued: {job_type} [{job_id}] prio={priority} dedupe={dedupe_key or 'none'}")

    return {"job_id": job_id, "status": "queued", "correlation_id": correlation_id}


async def claim_next() -> Optional[dict]:
    """
    Beansprucht den naechsten ausfuehrbaren Job (atomar).
    Setzt Status auf 'running' und started_at.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    job = await db.background_jobs.find_one_and_update(
        {
            "status": {"$in": ["queued", "retry_scheduled"]},
            "scheduled_at": {"$lte": now.isoformat()},
        },
        {
            "$set": {
                "status": "running",
                "started_at": now.isoformat(),
            },
        },
        sort=[("priority_order", 1), ("scheduled_at", 1)],
        return_document=True,
    )

    if job:
        job_id = job.get("job_id", "?")
        logger.info(f"[JOB_QUEUE] Claimed: {job.get('job_type')} [{job_id}]")
        # ObjectId entfernen
        result = dict(job)
        result["_mongo_id"] = str(result.pop("_id"))
        return result

    return None


async def complete_job(job_id: str, result_data: dict = None):
    """Markiert einen Job als erfolgreich abgeschlossen."""
    db = get_db()
    now = datetime.now(timezone.utc)

    job = await db.background_jobs.find_one({"job_id": job_id})
    started = job.get("started_at", now.isoformat()) if job else now.isoformat()

    try:
        started_dt = datetime.fromisoformat(started)
        duration_ms = int((now - started_dt).total_seconds() * 1000)
    except Exception:
        duration_ms = 0

    await db.background_jobs.update_one(
        {"job_id": job_id},
        {"$set": {
            "status": "succeeded",
            "finished_at": now.isoformat(),
            "duration_ms": duration_ms,
            "result": _sanitize_payload(result_data) if result_data else None,
        }},
    )
    logger.info(f"[JOB_QUEUE] Completed: [{job_id}] in {duration_ms}ms")


async def fail_job(job_id: str, error: str, retry: bool = True):
    """
    Markiert einen Job als fehlgeschlagen.
    Bei retry=True und verbleibenden Versuchen: retry_scheduled.
    Sonst: dead_letter.
    """
    db = get_db()
    now = datetime.now(timezone.utc)

    job = await db.background_jobs.find_one({"job_id": job_id})
    if not job:
        return

    retry_count = job.get("retry_count", 0)
    max_retries = job.get("max_retries", DEFAULT_MAX_RETRIES)

    if retry and retry_count < max_retries:
        delay_idx = min(retry_count, len(RETRY_DELAYS) - 1)
        delay = RETRY_DELAYS[delay_idx]
        scheduled = now + timedelta(seconds=delay)

        await db.background_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "retry_scheduled",
                "failed_at": now.isoformat(),
                "error_summary": str(error)[:500],
                "retry_count": retry_count + 1,
                "scheduled_at": scheduled.isoformat(),
            }},
        )
        logger.warning(f"[JOB_QUEUE] Retry scheduled: [{job_id}] attempt {retry_count + 1}/{max_retries} in {delay}s")
    else:
        await db.background_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": "dead_letter",
                "failed_at": now.isoformat(),
                "finished_at": now.isoformat(),
                "error_summary": str(error)[:500],
            }},
        )
        logger.error(f"[JOB_QUEUE] Dead letter: [{job_id}] nach {retry_count} Versuchen: {error[:200]}")


async def cancel_job(job_id: str, cancelled_by: str = "system"):
    """Bricht einen wartenden Job ab."""
    db = get_db()
    now = datetime.now(timezone.utc)

    result = await db.background_jobs.update_one(
        {"job_id": job_id, "status": {"$in": ["queued", "retry_scheduled"]}},
        {"$set": {
            "status": "cancelled",
            "cancelled_at": now.isoformat(),
            "error_summary": f"Abgebrochen durch {cancelled_by}",
        }},
    )
    if result.modified_count > 0:
        logger.info(f"[JOB_QUEUE] Cancelled: [{job_id}] by {cancelled_by}")
    return result.modified_count > 0


async def retry_job(job_id: str, retried_by: str = "system"):
    """Setzt einen fehlgeschlagenen Job zurueck in die Queue."""
    db = get_db()
    now = datetime.now(timezone.utc)

    result = await db.background_jobs.update_one(
        {"job_id": job_id, "status": {"$in": ["failed", "dead_letter"]}},
        {"$set": {
            "status": "queued",
            "scheduled_at": now.isoformat(),
            "error_summary": None,
            "failed_at": None,
        }},
    )
    if result.modified_count > 0:
        logger.info(f"[JOB_QUEUE] Re-queued: [{job_id}] by {retried_by}")
    return result.modified_count > 0


async def get_stats() -> dict:
    """Job-Queue-Statistiken fuer Monitoring/Dashboard."""
    db = get_db()
    now = datetime.now(timezone.utc)
    one_hour_ago = (now - timedelta(hours=1)).isoformat()
    one_day_ago = (now - timedelta(hours=24)).isoformat()

    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    status_counts = {}
    async for doc in db.background_jobs.aggregate(pipeline):
        status_counts[doc["_id"]] = doc["count"]

    # Job-Typ-Verteilung (letzte 24h)
    type_pipeline = [
        {"$match": {"created_at": {"$gte": one_day_ago}}},
        {"$group": {"_id": "$job_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    type_counts = {}
    async for doc in db.background_jobs.aggregate(type_pipeline):
        type_counts[doc["_id"]] = doc["count"]

    # Fehlerrate letzte Stunde
    recent_total = await db.background_jobs.count_documents({"created_at": {"$gte": one_hour_ago}})
    recent_failed = await db.background_jobs.count_documents({
        "created_at": {"$gte": one_hour_ago},
        "status": {"$in": ["failed", "dead_letter"]},
    })

    # Letzte Fehler
    recent_errors = await db.background_jobs.find(
        {"status": {"$in": ["failed", "dead_letter"]}},
        {"_id": 0, "job_id": 1, "job_type": 1, "error_summary": 1, "failed_at": 1, "retry_count": 1},
    ).sort("failed_at", -1).to_list(5)

    # Durchschnittliche Laufzeit (letzte Stunde, nur succeeded)
    dur_pipeline = [
        {"$match": {"status": "succeeded", "created_at": {"$gte": one_hour_ago}, "duration_ms": {"$ne": None}}},
        {"$group": {"_id": None, "avg_ms": {"$avg": "$duration_ms"}, "max_ms": {"$max": "$duration_ms"}}},
    ]
    dur_result = await db.background_jobs.aggregate(dur_pipeline).to_list(1)
    avg_duration = dur_result[0]["avg_ms"] if dur_result else 0
    max_duration = dur_result[0]["max_ms"] if dur_result else 0

    return {
        "total": sum(status_counts.values()),
        "by_status": status_counts,
        "queued": status_counts.get("queued", 0) + status_counts.get("retry_scheduled", 0),
        "running": status_counts.get("running", 0),
        "succeeded": status_counts.get("succeeded", 0),
        "failed": status_counts.get("failed", 0),
        "dead_letter": status_counts.get("dead_letter", 0),
        "cancelled": status_counts.get("cancelled", 0),
        "by_type_24h": type_counts,
        "error_rate_1h": round(recent_failed / max(recent_total, 1) * 100, 1),
        "recent_errors": recent_errors,
        "avg_duration_ms": round(avg_duration),
        "max_duration_ms": round(max_duration),
    }


async def recover_stale_jobs():
    """
    Recovery: Jobs die laenger als JOB_TIMEOUT_MINUTES im 'running'-Status
    haengen, werden als failed zurueckgesetzt.
    """
    db = get_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=JOB_TIMEOUT_MINUTES)).isoformat()

    result = await db.background_jobs.update_many(
        {"status": "running", "started_at": {"$lte": cutoff}},
        {"$set": {
            "status": "failed",
            "error_summary": f"Timeout nach {JOB_TIMEOUT_MINUTES} Minuten – Worker-Recovery",
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }},
    )
    if result.modified_count > 0:
        logger.warning(f"[JOB_QUEUE] Recovery: {result.modified_count} stale Jobs zurueckgesetzt")
    return result.modified_count


def _sanitize_payload(data: dict) -> dict:
    """Entfernt sensible Felder aus dem Payload."""
    if not data:
        return {}
    sensitive_keys = {
        "password", "secret", "token", "api_key", "apikey",
        "smtp_password", "imap_password", "access_token",
        "refresh_token", "private_key", "credential",
    }
    result = {}
    for k, v in data.items():
        lower_k = k.lower()
        if any(sk in lower_k for sk in sensitive_keys):
            result[k] = "***REDACTED***"
        elif isinstance(v, dict):
            result[k] = _sanitize_payload(v)
        else:
            result[k] = v
    return result
