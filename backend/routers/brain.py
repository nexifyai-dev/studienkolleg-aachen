"""
Brain Router – API-Endpoints fuer das KI-Gedaechtnis und den E-Mail-Agenten.

Endpoints:
- GET  /api/brain/stats          – Memory-Statistiken
- GET  /api/brain/recall/{id}    – Erinnerungen zu einer Entity abrufen
- POST /api/brain/ask            – Kontextuellen KI-Assistenten fragen
- POST /api/brain/search         – Memories durchsuchen
- GET  /api/brain/emails         – E-Mail-Inbox mit KI-Entwuerfen
- GET  /api/brain/drafts/{id}    – Einzelnen Entwurf laden
- POST /api/brain/drafts/{id}/approve – Entwurf genehmigen und senden
- POST /api/brain/drafts/{id}/reject  – Entwurf ablehnen
- POST /api/brain/drafts/{id}/edit    – Entwurf bearbeiten
- POST /api/brain/poll-inbox     – IMAP-Polling manuell ausloesen
- POST /api/brain/ingest         – Manuelles Wissen einspeisen
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from database import get_db
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES
from bson import ObjectId

router = APIRouter(prefix="/api/brain", tags=["brain"])


def _detect_query_language(text: str) -> str:
    """Detect language from user query text. Returns 'en' or 'de'."""
    if not text or len(text.strip()) < 5:
        return "de"
    sample = text[:300].lower()
    en_words = {"the ", " is ", " are ", " was ", " have ", " has ",
                " would ", " could ", " should ", " will ", " can ",
                " what ", " how ", " when ", " where ", " which ",
                "please ", "thank ", "hello ", " my ", " your ",
                " need ", " want ", " like ", " about "}
    de_words = {"der ", " die ", " das ", " ist ", " sind ", " hat ",
                " haben ", " wird ", " kann ", " was ", " wie ",
                " wann ", " wo ", " welche", "bitte ", "danke",
                "hallo ", " mein", " dein", " muss ", " noch "}
    en_count = sum(1 for w in en_words if w in sample)
    de_count = sum(1 for w in de_words if w in sample)
    if en_count > de_count:
        return "en"
    return "de"


@router.get("/stats")
async def brain_stats(user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Memory-Statistiken."""
    from services.brain_memory import get_brain_stats
    return await get_brain_stats()


@router.get("/recall/{entity_id}")
async def recall_memories(entity_id: str, category: str = None,
                          user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Erinnerungen zu einer Entity abrufen."""
    from services.brain_memory import recall
    memories = await recall(entity_id, category=category, limit=100)
    return {"entity_id": entity_id, "count": len(memories), "memories": memories}


@router.post("/ask")
async def ask_brain(request: Request, user: dict = Depends(get_current_user)):
    """Kontextuellen KI-Assistenten fragen – mit vollem Memory-Kontext."""
    body = await request.json()
    query = body.get("query", "")
    entity_id = body.get("entity_id", "")
    context = body.get("context", "")
    lang = body.get("lang", "")

    if not query:
        raise HTTPException(status_code=400, detail="Frage erforderlich")

    # Auto-detect language from query if not explicitly set
    if not lang:
        lang = _detect_query_language(query)

    from services.brain_memory import generate_response

    # Wenn entity_id eine Application ist, Bewerber-ID ermitteln
    if entity_id and len(entity_id) == 24:
        db = get_db()
        app = await db.applications.find_one({"_id": ObjectId(entity_id)}, {"applicant_id": 1})
        if app:
            entity_id = app.get("applicant_id", entity_id)

    # Oracle-Systemkontext laden (Live-Daten) — praezise Zahlen
    enriched_context = context
    try:
        from services.oracle_service import aggregate_system_context, _build_system_prompt
        sys_ctx = await aggregate_system_context()

        # Praezise Pipeline-Darstellung
        pipeline_str = ', '.join(f'{k}: {v}' for k, v in sys_ctx['applications']['pipeline'].items())
        task_str = ', '.join(f'{k}: {v}' for k, v in sys_ctx['tasks']['by_status'].items())
        doc_str = ', '.join(f'{k}: {v}' for k, v in sys_ctx['documents']['by_status'].items())

        enriched_context = f"""LIVE-SYSTEMDATEN (EXAKTE ZAHLEN - NUR DIESE NENNEN):

BEWERBUNGEN: {sys_ctx['applications']['total']} gesamt
Pipeline: {pipeline_str}

AUFGABEN: {sys_ctx['tasks']['total']} gesamt, davon {sys_ctx['tasks']['open']} offen
Aufschluesselung: {task_str}
Ueberfaellig: {sys_ctx['tasks']['overdue']}

DOKUMENTE: {sys_ctx['documents']['total']} gesamt
Dokumente zur Pruefung (Review-Queue): EXAKT {sys_ctx['documents']['review_queue']} Dokumente
Aufschluesselung: {doc_str}

OFFENE KONVERSATIONEN: {sys_ctx['conversations']['open']}

{context}"""
    except Exception:
        pass

    result = await generate_response(entity_id, enriched_context, query, lang=lang)
    return result


@router.post("/search")
async def search_brain(request: Request, user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Memories durchsuchen."""
    body = await request.json()
    query = body.get("query", "")
    entity_type = body.get("entity_type")
    if not query:
        raise HTTPException(status_code=400, detail="Suchbegriff erforderlich")

    from services.brain_memory import search_memories
    results = await search_memories(query, entity_type=entity_type, limit=30)
    return {"query": query, "count": len(results), "results": results}


# ── E-Mail Brain ───────────────────────────────────────────────────────────────

@router.get("/emails")
async def list_brain_emails(status: str = None, limit: int = 50,
                            user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """E-Mail-Inbox mit KI-Entwuerfen."""
    from services.email_brain import get_email_inbox
    return await get_email_inbox(limit=limit, status_filter=status)


@router.get("/drafts/{draft_id}")
async def get_draft(draft_id: str, user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Einzelnen Entwurf laden."""
    from services.email_brain import get_draft as get_draft_fn
    draft = await get_draft_fn(draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Entwurf nicht gefunden")
    return draft


@router.post("/drafts/{draft_id}/approve")
async def approve_draft(draft_id: str, request: Request,
                        user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Entwurf genehmigen und per SMTP senden."""
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    edited_body = body.get("edited_body")

    from services.email_brain import approve_and_send
    result = await approve_and_send(draft_id, approved_by=user["id"], edited_body=edited_body)
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.post("/drafts/{draft_id}/reject")
async def reject_draft(draft_id: str, request: Request,
                       user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Entwurf ablehnen."""
    db = get_db()
    body = await request.json() if request.headers.get("content-type") == "application/json" else {}
    reason = body.get("reason", "")

    result = await db.brain_email_drafts.update_one(
        {"_id": ObjectId(draft_id)},
        {"$set": {"status": "rejected", "reject_reason": reason, "rejected_by": user["id"]}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Entwurf nicht gefunden")
    return {"status": "rejected"}


@router.post("/drafts/{draft_id}/edit")
async def edit_draft(draft_id: str, request: Request,
                     user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """Entwurf bearbeiten (Body aktualisieren)."""
    db = get_db()
    body = await request.json()
    new_body = body.get("body", "")
    new_subject = body.get("subject")

    update = {"body": new_body, "edited_by": user["id"], "edited_at": datetime.now(timezone.utc)}
    if new_subject:
        update["subject"] = new_subject

    result = await db.brain_email_drafts.update_one(
        {"_id": ObjectId(draft_id)}, {"$set": update}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Entwurf nicht gefunden")
    return {"status": "updated"}


@router.post("/poll-inbox")
async def trigger_poll(user: dict = Depends(require_roles(*STAFF_ROLES, *ADMIN_ROLES))):
    """IMAP-Polling manuell ausloesen."""
    from services.email_brain import poll_inbox
    result = await poll_inbox(max_emails=50, since_days=30)
    return result


@router.post("/ingest")
async def ingest_knowledge(request: Request, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Manuelles Wissen einspeisen (Policies, Standardantworten etc.)."""
    body = await request.json()
    text = body.get("text", "")
    entity_id = body.get("entity_id", "institution")
    entity_type = body.get("entity_type", "institution")
    category = body.get("category", "institutional")

    if not text:
        raise HTTPException(status_code=400, detail="Text erforderlich")

    from services.brain_memory import extract_facts, remember
    facts = await extract_facts(text, category)
    if not facts:
        facts = [{"fact": text[:500], "category": category, "confidence": 0.8}]

    count = await remember(entity_id, entity_type, facts, source="manual_ingest")
    return {"ingested": count, "facts": facts}
