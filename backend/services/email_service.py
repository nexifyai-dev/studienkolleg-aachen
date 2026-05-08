"""
E-Mail-Service: Echter SMTP-Versand und IMAP-Empfang.
Zentrale Signatur, professionelle Templates, Threading.
"""
import os
import ssl
import email
import smtplib
import imaplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, parseaddr
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
IMAP_HOST = os.environ.get("IMAP_HOST", "")
IMAP_PORT = int(os.environ.get("IMAP_PORT", "993"))
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USER)
EMAIL_FROM_NAME = os.environ.get("EMAIL_FROM_NAME", "Studienkolleg Aachen")

SIGNATURE_DE = """
--
Studienkolleg Aachen / Way2Germany
Templergraben 55, 52062 Aachen
Tel: +49 241 80911 | info@stk-aachen.de
www.studienkolleg-aachen.de
""".strip()

SIGNATURE_EN = """
--
Studienkolleg Aachen / Way2Germany
Templergraben 55, 52062 Aachen
Phone: +49 241 80911 | info@stk-aachen.de
www.studienkolleg-aachen.de
""".strip()


def get_signature(lang="de", sender_name="", sender_role=""):
    role_label = {
        "admin": "Administration",
        "superadmin": "Administration",
        "staff": "Studienberatung",
        "teacher": "Lehrkraft",
    }.get(sender_role, "Team")
    sig = SIGNATURE_EN if lang == "en" else SIGNATURE_DE
    greeting = "Best regards" if lang == "en" else "Mit freundlichen Gruessen"
    return f"\n\n{greeting},\n{sender_name}\n{role_label}\n\n{sig}"


def is_configured():
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_email(to_email: str, subject: str, body: str, lang: str = "de",
               sender_name: str = "", sender_role: str = "",
               reply_to: str = None, html_body: str = None) -> dict:
    """Send email via SMTP with central signature."""
    if not is_configured():
        logger.warning("SMTP not configured, email not sent")
        return {"success": False, "error": "SMTP nicht konfiguriert"}

    try:
        # Add signature
        full_body = body + get_signature(lang, sender_name, sender_role)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((EMAIL_FROM_NAME, EMAIL_FROM))
        msg["To"] = to_email
        msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        if reply_to:
            msg["Reply-To"] = reply_to

        # Plain text
        msg.attach(MIMEText(full_body, "plain", "utf-8"))

        # HTML version
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))
        else:
            html = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 14px; color: #1e293b; line-height: 1.6;">
{full_body.replace(chr(10), '<br>')}
</div>"""
            msg.attach(MIMEText(html, "html", "utf-8"))

        # Connect and send
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=15) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}: {subject}")
        return {"success": True, "to": to_email, "subject": subject}

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP auth error: {e}")
        return {"success": False, "error": f"SMTP-Authentifizierung fehlgeschlagen: {str(e)}"}
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return {"success": False, "error": f"SMTP-Fehler: {str(e)}"}
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return {"success": False, "error": str(e)}


def fetch_new_emails(max_count: int = 20) -> list:
    """Fetch new emails from IMAP inbox."""
    if not IMAP_HOST or not IMAP_USER or not IMAP_PASSWORD:
        return []

    emails = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASSWORD)
        mail.select("INBOX")

        status, data = mail.search(None, "UNSEEN")
        if status != "OK":
            mail.logout()
            return []

        msg_ids = data[0].split()[-max_count:] if data[0] else []
        for msg_id in msg_ids:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)

            from_name, from_email = parseaddr(msg.get("From", ""))
            subject = msg.get("Subject", "(Kein Betreff)")
            date_str = msg.get("Date", "")
            message_id = msg.get("Message-ID", "")

            # Decode subject
            if subject:
                decoded = email.header.decode_header(subject)
                subject = "".join(
                    part.decode(enc or "utf-8") if isinstance(part, bytes) else part
                    for part, enc in decoded
                )

            # Get body (plain + HTML)
            body_text = ""
            body_html = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    charset = part.get_content_charset() or "utf-8"
                    decoded = payload.decode(charset, errors="replace")
                    if ctype == "text/plain" and not body_text:
                        body_text = decoded
                    elif ctype == "text/html" and not body_html:
                        body_html = decoded
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or "utf-8"
                    decoded = payload.decode(charset, errors="replace")
                    if msg.get_content_type() == "text/html":
                        body_html = decoded
                    else:
                        body_text = decoded

            emails.append({
                "from_name": from_name,
                "from_email": from_email,
                "subject": subject,
                "body": body_text[:3000],
                "body_html": body_html[:8000] if body_html else "",
                "date": date_str,
                "message_id": message_id,
                "imap_id": msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id),
            })

        mail.logout()
    except Exception as e:
        logger.error(f"IMAP fetch error: {e}")

    return emails
