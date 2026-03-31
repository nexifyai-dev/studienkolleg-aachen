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
from services.workflow_status import ai_suggestible_statuses, can_transition

router = APIRouter(prefix="/api", tags=["ai_screening"])


async def _persist_document_analysis(db, app_id: str, screening_id: str, document_analysis: dict):
    """Persist extraction/evidence per document for traceable precheck outputs."""
    for item in (document_analysis or {}).get("documents", []):
        doc_id = item.get("document_id")
        if not doc_id:
            continue
        try:
            await db.documents.update_one(
                {"_id": ObjectId(doc_id), "application_id": app_id},
                {
                    "$set": {
                        "analysis.extraction": item.get("core_fields", {}),
                        "analysis.suitability": item.get("suitability", {}),
                        "analysis.category": item.get("category"),
                        "analysis.evidence": item.get("evidence", []),
                        "analysis.last_screening_id": screening_id,
                        "analysis.updated_at": datetime.now(timezone.utc),
                    }
                },
            )
        except Exception:
            # Non-blocking: screening output keeps evidence payload even if persistence fails.
            continue


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

    # Dokumentanalyse dokumentbezogen speichern (nicht entscheidend für den Ablauf)
    await _persist_document_analysis(db, app_id, result.get("screening_id"), result.get("document_analysis"))

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
    from services.deepseek_provider import get_model_registry, is_enabled
    return {
        "provider": "deepseek",
        "enabled": is_enabled(),
        "models": get_model_registry(),
    }


@router.post("/applications/{app_id}/accept-ai-suggestion")
async def accept_ai_suggestion(
    app_id: str,
    body: dict | None = None,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """
    Übernimmt den KI-Vorschlag: Ändert den Status der Bewerbung
    und schreibt einen Audit-Trail-Eintrag.
    """
    db = get_db()
    body = body or {}
    requested_stage = body.get("suggested_stage")

    allowed_suggested_stages = ai_suggestible_statuses()

    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    latest_screening_raw = await db.ai_screenings.find_one(
        {"application_id": app_id},
        sort=[("created_at", -1)],
    )
    if not latest_screening_raw:
        raise HTTPException(status_code=409, detail="Keine KI-Prüfung vorhanden")

    latest_screening = to_str_id(dict(latest_screening_raw))
    latest_suggested_stage = latest_screening.get("suggested_stage")
    if not latest_suggested_stage:
        raise HTTPException(status_code=409, detail="Neueste KI-Prüfung enthält keinen Stage-Vorschlag")

    if latest_suggested_stage not in allowed_suggested_stages:
        raise HTTPException(status_code=400, detail="Ungültiger KI-Vorschlag im neuesten Screening")

    accepted_from_latest_screening = True
    if requested_stage and requested_stage != latest_suggested_stage:
        accepted_from_latest_screening = False
        raise HTTPException(
            status_code=409,
            detail="Stage stimmt nicht mit der neuesten KI-Empfehlung überein",
        )

    suggested_stage = latest_suggested_stage

    old_stage = app.get("current_stage", "")
    if not can_transition(old_stage, suggested_stage):
        raise HTTPException(status_code=409, detail="Ungültiger Stage-Wechsel laut Workflow-Regeln")
    if old_stage == suggested_stage:
        return {
            "status": "unchanged",
            "message": "Status stimmt bereits überein",
            "new_stage": suggested_stage,
            "screening_id": latest_screening.get("id"),
            "screening_created_at": latest_screening.get("created_at"),
            "accepted_from_latest_screening": accepted_from_latest_screening,
        }

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
            "screening_id": latest_screening.get("id"),
            "screening_created_at": latest_screening.get("created_at"),
            "accepted_from_latest_screening": accepted_from_latest_screening,
        },
    )

    return {
        "status": "accepted",
        "old_stage": old_stage,
        "new_stage": suggested_stage,
        "screening_id": latest_screening.get("id"),
        "screening_created_at": latest_screening.get("created_at"),
        "accepted_from_latest_screening": accepted_from_latest_screening,
    }
