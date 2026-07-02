"""
Job Handlers – Registrierte Handler fuer jeden Job-Typ.

Jeder Handler empfaengt den Job-Dict und fuehrt die fachliche Logik aus.
Handler muessen idempotent sein und duerfen keine Secrets loggen.

Registrierung: HANDLER_REGISTRY[job_type] = handler_function
"""
import logging
from typing import Callable, Awaitable

logger = logging.getLogger(__name__)

# Handler-Registry: job_type -> async handler function
HANDLER_REGISTRY: dict[str, Callable[..., Awaitable]] = {}


def register_handler(job_type: str):
    """Decorator: Registriert einen Handler fuer einen Job-Typ."""
    def decorator(func):
        HANDLER_REGISTRY[job_type] = func
        return func
    return decorator


# ═══════════════════════════════════════════════════════════════════════════
# AI SCREENING
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("ai_screening")
async def handle_ai_screening(job: dict) -> dict:
    """Fuehrt ein KI-Screening fuer eine Bewerbung durch."""
    from bson import ObjectId
    from database import get_db
    from models.schemas import to_str_id
    from services.ai_screening import run_ai_screening
    from services.audit import write_audit_log
    from datetime import datetime, timezone

    payload = job.get("payload", {})
    app_id = payload.get("application_id")
    triggered_by = payload.get("triggered_by", job.get("actor_id", "system"))

    if not app_id:
        raise ValueError("application_id fehlt im Payload")

    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise ValueError(f"Bewerbung {app_id} nicht gefunden")

    app_dict = to_str_id(dict(app))

    # Bewerber laden
    applicant = {}
    if app_dict.get("applicant_id"):
        u = await db.users.find_one(
            {"_id": ObjectId(app_dict["applicant_id"])},
            {"full_name": 1, "email": 1, "country": 1, "phone": 1},
        )
        if u:
            applicant = to_str_id(u)

    # Dokumente laden
    docs_raw = await db.documents.find({"application_id": app_id}).to_list(50)
    docs = [to_str_id(dict(d)) for d in docs_raw]
    for d in docs:
        d.pop("storage_key", None)

    # Nachrichten laden
    messages_raw = await db.messages.find({"application_id": app_id}).sort("created_at", 1).to_list(20)
    messages = [to_str_id(dict(m)) for m in messages_raw]

    # Screening durchfuehren
    result = await run_ai_screening(app_dict, applicant, docs, messages)

    # Ergebnis speichern
    result_to_save = {
        **result,
        "triggered_by": triggered_by,
        "trigger_source": "job_queue",
        "job_id": job.get("job_id"),
        "created_at": datetime.now(timezone.utc),
    }
    await db.ai_screenings.insert_one(result_to_save)

    await write_audit_log(
        "ai_screening_run", triggered_by, "application", app_id,
        {
            "screening_id": result["screening_id"],
            "suggested_stage": result["suggested_stage"],
            "source": "background_job",
            "job_id": job.get("job_id"),
        },
    )

    return {
        "screening_id": result["screening_id"],
        "suggested_stage": result["suggested_stage"],
        "is_complete": result["is_complete"],
        "anabin_category": result["anabin_category"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# DELTA RE-SCREENING
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("delta_rescreening")
async def handle_delta_rescreening(job: dict) -> dict:
    """Fuehrt ein Delta-Re-Screening nach Dokument-Upload durch."""
    from services.delta_screening import trigger_auto_rescreening

    payload = job.get("payload", {})
    app_id = payload.get("application_id")
    doc_type = payload.get("doc_type", "")
    filename = payload.get("filename", "")
    uploaded_by = payload.get("uploaded_by", "system")

    if not app_id:
        raise ValueError("application_id fehlt im Payload")

    result = await trigger_auto_rescreening(app_id, doc_type, filename, uploaded_by)

    if not result:
        return {"status": "skipped", "reason": "Bewerbung nicht gefunden oder Fehler"}

    return {
        "screening_id": result.get("screening_id"),
        "changes_count": result.get("delta", {}).get("changes_count", 0),
        "risk_change": result.get("delta", {}).get("risk_change", ""),
    }


# ═══════════════════════════════════════════════════════════════════════════
# E-MAIL VERSAND
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("email_send")
async def handle_email_send(job: dict) -> dict:
    """Versendet eine E-Mail ueber den konfigurierten Provider."""
    from services import email as email_svc

    payload = job.get("payload", {})
    template = payload.get("template")
    to_email = payload.get("to_email")

    if not template or not to_email:
        raise ValueError("template und to_email erforderlich")

    # Template-Dispatch
    template_funcs = {
        "welcome": lambda p: email_svc.send_welcome(p["to_email"], p.get("full_name", ""), p.get("lang", "de")),
        "application_received": lambda p: email_svc.send_application_received(p["to_email"], p.get("full_name", ""), p.get("application_id", ""), p.get("lang", "de")),
        "document_requested": lambda p: email_svc.send_document_requested(p["to_email"], p.get("full_name", ""), p.get("document_types", []), p.get("lang", "de")),
        "status_changed": lambda p: email_svc.send_status_changed(p["to_email"], p.get("full_name", ""), p.get("new_status", ""), p.get("lang", "de")),
        "password_reset": lambda p: email_svc.send_password_reset(p["to_email"], p.get("reset_url", ""), p.get("lang", "de")),
        "teacher_assigned": lambda p: email_svc.send_teacher_assigned(p["to_email"], p.get("full_name", ""), p.get("teacher_name", ""), p.get("lang", "de")),
        "case_email": lambda p: email_svc.send_case_email(p["to_email"], p.get("full_name", ""), p.get("subject_line", ""), p.get("body_text", ""), p.get("lang", "de")),
    }

    handler = template_funcs.get(template)
    if not handler:
        raise ValueError(f"Unbekanntes E-Mail-Template: {template}")

    success = await __import__("asyncio").to_thread(handler, payload)
    if not success:
        raise RuntimeError(f"E-Mail-Versand fehlgeschlagen: {template} an {to_email}")

    return {"sent": True, "template": template, "to": to_email}


# ═══════════════════════════════════════════════════════════════════════════
# NOTIFICATION ERSTELLEN
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("notification_create")
async def handle_notification_create(job: dict) -> dict:
    """Erstellt eine In-App-Benachrichtigung."""
    from services.notifications import create_notification

    payload = job.get("payload", {})
    user_id = payload.get("user_id")
    ntype = payload.get("notification_type", "info")
    message = payload.get("message", "")

    if not user_id or not message:
        raise ValueError("user_id und message erforderlich")

    await create_notification(
        user_id, ntype, message,
        link=payload.get("link"),
        triggered_by=payload.get("triggered_by", "system"),
        lang=payload.get("lang", "de"),
    )

    return {"created": True, "user_id": user_id, "type": ntype}


# ═══════════════════════════════════════════════════════════════════════════
# QUEUE FOLLOWUP (nach Resolution)
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("queue_followup")
async def handle_queue_followup(job: dict) -> dict:
    """Folgeaktionen nach Queue-Resolution (Re-Screening betroffener Bewerbungen)."""
    from bson import ObjectId
    from database import get_db
    from services.job_queue import enqueue

    payload = job.get("payload", {})
    country = payload.get("country", "")
    application_ids = payload.get("application_ids", [])

    if not application_ids:
        return {"status": "no_applications", "country": country}

    db = get_db()
    enqueued = 0
    for app_id in application_ids[:10]:  # Max 10 Re-Screenings
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
        if app and app.get("current_stage") not in ("enrolled", "declined"):
            await enqueue(
                job_type="ai_screening",
                payload={"application_id": app_id, "triggered_by": "queue_followup"},
                dedupe_key=f"followup_rescreen_{app_id}",
                related_entity_type="application",
                related_entity_id=app_id,
                priority="normal",
            )
            enqueued += 1

    return {"re_screenings_enqueued": enqueued, "country": country}


# ═══════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("cleanup")
async def handle_cleanup(job: dict) -> dict:
    """Bereinigt alte Jobs und stale Daten."""
    from database import get_db
    from datetime import datetime, timezone, timedelta

    db = get_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    result = await db.background_jobs.delete_many({
        "status": {"$in": ["succeeded", "cancelled"]},
        "created_at": {"$lte": cutoff},
    })

    return {"deleted_jobs": result.deleted_count}



# ═══════════════════════════════════════════════════════════════════════════
# INACTIVITY REMINDER
# ═══════════════════════════════════════════════════════════════════════════

@register_handler("inactivity_reminder")
async def handle_inactivity_reminder(job: dict) -> dict:
    """Sendet Inaktivitaets-Reminder an Bewerber."""
    from services.automation import trigger_inactivity_reminder

    payload = job.get("payload", {})
    app_id = payload.get("application_id")
    if not app_id:
        raise ValueError("application_id fehlt")

    await trigger_inactivity_reminder(
        application_id=app_id,
        applicant_email=payload.get("applicant_email", ""),
        applicant_name=payload.get("applicant_name", ""),
        days_inactive=payload.get("days_inactive", 5),
        applicant_id=payload.get("applicant_id", ""),
    )
    return {"sent": True, "application_id": app_id}
