"""
Dunning Service – Automatisches Mahnwesen fuer ueberfaellige Rechnungen.

Wird vom Scheduler periodisch aufgerufen.
Identifiziert ueberfaellige Rechnungen und versendet gestaffelte Mahnungen:
  - 1. Mahnung: 3 Tage nach Faelligkeit
  - 2. Mahnung: 10 Tage nach Faelligkeit
  - 3. Mahnung: 21 Tage nach Faelligkeit (mit Eskalation)
"""
import logging
from datetime import datetime, timezone, timedelta
from database import get_db

logger = logging.getLogger(__name__)


async def check_overdue_invoices():
    """Prueft Rechnungen auf Faelligkeit und versetzt Status / versendet Mahnungen."""
    db = get_db()
    now = datetime.now(timezone.utc)

    overdue_invoices = await db.invoices.find({
        "status": {"$in": ["sent", "draft", "overdue"]},
        "due_date": {"$ne": None},
    }).to_list(200)

    if not overdue_invoices:
        logger.info("[DUNNING] Keine offenen Rechnungen mit Faelligkeitsdatum")
        return

    reminded = 0
    escalated = 0

    for inv in overdue_invoices:
        due_str = inv.get("due_date")
        if not due_str:
            continue

        try:
            if isinstance(due_str, str):
                due_date = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
            else:
                due_date = due_str
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue

        days_overdue = (now - due_date).days
        if days_overdue < 1:
            continue

        inv_id = str(inv["_id"])
        inv_number = inv.get("invoice_number", inv_id)
        current_reminders = inv.get("dunning_count", 0)

        # Status auf overdue setzen falls noch nicht geschehen
        if inv.get("status") != "overdue":
            await db.invoices.update_one(
                {"_id": inv["_id"]},
                {"$set": {"status": "overdue", "updated_at": now.isoformat()}}
            )

        # Gestaffelte Mahnung
        should_remind = False
        if days_overdue >= 3 and current_reminders < 1:
            should_remind = True
        elif days_overdue >= 10 and current_reminders < 2:
            should_remind = True
        elif days_overdue >= 21 and current_reminders < 3:
            should_remind = True
            escalated += 1

        if should_remind:
            new_count = current_reminders + 1
            await db.invoices.update_one(
                {"_id": inv["_id"]},
                {"$set": {
                    "dunning_count": new_count,
                    "last_dunning_at": now.isoformat(),
                    "updated_at": now.isoformat(),
                }}
            )

            # E-Mail versenden
            applicant_email = inv.get("applicant_email", "")
            applicant_name = inv.get("applicant_name", "")
            amount = inv.get("amount", 0)
            currency = inv.get("currency", "EUR")

            if applicant_email:
                try:
                    # Sprache des Bewerbers ermitteln
                    lang = "de"
                    if inv.get("applicant_id"):
                        from bson import ObjectId
                        user = await db.users.find_one(
                            {"_id": ObjectId(inv["applicant_id"])},
                            {"language_pref": 1}
                        )
                        if user:
                            lang = user.get("language_pref", "de")

                    from services.email import send_payment_reminder
                    send_payment_reminder(
                        to=applicant_email,
                        full_name=applicant_name,
                        invoice_number=inv_number,
                        amount=amount,
                        currency=currency,
                        days_overdue=days_overdue,
                        reminder_level=new_count,
                        lang=lang,
                    )
                    reminded += 1
                except Exception as e:
                    logger.error(f"[DUNNING] Mahnung fehlgeschlagen fuer {inv_number}: {e}")

            # Audit
            from services.audit import write_audit_log
            await write_audit_log(
                "dunning_sent", "system", "invoice", inv_id,
                {"level": new_count, "days_overdue": days_overdue}
            )

            # Eskalation bei 3. Mahnung: Staff benachrichtigen
            if new_count >= 3:
                from services.notifications import create_notification
                admins = await db.users.find(
                    {"role": {"$in": ["superadmin", "admin", "accounting_staff", "staff"]}},
                    {"_id": 1}
                ).to_list(20)
                for admin in admins:
                    await create_notification(
                        str(admin["_id"]),
                        "invoice_escalated",
                        f"3. Mahnung: Rechnung {inv_number} ({amount:.2f} {currency}) – {days_overdue} Tage ueberfaellig",
                        link="/staff/invoices",
                        triggered_by="dunning_service",
                    )

    logger.info(f"[DUNNING] Pruefung abgeschlossen: {reminded} Mahnungen, {escalated} Eskalationen")
