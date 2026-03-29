"""
Leads router – public ingest endpoint.
No authentication required (public-facing form submission).
Duplicate detection prevents double-entries.

Phase 3 Updates:
- Erweiterte Formularfelder: course_type, semester, degree_country, date_of_birth, combo_option
- Inline Dokument-Uploads (language_certificate, highschool_diploma, passport)
- Workflow-Automation: trigger_application_received nach Eingang
- AI-Screening-Trigger nach erfolgreicher Lead-Erstellung
"""
import base64
import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from database import get_db
from models.schemas import LeadIngest, to_str_id
from services.audit import write_audit_log
from services.storage import storage, build_storage_key, sanitize_filename, validate_upload
from services.automation import trigger_application_received, trigger_missing_documents
from services.ai_screening import REQUIRED_DOCUMENT_TYPES

router = APIRouter(prefix="/api/leads", tags=["leads"])
logger = logging.getLogger(__name__)


@router.post("/ingest")
async def ingest_lead(data: LeadIngest):
    db = get_db()
    email = data.email.lower().strip()

    # full_name aus first/last ableiten wenn vorhanden
    full_name = data.full_name
    if not full_name and data.first_name:
        full_name = f"{data.first_name} {data.last_name or ''}".strip()

    existing_user = await db.users.find_one({"email": email})
    duplicate_flag = bool(existing_user)
    user_id = None

    if existing_user:
        user_id = str(existing_user["_id"])
        await write_audit_log("lead_duplicate_flagged", "system", "lead", user_id, {"email": email})
    else:
        result = await db.users.insert_one({
            "email": email,
            "full_name": full_name,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "phone": data.phone,
            "country": data.country,
            "date_of_birth": data.date_of_birth,
            "role": "applicant",
            "language_pref": "de",
            "active": True,
            "created_at": datetime.now(timezone.utc),
        })
        user_id = str(result.inserted_id)

    # Workspace auflösen
    area = data.area_interest.replace("-", "_")
    workspace = await db.workspaces.find_one({"area": area})
    if not workspace:
        workspace = await db.workspaces.find_one({"slug": "studienkolleg"})
    workspace_id = str(workspace["_id"]) if workspace else None

    # Prüfen ob bereits aktive Bewerbung vorhanden
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
            # Neue Pflichtfelder
            "course_type": data.course_type,
            "desired_start": data.desired_start,
            "combo_option": data.combo_option,
            "language_level": data.language_level,
            "degree_country": data.degree_country,
            "date_of_birth": data.date_of_birth,
            "notes": data.notes,
            "priority": "normal",
            "duplicate_flag": duplicate_flag,
            "referral_code": data.referral_code,
            "created_at": datetime.now(timezone.utc),
            "last_activity_at": datetime.now(timezone.utc),
        }
        result = await db.applications.insert_one(app_doc)
        application_id = str(result.inserted_id)
        await write_audit_log(
            "lead_created", "system", "application", application_id,
            {"source": data.source, "email": email, "duplicate": duplicate_flag,
             "course": data.course_type, "degree_country": data.degree_country}
        )

        # Inline-Dokument-Uploads verarbeiten
        uploaded_doc_types = []
        if data.documents:
            for doc_upload in data.documents:
                try:
                    file_bytes = None
                    if doc_upload.file_data:
                        file_bytes = base64.b64decode(doc_upload.file_data)
                        validate_upload(doc_upload.filename, len(file_bytes), doc_upload.content_type)

                    filename = sanitize_filename(doc_upload.filename or doc_upload.document_type)
                    storage_key = build_storage_key(application_id, doc_upload.document_type, filename)

                    if file_bytes:
                        await storage().upload(storage_key, file_bytes, doc_upload.content_type)

                    doc = {
                        "application_id": application_id,
                        "document_type": doc_upload.document_type,
                        "filename": filename,
                        "content_type": doc_upload.content_type,
                        "file_size": len(file_bytes) if file_bytes else None,
                        "status": "uploaded",
                        "uploaded_by": user_id,
                        "uploaded_at": datetime.now(timezone.utc),
                        "visibility": "private",
                        "storage_key": storage_key,
                        "has_binary": bool(file_bytes),
                    }
                    doc_result = await db.documents.insert_one(doc)
                    doc_id = str(doc_result.inserted_id)
                    await write_audit_log(
                        "document_uploaded", user_id, "document", doc_id,
                        {"doc_type": doc_upload.document_type, "source": "lead_form"}
                    )
                    uploaded_doc_types.append(doc_upload.document_type)
                except Exception as e:
                    logger.warning(f"[LEADS] Doc upload failed for {doc_upload.document_type}: {e}")

        # Fehlende Pflichtdokumente ermitteln
        missing_types = [t for t in REQUIRED_DOCUMENT_TYPES if t not in uploaded_doc_types]

        # Automationen auslösen
        await trigger_application_received(application_id, email, full_name, data.course_type)

        if missing_types:
            await trigger_missing_documents(application_id, email, full_name, missing_types)

    return {
        "success": True,
        "user_id": user_id,
        "application_id": application_id,
        "duplicate_flag": duplicate_flag,
        "message": "Deine Bewerbung ist eingegangen. Wir melden uns innerhalb von 24 Stunden.",
    }
