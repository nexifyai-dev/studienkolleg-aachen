"""
Messaging router.

Security notes:
- Applicants can only read conversations they are a participant in
- Staff can read all conversations
- Message send validation: content non-empty, max 5000 chars
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES
from models.schemas import MessageCreate, to_str_id

router = APIRouter(prefix="/api", tags=["messaging"])

MAX_MSG_LENGTH = 5000


@router.get("/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    db = get_db()
    if user["role"] == "applicant":
        convs = await db.conversations.find({"participants": user["id"]}).to_list(50)
    else:
        convs = await db.conversations.find({}).sort("last_message_at", -1).to_list(200)
    return [to_str_id(c) for c in convs]


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
        # Verify user is a participant
        try:
            conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
        except Exception:
            raise HTTPException(status_code=400, detail="Ungültige Konversations-ID")
        if not conv:
            raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
        if user["role"] == "applicant" and user["id"] not in conv.get("participants", []):
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        # Create new conversation
        participants = [user["id"]]
        if data.recipient_id:
            # Validate recipient exists
            try:
                recipient = await db.users.find_one({"_id": ObjectId(data.recipient_id)}, {"_id": 1})
            except Exception:
                raise HTTPException(status_code=400, detail="Ungültige Empfänger-ID")
            if not recipient:
                raise HTTPException(status_code=404, detail="Empfänger nicht gefunden")
            participants.append(data.recipient_id)
        result = await db.conversations.insert_one({
            "participants": participants,
            "application_id": data.application_id,
            "created_at": datetime.now(timezone.utc),
            "last_message_at": datetime.now(timezone.utc),
        })
        conv_id = str(result.inserted_id)

    msg = {
        "conversation_id": conv_id,
        "content": content,
        "sender_id": user["id"],
        "visibility": data.visibility,
        "sent_at": datetime.now(timezone.utc),
        "read": False,
    }
    result = await db.messages.insert_one(msg)
    await db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"last_message_at": datetime.now(timezone.utc)}},
    )
    msg["id"] = str(result.inserted_id)
    msg["conversation_id"] = conv_id
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
    return [to_str_id(m) for m in msgs]
