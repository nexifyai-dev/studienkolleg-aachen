"""
Stripe Payment Router – Rechnungszahlung via Stripe Checkout.

Endpunkte:
- POST /api/payments/checkout       – Checkout-Session fuer Rechnung erstellen
- GET  /api/payments/status/{sid}   – Zahlungsstatus abfragen
- POST /api/webhook/stripe          – Stripe Webhook Handler
- GET  /api/payments/transactions   – Zahlungsverlauf (Staff)

Sicherheit:
- Betrag wird IMMER serverseitig aus der Rechnung geladen (kein Frontend-Override)
- payment_transactions Collection speichert jeden Zahlungsvorgang
"""
import logging
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")


@router.post("/checkout")
async def create_checkout(
    body: dict,
    request: Request,
    user: dict = Depends(get_current_user),
):
    """
    Erstellt eine Stripe Checkout Session fuer eine Rechnung.
    Betrag wird serverseitig aus der DB gelesen – kein Frontend-Override.
    """
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Stripe nicht konfiguriert")

    from emergentintegrations.payments.stripe.checkout import (
        StripeCheckout, CheckoutSessionRequest,
    )

    invoice_number = body.get("invoice_number")
    origin_url = body.get("origin_url", "")
    if not invoice_number:
        raise HTTPException(status_code=400, detail="invoice_number erforderlich")
    if not origin_url:
        raise HTTPException(status_code=400, detail="origin_url erforderlich")

    db = get_db()
    invoice = await db.invoices.find_one({"invoice_number": invoice_number})
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")

    if invoice.get("status") == "paid":
        raise HTTPException(status_code=400, detail="Rechnung ist bereits bezahlt")
    if invoice.get("status") == "cancelled":
        raise HTTPException(status_code=400, detail="Rechnung ist storniert")

    amount = float(invoice.get("amount", 0))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Rechnungsbetrag ungueltig")

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

    success_url = f"{origin_url}/staff/invoices?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/staff/invoices?payment=cancelled"

    checkout_req = CheckoutSessionRequest(
        amount=amount,
        currency="eur",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "invoice_number": invoice_number,
            "applicant_name": invoice.get("applicant_name", ""),
            "user_email": user.get("email", ""),
        },
    )

    session = await stripe_checkout.create_checkout_session(checkout_req)

    # Payment Transaction erstellen
    tx = {
        "session_id": session.session_id,
        "invoice_number": invoice_number,
        "amount": amount,
        "currency": "eur",
        "payment_status": "initiated",
        "status": "pending",
        "user_id": user.get("id"),
        "user_email": user.get("email"),
        "applicant_name": invoice.get("applicant_name", ""),
        "metadata": {
            "invoice_number": invoice_number,
            "applicant_name": invoice.get("applicant_name", ""),
        },
        "created_at": datetime.now(timezone.utc),
    }
    await db.payment_transactions.insert_one(tx)

    return {
        "url": session.url,
        "session_id": session.session_id,
        "amount": amount,
        "currency": "eur",
    }


@router.get("/status/{session_id}")
async def get_payment_status(
    session_id: str,
    user: dict = Depends(get_current_user),
):
    """Fragt den Zahlungsstatus bei Stripe ab und aktualisiert die DB."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=503, detail="Stripe nicht konfiguriert")

    from emergentintegrations.payments.stripe.checkout import StripeCheckout

    db = get_db()
    tx = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not tx:
        raise HTTPException(status_code=404, detail="Transaktion nicht gefunden")

    # Status bei Stripe abfragen
    host_url = str("https://placeholder.com")
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")

    try:
        status = await stripe_checkout.get_checkout_status(session_id)
    except Exception as e:
        logger.error(f"[STRIPE] Status-Abfrage fehlgeschlagen: {e}")
        raise HTTPException(status_code=502, detail="Stripe-Abfrage fehlgeschlagen")

    # Nur einmal auf 'paid' setzen (Idempotenz)
    if status.payment_status == "paid" and tx.get("payment_status") != "paid":
        invoice_number = tx.get("invoice_number")
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "payment_status": "paid",
                "status": "completed",
                "paid_at": datetime.now(timezone.utc),
            }},
        )
        # Rechnung auf 'paid' setzen
        if invoice_number:
            await db.invoices.update_one(
                {"invoice_number": invoice_number},
                {"$set": {
                    "status": "paid",
                    "paid_at": datetime.now(timezone.utc).isoformat(),
                    "payment_method": "stripe",
                    "stripe_session_id": session_id,
                }},
            )
            logger.info(f"[STRIPE] Rechnung {invoice_number} als bezahlt markiert")
    elif status.payment_status != "paid":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": status.payment_status, "status": status.status}},
        )

    return {
        "session_id": session_id,
        "status": status.status,
        "payment_status": status.payment_status,
        "amount_total": status.amount_total,
        "currency": status.currency,
        "invoice_number": tx.get("invoice_number"),
    }


webhook_router = APIRouter(tags=["stripe-webhook"])


@webhook_router.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Stripe Webhook – verarbeitet Payment-Events."""
    if not STRIPE_API_KEY:
        return {"ok": False}

    from emergentintegrations.payments.stripe.checkout import StripeCheckout

    body = await request.body()
    sig = request.headers.get("Stripe-Signature", "")

    host_url = str(request.base_url).rstrip("/")
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}/api/webhook/stripe")

    try:
        event = await stripe_checkout.handle_webhook(body, sig)
    except Exception as e:
        logger.warning(f"[STRIPE] Webhook Fehler: {e}")
        return {"ok": False, "error": str(e)}

    db = get_db()
    session_id = event.session_id

    if event.payment_status == "paid":
        tx = await db.payment_transactions.find_one({"session_id": session_id})
        if tx and tx.get("payment_status") != "paid":
            invoice_number = tx.get("invoice_number")
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "payment_status": "paid",
                    "status": "completed",
                    "paid_at": datetime.now(timezone.utc),
                }},
            )
            if invoice_number:
                await db.invoices.update_one(
                    {"invoice_number": invoice_number},
                    {"$set": {
                        "status": "paid",
                        "paid_at": datetime.now(timezone.utc).isoformat(),
                        "payment_method": "stripe",
                        "stripe_session_id": session_id,
                    }},
                )
                logger.info(f"[STRIPE:webhook] Rechnung {invoice_number} als bezahlt markiert")

                # Payment → Stage-Advance Automation
                try:
                    from services.stage_effects import execute_payment_stage_advance
                    await execute_payment_stage_advance(invoice_number)
                except Exception as adv_err:
                    logger.error(f"[STRIPE:webhook] Stage-Advance fehlgeschlagen: {adv_err}")

                # Bewerber-Benachrichtigung
                try:
                    import uuid as _uuid
                    inv = await db.invoices.find_one({"invoice_number": invoice_number}, {"_id": 0, "application_id": 1, "applicant_id": 1, "amount": 1})
                    if inv and inv.get("applicant_id"):
                        await db.notifications.insert_one({
                            "id": str(_uuid.uuid4()),
                            "user_id": inv["applicant_id"],
                            "type": "payment_confirmed",
                            "title": "Zahlung bestaetigt",
                            "message": f"Ihre Zahlung fuer Rechnung {invoice_number} ({inv.get('amount', 0):.2f} EUR) wurde erfolgreich verarbeitet.",
                            "read": False,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        })
                        logger.info(f"[STRIPE:webhook] Bewerber {inv['applicant_id']} benachrichtigt")
                except Exception as notify_err:
                    logger.warning(f"[STRIPE:webhook] Benachrichtigung fehlgeschlagen: {notify_err}")

    return {"ok": True, "event_type": event.event_type}


@router.get("/transactions")
async def list_transactions(
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Listet alle Zahlungstransaktionen (Staff only, neueste zuerst)."""
    db = get_db()
    txs = await db.payment_transactions.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    for tx in txs:
        if isinstance(tx.get("created_at"), datetime):
            tx["created_at"] = tx["created_at"].isoformat()
        if isinstance(tx.get("paid_at"), datetime):
            tx["paid_at"] = tx["paid_at"].isoformat()
    return txs
