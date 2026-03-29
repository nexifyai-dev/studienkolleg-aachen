"""
Audit & system routers: audit logs, dashboard stats, health, consent, notifications.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request
from database import get_db
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES
from models.schemas import ConsentCapture, to_str_id
from bson import ObjectId

# ─── Audit Router ─────────────────────────────────────────────────────────────
audit_router = APIRouter(prefix="/api", tags=["audit"])


@audit_router.get("/audit-logs")
async def get_audit_logs(request: Request, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    db = get_db()
    query = {}
    if tid := request.query_params.get("target_id"):
        query["target_id"] = tid
    if aid := request.query_params.get("actor_id"):
        query["actor_id"] = aid
    logs = await db.audit_logs.find(query).sort("occurred_at", -1).to_list(500)
    return [to_str_id(log) for log in logs]


# ─── Dashboard Router ─────────────────────────────────────────────────────────
dashboard_router = APIRouter(prefix="/api", tags=["dashboard"])


@dashboard_router.get("/dashboard/stats")
async def dashboard_stats(user: dict = Depends(get_current_user)):
    db = get_db()
    if user["role"] == "applicant":
        apps = await db.applications.find({"applicant_id": user["id"]}).to_list(20)
        open_tasks = await db.tasks.count_documents({
            "application_id": {"$in": [str(a["_id"]) for a in apps]},
            "status": "open",
            "visibility": "public",
        })
        return {
            "applications": len(apps),
            "open_tasks": open_tasks,
            "stages": [{"stage": a.get("current_stage"), "id": str(a["_id"])} for a in apps],
        }
    else:
        total_leads = await db.applications.count_documents({})
        open_leads = await db.applications.count_documents({"current_stage": {"$nin": ["completed", "archived"]}})
        open_tasks = await db.tasks.count_documents({"status": "open"})
        pending_docs = await db.documents.count_documents({"status": "uploaded"})
        return {
            "total_leads": total_leads,
            "open_leads": open_leads,
            "open_tasks": open_tasks,
            "pending_documents": pending_docs,
        }


# ─── Notifications Router (legacy – kept for backward compat, new router handles /api/notifications) ─
notif_router = APIRouter(prefix="/api", tags=["notifications-legacy"])


@notif_router.post("/consent")
async def capture_consent(data: ConsentCapture, user: dict = Depends(get_current_user)):
    db = get_db()
    await db.user_consents.update_one(
        {"user_id": user["id"], "consent_type": data.consent_type},
        {"$set": {
            "version": data.version,
            "granted": data.granted,
            "recorded_at": datetime.now(timezone.utc),
            "user_id": user["id"],
            "consent_type": data.consent_type,
        }},
        upsert=True,
    )
    return {"message": "Einwilligung gespeichert"}


# ─── Health Router ────────────────────────────────────────────────────────────
system_router = APIRouter(prefix="/api", tags=["system"])


@system_router.get("/health")
async def health():
    from config import EMAIL_ENABLED, STORAGE_BACKEND
    return {
        "status": "ok",
        "service": "W2G Platform API",
        "version": "1.1.0",
        "email_enabled": EMAIL_ENABLED,
        "storage_backend": STORAGE_BACKEND,
    }
