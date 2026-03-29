"""
Email service – Resend integration with feature flag.

[OFFEN] RESEND_API_KEY must be set in .env before emails are delivered.
When not set, all send_* calls log to console only (no-op / dev fallback).
This is intentional and safe: the system functions without email,
but delivery must be verified before go-live.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy import to avoid hard dependency when Resend is not configured
_resend = None


def _get_resend():
    global _resend
    if _resend is None:
        try:
            import resend as _r
            _resend = _r
        except ImportError:
            logger.warning("[EMAIL] resend package not installed")
    return _resend


def _is_enabled() -> bool:
    from config import EMAIL_ENABLED
    return EMAIL_ENABLED


def _send(to: str, subject: str, html: str) -> bool:
    """Internal dispatcher. Returns True on success."""
    if not _is_enabled():
        logger.info(f"[EMAIL:DEV] Would send to={to} subject='{subject}' (RESEND disabled)")
        return False
    try:
        from config import RESEND_API_KEY, EMAIL_FROM, REPLY_TO
        r = _get_resend()
        if r is None:
            return False
        r.api_key = RESEND_API_KEY
        r.Emails.send({
            "from": f"Studienkolleg Aachen <{EMAIL_FROM}>",
            "to": [to],
            "reply_to": REPLY_TO,
            "subject": subject,
            "html": html,
        })
        logger.info(f"[EMAIL] Sent to={to} subject='{subject}' via {EMAIL_FROM}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Send failed to={to}: {e}")
        return False


# ─── Templates ────────────────────────────────────────────────────────────────

def send_welcome(to: str, full_name: str) -> bool:
    """Sent after successful registration / account claim."""
    name = full_name or "Bewerber/in"
    subject = "Willkommen bei Studienkolleg Aachen"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Willkommen, {name}!</h3>
      <p style="color:#475569">Dein Konto wurde erfolgreich erstellt. Du kannst dich jetzt in dein Portal einloggen
      und deinen Bewerbungsprozess verfolgen.</p>
      <a href="{{APP_URL}}/portal"
         style="display:inline-block;background:#113655;color:white;padding:12px 24px;border-radius:4px;text-decoration:none;font-weight:600;margin-top:16px">
        Zum Portal →
      </a>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Bei Fragen: <a href="mailto:info@stk-aachen.de">info@stk-aachen.de</a>
      </p>
    </div>
    """
    return _send(to, subject, html)


def send_application_received(to: str, full_name: str, application_id: str) -> bool:
    """Sent after lead ingest or application creation."""
    name = full_name or "Bewerber/in"
    subject = "Deine Bewerbung ist eingegangen – Studienkolleg Aachen"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Hallo {name},</h3>
      <p style="color:#475569">deine Bewerbung ist bei uns eingegangen (Ref: #{application_id[-6:].upper()}).
      Wir melden uns innerhalb von 24 Stunden bei dir.</p>
      <p style="color:#475569">In der Zwischenzeit kannst du dein Portal aufrufen und weitere Informationen hochladen.</p>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Bei Fragen: <a href="mailto:info@stk-aachen.de">info@stk-aachen.de</a>
      </p>
    </div>
    """
    return _send(to, subject, html)


def send_document_requested(to: str, full_name: str, document_types: list) -> bool:
    """Sent when staff requests documents from applicant."""
    name = full_name or "Bewerber/in"
    docs_list = "".join(f"<li style='margin:4px 0;color:#475569'>{d}</li>" for d in document_types)
    subject = "Dokumente angefordert – Studienkolleg Aachen"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Hallo {name},</h3>
      <p style="color:#475569">wir benötigen folgende Dokumente von dir:</p>
      <ul style="padding-left:20px">{docs_list}</ul>
      <p style="color:#475569">Bitte lade diese in deinem Portal hoch.</p>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Bei Fragen: <a href="mailto:info@stk-aachen.de">info@stk-aachen.de</a>
      </p>
    </div>
    """
    return _send(to, subject, html)


def send_password_reset(to: str, reset_url: str) -> bool:
    """Password reset link."""
    subject = "Passwort zurücksetzen – Studienkolleg Aachen"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Passwort zurücksetzen</h3>
      <p style="color:#475569">Klicke auf den Button, um dein Passwort zurückzusetzen.
      Dieser Link ist 1 Stunde gültig.</p>
      <a href="{reset_url}"
         style="display:inline-block;background:#113655;color:white;padding:12px 24px;border-radius:4px;text-decoration:none;font-weight:600;margin-top:16px">
        Passwort zurücksetzen →
      </a>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Falls du keinen Reset angefordert hast, ignoriere diese E-Mail.
      </p>
    </div>
    """
    return _send(to, subject, html)


def send_invite(to: str, full_name: str, invite_url: str, role: str) -> bool:
    """Invite link for new team members / partners."""
    name = full_name or "Nutzer/in"
    subject = "Einladung zur Plattform – Studienkolleg Aachen"
    html = f"""
    <div style="font-family:Inter,sans-serif;max-width:600px;margin:auto;padding:24px">
      <div style="background:#113655;padding:20px;border-radius:4px;margin-bottom:24px">
        <h2 style="color:white;margin:0;font-size:20px">Studienkolleg Aachen</h2>
      </div>
      <h3 style="color:#113655">Hallo {name},</h3>
      <p style="color:#475569">Du wurdest als <strong>{role}</strong> zur Plattform von Studienkolleg Aachen eingeladen.
      Dieser Einladungslink ist 7 Tage gültig.</p>
      <a href="{invite_url}"
         style="display:inline-block;background:#113655;color:white;padding:12px 24px;border-radius:4px;text-decoration:none;font-weight:600;margin-top:16px">
        Konto erstellen →
      </a>
      <p style="color:#94a3b8;font-size:12px;margin-top:32px">
        Falls du keine Einladung erwartest, ignoriere diese E-Mail.
      </p>
    </div>
    """
    return _send(to, subject, html)
