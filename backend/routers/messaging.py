"""
Messaging router.

Security notes:
- Applicants can only read conversations they are a participant in
- Staff can read all conversations
- Message send validation: content non-empty, max 5000 chars
- Auto-creates support conversation for applicants without explicit recipient
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
from models.schemas import MessageCreate, to_str_id

router = APIRouter(prefix="/api", tags=["messaging"])

MAX_MSG_LENGTH = 5000


def _serialize_conv(conv: dict) -> dict:
    """Serialize conversation doc, converting ObjectId and datetime."""
    conv = to_str_id(conv)
    for k in ("created_at", "last_message_at"):
        if hasattr(conv.get(k), "isoformat"):
            conv[k] = conv[k].isoformat()
    return conv


def _serialize_msg(msg: dict) -> dict:
    """Serialize message doc."""
    msg = to_str_id(msg)
    if hasattr(msg.get("sent_at"), "isoformat"):
        msg["sent_at"] = msg["sent_at"].isoformat()
    return msg


async def _find_staff_user(db) -> str | None:
    """Find an active admin or staff user to auto-assign as conversation partner."""
    for role in ["superadmin", "admin", "staff"]:
        u = await db.users.find_one({"role": role, "active": True}, {"_id": 1})
        if u:
            return str(u["_id"])
    return None


async def _enrich_conversations(db, convs: list) -> list:
    """Add participant_names and last_message_preview to conversations (batch)."""
    if not convs:
        return []

    # Batch-fetch all participants
    user_ids = set()
    for c in convs:
        for pid in c.get("participants", []):
            user_ids.add(pid)

    user_map = {}
    if user_ids:
        try:
            users = await db.users.find(
                {"_id": {"$in": [ObjectId(uid) for uid in user_ids]}},
                {"full_name": 1, "email": 1, "role": 1},
            ).to_list(None)
            for u in users:
                uid = str(u["_id"])
                user_map[uid] = {"name": u.get("full_name") or u.get("email", ""), "role": u.get("role", "")}
        except Exception:
            pass

    # Batch-fetch last messages using aggregation
    serialized_convs = [_serialize_conv(c) for c in convs]
    conv_ids = [sc["id"] for sc in serialized_convs]
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

    enriched = []
    for sc in serialized_convs:
        sc["participant_names"] = {pid: user_map.get(pid, {}).get("name", "Unbekannt") for pid in sc.get("participants", [])}
        sc["participant_roles"] = {pid: user_map.get(pid, {}).get("role", "") for pid in sc.get("participants", [])}
        last_msg = msg_map.get(sc["id"])
        if last_msg:
            content = last_msg.get("content", "")
            sc["last_message_preview"] = (content[:80] + "...") if len(content) > 80 else content
            sc["last_message_sender"] = last_msg.get("sender_id", "")
        enriched.append(sc)
    return enriched


@router.get("/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    db = get_db()
    if user["role"] == "applicant":
        convs = await db.conversations.find({"participants": user["id"]}).sort("last_message_at", -1).to_list(50)
    else:
        convs = await db.conversations.find({}).sort("last_message_at", -1).to_list(200)
    return await _enrich_conversations(db, convs)


@router.get("/conversations/support")
async def get_or_create_support_conversation(user: dict = Depends(get_current_user)):
    """Get or create a support conversation for the current applicant."""
    db = get_db()
    existing = await db.conversations.find_one({
        "participants": user["id"],
        "is_support": True,
    })
    if existing:
        result = await _enrich_conversations(db, [existing])
        return result[0]

    staff_id = await _find_staff_user(db)
    participants = [user["id"]]
    if staff_id:
        participants.append(staff_id)

    now = datetime.now(timezone.utc)
    conv_doc = {
        "participants": participants,
        "is_support": True,
        "created_at": now,
        "last_message_at": now,
    }
    result = await db.conversations.insert_one(conv_doc)
    conv_doc["_id"] = result.inserted_id
    enriched = await _enrich_conversations(db, [conv_doc])
    return enriched[0]


@router.post("/messages")
async def send_message(data: MessageCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    content = data.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Nachricht darf nicht leer sein")
    if len(content) > MAX_MSG_LENGTH:
        raise HTTPException(status_code=400, detail=f"Nachricht zu lang (max {MAX_MSG_LENGTH} Zeichen)")

    conv_id = data.conversation_id
    if conv_id:
        try:
            conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Ungültige Konversations-ID")
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
                raise HTTPException(status_code=400, detail="Ungültige Empfänger-ID")
            if not recipient:
                raise HTTPException(status_code=404, detail="Empfänger nicht gefunden")
            participants.append(data.recipient_id)
        else:
            staff_id = await _find_staff_user(db)
            if staff_id and staff_id != user["id"]:
                participants.append(staff_id)

        now = datetime.now(timezone.utc)
        result = await db.conversations.insert_one({
            "participants": participants,
            "application_id": data.application_id,
            "is_support": True,
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
        "visibility": data.visibility,
        "sent_at": now,
        "read": False,
    }
    result = await db.messages.insert_one(msg)
    await db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"last_message_at": now}},
    )
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
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not conv:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
    if user["role"] == "applicant" and user["id"] not in conv.get("participants", []):
        raise HTTPException(status_code=403, detail="Forbidden")
    msgs = await db.messages.find({"conversation_id": conv_id}).sort("sent_at", 1).to_list(500)
    return [_serialize_msg(m) for m in msgs]


@router.put("/messages/{msg_id}/read")
async def mark_message_read(msg_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        await db.messages.update_one({"_id": ObjectId(msg_id)}, {"$set": {"read": True}})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    return {"status": "ok"}


@router.post("/conversations/{conv_id}/attachments")
async def upload_message_attachment(conv_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Upload a file attachment to a conversation message."""
    import base64
    from services.storage import storage, sanitize_filename, validate_upload

    db = get_db()
    try:
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Konversations-ID")
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
        raise HTTPException(status_code=400, detail="Ungültige Datei-Kodierung")

    try:
        validate_upload(filename, len(file_bytes), content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    import uuid
    storage_key = f"messages/{conv_id}/{uuid.uuid4().hex[:8]}_{filename}"
    await storage().upload(storage_key, file_bytes, content_type)

    now = datetime.now(timezone.utc)
    msg = {
        "conversation_id": conv_id,
        "content": message_text or f"[Datei: {filename}]",
        "sender_id": user["id"],
        "sender_name": user.get("full_name") or user.get("email", ""),
        "visibility": "public",
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
    # Never expose storage_key to frontend
    if "attachment" in msg:
        msg["attachment"].pop("storage_key", None)
        msg["attachment"]["id"] = msg["id"]
    return msg


@router.get("/messages/{msg_id}/attachment")
async def download_message_attachment(msg_id: str, user: dict = Depends(get_current_user)):
    """Download a message attachment."""
    from fastapi.responses import Response
    from services.storage import storage as get_storage

    db = get_db()
    try:
        msg = await db.messages.find_one({"_id": ObjectId(msg_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
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
