"""
Messaging router – Echte Kommunikationszentrale.

Channels: portal (In-App), email (vorbereitet), whatsapp (Link only).
Conversation fields:
  - channel: portal | email | whatsapp
  - status: open | answered | escalated | closed
  - assigned_to: Staff-User-ID
  - application_id: Fallbezug
  - subject: Thread-Betreff (optional)
  - sla_due: Deadline fuer SLA
  - participants: [user_id, ...]

Message fields:
  - channel, visibility (public | internal), content, sender_id, sent_at, read
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
from models.schemas import MessageCreate, to_str_id

router = APIRouter(prefix="/api", tags=["messaging"])

MAX_MSG_LENGTH = 5000
VALID_CHANNELS = ["portal", "email", "whatsapp"]
VALID_STATUSES = ["open", "answered", "escalated", "closed"]

# --- Central Email Signature ---
EMAIL_SIGNATURE_DE = """
--
Studienkolleg Aachen / Way2Germany
Templergraben 55, 52062 Aachen
Tel: +49 241 80911 | info@stk-aachen.de
www.studienkolleg-aachen.de

Diese Nachricht wurde ueber das W2G-System versendet.
""".strip()

EMAIL_SIGNATURE_EN = """
--
Studienkolleg Aachen / Way2Germany
Templergraben 55, 52062 Aachen
Phone: +49 241 80911 | info@stk-aachen.de
www.studienkolleg-aachen.de

This message was sent via the W2G platform.
""".strip()


def _serialize_conv(conv: dict) -> dict:
    conv = to_str_id(conv)
    for k in ("created_at", "last_message_at", "sla_due"):
        if hasattr(conv.get(k), "isoformat"):
            conv[k] = conv[k].isoformat()
    return conv


def _serialize_msg(msg: dict) -> dict:
    msg = to_str_id(msg)
    if hasattr(msg.get("sent_at"), "isoformat"):
        msg["sent_at"] = msg["sent_at"].isoformat()
    # Preserve html_content for email rendering
    return msg


async def _find_staff_user(db) -> str | None:
    for role in ["superadmin", "admin", "staff"]:
        u = await db.users.find_one({"role": role, "active": True}, {"_id": 1})
        if u:
            return str(u["_id"])
    return None


async def _enrich_conversations(db, convs: list, current_user_id: str = None) -> list:
    if not convs:
        return []

    user_ids = set()
    app_ids = set()
    for c in convs:
        for pid in c.get("participants", []):
            user_ids.add(pid)
        if c.get("assigned_to"):
            user_ids.add(c["assigned_to"])
        if c.get("application_id"):
            app_ids.add(c["application_id"])

    user_map = {}
    if user_ids:
        try:
            users = await db.users.find(
                {"_id": {"$in": [ObjectId(uid) for uid in user_ids if len(uid) == 24]}},
                {"full_name": 1, "email": 1, "role": 1},
            ).to_list(None)
            for u in users:
                uid = str(u["_id"])
                user_map[uid] = {"name": u.get("full_name") or u.get("email", ""), "role": u.get("role", "")}
        except Exception:
            pass

    app_map = {}
    if app_ids:
        try:
            apps = await db.applications.find(
                {"_id": {"$in": [ObjectId(aid) for aid in app_ids if len(aid) == 24]}},
                {"applicant_id": 1, "current_stage": 1, "course_type": 1},
            ).to_list(None)
            for a in apps:
                app_map[str(a["_id"])] = {
                    "stage": a.get("current_stage", ""),
                    "course_type": a.get("course_type", ""),
                    "applicant_id": a.get("applicant_id", ""),
                }
        except Exception:
            pass

    serialized_convs = [_serialize_conv(c) for c in convs]
    conv_ids = [sc["id"] for sc in serialized_convs]

    # Last message per conversation
    msg_map = {}
    if conv_ids:
        try:
            pipeline = [
                {"$match": {"conversation_id": {"$in": conv_ids}}},
                {"$sort": {"sent_at": -1}},
                {"$group": {"_id": "$conversation_id", "last": {"$first": "$$ROOT"}}},
            ]
            last_msgs = await db.messages.aggregate(pipeline).to_list(None)
            msg_map = {m["_id"]: m["last"] for m in last_msgs}
        except Exception:
            pass

    # Unread count per conversation for current user
    unread_map = {}
    if conv_ids and current_user_id:
        try:
            pipeline = [
                {"$match": {"conversation_id": {"$in": conv_ids}, "sender_id": {"$ne": current_user_id}, "read": False, "visibility": {"$ne": "internal"}}},
                {"$group": {"_id": "$conversation_id", "count": {"$sum": 1}}},
            ]
            unread_results = await db.messages.aggregate(pipeline).to_list(None)
            unread_map = {r["_id"]: r["count"] for r in unread_results}
        except Exception:
            pass

    enriched = []
    for sc in serialized_convs:
        sc["participant_names"] = {pid: user_map.get(pid, {}).get("name", "Unbekannt") for pid in sc.get("participants", [])}
        sc["participant_roles"] = {pid: user_map.get(pid, {}).get("role", "") for pid in sc.get("participants", [])}

        # Fuer E-Mail-Conversations: externen Absendernamen verwenden
        ext_email = sc.get("external_email", "")
        ext_name = sc.get("external_name", "")
        if ext_email and not ext_name:
            ext_name = ext_email.split("@")[0].replace(".", " ").title()
        if ext_name or ext_email:
            sc["display_name"] = ext_name or ext_email
        else:
            # Participant-Name (nicht Staff/Admin)
            others = {pid: n for pid, n in sc["participant_names"].items()
                      if user_map.get(pid, {}).get("role") not in ("staff", "admin", "superadmin", "accounting_staff")}
            sc["display_name"] = next(iter(others.values()), "") if others else ""

        if "channel" not in sc:
            sc["channel"] = "portal"
        if "status" not in sc:
            sc["status"] = "open"
        sc["assigned_to_name"] = user_map.get(sc.get("assigned_to", ""), {}).get("name", "")
        sc["unread_count"] = unread_map.get(sc["id"], 0)

        # Application context
        aid = sc.get("application_id", "")
        if aid and aid in app_map:
            sc["case_stage"] = app_map[aid].get("stage", "")
            sc["case_course"] = app_map[aid].get("course_type", "")
        
        last_msg = msg_map.get(sc["id"])
        if last_msg:
            content = last_msg.get("content", "")
            sc["last_message_preview"] = (content[:80] + "...") if len(content) > 80 else content
            sc["last_message_sender"] = last_msg.get("sender_id", "")
            sc["last_message_channel"] = last_msg.get("channel", sc.get("channel", "portal"))
        enriched.append(sc)
    return enriched


@router.get("/conversations")
async def list_conversations(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    channel = request.query_params.get("channel")
    status = request.query_params.get("status")
    assigned = request.query_params.get("assigned_to")
    app_id = request.query_params.get("application_id")
    unread_only = request.query_params.get("unread") == "true"

    if user["role"] == "applicant":
        query["participants"] = user["id"]
    if channel and channel in VALID_CHANNELS:
        query["channel"] = channel
    if status and status in VALID_STATUSES:
        query["status"] = status
    if assigned:
        query["assigned_to"] = assigned
    if app_id:
        query["application_id"] = app_id

    limit_param = request.query_params.get("limit")
    skip_param = request.query_params.get("skip")
    max_limit = 50 if user["role"] == "applicant" else 200
    limit = min(int(limit_param), max_limit) if limit_param and limit_param.isdigit() else max_limit
    skip = int(skip_param) if skip_param and skip_param.isdigit() else 0

    total = await db.conversations.count_documents(query)
    convs = await db.conversations.find(
        query,
        {"participants": 1, "channel": 1, "status": 1, "assigned_to": 1, "application_id": 1, "last_message_at": 1, "subject": 1, "is_support": 1, "created_at": 1, "external_email": 1, "external_name": 1}
    ).sort("last_message_at", -1).skip(skip).to_list(limit)
    enriched = await _enrich_conversations(db, convs, user["id"])

    if unread_only:
        enriched = [c for c in enriched if c.get("unread_count", 0) > 0]

    return {"conversations": enriched, "total": total, "skip": skip, "limit": limit}


@router.get("/conversations/support")
async def get_or_create_support_conversation(user: dict = Depends(get_current_user)):
    db = get_db()
    existing = await db.conversations.find_one({
        "participants": user["id"],
        "is_support": True,
    })
    if existing:
        result = await _enrich_conversations(db, [existing], user["id"])
        return result[0]

    staff_id = await _find_staff_user(db)
    participants = [user["id"]]
    if staff_id:
        participants.append(staff_id)

    now = datetime.now(timezone.utc)
    conv_doc = {
        "participants": participants,
        "is_support": True,
        "channel": "portal",
        "status": "open",
        "created_at": now,
        "last_message_at": now,
    }
    result = await db.conversations.insert_one(conv_doc)
    conv_doc["_id"] = result.inserted_id
    enriched = await _enrich_conversations(db, [conv_doc], user["id"])
    return enriched[0]


@router.get("/conversations/stats")
async def conversation_stats(user: dict = Depends(get_current_user)):
    db = get_db()
    pipeline = [
        {"$group": {"_id": "$channel", "count": {"$sum": 1}}},
    ]
    results = await db.conversations.aggregate(pipeline).to_list(None)
    stats = {"portal": 0, "email": 0, "whatsapp": 0, "total": 0}
    for r in results:
        ch = r["_id"] or "portal"
        if ch in stats:
            stats[ch] = r["count"]
        stats["total"] += r["count"]

    # Status counts
    status_pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
    ]
    status_results = await db.conversations.aggregate(status_pipeline).to_list(None)
    stats["open"] = 0
    stats["answered"] = 0
    stats["escalated"] = 0
    stats["closed"] = 0
    for r in status_results:
        st = r["_id"] or "open"
        if st in stats:
            stats[st] = r["count"]

    if user["role"] in STAFF_ROLES:
        unread = await db.messages.count_documents({"read": False, "sender_id": {"$ne": user["id"]}, "visibility": {"$ne": "internal"}})
        stats["unread"] = unread
    else:
        stats["unread"] = 0
    return stats


@router.put("/conversations/{conv_id}")
async def update_conversation(conv_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Update conversation metadata (status, assigned_to, application_id, subject)."""
    db = get_db()
    if user["role"] not in STAFF_ROLES:
        raise HTTPException(status_code=403, detail="Nur Staff kann Konversationen bearbeiten")
    body = await request.json()
    update = {}
    if "status" in body and body["status"] in VALID_STATUSES:
        update["status"] = body["status"]
    if "assigned_to" in body:
        update["assigned_to"] = body["assigned_to"]
    if "application_id" in body:
        update["application_id"] = body["application_id"]
    if "subject" in body:
        update["subject"] = body["subject"]
    if not update:
        raise HTTPException(status_code=400, detail="Keine aenderbaren Felder")
    try:
        await db.conversations.update_one({"_id": ObjectId(conv_id)}, {"$set": update})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    return {"status": "ok", "updated": list(update.keys())}


@router.post("/messages")
async def send_message(data: MessageCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    content = data.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Nachricht darf nicht leer sein")
    if len(content) > MAX_MSG_LENGTH:
        raise HTTPException(status_code=400, detail=f"Nachricht zu lang (max {MAX_MSG_LENGTH} Zeichen)")

    channel = getattr(data, 'channel', 'portal') or 'portal'
    if channel not in VALID_CHANNELS:
        channel = 'portal'

    visibility = getattr(data, 'visibility', 'public') or 'public'

    conv_id = data.conversation_id
    if conv_id:
        try:
            conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Ungueltige Konversations-ID")
        if not conv:
            raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
        if user["role"] == "applicant" and user["id"] not in conv.get("participants", []):
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        participants = [user["id"]]
        if data.recipient_id:
            try:
                recipient = await db.users.find_one({"_id": ObjectId(data.recipient_id)}, {"_id": 1})
            except Exception:
                raise HTTPException(status_code=400, detail="Ungueltige Empfaenger-ID")
            if not recipient:
                raise HTTPException(status_code=404, detail="Empfaenger nicht gefunden")
            participants.append(data.recipient_id)
        else:
            staff_id = await _find_staff_user(db)
            if staff_id and staff_id != user["id"]:
                participants.append(staff_id)

        now = datetime.now(timezone.utc)
        sla_due = now + timedelta(hours=24)
        result = await db.conversations.insert_one({
            "participants": participants,
            "application_id": data.application_id,
            "is_support": True,
            "channel": channel,
            "status": "open",
            "assigned_to": participants[1] if len(participants) > 1 and user["role"] == "applicant" else user["id"],
            "sla_due": sla_due,
            "created_at": now,
            "last_message_at": now,
        })
        conv_id = str(result.inserted_id)

    now = datetime.now(timezone.utc)
    msg = {
        "conversation_id": conv_id,
        "content": content,
        "sender_id": user["id"],
        "sender_name": user.get("full_name") or user.get("email", ""),
        "visibility": visibility,
        "channel": channel,
        "sent_at": now,
        "read": False,
    }
    result = await db.messages.insert_one(msg)

    # Auto-update conversation status
    conv_update = {"last_message_at": now}
    if user["role"] in STAFF_ROLES:
        conv_update["status"] = "answered"
    elif user["role"] == "applicant":
        conv_update["status"] = "open"
    await db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": conv_update},
    )

    # If channel is email and user is staff, also send via SMTP
    if channel == "email" and user["role"] in STAFF_ROLES:
        try:
            conv_doc = await db.conversations.find_one({"_id": ObjectId(conv_id)})
            # Find recipient email
            recipient_email = conv_doc.get("external_email", "")
            if not recipient_email:
                for pid in conv_doc.get("participants", []):
                    if pid != user["id"]:
                        try:
                            recip = await db.users.find_one({"_id": ObjectId(pid)}, {"email": 1})
                            if recip:
                                recipient_email = recip.get("email", "")
                                break
                        except Exception:
                            pass
            if recipient_email:
                from services.email_service import send_email as smtp_send, is_configured
                if is_configured():
                    subject = conv_doc.get("subject", "") or "Nachricht vom Studienkolleg Aachen"
                    smtp_send(
                        to_email=recipient_email,
                        subject=subject,
                        body=content,
                        sender_name=user.get("full_name", "Staff"),
                        sender_role=user.get("role", "staff"),
                    )
        except Exception:
            pass  # SMTP-Fehler nicht blockierend

    msg.pop("_id", None)
    msg["id"] = str(result.inserted_id)
    msg["sent_at"] = now.isoformat()
    return msg


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not conv:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
    if user["role"] == "applicant" and user["id"] not in conv.get("participants", []):
        raise HTTPException(status_code=403, detail="Forbidden")

    query = {"conversation_id": conv_id}
    # Applicants cannot see internal notes
    if user["role"] == "applicant":
        query["visibility"] = {"$ne": "internal"}

    msgs = await db.messages.find(query).sort("sent_at", 1).to_list(500)
    return [_serialize_msg(m) for m in msgs]


@router.put("/messages/{msg_id}/read")
async def mark_message_read(msg_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        await db.messages.update_one({"_id": ObjectId(msg_id)}, {"$set": {"read": True}})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    return {"status": "ok"}


@router.put("/conversations/{conv_id}/read-all")
async def mark_conversation_read(conv_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await db.messages.update_many(
        {"conversation_id": conv_id, "sender_id": {"$ne": user["id"]}, "read": False},
        {"$set": {"read": True}},
    )
    return {"status": "ok"}


@router.get("/email-signature")
async def get_email_signature(request: Request, user: dict = Depends(get_current_user)):
    """Return per-user email signature (fallback to central default)."""
    db = get_db()
    lang = request.query_params.get("lang", "de")
    reset = request.query_params.get("reset")
    sender_name = user.get("full_name") or user.get("email", "")
    sender_role = user.get("role", "staff")
    role_label = {
        "admin": "Administration",
        "superadmin": "Administration",
        "staff": "Studienberatung",
        "teacher": "Lehrkraft",
    }.get(sender_role, "Team")

    # If reset requested, delete custom signature and return default
    if reset:
        await db.user_signatures.delete_one({"user_id": user["id"]})

    # Check for per-user signature in DB (only if not resetting)
    if not reset:
        user_sig = await db.user_signatures.find_one({"user_id": user["id"]}, {"_id": 0})
        if user_sig and user_sig.get("signature"):
            return {"signature": user_sig["signature"], "sender_name": sender_name, "sender_role": role_label, "is_custom": True}

    # Default signature
    sig = EMAIL_SIGNATURE_EN if lang == "en" else EMAIL_SIGNATURE_DE
    header = f"Mit freundlichen Gruessen,\n{sender_name}\n{role_label}" if lang == "de" else f"Best regards,\n{sender_name}\n{role_label}"
    return {"signature": f"{header}\n\n{sig}", "sender_name": sender_name, "sender_role": role_label, "is_custom": False}


@router.put("/email-signature")
async def save_email_signature(request: Request, user: dict = Depends(get_current_user)):
    """Save per-user email signature."""
    db = get_db()
    body = await request.json()
    sig_text = body.get("signature", "").strip()
    if not sig_text:
        raise HTTPException(status_code=400, detail="Signatur darf nicht leer sein")

    await db.user_signatures.update_one(
        {"user_id": user["id"]},
        {"$set": {
            "user_id": user["id"],
            "user_name": user.get("full_name", ""),
            "signature": sig_text,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )
    return {"ok": True, "signature": sig_text}


def _detect_language(text: str) -> str:
    """Detect language from message text. Returns 'en' or 'de' or ''."""
    if not text or len(text.strip()) < 10:
        return ""
    sample = text[:500].lower()
    # English indicators (common words that rarely appear in German)
    en_words = {"the ", " is ", " are ", " was ", " were ", " have ", " has ",
                " would ", " could ", " should ", " will ", " can ", " this ",
                " that ", " with ", " from ", " your ", " you ", " for ",
                "dear ", "hello ", "please ", "thank ", "thanks", "regards",
                "sincerely", " my ", " am ", " been ", " which ", " their ",
                "application", "documents", "question", "information"}
    de_words = {"der ", " die ", " das ", " ist ", " sind ", " war ", " hat ",
                " haben ", " wird ", " kann ", " mit ", " fuer ", " für ",
                " und ", " oder ", " nicht ", " sich ", " wir ", " ihr ",
                "sehr geehrte", "hallo ", "bitte ", "danke", "freundlich",
                "bewerbung", "unterlagen", "studienkolleg"}
    en_count = sum(1 for w in en_words if w in sample)
    de_count = sum(1 for w in de_words if w in sample)
    if en_count > de_count and en_count >= 3:
        return "en"
    if de_count > en_count and de_count >= 3:
        return "de"
    if en_count >= 2 and de_count == 0:
        return "en"
    if de_count >= 2 and en_count == 0:
        return "de"
    return ""


@router.post("/messaging/generate-email")
async def generate_email_text(request: Request, user: dict = Depends(get_current_user)):
    """AI-powered email text generation based on conversation context and template category."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    body = await request.json()
    conversation_id = body.get("conversation_id")
    hints = body.get("hints", "")
    template_key = body.get("template", "")  # e.g. "documents_request", "status_update", etc.

    db = get_db()
    context_msgs = []
    recipient_name = ""
    recipient_lang = "de"  # Default from profile
    detected_msg_lang = ""  # Detected from actual messages
    subject = ""
    applicant_info = ""

    if conversation_id:
        try:
            conv = await db.conversations.find_one({"_id": ObjectId(conversation_id)})
            if conv:
                subject = conv.get("subject", "")
                recent = await db.messages.find(
                    {"conversation_id": conversation_id}
                ).sort("sent_at", -1).to_list(5)

                # Collect messages AND detect language from last incoming message
                last_incoming_text = ""
                for m in reversed(recent):
                    is_incoming = m.get("sender_id") != user["id"]
                    role = "Bewerber" if is_incoming else "Mitarbeiter"
                    msg_text = m.get("content", "") or ""
                    context_msgs.append(f"{role}: {msg_text[:300]}")
                    if is_incoming and msg_text.strip():
                        last_incoming_text = msg_text

                # Detect language from last incoming message
                if last_incoming_text:
                    detected_msg_lang = _detect_language(last_incoming_text)

                # Get recipient info including language preference
                for pid in conv.get("participants", []):
                    if pid != user["id"]:
                        try:
                            recip = await db.users.find_one(
                                {"_id": ObjectId(pid)},
                                {"full_name": 1, "language_pref": 1, "country": 1, "email": 1, "_id": 0}
                            )
                            if recip:
                                recipient_name = recip.get("full_name", "")
                                recipient_lang = recip.get("language_pref", "de") or "de"
                                country = recip.get("country", "")
                                if country:
                                    applicant_info += f"Land: {country}. "
                        except Exception:
                            pass
                if not recipient_name:
                    recipient_name = conv.get("external_email", "")

                # Check if there's an application linked
                app_doc = None
                for pid in conv.get("participants", []):
                    if pid != user["id"]:
                        app_doc = await db.applications.find_one(
                            {"applicant_id": pid},
                            {"current_stage": 1, "course_type": 1, "desired_start": 1, "_id": 0}
                        )
                        if app_doc:
                            if app_doc.get("current_stage"):
                                applicant_info += f"Status: {app_doc['current_stage']}. "
                            if app_doc.get("course_type"):
                                applicant_info += f"Kurs: {app_doc['course_type']}. "
                            break
        except Exception:
            pass

    # Language priority: 1) detected from incoming message, 2) explicit param, 3) profile
    lang = detected_msg_lang or body.get("lang") or recipient_lang
    is_de = lang == "de"

    sender_name = user.get("full_name", "")

    # Template-specific instructions
    TEMPLATE_INSTRUCTIONS = {
        "documents_request": {
            "de": "Fordere fehlende Unterlagen an. Erklaere welche Dokumente benoetigt werden und bis wann. Weise auf den Upload im Portal hin.",
            "en": "Request missing documents. Explain which documents are needed and by when. Point to the portal upload feature.",
        },
        "status_update": {
            "de": "Informiere ueber den aktuellen Stand der Bewerbung. Sei transparent und nenne die naechsten Schritte.",
            "en": "Inform about the current application status. Be transparent and mention next steps.",
        },
        "appointment": {
            "de": "Schlage einen Termin vor oder bestaetige einen vereinbarten Termin. Nenne Datum, Uhrzeit und Ort/Link.",
            "en": "Propose or confirm an appointment. Mention date, time, and location/link.",
        },
        "offer": {
            "de": "Gratuliere zur bedingten oder endgueltigen Zusage. Erklaere die naechsten Schritte (Zahlung, Einschreibung).",
            "en": "Congratulate on the conditional or final offer. Explain next steps (payment, enrollment).",
        },
        "rejection": {
            "de": "Teile eine Absage respektvoll und empathisch mit. Biete Alternativen an (Sprachkurs, naechstes Semester).",
            "en": "Communicate a rejection respectfully and empathetically. Offer alternatives (language course, next semester).",
        },
        "payment_reminder": {
            "de": "Erinnere freundlich an eine offene Zahlung. Nenne Rechnungsnummer und Betrag wenn bekannt.",
            "en": "Friendly reminder about an outstanding payment. Mention invoice number and amount if known.",
        },
        "welcome": {
            "de": "Begruesse einen neuen Bewerber herzlich. Erklaere kurz die naechsten Schritte und das Portal.",
            "en": "Welcome a new applicant warmly. Briefly explain next steps and the portal.",
        },
        "follow_up": {
            "de": "Frage nach dem Stand oder erinnere an eine ausstehende Aufgabe. Biete Hilfe an.",
            "en": "Follow up on status or remind about a pending task. Offer help.",
        },
    }

    template_instruction = ""
    if template_key and template_key in TEMPLATE_INSTRUCTIONS:
        tmpl = TEMPLATE_INSTRUCTIONS[template_key]
        template_instruction = tmpl.get("de" if is_de else "en", "")

    system_prompt = f"""Du bist ein professioneller Mitarbeiter des Studienkolleg Aachen (W2G Academy GmbH).
Schreibe eine {'deutsche' if is_de else 'englische'} E-Mail-Antwort.

Regeln:
- Professionell, freundlich, klar und menschlich
- Keine Signatur (wird separat angehaengt)
- Beginne mit einer passenden Anrede (z.B. "{'Guten Tag' if is_de else 'Dear'} {recipient_name},")
- Kurz und praegnant, max 5-8 Saetze
- Beziehe dich auf den Konversationsverlauf wenn vorhanden
- Wenn Hinweise vom Mitarbeiter gegeben werden, integriere diese
{'- Vorlage: ' + template_instruction if template_instruction else ''}"""

    context = ""
    if subject:
        context += f"Betreff: {subject}\n"
    if applicant_info:
        context += f"Bewerber-Info: {applicant_info}\n"
    if context_msgs:
        context += "Bisheriger Verlauf:\n" + "\n".join(context_msgs[-3:]) + "\n\n"
    if hints:
        context += f"Hinweise vom Mitarbeiter: {hints}\n"
    context += f"\nSchreibe jetzt eine passende Antwort-E-Mail {'auf Deutsch' if is_de else 'in English'}."

    from services.openrouter_provider import chat_completion, is_enabled
    if not is_enabled():
        raise HTTPException(status_code=503, detail="KI-Service nicht konfiguriert")

    result = await chat_completion(
        system_message=system_prompt,
        user_message=context,
        task="email_generation",
        override_max_tokens=1024,
        temperature=0.5,
    )

    if result.get("error"):
        raise HTTPException(status_code=502, detail=f"KI-Fehler: {result['error']}")

    return {
        "generated_text": result.get("content", ""),
        "tokens_used": result.get("tokens_used", 0),
        "detected_lang": lang,
        "recipient_name": recipient_name,
    }


@router.post("/conversations/{conv_id}/attachments")
async def upload_message_attachment(conv_id: str, request: Request, user: dict = Depends(get_current_user)):
    import base64
    from services.storage import storage, sanitize_filename, validate_upload

    db = get_db()
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige Konversations-ID")
    if not conv:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
    if user["role"] == "applicant" and user["id"] not in conv.get("participants", []):
        raise HTTPException(status_code=403, detail="Forbidden")

    body = await request.json()
    filename = sanitize_filename(body.get("filename", "attachment"))
    content_type = body.get("content_type", "application/octet-stream")
    file_data_b64 = body.get("file_data")
    message_text = body.get("content", "")

    if not file_data_b64:
        raise HTTPException(status_code=400, detail="Keine Datei-Daten")

    try:
        file_bytes = base64.b64decode(file_data_b64)
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige Datei-Kodierung")

    try:
        validate_upload(filename, len(file_bytes), content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    import uuid
    storage_key = f"messages/{conv_id}/{uuid.uuid4().hex[:8]}_{filename}"
    await storage().upload(storage_key, file_bytes, content_type)

    channel = conv.get("channel", "portal")
    now = datetime.now(timezone.utc)
    msg = {
        "conversation_id": conv_id,
        "content": message_text or f"[Datei: {filename}]",
        "sender_id": user["id"],
        "sender_name": user.get("full_name") or user.get("email", ""),
        "visibility": "public",
        "channel": channel,
        "sent_at": now,
        "read": False,
        "attachment": {
            "filename": filename,
            "content_type": content_type,
            "file_size": len(file_bytes),
            "storage_key": storage_key,
        },
    }
    result = await db.messages.insert_one(msg)
    await db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"last_message_at": now}},
    )
    msg.pop("_id", None)
    msg["id"] = str(result.inserted_id)
    msg["sent_at"] = now.isoformat()
    if "attachment" in msg:
        msg["attachment"].pop("storage_key", None)
        msg["attachment"]["id"] = msg["id"]
    return msg


@router.get("/messages/{msg_id}/attachment")
async def download_message_attachment(msg_id: str, user: dict = Depends(get_current_user)):
    from fastapi.responses import Response
    from services.storage import storage as get_storage

    db = get_db()
    try:
        msg = await db.messages.find_one({"_id": ObjectId(msg_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not msg or not msg.get("attachment"):
        raise HTTPException(status_code=404, detail="Kein Anhang gefunden")

    conv = await db.conversations.find_one({"_id": ObjectId(msg["conversation_id"])})
    if user["role"] == "applicant" and user["id"] not in (conv or {}).get("participants", []):
        raise HTTPException(status_code=403, detail="Forbidden")

    storage_key = msg["attachment"]["storage_key"]
    try:
        file_bytes = await get_storage().download(storage_key)
    except (FileNotFoundError, NotImplementedError):
        raise HTTPException(status_code=404, detail="Datei nicht gefunden")

    return Response(
        content=file_bytes,
        media_type=msg["attachment"].get("content_type", "application/octet-stream"),
        headers={"Content-Disposition": f'attachment; filename="{msg["attachment"]["filename"]}"'},
    )


@router.get("/conversations/{conv_id}/context")
async def get_conversation_context(conv_id: str, user: dict = Depends(get_current_user)):
    """Return full context for the active conversation: case info, tasks, docs, invoices."""
    db = get_db()
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not conv:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")

    context = {
        "conversation_id": conv_id,
        "application": None,
        "applicant": None,
        "tasks": [],
        "documents": [],
        "invoices": [],
    }

    # Find application
    app_id = conv.get("application_id")
    other_participant = None
    for pid in conv.get("participants", []):
        if pid != user["id"]:
            other_participant = pid
            break

    if not app_id and other_participant:
        app_doc = await db.applications.find_one({"applicant_id": other_participant})
        if app_doc:
            app_id = str(app_doc["_id"])

    if app_id:
        try:
            app_doc = await db.applications.find_one({"_id": ObjectId(app_id)})
            if app_doc:
                context["application"] = {
                    "id": str(app_doc["_id"]),
                    "current_stage": app_doc.get("current_stage", ""),
                    "course_type": app_doc.get("course_type", ""),
                    "desired_start": app_doc.get("desired_start", ""),
                    "source": app_doc.get("source", ""),
                }
                # Applicant info
                applicant_id = app_doc.get("applicant_id")
                if applicant_id:
                    user_doc = await db.users.find_one({"_id": ObjectId(applicant_id)}, {"full_name": 1, "email": 1, "phone": 1, "country": 1})
                    if user_doc:
                        context["applicant"] = {
                            "id": str(user_doc["_id"]),
                            "name": user_doc.get("full_name", ""),
                            "email": user_doc.get("email", ""),
                            "phone": user_doc.get("phone", ""),
                            "country": user_doc.get("country", ""),
                        }

                # Tasks for this application
                tasks = await db.tasks.find({"application_id": app_id}).sort("created_at", -1).to_list(10)
                context["tasks"] = [{"id": str(t["_id"]), "title": t.get("title", ""), "status": t.get("status", ""), "priority": t.get("priority", "")} for t in tasks]

                # Documents
                docs = await db.documents.find({"application_id": app_id}, {"storage_key": 0}).to_list(20)
                context["documents"] = [{"id": str(d["_id"]), "filename": d.get("filename", ""), "status": d.get("status", ""), "document_type": d.get("document_type", "")} for d in docs]

                # Invoices
                invoices = await db.invoices.find({"applicant_id": applicant_id}).sort("created_at", -1).to_list(5)
                context["invoices"] = [{"id": str(i["_id"]), "status": i.get("status", ""), "amount": i.get("amount", 0)} for i in invoices]
        except Exception:
            pass

    return context


@router.post("/messaging/send-email")
async def send_email_from_inbox(request: Request, user: dict = Depends(get_current_user)):
    """Send a real email from the messaging inbox."""
    if user["role"] not in STAFF_ROLES:
        raise HTTPException(status_code=403, detail="Nur Staff kann E-Mails senden")
    
    body = await request.json()
    to_email = body.get("to_email", "").strip()
    subject = body.get("subject", "").strip()
    content = body.get("content", "").strip()
    conv_id = body.get("conversation_id")

    if not to_email or not subject or not content:
        raise HTTPException(status_code=400, detail="to_email, subject und content erforderlich")

    from services.email_service import send_email as smtp_send
    result = smtp_send(
        to_email=to_email,
        subject=subject,
        body=content,
        sender_name=user.get("full_name", "Staff"),
        sender_role=user.get("role", "staff"),
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "E-Mail-Versand fehlgeschlagen"))

    # Log as message if conversation exists
    db = get_db()
    if conv_id:
        now = datetime.now(timezone.utc)
        msg = {
            "conversation_id": conv_id,
            "content": f"[E-Mail gesendet] An: {to_email}\nBetreff: {subject}\n\n{content}",
            "sender_id": user["id"],
            "sender_name": user.get("full_name", ""),
            "visibility": "public",
            "channel": "email",
            "sent_at": now,
            "read": True,
        }
        await db.messages.insert_one(msg)
        await db.conversations.update_one({"_id": ObjectId(conv_id)}, {"$set": {"last_message_at": now, "status": "answered"}})

    return {"status": "sent", "to": to_email}


@router.post("/messaging/sync-imap")
async def sync_imap_emails(user: dict = Depends(get_current_user)):
    """Sync incoming emails from IMAP into conversations."""
    if user["role"] not in STAFF_ROLES:
        raise HTTPException(status_code=403, detail="Nur Staff kann E-Mails synchronisieren")

    from services.email_service import fetch_new_emails, is_configured
    if not is_configured():
        return {"status": "not_configured", "synced": 0}

    db = get_db()
    emails = fetch_new_emails(max_count=20)
    synced = 0

    # Filter out bounced/returned/mailer-daemon emails
    BOUNCE_PATTERNS = ["returned mail", "undelivered", "mailer-daemon", "delivery status", "mail delivery failed"]

    for em in emails:
        # Skip bounce/returned mail notifications
        subject_lower = (em.get("subject") or "").lower()
        from_lower = (em.get("from_email") or "").lower()
        if any(p in subject_lower for p in BOUNCE_PATTERNS) or "mailer-daemon" in from_lower:
            continue

        # Check if already imported
        existing = await db.messages.find_one({"external_id": em.get("message_id")})
        if existing:
            continue

        # Try to find matching applicant by email
        from_email = em.get("from_email", "")
        applicant = await db.users.find_one({"email": from_email, "role": "applicant"}, {"_id": 1, "full_name": 1})

        # Find or create conversation
        conv = None
        if applicant:
            conv = await db.conversations.find_one({
                "participants": str(applicant["_id"]),
                "channel": "email",
            })
            if not conv:
                now = datetime.now(timezone.utc)
                staff_id = await _find_staff_user(db)
                participants = [str(applicant["_id"])]
                if staff_id:
                    participants.append(staff_id)
                # Find application
                app_doc = await db.applications.find_one({"applicant_id": str(applicant["_id"])})
                result = await db.conversations.insert_one({
                    "participants": participants,
                    "channel": "email",
                    "status": "open",
                    "subject": em.get("subject", ""),
                    "application_id": str(app_doc["_id"]) if app_doc else None,
                    "created_at": now,
                    "last_message_at": now,
                })
                conv = await db.conversations.find_one({"_id": result.inserted_id})

        if not conv:
            # Create orphan email conversation
            now = datetime.now(timezone.utc)
            staff_id = await _find_staff_user(db)
            from_name = em.get("from_name") or from_email.split("@")[0].replace(".", " ").title()
            result = await db.conversations.insert_one({
                "participants": [staff_id] if staff_id else [],
                "channel": "email",
                "status": "open",
                "subject": em.get("subject", f"E-Mail von {from_name}"),
                "external_email": from_email,
                "external_name": from_name,
                "created_at": now,
                "last_message_at": now,
            })
            conv = await db.conversations.find_one({"_id": result.inserted_id})

        conv_id = str(conv["_id"])
        now = datetime.now(timezone.utc)
        msg_doc = {
            "conversation_id": conv_id,
            "content": em.get("body", ""),
            "sender_id": str(applicant["_id"]) if applicant else "external",
            "sender_name": em.get("from_name") or from_email,
            "visibility": "public",
            "channel": "email",
            "sent_at": now,
            "read": False,
            "external_id": em.get("message_id"),
            "email_subject": em.get("subject"),
        }
        if em.get("body_html"):
            msg_doc["html_content"] = em["body_html"]
        await db.messages.insert_one(msg_doc)
        await db.conversations.update_one({"_id": conv["_id"]}, {"$set": {"last_message_at": now, "status": "open"}})
        synced += 1

    return {"status": "ok", "synced": synced}


@router.get("/messaging/email-status")
async def email_integration_status(user: dict = Depends(get_current_user)):
    """Check if SMTP/IMAP is configured and working."""
    from services.email_service import is_configured
    import os
    return {
        "smtp_configured": is_configured(),
        "smtp_host": os.environ.get("SMTP_HOST", ""),
        "imap_host": os.environ.get("IMAP_HOST", ""),
        "email_from": os.environ.get("EMAIL_FROM", ""),
        "status": "aktiv" if is_configured() else "nicht_konfiguriert",
    }
