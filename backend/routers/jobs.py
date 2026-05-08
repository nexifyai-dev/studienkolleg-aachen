"""
Jobs Admin Router – Monitoring, Retry, Cancel fuer Background-Jobs.
Prefix: /api/jobs
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from database import get_db
from deps import require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["jobs-admin"])

ADMIN_ROLES = ("superadmin", "admin")
STAFF_ROLES = ("superadmin", "admin", "staff")


def _str_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


@router.get("/stats")
async def get_job_stats(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Job-Queue-Statistiken fuer Dashboard und Monitoring."""
    from services.job_queue import get_stats
    return await get_stats()


@router.get("/health")
async def get_worker_health(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Worker Health-Check."""
    from services.worker import get_worker_health
    return get_worker_health()


@router.get("")
async def list_jobs(
    status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Jobs auflisten mit Filter und Pagination."""
    db = get_db()
    query = {}

    if status:
        query["status"] = status
    if job_type:
        query["job_type"] = job_type
    if q:
        query["$or"] = [
            {"job_id": {"$regex": q, "$options": "i"}},
            {"related_entity_id": {"$regex": q, "$options": "i"}},
            {"error_summary": {"$regex": q, "$options": "i"}},
        ]

    total = await db.background_jobs.count_documents(query)
    jobs_raw = await db.background_jobs.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    jobs = [_str_id(dict(j)) for j in jobs_raw]

    return {"jobs": jobs, "total": total, "skip": skip, "limit": limit}


@router.get("/{job_id}")
async def get_job(job_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Einzelnen Job abrufen."""
    db = get_db()
    job = await db.background_jobs.find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    return _str_id(dict(job))


@router.post("/{job_id}/retry")
async def retry_job(job_id: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Fehlgeschlagenen Job erneut in die Queue stellen."""
    from services.job_queue import retry_job as do_retry
    from services.audit import write_audit_log

    success = await do_retry(job_id, retried_by=user.get("email", user["id"]))
    if not success:
        raise HTTPException(status_code=400, detail="Job kann nicht erneut gestartet werden (nur failed/dead_letter)")

    await write_audit_log(
        "job_retried", user["id"], "background_job", job_id,
        {"retried_by": user.get("email", user["id"])},
    )
    return {"retried": True, "job_id": job_id}


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Wartenden Job abbrechen."""
    from services.job_queue import cancel_job as do_cancel
    from services.audit import write_audit_log

    success = await do_cancel(job_id, cancelled_by=user.get("email", user["id"]))
    if not success:
        raise HTTPException(status_code=400, detail="Job kann nicht abgebrochen werden (nur queued/retry_scheduled)")

    await write_audit_log(
        "job_cancelled", user["id"], "background_job", job_id,
        {"cancelled_by": user.get("email", user["id"])},
    )
    return {"cancelled": True, "job_id": job_id}
