"""
Consent router – GDPR-compliant consent capture and management.

Purpose: Allows applicants to grant/revoke consent for data sharing
with teaching/supervisory staff as required for educational administration.

Key principles:
- Purpose limitation (Zweckbindung)
- Data minimization (Datenminimierung)
- Versioned consent with timestamps
- Revocable at any time
- Full audit trail
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from deps import get_current_user, ADMIN_ROLES, STAFF_ROLES, TEACHING_ROLES
from database import get_db
from models.schemas import ConsentCapture
from services.audit import write_audit_log

router = APIRouter(prefix="/api/consents", tags=["consents"])

# Consent type definitions with purpose descriptions
CONSENT_TYPES = {
    "teacher_data_access": {
        "purpose_de": "Weitergabe relevanter Bewerbungs- und Lerndaten an zugewiesenes Lehr- und Betreuungspersonal zum Zweck der padagogischen Betreuung und Kursorganisation.",
        "purpose_en": "Sharing of relevant application and learning data with assigned teaching and supervisory staff for the purpose of educational support and course administration.",
        "scope": ["full_name", "email", "phone", "course_type", "language_level", "degree_country", "documents_status", "application_stage"],
        "excludes": ["financial_data", "passport_details", "internal_notes", "ai_screening_reports"],
    },
}


@router.post("/grant")
async def grant_consent(data: ConsentCapture, user: dict = Depends(get_current_user)):
    """Applicant grants consent for a specific purpose."""
    if data.consent_type not in CONSENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unknown consent type: {data.consent_type}")

    db = get_db()
    consent_def = CONSENT_TYPES[data.consent_type]

    consent_doc = {
        "user_id": user["id"],
        "consent_type": data.consent_type,
        "version": data.version,
        "granted": data.granted,
        "purpose_de": consent_def["purpose_de"],
        "purpose_en": consent_def["purpose_en"],
        "scope": consent_def["scope"],
        "excludes": consent_def["excludes"],
        "granted_at": datetime.now(timezone.utc),
        "revoked_at": None,
        "ip_hint": "recorded_server_side",
    }

    # Revoke any existing consent of same type
    await db.consents.update_many(
        {"user_id": user["id"], "consent_type": data.consent_type, "revoked_at": None},
        {"$set": {"revoked_at": datetime.now(timezone.utc)}},
    )

    result = await db.consents.insert_one(consent_doc)
    await write_audit_log(
        "consent_granted" if data.granted else "consent_declined",
        user["id"], "consent", str(result.inserted_id),
        {"consent_type": data.consent_type, "version": data.version},
    )

    return {"status": "ok", "consent_type": data.consent_type, "granted": data.granted}


@router.post("/revoke/{consent_type}")
async def revoke_consent(consent_type: str, user: dict = Depends(get_current_user)):
    """Applicant revokes a previously granted consent."""
    db = get_db()
    result = await db.consents.update_many(
        {"user_id": user["id"], "consent_type": consent_type, "revoked_at": None, "granted": True},
        {"$set": {"revoked_at": datetime.now(timezone.utc)}},
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No active consent found to revoke")

    await write_audit_log("consent_revoked", user["id"], "consent", consent_type)
    return {"status": "revoked", "consent_type": consent_type}


@router.get("/my")
async def get_my_consents(user: dict = Depends(get_current_user)):
    """Get all consents for the current user."""
    db = get_db()
    consents = await db.consents.find(
        {"user_id": user["id"]},
        {"_id": 0},
    ).sort("granted_at", -1).to_list(100)
    return consents


@router.get("/check/{user_id}/{consent_type}")
async def check_consent(user_id: str, consent_type: str, user: dict = Depends(get_current_user)):
    """Check if a specific user has active consent (staff/teacher use)."""
    if user["role"] not in TEACHING_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = get_db()
    active = await db.consents.find_one({
        "user_id": user_id,
        "consent_type": consent_type,
        "granted": True,
        "revoked_at": None,
    })
    return {"has_consent": active is not None, "consent_type": consent_type}


@router.get("/types")
async def get_consent_types():
    """Return available consent types with descriptions."""
    return CONSENT_TYPES
