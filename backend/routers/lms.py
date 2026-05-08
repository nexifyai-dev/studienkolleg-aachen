"""
LMS Router – Kurs-Management, Enrollment, Zugang und Stipendien.

Endpunkte:
- GET  /api/lms/courses              – Kurs-Katalog (oeffentlich)
- GET  /api/lms/courses/{id}         – Kurs-Detail
- POST /api/lms/enroll               – Kurs-Enrollment (Bewerber)
- GET  /api/lms/my-enrollments       – Meine Enrollments (Bewerber)
- GET  /api/lms/enrollments          – Alle Enrollments (Staff)
- PUT  /api/lms/enrollments/{id}     – Enrollment aktualisieren (Staff)
- POST /api/lms/grant-access         – Stipendien-/Admin-Freigabe (Staff)
- GET  /api/lms/courses/{id}/content – Kurs-Inhalte (nur bei Zugang)

Logik:
- Kurszugang erst nach Zahlung ODER manueller Freigabe (Stipendium)
- On-Demand Videos, Live-Sessions (Zoom), Praesenztermine
"""
import logging
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lms", tags=["lms"])


# ── Models ──────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    code: str
    title: str
    description: str = ""
    category: str = "kurs"
    price: float = 0
    currency: str = "EUR"
    course_type: str = "on_demand"  # on_demand, live_session, praesenz, hybrid
    duration_weeks: int = 0
    max_participants: Optional[int] = None
    prerequisites: list = []
    modules: list = []
    zoom_link: Optional[str] = None
    location: Optional[str] = None
    schedule: Optional[str] = None
    active: bool = True


class EnrollRequest(BaseModel):
    course_id: str
    payment_method: str = "stripe"  # stripe, manual, stipendium


class GrantAccessRequest(BaseModel):
    enrollment_id: str
    reason: str = "admin_freigabe"
    notes: str = ""


# ── Kurskatalog ─────────────────────────────────────────────────────

DEFAULT_COURSES = [
    {
        "id": "course-tkurs", "code": "SK-TKURS", "title": "T-Kurs (Technik)",
        "description": "Studienkolleg Vorbereitungskurs Technik. Schwerpunkte: Mathematik, Physik, Chemie, Informatik.",
        "category": "studienkolleg", "price": 4500, "currency": "EUR",
        "course_type": "praesenz", "duration_weeks": 24, "max_participants": 25,
        "prerequisites": ["B1 Deutsch", "Hochschulreife (bedingt)"],
        "modules": [
            {"title": "Mathematik I", "type": "praesenz", "hours": 60},
            {"title": "Physik", "type": "praesenz", "hours": 40},
            {"title": "Chemie", "type": "praesenz", "hours": 30},
            {"title": "Deutsch (fachbezogen)", "type": "hybrid", "hours": 50},
        ],
        "active": True,
    },
    {
        "id": "course-mkurs", "code": "SK-MKURS", "title": "M-Kurs (Medizin/Bio)",
        "description": "Vorbereitungskurs Medizin und Biologie. Schwerpunkte: Biologie, Chemie, Physik, Mathematik.",
        "category": "studienkolleg", "price": 4500, "currency": "EUR",
        "course_type": "praesenz", "duration_weeks": 24, "max_participants": 25,
        "prerequisites": ["B1 Deutsch", "Hochschulreife (bedingt)"],
        "modules": [
            {"title": "Biologie", "type": "praesenz", "hours": 50},
            {"title": "Chemie", "type": "praesenz", "hours": 50},
            {"title": "Physik", "type": "praesenz", "hours": 30},
            {"title": "Mathematik", "type": "praesenz", "hours": 40},
        ],
        "active": True,
    },
    {
        "id": "course-wkurs", "code": "SK-WKURS", "title": "W-Kurs (Wirtschaft)",
        "description": "Vorbereitungskurs Wirtschaftswissenschaften. Schwerpunkte: Mathematik, VWL/BWL, Deutsch.",
        "category": "studienkolleg", "price": 4500, "currency": "EUR",
        "course_type": "praesenz", "duration_weeks": 24, "max_participants": 30,
        "prerequisites": ["B1 Deutsch", "Hochschulreife (bedingt)"],
        "modules": [
            {"title": "Mathematik", "type": "praesenz", "hours": 60},
            {"title": "VWL/BWL", "type": "praesenz", "hours": 50},
            {"title": "Deutsch (Wirtschaft)", "type": "hybrid", "hours": 50},
        ],
        "active": True,
    },
    {
        "id": "course-dsh", "code": "DSH-PREP", "title": "DSH-Vorbereitung",
        "description": "Intensivkurs zur Vorbereitung auf die Deutsche Sprachpruefung fuer den Hochschulzugang.",
        "category": "sprache", "price": 2800, "currency": "EUR",
        "course_type": "hybrid", "duration_weeks": 12,
        "prerequisites": ["B2 Deutsch"],
        "modules": [
            {"title": "Hoerverstehen", "type": "on_demand", "hours": 20},
            {"title": "Leseverstehen", "type": "on_demand", "hours": 20},
            {"title": "Schriftlicher Ausdruck", "type": "live_session", "hours": 30},
            {"title": "Muendliche Pruefung", "type": "live_session", "hours": 15},
        ],
        "active": True,
    },
    {
        "id": "course-b1b2", "code": "B1-B2", "title": "Deutsch B1-B2",
        "description": "Deutschkurs Niveau B1 bis B2. Online und Praesenz kombiniert.",
        "category": "sprache", "price": 1800, "currency": "EUR",
        "course_type": "hybrid", "duration_weeks": 16,
        "prerequisites": ["A2 Deutsch"],
        "modules": [
            {"title": "Grammatik B1", "type": "on_demand", "hours": 30},
            {"title": "Konversation B1", "type": "live_session", "hours": 20},
            {"title": "Grammatik B2", "type": "on_demand", "hours": 30},
            {"title": "Pruefungstraining", "type": "live_session", "hours": 20},
        ],
        "active": True,
    },
    {
        "id": "course-a1a2", "code": "A1-A2", "title": "Deutsch A1-A2",
        "description": "Deutschkurs fuer Anfaenger. Online-Module mit Live-Tutorien.",
        "category": "sprache", "price": 1200, "currency": "EUR",
        "course_type": "on_demand", "duration_weeks": 12,
        "prerequisites": [],
        "modules": [
            {"title": "Grundlagen A1", "type": "on_demand", "hours": 40},
            {"title": "Aufbau A2", "type": "on_demand", "hours": 40},
            {"title": "Live-Tutorium", "type": "live_session", "hours": 10},
        ],
        "active": True,
    },
]


@router.get("/courses")
async def list_courses():
    """Oeffentlicher Kurskatalog."""
    db = get_db()
    custom = await db.lms_courses.find({"active": True}, {"_id": 0}).to_list(100)
    courses = DEFAULT_COURSES + custom if custom else DEFAULT_COURSES
    return [c for c in courses if c.get("active", True)]


@router.get("/courses/{course_id}")
async def get_course(course_id: str):
    """Kurs-Detail."""
    for c in DEFAULT_COURSES:
        if c["id"] == course_id:
            return c
    db = get_db()
    course = await db.lms_courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")
    return course


@router.post("/courses")
async def create_course(data: CourseCreate, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Neuen Kurs erstellen (Staff)."""
    db = get_db()
    course = {
        "id": f"course-{uuid.uuid4().hex[:8]}",
        **data.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": user["id"],
    }
    await db.lms_courses.insert_one(course)
    course.pop("_id", None)
    return course


# ── Enrollment ──────────────────────────────────────────────────────

@router.post("/enroll")
async def enroll_in_course(data: EnrollRequest, user: dict = Depends(get_current_user)):
    """Bewerber meldet sich fuer einen Kurs an."""
    db = get_db()

    # Kurs pruefen
    course = None
    for c in DEFAULT_COURSES:
        if c["id"] == data.course_id:
            course = c
            break
    if not course:
        course = await db.lms_courses.find_one({"id": data.course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")

    # Doppel-Enrollment verhindern
    existing = await db.lms_enrollments.find_one({
        "user_id": user["id"], "course_id": data.course_id, "status": {"$nin": ["cancelled", "expired"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Bereits fuer diesen Kurs angemeldet")

    enrollment = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "user_email": user.get("email", ""),
        "user_name": user.get("full_name", ""),
        "course_id": data.course_id,
        "course_title": course.get("title", ""),
        "course_price": course.get("price", 0),
        "payment_method": data.payment_method,
        "payment_status": "pending" if data.payment_method != "stipendium" else "waived",
        "access_granted": data.payment_method == "stipendium",
        "status": "pending_payment" if data.payment_method != "stipendium" else "active",
        "enrolled_at": datetime.now(timezone.utc).isoformat(),
        "progress_percent": 0,
        "completed_modules": [],
    }
    await db.lms_enrollments.insert_one(enrollment)
    enrollment.pop("_id", None)

    logger.info(f"[LMS] Enrollment: {user['id']} → {data.course_id} ({data.payment_method})")
    return enrollment


@router.get("/my-enrollments")
async def my_enrollments(user: dict = Depends(get_current_user)):
    """Meine Kurs-Enrollments."""
    db = get_db()
    enrollments = await db.lms_enrollments.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("enrolled_at", -1).to_list(50)
    return enrollments


@router.get("/enrollments")
async def list_enrollments(user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Alle Enrollments (Staff)."""
    db = get_db()
    enrollments = await db.lms_enrollments.find({}, {"_id": 0}).sort("enrolled_at", -1).to_list(500)
    return enrollments


@router.put("/enrollments/{enrollment_id}")
async def update_enrollment(enrollment_id: str, body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Enrollment aktualisieren (Staff): Status, Payment, Progress."""
    db = get_db()
    allowed = {"status", "payment_status", "access_granted", "progress_percent", "notes"}
    update = {k: v for k, v in body.items() if k in allowed}
    if not update:
        raise HTTPException(status_code=400, detail="Keine gueltigen Felder")

    # Zahlungseingang → Zugang freischalten
    if update.get("payment_status") == "paid" and body.get("access_granted") is not False:
        update["access_granted"] = True
        update["status"] = "active"

    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    update["updated_by"] = user["id"]

    result = await db.lms_enrollments.update_one({"id": enrollment_id}, {"$set": update})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Enrollment nicht gefunden")
    return {"ok": True, "updated": list(update.keys())}


@router.post("/grant-access")
async def grant_access(data: GrantAccessRequest, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Stipendien-/Admin-Freigabe: Kurszugang ohne Zahlung gewaehren."""
    db = get_db()
    enrollment = await db.lms_enrollments.find_one({"id": data.enrollment_id})
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment nicht gefunden")

    await db.lms_enrollments.update_one(
        {"id": data.enrollment_id},
        {"$set": {
            "access_granted": True,
            "status": "active",
            "payment_status": "waived",
            "grant_reason": data.reason,
            "grant_notes": data.notes,
            "granted_by": user["id"],
            "granted_at": datetime.now(timezone.utc).isoformat(),
        }},
    )

    # Bewerber benachrichtigen
    await db.notifications.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": enrollment["user_id"],
        "type": "course_access_granted",
        "title": "Kurszugang freigeschaltet",
        "message": f"Ihr Zugang zu '{enrollment.get('course_title', 'Kurs')}' wurde freigeschaltet ({data.reason}).",
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    logger.info(f"[LMS] Access granted: enrollment={data.enrollment_id} by={user['id']} reason={data.reason}")
    return {"ok": True, "enrollment_id": data.enrollment_id, "access_granted": True}


# ── Kurs-Inhalte (zugangsgeschuetzt) ────────────────────────────────

@router.get("/courses/{course_id}/content")
async def get_course_content(course_id: str, user: dict = Depends(get_current_user)):
    """Kurs-Inhalte – nur bei aktivem Zugang."""
    db = get_db()

    # Zugang pruefen
    enrollment = await db.lms_enrollments.find_one({
        "user_id": user["id"], "course_id": course_id,
        "access_granted": True, "status": {"$in": ["active", "completed"]},
    })
    is_staff = user.get("role") in ("superadmin", "admin", "staff", "teacher")
    if not enrollment and not is_staff:
        raise HTTPException(status_code=403, detail="Kein Zugang. Bitte zuerst anmelden und Zahlung abschliessen.")

    # Kurs-Daten laden
    course = None
    for c in DEFAULT_COURSES:
        if c["id"] == course_id:
            course = c
            break
    if not course:
        course = await db.lms_courses.find_one({"id": course_id}, {"_id": 0})
    if not course:
        raise HTTPException(status_code=404, detail="Kurs nicht gefunden")

    return {
        "course": course,
        "enrollment": {
            "progress_percent": enrollment.get("progress_percent", 0) if enrollment else 0,
            "completed_modules": enrollment.get("completed_modules", []) if enrollment else [],
        } if enrollment else None,
        "access": True,
    }
