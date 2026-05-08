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


async def _get_user_lang(user_id: str) -> str:
    """Resolve a user's language preference from DB."""
    try:
        db = get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"language_pref": 1})
        return (user or {}).get("language_pref", "de")
    except Exception:
        return "de"


async def trigger_application_received(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    applicant_id: str = "",
    course_type: Optional[str] = None,
):
    """
    Ausloeser: Neue Bewerbung/Lead eingegangen.
    - Bewerber erhaelt Eingangsbestaetigung (DE/EN) via Job-Queue
    - Staff/Admin erhalten In-App Notification
    - Audit-Log
    """
    try:
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"

        # E-Mail ueber Job-Queue statt synchron
        from services.job_queue import enqueue
        await enqueue(
            job_type="email_send",
            payload={
                "template": "application_received",
                "to_email": applicant_email,
                "full_name": applicant_name,
                "application_id": application_id,
                "lang": lang,
            },
            dedupe_key=f"email_app_received_{application_id}",
            related_entity_type="application",
            related_entity_id=application_id,
            priority="high",
        )

        if applicant_id:
            await notify_staff_new_application(applicant_name, application_id, triggered_by=applicant_id)
        await write_audit_log(
            "automation_application_received",
            "system",
            "application",
            application_id,
            {"course": course_type, "lang": lang},
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
    - Nachforderungs-E-Mail ueber Job-Queue
    - In-App Notification an Bewerber
    - Audit-Log
    """
    if not missing_doc_types:
        return
    try:
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"
        label_map = REQUIRED_DOCUMENT_LABELS_EN if lang == "en" else REQUIRED_DOCUMENT_LABELS_DE
        labels = [label_map.get(t, t) for t in missing_doc_types]

        from services.job_queue import enqueue
        await enqueue(
            job_type="email_send",
            payload={
                "template": "document_requested",
                "to_email": applicant_email,
                "full_name": applicant_name,
                "document_types": labels,
                "lang": lang,
            },
            dedupe_key=f"email_docs_req_{application_id}",
            related_entity_type="application",
            related_entity_id=application_id,
            priority="high",
        )

        if applicant_id:
            await notify_applicant_doc_requested(applicant_id, labels, lang=lang)
        await write_audit_log(
            "automation_docs_requested",
            "system",
            "application",
            application_id,
            {"missing": missing_doc_types, "lang": lang},
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
    - Status-Mail ueber Job-Queue
    - In-App Notification an Bewerber
    - Audit-Log
    """
    try:
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"

        from services.job_queue import enqueue
        await enqueue(
            job_type="email_send",
            payload={
                "template": "status_changed",
                "to_email": applicant_email,
                "full_name": applicant_name,
                "new_status": new_stage,
                "lang": lang,
            },
            dedupe_key=f"email_status_{application_id}_{new_stage}",
            related_entity_type="application",
            related_entity_id=application_id,
            priority="high",
        )

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


async def trigger_language_level_action(
    application_id: str,
    applicant_id: str,
    applicant_email: str,
    applicant_name: str,
    language_level: str,
    course_type: str = "",
):
    """
    Sprachniveau-Trigger (aus Qualifizierungs-Engine):
    - < B1 → Auto-Sprachkursangebot + In-App Task
    - >= B1 → Naechste Pipeline-Stufe freischalten
    - >= B2 + Pflege → Pflege-Pipeline aktivieren
    """
    try:
        db = get_db()
        lang = await _get_user_lang(applicant_id) if applicant_id else "de"
        CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]
        idx = CEFR.index(language_level) if language_level in CEFR else -1
        now_iso = datetime.now(timezone.utc).isoformat()

        if idx < 2:  # < B1
            # Auto-Sprachkursangebot erstellen
            await db.tasks.insert_one({
                "id": str(uuid.uuid4()),
                "application_id": application_id,
                "assigned_to": applicant_id,
                "title": "Sprachkurs buchen – Niveau unter B1" if lang == "de" else "Book Language Course – Level below B1",
                "description": (
                    f"Ihr aktuelles Sprachniveau ({language_level}) liegt unter B1. "
                    "Fuer die Zulassung zum Studienkolleg ist mindestens B1 erforderlich. "
                    "Bitte buchen Sie einen Deutschkurs."
                ) if lang == "de" else (
                    f"Your current language level ({language_level}) is below B1. "
                    "At least B1 is required for Studienkolleg admission. "
                    "Please book a German course."
                ),
                "status": "open",
                "priority": "high",
                "type": "language_course",
                "category": "sprachkurs",
                "created_at": now_iso,
                "created_by": "system",
            })

            # E-Mail: Sprachkursangebot
            from services.job_queue import enqueue
            await enqueue(
                job_type="email_send",
                payload={
                    "template": "language_course_offer",
                    "to_email": applicant_email,
                    "full_name": applicant_name,
                    "language_level": language_level,
                    "lang": lang,
                },
                dedupe_key=f"lang_course_{application_id}",
                related_entity_type="application",
                related_entity_id=application_id,
                priority="normal",
            )

            # In-App Notification
            await db.notifications.insert_one({
                "id": str(uuid.uuid4()),
                "user_id": applicant_id,
                "type": "language_course_offer",
                "title": "Sprachkurs-Empfehlung" if lang == "de" else "Language Course Recommendation",
                "message": f"Sprachniveau {language_level} – Deutschkurs empfohlen." if lang == "de" else f"Language level {language_level} – German course recommended.",
                "read": False,
                "created_at": now_iso,
            })

            logger.info(f"[AUTOMATION] language_trigger: {application_id} level={language_level} → Sprachkurs-Angebot")

        elif idx >= 2:  # >= B1
            # Pipeline-Stufe freischalten: Falls in lead_new → in_review
            app = await db.applications.find_one({"_id": ObjectId(application_id)}, {"_id": 0, "current_stage": 1})
            if app and app.get("current_stage") in ("lead_new", "contacted"):
                await db.applications.update_one(
                    {"_id": ObjectId(application_id)},
                    {"$set": {"current_stage": "in_review", "updated_at": now_iso}},
                )
                await db.notifications.insert_one({
                    "id": str(uuid.uuid4()),
                    "user_id": applicant_id,
                    "type": "pipeline_advanced",
                    "title": "Bewerbung freigeschaltet" if lang == "de" else "Application Unlocked",
                    "message": "Ihr Sprachniveau genuegt – Ihre Bewerbung wird jetzt geprueft." if lang == "de" else "Your language level is sufficient – your application is now being reviewed.",
                    "read": False,
                    "created_at": now_iso,
                })
                logger.info(f"[AUTOMATION] language_trigger: {application_id} level={language_level} → Pipeline advanced to in_review")

    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_language_level_action failed: {e}")


import uuid  # noqa: E402
