"""
Email service – Resend integration with bilingual templates (DE/EN).

All templates support language selection via `lang` parameter.
Language is determined by user.language_pref (default: "de").

Domain: send.nexify-automate.com
Reply-To: info@stk-aachen.de
Legal entity: W2G Academy GmbH, Amtsgericht Aachen HRB 23610

Pricing rule: No fixed prices in any email. All cost references are individual/case-dependent.
"""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

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


def _get_app_url() -> str:
    return os.environ.get("APP_URL", os.environ.get("REACT_APP_BACKEND_URL", ""))


def _send(to: str, subject: str, html: str) -> bool:
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


# ─── Shared Components ─────────────────────────────────────────────────────────

def _header() -> str:
    return """<div style="background:#113655;padding:20px 24px;border-radius:4px 4px 0 0">
      <h2 style="color:white;margin:0;font-size:18px;font-weight:700">Studienkolleg Aachen</h2>
      <p style="color:rgba(255,255,255,0.6);margin:4px 0 0;font-size:12px">Way2Germany</p>
    </div>"""


def _footer(lang: str = "de") -> str:
    if lang == "en":
        return """<div style="border-top:1px solid #e2e8f0;margin-top:32px;padding-top:16px">
      <p style="color:#94a3b8;font-size:11px;line-height:1.6;margin:0">
        W2G Academy GmbH · Amtsgericht Aachen HRB 23610<br>
        Theaterstr. 30–32, 52062 Aachen · <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a><br>
        This is an automated message. Please do not reply directly to this email.
      </p></div>"""
    return """<div style="border-top:1px solid #e2e8f0;margin-top:32px;padding-top:16px">
      <p style="color:#94a3b8;font-size:11px;line-height:1.6;margin:0">
        W2G Academy GmbH · Amtsgericht Aachen HRB 23610<br>
        Theaterstr. 30–32, 52062 Aachen · <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a><br>
        Dies ist eine automatische Nachricht. Bitte antworte nicht direkt auf diese E-Mail.
      </p></div>"""


def _wrap(content: str, lang: str = "de") -> str:
    return f"""<div style="font-family:'Inter','Helvetica Neue',Arial,sans-serif;max-width:600px;margin:auto;padding:0;background:#ffffff">
    {_header()}
    <div style="padding:24px">{content}</div>
    {_footer(lang)}
    </div>"""


def _btn(url: str, text: str) -> str:
    return f"""<a href="{url}" style="display:inline-block;background:#113655;color:white;padding:12px 24px;border-radius:4px;text-decoration:none;font-weight:600;margin-top:16px;font-size:14px">{text}</a>"""


# ─── Templates ─────────────────────────────────────────────────────────────────

def send_welcome(to: str, full_name: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    if lang == "en":
        subject = "Welcome to Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Welcome, {name}!</h3>
        <p style="color:#475569;line-height:1.6">Your account has been created successfully. You can now log in to your personal portal to track your application.</p>
        {_btn(f'{app_url}/portal', 'Go to Portal →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Questions? Contact us at <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""
    else:
        subject = "Willkommen bei Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Willkommen, {name}!</h3>
        <p style="color:#475569;line-height:1.6">Dein Konto wurde erfolgreich erstellt. Du kannst dich jetzt in dein persönliches Portal einloggen und deinen Bewerbungsprozess verfolgen.</p>
        {_btn(f'{app_url}/portal', 'Zum Portal →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Fragen? Schreib uns an <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_application_received(to: str, full_name: str, application_id: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    ref = application_id[-6:].upper() if application_id else "------"
    app_url = _get_app_url()

    if lang == "en":
        subject = "Application Received – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hello {name},</h3>
        <p style="color:#475569;line-height:1.6">Your application has been received (Ref: #{ref}). Our team will review your documents and get back to you within 24 hours.</p>
        <p style="color:#475569;line-height:1.6">You can check your application status at any time in your portal.</p>
        {_btn(f'{app_url}/portal', 'Go to Portal →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""
    else:
        subject = "Bewerbung eingegangen – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.6">Deine Bewerbung ist bei uns eingegangen (Ref: #{ref}). Unser Team prüft deine Unterlagen und meldet sich innerhalb von 24 Stunden bei dir.</p>
        <p style="color:#475569;line-height:1.6">Du kannst deinen Bewerbungsstatus jederzeit in deinem Portal einsehen.</p>
        {_btn(f'{app_url}/portal', 'Zum Portal →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Fragen? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_document_requested(to: str, full_name: str, document_types: list, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    docs_list = "".join(f"<li style='margin:4px 0;color:#475569'>{d}</li>" for d in document_types)
    app_url = _get_app_url()

    if lang == "en":
        subject = "Documents Requested – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hello {name},</h3>
        <p style="color:#475569;line-height:1.6">We need the following documents from you to continue processing your application:</p>
        <ul style="padding-left:20px">{docs_list}</ul>
        <p style="color:#475569;line-height:1.6">Please upload them in your portal as soon as possible.</p>
        {_btn(f'{app_url}/portal/documents', 'Upload Documents →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""
    else:
        subject = "Dokumente angefordert – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.6">Wir benötigen folgende Dokumente von dir, um deine Bewerbung weiter bearbeiten zu können:</p>
        <ul style="padding-left:20px">{docs_list}</ul>
        <p style="color:#475569;line-height:1.6">Bitte lade diese so bald wie möglich in deinem Portal hoch.</p>
        {_btn(f'{app_url}/portal/documents', 'Dokumente hochladen →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Fragen? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_status_changed(to: str, full_name: str, new_status: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    status_labels_de = {
        "in_review": "In Prüfung",
        "pending_docs": "Dokumente ausstehend",
        "interview_scheduled": "Interview geplant",
        "conditional_offer": "Bedingte Zusage",
        "offer_sent": "Angebot versendet",
        "enrolled": "Eingeschrieben",
        "declined": "Abgelehnt",
        "on_hold": "Zurückgestellt",
    }
    status_labels_en = {
        "in_review": "Under Review",
        "pending_docs": "Documents Pending",
        "interview_scheduled": "Interview Scheduled",
        "conditional_offer": "Conditional Offer",
        "offer_sent": "Offer Sent",
        "enrolled": "Enrolled",
        "declined": "Declined",
        "on_hold": "On Hold",
    }

    if lang == "en":
        label = status_labels_en.get(new_status, new_status)
        subject = f"Application Update: {label} – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hello {name},</h3>
        <p style="color:#475569;line-height:1.6">Your application status has been updated:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:12px 16px;margin:16px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0;font-size:16px">{label}</p>
        </div>
        <p style="color:#475569;line-height:1.6">Log in to your portal for details and next steps.</p>
        {_btn(f'{app_url}/portal/journey', 'View Status →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""
    else:
        label = status_labels_de.get(new_status, new_status)
        subject = f"Bewerbungsupdate: {label} – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.6">Der Status deiner Bewerbung wurde aktualisiert:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:12px 16px;margin:16px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0;font-size:16px">{label}</p>
        </div>
        <p style="color:#475569;line-height:1.6">Melde dich in deinem Portal an, um Details und nächste Schritte zu sehen.</p>
        {_btn(f'{app_url}/portal/journey', 'Status ansehen →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Fragen? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_password_reset(to: str, reset_url: str, lang: str = "de") -> bool:
    if lang == "en":
        subject = "Reset Password – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Reset Your Password</h3>
        <p style="color:#475569;line-height:1.6">Click the button below to reset your password. This link is valid for 1 hour.</p>
        {_btn(reset_url, 'Reset Password →')}
        <p style="color:#94a3b8;font-size:12px;margin-top:24px">If you did not request a password reset, please ignore this email.</p>"""
    else:
        subject = "Passwort zurücksetzen – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Passwort zurücksetzen</h3>
        <p style="color:#475569;line-height:1.6">Klicke auf den Button, um dein Passwort zurückzusetzen. Dieser Link ist 1 Stunde gültig.</p>
        {_btn(reset_url, 'Passwort zurücksetzen →')}
        <p style="color:#94a3b8;font-size:12px;margin-top:24px">Falls du keinen Reset angefordert hast, ignoriere diese E-Mail.</p>"""

    return _send(to, subject, _wrap(content, lang))


def send_invite(to: str, full_name: str, invite_url: str, role: str, lang: str = "de") -> bool:
    name = full_name or ("User" if lang == "en" else "Nutzer/in")
    role_labels_de = {"staff": "Mitarbeiter/in", "teacher": "Lehrer/in", "admin": "Administrator/in", "accounting_staff": "Buchhaltung"}
    role_labels_en = {"staff": "Staff Member", "teacher": "Teacher", "admin": "Administrator", "accounting_staff": "Accounting"}

    if lang == "en":
        role_label = role_labels_en.get(role, role)
        subject = "Platform Invitation – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hello {name},</h3>
        <p style="color:#475569;line-height:1.6">You have been invited as <strong>{role_label}</strong> to the Studienkolleg Aachen platform. This invitation link is valid for 7 days.</p>
        {_btn(invite_url, 'Create Account →')}
        <p style="color:#94a3b8;font-size:12px;margin-top:24px">If you did not expect this invitation, please ignore this email.</p>"""
    else:
        role_label = role_labels_de.get(role, role)
        subject = "Einladung zur Plattform – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.6">Du wurdest als <strong>{role_label}</strong> zur Plattform von Studienkolleg Aachen eingeladen. Dieser Einladungslink ist 7 Tage gültig.</p>
        {_btn(invite_url, 'Konto erstellen →')}
        <p style="color:#94a3b8;font-size:12px;margin-top:24px">Falls du keine Einladung erwartest, ignoriere diese E-Mail.</p>"""

    return _send(to, subject, _wrap(content, lang))


def send_teacher_assigned(to: str, full_name: str, teacher_name: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    if lang == "en":
        subject = "Supervisor Assigned – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hello {name},</h3>
        <p style="color:#475569;line-height:1.6">A supervisor has been assigned to support you during your studies:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:12px 16px;margin:16px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0">{teacher_name}</p>
        </div>
        <p style="color:#475569;line-height:1.6">You can manage your data sharing preferences in the Consents section of your portal.</p>
        {_btn(f'{app_url}/portal/consents', 'Manage Consents →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""
    else:
        subject = "Betreuer/in zugewiesen – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.6">Dir wurde eine Betreuungsperson für dein Studium zugewiesen:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:12px 16px;margin:16px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0">{teacher_name}</p>
        </div>
        <p style="color:#475569;line-height:1.6">Du kannst deine Einwilligungen zur Datenweitergabe jederzeit in deinem Portal verwalten.</p>
        {_btn(f'{app_url}/portal/consents', 'Einwilligungen verwalten →')}
        <p style="color:#64748b;font-size:13px;margin-top:24px">Fragen? <a href="mailto:info@stk-aachen.de" style="color:#113655">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))
