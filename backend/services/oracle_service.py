"""
Oracle Service – Zentrale Wissensquelle mit Live-Daten und KI-Chat.

Aggregiert Echtzeit-Daten aus allen Collections und stellt sie dem
LLM als Kontext zur Verfuegung. Jede Interaktion wird
automatisch in oracle_conversations protokolliert (Auto-Record).

Praezisionsprinzip: Jede Zahl muss mit der UI uebereinstimmen.
"""
import logging
from datetime import datetime, timezone
from bson import ObjectId
from database import get_db

logger = logging.getLogger(__name__)

STAGE_LABELS = {
    "lead_new": "Neue Anfrage",
    "in_review": "In Bearbeitung",
    "pending_docs": "Docs ausstehend",
    "interview_scheduled": "Interview geplant",
    "conditional_offer": "Bedingtes Angebot",
    "offer_sent": "Angebot versendet",
    "enrolled": "Eingeschrieben",
    "eligible": "Zugelassen",
    "declined": "Abgelehnt",
    "on_hold": "Pausiert",
    "archived": "Archiviert",
}

DOC_STATUS_LABELS = {
    "uploaded": "Hochgeladen (wartet auf Pruefung)",
    "in_review": "In Pruefung",
    "needs_review": "Pruefung erforderlich",
    "approved": "Akzeptiert",
    "rejected": "Abgelehnt",
    "superseded": "Ersetzt",
}


async def aggregate_system_context() -> dict:
    """Sammelt praezise Live-Daten aus allen relevanten Collections."""
    db = get_db()

    # --- Bewerbungen ---
    total_apps = await db.applications.count_documents({})
    pipeline_raw = await db.applications.aggregate([
        {"$group": {"_id": "$current_stage", "count": {"$sum": 1}}}
    ]).to_list(50)
    pipeline_counts = {p["_id"]: p["count"] for p in pipeline_raw if p["_id"]}

    # --- Aufgaben ---
    total_tasks = await db.tasks.count_documents({})
    task_pipeline = await db.tasks.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(20)
    task_by_status = {t["_id"]: t["count"] for t in task_pipeline if t["_id"]}
    open_tasks = task_by_status.get("open", 0) + task_by_status.get("in_progress", 0)

    # Ueberfaellige Aufgaben (due_date als String gespeichert)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    overdue_tasks = await db.tasks.count_documents({
        "status": {"$in": ["open", "in_progress"]},
        "due_date": {"$lt": now_iso, "$ne": None, "$exists": True}
    })

    # --- Rechnungen ---
    total_invoices = await db.invoices.count_documents({})
    inv_pipeline = await db.invoices.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}, "total": {"$sum": {"$ifNull": ["$amount", 0]}}}}
    ]).to_list(20)
    invoice_stats = {}
    for i in inv_pipeline:
        if i["_id"]:
            invoice_stats[i["_id"]] = {"count": i["count"], "total": round(i.get("total", 0), 2)}

    # --- Dokumente (praezise Aufschluesselung) ---
    total_docs = await db.documents.count_documents({})
    doc_pipeline = await db.documents.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]).to_list(20)
    doc_by_status = {d["_id"]: d["count"] for d in doc_pipeline if d["_id"]}

    # Review-Queue = uploaded + in_review + needs_review (= was Staff bearbeiten muss)
    review_queue = sum(doc_by_status.get(s, 0) for s in ["uploaded", "in_review", "needs_review"])

    # --- Benutzer ---
    user_pipeline = await db.users.aggregate([
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]).to_list(20)
    user_stats = {u["_id"]: u["count"] for u in user_pipeline if u["_id"]}

    # --- Konversationen / Ungelesene ---
    unread_convs = await db.conversations.count_documents({"status": "open"})

    # --- Letzte 5 Aktivitaeten ---
    recent_activities = await db.application_activities.find(
        {}, {"_id": 0, "action": 1, "new_value": 1, "actor_name": 1, "occurred_at": 1}
    ).sort("occurred_at", -1).to_list(5)

    context = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "applications": {
            "total": total_apps,
            "pipeline": {STAGE_LABELS.get(k, k): v for k, v in pipeline_counts.items()},
        },
        "tasks": {
            "total": total_tasks,
            "open": open_tasks,
            "by_status": task_by_status,
            "overdue": overdue_tasks,
        },
        "invoices": {
            "total": total_invoices,
            "by_status": invoice_stats,
        },
        "documents": {
            "total": total_docs,
            "by_status": doc_by_status,
            "review_queue": review_queue,
        },
        "users": user_stats,
        "conversations": {
            "open": unread_convs,
        },
        "recent_activities": [
            {
                "action": a.get("action", ""),
                "detail": str(a.get("new_value", ""))[:80],
                "actor": a.get("actor_name", ""),
                "time": a.get("occurred_at").isoformat() if a.get("occurred_at") else "",
            }
            for a in recent_activities
        ],
    }
    return context


def _build_system_prompt(context: dict) -> str:
    """Baut den System-Prompt mit praezisen Live-Daten."""
    pipeline_str = "\n".join(
        f"  - {stage}: {count}" for stage, count in context["applications"]["pipeline"].items()
    ) or "  (keine Bewerbungen)"

    inv_str = "\n".join(
        f"  - {status}: {data['count']} Stueck, {data['total']:.2f} EUR"
        for status, data in context["invoices"]["by_status"].items()
    ) or "  (keine Rechnungen)"

    task_str = "\n".join(
        f"  - {status}: {count}" for status, count in context["tasks"]["by_status"].items()
    ) or "  (keine Aufgaben)"

    doc_str = "\n".join(
        f"  - {DOC_STATUS_LABELS.get(status, status)}: {count}"
        for status, count in context["documents"]["by_status"].items()
    ) or "  (keine Dokumente)"

    activities_str = "\n".join(
        f"  - [{a['time'][:16]}] {a['action']}: {a['detail']} ({a['actor']})"
        for a in context["recent_activities"]
    ) or "  (keine Aktivitaeten)"

    return f"""Du bist der interne Operations-Assistent des Studienkolleg Aachen.

KRITISCHE REGEL: Nenne NUR die Zahlen, die unten stehen. Erfinde KEINE Zahlen.
Wenn du eine Zahl nennst, muss sie EXAKT mit den Daten unten uebereinstimmen.
Wenn du etwas nicht weisst, sage es. Halluziniere NICHT.

LIVE-SYSTEMDATEN (Stand: {context['timestamp'][:19]}):

BEWERBUNGEN ({context['applications']['total']} gesamt):
{pipeline_str}

AUFGABEN ({context['tasks']['total']} gesamt, {context['tasks']['open']} offen):
{task_str}
  Ueberfaellig: {context['tasks']['overdue']}

DOKUMENTE ({context['documents']['total']} gesamt):
  Review-Queue (zu pruefen): EXAKT {context['documents']['review_queue']} Dokumente
{doc_str}

RECHNUNGEN ({context['invoices']['total']} gesamt):
{inv_str}

OFFENE KONVERSATIONEN: {context['conversations']['open']}

BENUTZER: {', '.join(f'{role}: {count}' for role, count in context['users'].items())}

LETZTE AKTIVITAETEN:
{activities_str}

DEIN VERHALTEN:
- Sei PRAEZISE. Jede Zahl muss exakt den obigen Daten entsprechen.
- Antworte direkt und handlungsorientiert.
- Priorisiere: Was ist dringend? Was blockiert?
- Gib konkrete naechste Schritte.
- Formatiere mit Markdown (**fett**, Listen, Tabellen).
- Halte dich kurz: max 3-4 Absaetze.
- Antworte in der Sprache der Frage."""


async def process_query(
    user_message: str,
    conversation_id: str | None,
    user: dict,
) -> dict:
    """Verarbeitet eine Oracle-Anfrage mit praezisem Kontext."""
    db = get_db()
    context = await aggregate_system_context()
    system_prompt = _build_system_prompt(context)

    # Konversationshistorie laden
    history_messages = []
    if conversation_id:
        conv = await db.oracle_conversations.find_one({"_id": ObjectId(conversation_id)})
        if conv and conv.get("messages"):
            for msg in conv["messages"][-10:]:
                history_messages.append({"role": msg["role"], "content": msg["content"]})

    history_messages.append({"role": "user", "content": user_message})

    if len(history_messages) > 1:
        conversation_context = "\n".join(
            f"{'BENUTZER' if m['role'] == 'user' else 'ASSISTENT'}: {m['content']}"
            for m in history_messages[:-1]
        )
        full_user_message = f"BISHERIGER VERLAUF:\n{conversation_context}\n\nAKTUELLE FRAGE:\n{user_message}"
    else:
        full_user_message = user_message

    # Use OpenRouter (Gemini Flash) via openrouter_provider
    from services.openrouter_provider import chat_completion, is_enabled
    if not is_enabled():
        ai_response = "OpenRouter API nicht konfiguriert. KI ist deaktiviert."
        model_used = None
        tokens_used = 0
    else:
        result = await chat_completion(
            task="brain_response",
            system_message=system_prompt,
            user_message=full_user_message,
            temperature=0.3,
            override_max_tokens=2048,
        )
        if result["content"]:
            ai_response = result["content"]
            model_used = result["model"]
            tokens_used = result["tokens_used"]
        else:
            ai_response = f"Fehler bei der KI-Verarbeitung: {result.get('error', 'Unbekannt')}"
            model_used = result.get("model")
            tokens_used = 0

    now = datetime.now(timezone.utc)

    user_msg_doc = {
        "role": "user",
        "content": user_message,
        "timestamp": now,
        "actor_id": user["id"],
        "actor_name": user.get("full_name", user.get("email", "")),
    }
    assistant_msg_doc = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": now,
        "model": model_used,
        "tokens_used": tokens_used,
    }

    if conversation_id:
        await db.oracle_conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$push": {"messages": {"$each": [user_msg_doc, assistant_msg_doc]}},
                "$set": {"updated_at": now},
                "$inc": {"message_count": 2, "total_tokens": tokens_used},
            },
        )
    else:
        title = user_message[:60] + ("..." if len(user_message) > 60 else "")
        conv_doc = {
            "title": title,
            "created_by": user["id"],
            "created_by_name": user.get("full_name", user.get("email", "")),
            "messages": [user_msg_doc, assistant_msg_doc],
            "message_count": 2,
            "total_tokens": tokens_used,
            "created_at": now,
            "updated_at": now,
        }
        result_insert = await db.oracle_conversations.insert_one(conv_doc)
        conversation_id = str(result_insert.inserted_id)

    return {
        "conversation_id": conversation_id,
        "response": ai_response,
        "model": model_used,
        "tokens_used": tokens_used,
        "context_snapshot": {
            "total_applications": context["applications"]["total"],
            "open_tasks": context["tasks"]["open"],
            "overdue_tasks": context["tasks"]["overdue"],
            "pending_documents": context["documents"]["review_queue"],
            "total_invoices": context["invoices"]["total"],
        },
    }
