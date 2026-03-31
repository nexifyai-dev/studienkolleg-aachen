"""
Leads router – public ingest endpoint.
No authentication required (public-facing form submission).
Duplicate detection prevents double-entries.
Bewerbung + Registrierung gekoppelt: Optional password creates portal account.
"""
import base64
import bcrypt
import jwt
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from database import get_db
from config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_TTL_MINUTES, REFRESH_TOKEN_TTL_DAYS, COOKIE_SECURE, COOKIE_SAMESITE
from models.schemas import LeadIngest, to_str_id
from services.audit import write_audit_log
from services.storage import (
    storage, build_storage_key, sanitize_filename,
    preflight_validate_upload, derive_document_status,
)
from services.automation import trigger_application_received, trigger_missing_documents
from services.ai_screening import REQUIRED_DOCUMENT_TYPES

router = APIRouter(prefix="/api/leads", tags=["leads"])
logger = logging.getLogger(__name__)


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _access_token(user_id: str, email: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "email": email, "role": role, "type": "access",
         "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)},
        JWT_SECRET, algorithm=JWT_ALGORITHM,
    )


def _refresh_token(user_id: str) -> str:
    return jwt.encode(
        {"sub": user_id, "type": "refresh",
         "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_TTL_DAYS)},
        JWT_SECRET, algorithm=JWT_ALGORITHM,
    )


@router.post("/ingest")
async def ingest_lead(data: LeadIngest):
    db = get_db()
    email = data.email.lower().strip()

    full_name = data.full_name
    if not full_name and data.first_name:
        full_name = f"{data.first_name} {data.last_name or ''}".strip()

    existing_user = await db.users.find_one({"email": email})
    duplicate_flag = bool(existing_user)
    user_id = None
    password_hash = _hash(data.password) if data.password and len(data.password) >= 8 else None

    if existing_user:
        user_id = str(existing_user["_id"])
        # Claim account: set password if not yet set
        if password_hash and not existing_user.get("password_hash"):
            await db.users.update_one(
                {"_id": existing_user["_id"]},
                {"$set": {
                    "password_hash": password_hash,
                    "full_name": full_name or existing_user.get("full_name"),
                    "claimed_at": datetime.now(timezone.utc),
                }},
            )
        await write_audit_log("lead_duplicate_flagged", "system", "lead", user_id, {"email": email})
    else:
        user_doc = {
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
        }
        if password_hash:
            user_doc["password_hash"] = password_hash
        result = await db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)

    # Workspace auflösen
    area = data.area_interest.replace("-", "_")
    workspace = await db.workspaces.find_one({"area": area})
    if not workspace:
        workspace = await db.workspaces.find_one({"slug": "studienkolleg"})
    workspace_id = str(workspace["_id"]) if workspace else None

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

        # Inline document uploads
        uploaded_doc_types = []
        if data.documents:
            for doc_upload in data.documents:
                try:
                    file_bytes = None
                    technical_validation = None
                    filename = sanitize_filename(doc_upload.filename or doc_upload.document_type)
                    if doc_upload.file_data:
                        file_bytes = base64.b64decode(doc_upload.file_data)
                        technical_validation = preflight_validate_upload(
                            filename,
                            doc_upload.content_type,
                            file_bytes,
                        )

                    storage_key = build_storage_key(application_id, doc_upload.document_type, filename)
                    status = derive_document_status(bool(file_bytes), technical_validation)

                    if file_bytes and status == "uploaded":
                        await storage().upload(storage_key, file_bytes, doc_upload.content_type)

                    doc = {
                        "application_id": application_id,
                        "document_type": doc_upload.document_type,
                        "filename": filename,
                        "content_type": doc_upload.content_type,
                        "file_size": len(file_bytes) if file_bytes else None,
                        "status": status,
                        "uploaded_by": user_id,
                        "uploaded_at": datetime.now(timezone.utc),
                        "visibility": "private",
                        "storage_key": storage_key if status == "uploaded" else None,
                        "has_binary": bool(file_bytes),
                        "technical_validation": technical_validation,
                    }
                    doc_result = await db.documents.insert_one(doc)
                    doc_id = str(doc_result.inserted_id)
                    await write_audit_log(
                        "document_uploaded", user_id, "document", doc_id,
                        {
                            "doc_type": doc_upload.document_type,
                            "source": "lead_form",
                            "status": status,
                        }
                    )
                    if status == "uploaded":
                        uploaded_doc_types.append(doc_upload.document_type)
                except Exception as e:
                    logger.warning(f"[LEADS] Doc upload failed for {doc_upload.document_type}: {e}")

        missing_types = [t for t in REQUIRED_DOCUMENT_TYPES if t not in uploaded_doc_types]
        await trigger_application_received(application_id, email, full_name, data.course_type)
        if missing_types:
            await trigger_missing_documents(application_id, email, full_name, missing_types)

    # Welcome email
    if password_hash:
        from services.email import send_welcome
        send_welcome(email, full_name)

    # Build response – set auth cookies if password was provided
    response_data = {
        "success": True,
        "user_id": user_id,
        "application_id": application_id,
        "duplicate_flag": duplicate_flag,
        "message": "Deine Bewerbung ist eingegangen. Wir melden uns innerhalb von 24 Stunden.",
    }

    if password_hash:
        response_data["account_created"] = True
        access = _access_token(user_id, email, "applicant")
        refresh = _refresh_token(user_id)
        resp = JSONResponse(content=response_data)
        common = dict(httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE, path="/")
        resp.set_cookie("access_token", access, max_age=ACCESS_TOKEN_TTL_MINUTES * 60, **common)
        resp.set_cookie("refresh_token", refresh, max_age=REFRESH_TOKEN_TTL_DAYS * 86400, **common)
        return resp

    return response_data
