"""
Followup / Wiedervorlage router.
Allows staff to set reminders on applications.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from database import get_db
from deps import require_roles, get_current_user, STAFF_ROLES
from models.schemas import FollowupCreate, FollowupUpdate, to_str_id

router = APIRouter(prefix="/api/followups", tags=["followups"])


def _serialize(doc: dict) -> dict:
    doc = to_str_id(doc)
    for k in ("due_date", "created_at", "updated_at"):
        if hasattr(doc.get(k), "isoformat"):
            doc[k] = doc[k].isoformat()
    return doc


@router.get("")
async def list_followups(user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    followups = await db.followups.find({"status": {"$ne": "dismissed"}}).sort("due_date", 1).to_list(200)
    return [_serialize(f) for f in followups]


@router.get("/due")
async def list_due_followups(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Get followups that are due today or overdue."""
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()[:10]
    followups = await db.followups.find({
        "status": "pending",
        "due_date": {"$lte": now},
    }).sort("due_date", 1).to_list(100)
    return [_serialize(f) for f in followups]


@router.post("")
async def create_followup(data: FollowupCreate, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(data.application_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    # Get applicant name for display
    applicant = await db.users.find_one({"_id": ObjectId(app["applicant_id"])}, {"_id": 0, "full_name": 1, "email": 1})
    applicant_name = (applicant.get("full_name") or applicant.get("email", "")) if applicant else ""

    doc = {
        "application_id": data.application_id,
        "applicant_name": applicant_name,
        "due_date": data.due_date,
        "reason": data.reason,
        "assigned_to": data.assigned_to or user["id"],
        "created_by": user["id"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.followups.insert_one(doc)
    doc.pop("_id", None)
    doc["id"] = str(result.inserted_id)
    for k in ("created_at",):
        if hasattr(doc.get(k), "isoformat"):
            doc[k] = doc[k].isoformat()
    return doc


@router.put("/{followup_id}")
async def update_followup(followup_id: str, data: FollowupUpdate, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    update = {"updated_at": datetime.now(timezone.utc)}
    if data.status:
        update["status"] = data.status
    if data.due_date:
        update["due_date"] = data.due_date
    if data.reason:
        update["reason"] = data.reason
    try:
        await db.followups.update_one({"_id": ObjectId(followup_id)}, {"$set": update})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    return {"message": "Aktualisiert"}


@router.delete("/{followup_id}")
async def dismiss_followup(followup_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    try:
        await db.followups.update_one({"_id": ObjectId(followup_id)}, {"$set": {"status": "dismissed"}})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    return {"message": "Verworfen"}
