"""
Workflow-Automationen pro Bewerberfall.

Pflichtlogik:
- Eingang neuer Bewerbung → E-Mail + Notification + Staff-Queue
- Vollständigkeitsprüfung → Nachforderung bei fehlenden Docs
- Statuswechsel → Trigger-Mail + Notification
- Reminder bei Inaktivität (> 3 Tage keine Aktion)
- Audit-Trail für alle Automationen

Alle Automationen sind non-blocking (try/except) und audit-geloggt.
Sprache: basierend auf user.language_pref (DE/EN).
Preisregel: Keine Festpreise – immer individuell/einzelfallabhängig.
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId

from database import get_db
from services.audit import write_audit_log
from services.email import (
    send_application_received,
    send_document_requested,
    send_precheck_process_update,
    send_status_changed,
    send_teacher_assigned,
)
from services.notifications import (
    notify_staff_new_application,
    notify_applicant_status_change,
    notify_applicant_doc_requested,
    notify_teacher_assignment,
    create_notification,
)

logger = logging.getLogger(__name__)

REQUIRED_DOCUMENT_LABELS_DE = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}
REQUIRED_DOCUMENT_LABELS_EN = {
    "language_certificate": "German Language Certificate",
    "highschool_diploma": "High School Diploma / University Entrance Qualification",
    "passport": "Passport / ID Card",
}

AUTOMATION_TRIGGER_MAP = {
    "special_case_detected": {
        "task_type": "staff_manual_review",
        "priority": "high",
        "scope": "admission",
    },
    "document_rejected": {
        "task_type": "staff_manual_review",
        "priority": "high",
        "scope": "documents",
    },
    "reference_mismatch": {
        "task_type": "authority_clarification",
        "priority": "high",
        "scope": "recognition",
    },
    "missing_activity": {
        "task_type": "applicant_followup",
        "priority": "normal",
        "scope": "engagement",
    },
    "seat_reservation": {
        "task_type": "seat_reservation_check",
        "priority": "normal",
        "scope": "capacity",
    },
    "language_course_needed": {
        "task_type": "language_course_followup",
        "priority": "normal",
        "scope": "language",
    },
    "payment_status_active_case": {
        "task_type": "payment_status_review",
        "priority": "high",
        "scope": "finance",
    },
}


async def _get_user_lang(user_id: str) -> str:
    """Resolve a user's language preference from DB."""
    try:
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"language_pref": 1})
        return (user or {}).get("language_pref", "de")
    except Exception:
        return "de"


async def _create_automation_task(
    *,
    application_id: str,
    task_type: str,
    title: str,
    description: str,
    priority: str,
    scope: str,
    actor_id: str = "system",
) -> Optional[str]:
    """Create an internal task and history entry for automation-driven follow-ups."""
    try:
        db = get_db()
        now = datetime.now(timezone.utc)

        app = await db.applications.find_one({"_id": ObjectId(application_id)}, {"assigned_staff_id": 1})
        assigned_to = (app or {}).get("assigned_staff_id")
        if not assigned_to:
            staff = await db.users.find_one(
                {"role": {"$in": ["superadmin", "admin", "staff"]}, "active": True},
                {"_id": 1},
            )
            assigned_to = str(staff["_id"]) if staff else None

        task_doc = {
            "title": title,
            "description": description,
            "application_id": application_id,
            "assigned_to": assigned_to,
            "priority": priority,
            "visibility": "internal",
            "status": "open",
            "created_by": actor_id,
            "created_at": now,
            "task_type": task_type,
            "scope": scope,
            "source": "automation",
        }
        result = await db.tasks.insert_one(task_doc)
        task_id = str(result.inserted_id)

        await db.task_history.insert_one({
            "task_id": task_id,
            "action": "created",
            "old_value": None,
            "new_value": "open",
            "actor_id": actor_id,
            "actor_name": "Automation",
            "occurred_at": now,
        })
        return task_id
    except Exception as exc:
        logger.error("[AUTOMATION] _create_automation_task failed: %s", exc)
        return None


async def trigger_application_received(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    applicant_id: str = "",
    course_type: Optional[str] = None,
):
    """
    Ausloeser: Neue Bewerbung/Lead eingegangen.
    - Bewerber erhaelt Eingangsbestaetigung (DE/EN)
    - Staff/Admin erhalten In-App Notification
    - Audit-Log
    """
    try:
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"
        send_application_received(applicant_email, applicant_name, application_id, lang=lang)
        if applicant_id:
            await notify_staff_new_application(applicant_name, application_id, triggered_by=applicant_id)
        await write_audit_log(
            "automation_application_received",
            "system",
            "application",
            application_id,
            {"email": applicant_email, "course": course_type, "lang": lang},
        )
        logger.info(f"[AUTOMATION] application_received: {application_id} lang={lang}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_application_received failed: {e}")


async def trigger_missing_documents(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    missing_doc_types: list,
    applicant_id: str = "",
):
    """
    Ausloeser: Pflichtdokumente fehlen.
    - Nachforderungs-E-Mail an Bewerber (DE/EN)
    - In-App Notification an Bewerber
    - Audit-Log
    """
    if not missing_doc_types:
        return
    try:
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"
        label_map = REQUIRED_DOCUMENT_LABELS_EN if lang == "en" else REQUIRED_DOCUMENT_LABELS_DE
        labels = [label_map.get(t, t) for t in missing_doc_types]
        send_document_requested(applicant_email, applicant_name, labels, lang=lang)
        if applicant_id:
            await notify_applicant_doc_requested(applicant_id, labels, lang=lang)
        await write_audit_log(
            "automation_docs_requested",
            "system",
            "application",
            application_id,
            {"missing": missing_doc_types, "email": applicant_email, "lang": lang},
        )
        logger.info(f"[AUTOMATION] docs_requested: {application_id}, missing: {missing_doc_types}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_missing_documents failed: {e}")


async def trigger_status_change(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    old_stage: str,
    new_stage: str,
    actor_id: str,
    applicant_id: str = "",
):
    """
    Ausloeser: Statuswechsel einer Bewerbung.
    - Bewerber erhaelt Status-Mail (DE/EN aus email.py Templates)
    - In-App Notification an Bewerber
    - Audit-Log
    """
    try:
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"
        send_status_changed(applicant_email, applicant_name, new_stage, lang=lang)
        if applicant_id:
            await notify_applicant_status_change(applicant_id, new_stage, lang=lang)
        await write_audit_log(
            "automation_status_change_email",
            actor_id,
            "application",
            application_id,
            {"old_stage": old_stage, "new_stage": new_stage, "lang": lang},
        )
        logger.info(f"[AUTOMATION] status_change: {application_id} -> {new_stage} lang={lang}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_status_change failed: {e}")


async def trigger_teacher_assigned(
    applicant_id: str,
    teacher_id: str,
    applicant_email: str,
    applicant_name: str,
    teacher_name: str,
):
    """
    Ausloeser: Lehrer wird Bewerber zugewiesen.
    - Bewerber erhaelt E-Mail (DE/EN)
    - In-App Notification an Bewerber + Lehrer
    - Audit-Log
    """
    try:
        lang = await _get_user_lang(applicant_id)
        send_teacher_assigned(applicant_email, applicant_name, teacher_name, lang=lang)
        await notify_teacher_assignment(applicant_id, teacher_id, applicant_name, teacher_name)
        await write_audit_log(
            "automation_teacher_assigned",
            "system",
            "teacher_assignment",
            teacher_id,
            {"applicant_id": applicant_id, "teacher_name": teacher_name},
        )
        logger.info(f"[AUTOMATION] teacher_assigned: {applicant_id} -> {teacher_id}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_teacher_assigned failed: {e}")


async def trigger_document_uploaded(
    application_id: str,
    applicant_id: str,
    applicant_name: str,
    doc_type: str,
    filename: str,
):
    """
    Ausloeser: Bewerber laedt Dokument hoch.
    - In-App Notification an Staff/Admin
    - Audit-Log
    """
    try:
        db = get_db()
        staff_users = await db.users.find(
            {"role": {"$in": ["superadmin", "admin", "staff"]}, "active": True},
            {"_id": 1, "language_pref": 1},
        ).to_list(100)

        for su in staff_users:
            uid = str(su["_id"])
            lang = su.get("language_pref", "de")
            msg = (
                f"{applicant_name} hat ein Dokument hochgeladen: {filename}"
                if lang == "de"
                else f"{applicant_name} uploaded a document: {filename}"
            )
            await create_notification(
                uid, "document_uploaded", msg,
                link=f"/staff/applications/{application_id}",
                triggered_by=applicant_id, lang=lang,
            )
        logger.info(f"[AUTOMATION] document_uploaded: {application_id} by {applicant_id}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_document_uploaded failed: {e}")


async def trigger_inactivity_reminder(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    days_inactive: int,
    applicant_id: str = "",
):
    """
    Ausloeser: Keine Aktivitaet seit X Tagen.
    - Erinnerungs-E-Mail an Bewerber (DE/EN)
    """
    try:
        from services.email import _send, _wrap, _btn, _get_app_url
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"
        app_url = _get_app_url()
        name = applicant_name or ("Applicant" if lang == "en" else "Bewerber/in")

        if lang == "en":
            subject = "Reminder – Please Complete Your Application"
            content = f"""<h3 style="color:#113655;margin-top:0">Hello {name},</h3>
            <p style="color:#475569;line-height:1.6">We have not received any updates on your application for {days_inactive} days.</p>
            <p style="color:#475569;line-height:1.6">Please check your portal and upload any missing documents so we can continue processing your application.</p>
            {_btn(f'{app_url}/portal', 'Go to Portal')}
            <p style="color:#64748b;font-size:13px;margin-top:24px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""
        else:
            subject = "Erinnerung – Bitte vervollstaendige deine Bewerbung"
            content = f"""<h3 style="color:#113655;margin-top:0">Hallo {name},</h3>
            <p style="color:#475569;line-height:1.6">Wir haben seit {days_inactive} Tagen keine Aktualisierung deiner Bewerbung erhalten.</p>
            <p style="color:#475569;line-height:1.6">Bitte pruefe dein Portal und vervollstaendige ggf. fehlende Unterlagen, damit wir deine Bewerbung weiter bearbeiten koennen.</p>
            {_btn(f'{app_url}/portal', 'Zum Portal')}
            <p style="color:#64748b;font-size:13px;margin-top:24px">Fragen? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""

        _send(applicant_email, subject, _wrap(content, lang))
        await trigger_case_signal(
            application_id=application_id,
            trigger_code="missing_activity",
            actor_id="system",
            applicant_id=applicant_id,
            applicant_email=applicant_email,
            applicant_name=applicant_name,
            status_context="inactive",
            area_context="engagement",
        )
        await write_audit_log(
            "automation_inactivity_reminder",
            "system",
            "application",
            application_id,
            {"days_inactive": days_inactive, "lang": lang},
        )
        logger.info(f"[AUTOMATION] inactivity_reminder: {application_id}, {days_inactive}d")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_inactivity_reminder failed: {e}")


async def trigger_case_signal(
    *,
    application_id: str,
    trigger_code: str,
    actor_id: str,
    applicant_id: str = "",
    applicant_email: str = "",
    applicant_name: str = "",
    status_context: str = "",
    area_context: str = "",
    fachlich_aktiv: bool = False,
    detail: str = "",
):
    """
    Generic automation trigger for case-relevant signals.
    Creates concrete follow-up tasks and (if possible) sends a precheck process email.
    """
    config = AUTOMATION_TRIGGER_MAP.get(trigger_code)
    if not config:
        logger.warning("[AUTOMATION] Unknown trigger_code=%s", trigger_code)
        return
    if trigger_code == "payment_status_active_case" and not fachlich_aktiv:
        logger.info("[AUTOMATION] Skip payment_status_active_case (fachlich_aktiv=False)")
        return

    try:
        task_title = f"{config['task_type']}: {trigger_code}"
        task_description = detail or f"Automation trigger '{trigger_code}' wurde erkannt."
        task_id = await _create_automation_task(
            application_id=application_id,
            task_type=config["task_type"],
            title=task_title,
            description=task_description,
            priority=config["priority"],
            scope=config["scope"],
            actor_id=actor_id or "system",
        )

        if applicant_email:
            lang = await _get_user_lang(applicant_id) if applicant_id else "de"
            send_precheck_process_update(
                to=applicant_email,
                full_name=applicant_name,
                status_context=status_context or trigger_code,
                area_context=area_context or config["scope"],
                lang=lang,
                requires_staff_review=config["task_type"] == "staff_manual_review",
                requires_authority_or_university_decision=config["task_type"] == "authority_clarification",
            )

        await write_audit_log(
            "automation_case_signal",
            actor_id or "system",
            "application",
            application_id,
            {
                "trigger_code": trigger_code,
                "task_type": config["task_type"],
                "task_id": task_id,
                "scope": config["scope"],
                "status_context": status_context,
                "area_context": area_context,
                "fachlich_aktiv": fachlich_aktiv,
            },
        )
        logger.info("[AUTOMATION] case_signal: app=%s trigger=%s task=%s", application_id, trigger_code, task_id)
    except Exception as exc:
        logger.error("[AUTOMATION] trigger_case_signal failed: %s", exc)


async def trigger_seat_reservation(
    application_id: str,
    actor_id: str,
    applicant_id: str = "",
    applicant_email: str = "",
    applicant_name: str = "",
):
    await trigger_case_signal(
        application_id=application_id,
        trigger_code="seat_reservation",
        actor_id=actor_id,
        applicant_id=applicant_id,
        applicant_email=applicant_email,
        applicant_name=applicant_name,
        status_context="seat_reservation_pending",
        area_context="capacity",
        detail="Platzreservierung wurde markiert und benötigt Staff-Validierung.",
    )


async def trigger_payment_status_active_case(
    application_id: str,
    actor_id: str,
    fachlich_aktiv: bool,
    applicant_id: str = "",
    applicant_email: str = "",
    applicant_name: str = "",
):
    await trigger_case_signal(
        application_id=application_id,
        trigger_code="payment_status_active_case",
        actor_id=actor_id,
        applicant_id=applicant_id,
        applicant_email=applicant_email,
        applicant_name=applicant_name,
        status_context="payment_status_open",
        area_context="finance",
        fachlich_aktiv=fachlich_aktiv,
        detail="Zahlungsstatus im fachlich aktiven Fall erfordert Nachverfolgung.",
    )
