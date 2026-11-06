"""
Google Calendar Service – OAuth2-basierte Synchronisation von Terminen
mit einem zentralen Kalender.

Tokens werden im Setting-Dokument (settings.type='google_calendar') gespeichert.
Die Integration ist optional: Fehlen die Umgebungsvariablen GOOGLE_CLIENT_ID /
GOOGLE_CLIENT_SECRET, so bleibt das Feature komplett deaktiviert.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]


def is_configured() -> bool:
    """True wenn Client-ID + Secret gesetzt sind (Env)."""
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)


def build_redirect_uri() -> str:
    from config import APP_URL
    base = APP_URL.rstrip("/")
    return f"{base}/api/oauth/google/callback"


def build_auth_url(state: str) -> str:
    """Baut die Google-OAuth-Authorization-URL."""
    from urllib.parse import urlencode
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": build_redirect_uri(),
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def exchange_code(code: str) -> dict:
    """Tauscht Code gegen Access + Refresh Token."""
    import requests
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": build_redirect_uri(),
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"Google token exchange failed: {resp.status_code} {resp.text[:200]}")
    return resp.json()


async def load_tokens() -> Optional[dict]:
    """Lädt gespeicherte Tokens aus settings."""
    from database import get_db
    db = get_db()
    doc = await db.settings.find_one({"type": "google_calendar"})
    if not doc:
        return None
    return doc.get("tokens")


async def save_tokens(tokens: dict, connected_email: str) -> None:
    """Persistiert Tokens + Connected-Email."""
    from database import get_db
    db = get_db()
    await db.settings.update_one(
        {"type": "google_calendar"},
        {
            "$set": {
                "type": "google_calendar",
                "tokens": tokens,
                "connected_email": connected_email,
                "connected_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        upsert=True,
    )


async def disconnect() -> None:
    from database import get_db
    db = get_db()
    await db.settings.delete_one({"type": "google_calendar"})


async def get_status() -> dict:
    """Verbindungsstatus für Admin UI."""
    doc = None
    try:
        from database import get_db
        db = get_db()
        doc = await db.settings.find_one({"type": "google_calendar"})
    except Exception:
        pass
    return {
        "configured": is_configured(),
        "connected": bool(doc and doc.get("tokens")),
        "connected_email": (doc or {}).get("connected_email"),
        "connected_at": (doc or {}).get("connected_at"),
        "calendar_id": GOOGLE_CALENDAR_ID,
    }


async def _get_creds():
    """Lädt Tokens und liefert google.oauth2.credentials.Credentials.
    Refresht Access-Token automatisch."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request as GoogleRequest
    tokens = await load_tokens()
    if not tokens:
        return None
    creds = Credentials(
        token=tokens.get("access_token"),
        refresh_token=tokens.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=GOOGLE_SCOPES,
    )
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleRequest())
            tokens["access_token"] = creds.token
            from database import get_db
            db = get_db()
            await db.settings.update_one(
                {"type": "google_calendar"},
                {"$set": {"tokens.access_token": creds.token}},
            )
        except Exception as e:
            logger.error(f"[GCAL] Token-Refresh fehlgeschlagen: {e}")
            return None
    return creds


def _event_body(appointment: dict) -> dict:
    """Baut den Body für die Google-Events-API aus einem Appointment-Dokument."""
    date = appointment.get("date")  # 'YYYY-MM-DD'
    time = appointment.get("time", "10:00")
    duration = int(appointment.get("duration_min", 30))
    # Assume Europe/Berlin timezone for the calendar
    tz = "Europe/Berlin"
    start_iso = f"{date}T{time}:00"
    # Naive – Google needs either dateTime + timeZone
    from datetime import datetime as _dt, timedelta as _td
    dt_start = _dt.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    dt_end = dt_start + _td(minutes=duration)
    summary = appointment.get("title") or "Termin"
    body = {
        "summary": summary,
        "description": appointment.get("description") or f"Erstellt aus STK Portal ({appointment.get('type', 'consultation')})",
        "location": appointment.get("location", "Online (Zoom)"),
        "start": {"dateTime": dt_start.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": tz},
        "end": {"dateTime": dt_end.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": tz},
    }
    email = appointment.get("user_email")
    name = appointment.get("user_name")
    if email:
        body["attendees"] = [{"email": email, "displayName": name or email}]
    return body


async def sync_event(appointment: dict) -> Optional[str]:
    """Erstellt oder aktualisiert einen Termin in Google Calendar.
    Returns Event-ID oder None (wenn Feature inaktiv)."""
    if not is_configured():
        return None
    try:
        creds = await _get_creds()
        if not creds:
            return None
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        cal_id = GOOGLE_CALENDAR_ID
        body = _event_body(appointment)
        existing_event_id = appointment.get("google_event_id")
        if existing_event_id:
            result = service.events().update(calendarId=cal_id, eventId=existing_event_id, body=body).execute()
        else:
            result = service.events().insert(calendarId=cal_id, body=body).execute()
        return result.get("id")
    except Exception as e:
        logger.error(f"[GCAL] sync_event fehlgeschlagen: {e}")
        return None


async def delete_event(event_id: str) -> bool:
    if not is_configured() or not event_id:
        return False
    try:
        creds = await _get_creds()
        if not creds:
            return False
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        service.events().delete(calendarId=GOOGLE_CALENDAR_ID, eventId=event_id).execute()
        return True
    except Exception as e:
        logger.error(f"[GCAL] delete_event fehlgeschlagen: {e}")
        return False


async def list_upcoming(max_results: int = 20) -> list:
    """Liefert kommende Events aus dem verbundenen Kalender (für Diagnose-UI)."""
    if not is_configured():
        return []
    try:
        creds = await _get_creds()
        if not creds:
            return []
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        events = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        return events.get("items", [])
    except Exception as e:
        logger.error(f"[GCAL] list_upcoming fehlgeschlagen: {e}")
        return []
