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
    return """<div style="background:#113655;padding:24px 32px;border-radius:4px 4px 0 0">
      <h2 style="color:white;margin:0;font-size:18px;font-weight:700;letter-spacing:-0.3px">Studienkolleg Aachen</h2>
      <p style="color:rgba(255,255,255,0.55);margin:4px 0 0;font-size:12px;font-weight:400">Way2Germany</p>
    </div>"""


def _footer(lang: str = "de") -> str:
    if lang == "en":
        return """<div style="border-top:1px solid #e2e8f0;margin-top:32px;padding-top:20px">
      <p style="color:#94a3b8;font-size:11px;line-height:1.7;margin:0">
        <strong>W2G Academy GmbH</strong><br>
        Theaterstr. 30–32, 52062 Aachen, Germany<br>
        Managing Director: Laura Saboor<br>
        Registered: Amtsgericht Aachen, HRB 23610<br>
        Email: <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a><br><br>
        This is an automated message from Studienkolleg Aachen.<br>
        Please reply to <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a> if you have questions.
      </p></div>"""
    return """<div style="border-top:1px solid #e2e8f0;margin-top:32px;padding-top:20px">
      <p style="color:#94a3b8;font-size:11px;line-height:1.7;margin:0">
        <strong>W2G Academy GmbH</strong><br>
        Theaterstr. 30–32, 52062 Aachen<br>
        Geschäftsführung: Laura Saboor<br>
        Registergericht: Amtsgericht Aachen, HRB 23610<br>
        Kontakt: <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a><br><br>
        Dies ist eine automatische Nachricht von Studienkolleg Aachen.<br>
        Bei Fragen antworte bitte an <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a>.
      </p></div>"""


def _wrap(content: str, lang: str = "de") -> str:
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f8fafc">
<div style="font-family:'Inter','Helvetica Neue',Arial,sans-serif;max-width:600px;margin:32px auto;padding:0;background:#ffffff;border-radius:4px;border:1px solid #e2e8f0">
    {_header()}
    <div style="padding:28px 32px">{content}</div>
    {_footer(lang)}
</div>
</body></html>"""


def _btn(url: str, text: str) -> str:
    return f"""<a href="{url}" style="display:inline-block;background:#113655;color:white;padding:12px 28px;border-radius:4px;text-decoration:none;font-weight:600;margin-top:16px;font-size:14px;letter-spacing:-0.2px">{text}</a>"""


def _divider() -> str:
    return '<div style="border-top:1px solid #f1f5f9;margin:24px 0"></div>'


# ─── Templates ─────────────────────────────────────────────────────────────────

def send_welcome(to: str, full_name: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    if lang == "en":
        subject = "Welcome to Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Welcome, {name}!</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Your account has been successfully created. You can now log in to your personal portal to track your application and manage your documents.</p>
        {_btn(f'{app_url}/portal', 'Go to Portal')}
        {_divider()}
        <p style="color:#64748b;font-size:13px;line-height:1.6">If you have questions, contact us at <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a>.</p>"""
    else:
        subject = "Willkommen bei Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Willkommen, {name}!</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Dein Konto wurde erfolgreich erstellt. Du kannst dich ab sofort in dein persönliches Portal einloggen, deinen Bewerbungsprozess verfolgen und Dokumente verwalten.</p>
        {_btn(f'{app_url}/portal', 'Zum Portal')}
        {_divider()}
        <p style="color:#64748b;font-size:13px;line-height:1.6">Bei Fragen erreichst du uns jederzeit unter <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a>.</p>"""

    return _send(to, subject, _wrap(content, lang))


def send_application_received(to: str, full_name: str, application_id: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    ref = application_id[-6:].upper() if application_id else "------"
    app_url = _get_app_url()

    if lang == "en":
        subject = "Application Received – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">We have received your application (Ref: <strong>#{ref}</strong>). Our team will review your documents and respond within 24 hours.</p>
        <p style="color:#475569;line-height:1.7;font-size:14px">You can check your application status at any time in your portal.</p>
        {_btn(f'{app_url}/portal', 'Go to Portal')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Questions? Contact us at <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a>.</p>"""
    else:
        subject = "Bewerbung eingegangen – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Deine Bewerbung ist bei uns eingegangen (Ref: <strong>#{ref}</strong>). Unser Team prüft deine Unterlagen und meldet sich innerhalb von 24 Stunden bei dir.</p>
        <p style="color:#475569;line-height:1.7;font-size:14px">Du kannst deinen Bewerbungsstatus jederzeit in deinem Portal einsehen.</p>
        {_btn(f'{app_url}/portal', 'Zum Portal')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Bei Fragen erreichst du uns unter <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a>.</p>"""

    return _send(to, subject, _wrap(content, lang))


def send_document_requested(to: str, full_name: str, document_types: list, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    docs_list = "".join(f"<li style='margin:6px 0;color:#475569;font-size:14px'>{d}</li>" for d in document_types)
    app_url = _get_app_url()

    if lang == "en":
        subject = "Documents Requested – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">We need the following documents to continue processing your application:</p>
        <ul style="padding-left:20px;margin:16px 0">{docs_list}</ul>
        <p style="color:#475569;line-height:1.7;font-size:14px">Please upload them in your portal as soon as possible.</p>
        {_btn(f'{app_url}/portal/documents', 'Upload Documents')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""
    else:
        subject = "Dokumente angefordert – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Zur Weiterbearbeitung deiner Bewerbung benötigen wir folgende Dokumente:</p>
        <ul style="padding-left:20px;margin:16px 0">{docs_list}</ul>
        <p style="color:#475569;line-height:1.7;font-size:14px">Bitte lade diese so bald wie möglich in deinem Portal hoch.</p>
        {_btn(f'{app_url}/portal/documents', 'Dokumente hochladen')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Bei Fragen: <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_status_changed(to: str, full_name: str, new_status: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    status_labels_de = {
        "in_review": "In Prüfung",
        "pending_docs": "Dokumente ausstehend",
        "interview_scheduled": "Beratungsgespräch geplant",
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
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Your application status has been updated:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:14px 18px;margin:20px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0;font-size:16px">{label}</p>
        </div>
        <p style="color:#475569;line-height:1.7;font-size:14px">Log in to your portal for details and next steps.</p>
        {_btn(f'{app_url}/portal/journey', 'View Status')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""
    else:
        label = status_labels_de.get(new_status, new_status)
        subject = f"Bewerbungsupdate: {label} – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Der Status deiner Bewerbung wurde aktualisiert:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:14px 18px;margin:20px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0;font-size:16px">{label}</p>
        </div>
        <p style="color:#475569;line-height:1.7;font-size:14px">Melde dich in deinem Portal an, um Details und nächste Schritte zu sehen.</p>
        {_btn(f'{app_url}/portal/journey', 'Status ansehen')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Bei Fragen: <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_password_reset(to: str, reset_url: str, lang: str = "de") -> bool:
    if lang == "en":
        subject = "Reset Password – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Reset Your Password</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Click the button below to reset your password. This link is valid for 1 hour.</p>
        {_btn(reset_url, 'Reset Password')}
        {_divider()}
        <p style="color:#94a3b8;font-size:12px">If you did not request a password reset, please ignore this email.</p>"""
    else:
        subject = "Passwort zurücksetzen – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Passwort zurücksetzen</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Klicke auf den Button, um dein Passwort zurückzusetzen. Dieser Link ist 1 Stunde gültig.</p>
        {_btn(reset_url, 'Passwort zurücksetzen')}
        {_divider()}
        <p style="color:#94a3b8;font-size:12px">Falls du keinen Reset angefordert hast, ignoriere diese E-Mail.</p>"""

    return _send(to, subject, _wrap(content, lang))


def send_invite(to: str, full_name: str, invite_url: str, role: str, lang: str = "de") -> bool:
    name = full_name or ("User" if lang == "en" else "Nutzer/in")
    role_labels_de = {"staff": "Mitarbeiter/in", "teacher": "Lehrer/in", "admin": "Administrator/in", "accounting_staff": "Buchhaltung"}
    role_labels_en = {"staff": "Staff Member", "teacher": "Teacher", "admin": "Administrator", "accounting_staff": "Accounting"}

    if lang == "en":
        role_label = role_labels_en.get(role, role)
        subject = "Platform Invitation – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">You have been invited as <strong>{role_label}</strong> to the Studienkolleg Aachen platform. This invitation link is valid for 7 days.</p>
        {_btn(invite_url, 'Create Account')}
        {_divider()}
        <p style="color:#94a3b8;font-size:12px">If you did not expect this invitation, please ignore this email.</p>"""
    else:
        role_label = role_labels_de.get(role, role)
        subject = "Einladung zur Plattform – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Du wurdest als <strong>{role_label}</strong> zur Plattform von Studienkolleg Aachen eingeladen. Dieser Einladungslink ist 7 Tage gültig.</p>
        {_btn(invite_url, 'Konto erstellen')}
        {_divider()}
        <p style="color:#94a3b8;font-size:12px">Falls du keine Einladung erwartest, ignoriere diese E-Mail.</p>"""

    return _send(to, subject, _wrap(content, lang))


def send_teacher_assigned(to: str, full_name: str, teacher_name: str, lang: str = "de") -> bool:
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    if lang == "en":
        subject = "Supervisor Assigned – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">A supervisor has been assigned to support you during your studies:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:14px 18px;margin:20px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0">{teacher_name}</p>
        </div>
        <p style="color:#475569;line-height:1.7;font-size:14px">You can manage your data sharing preferences in the Consents section of your portal.</p>
        {_btn(f'{app_url}/portal/consents', 'Manage Consents')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""
    else:
        subject = "Betreuer/in zugewiesen – Studienkolleg Aachen"
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        <p style="color:#475569;line-height:1.7;font-size:14px">Dir wurde eine Betreuungsperson für dein Studium zugewiesen:</p>
        <div style="background:#f1f5f9;border-left:4px solid #113655;padding:14px 18px;margin:20px 0;border-radius:0 4px 4px 0">
          <p style="color:#113655;font-weight:700;margin:0">{teacher_name}</p>
        </div>
        <p style="color:#475569;line-height:1.7;font-size:14px">Du kannst deine Einwilligungen zur Datenweitergabe jederzeit in deinem Portal verwalten.</p>
        {_btn(f'{app_url}/portal/consents', 'Einwilligungen verwalten')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Bei Fragen: <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_precheck_process_update(
    to: str,
    full_name: str,
    status_context: str,
    area_context: str,
    lang: str = "de",
    requires_staff_review: bool = False,
    requires_authority_or_university_decision: bool = False,
) -> bool:
    """
    Sendet ein klar getrenntes Vorprüfungs-Update:
    1) Vorprüfung (informativ)
    2) Staff-Prüfung erforderlich (falls relevant)
    3) Behörden-/Uni-Entscheidung erforderlich (falls relevant)
    + ausdrücklicher Hinweis: keine Zusagegarantie
    """
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    if lang == "en":
        subject = "Precheck Update – Studies Application Status"
        precheck_section = f"""
        <h4 style="color:#113655;margin:0 0 8px;font-size:15px">Precheck</h4>
        <p style="color:#475569;line-height:1.7;font-size:14px;margin:0">
          Your case has been prechecked in the area <strong>{area_context}</strong>
          with current status context <strong>{status_context}</strong>.
          This step is a formal precheck and not a final admission decision.
        </p>"""
        staff_section = f"""
        <h4 style="color:#113655;margin:20px 0 8px;font-size:15px">Staff review required</h4>
        <p style="color:#475569;line-height:1.7;font-size:14px;margin:0">
          A manual review by our staff team is required before further processing.
        </p>""" if requires_staff_review else ""
        authority_section = f"""
        <h4 style="color:#113655;margin:20px 0 8px;font-size:15px">Authority/University decision may be required</h4>
        <p style="color:#475569;line-height:1.7;font-size:14px;margin:0">
          Clarification by an authority or partner university may be needed depending on your specific documents.
        </p>""" if requires_authority_or_university_decision else ""
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        {precheck_section}
        {staff_section}
        {authority_section}
        {_divider()}
        <p style="color:#334155;line-height:1.7;font-size:14px"><strong>No admission guarantee:</strong> This communication does not guarantee admission, seat reservation, or final acceptance.</p>
        {_btn(f'{app_url}/portal/journey', 'Open Application Status')}
        <p style="color:#64748b;font-size:13px;margin-top:16px">Questions? <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""
    else:
        subject = "Vorprüfungs-Update – Bewerbungsstatus"
        precheck_section = f"""
        <h4 style="color:#113655;margin:0 0 8px;font-size:15px">Vorprüfung</h4>
        <p style="color:#475569;line-height:1.7;font-size:14px;margin:0">
          Dein Fall wurde im Bereich <strong>{area_context}</strong> mit dem aktuellen Statuskontext
          <strong>{status_context}</strong> vorgeprüft.
          Dieser Schritt ist eine formale Vorprüfung und keine finale Zulassungsentscheidung.
        </p>"""
        staff_section = f"""
        <h4 style="color:#113655;margin:20px 0 8px;font-size:15px">Staff-Prüfung erforderlich</h4>
        <p style="color:#475569;line-height:1.7;font-size:14px;margin:0">
          Vor der weiteren Bearbeitung ist eine manuelle Prüfung durch unser Staff-Team erforderlich.
        </p>""" if requires_staff_review else ""
        authority_section = f"""
        <h4 style="color:#113655;margin:20px 0 8px;font-size:15px">Ggf. Behörden-/Uni-Entscheidung erforderlich</h4>
        <p style="color:#475569;line-height:1.7;font-size:14px;margin:0">
          Abhängig von deinen Unterlagen kann eine Klärung mit Behörde oder Partnerhochschule notwendig sein.
        </p>""" if requires_authority_or_university_decision else ""
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        {precheck_section}
        {staff_section}
        {authority_section}
        {_divider()}
        <p style="color:#334155;line-height:1.7;font-size:14px"><strong>Keine Zusagegarantie:</strong> Diese Mitteilung stellt keine Garantie auf Zulassung, Platzreservierung oder finale Annahme dar.</p>
        {_btn(f'{app_url}/portal/journey', 'Bewerbungsstatus öffnen')}
        <p style="color:#64748b;font-size:13px;margin-top:16px">Fragen? <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a></p>"""

    return _send(to, subject, _wrap(content, lang))


def send_case_email(to: str, full_name: str, subject_line: str, body_text: str, lang: str = "de") -> bool:
    """Staff-initiated email from case context – uses CI template wrapper."""
    name = full_name or ("Applicant" if lang == "en" else "Bewerber/in")
    app_url = _get_app_url()

    paragraphs = "".join(
        f'<p style="color:#475569;line-height:1.7;font-size:14px">{p.strip()}</p>'
        for p in body_text.strip().split("\n") if p.strip()
    )

    if lang == "en":
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hello {name},</h3>
        {paragraphs}
        {_btn(f'{app_url}/portal', 'Go to Portal')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">This message was sent by a team member of Studienkolleg Aachen.<br>
        Reply to <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a> for further questions.</p>"""
    else:
        content = f"""<h3 style="color:#113655;margin-top:0;font-size:16px">Hallo {name},</h3>
        {paragraphs}
        {_btn(f'{app_url}/portal', 'Zum Portal')}
        {_divider()}
        <p style="color:#64748b;font-size:13px">Diese Nachricht wurde von einem Teammitglied des Studienkolleg Aachen gesendet.<br>
        Antworte an <a href="mailto:info@stk-aachen.de" style="color:#113655;text-decoration:none">info@stk-aachen.de</a> für weitere Fragen.</p>"""

    return _send(to, subject_line, _wrap(content, lang))
