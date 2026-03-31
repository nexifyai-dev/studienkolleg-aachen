"""
Audit & system routers: audit logs, dashboard stats, health, consent, notifications.
"""
from datetime import datetime, timezone, timedelta
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
        app_ids = [str(a["_id"]) for a in apps]
        open_tasks = await db.tasks.count_documents({
            "application_id": {"$in": app_ids},
            "status": "open",
            "visibility": "public",
        })

        required_doc_types = ["passport", "school_certificate", "language_certificate"]
        uploaded_required_docs = await db.documents.find({
            "application_id": {"$in": app_ids},
            "document_type": {"$in": required_doc_types},
            "status": {"$ne": "rejected"},
        }).to_list(200)
        uploaded_types = {d.get("document_type") for d in uploaded_required_docs}
        missing_documents = [doc_type for doc_type in required_doc_types if doc_type not in uploaded_types]

        convs = await db.conversations.find({"participants": user["id"]}).to_list(50)
        conv_ids = [str(c["_id"]) for c in convs]
        unread_messages = await db.messages.count_documents({
            "conversation_id": {"$in": conv_ids},
            "sender_id": {"$ne": user["id"]},
            "read": {"$ne": True},
        }) if conv_ids else 0

        active_consent = await db.consents.find_one({
            "user_id": user["id"],
            "consent_type": "teacher_data_access",
            "granted": True,
            "revoked_at": None,
        })
        consent_missing = active_consent is None

        due_soon_count = await db.tasks.count_documents({
            "application_id": {"$in": app_ids},
            "status": "open",
            "visibility": "public",
            "due_date": {
                "$gte": datetime.now(timezone.utc),
                "$lte": datetime.now(timezone.utc) + timedelta(days=3),
            },
        })

        return {
            "applications": len(apps),
            "open_tasks": open_tasks,
            "stages": [{"stage": a.get("current_stage"), "id": str(a["_id"])} for a in apps],
            "missing_documents": len(missing_documents),
            "missing_document_types": missing_documents,
            "unread_messages": unread_messages,
            "consent_missing": consent_missing,
            "due_soon_tasks": due_soon_count,
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
