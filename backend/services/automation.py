"""
Workflow-Automationen pro Bewerberfall.

Pflichtlogik:
- Eingang neuer Bewerbung → E-Mail + Staff-Queue
- Vollständigkeitsprüfung → Nachforderung bei fehlenden Docs
- Statuswechsel → Trigger-Mail
- Reminder bei Inaktivität (> 3 Tage keine Aktion)
- Audit-Trail für alle Automationen

Alle Automationen sind non-blocking (try/except) und audit-geloggt.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from services.audit import write_audit_log
from services.email import (
    send_application_received,
    send_document_requested,
    _send,
)

logger = logging.getLogger(__name__)

REQUIRED_DOCUMENT_LABELS = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}

STAGE_LABELS_DE = {
    "lead_new": "Neue Anfrage eingegangen",
    "in_review": "In Bearbeitung",
    "pending_docs": "Unterlagen angefordert",
    "interview_scheduled": "Beratungsgespräch geplant",
    "conditional_offer": "Vorläufige Zusage erteilt",
    "offer_sent": "Zulassungsangebot versandt",
    "enrolled": "Eingeschrieben",
    "declined": "Abgelehnt",
    "on_hold": "Warteschleife",
    "archived": "Archiviert",
}


async def trigger_application_received(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    course_type: Optional[str] = None,
):
    """
    Auslöser: Neue Bewerbung/Lead eingegangen.
    - Bewerber erhält Eingangsbestätigung
    - Audit-Log
    """
    try:
        send_application_received(applicant_email, applicant_name, application_id)
        await write_audit_log(
            "automation_application_received",
            "system",
            "application",
            application_id,
            {"email": applicant_email, "course": course_type},
        )
        logger.info(f"[AUTOMATION] application_received: {application_id}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_application_received failed: {e}")


async def trigger_missing_documents(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    missing_doc_types: list,
):
    """
    Auslöser: Pflichtdokumente fehlen.
    - Nachforderungs-E-Mail an Bewerber
    - Audit-Log
    """
    if not missing_doc_types:
        return
    try:
        labels = [REQUIRED_DOCUMENT_LABELS.get(t, t) for t in missing_doc_types]
        send_document_requested(applicant_email, applicant_name, labels)
        await write_audit_log(
            "automation_docs_requested",
            "system",
            "application",
            application_id,
            {"missing": missing_doc_types, "email": applicant_email},
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
    extra_info: Optional[str] = None,
):
    """
    Auslöser: Statuswechsel einer Bewerbung.
    - Bewerber erhält Status-Mail
    - Audit-Log
    """
    try:
        stage_label = STAGE_LABELS_DE.get(new_stage, new_stage)
        subject = f"Update zu deiner Bewerbung – {stage_label}"
        html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Hallo {applicant_name or 'Bewerber/in'},</h3>
      <p style="color:#475569">der Status deiner Bewerbung wurde aktualisiert:</p>
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;padding:16px;margin:16px 0">
        <p style="color:#64748b;font-size:13px;margin:0 0 4px 0">Neuer Status:</p>
        <p style="color:#113655;font-size:18px;font-weight:600;margin:0">{stage_label}</p>
      </div>
      {f'<p style="color:#475569">{extra_info}</p>' if extra_info else ''}
      <p style="color:#475569">Du kannst deinen aktuellen Status jederzeit im Portal einsehen.</p>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Bei Fragen: <a href="mailto:info@stk-aachen.de">info@stk-aachen.de</a>
      </p>
    </div>
    """
        _send(applicant_email, subject, html)
        await write_audit_log(
            "automation_status_change_email",
            actor_id,
            "application",
            application_id,
            {"old_stage": old_stage, "new_stage": new_stage},
        )
        logger.info(f"[AUTOMATION] status_change_email: {application_id} → {new_stage}")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_status_change failed: {e}")


async def trigger_inactivity_reminder(
    application_id: str,
    applicant_email: str,
    applicant_name: str,
    days_inactive: int,
):
    """
    Auslöser: Keine Aktivität seit X Tagen.
    - Erinnerungs-E-Mail an Bewerber
    """
    try:
        subject = "Erinnerung – Bitte vervollständige deine Bewerbung"
        html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Hallo {applicant_name or 'Bewerber/in'},</h3>
      <p style="color:#475569">wir haben seit {days_inactive} Tagen keine Aktualisierung deiner Bewerbung erhalten.</p>
      <p style="color:#475569">Bitte prüfe dein Portal und vervollständige ggf. fehlende Unterlagen, damit wir deine Bewerbung weiter bearbeiten können.</p>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Bei Fragen: <a href="mailto:info@stk-aachen.de">info@stk-aachen.de</a>
      </p>
    </div>
    """
        _send(applicant_email, subject, html)
        await write_audit_log(
            "automation_inactivity_reminder",
            "system",
            "application",
            application_id,
            {"days_inactive": days_inactive},
        )
        logger.info(f"[AUTOMATION] inactivity_reminder: {application_id}, {days_inactive}d")
    except Exception as e:
        logger.error(f"[AUTOMATION] trigger_inactivity_reminder failed: {e}")
