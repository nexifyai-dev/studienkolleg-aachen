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
        in_progress_tasks = await db.tasks.count_documents({"status": "in_progress"})
        pending_docs = await db.documents.count_documents({"status": "uploaded"})

        # Pipeline breakdown by stage
        pipeline_stages = [
            "lead_new", "in_review", "pending_docs", "interview_scheduled",
            "conditional_offer", "offer_sent", "enrolled", "declined", "on_hold",
        ]
        pipeline_counts = {}
        for stage in pipeline_stages:
            pipeline_counts[stage] = await db.applications.count_documents({"current_stage": stage})

        # Recent activity (last 10 audit entries)
        recent_activity = []
        try:
            activities = await db.audit_logs.find({}).sort("occurred_at", -1).to_list(10)
            for a in activities:
                ad = to_str_id(a)
                if hasattr(ad.get("occurred_at"), "isoformat"):
                    ad["occurred_at"] = ad["occurred_at"].isoformat()
                recent_activity.append(ad)
        except Exception:
            pass

        # Unread messages count for staff
        unread_messages = 0
        try:
            unread_messages = await db.messages.count_documents({"read": False, "sender_id": {"$ne": user["id"]}})
        except Exception:
            pass

        # Total users by role
        total_users = await db.users.count_documents({})
        total_staff = await db.users.count_documents({"role": {"$in": ["staff", "admin", "superadmin", "teacher"]}})
        total_applicants = await db.users.count_documents({"role": "applicant"})

        return {
            "total_leads": total_leads,
            "open_leads": open_leads,
            "open_tasks": open_tasks,
            "in_progress_tasks": in_progress_tasks,
            "pending_documents": pending_docs,
            "pipeline": pipeline_counts,
            "recent_activity": recent_activity,
            "unread_messages": unread_messages,
            "total_users": total_users,
            "total_staff": total_staff,
            "total_applicants": total_applicants,
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
        "version": "1.4.0",
        "email_enabled": EMAIL_ENABLED,
        "storage_backend": STORAGE_BACKEND,
    }


# ─── DEMO RESET (Admin only, destructive) ─────────────────────────────────────
# Wipes all operational/mock data while preserving the 5 dev accounts and
# system-essential reference collections. Used to prepare a fresh demo state.
_DEMO_KEEP_USER_EMAILS = frozenset({
    "admin@studienkolleg-aachen.de",
    "staff@studienkolleg-aachen.de",
    "teacher@studienkolleg-aachen.de",
    "applicant@studienkolleg-aachen.de",
    "partner@studienkolleg-aachen.de",
})

_DEMO_WIPE_COLLECTIONS = (
    "applications", "invoices", "documents", "messages", "conversations",
    "notifications", "ai_screenings", "batch_screenings", "anabin_review_queue",
    "application_activities", "appointments", "tasks", "task_history",
    "task_attachments", "task_notes", "payment_transactions",
    "oracle_conversations", "case_notes", "followups", "consents",
    "audit_logs", "background_jobs", "system_metrics", "email_events",
    "login_attempts", "password_reset_tokens", "invite_tokens", "webhook_events",
    "lms_enrollments", "teacher_assignments", "temp_uploads", "user_signatures",
)


@system_router.post("/system/clean-demo-data")
async def clean_demo_data(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Pre-presentation reset: wipe operational data, keep dev accounts + reference data.

    Removes:
      - All non-dev users (mock applicants and their data)
      - Applications, invoices, documents, messages, conversations
      - Notifications, screenings, activities, tasks, payments, audit logs, etc.
      - Local storage files for documents/messages/invoices
      - Counters (so applicant/invoice numbers restart from 1)

    Preserves:
      - 5 dev accounts (admin/staff/teacher/applicant/partner)
      - workspaces, settings, anabin_knowledge
      - brain_emails / brain_email_drafts / brain_memories (real IMAP data)

    Admin-only. Returns a per-collection deletion summary.
    """
    import os
    import shutil

    db = get_db()
    summary: dict = {}

    # 1) Users: keep only dev accounts
    res = await db.users.delete_many({"email": {"$nin": list(_DEMO_KEEP_USER_EMAILS)}})
    summary["users_removed"] = res.deleted_count

    # 2) Wipe operational collections
    existing = set(await db.list_collection_names())
    for col in _DEMO_WIPE_COLLECTIONS:
        if col in existing:
            res = await db[col].delete_many({})
            if res.deleted_count:
                summary[col] = res.deleted_count

    # 3) Reset counters (fresh applicant numbers / invoice numbers)
    await db.counters.delete_many({})
    summary["counters_reset"] = True

    # 4) Wipe local storage files
    storage_root = os.environ.get("LOCAL_STORAGE_PATH", "/app/storage")
    files_removed = 0
    for sub in ("documents", "messages", "invoices"):
        path = os.path.join(storage_root, sub)
        if os.path.isdir(path):
            for entry in os.listdir(path):
                full = os.path.join(path, entry)
                try:
                    if os.path.isdir(full):
                        shutil.rmtree(full, ignore_errors=True)
                    else:
                        os.remove(full)
                    files_removed += 1
                except OSError:
                    pass
    summary["storage_files_removed"] = files_removed

    return {
        "status": "ok",
        "performed_by": user.get("email"),
        "performed_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }


# ─── DEMO SEED (Admin only) ───────────────────────────────────────────────────
# Re-creates 12 realistic demo applicants + 5 staff tasks for presentation/demo
# usage. Idempotent: existing users with the same email are updated, not
# duplicated. Designed for one-click re-seeding via the admin UI after a
# clean-demo-data wipe.

_DEMO_APPLICANTS = [
    {"full_name": "Amira El-Khoury", "email": "amira.elkhoury@gmail.com", "country": "Libanon", "phone": "+961 71 234567"},
    {"full_name": "Yusuf Demir", "email": "yusuf.demir@hotmail.com", "country": "Türkei", "phone": "+90 532 1234567"},
    {"full_name": "Fatima Benali", "email": "fatima.benali@yahoo.com", "country": "Marokko", "phone": "+212 6 12345678"},
    {"full_name": "Chen Wei", "email": "chen.wei@outlook.com", "country": "China", "phone": "+86 138 1234 5678"},
    {"full_name": "Nguyen Thi Lan", "email": "ntlan.nguyen@gmail.com", "country": "Vietnam", "phone": "+84 91 234 5678"},
    {"full_name": "Mohammad Reza Hosseini", "email": "m.hosseini@gmail.com", "country": "Iran", "phone": "+98 912 345 6789"},
    {"full_name": "Priya Sharma", "email": "priya.sharma@gmail.com", "country": "Indien", "phone": "+91 98765 43210"},
    {"full_name": "Carlos Mendoza", "email": "c.mendoza@hotmail.com", "country": "Kolumbien", "phone": "+57 310 1234567"},
    {"full_name": "Olga Petrov", "email": "olga.petrov@mail.ru", "country": "Russland", "phone": "+7 916 123 4567"},
    {"full_name": "Samuel Okafor", "email": "samuel.okafor@gmail.com", "country": "Nigeria", "phone": "+234 803 1234567"},
    {"full_name": "Lina Al-Rashid", "email": "lina.alrashid@gmail.com", "country": "Irak", "phone": "+964 770 1234567"},
    {"full_name": "Ahmed Hassan", "email": "applicant@studienkolleg-aachen.de", "country": "Ägypten", "phone": "+20 100 1234567"},
]

_DEMO_STAGES_DISTRIBUTION = [
    ("lead_new", 3),
    ("in_review", 2),
    ("pending_docs", 2),
    ("interview_scheduled", 1),
    ("conditional_offer", 1),
    ("offer_sent", 1),
    ("enrolled", 1),
]

_DEMO_TASKS = [
    {"title": "Unterlagen von Amira El-Khoury prüfen", "description": "Zeugnis-Übersetzung und Sprachnachweis kontrollieren", "priority": "high", "status": "open"},
    {"title": "Beratungsgespräch Yusuf Demir planen", "description": "Termin für Online-Beratung koordinieren", "priority": "medium", "status": "open"},
    {"title": "Einschreibebestätigung versenden", "description": "Offizielle Bestätigung an Chen Wei senden", "priority": "high", "status": "in_progress"},
    {"title": "Sprachtest-Ergebnis nachverfolgen", "description": "B2-Nachweis von Fatima Benali anfordern", "priority": "medium", "status": "open"},
    {"title": "Visum-Unterstützungsschreiben erstellen", "description": "Für Mohammad Reza Hosseini vorbereiten", "priority": "high", "status": "open"},
]


@system_router.post("/system/seed-demo-data")
async def seed_demo_data(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Re-seed 12 realistic demo applicants + 5 staff tasks for the live demo.

    Idempotent: if a demo email already exists, its profile and application
    are updated instead of duplicated. Returns a per-step summary.

    Admin-only.
    """
    import os
    import random
    from datetime import timedelta
    import bcrypt

    db = get_db()
    seed_pw = os.environ.get("SEED_DEV_PASSWORD", "DevSeed@2026!")
    now = datetime.now(timezone.utc)

    # Workspace anchor
    ws = await db.workspaces.find_one({"slug": "studienkolleg"}) or await db.workspaces.find_one()
    ws_id = str(ws["_id"]) if ws else None

    # Stage pool – distribute applicants across pipeline stages
    stage_pool: list = []
    for stage, count in _DEMO_STAGES_DISTRIBUTION:
        stage_pool.extend([stage] * count)
    random.shuffle(stage_pool)

    summary = {"users_created": 0, "users_updated": 0, "applications_created": 0, "applications_updated": 0, "tasks_created": 0}

    for i, demo in enumerate(_DEMO_APPLICANTS):
        existing = await db.users.find_one({"email": demo["email"]})
        if existing:
            await db.users.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "full_name": demo["full_name"],
                    "country": demo.get("country", ""),
                    "phone": demo.get("phone", ""),
                    "active": True,
                    "role": "applicant",
                }},
            )
            user_id = str(existing["_id"])
            summary["users_updated"] += 1
        else:
            pw_hash = bcrypt.hashpw(seed_pw.encode(), bcrypt.gensalt()).decode()
            res = await db.users.insert_one({
                "email": demo["email"],
                "full_name": demo["full_name"],
                "password_hash": pw_hash,
                "role": "applicant",
                "active": True,
                "country": demo.get("country", ""),
                "phone": demo.get("phone", ""),
                "language_pref": "de",
                "created_at": now - timedelta(days=random.randint(5, 45)),
                "seeded": True,
            })
            user_id = str(res.inserted_id)
            summary["users_created"] += 1

        stage = stage_pool[i % len(stage_pool)] if stage_pool else "lead_new"
        days_ago = random.randint(1, 30)

        existing_app = await db.applications.find_one({"applicant_id": user_id})
        if existing_app:
            await db.applications.update_one(
                {"_id": existing_app["_id"]},
                {"$set": {
                    "current_stage": stage,
                    "last_activity_at": now - timedelta(days=random.randint(0, 3)),
                }},
            )
            summary["applications_updated"] += 1
        else:
            await db.applications.insert_one({
                "applicant_id": user_id,
                "workspace_id": ws_id,
                "current_stage": stage,
                "source": random.choice(["website_form", "partner_referral", "direct_inquiry"]),
                "priority": random.choice(["normal", "normal", "high"]),
                "created_at": now - timedelta(days=days_ago),
                "last_activity_at": now - timedelta(days=random.randint(0, 3)),
            })
            summary["applications_created"] += 1

    # Demo tasks (only seed if none of the demo titles already exist)
    staff = await db.users.find_one({"role": "staff"})
    staff_id = str(staff["_id"]) if staff else None
    existing_task_titles = {t["title"] for t in _DEMO_TASKS}
    have = await db.tasks.count_documents({"title": {"$in": list(existing_task_titles)}})
    if have == 0 and staff_id:
        for t in _DEMO_TASKS:
            await db.tasks.insert_one({
                "title": t["title"],
                "description": t["description"],
                "priority": t["priority"],
                "status": t["status"],
                "assigned_to": staff_id,
                "created_by": staff_id,
                "workspace_id": ws_id,
                "created_at": now - timedelta(days=random.randint(1, 7)),
                "due_date": (now + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                "history": [],
                "notes": [],
            })
            summary["tasks_created"] += 1

    # Final counts
    summary["total_applications"] = await db.applications.count_documents({})
    summary["total_users"] = await db.users.count_documents({})
    summary["total_tasks"] = await db.tasks.count_documents({})

    return {
        "status": "ok",
        "performed_by": user.get("email"),
        "performed_at": now.isoformat(),
        "summary": summary,
    }




@system_router.get("/system/monitoring")
async def system_monitoring(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Umfassendes System-Monitoring fuer Admins."""
    from services.worker import get_worker_health
    from services.scheduler import get_scheduler_health

    db = get_db()
    now = datetime.now(timezone.utc)

    # Letzte Health-Metriken aus DB
    latest_metrics = await db.system_metrics.find_one(sort=[("timestamp", -1)])
    metrics = {}
    if latest_metrics:
        metrics = {k: v for k, v in latest_metrics.items() if k not in ("_id", "timestamp")}
        if hasattr(latest_metrics.get("timestamp"), "isoformat"):
            ts = latest_metrics["timestamp"]
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            metrics["metrics_age_seconds"] = int((now - ts).total_seconds())

    # Job-Queue Stats
    job_stats = {
        "pending": await db.background_jobs.count_documents({"status": "pending"}),
        "processing": await db.background_jobs.count_documents({"status": "processing"}),
        "failed_24h": await db.background_jobs.count_documents({
            "status": "failed",
            "created_at": {"$gte": (now - __import__("datetime").timedelta(hours=24)).isoformat()},
        }),
    }

    return {
        "worker": get_worker_health(),
        "scheduler": get_scheduler_health(),
        "job_queue": job_stats,
        "system_metrics": metrics,
        "integrations": _get_integration_status(),
    }


def _get_integration_status() -> dict:
    """Integrations-Status ohne Secrets zu leaken."""
    import os
    stripe_key = os.environ.get("STRIPE_API_KEY", "")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    nscale_key = os.environ.get("NSCALE_API_KEY", "")
    resend_key = os.environ.get("RESEND_API_KEY", "")
    return {
        "stripe_active": bool(stripe_key and stripe_key.startswith("sk_")),
        "stripe_mode": "live" if stripe_key.startswith("sk_live_") else "test" if stripe_key.startswith("sk_test_") else "unconfigured",
        "ai_provider": "openrouter" if openrouter_key else ("nscale" if nscale_key else "none"),
        "ai_active": bool(openrouter_key or nscale_key),
        "email_active": bool(resend_key) or os.environ.get("EMAIL_ENABLED", "").lower() == "true",
        "storage_active": os.environ.get("STORAGE_BACKEND", "") in ("s3", "rustfs") or bool(os.environ.get("S3_ENDPOINT")),
    }



# ─── System Settings ──────────────────────────────────────────────────────────

@system_router.get("/system/settings")
async def get_settings(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Systemweite Einstellungen (Screening-Regeln, etc.)."""
    db = get_db()
    settings = await db.settings.find_one({"type": "global"}, {"_id": 0})
    return settings or {}


@system_router.put("/system/settings")
async def update_settings(data: dict, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Systemeinstellungen aktualisieren."""
    db = get_db()
    now = datetime.now(timezone.utc)
    await db.settings.update_one(
        {"type": "global"},
        {"$set": {**data, "type": "global", "updated_at": now.isoformat(), "updated_by": user["id"]}},
        upsert=True,
    )
    from services.audit import write_audit_log
    await write_audit_log("settings_updated", user["id"], "settings", "global", {"keys": list(data.keys())})
    return {"message": "Einstellungen gespeichert"}


# ─── DSGVO Data Management ────────────────────────────────────────────────────

@system_router.get("/system/gdpr/user-data/{user_id}")
async def export_user_data(user_id: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """DSGVO Art. 15: Vollstaendiger Datenexport eines Nutzers."""
    db = get_db()
    try:
        target = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0, "_id": 0})
    except Exception:
        return {"error": "Ungueltige ID"}
    if not target:
        return {"error": "Nutzer nicht gefunden"}

    target["id"] = user_id
    apps = await db.applications.find({"applicant_id": user_id}, {"_id": 0}).to_list(50)
    docs = await db.documents.find({"application_id": {"$in": [str(a.get("_id", "")) for a in apps] + [user_id]}}, {"_id": 0}).to_list(200)
    consents = await db.consents.find({"user_id": user_id}, {"_id": 0}).to_list(50)
    invoices = await db.invoices.find({"applicant_id": user_id}, {"_id": 0}).to_list(50)
    messages_sent = await db.messages.find({"sender_id": user_id}, {"_id": 0}).to_list(500)
    audit = await db.audit_logs.find({"actor_id": user_id}, {"_id": 0}).to_list(500)

    return {
        "export_date": datetime.now(timezone.utc).isoformat(),
        "user": target,
        "applications": apps,
        "documents": docs,
        "consents": consents,
        "invoices": invoices,
        "messages_sent": messages_sent,
        "audit_logs": audit,
    }


@system_router.post("/system/gdpr/anonymize/{user_id}")
async def anonymize_user(user_id: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """DSGVO Art. 17: Nutzer anonymisieren (Recht auf Vergessenwerden)."""
    db = get_db()
    try:
        target = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return {"error": "Ungueltige ID"}
    if not target:
        return {"error": "Nutzer nicht gefunden"}
    if target.get("role") in ["superadmin", "admin"]:
        return {"error": "Admin-Konten koennen nicht anonymisiert werden"}

    now = datetime.now(timezone.utc)
    anon_name = f"ANON-{user_id[:8]}"

    # Nutzer anonymisieren
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {
        "full_name": anon_name, "first_name": "ANONYMISIERT", "last_name": "ANONYMISIERT",
        "email": f"anon-{user_id[:8]}@deleted.local", "phone": "",
        "anonymized": True, "anonymized_at": now.isoformat(), "anonymized_by": user["id"],
        "active": False,
    }})

    # Applications anonymisieren
    await db.applications.update_many({"applicant_id": user_id}, {"$set": {
        "applicant_name": anon_name, "anonymized": True,
    }})

    # Rechnungen: Bewerber-Name anonymisieren (Aufbewahrungspflicht: Betrag/Nummer bleiben)
    await db.invoices.update_many({"applicant_id": user_id}, {"$set": {
        "applicant_name": anon_name, "applicant_email": f"anon-{user_id[:8]}@deleted.local",
    }})

    # Nachrichten: Absender anonymisieren
    await db.messages.update_many({"sender_id": user_id}, {"$set": {
        "sender_name": anon_name,
    }})

    from services.audit import write_audit_log
    await write_audit_log("gdpr_anonymized", user["id"], "user", user_id, {"reason": "DSGVO Art. 17"})

    return {"message": f"Nutzer {user_id} anonymisiert", "anon_name": anon_name}
