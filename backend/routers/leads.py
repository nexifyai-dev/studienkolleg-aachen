"""
Leads router – public ingest endpoint.
No authentication required (public-facing form submission).
Duplicate detection prevents double-entries.
"""
from datetime import datetime, timezone
from fastapi import APIRouter
from database import get_db
from models.schemas import LeadIngest, to_str_id
from services.audit import write_audit_log
from services.email import send_application_received

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.post("/ingest")
async def ingest_lead(data: LeadIngest):
    db = get_db()
    email = data.email.lower().strip()

    existing_user = await db.users.find_one({"email": email})
    duplicate_flag = bool(existing_user)
    user_id = None

    if existing_user:
        user_id = str(existing_user["_id"])
        await write_audit_log("lead_duplicate_flagged", "system", "lead", user_id, {"email": email})
    else:
        result = await db.users.insert_one({
            "email": email,
            "full_name": data.full_name,
            "phone": data.phone,
            "country": data.country,
            "role": "applicant",
            "language_pref": "en",
            "active": True,
            "created_at": datetime.now(timezone.utc),
        })
        user_id = str(result.inserted_id)

    # Resolve workspace
    area = data.area_interest.replace("-", "_")
    workspace = await db.workspaces.find_one({"area": area})
    if not workspace:
        workspace = await db.workspaces.find_one({"slug": "studienkolleg"})
    workspace_id = str(workspace["_id"]) if workspace else None

    # Check for existing active application
    existing_app = None
    if workspace_id:
        existing_app = await db.applications.find_one({
            "applicant_id": user_id,
            "workspace_id": workspace_id,
            "current_stage": {"$nin": ["completed", "archived"]},
        })

    application_id = None
    if not existing_app and workspace_id:
        app_doc = {
            "applicant_id": user_id,
            "workspace_id": workspace_id,
            "current_stage": "lead_new",
            "source": data.source,
            "desired_start": data.desired_start,
            "language_level": data.language_level,
            "notes": data.notes,
            "priority": "normal",
            "duplicate_flag": duplicate_flag,
            "referral_code": data.referral_code,
            "created_at": datetime.now(timezone.utc),
            "last_activity_at": datetime.now(timezone.utc),
        }
        result = await db.applications.insert_one(app_doc)
        application_id = str(result.inserted_id)
        await write_audit_log("lead_created", "system", "application", application_id,
                              {"source": data.source, "email": email, "duplicate": duplicate_flag})
        send_application_received(email, data.full_name, application_id)

    return {
        "success": True,
        "user_id": user_id,
        "application_id": application_id,
        "duplicate_flag": duplicate_flag,
        "message": "Deine Bewerbung ist eingegangen. Wir melden uns innerhalb von 24 Stunden.",
    }
