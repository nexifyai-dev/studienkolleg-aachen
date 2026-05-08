"""
AI Screening Router – KI-gestützte Bewerbervorprüfung.

Endpunkte:
- POST /api/applications/{app_id}/ai-screen  – Neue Prüfung starten (Staff only)
- GET  /api/applications/{app_id}/ai-screenings – Prüfungsverlauf abrufen

Sicherheit:
- Nur Staff/Admin darf Prüfung starten
- Bewerber sieht eigene Prüfungen nicht (intern)
- Klare Trennung: AI suggestion vs. Staff decision vs. Final status
- Audit-Trail für jede Prüfung
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES
from models.schemas import to_str_id
from services.audit import write_audit_log
from services.ai_screening import run_ai_screening

router = APIRouter(prefix="/api", tags=["ai_screening"])


@router.post("/applications/{app_id}/ai-screen")
async def start_ai_screening(
    app_id: str,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Startet KI-Vorprüfung für eine Bewerbung.
    Nur für Staff/Admin verfügbar.
    Ergebnis wird in 'ai_screenings' Collection gespeichert.
    """
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    app_dict = to_str_id(dict(app))

    # Bewerber-Daten laden
    applicant = {}
    if app_dict.get("applicant_id"):
        try:
            u = await db.users.find_one(
                {"_id": ObjectId(app_dict["applicant_id"])},
                {"full_name": 1, "email": 1, "country": 1, "phone": 1},
            )
            if u:
                applicant = to_str_id(u)
        except Exception:
            pass

    # Dokumente laden
    docs_raw = await db.documents.find({"application_id": app_id}).to_list(50)
    docs = [to_str_id(dict(d)) for d in docs_raw]
    for d in docs:
        d.pop("storage_key", None)

    # Kommunikationsverlauf laden
    messages_raw = await db.messages.find({"application_id": app_id}).sort("created_at", 1).to_list(20)
    messages = [to_str_id(dict(m)) for m in messages_raw]

    # KI-Prüfung durchführen
    result = await run_ai_screening(app_dict, applicant, docs, messages)

    # In DB speichern
    result_to_save = {
        **result,
        "triggered_by": user["id"],
        "created_at": datetime.now(timezone.utc),
    }
    await db.ai_screenings.insert_one(result_to_save)

    # Audit-Log
    await write_audit_log(
        "ai_screening_run",
        user["id"],
        "application",
        app_id,
        {
            "screening_id": result["screening_id"],
            "is_complete": result["is_complete"],
            "suggested_stage": result["suggested_stage"],
            "anabin_category": result["anabin_category"],
        },
    )

    # Serializierbar machen
    result.pop("_id", None)
    return result


@router.post("/applications/{app_id}/ai-screen-async")
async def start_ai_screening_async(
    app_id: str,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Startet KI-Vorpruefung asynchron ueber die Job-Queue.
    Gibt sofort eine Job-Referenz zurueck. Ergebnis wird im Hintergrund verarbeitet.
    """
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    from services.job_queue import enqueue

    job_result = await enqueue(
        job_type="ai_screening",
        payload={
            "application_id": app_id,
            "triggered_by": user["id"],
        },
        dedupe_key=f"screening_{app_id}",
        related_entity_type="application",
        related_entity_id=app_id,
        actor_id=user["id"],
        priority="high",
    )

    return {
        "mode": "async",
        "job_id": job_result["job_id"],
        "job_status": job_result["status"],
        "message": "KI-Screening wurde in die Queue gestellt. Ergebnis wird im Hintergrund verarbeitet.",
    }


@router.get("/applications/{app_id}/ai-screenings")
async def list_ai_screenings(
    app_id: str,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Listet alle KI-Prüfungen für eine Bewerbung (neueste zuerst).
    Nur Staff/Admin.
    """
    db = get_db()
    screenings_raw = await db.ai_screenings.find(
        {"application_id": app_id}
    ).sort("created_at", -1).to_list(20)

    result = []
    for s in screenings_raw:
        s_dict = to_str_id(dict(s))
        # Datum serialisieren
        if isinstance(s_dict.get("created_at"), datetime):
            s_dict["created_at"] = s_dict["created_at"].isoformat()
        result.append(s_dict)
    return result


@router.get("/ai/model-registry")
async def get_ai_model_registry(
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Returns the current AI model registry for audit/documentation (staff only)."""
    from services.nscale_provider import get_model_registry, is_enabled
    return {
        "provider": "nscale",
        "enabled": is_enabled(),
        "models": get_model_registry(),
    }


@router.post("/applications/{app_id}/accept-ai-suggestion")
async def accept_ai_suggestion(
    app_id: str,
    body: dict,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Übernimmt den KI-Vorschlag: Ändert den Status der Bewerbung
    und schreibt einen Audit-Trail-Eintrag.
    """
    db = get_db()
    suggested_stage = body.get("suggested_stage")
    if not suggested_stage:
        raise HTTPException(status_code=400, detail="suggested_stage erforderlich")

    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    old_stage = app.get("current_stage", "")
    if old_stage == suggested_stage:
        return {"status": "unchanged", "message": "Status stimmt bereits überein"}

    await db.applications.update_one(
        {"_id": ObjectId(app_id)},
        {"$set": {"current_stage": suggested_stage, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    await write_audit_log(
        "stage_changed",
        user["id"],
        "application",
        app_id,
        {
            "old_value": old_stage,
            "new_value": suggested_stage,
            "source": "ai_suggestion_accepted",
            "actor_name": user.get("full_name", user.get("email", "")),
        },
    )

    return {"status": "accepted", "old_stage": old_stage, "new_stage": suggested_stage}


@router.get("/applications/{app_id}/screening-delta")
async def get_screening_delta(
    app_id: str,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Gibt das letzte Delta-Screening-Ergebnis zurueck.
    Vergleicht die zwei neuesten Screenings einer Bewerbung.
    """
    db = get_db()
    screenings_raw = await db.ai_screenings.find(
        {"application_id": app_id}
    ).sort("created_at", -1).to_list(2)

    if len(screenings_raw) == 0:
        return {"has_screening": False, "delta": None, "latest": None, "previous": None}

    latest = to_str_id(dict(screenings_raw[0]))
    if isinstance(latest.get("created_at"), datetime):
        latest["created_at"] = latest["created_at"].isoformat()

    # Wenn Delta bereits im Screening gespeichert ist, nutze es
    if latest.get("delta"):
        return {
            "has_screening": True,
            "delta": latest["delta"],
            "latest": latest,
            "previous": to_str_id(dict(screenings_raw[1])) if len(screenings_raw) > 1 else None,
            "is_delta_screening": latest.get("is_delta_screening", False),
        }

    # Ansonsten Delta on-the-fly berechnen
    previous = None
    if len(screenings_raw) > 1:
        previous = to_str_id(dict(screenings_raw[1]))
        if isinstance(previous.get("created_at"), datetime):
            previous["created_at"] = previous["created_at"].isoformat()

    from services.delta_screening import compute_delta
    delta = compute_delta(previous, latest)

    return {
        "has_screening": True,
        "delta": delta,
        "latest": latest,
        "previous": previous,
        "is_delta_screening": latest.get("is_delta_screening", False),
    }


@router.post("/applications/{app_id}/manual-rescreen")
async def manual_rescreen(
    app_id: str,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Manuelles Re-Screening mit Delta-Vergleich (Staff-initiated).
    """
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    app_dict = to_str_id(dict(app))

    # Bewerber laden
    applicant = {}
    if app_dict.get("applicant_id"):
        try:
            u = await db.users.find_one(
                {"_id": ObjectId(app_dict["applicant_id"])},
                {"full_name": 1, "email": 1, "country": 1, "phone": 1},
            )
            if u:
                applicant = to_str_id(u)
        except Exception:
            pass

    docs_raw = await db.documents.find({"application_id": app_id}).to_list(50)
    docs = [to_str_id(dict(d)) for d in docs_raw]
    for d in docs:
        d.pop("storage_key", None)

    messages_raw = await db.messages.find({"application_id": app_id}).sort("created_at", 1).to_list(20)
    messages = [to_str_id(dict(m)) for m in messages_raw]

    # Vorheriges Screening
    previous_screening = await db.ai_screenings.find_one(
        {"application_id": app_id},
        sort=[("created_at", -1)],
    )
    previous_dict = to_str_id(dict(previous_screening)) if previous_screening else None

    # Neues Screening
    result = await run_ai_screening(app_dict, applicant, docs, messages)

    # Delta
    from services.delta_screening import compute_delta
    delta = compute_delta(previous_dict, result)

    result_to_save = {
        **result,
        "triggered_by": user["id"],
        "trigger_reason": "Manuelles Re-Screening durch Staff",
        "is_delta_screening": True,
        "delta": delta,
        "created_at": datetime.now(timezone.utc),
    }
    await db.ai_screenings.insert_one(result_to_save)

    await write_audit_log(
        "manual_rescreening",
        user["id"],
        "application",
        app_id,
        {
            "screening_id": result["screening_id"],
            "changes_count": delta.get("changes_count", 0),
            "risk_change": delta.get("risk_change", ""),
        },
    )

    result.pop("_id", None)
    return {**result, "delta": delta}



# ═══════════════════════════════════════════════════════════════════════════
# BATCH-SCREENING
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/ai-screening/batch")
async def start_batch_screening(
    body: dict,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Startet KI-Batch-Screening fuer mehrere Bewerbungen gleichzeitig.
    Jede Bewerbung wird als separater Job in die Queue gestellt.
    Max. 50 Bewerbungen pro Batch.
    """
    import uuid
    db = get_db()
    app_ids = body.get("application_ids", [])
    if not app_ids:
        raise HTTPException(status_code=400, detail="application_ids erforderlich (mindestens 1)")
    if len(app_ids) > 50:
        raise HTTPException(status_code=400, detail="Maximal 50 Bewerbungen pro Batch erlaubt")

    batch_id = str(uuid.uuid4())[:12]
    enqueued = 0
    skipped = []
    from services.job_queue import enqueue

    for app_id in app_ids:
        try:
            app = await db.applications.find_one({"_id": ObjectId(app_id)})
            if not app:
                skipped.append({"id": app_id, "reason": "nicht gefunden"})
                continue
            if app.get("current_stage") in ("enrolled", "declined"):
                skipped.append({"id": app_id, "reason": f"Status: {app.get('current_stage')}"})
                continue

            await enqueue(
                job_type="ai_screening",
                payload={
                    "application_id": app_id,
                    "triggered_by": user["id"],
                    "batch_id": batch_id,
                },
                dedupe_key=f"batch_{batch_id}_{app_id}",
                related_entity_type="application",
                related_entity_id=app_id,
                actor_id=user["id"],
                priority="normal",
            )
            enqueued += 1
        except Exception:
            skipped.append({"id": app_id, "reason": "Fehler beim Einreihen"})

    # Batch-Eintrag speichern
    batch_doc = {
        "batch_id": batch_id,
        "total": len(app_ids),
        "enqueued": enqueued,
        "skipped": skipped,
        "triggered_by": user["id"],
        "created_at": datetime.now(timezone.utc),
        "status": "running" if enqueued > 0 else "empty",
    }
    await db.batch_screenings.insert_one(batch_doc)

    await write_audit_log(
        "batch_screening_started", user["id"], "batch", batch_id,
        {"total": len(app_ids), "enqueued": enqueued, "skipped_count": len(skipped)},
    )

    return {
        "batch_id": batch_id,
        "total": len(app_ids),
        "enqueued": enqueued,
        "skipped": skipped,
        "status": "running" if enqueued > 0 else "empty",
    }


@router.get("/ai-screening/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Status eines laufenden Batch-Screenings abfragen."""
    db = get_db()
    batch = await db.batch_screenings.find_one({"batch_id": batch_id}, {"_id": 0})
    if not batch:
        raise HTTPException(status_code=404, detail="Batch nicht gefunden")

    # Zaehle abgeschlossene Jobs dieses Batches
    completed = await db.background_jobs.count_documents({
        "payload.batch_id": batch_id,
        "status": "succeeded",
    })
    failed = await db.background_jobs.count_documents({
        "payload.batch_id": batch_id,
        "status": {"$in": ["failed", "dead_letter"]},
    })
    running = await db.background_jobs.count_documents({
        "payload.batch_id": batch_id,
        "status": {"$in": ["queued", "running", "retry_scheduled"]},
    })

    total_enqueued = batch.get("enqueued", 0)
    is_done = running == 0 and (completed + failed) >= total_enqueued

    if is_done and batch.get("status") == "running":
        await db.batch_screenings.update_one(
            {"batch_id": batch_id},
            {"$set": {"status": "completed", "completed_at": datetime.now(timezone.utc)}},
        )

    if isinstance(batch.get("created_at"), datetime):
        batch["created_at"] = batch["created_at"].isoformat()
    if isinstance(batch.get("completed_at"), datetime):
        batch["completed_at"] = batch["completed_at"].isoformat()

    return {
        **batch,
        "progress": {
            "completed": completed,
            "failed": failed,
            "running": running,
            "total": total_enqueued,
            "is_done": is_done,
            "percent": round((completed + failed) / max(total_enqueued, 1) * 100),
        },
    }


@router.get("/ai-screening/batches")
async def list_batches(
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Listet alle Batch-Screenings (neueste zuerst)."""
    db = get_db()
    batches = await db.batch_screenings.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).to_list(20)
    for b in batches:
        if isinstance(b.get("created_at"), datetime):
            b["created_at"] = b["created_at"].isoformat()
        if isinstance(b.get("completed_at"), datetime):
            b["completed_at"] = b["completed_at"].isoformat()
    return batches
