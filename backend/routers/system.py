"""
Audit & system routers: audit logs, dashboard stats, health, consent, notifications.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, HTTPException
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


@dashboard_router.get("/dashboard/applicant-summary")
async def dashboard_applicant_summary(user: dict = Depends(get_current_user)):
    if user["role"] != "applicant":
        raise HTTPException(status_code=403, detail="Only applicants can access applicant dashboard summary")

    db = get_db()
    apps = await db.applications.find({"applicant_id": user["id"]}).sort("created_at", -1).to_list(20)
    app_ids = [str(a["_id"]) for a in apps]
    required_doc_types = {
        "passport",
        "school_certificate",
        "language_certificate",
        "photo",
        "birth_certificate",
    }

    docs = await db.documents.find(
        {"application_id": {"$in": app_ids}},
        {"application_id": 1, "document_type": 1, "status": 1},
    ).to_list(300)
    docs_in_review = sum(1 for d in docs if d.get("status") in {"uploaded", "in_review"})
    docs_accepted = sum(1 for d in docs if d.get("status") == "approved")

    provided_required = set()
    for d in docs:
        doc_type = d.get("document_type")
        if doc_type in required_doc_types and d.get("status") in {"uploaded", "in_review", "approved"}:
            provided_required.add(doc_type)
    docs_missing = max(0, len(required_doc_types) - len(provided_required))

    convs = await db.conversations.find({"participants": user["id"]}, {"_id": 1}).to_list(100)
    conv_ids = [str(c["_id"]) for c in convs]
    unread_messages = 0
    open_conversations = 0
    if conv_ids:
        unread_messages = await db.messages.count_documents({
            "conversation_id": {"$in": conv_ids},
            "sender_id": {"$ne": user["id"]},
            "read": {"$ne": True},
        })
        open_conversations = len(await db.messages.distinct(
            "conversation_id",
            {
                "conversation_id": {"$in": conv_ids},
                "sender_id": {"$ne": user["id"]},
                "read": {"$ne": True},
            }
        ))

    invoices = await db.invoices.find(
        {"applicant_id": user["id"]},
        {"status": 1},
    ).to_list(200)
    open_invoice_statuses = {"draft", "sent", "overdue", "pending", "open"}
    open_invoices = sum(1 for i in invoices if (i.get("status") or "").lower() in open_invoice_statuses)
    paid_invoices = sum(1 for i in invoices if (i.get("status") or "").lower() == "paid")

    tasks = await db.tasks.find(
        {"application_id": {"$in": app_ids}, "status": "open", "visibility": "public"},
        {"title": 1, "priority": 1, "due_date": 1},
    ).to_list(200)
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    tasks_sorted = sorted(
        tasks,
        key=lambda t: (
            priority_rank.get((t.get("priority") or "").lower(), 9),
            t.get("due_date") is None,
            t.get("due_date") or datetime.max.replace(tzinfo=timezone.utc),
        ),
    )
    next_actions = []
    for task in tasks_sorted[:3]:
        next_actions.append({
            "type": "task",
            "title": task.get("title") or "Open task",
            "priority": (task.get("priority") or "medium").lower(),
            "due_date": task.get("due_date").isoformat() if hasattr(task.get("due_date"), "isoformat") else None,
        })

    if docs_missing > 0 and len(next_actions) < 3:
        next_actions.append({
            "type": "documents",
            "title": f"{docs_missing} required document(s) missing",
            "priority": "high",
            "due_date": None,
        })
    if open_invoices > 0 and len(next_actions) < 3:
        next_actions.append({
            "type": "financials",
            "title": f"{open_invoices} invoice(s) need attention",
            "priority": "high",
            "due_date": None,
        })
    if unread_messages > 0 and len(next_actions) < 3:
        next_actions.append({
            "type": "messages",
            "title": f"{unread_messages} unread support message(s)",
            "priority": "medium",
            "due_date": None,
        })

    return {
        "applications": len(apps),
        "documents": {
            "missing": docs_missing,
            "in_review": docs_in_review,
            "accepted": docs_accepted,
        },
        "messages": {
            "unread": unread_messages,
            "open": open_conversations,
        },
        "financials": {
            "open_invoices": open_invoices,
            "paid": paid_invoices,
        },
        "tasks": {
            "open": len(tasks),
            "next_actions": next_actions,
        },
        "stages": [{"stage": a.get("current_stage"), "id": str(a["_id"])} for a in apps],
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
