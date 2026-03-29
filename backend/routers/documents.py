"""
Document router – upload, download, review.

Security notes:
- All document access is scoped to application ownership
- Downloads are served server-side (no presigned URLs exposed directly)
- File validation: MIME type + size limits enforced
- Storage key never returned as a public URL
- All upload/download/review actions are audit-logged
"""
import base64
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import Response
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES
from models.schemas import DocumentStatusUpdate, to_str_id
from services.audit import write_audit_log
from services.storage import (
    storage, build_storage_key, sanitize_filename,
    validate_upload, ALLOWED_MIME_TYPES, MAX_FILE_SIZE_BYTES
)

router = APIRouter(prefix="/api", tags=["documents"])


async def _assert_app_access(app_id: str, user: dict, db):
    """Raise 403/404 if user cannot access this application's documents."""
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    if user["role"] == "applicant" and str(app.get("applicant_id")) != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return app


@router.get("/applications/{app_id}/documents")
async def list_documents(app_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await _assert_app_access(app_id, user, db)
    docs = await db.documents.find({"application_id": app_id}).to_list(100)
    result = []
    for d in docs:
        doc = to_str_id(d)
        doc.pop("storage_key", None)  # Never expose internal storage key
        result.append(doc)
    return result


@router.post("/applications/{app_id}/documents/upload")
async def upload_document(app_id: str, request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    await _assert_app_access(app_id, user, db)

    body = await request.json()
    doc_type = body.get("document_type", "other")
    filename = sanitize_filename(body.get("filename", "document"))
    content_type = body.get("content_type", "application/octet-stream")
    file_data_b64 = body.get("file_data")  # base64-encoded binary (optional in MVP)

    file_bytes = None
    if file_data_b64:
        try:
            file_bytes = base64.b64decode(file_data_b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Ungültige Datei-Kodierung (erwartet Base64)")
        try:
            validate_upload(filename, len(file_bytes), content_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    storage_key = build_storage_key(app_id, doc_type, filename)

    if file_bytes:
        await storage().upload(storage_key, file_bytes, content_type)

    doc = {
        "application_id": app_id,
        "document_type": doc_type,
        "filename": filename,
        "content_type": content_type,
        "file_size": len(file_bytes) if file_bytes else None,
        "status": "uploaded",
        "uploaded_by": user["id"],
        "uploaded_at": datetime.now(timezone.utc),
        "visibility": "private",
        "storage_key": storage_key,  # internal only – never returned to client
        "has_binary": bool(file_bytes),
    }
    result = await db.documents.insert_one(doc)
    doc_id = str(result.inserted_id)

    await write_audit_log("document_uploaded", user["id"], "document", doc_id,
                          {"doc_type": doc_type, "filename": filename, "has_binary": doc["has_binary"]})
    await db.applications.update_one(
        {"_id": ObjectId(app_id)},
        {"$set": {"last_activity_at": datetime.now(timezone.utc)}},
    )

    # Notify staff about new document upload (applicants only)
    if user["role"] == "applicant":
        try:
            from services.automation import trigger_document_uploaded
            await trigger_document_uploaded(
                application_id=app_id,
                applicant_id=user["id"],
                applicant_name=user.get("full_name", user.get("email", "")),
                doc_type=doc_type,
                filename=filename,
            )
        except Exception:
            pass

    # Return without storage_key
    return {
        "id": doc_id, "application_id": app_id,
        "document_type": doc_type, "filename": filename,
        "status": "uploaded", "uploaded_at": doc["uploaded_at"].isoformat(),
        "has_binary": doc["has_binary"],
    }


@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    """
    Server-side download: authenticates user, fetches from storage, streams to client.
    Never exposes the storage key or a direct storage URL.
    """
    db = get_db()
    try:
        doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Dokument-ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    # Access check: applicant must own the parent application
    if user["role"] == "applicant":
        app = await db.applications.find_one({"_id": ObjectId(doc["application_id"])})
        if not app or str(app.get("applicant_id")) != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

    storage_key = doc.get("storage_key")
    if not storage_key or not doc.get("has_binary"):
        raise HTTPException(status_code=404, detail="Keine Datei vorhanden (nur Metadaten gespeichert)")

    try:
        file_bytes = await storage().download(storage_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Datei im Speicher nicht gefunden")
    except NotImplementedError:
        raise HTTPException(status_code=503, detail="Datei-Download noch nicht konfiguriert")

    await write_audit_log("document_downloaded", user["id"], "document", doc_id)

    return Response(
        content=file_bytes,
        media_type=doc.get("content_type", "application/octet-stream"),
        headers={"Content-Disposition": f'attachment; filename="{doc["filename"]}"'},
    )


@router.put("/documents/{doc_id}/review")
async def review_document(
    doc_id: str,
    data: DocumentStatusUpdate,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    db = get_db()
    try:
        doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    allowed_statuses = {"in_review", "approved", "rejected", "superseded"}
    if data.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Ungültiger Status. Erlaubt: {sorted(allowed_statuses)}")

    update = {
        "status": data.status,
        "reviewed_by": user["id"],
        "reviewed_at": datetime.now(timezone.utc),
    }
    if data.rejection_reason:
        update["rejection_reason"] = data.rejection_reason

    if data.comment:
        await db.comments.insert_one({
            "document_id": doc_id,
            "application_id": doc.get("application_id"),
            "content": data.comment,
            "author_id": user["id"],
            "visibility": "internal",
            "created_at": datetime.now(timezone.utc),
        })

    await db.documents.update_one({"_id": ObjectId(doc_id)}, {"$set": update})
    await write_audit_log(f"document_{data.status}", user["id"], "document", doc_id,
                          {"reason": data.rejection_reason})
    return {"message": f"Dokument: {data.status}", "id": doc_id}
