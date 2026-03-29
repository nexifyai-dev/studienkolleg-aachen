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
