"""OAuth-Flow für Google Calendar Anbindung (Admin-Only)."""
import logging
import secrets
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from config import APP_URL
from deps import get_current_user, require_roles, ADMIN_ROLES
from services import google_calendar as gcal
import requests

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/oauth/google", tags=["oauth-google"])

# In-Memory State-Store (nur für den OAuth-Handshake, kurzlebig)
_STATES: dict[str, str] = {}


@router.get("/status")
async def status(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    return await gcal.get_status()


@router.get("/authorize")
async def authorize(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    if not gcal.is_configured():
        raise HTTPException(status_code=400, detail="Google Calendar ist nicht konfiguriert (GOOGLE_CLIENT_ID/SECRET fehlen).")
    state = secrets.token_urlsafe(24)
    _STATES[state] = user["id"]
    url = gcal.build_auth_url(state)
    return {"authorization_url": url}


@router.get("/callback")
async def callback(code: str = Query(...), state: str = Query(...)):
    """OAuth-Redirect-Ziel. State prüfen, Token tauschen, weiterleiten."""
    if state not in _STATES:
        raise HTTPException(status_code=400, detail="Invalid OAuth state.")
    _STATES.pop(state, None)
    if not gcal.is_configured():
        raise HTTPException(status_code=400, detail="Google Calendar nicht konfiguriert.")
    try:
        tokens = gcal.exchange_code(code)
    except Exception as e:
        logger.error(f"[GCAL] callback failed: {e}")
        return RedirectResponse(f"{APP_URL}/admin/integrations?google=error")
    # E-Mail des Verbundenen holen
    try:
        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
            timeout=10,
        ).json()
        email = userinfo.get("email", "")
    except Exception:
        email = ""
    await gcal.save_tokens(tokens, email)
    return RedirectResponse(f"{APP_URL}/admin/integrations?google=connected")


@router.post("/disconnect")
async def disconnect(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    await gcal.disconnect()
    return {"status": "disconnected"}


@router.get("/upcoming")
async def upcoming(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Diagnose-Endpoint: kommende Events des verbundenen Kalenders."""
    return {"events": await gcal.list_upcoming(20)}
