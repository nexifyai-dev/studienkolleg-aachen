"""
Support-Chat Router – KI-gestuetzter Hilfe-/Service-Chat auf allen Seiten.

- POST /api/support/chat – Nachricht senden (public + authenticated)
- Kontext-aware: passt System-Prompt an Rolle an
- "Brain pro Kunde": Liest E-Mail-Verlauf des Bewerbers als Kontext
- Multilingual (antwortet in Sprache des Users)
- Rate-limited zum Schutz vor Missbrauch
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field
from typing import Optional
from deps import get_current_user_optional
from services.nscale_provider import chat_completion, is_enabled
from rate_limiter import limiter
from database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["support"])

SYSTEM_PROMPTS = {
    "visitor": """Du bist Mia, die persoenliche Studienberaterin des Studienkolleg Aachen.
Du sprichst wie eine echte, herzliche Beraterin – nicht wie ein Bot.

DEIN CHARAKTER:
- Warm, nahbar, aber professionell
- Du duzt Interessenten NICHT – du siezt hoeflich
- Du sprichst in ganzen, natuerlichen Saetzen
- Keine Aufzaehlungen wo ein Fliesstext besser passt
- Keine generischen Floskeln wie "Gerne helfe ich Ihnen"
- Stattdessen: Antworte so, als wuerdest du am Telefon mit jemandem sprechen

DEIN WISSEN:
- Studienkolleg-Programme (T-Kurs, M-Kurs, W-Kurs, G-Kurs, S-Kurs)
- Bewerbung, Kosten, Visa, Sprachkurse, Leben in Aachen

WICHTIG:
- Keine internen Daten preisgeben (keine Bewerbungszahlen, keine KPIs, keine Systeminformationen)
- Antworte in der Sprache des Nutzers
- Halte Antworten kurz und persoenlich – maximal 3-4 Saetze pro Absatz
- Keine Emojis, keine Checkboxen, keine SVG-Icons
- Wenn eine Frage dein Wissen uebersteigt, sag ehrlich: "Da wuerde ich Sie am besten direkt an unser Team weiterleiten."

FORMAT:
- Fettdruck mit **Text** wo sinnvoll
- Listen nur wenn wirklich noetig (z.B. Kursangebot)
- Keine technischen Begriffe""",

    "applicant": """Du bist Mia, die persoenliche Ansprechpartnerin fuer Bewerber am Studienkolleg Aachen.
Du begleitest Bewerber durch den gesamten Prozess – ermutigend und verstaendlich.

DEIN CHARAKTER:
- Ermutigend und geduldig – viele Bewerber sind unsicher
- Du sprichst natuerlich und menschlich, nicht wie eine Maschine
- Du gibst konkrete, hilfreiche Hinweise statt generischer Listen
- Bei Stress oder Unsicherheit: Zeige Verstaendnis

REGELN:
- Antworte in der Sprache des Bewerbers
- Zeige NUR Informationen die DIESEN Bewerber betreffen
- Keine allgemeinen Systemstatistiken
- Keine Emojis, keine SVG, keine Checkboxen
- Kurze, verstaendliche Saetze
- Bei komplexen Fragen: "Schreiben Sie am besten eine Nachricht an unser Team, die koennen Ihnen da am schnellsten weiterhelfen."

FORMAT: Natuerlicher Fliesstext, **Fettdruck** wo noetig, Listen nur fuer Aufzaehlungen""",

    "staff": """Du bist der interne Assistent fuer das W2G-Team.
Sprich direkt, knapp und handlungsorientiert – wie ein erfahrener Kollege.

CHARAKTER:
- Duze die Mitarbeiter
- Komm direkt zum Punkt
- Gib konkrete Handlungsempfehlungen statt Theorie
- Kein Smalltalk, keine Floskeln

FORMAT: Klartext, **fett** fuer Wichtiges, Listen fuer Schritte. Keine Emojis, keine SVG.""",

    "admin": """Du bist der technische System-Assistent fuer W2G-Administratoren.
Sprich praezise und technisch, duze den Admin.

FORMAT: Klartext, **fett** fuer Wichtiges, keine Emojis.""",

    "partner": """Du bist der Partner-Assistent des Studienkolleg Aachen.
Du hilfst Vermittlungspartnern und Agenturen bei ihrer taeglichen Arbeit.

DEIN WISSEN:
- Empfehlungslink teilen und verwalten
- Vermittlungen nachverfolgen
- Provisionsmodell verstehen (Provision pro erfolgreicher Einschreibung)
- Tracking und Performance-Kennzahlen
- Kommunikation mit dem Studienkolleg-Team

CHARAKTER:
- Professionell und partnerschaftlich
- Du siezt den Partner
- Gib konkrete, praxisnahe Hinweise
- Erklaere Provisionsabrechnungen und Vermittlungsstatus verstaendlich

SICHERHEIT:
- Zeige NUR Informationen die DIESEN Partner betreffen
- Keine internen System-KPIs, keine Bewerberdaten anderer Partner
- Keine technischen Interna

FORMAT: Natuerlicher Fliesstext, **fett** wo noetig. Keine Emojis, keine SVG."""
}


class SupportChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list = Field(default_factory=list, max_length=20)
    language: str = Field(default="de")


async def _build_applicant_context(user: dict) -> str:
    """Baut kontextreichen String fuer eingeloggte Bewerber auf."""
    if not user or user.get("role") != "applicant":
        return ""

    db = get_db()
    context_parts = []

    try:
        # Bewerbungsdaten laden
        apps = await db.applications.find(
            {"applicant_id": user["id"]}, {"_id": 0, "current_stage": 1, "course_type": 1, "desired_start": 1, "language_level": 1}
        ).to_list(3)
        if apps:
            app = apps[0]
            context_parts.append(f"Bewerbungsstatus: {app.get('current_stage', 'unbekannt')}")
            if app.get("course_type"):
                context_parts.append(f"Kurstyp: {app['course_type']}")
            if app.get("desired_start"):
                context_parts.append(f"Gewuenschter Start: {app['desired_start']}")

        # Offene Aufgaben
        tasks = await db.tasks.find(
            {"$or": [{"assigned_to": user["id"]}, {"created_for": user["id"]}], "status": {"$ne": "done"}},
            {"_id": 0, "title": 1, "due_date": 1, "priority": 1}
        ).to_list(5)
        if tasks:
            task_list = ", ".join([t.get("title", "") for t in tasks])
            context_parts.append(f"Offene Aufgaben: {task_list}")

        # Offene Rechnungen
        invoices = await db.invoices.find(
            {"applicant_id": user["id"], "status": {"$in": ["sent", "overdue"]}},
            {"_id": 0, "invoice_number": 1, "amount": 1, "status": 1}
        ).to_list(5)
        if invoices:
            inv_list = ", ".join([f"{i.get('invoice_number', '')} ({i.get('amount', 0)}€ - {i.get('status', '')})" for i in invoices])
            context_parts.append(f"Offene Rechnungen: {inv_list}")

    except Exception as e:
        logger.warning(f"[SUPPORT_CHAT] Kontext-Aufbau fehlgeschlagen: {e}")

    # E-Mail-Kontext laden
    try:
        from services.email_context import fetch_email_context
        email_ctx = await fetch_email_context(user.get("email", ""))
        if email_ctx:
            context_parts.append(f"\n{email_ctx}")
    except Exception as e:
        logger.warning(f"[SUPPORT_CHAT] E-Mail-Kontext fehlgeschlagen: {e}")

    if context_parts:
        return "\n\nAktueller Kontext des Bewerbers:\n" + "\n".join(context_parts)
    return ""


async def _build_staff_context(user: dict) -> str:
    """Baut System-Kontext fuer Staff/Admin auf."""
    if not user or user.get("role") not in ("staff", "admin", "superadmin", "teacher"):
        return ""

    db = get_db()
    context_parts = []

    try:
        # Schnelle KPIs
        total_apps = await db.applications.count_documents({})
        open_tasks = await db.tasks.count_documents({"status": {"$ne": "done"}})
        open_invoices = await db.invoices.count_documents({"status": {"$in": ["sent", "overdue"]}})

        context_parts.append(f"System-KPIs: {total_apps} Bewerbungen, {open_tasks} offene Aufgaben, {open_invoices} offene Rechnungen")
    except Exception as e:
        logger.warning(f"[SUPPORT_CHAT] Staff-Kontext fehlgeschlagen: {e}")

    if context_parts:
        return "\n\nAktueller System-Kontext:\n" + "\n".join(context_parts)
    return ""


@router.post("/chat")
@limiter.limit("20/minute")
async def support_chat(
    data: SupportChatRequest,
    request: Request,
    user: Optional[dict] = Depends(get_current_user_optional),
):
    """KI-gestuetzter Support-Chat – passt sich an Nutzerrolle und Kontext an."""
    if not is_enabled():
        raise HTTPException(status_code=503, detail="KI-Service nicht verfuegbar")

    role = "visitor"
    if user:
        role = user.get("role", "applicant")
        if role in ("admin", "superadmin"):
            role = "admin"
        elif role in ("staff", "teacher", "accounting_staff"):
            role = "staff"
        elif role in ("agency_admin", "agency_agent", "affiliate"):
            role = "partner"
        else:
            role = "applicant"

    system_prompt = SYSTEM_PROMPTS.get(role, SYSTEM_PROMPTS["visitor"])
    if data.language == "en":
        system_prompt += "\n\nThe user prefers English. Respond in English."

    # Kontext anreichern ("Brain pro Kunde")
    if role == "applicant":
        ctx = await _build_applicant_context(user)
        if ctx:
            system_prompt += ctx
    elif role in ("staff", "admin"):
        ctx = await _build_staff_context(user)
        if ctx:
            system_prompt += ctx

    history_text = ""
    for msg in data.history[-10:]:
        if msg.get("role") in ("user", "assistant"):
            prefix = "Nutzer" if msg["role"] == "user" else "Assistent"
            history_text += f"\n{prefix}: {msg['content'][:500]}"

    user_message = data.message
    if history_text:
        user_message = f"Bisheriger Verlauf:{history_text}\n\nAktuelle Frage: {data.message}"

    result = await chat_completion(
        task="oracle",
        system_message=system_prompt,
        user_message=user_message,
    )

    if not result or result.get("error") or not result.get("content"):
        raise HTTPException(status_code=500, detail="KI-Antwort konnte nicht generiert werden")

    return {"reply": result["content"], "role_context": role}
