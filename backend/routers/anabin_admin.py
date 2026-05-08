"""
Anabin Admin Router – CRUD, Review Queue, Mapping, Knowledge Gaps.
Prefix: /api/anabin
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from database import get_db
from deps import require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/anabin", tags=["anabin-admin"])

STAFF_ROLES = ("superadmin", "admin", "staff")

VALID_CATEGORIES = ("H+", "H", "H+-", "D", "pruefen", "unbekannt")
VALID_STATUSES = ("verified", "in_review", "outdated", "locked", "draft")
VALID_CONFIDENCES = ("high", "medium", "low", "unknown")
VALID_QUEUE_STATUSES = ("open", "in_progress", "resolved", "escalated")

def _str_id(doc: dict) -> dict:
    """Convert _id ObjectId to string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD / STATS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/stats")
async def get_stats(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Dashboard-Statistiken fuer Wissensbasis."""
    db = get_db()
    total = await db.anabin_knowledge.count_documents({})
    verified = await db.anabin_knowledge.count_documents({"status": "verified"})
    in_review = await db.anabin_knowledge.count_documents({"status": "in_review"})
    special_cases = await db.anabin_knowledge.count_documents({"is_special_case": True})
    unknown = await db.anabin_knowledge.count_documents({"category": {"$in": ["pruefen", "unbekannt"]}})
    queue_open = await db.anabin_review_queue.count_documents({"status": {"$in": ["open", "in_progress"]}})

    # Zuletzt geaendert
    recent_raw = await db.anabin_knowledge.find(
        {}, {"_id": 1, "country": 1, "degree_type": 1, "category": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(5)
    recent = [_str_id(dict(r)) for r in recent_raw]

    # Kategorieverteilung
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    cats_raw = await db.anabin_knowledge.aggregate(pipeline).to_list(20)
    categories = {c["_id"]: c["count"] for c in cats_raw if c["_id"]}

    return {
        "total": total,
        "verified": verified,
        "in_review": in_review,
        "special_cases": special_cases,
        "unknown": unknown,
        "queue_open": queue_open,
        "categories": categories,
        "recent_changes": recent,
    }


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE ENTRIES – LIST / SEARCH / FILTER
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/entries")
async def list_entries(
    q: Optional[str] = Query(None, description="Suchtext"),
    country: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    confidence: Optional[str] = Query(None),
    special_case: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("country"),
    sort_dir: Optional[int] = Query(1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Wissensbasis-Eintraege mit Such-/Filter-/Sortierlogik."""
    db = get_db()
    query = {}

    if q:
        query["$or"] = [
            {"country": {"$regex": q, "$options": "i"}},
            {"degree_type": {"$regex": q, "$options": "i"}},
            {"degree_variants": {"$regex": q, "$options": "i"}},
            {"notes": {"$regex": q, "$options": "i"}},
        ]
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    if category and category in VALID_CATEGORIES:
        query["category"] = category
    if status and status in VALID_STATUSES:
        query["status"] = status
    if confidence and confidence in VALID_CONFIDENCES:
        query["confidence"] = confidence
    if special_case is not None:
        query["is_special_case"] = special_case

    sort_field = sort_by if sort_by in ("country", "category", "status", "confidence", "updated_at", "usage_count") else "country"
    total = await db.anabin_knowledge.count_documents(query)
    entries_raw = await db.anabin_knowledge.find(query).sort(sort_field, sort_dir).skip(skip).limit(limit).to_list(limit)
    entries = [_str_id(dict(e)) for e in entries_raw]

    return {"entries": entries, "total": total, "skip": skip, "limit": limit}


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE ENTRY – CRUD
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/entries/{entry_id}")
async def get_entry(entry_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Einzelnen Wissenseintrag abrufen."""
    db = get_db()
    try:
        entry = await db.anabin_knowledge.find_one({"_id": ObjectId(entry_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not entry:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    return _str_id(dict(entry))


@router.post("/entries")
async def create_entry(body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Neuen Wissenseintrag erstellen."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "country": body.get("country", "").strip(),
        "country_lower": body.get("country", "").strip().lower(),
        "degree_type": body.get("degree_type", "Allgemein").strip(),
        "degree_variants": body.get("degree_variants", []),
        "category": body.get("category", "pruefen"),
        "confidence": body.get("confidence", "unknown"),
        "status": body.get("status", "draft"),
        "is_special_case": body.get("is_special_case", False),
        "staff_note": body.get("staff_note", ""),
        "source": body.get("source", "staff_manual"),
        "source_url": body.get("source_url", ""),
        "operational_classification": body.get("operational_classification", ""),
        "standard_response": body.get("standard_response", ""),
        "requires_staff_decision": body.get("requires_staff_decision", False),
        "notes": body.get("notes", ""),
        "last_verified": now,
        "last_verified_by": user.get("email", user["id"]),
        "version": 1,
        "change_history": [{
            "action": "created",
            "by": user.get("email", user["id"]),
            "at": now,
            "fields": ["all"],
        }],
        "usage_count": 0,
        "created_at": now,
        "updated_at": now,
    }

    if not entry["country"]:
        raise HTTPException(status_code=400, detail="Land ist erforderlich")

    result = await db.anabin_knowledge.insert_one(entry)
    entry["id"] = str(result.inserted_id)
    del entry["_id"]
    return entry


@router.put("/entries/{entry_id}")
async def update_entry(entry_id: str, body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Wissenseintrag aktualisieren (versioniert)."""
    db = get_db()
    try:
        existing = await db.anabin_knowledge.find_one({"_id": ObjectId(entry_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not existing:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    now = datetime.now(timezone.utc).isoformat()
    changed_fields = []
    update = {}
    updatable_fields = [
        "country", "degree_type", "degree_variants", "category", "confidence",
        "status", "is_special_case", "staff_note", "source", "source_url",
        "operational_classification", "standard_response", "requires_staff_decision", "notes",
    ]
    for field in updatable_fields:
        if field in body and body[field] != existing.get(field):
            update[field] = body[field]
            changed_fields.append(field)

    if "country" in update:
        update["country_lower"] = update["country"].strip().lower()

    if not update:
        return _str_id(dict(existing))

    update["updated_at"] = now
    update["version"] = existing.get("version", 1) + 1

    history_entry = {
        "action": "updated",
        "by": user.get("email", user["id"]),
        "at": now,
        "fields": changed_fields,
        "previous_values": {f: existing.get(f) for f in changed_fields},
    }

    await db.anabin_knowledge.update_one(
        {"_id": ObjectId(entry_id)},
        {"$set": update, "$push": {"change_history": history_entry}},
    )

    updated = await db.anabin_knowledge.find_one({"_id": ObjectId(entry_id)})
    return _str_id(dict(updated))


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: str, user: dict = Depends(require_roles("superadmin", "admin"))):
    """Wissenseintrag loeschen (nur Admin)."""
    db = get_db()
    try:
        result = await db.anabin_knowledge.delete_one({"_id": ObjectId(entry_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")
    return {"deleted": True}


# ═══════════════════════════════════════════════════════════════════════════
# REVIEW QUEUE
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/review-queue")
async def get_review_queue(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Review-Queue: Offene Wissenslücken und Pruefungsfaelle."""
    db = get_db()
    query = {}
    if status and status in VALID_QUEUE_STATUSES:
        query["status"] = status
    elif not status:
        query["status"] = {"$in": ["open", "in_progress"]}
    if priority:
        query["priority"] = priority

    total = await db.anabin_review_queue.count_documents(query)
    items_raw = await db.anabin_review_queue.find(query).sort([
        ("priority_order", 1), ("created_at", -1)
    ]).skip(skip).limit(limit).to_list(limit)
    items = [_str_id(dict(i)) for i in items_raw]
    return {"items": items, "total": total}


@router.post("/review-queue")
async def create_review_item(body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Manuell einen Fall zur Wissenspruefung melden."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    priority = body.get("priority", "medium")
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(priority, 2)

    item = {
        "queue_id": str(uuid.uuid4())[:8],
        "application_id": body.get("application_id"),
        "applicant_name": body.get("applicant_name", ""),
        "country": body.get("country", ""),
        "degree_type": body.get("degree_type", ""),
        "reason": body.get("reason", "manual_review"),
        "reason_label": body.get("reason_label", "Manuelle Pruefung angefordert"),
        "suggested_matches": body.get("suggested_matches", []),
        "last_screening_output": body.get("last_screening_output", {}),
        "owner": body.get("owner"),
        "status": "open",
        "priority": priority,
        "priority_order": priority_order,
        "next_action": body.get("next_action", "Mapping pruefen und operative Einstufung vornehmen"),
        "resolution": None,
        "resolved_at": None,
        "resolved_by": None,
        "created_at": now,
        "created_by": user.get("email", user["id"]),
    }
    result = await db.anabin_review_queue.insert_one(item)
    item["id"] = str(result.inserted_id)
    del item["_id"]
    return item


@router.put("/review-queue/{item_id}")
async def update_review_item(item_id: str, body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Review-Eintrag aktualisieren (Status, Owner, Resolution)."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    update = {}

    if "status" in body and body["status"] in VALID_QUEUE_STATUSES:
        update["status"] = body["status"]
        if body["status"] == "resolved":
            update["resolved_at"] = now
            update["resolved_by"] = user.get("email", user["id"])
    if "owner" in body:
        update["owner"] = body["owner"]
    if "priority" in body:
        update["priority"] = body["priority"]
        update["priority_order"] = {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(body["priority"], 2)
    if "resolution" in body:
        update["resolution"] = body["resolution"]
    if "next_action" in body:
        update["next_action"] = body["next_action"]

    if not update:
        raise HTTPException(status_code=400, detail="Keine aenderbaren Felder")

    try:
        result = await db.anabin_review_queue.update_one({"_id": ObjectId(item_id)}, {"$set": update})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Queue-Eintrag nicht gefunden")

    updated = await db.anabin_review_queue.find_one({"_id": ObjectId(item_id)})
    return _str_id(dict(updated))


@router.post("/review-queue/{item_id}/resolve")
async def resolve_with_feedback(item_id: str, body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """
    Loest einen Queue-Eintrag und schreibt optional das Ergebnis
    in die Wissensbasis zurueck (Feedback-Loop).
    """
    from services.anabin_knowledge import resolve_queue_with_feedback

    resolution = {
        "resolution_note": body.get("resolution_note", "Mapping geprueft und akzeptiert"),
    }

    # Wissensbasis-Update mitgeben (optional)
    if body.get("update_knowledge"):
        resolution["update_knowledge"] = body["update_knowledge"]

    result = await resolve_queue_with_feedback(
        queue_item_id=item_id,
        resolution=resolution,
        resolved_by=user.get("email", user["id"]),
    )

    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# ═══════════════════════════════════════════════════════════════════════════
# KNOWLEDGE GAPS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/knowledge-gaps")
async def get_knowledge_gaps(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Wissenslücken: ungemappte, unsichere oder pruefungsbeduerftige Eintraege."""
    db = get_db()

    gaps_raw = await db.anabin_knowledge.find(
        {"$or": [
            {"category": {"$in": ["pruefen", "unbekannt"]}},
            {"confidence": {"$in": ["low", "unknown"]}},
            {"status": "in_review"},
        ]},
    ).sort("usage_count", -1).to_list(100)
    gaps = [_str_id(dict(g)) for g in gaps_raw]

    # Haeufigkeit aus Screenings zaehlen
    for gap in gaps:
        country = gap.get("country", "")
        screening_count = await db.ai_screenings.count_documents(
            {"local_checks.anabin_lookup.label": {"$regex": country, "$options": "i"}}
        ) if country else 0
        gap["screening_frequency"] = screening_count

    return {"gaps": gaps, "total": len(gaps)}


# ═══════════════════════════════════════════════════════════════════════════
# BULK ACTIONS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/bulk-update")
async def bulk_update(body: dict, user: dict = Depends(require_roles("superadmin", "admin"))):
    """Bulk-Update fuer mehrere Eintraege (z.B. Status/Kategorie aendern)."""
    db = get_db()
    ids = body.get("ids", [])
    update_fields = body.get("update", {})

    if not ids or not update_fields:
        raise HTTPException(status_code=400, detail="IDs und Update-Felder erforderlich")

    allowed = {"category", "status", "confidence", "is_special_case"}
    filtered = {k: v for k, v in update_fields.items() if k in allowed}
    if not filtered:
        raise HTTPException(status_code=400, detail="Keine erlaubten Update-Felder")

    now = datetime.now(timezone.utc).isoformat()
    filtered["updated_at"] = now

    oids = []
    for i in ids:
        try:
            oids.append(ObjectId(i))
        except Exception:
            continue

    result = await db.anabin_knowledge.update_many(
        {"_id": {"$in": oids}},
        {
            "$set": filtered,
            "$push": {"change_history": {
                "action": "bulk_updated",
                "by": user.get("email", user["id"]),
                "at": now,
                "fields": list(filtered.keys()),
            }},
        },
    )
    return {"modified": result.modified_count}
