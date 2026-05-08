"""
Appointments router – CRUD for appointments/bookings.
- Authenticated users: full CRUD
- Public: booking request (no auth needed)
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
# Rate-Limiter wird zentral aus rate_limiter.py importiert

router = APIRouter(prefix="/api/appointments", tags=["appointments"])
from rate_limiter import limiter


def serialize(doc):
    if not doc:
        return None
    out = {}
    for k, v in doc.items():
        if k == "_id":
            out["id"] = str(v)
        elif isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    return out


# ─── Authenticated endpoints ─────────────────────────────────────────────────

@router.get("")
async def list_appointments(user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    if user["role"] == "applicant":
        query["$or"] = [{"user_id": user["id"]}, {"user_email": user.get("email")}]
    elif user["role"] == "teacher":
        query["$or"] = [{"teacher_id": user["id"]}, {"type": "course"}]
    cursor = db.appointments.find(query).sort("date", 1)
    results = []
    async for doc in cursor:
        results.append(serialize(doc))
    return results


@router.post("")
async def create_appointment(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    body = await request.json()

    apt = {
        "title": body.get("title", "Termin"),
        "type": body.get("type", "consultation"),
        "date": body.get("date"),
        "time": body.get("time", "10:00"),
        "duration_min": body.get("duration_min", 30),
        "description": body.get("description", ""),
        "status": "confirmed",
        "user_id": user["id"],
        "user_name": user.get("full_name", user.get("email", "")),
        "user_email": user.get("email", ""),
        "location": body.get("location", "Online (Zoom)"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": user["id"],
    }

    if body.get("applicant_id"):
        apt["applicant_id"] = body["applicant_id"]

    result = await db.appointments.insert_one(apt)
    apt["id"] = str(result.inserted_id)
    apt.pop("_id", None)
    return apt


@router.put("/{apt_id}")
async def update_appointment(apt_id: str, request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    body = await request.json()

    update_fields = {}
    for field in ["title", "date", "time", "duration_min", "description", "status", "location", "type"]:
        if field in body:
            update_fields[field] = body[field]
    update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.appointments.find_one_and_update(
        {"_id": ObjectId(apt_id)},
        {"$set": update_fields},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return serialize(result)


@router.delete("/{apt_id}")
async def cancel_appointment(apt_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.appointments.find_one_and_update(
        {"_id": ObjectId(apt_id)},
        {"$set": {"status": "cancelled", "updated_at": datetime.now(timezone.utc).isoformat()}},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return serialize(result)


@router.get("/available-slots")
async def get_available_slots(
    date: str = Query(default=None),
    user: dict = Depends(get_current_user)
):
    if not date:
        date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    db = get_db()
    booked = []
    async for doc in db.appointments.find({"date": date, "status": {"$ne": "cancelled"}}):
        booked.append(doc.get("time"))
    all_slots = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in [0, 30]]
    available = [s for s in all_slots if s not in booked]
    return {"date": date, "slots": available, "booked_count": len(booked)}


# ─── Public endpoint (no auth) ───────────────────────────────────────────────

@router.post("/public-booking")
@limiter.limit("5/minute")
async def public_booking(request: Request):
    """Pre-login appointment booking request."""
    db = get_db()
    body = await request.json()

    required = ["name", "email", "date", "time", "type"]
    for field in required:
        if not body.get(field):
            raise HTTPException(status_code=400, detail=f"Field '{field}' is required")

    apt = {
        "title": f"Anfrage: {body.get('type', 'Beratung')}",
        "type": body.get("type", "consultation"),
        "date": body["date"],
        "time": body["time"],
        "duration_min": 30,
        "description": body.get("message", ""),
        "status": "pending",
        "user_id": None,
        "user_name": body["name"],
        "user_email": body["email"],
        "phone": body.get("phone", ""),
        "location": "Online (Zoom)",
        "source": "public_booking",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    result = await db.appointments.insert_one(apt)
    apt["id"] = str(result.inserted_id)
    apt.pop("_id", None)
    return {"success": True, "appointment": apt}


@router.get("/public-slots")
async def public_available_slots(date: str = Query(default=None)):
    """Public endpoint – available slots without auth."""
    if not date:
        date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    db = get_db()
    booked = []
    async for doc in db.appointments.find({"date": date, "status": {"$ne": "cancelled"}}):
        booked.append(doc.get("time"))
    all_slots = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in [0, 30]]
    available = [s for s in all_slots if s not in booked]
    return {"date": date, "slots": available}
