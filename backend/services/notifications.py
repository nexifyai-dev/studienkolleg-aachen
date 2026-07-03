"""
Notification System – In-App Notifications for all roles.

Architecture:
- MongoDB collection: notifications
- Each notification is tied to a recipient (user_id)
- Trigger-based: Events in the system create notifications
- Read/Unread tracking
- Language-aware (DE/EN based on user.language_pref)
- Auditable: who, when, what, for whom

Trigger events:
- application_received    → Staff/Admin
- status_changed          → Applicant
- document_requested      → Applicant
- document_uploaded       → Staff
- teacher_assigned        → Applicant + Teacher
- consent_granted         → Teacher (for assigned applicant)
- consent_revoked         → Teacher (for assigned applicant)
- new_message             → Recipient
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

# Notification type definitions with DE/EN templates
NOTIFICATION_TEMPLATES = {
    "application_received": {
        "de": {"title": "Neue Bewerbung", "icon": "file-text"},
        "en": {"title": "New Application", "icon": "file-text"},
    },
    "status_changed": {
        "de": {"title": "Statusänderung", "icon": "refresh-cw"},
        "en": {"title": "Status Update", "icon": "refresh-cw"},
    },
    "document_requested": {
        "de": {"title": "Dokument angefordert", "icon": "file-text"},
        "en": {"title": "Document Requested", "icon": "file-text"},
    },
    "document_uploaded": {
        "de": {"title": "Dokument hochgeladen", "icon": "upload"},
        "en": {"title": "Document Uploaded", "icon": "upload"},
    },
    "teacher_assigned": {
        "de": {"title": "Betreuer/in zugewiesen", "icon": "graduation-cap"},
        "en": {"title": "Supervisor Assigned", "icon": "graduation-cap"},
    },
    "consent_granted": {
        "de": {"title": "Einwilligung erteilt", "icon": "shield"},
        "en": {"title": "Consent Granted", "icon": "shield"},
    },
    "consent_revoked": {
        "de": {"title": "Einwilligung widerrufen", "icon": "shield-off"},
        "en": {"title": "Consent Revoked", "icon": "shield-off"},
    },
    "new_message": {
        "de": {"title": "Neue Nachricht", "icon": "message-square"},
        "en": {"title": "New Message", "icon": "message-square"},
    },
}


async def create_notification(
    recipient_id: str,
    notification_type: str,
    message: str,
    link: Optional[str] = None,
    triggered_by: Optional[str] = None,
    lang: str = "de",
    metadata: Optional[dict] = None,
) -> str:
    """Create a new notification for a user. Returns notification ID."""
    db = get_db()

    template = NOTIFICATION_TEMPLATES.get(notification_type, {})
    lang_tmpl = template.get(lang, template.get("de", {"title": notification_type, "icon": "bell"}))

    doc = {
        "recipient_id": recipient_id,
        "type": notification_type,
        "title": lang_tmpl["title"],
        "icon": lang_tmpl["icon"],
        "message": message,
        "link": link,
        "read": False,
        "triggered_by": triggered_by,
        "lang": lang,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc),
    }

    result = await db.notifications.insert_one(doc)
    logger.info(f"[NOTIFY] Created {notification_type} for {recipient_id}")
    return str(result.inserted_id)


async def notify_staff_new_application(applicant_name: str, application_id: str, triggered_by: str) -> None:
    """Notify all staff/admin about a new application."""
    db = get_db()
    staff_users = await db.users.find(
        {"role": {"$in": ["superadmin", "admin", "staff"]}, "active": True},
        {"_id": 1, "language_pref": 1},
    ).to_list(100)

    for user in staff_users:
        uid = str(user["_id"])
        lang = user.get("language_pref", "de")
        msg = f"Neue Bewerbung von {applicant_name}" if lang == "de" else f"New application from {applicant_name}"
        await create_notification(uid, "application_received", msg,
            link=f"/staff/applications/{application_id}", triggered_by=triggered_by, lang=lang)


async def notify_applicant_status_change(applicant_id: str, new_status: str, lang: str = "de") -> None:
    """Notify applicant about status change."""
    status_de = {"in_review": "In Prüfung", "pending_docs": "Dokumente ausstehend", "enrolled": "Eingeschrieben",
                 "declined": "Abgelehnt", "offer_sent": "Angebot versendet", "conditional_offer": "Bedingte Zusage"}
    status_en = {"in_review": "Under Review", "pending_docs": "Documents Pending", "enrolled": "Enrolled",
                 "declined": "Declined", "offer_sent": "Offer Sent", "conditional_offer": "Conditional Offer"}
    label = (status_en if lang == "en" else status_de).get(new_status, new_status)
    msg = f"Your status: {label}" if lang == "en" else f"Dein Status: {label}"
    await create_notification(applicant_id, "status_changed", msg,
        link="/portal/journey", lang=lang)


async def notify_applicant_doc_requested(applicant_id: str, doc_types: list, lang: str = "de") -> None:
    """Notify applicant about document request."""
    docs = ", ".join(doc_types[:3])
    msg = f"Documents requested: {docs}" if lang == "en" else f"Dokumente angefordert: {docs}"
    await create_notification(applicant_id, "document_requested", msg,
        link="/portal/documents", lang=lang)


async def notify_teacher_assignment(applicant_id: str, teacher_id: str, applicant_name: str, teacher_name: str) -> None:
    """Notify both applicant and teacher about assignment."""
    db = get_db()
    from bson import ObjectId

    applicant = await db.users.find_one({"_id": ObjectId(applicant_id)}, {"language_pref": 1})
    teacher = await db.users.find_one({"_id": ObjectId(teacher_id)}, {"language_pref": 1})

    a_lang = (applicant or {}).get("language_pref", "de")
    t_lang = (teacher or {}).get("language_pref", "de")

    a_msg = f"Supervisor assigned: {teacher_name}" if a_lang == "en" else f"Betreuer/in zugewiesen: {teacher_name}"
    await create_notification(applicant_id, "teacher_assigned", a_msg,
        link="/portal/consents", lang=a_lang, triggered_by="system")

    t_msg = f"New student assigned: {applicant_name}" if t_lang == "en" else f"Neuer Lernender zugewiesen: {applicant_name}"
    await create_notification(teacher_id, "teacher_assigned", t_msg,
        link="/staff", lang=t_lang, triggered_by="system")


async def notify_teacher_consent_change(teacher_id: str, applicant_name: str, granted: bool, lang: str = "de") -> None:
    """Notify teacher when applicant grants/revokes consent."""
    if granted:
        msg = f"{applicant_name} granted data access consent" if lang == "en" else f"{applicant_name} hat die Datenweitergabe genehmigt"
        ntype = "consent_granted"
    else:
        msg = f"{applicant_name} revoked data access consent" if lang == "en" else f"{applicant_name} hat die Datenweitergabe widerrufen"
        ntype = "consent_revoked"
    await create_notification(teacher_id, ntype, msg, link="/staff", lang=lang, triggered_by="system")


async def notify_new_message(conv_id: str, sender: dict, content: str, visibility: str = "public", channel: str = "portal"):
    """Systemweite Logik: informiert alle Gespraechsteilnehmer (ausser Absender)
    ueber neue Nachrichten via In-App-Notification + E-Mail-Hinweis."""
    import os
    import asyncio
    from bson import ObjectId

    db = get_db()
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
    except Exception:
        return
    if not conv:
        return

    preview = (content or "")[:120]
    sender_name = sender.get("full_name") or sender.get("email") or "Jemand"

    for pid in conv.get("participants", []):
        if not pid or pid == sender.get("id"):
            continue
        try:
            recipient = await db.users.find_one(
                {"_id": ObjectId(pid)},
                {"role": 1, "email": 1, "full_name": 1, "language_pref": 1},
            )
        except Exception:
            continue
        if not recipient:
            continue
        r_role = recipient.get("role", "")
        if visibility == "internal" and r_role == "applicant":
            continue

        link = "/portal/messages" if r_role == "applicant" else "/staff/messaging"
        try:
            await create_notification(
                recipient_id=pid,
                notification_type="new_message",
                message=f"{sender_name}: {preview}",
                link=link,
                triggered_by=sender.get("id"),
                lang=recipient.get("language_pref", "de"),
            )
        except Exception:
            logger.warning(f"[notify_new_message] In-App-Notification fehlgeschlagen fuer {pid}")

        # E-Mail-Hinweis an Bewerber bei Portal-Nachrichten (email-Kanal sendet ohnehin via SMTP)
        if r_role == "applicant" and channel == "portal" and recipient.get("email"):
            try:
                from services.email_service import send_email as smtp_send, is_configured
                if is_configured():
                    app_url = os.environ.get("APP_URL") or os.environ.get("FRONTEND_URL", "")
                    body = (
                        f"Hallo {recipient.get('full_name', '')},\n\n"
                        f"Sie haben eine neue Nachricht in Ihrem Bewerberportal erhalten:\n\n"
                        f"\"{preview}\"\n\n"
                        f"Bitte melden Sie sich in Ihrem Portal an, um zu antworten:\n"
                        f"{app_url}/portal/messages\n\n"
                        f"Ihr Team vom Studienkolleg Aachen"
                    )
                    asyncio.create_task(asyncio.to_thread(
                        smtp_send,
                        to_email=recipient["email"],
                        subject="Neue Nachricht vom Studienkolleg Aachen",
                        body=body,
                        sender_name="Studienkolleg Aachen",
                        sender_role="staff",
                    ))
            except Exception:
                pass
