"""
Messaging router.

Security notes:
- Applicants can only read conversations they are a participant in
- Staff can read all conversations
- Message send validation: content non-empty, max 5000 chars
- Auto-creates support conversation for applicants without explicit recipient
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
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
    """Add participant_names and last_message_preview to conversations."""
    user_ids = set()
    for c in convs:
        for pid in c.get("participants", []):
            user_ids.add(pid)

    user_map = {}
    for uid in user_ids:
        try:
            u = await db.users.find_one({"_id": ObjectId(uid)}, {"_id": 0, "full_name": 1, "email": 1, "role": 1})
            if u:
                user_map[uid] = {"name": u.get("full_name") or u.get("email", ""), "role": u.get("role", "")}
        except Exception:
            pass

    enriched = []
    for c in convs:
        sc = _serialize_conv(c)
        sc["participant_names"] = {pid: user_map.get(pid, {}).get("name", "Unbekannt") for pid in sc.get("participants", [])}
        sc["participant_roles"] = {pid: user_map.get(pid, {}).get("role", "") for pid in sc.get("participants", [])}
        last_msg = await db.messages.find_one({"conversation_id": sc["id"]}, sort=[("sent_at", -1)])
        if last_msg:
            sc["last_message_preview"] = (last_msg.get("content", "")[:80] + "...") if len(last_msg.get("content", "")) > 80 else last_msg.get("content", "")
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
