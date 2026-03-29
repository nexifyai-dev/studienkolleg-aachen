"""
Teacher router – assignment-based, purpose-limited access to student data.

Access model:
- Teachers can ONLY see students explicitly assigned to them
- Teachers see ONLY data needed for teaching/supervision (consent-gated)
- Teachers CANNOT see: financial data, AI screening reports, internal notes, passport details
- All teacher access is audit-logged

Role: "teacher"
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES, TEACHING_ROLES
from database import get_db
from services.audit import write_audit_log
from bson import ObjectId

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

# Fields teachers are allowed to see (purpose-limited)
TEACHER_VISIBLE_FIELDS = {
    "full_name", "first_name", "last_name", "email", "phone",
    "course_type", "language_level", "degree_country",
    "current_stage", "created_at", "last_activity_at",
}

# Fields teachers must NEVER see
TEACHER_EXCLUDED_FIELDS = {
    "password_hash", "financial_data", "payment_status",
    "internal_notes", "ai_report", "ai_screening",
    "passport_data", "referral_code", "duplicate_flag",
}


@router.get("/my-students")
async def get_my_students(
    user: dict = Depends(require_roles("teacher")),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
):
    """Get students assigned to the current teacher. Consent-checked."""
    db = get_db()
    teacher_id = user["id"]

    # Get assignments
    assignments = await db.teacher_assignments.find(
        {"teacher_id": teacher_id, "active": True},
    ).to_list(500)

    if not assignments:
        return {"students": [], "total": 0, "page": page}

    applicant_ids = [a["applicant_id"] for a in assignments]

    # Check consent for each applicant
    consented_ids = []
    for aid in applicant_ids:
        consent = await db.consents.find_one({
            "user_id": aid,
            "consent_type": "teacher_data_access",
            "granted": True,
            "revoked_at": None,
        })
        if consent:
            consented_ids.append(aid)

    if not consented_ids:
        return {"students": [], "total": 0, "page": page, "note": "No students with active consent"}

    # Build projection (only allowed fields)
    projection = {"_id": 0}
    for f in TEACHER_EXCLUDED_FIELDS:
        projection[f] = 0

    # Fetch user data for consented students
    skip = (page - 1) * limit
    students = []

    for cid in consented_ids[skip:skip + limit]:
        # Get user info
        user_doc = await db.users.find_one(
            {"_id": ObjectId(cid)},
            {"_id": 1, "full_name": 1, "first_name": 1, "last_name": 1,
             "email": 1, "phone": 1, "language_pref": 1},
        )
        if not user_doc:
            continue

        # Get application info
        app_doc = await db.applications.find_one(
            {"applicant_id": cid},
            {"_id": 0, "applicant_id": 0, "notes": 0, "priority": 0,
             "duplicate_flag": 0, "referral_code": 0},
        )

        student = {
            "id": str(user_doc["_id"]),
            "full_name": user_doc.get("full_name", ""),
            "first_name": user_doc.get("first_name", ""),
            "last_name": user_doc.get("last_name", ""),
            "email": user_doc.get("email", ""),
            "phone": user_doc.get("phone", ""),
        }
        if app_doc:
            student.update({
                "course_type": app_doc.get("course_type"),
                "language_level": app_doc.get("language_level"),
                "degree_country": app_doc.get("degree_country"),
                "current_stage": app_doc.get("current_stage"),
                "created_at": str(app_doc.get("created_at", "")),
            })

        students.append(student)

    # Audit log
    await write_audit_log(
        "teacher_viewed_students", teacher_id, "teacher_access", teacher_id,
        {"student_count": len(students)},
    )

    return {"students": students, "total": len(consented_ids), "page": page}


@router.post("/assignments")
async def create_assignment(
    applicant_id: str = Query(...),
    teacher_id: str = Query(...),
    user: dict = Depends(require_roles("superadmin", "admin", "staff")),
):
    """Assign a student to a teacher (staff/admin only)."""
    db = get_db()

    # Verify teacher exists and has teacher role
    teacher = await db.users.find_one({"_id": ObjectId(teacher_id), "role": "teacher"})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found or not a teacher role")

    # Verify applicant exists
    applicant = await db.users.find_one({"_id": ObjectId(applicant_id)})
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    # Check if assignment already exists
    existing = await db.teacher_assignments.find_one({
        "teacher_id": teacher_id,
        "applicant_id": applicant_id,
        "active": True,
    })
    if existing:
        return {"status": "already_assigned"}

    await db.teacher_assignments.insert_one({
        "teacher_id": teacher_id,
        "applicant_id": applicant_id,
        "assigned_by": user["id"],
        "active": True,
        "assigned_at": datetime.now(timezone.utc),
    })

    await write_audit_log(
        "teacher_assignment_created", user["id"], "teacher_assignment", teacher_id,
        {"applicant_id": applicant_id},
    )

    return {"status": "assigned", "teacher_id": teacher_id, "applicant_id": applicant_id}


@router.delete("/assignments")
async def remove_assignment(
    applicant_id: str = Query(...),
    teacher_id: str = Query(...),
    user: dict = Depends(require_roles("superadmin", "admin", "staff")),
):
    """Remove a student-teacher assignment (staff/admin only)."""
    db = get_db()
    result = await db.teacher_assignments.update_one(
        {"teacher_id": teacher_id, "applicant_id": applicant_id, "active": True},
        {"$set": {"active": False, "removed_at": datetime.now(timezone.utc), "removed_by": user["id"]}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await write_audit_log(
        "teacher_assignment_removed", user["id"], "teacher_assignment", teacher_id,
        {"applicant_id": applicant_id},
    )

    return {"status": "removed"}


@router.get("/assignments")
async def list_assignments(
    teacher_id: Optional[str] = None,
    user: dict = Depends(get_current_user),
):
    """List assignments. Teachers see their own; staff/admin see all or filtered."""
    db = get_db()

    if user["role"] == "teacher":
        query = {"teacher_id": user["id"], "active": True}
    elif user["role"] in STAFF_ROLES or user["role"] in ADMIN_ROLES:
        query = {"active": True}
        if teacher_id:
            query["teacher_id"] = teacher_id
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    assignments = await db.teacher_assignments.find(query, {"_id": 0}).to_list(500)
    return {"assignments": assignments}



@router.get("/list")
async def list_teachers(
    user: dict = Depends(get_current_user),
):
    """List all teachers with basic info (staff/admin/teacher use)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES and user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = get_db()
    teachers = await db.users.find(
        {"role": "teacher"},
        {"_id": 1, "full_name": 1, "email": 1, "active": 1},
    ).to_list(200)

    result = []
    for t in teachers:
        result.append({
            "id": str(t["_id"]),
            "full_name": t.get("full_name", ""),
            "email": t.get("email", ""),
            "active": t.get("active", True),
        })
    return result
