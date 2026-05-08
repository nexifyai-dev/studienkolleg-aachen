"""
Stage-Effects-Engine – Seiteneffekte bei Statuswechsel.

Pflichtlogik aus 07_ux_workflows (Flow 4):
- System validiert erlaubten Uebergang (→ state_machine.py)
- Alte Aufgaben werden geschlossen oder entwertet
- Neue Aufgaben / Nachrichten / Rechnungen / Notifications erzeugt
- Applicant und ggf. Agentur erhalten kontextspezifische Information
- Audit Log schreibt alten und neuen Wert

Wird von applications.py nach erfolgreichem Statuswechsel aufgerufen.
"""
import logging
from datetime import datetime, timezone
from bson import ObjectId
from database import get_db
from services.audit import write_audit_log
from services.notifications import create_notification

logger = logging.getLogger(__name__)

# Konfiguration: Welche Aufgaben bei welchem Status erzeugt werden
STAGE_TASKS: dict[str, list[dict]] = {
    "in_review": [
        {"title": "Bewerbung pruefen und bewerten", "priority": "high",
         "description": "Neue Bewerbung eingegangen. Vollstaendigkeit und Eignung pruefen."},
    ],
    "pending_docs": [
        {"title": "Fehlende Dokumente nachverfolgen", "priority": "medium",
         "description": "Bewerber wurde ueber fehlende Unterlagen informiert. Nach 5 Tagen Follow-Up."},
    ],
    "interview_scheduled": [
        {"title": "Interview durchfuehren", "priority": "high",
         "description": "Termin mit Bewerber vereinbaren oder durchfuehren."},
    ],
    "conditional_offer": [
        {"title": "Bedingtes Angebot erstellen und versenden", "priority": "high",
         "description": "Angebot mit Bedingungen formulieren und an Bewerber uebermitteln."},
    ],
    "offer_sent": [
        {"title": "Angebotsrueckmeldung nachverfolgen", "priority": "medium",
         "description": "Bewerber hat Angebot erhalten. Rueckmeldung abwarten, nach 7 Tagen Follow-Up."},
    ],
    "enrolled": [
        {"title": "Einschreibung finalisieren", "priority": "high",
         "description": "Alle Unterlagen pruefen. Immatrikulations-Bestaetigung versenden."},
    ],
}

# Stages, bei denen offene Aufgaben automatisch geschlossen werden
CLOSE_TASKS_ON_STAGES = {"enrolled", "declined", "archived"}


async def execute_stage_effects(
    application_id: str,
    old_stage: str,
    new_stage: str,
    actor_id: str,
):
    """
    Fuehrt alle Seiteneffekte eines Statuswechsels aus.
    Non-blocking: Fehler werden geloggt, aber nicht geworfen.
    """
    db = get_db()

    try:
        app = await db.applications.find_one(
            {"_id": ObjectId(application_id)},
            {"applicant_id": 1, "applicant_name": 1, "assigned_to": 1},
        )
        if not app:
            return

        applicant_name = app.get("applicant_name", "Bewerber")
        assigned_to = app.get("assigned_to", actor_id)

        # 1. Offene Aufgaben schliessen bei Terminal-Stages
        if new_stage in CLOSE_TASKS_ON_STAGES:
            closed = await db.tasks.update_many(
                {"application_id": application_id, "status": {"$in": ["open", "in_progress"]}},
                {"$set": {
                    "status": "done",
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "closed_by": "system",
                    "close_reason": f"Status auf {new_stage} gesetzt",
                }},
            )
            if closed.modified_count > 0:
                logger.info(
                    f"[STAGE_EFFECTS] {closed.modified_count} Aufgaben geschlossen "
                    f"fuer Application {application_id} (-> {new_stage})"
                )

        # 2. Neue kontextuelle Aufgaben erzeugen
        task_templates = STAGE_TASKS.get(new_stage, [])
        for tmpl in task_templates:
            await db.tasks.insert_one({
                "application_id": application_id,
                "title": tmpl["title"],
                "description": tmpl.get("description", ""),
                "priority": tmpl.get("priority", "medium"),
                "status": "open",
                "assigned_to": assigned_to,
                "created_by": "system",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "due_date": None,
                "source": "stage_effect",
                "trigger_stage": new_stage,
            })

        if task_templates:
            logger.info(
                f"[STAGE_EFFECTS] {len(task_templates)} Aufgaben erzeugt "
                f"fuer Application {application_id} (-> {new_stage})"
            )

        # 3. Staff-Notification bei relevanten Stages
        if new_stage in {"enrolled", "declined"}:
            staff_users = await db.users.find(
                {"role": {"$in": ["superadmin", "admin", "staff"]}, "active": True},
                {"_id": 1},
            ).to_list(20)
            stage_label = "eingeschrieben" if new_stage == "enrolled" else "abgelehnt"
            for su in staff_users:
                if str(su["_id"]) != actor_id:
                    await create_notification(
                        str(su["_id"]),
                        "stage_changed",
                        f"{applicant_name}: Status auf '{stage_label}' geaendert",
                        link=f"/staff/applicants/{application_id}",
                        triggered_by=actor_id,
                    )

        # 4. Audit
        await write_audit_log(
            "stage_effects_executed", "system", "application", application_id,
            {
                "old_stage": old_stage,
                "new_stage": new_stage,
                "tasks_created": len(task_templates),
                "tasks_closed": new_stage in CLOSE_TASKS_ON_STAGES,
            },
        )

    except Exception as e:
        logger.error(f"[STAGE_EFFECTS] Fehler fuer {application_id}: {e}")


async def execute_payment_stage_advance(invoice_number: str):
    """
    Pflichtlogik aus 14_tracking_kpis: invoice_paid → stage_advance + staff_notice.
    Prueft ob die Application in einem zahlungsrelevanten Stage ist und setzt weiter.
    """
    db = get_db()

    try:
        invoice = await db.invoices.find_one({"invoice_number": invoice_number})
        if not invoice:
            return

        app_id = invoice.get("application_id")
        if not app_id:
            return

        app = await db.applications.find_one({"_id": ObjectId(app_id)})
        if not app:
            return

        current_stage = app.get("current_stage")

        # Zahlungsbasierter Stage-Advance: conditional_offer oder offer_sent → enrolled
        advance_map = {
            "conditional_offer": "offer_sent",
            "offer_sent": "enrolled",
        }

        next_stage = advance_map.get(current_stage)
        if not next_stage:
            logger.info(
                f"[PAYMENT_ADVANCE] Kein Auto-Advance fuer Stage '{current_stage}' "
                f"(Application {app_id})"
            )
            return

        await db.applications.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {
                "current_stage": next_stage,
                "last_activity_at": datetime.now(timezone.utc),
                "updated_by": "system",
            }},
        )

        await db.application_activities.insert_one({
            "application_id": str(app_id),
            "action": "stage_changed",
            "old_value": current_stage,
            "new_value": next_stage,
            "actor_id": "system",
            "occurred_at": datetime.now(timezone.utc),
            "trigger": "payment_received",
        })

        # Stage-Effects ausfuehren
        await execute_stage_effects(str(app_id), current_stage, next_stage, "system")

        # Staff benachrichtigen
        applicant_name = app.get("applicant_name", invoice.get("applicant_name", "Bewerber"))
        staff_users = await db.users.find(
            {"role": {"$in": ["superadmin", "admin", "staff"]}, "active": True},
            {"_id": 1},
        ).to_list(20)
        for su in staff_users:
            await create_notification(
                str(su["_id"]),
                "payment_received",
                f"Zahlung eingegangen: {applicant_name} – Rechnung {invoice_number}. "
                f"Status automatisch auf '{next_stage}' gesetzt.",
                link=f"/staff/applicants/{app_id}",
                triggered_by="stripe_webhook",
            )

        await write_audit_log(
            "payment_stage_advance", "system", "application", str(app_id),
            {"invoice": invoice_number, "old_stage": current_stage, "new_stage": next_stage},
        )

        logger.info(
            f"[PAYMENT_ADVANCE] Application {app_id}: {current_stage} -> {next_stage} "
            f"(Rechnung {invoice_number})"
        )

    except Exception as e:
        logger.error(f"[PAYMENT_ADVANCE] Fehler fuer Rechnung {invoice_number}: {e}")
