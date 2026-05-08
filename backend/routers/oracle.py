"""
Oracle Router – API-Endpunkte fuer die zentrale Wissensquelle.

Endpunkte:
- POST /api/oracle/chat – Nachricht senden, KI-Antwort erhalten
- GET  /api/oracle/context – Aktueller System-Snapshot (ohne Chat)
- GET  /api/oracle/conversations – Alle Konversationen des Users
- GET  /api/oracle/conversations/{id} – Einzelne Konversation mit Nachrichten
- DELETE /api/oracle/conversations/{id} – Konversation loeschen
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES
from models.schemas import to_str_id
from services.oracle_service import process_query, aggregate_system_context
from rate_limiter import limiter

router = APIRouter(prefix="/api/oracle", tags=["oracle"])


class OracleChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str | None = None


@router.post("/chat")
@limiter.limit("15/minute")
async def oracle_chat(
    data: OracleChatRequest,
    request: Request,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Sende eine Frage an das Oracle und erhalte eine KI-Antwort mit Live-Daten-Kontext."""
    result = await process_query(
        user_message=data.message,
        conversation_id=data.conversation_id,
        user=user,
    )
    return result


@router.get("/context")
async def oracle_context(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Aktueller System-Snapshot (Live-Daten ohne Chat)."""
    ctx = await aggregate_system_context()
    return ctx


@router.get("/conversations")
async def list_conversations(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Alle Oracle-Konversationen (neueste zuerst)."""
    db = get_db()
    convs = await db.oracle_conversations.find(
        {}, {"messages": 0}
    ).sort("updated_at", -1).to_list(50)
    return [to_str_id(c) for c in convs]


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Einzelne Konversation mit allen Nachrichten."""
    db = get_db()
    try:
        conv = await db.oracle_conversations.find_one({"_id": ObjectId(conv_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not conv:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
    result = to_str_id(conv)
    # Timestamps in messages serialisieren
    if result.get("messages"):
        for msg in result["messages"]:
            if hasattr(msg.get("timestamp"), "isoformat"):
                msg["timestamp"] = msg["timestamp"].isoformat()
    return result


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Konversation loeschen."""
    db = get_db()
    try:
        result = await db.oracle_conversations.delete_one({"_id": ObjectId(conv_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Konversation nicht gefunden")
    return {"status": "deleted"}



@router.get("/knowledge-base")
async def get_knowledge_base(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Gibt die externe Wissensbasis als strukturierte Daten zurueck."""
    from services.external_knowledge import EXTERNAL_KNOWLEDGE_BASE, get_all_reference_urls
    return {
        "knowledge_base": EXTERNAL_KNOWLEDGE_BASE,
        "reference_urls": get_all_reference_urls(),
    }
