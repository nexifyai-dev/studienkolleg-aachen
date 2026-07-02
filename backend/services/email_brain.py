"""
E-Mail Brain Agent – IMAP-Ingestion + KI-Antwortgenerierung + Memory-Integration.

Architektur:
1. IMAP-Polling: Liest alle neuen E-Mails von Strato
2. Bewerber-Zuordnung: Matcht E-Mail-Absender mit Bewerbern in der DB
3. Memory-Ingestion: Speichert Fakten in brain_memory
4. Antwort-Vorschlag: Generiert KI-Entwurf mit vollem Kontext
5. Approval-Gate: Staff prueft und genehmigt/bearbeitet vor Versand
6. Versand: HTML-Layout mit rechtlich korrekter Signatur
"""
import os
import logging
import imaplib
import email as email_lib
from email.header import decode_header
from datetime import datetime, timezone, timedelta
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

# ── Rechtlich korrekte E-Mail-Signatur ─────────────────────────────────────────
EMAIL_SIGNATURE_DE = """
--
W2G Academy GmbH – Studienkolleg Aachen
Lothringer Str. 23, 52062 Aachen
Tel: +49 241 47599390
E-Mail: info@stk-aachen.de
Web: www.studienkolleg-aachen.de

Geschaeftsfuehrer: [Name]
Handelsregister: Amtsgericht Aachen, HRB [Nummer]
USt-IdNr.: DE[Nummer]

Diese E-Mail und ihre Anhaenge koennen vertrauliche Informationen enthalten.
Wenn Sie nicht der beabsichtigte Empfaenger sind, loeschen Sie diese E-Mail bitte
und informieren Sie uns unter info@stk-aachen.de.
""".strip()

EMAIL_SIGNATURE_EN = """
--
W2G Academy GmbH – Studienkolleg Aachen
Lothringer Str. 23, 52062 Aachen, Germany
Phone: +49 241 47599390
Email: info@stk-aachen.de
Web: www.studienkolleg-aachen.de

Managing Director: [Name]
Commercial Register: District Court Aachen, HRB [Number]
VAT ID: DE[Number]

This email and its attachments may contain confidential information.
If you are not the intended recipient, please delete this email
and notify us at info@stk-aachen.de.
""".strip()


def _get_signature(lang: str = "de") -> str:
    return EMAIL_SIGNATURE_DE if lang == "de" else EMAIL_SIGNATURE_EN


def _decode_header_value(val) -> str:
    if not val:
        return ""
    parts = decode_header(val)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or 'utf-8', errors='replace'))
        else:
            result.append(str(part))
    return " ".join(result)


def _extract_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='replace')
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='replace')
    return body[:2000].strip()


def _extract_email_addr(header: str) -> str:
    """Extrahiert reine E-Mail-Adresse aus Header."""
    if '<' in header and '>' in header:
        return header.split('<')[1].split('>')[0].strip().lower()
    return header.strip().lower()


async def poll_inbox(max_emails: int = 50, since_days: int = 7) -> dict:
    """Polled IMAP-Inbox und importiert neue E-Mails ins Brain."""
    imap_host = os.environ.get("IMAP_HOST")
    imap_port = int(os.environ.get("IMAP_PORT", "993"))
    imap_user = os.environ.get("IMAP_USER")
    imap_pass = os.environ.get("IMAP_PASSWORD")

    if not all([imap_host, imap_user, imap_pass]):
        return {"error": "IMAP nicht konfiguriert", "imported": 0}

    db = get_db()
    from services.brain_memory import ingest_email_to_memory

    imported = 0
    skipped = 0
    errors = 0

    try:
        import asyncio
        loop = asyncio.get_event_loop()
        raw_emails = await loop.run_in_executor(
            None, _fetch_raw_emails, imap_host, imap_port, imap_user, imap_pass, max_emails, since_days
        )
    except Exception as e:
        logger.error(f"[EMAIL_BRAIN] IMAP-Poll fehlgeschlagen: {e}")
        return {"error": str(e), "imported": 0}

    for raw in raw_emails:
        try:
            msg_id = raw.get("message_id", "")
            from_addr = _extract_email_addr(raw.get("from", ""))

            # Bewerber-Zuordnung: E-Mail-Adresse in users suchen
            applicant = await db.users.find_one(
                {"email": {"$regex": f"^{from_addr}$", "$options": "i"}, "role": "applicant"},
                {"_id": 1}
            )
            applicant_id = str(applicant["_id"]) if applicant else None

            # In Memory speichern
            email_id = await ingest_email_to_memory(
                {**raw, "direction": "inbound"},
                applicant_id=applicant_id
            )

            if email_id:
                imported += 1
                # KI-Antwortvorschlag generieren wenn Bewerber zugeordnet
                if applicant_id:
                    await _generate_draft_reply(email_id, raw, applicant_id)
            else:
                skipped += 1

        except Exception as e:
            logger.warning(f"[EMAIL_BRAIN] E-Mail-Import Fehler: {e}")
            errors += 1

    logger.info(f"[EMAIL_BRAIN] Poll abgeschlossen: {imported} importiert, {skipped} uebersprungen, {errors} Fehler")
    return {"imported": imported, "skipped": skipped, "errors": errors}


def _fetch_raw_emails(host, port, user, password, max_emails, since_days) -> list:
    """Synchroner IMAP-Abruf."""
    results = []
    conn = None
    try:
        conn = imaplib.IMAP4_SSL(host, port)
        conn.login(user, password)
        conn.select('INBOX', readonly=True)

        since_date = (datetime.now() - timedelta(days=since_days)).strftime("%d-%b-%Y")
        status, data = conn.search(None, f'(SINCE "{since_date}")')
        if status != 'OK':
            return results

        msg_ids = data[0].split()
        for msg_id in msg_ids[-max_emails:]:
            try:
                status, msg_data = conn.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                raw = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw)

                results.append({
                    "message_id": msg.get("Message-ID", ""),
                    "from": _decode_header_value(msg.get("From", "")),
                    "to": _decode_header_value(msg.get("To", "")),
                    "subject": _decode_header_value(msg.get("Subject", "")),
                    "body": _extract_body(msg),
                    "date": msg.get("Date", ""),
                })
            except Exception:
                continue

        conn.logout()
    except Exception as e:
        logger.warning(f"[EMAIL_BRAIN] IMAP Fehler: {e}")
        if conn:
            try: conn.logout()
            except: pass

    return results


async def _generate_draft_reply(email_id: str, email_data: dict, applicant_id: str):
    """Generiert einen KI-Antwort-Entwurf fuer eine eingehende E-Mail."""
    from services.brain_memory import generate_response, recall_context

    db = get_db()

    # Bewerber-Daten laden
    from bson import ObjectId
    applicant = await db.users.find_one({"_id": ObjectId(applicant_id)}, {"_id": 0, "full_name": 1, "email": 1, "language_pref": 1, "country": 1})
    if not applicant:
        return

    lang = applicant.get("language_pref", "de")
    name = applicant.get("full_name", "")

    # Bewerbung laden
    app = await db.applications.find_one({"applicant_id": applicant_id}, {"_id": 0, "current_stage": 1, "course_type": 1, "applicant_number": 1})

    context = f"""Eingehende E-Mail:
Von: {email_data.get('from', '')}
Betreff: {email_data.get('subject', '')}
Inhalt: {email_data.get('body', '')[:800]}

Bewerber: {name} ({applicant.get('email', '')})
Land: {applicant.get('country', '?')}
Bewerbungsstatus: {app.get('current_stage', '?') if app else 'Keine Bewerbung'}
Kurs: {app.get('course_type', '?') if app else '?'}
Bewerbernummer: {app.get('applicant_number', '?') if app else '?'}"""

    query = f"""Schreibe eine professionelle, aber menschlich klingende Antwort auf diese E-Mail.
Die Antwort soll klingen, als haette sie ein echter Mitarbeiter geschrieben – nicht ein Bot.

WICHTIG:
- Natuerlicher Fliesstext, keine Aufzaehlungen wo ein Satz reicht
- Kurze Absaetze, maximal 3-4 Saetze pro Absatz
- Beruecksichtige den Bewerbungsstatus und alle bekannten Fakten
- Zeige Verstaendnis fuer die Situation des Bewerbers
- Keine Floskeln wie "Gerne informiere ich Sie" oder "Wie bereits erwaehnt"
- Sprache: {'Deutsch (siezen)' if lang == 'de' else 'English (formal)'}
- Beginne mit: {'Sehr geehrte/r ' + name if lang == 'de' else 'Dear ' + name}
- Ende mit: {'Mit freundlichen Gruessen' if lang == 'de' else 'Kind regards'}
  Studienkolleg Aachen Team
- KEIN Markdown, KEIN HTML. Nur sauberer Fliesstext mit Absaetzen."""

    result = await generate_response(applicant_id, context, query, lang=lang)

    if result.get("content"):
        # Signatur anhaengen
        full_content = result["content"] + "\n\n" + _get_signature(lang)

        # Entwurf speichern
        draft = {
            "email_id": email_id,
            "applicant_id": applicant_id,
            "subject": f"Re: {email_data.get('subject', '')}",
            "body": full_content,
            "to_addr": _extract_email_addr(email_data.get("from", "")),
            "lang": lang,
            "status": "draft",  # draft → approved → sent → failed
            "ai_model": result.get("model", "deepseek-chat"),
            "tokens_used": result.get("tokens", 0),
            "created_at": datetime.now(timezone.utc),
            "approved_by": None,
            "sent_at": None,
        }
        await db.brain_email_drafts.insert_one(draft)
        logger.info(f"[EMAIL_BRAIN] Entwurf erstellt fuer {draft['to_addr']}: {draft['subject']}")


async def approve_and_send(draft_id: str, approved_by: str, edited_body: str = None) -> dict:
    """Staff genehmigt einen E-Mail-Entwurf – Versand ueber SMTP."""
    from bson import ObjectId
    db = get_db()

    draft = await db.brain_email_drafts.find_one({"_id": ObjectId(draft_id)})
    if not draft:
        return {"error": "Entwurf nicht gefunden"}
    if draft["status"] not in ("draft", "rejected"):
        return {"error": f"Status {draft['status']} kann nicht gesendet werden"}

    body = edited_body if edited_body else draft["body"]

    # SMTP-Versand
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASSWORD")
        from_name = os.environ.get("EMAIL_FROM_NAME", "Studienkolleg Aachen")
        from_addr = os.environ.get("EMAIL_FROM", smtp_user)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = draft["subject"]
        msg["From"] = f"{from_name} <{from_addr}>"
        msg["To"] = draft["to_addr"]
        msg["Reply-To"] = from_addr

        # Plain-Text
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # HTML-Version mit Corporate Layout
        html_body = _build_html_email(body, draft.get("lang", "de"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_smtp, smtp_host, smtp_port, smtp_user, smtp_pass, from_addr, draft["to_addr"], msg)

        # Status aktualisieren
        await db.brain_email_drafts.update_one(
            {"_id": ObjectId(draft_id)},
            {"$set": {"status": "sent", "approved_by": approved_by, "sent_at": datetime.now(timezone.utc), "body": body}}
        )

        # Gesendete E-Mail ins Memory aufnehmen
        from services.brain_memory import ingest_email_to_memory
        await ingest_email_to_memory({
            "message_id": f"brain-{draft_id}",
            "from": from_addr,
            "to": draft["to_addr"],
            "subject": draft["subject"],
            "body": body,
            "date": datetime.now(timezone.utc).isoformat(),
            "direction": "outbound",
        }, applicant_id=draft.get("applicant_id"))

        return {"success": True, "status": "sent"}
    except Exception as e:
        logger.error(f"[EMAIL_BRAIN] Versand fehlgeschlagen: {e}")
        await db.brain_email_drafts.update_one(
            {"_id": ObjectId(draft_id)},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        return {"error": str(e)}


def _send_smtp(host, port, user, password, from_addr, to_addr, msg):
    """Synchroner SMTP-Versand."""
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, to_addr, msg.as_string())


def _build_html_email(body: str, lang: str = "de") -> str:
    """Erzeugt eine professionelle HTML-E-Mail im Corporate Design."""
    import html as html_mod
    safe_body = html_mod.escape(body).replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width"></head>
<body style="margin:0; padding:0; font-family: 'Helvetica Neue', Arial, sans-serif; color:#1a1a2e; background:#f4f6f9;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9; padding:24px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
      <!-- Header -->
      <tr><td style="background:#0A192F; padding:20px 32px;">
        <table width="100%"><tr>
          <td style="color:#ffffff; font-size:18px; font-weight:700; letter-spacing:0.5px;">Studienkolleg Aachen</td>
          <td align="right" style="color:rgba(255,255,255,0.7); font-size:11px;">W2G Academy GmbH</td>
        </tr></table>
      </td></tr>
      <!-- Body -->
      <tr><td style="padding:32px; font-size:14px; line-height:1.7; color:#333;">
        {safe_body}
      </td></tr>
      <!-- Footer -->
      <tr><td style="background:#f8f9fa; padding:20px 32px; border-top:1px solid #e9ecef;">
        <p style="margin:0 0 4px; font-size:11px; color:#6c757d; font-weight:600;">W2G Academy GmbH – Studienkolleg Aachen</p>
        <p style="margin:0 0 2px; font-size:10px; color:#adb5bd;">Lothringer Str. 23, 52062 Aachen | +49 241 47599390</p>
        <p style="margin:0; font-size:10px; color:#adb5bd;">info@stk-aachen.de | www.studienkolleg-aachen.de</p>
      </td></tr>
    </table>
    <p style="font-size:9px; color:#adb5bd; margin-top:12px; text-align:center;">
      {'Diese E-Mail kann vertrauliche Informationen enthalten.' if lang == 'de' else 'This email may contain confidential information.'}
    </p>
  </td></tr>
</table>
</body></html>"""


async def get_email_inbox(limit: int = 50, status_filter: str = None) -> list:
    """Listet E-Mails und zugehoerige Entwuerfe fuer Staff-UI."""
    db = get_db()

    query = {}
    if status_filter == "needs_reply":
        # E-Mails ohne Entwurf oder mit abgelehntem Entwurf
        query["direction"] = "inbound"

    emails = await db.brain_emails.find(query).sort("created_at", -1).to_list(limit)

    result = []
    for em in emails:
        em_id = str(em.pop("_id"))
        drafts = await db.brain_email_drafts.find(
            {"email_id": em_id}, {"_id": 1, "status": 1, "created_at": 1}
        ).to_list(5)

        result.append({
            "id": em_id,
            **{k: v for k, v in em.items()},
            "drafts": [{
                "id": str(d.pop("_id")),
                **{k: v for k, v in d.items() if k != "_id"},
            } for d in drafts],
            "has_draft": len(drafts) > 0,
            "draft_status": drafts[0]["status"] if drafts else None,
        })

    return result


async def get_draft(draft_id: str) -> dict:
    """Einzelnen Entwurf laden."""
    from bson import ObjectId
    db = get_db()
    draft = await db.brain_email_drafts.find_one({"_id": ObjectId(draft_id)})
    if not draft:
        return None
    draft["id"] = str(draft.pop("_id"))
    return draft
