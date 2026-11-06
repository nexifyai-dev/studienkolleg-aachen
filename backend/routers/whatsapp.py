"""WhatsApp Router (Twilio). Admin-Only."""
from fastapi import APIRouter, Depends, HTTPException, Request
from deps import require_roles, ADMIN_ROLES
from services import whatsapp_service as wa

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.get("/status")
async def status(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    return await wa.get_status()


@router.post("/send")
async def send(request: Request, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    try:
        body = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Ungültiger JSON-Body")
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="JSON-Objekt erwartet")
    to = body.get("to") or ""
    msg = body.get("body") or ""
    if not isinstance(to, str) or not isinstance(msg, str):
        raise HTTPException(status_code=400, detail="Felder 'to' und 'body' müssen Text sein")
    to = to.strip()
    msg = msg.strip()
    if not to or not msg:
        raise HTTPException(status_code=400, detail="Felder 'to' und 'body' sind erforderlich")
    applicant_id = body.get("applicant_id")
    return await wa.send_message(to, msg, applicant_id=applicant_id, metadata={"sent_by": user["id"]})


@router.get("/messages")
async def messages(user: dict = Depends(require_roles(*ADMIN_ROLES)), limit: int = 50):
    return {"messages": await wa.recent_messages(limit=min(max(limit, 1), 200))}
