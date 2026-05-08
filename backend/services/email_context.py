"""
E-Mail-Kontext-Service – Liest IMAP-E-Mails pro Kunde fuer KI-Kontext.

Zweck:
- Read-Only-Zugriff auf die E-Mails, die an/von einem bestimmten Bewerber gesendet wurden
- Stellt Kontext fuer den Support-Chat bereit ("Brain pro Kunde")
- Cached Ergebnisse kurzzeitig, um IMAP-Last zu minimieren
"""
import os
import logging
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# In-Memory Cache (TTL-basiert)
_cache = {}
_CACHE_TTL = timedelta(minutes=10)


def _decode_header_value(val):
    """Dekodiert MIME-kodierte Header."""
    if not val:
        return ""
    decoded_parts = decode_header(val)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or 'utf-8', errors='replace'))
            except (LookupError, UnicodeDecodeError):
                result.append(part.decode('utf-8', errors='replace'))
        else:
            result.append(str(part))
    return " ".join(result)


def _extract_body(msg) -> str:
    """Extrahiert den Klartext-Body aus einer E-Mail."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    try:
                        body = payload.decode(charset, errors='replace')
                    except (LookupError, UnicodeDecodeError):
                        body = payload.decode('utf-8', errors='replace')
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            try:
                body = payload.decode(charset, errors='replace')
            except (LookupError, UnicodeDecodeError):
                body = payload.decode('utf-8', errors='replace')
    # Begrenzen auf 500 Zeichen pro Mail
    return body[:500].strip()


def _is_configured() -> bool:
    """Prueft ob IMAP-Konfiguration vorhanden ist."""
    return bool(os.environ.get("IMAP_HOST") and os.environ.get("IMAP_USER") and os.environ.get("IMAP_PASSWORD"))


async def fetch_email_context(email_address: str, max_emails: int = 5) -> Optional[str]:
    """
    Liest die letzten E-Mails von/an eine bestimmte Adresse.
    Gibt einen formatierten Kontext-String zurueck.

    Args:
        email_address: Die E-Mail-Adresse des Bewerbers
        max_emails: Maximale Anzahl E-Mails

    Returns:
        Formatierter Kontext-String oder None
    """
    if not _is_configured() or not email_address:
        return None

    # Cache pruefen
    cache_key = f"email_ctx_{email_address.lower()}"
    cached = _cache.get(cache_key)
    if cached and (datetime.now(timezone.utc) - cached["ts"]) < _CACHE_TTL:
        return cached["data"]

    imap_host = os.environ.get("IMAP_HOST")
    imap_port = int(os.environ.get("IMAP_PORT", "993"))
    imap_user = os.environ.get("IMAP_USER")
    imap_pass = os.environ.get("IMAP_PASSWORD")

    context_parts = []
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _fetch_emails_sync,
                                             imap_host, imap_port, imap_user, imap_pass,
                                             email_address, max_emails)
        context_parts = result
    except Exception as e:
        logger.warning(f"[EMAIL_CONTEXT] IMAP-Fehler: {e}")
        return None

    if not context_parts:
        _cache[cache_key] = {"data": None, "ts": datetime.now(timezone.utc)}
        return None

    context = f"E-Mail-Verlauf mit {email_address} (letzte {len(context_parts)} E-Mails):\n\n"
    context += "\n---\n".join(context_parts)

    _cache[cache_key] = {"data": context, "ts": datetime.now(timezone.utc)}
    return context


def _fetch_emails_sync(host, port, user, password, target_email, max_emails):
    """Synchroner IMAP-Abruf (wird in Thread-Executor ausgefuehrt)."""
    results = []
    conn = None
    try:
        conn = imaplib.IMAP4_SSL(host, port)
        conn.login(user, password)

        # Inbox + Sent durchsuchen
        for folder in ['INBOX', 'Sent', 'INBOX.Sent', '"Sent Items"']:
            try:
                status, _ = conn.select(folder, readonly=True)
                if status != 'OK':
                    continue
            except Exception:
                continue

            # Suche nach E-Mails an/von der Ziel-Adresse
            search_criteria = f'(OR FROM "{target_email}" TO "{target_email}")'
            try:
                status, data = conn.search(None, search_criteria)
                if status != 'OK':
                    continue
            except Exception:
                continue

            msg_ids = data[0].split()
            # Nur die letzten N
            for msg_id in msg_ids[-max_emails:]:
                try:
                    status, msg_data = conn.fetch(msg_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    raw = msg_data[0][1]
                    msg = email.message_from_bytes(raw)

                    subject = _decode_header_value(msg.get("Subject", ""))
                    from_addr = _decode_header_value(msg.get("From", ""))
                    date_str = msg.get("Date", "")
                    body = _extract_body(msg)

                    if body:
                        results.append(f"Datum: {date_str}\nVon: {from_addr}\nBetreff: {subject}\nInhalt: {body}")
                except Exception:
                    continue

            if len(results) >= max_emails:
                break

        conn.logout()
    except Exception as e:
        logger.warning(f"[EMAIL_CONTEXT] IMAP-Verbindung fehlgeschlagen: {e}")
        if conn:
            try:
                conn.logout()
            except Exception:
                pass

    return results[-max_emails:]
