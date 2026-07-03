"""
WhatsApp Business API Integration via Twilio.

Feature ist optional: Ohne TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN /
TWILIO_WHATSAPP_FROM bleibt die Integration deaktiviert.

Alle ausgehenden Nachrichten werden zusätzlich in `whatsapp_messages`
protokolliert (Audit / Diagnose).
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "")  # z.B. whatsapp:+14155238886


def is_configured() -> bool:
    return bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_FROM)


def _client():
    from twilio.rest import Client
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def _normalize_to(phone: str) -> Optional[str]:
    """Sicherstellen, dass Nummer im E.164 + whatsapp:-Prefix ist."""
    if not phone:
        return None
    p = phone.strip()
    if p.startswith("whatsapp:"):
        return p
    if not p.startswith("+"):
        # Ohne Ländercode können wir nicht raten – die Nummer wird verworfen
        return None
    return f"whatsapp:{p}"


async def send_message(to_phone: str, body: str, applicant_id: Optional[str] = None, metadata: Optional[dict] = None) -> dict:
    """Sendet eine WhatsApp-Nachricht via Twilio und persistiert das Log."""
    from database import get_db
    db = get_db()
    log_doc = {
        "to": to_phone,
        "body": body[:1000],
        "applicant_id": applicant_id,
        "status": "queued",
        "sid": None,
        "error": None,
        "metadata": metadata or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if not is_configured():
        log_doc["status"] = "skipped"
        log_doc["error"] = "twilio_not_configured"
        await db.whatsapp_messages.insert_one(log_doc)
        return {"status": "skipped", "reason": "twilio_not_configured"}

    to_e164 = _normalize_to(to_phone)
    if not to_e164:
        log_doc["status"] = "invalid"
        log_doc["error"] = "invalid_phone"
        await db.whatsapp_messages.insert_one(log_doc)
        return {"status": "error", "reason": "invalid_phone"}

    try:
        client = _client()
        msg = client.messages.create(from_=TWILIO_WHATSAPP_FROM, to=to_e164, body=body)
        log_doc["status"] = "sent"
        log_doc["sid"] = msg.sid
        await db.whatsapp_messages.insert_one(log_doc)
        return {"status": "sent", "sid": msg.sid}
    except Exception as e:
        log_doc["status"] = "failed"
        log_doc["error"] = str(e)[:400]
        await db.whatsapp_messages.insert_one(log_doc)
        logger.error(f"[WA] Send failed: {e}")
        return {"status": "error", "reason": str(e)[:200]}


async def get_status() -> dict:
    return {
        "configured": is_configured(),
        "from_number": TWILIO_WHATSAPP_FROM if is_configured() else None,
        "account_sid_prefix": TWILIO_ACCOUNT_SID[:6] + "…" if TWILIO_ACCOUNT_SID else None,
    }


async def recent_messages(limit: int = 50) -> list:
    from database import get_db
    db = get_db()
    docs = await db.whatsapp_messages.find({}).sort("created_at", -1).limit(limit).to_list(limit)
    out = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        out.append(d)
    return out
