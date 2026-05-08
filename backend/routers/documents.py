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
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
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



@router.get("/documents/my")
async def list_my_documents(user: dict = Depends(get_current_user)):
    """List all documents for the current applicant across all their applications."""
    db = get_db()
    # Find all applications for this user
    apps = await db.applications.find(
        {"applicant_id": user["id"]}, {"_id": 1}
    ).to_list(50)
    app_ids = [str(a["_id"]) for a in apps]
    if not app_ids:
        return []
    docs = await db.documents.find(
        {"application_id": {"$in": app_ids}}
    ).sort("uploaded_at", -1).to_list(200)
    result = []
    for d in docs:
        doc = to_str_id(d)
        doc.pop("storage_key", None)
        result.append(doc)
    return result


@router.post("/documents")
async def create_document_simple(request: Request, user: dict = Depends(get_current_user)):
    """Simplified document creation from the portal (metadata only, no file binary)."""
    db = get_db()
    body = await request.json()
    app_id = body.get("application_id")
    if not app_id:
        raise HTTPException(status_code=400, detail="application_id required")
    await _assert_app_access(app_id, user, db)

    filename = body.get("filename", "document")
    doc_type = body.get("document_type", "other")
    doc = {
        "application_id": app_id,
        "document_type": doc_type,
        "filename": filename,
        "content_type": "application/octet-stream",
        "file_size": None,
        "status": body.get("status", "uploaded"),
        "uploaded_by": user["id"],
        "uploaded_at": datetime.now(timezone.utc),
        "visibility": "private",
        "storage_key": "",
        "has_binary": False,
    }
    result = await db.documents.insert_one(doc)
    doc_id = str(result.inserted_id)
    await write_audit_log("document_uploaded", user["id"], "document", doc_id,
                          {"doc_type": doc_type, "filename": filename})
    return {"id": doc_id, "status": "uploaded"}



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

    content_type_header = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type_header:
        # Multipart File-Upload (Standard-Browser-Upload)
        form = await request.form()
        file_field = form.get("file")
        if not file_field:
            raise HTTPException(status_code=400, detail="Kein 'file' Feld im Upload")
        doc_type = form.get("doc_type", form.get("document_type", "other"))
        filename = sanitize_filename(file_field.filename or "document")
        content_type = file_field.content_type or "application/octet-stream"
        file_bytes = await file_field.read()
    else:
        # JSON mit Base64-encoded Datei (Legacy/API-Clients)
        body = await request.json()
        doc_type = body.get("document_type", body.get("doc_type", "other"))
        filename = sanitize_filename(body.get("filename", "document"))
        content_type = body.get("content_type", "application/octet-stream")
        file_data_b64 = body.get("file_data")
        file_bytes = None
        if file_data_b64:
            try:
                file_bytes = base64.b64decode(file_data_b64)
            except Exception:
                raise HTTPException(status_code=400, detail="Ungueltige Datei-Kodierung (erwartet Base64)")

    if file_bytes:
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

    # ─── Auto Re-Screening ueber Job-Queue (nicht mehr synchron) ───
    try:
        from services.delta_screening import is_screening_relevant_upload
        if is_screening_relevant_upload(doc_type):
            from services.job_queue import enqueue
            import asyncio
            asyncio.ensure_future(enqueue(
                job_type="delta_rescreening",
                payload={
                    "application_id": app_id,
                    "doc_type": doc_type,
                    "filename": filename,
                    "uploaded_by": user["id"],
                },
                dedupe_key=f"rescreen_{app_id}_{doc_type}",
                related_entity_type="application",
                related_entity_id=app_id,
                actor_id=user["id"],
                priority="high",
            ))
            import logging
            logging.getLogger(__name__).info(f"[AUTO_RESCREEN] Job enqueued for {app_id} after {doc_type} upload")
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"[AUTO_RESCREEN] Failed to enqueue: {e}")

    # ─── Autonome KI-Dokumentvalidierung ─────────────────────────
    validation_result = None
    if file_bytes:
        try:
            from services.document_validation import validate_document_with_ai
            # Bewerberprofil und Application-Daten laden
            app_doc = await db.applications.find_one({"_id": ObjectId(app_id)})
            applicant_profile = None
            application_data = None
            if app_doc:
                from models.schemas import to_str_id as _to_str
                application_data = _to_str(dict(app_doc))
                applicant = await db.users.find_one(
                    {"_id": ObjectId(app_doc.get("applicant_id"))},
                    {"_id": 0, "full_name": 1, "email": 1, "country": 1}
                )
                applicant_profile = applicant

            # Volle KI-Pipeline: Vision + Klassifikation + Extraktion + Wissensabgleich
            validation_result = await validate_document_with_ai(
                file_data=file_bytes,
                filename=filename,
                content_type=content_type,
                declared_type=doc_type,
                applicant_profile=applicant_profile,
                application=application_data,
                application_id=app_id,
            )

            # Update document with validation results
            validation_update = {
                "validation_status": validation_result["validation_status"],
                "validation_confidence": validation_result["confidence"],
                "detected_type": validation_result["detected_type"],
                "validation_evidence": validation_result["evidence"],
                "validation_warnings": validation_result["warnings"],
                "validation_errors": validation_result.get("errors", []),
                "staff_decision_required": validation_result["staff_decision_required"],
                "next_action": validation_result["next_action"],
                "validated_at": datetime.now(timezone.utc),
            }

            # KI-spezifische Felder speichern
            if validation_result.get("ai_classification"):
                validation_update["ai_classification"] = validation_result["ai_classification"]
            if validation_result.get("ai_extraction"):
                validation_update["ai_extraction"] = validation_result["ai_extraction"]
            if validation_result.get("ai_report"):
                validation_update["ai_report"] = validation_result["ai_report"]
            if validation_result.get("knowledge_match"):
                validation_update["knowledge_match"] = validation_result["knowledge_match"]

            # Map validation status to document status
            vs = validation_result["validation_status"]
            if vs == "validated":
                validation_update["status"] = "uploaded"
            elif vs == "rejected":
                validation_update["status"] = "rejected"
                validation_update["rejection_reason"] = ", ".join(validation_result.get("errors", []))
            elif vs == "needs_review":
                validation_update["status"] = "in_review"

            await db.documents.update_one(
                {"_id": result.inserted_id},
                {"$set": validation_update}
            )

            # Extrahierte Daten auf Application mappen (DB-Feld-Updates)
            db_updates = validation_result.get("db_field_updates", {})
            if db_updates:
                await db.applications.update_one(
                    {"_id": ObjectId(app_id)},
                    {"$set": db_updates}
                )
                logger.info(f"[DOC_UPLOAD] {len(db_updates)} Felder aus Dokument extrahiert und auf Bewerbung gemappt")

            # Task fuer Staff bei Review-Bedarf
            if validation_result["staff_decision_required"]:
                ai_class = validation_result.get("ai_classification", {})
                task_title = f"KI-Dokumentpruefung: {filename} ({doc_type})"
                warning_text = ", ".join(validation_result["warnings"][:3]) if validation_result["warnings"] else "Automatische Pruefung unsicher"
                desc_parts = [
                    f"Automatische KI-Validierung: {vs}.",
                    f"Erkannter Typ: {ai_class.get('document_type', '?')} (Konfidenz: {ai_class.get('confidence', '?')}).",
                    f"Land: {ai_class.get('issuing_country', '?')}.",
                    f"Hinweise: {warning_text}",
                ]
                await db.tasks.insert_one({
                    "title": task_title,
                    "description": " ".join(desc_parts),
                    "application_id": app_id,
                    "task_type": "document_review",
                    "priority": "high" if vs == "rejected" else "medium",
                    "status": "open",
                    "created_at": datetime.now(timezone.utc),
                    "created_by": "system",
                    "metadata": {
                        "document_id": doc_id,
                        "document_type": doc_type,
                        "validation_status": vs,
                        "confidence": validation_result["confidence"],
                        "ai_detected_type": ai_class.get("document_type"),
                        "issuing_country": ai_class.get("issuing_country"),
                    },
                })
        except Exception as e:
            logger.warning(f"[DOC_UPLOAD] KI-Dokumentvalidierung fehlgeschlagen: {e}", exc_info=True)

    # Return ohne storage_key
    ai_class = (validation_result or {}).get("ai_classification", {})
    return {
        "id": doc_id, "application_id": app_id,
        "document_type": doc_type, "filename": filename,
        "status": validation_result["validation_status"] if validation_result else "uploaded",
        "uploaded_at": doc["uploaded_at"].isoformat(),
        "has_binary": doc["has_binary"],
        "validation": {
            "status": validation_result["validation_status"],
            "confidence": validation_result["confidence"],
            "detected_type": validation_result["detected_type"],
            "warnings": validation_result["warnings"],
            "staff_review_required": validation_result["staff_decision_required"],
            "ai_classification": {
                "document_type": ai_class.get("document_type"),
                "issuing_country": ai_class.get("issuing_country"),
                "is_authentic": ai_class.get("is_authentic_document"),
                "readability": ai_class.get("readability"),
            } if ai_class else None,
            "extracted_fields": list((validation_result.get("db_field_updates") or {}).keys()),
        } if validation_result else None,
    }


@router.get("/documents/{doc_id}/download")
async def download_document(doc_id: str, user: dict = Depends(get_current_user)):
    """
    Server-side download: authenticates user, fetches from storage, streams to client.
    Supports inline display for PDFs and images (Content-Disposition: inline).
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

    content_type = doc.get("content_type", "application/octet-stream")
    filename = doc.get("filename", "document")

    # PDFs und Bilder inline anzeigen (fuer In-Browser-Vorschau)
    inline_types = {"application/pdf", "image/jpeg", "image/jpg", "image/png", "image/webp"}
    if content_type in inline_types:
        disposition = f'inline; filename="{filename}"'
    else:
        disposition = f'attachment; filename="{filename}"'

    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={"Content-Disposition": disposition},
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

    allowed_statuses = {"in_review", "approved", "rejected", "superseded", "validated", "needs_review"}
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

    # Automation: Bei Ablehnung Bewerber benachrichtigen (Pflichtlogik aus 07_ux_workflows Flow 3)
    if data.status == "rejected" and doc.get("application_id"):
        try:
            app = await db.applications.find_one(
                {"_id": ObjectId(doc["application_id"])},
                {"applicant_id": 1, "applicant_name": 1},
            )
            if app and app.get("applicant_id"):
                applicant = await db.users.find_one(
                    {"_id": ObjectId(app["applicant_id"])},
                    {"email": 1, "full_name": 1, "language_pref": 1},
                )
                if applicant:
                    lang = applicant.get("language_pref", "de")
                    doc_name = doc.get("document_type", doc.get("filename", "Dokument"))
                    reason = data.rejection_reason or ("Nicht spezifiziert" if lang == "de" else "Not specified")

                    # In-App Notification
                    msg = (
                        f"Dein Dokument '{doc_name}' wurde abgelehnt. Grund: {reason}. Bitte lade es erneut hoch."
                        if lang == "de" else
                        f"Your document '{doc_name}' was rejected. Reason: {reason}. Please re-upload."
                    )
                    from services.notifications import create_notification
                    await create_notification(
                        app["applicant_id"], "document_rejected", msg,
                        link="/portal/documents",
                        triggered_by=user["id"], lang=lang,
                    )

                    # E-Mail: Nachforderung mit spezifischem Grund
                    from services.email import send_document_requested
                    send_document_requested(
                        to=applicant["email"],
                        full_name=applicant.get("full_name", ""),
                        document_types=[f"{doc_name} (Grund: {reason})"],
                        lang=lang,
                    )
        except Exception as notify_err:
            logger.warning(f"[DOC_REVIEW] Benachrichtigung fehlgeschlagen: {notify_err}")

    return {"message": f"Dokument: {data.status}", "id": doc_id}


@router.get("/documents/{doc_id}/validation")
async def get_document_validation(doc_id: str, user: dict = Depends(get_current_user)):
    """Return validation details for a document."""
    db = get_db()
    try:
        doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    if user["role"] == "applicant":
        app = await db.applications.find_one({"_id": ObjectId(doc["application_id"])})
        if not app or str(app.get("applicant_id")) != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

    result = to_str_id(doc)
    result.pop("storage_key", None)
    return {
        "id": result.get("id"),
        "document_type": result.get("document_type"),
        "filename": result.get("filename"),
        "status": result.get("status"),
        "validation_status": result.get("validation_status"),
        "validation_confidence": result.get("validation_confidence"),
        "detected_type": result.get("detected_type"),
        "validation_warnings": result.get("validation_warnings", []),
        "validation_errors": result.get("validation_errors", []),
        "staff_decision_required": result.get("staff_decision_required", False),
        "next_action": result.get("next_action"),
        "validated_at": str(result.get("validated_at", "")),
        "reviewed_by": result.get("reviewed_by"),
        "reviewed_at": str(result.get("reviewed_at", "")),
        "rejection_reason": result.get("rejection_reason"),
        "ai_classification": result.get("ai_classification"),
        "ai_extraction": result.get("ai_extraction"),
        "ai_report": result.get("ai_report"),
        "knowledge_match": result.get("knowledge_match"),
    }


@router.post("/documents/{doc_id}/revalidate")
async def revalidate_document(doc_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Re-run validation on an existing document (staff only)."""
    db = get_db()
    try:
        doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not doc:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    storage_key = doc.get("storage_key")
    if not storage_key or not doc.get("has_binary"):
        raise HTTPException(status_code=400, detail="Keine Binärdaten vorhanden")

    try:
        file_bytes = await storage().download(storage_key)
    except Exception:
        raise HTTPException(status_code=404, detail="Datei nicht im Speicher gefunden")

    from services.document_validation import validate_document_with_ai
    app_id = doc["application_id"]
    app_doc = await db.applications.find_one({"_id": ObjectId(app_id)})
    applicant_profile = None
    application_data = None
    if app_doc:
        application_data = to_str_id(dict(app_doc))
        applicant = await db.users.find_one(
            {"_id": ObjectId(app_doc.get("applicant_id"))},
            {"_id": 0, "full_name": 1, "email": 1, "country": 1}
        )
        applicant_profile = applicant

    validation_result = await validate_document_with_ai(
        file_data=file_bytes,
        filename=doc.get("filename", ""),
        content_type=doc.get("content_type", ""),
        declared_type=doc.get("document_type", "other"),
        applicant_profile=applicant_profile,
        application=application_data,
        application_id=app_id,
    )

    vs = validation_result["validation_status"]
    update = {
        "validation_status": vs,
        "validation_confidence": validation_result["confidence"],
        "detected_type": validation_result["detected_type"],
        "validation_evidence": validation_result["evidence"],
        "validation_warnings": validation_result["warnings"],
        "validation_errors": validation_result.get("errors", []),
        "staff_decision_required": validation_result["staff_decision_required"],
        "next_action": validation_result["next_action"],
        "validated_at": datetime.now(timezone.utc),
        "revalidated_by": user["id"],
    }
    if validation_result.get("ai_classification"):
        update["ai_classification"] = validation_result["ai_classification"]
    if validation_result.get("ai_extraction"):
        update["ai_extraction"] = validation_result["ai_extraction"]
    if validation_result.get("ai_report"):
        update["ai_report"] = validation_result["ai_report"]
    if validation_result.get("knowledge_match"):
        update["knowledge_match"] = validation_result["knowledge_match"]

    # DB-Feld-Updates auf Application mappen
    db_updates = validation_result.get("db_field_updates", {})
    if db_updates:
        await db.applications.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": db_updates}
        )

    await db.documents.update_one({"_id": ObjectId(doc_id)}, {"$set": update})
    await write_audit_log("document_revalidated", user["id"], "document", doc_id,
                          {"validation_status": vs, "confidence": validation_result["confidence"]})

    return {
        "validation_status": vs,
        "confidence": validation_result["confidence"],
        "detected_type": validation_result["detected_type"],
        "warnings": validation_result["warnings"],
        "ai_classification": validation_result.get("ai_classification"),
        "ai_extraction": validation_result.get("ai_extraction"),
        "ai_report": validation_result.get("ai_report"),
        "knowledge_match": validation_result.get("knowledge_match"),
        "staff_decision_required": validation_result["staff_decision_required"],
        "db_fields_updated": list(db_updates.keys()) if db_updates else [],
        "total_ai_tokens": validation_result.get("total_ai_tokens", 0),
    }


# ─── Delete Document ───────────────────────────────────────────
@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, user=Depends(get_current_user)):
    """Loescht ein Dokument. Bewerber duerfen nur eigene, Staff alle loeschen."""
    db = get_db()
    doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(404, "Dokument nicht gefunden")

    app_id = doc.get("application_id")
    if user["role"] == "applicant":
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
        if not app or app.get("applicant_id") != user["id"]:
            raise HTTPException(403, "Kein Zugriff")
    elif user["role"] not in ("staff", "admin", "superadmin", "accounting_staff"):
        raise HTTPException(403, "Keine Berechtigung")

    # S3-Datei loeschen falls vorhanden
    storage_key = doc.get("storage_key")
    if storage_key:
        try:
            await storage().delete(storage_key)
        except Exception as e:
            logger.warning(f"[DOC_DELETE] S3-Loeschung fehlgeschlagen: {e}")

    await db.documents.delete_one({"_id": ObjectId(document_id)})
    await write_audit_log("document_deleted", user["id"], "document", document_id,
                          details={"filename": doc.get("filename"), "type": doc.get("document_type")})
    return {"ok": True, "message": "Dokument geloescht"}


# ─── Replace Document ──────────────────────────────────────────
@router.put("/documents/{document_id}/replace")
async def replace_document(document_id: str, request: Request, user=Depends(get_current_user)):
    """Ersetzt ein Dokument durch ein neues. Altes wird als 'superseded' markiert."""
    db = get_db()
    old_doc = await db.documents.find_one({"_id": ObjectId(document_id)})
    if not old_doc:
        raise HTTPException(404, "Dokument nicht gefunden")

    app_id = old_doc.get("application_id")
    if user["role"] == "applicant":
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
        if not app or app.get("applicant_id") != user["id"]:
            raise HTTPException(403, "Kein Zugriff")
    elif user["role"] not in ("staff", "admin", "superadmin"):
        raise HTTPException(403, "Keine Berechtigung")

    body = await request.json()
    file_data_b64 = body.get("file_data")
    filename = body.get("filename") or old_doc.get("filename")
    content_type = body.get("content_type") or old_doc.get("content_type", "application/pdf")

    if not file_data_b64:
        raise HTTPException(400, "file_data ist erforderlich")

    file_bytes = base64.b64decode(file_data_b64)
    validate_upload(filename, content_type, len(file_bytes))

    # Altes Dokument als superseded markieren
    await db.documents.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {"status": "superseded", "superseded_at": datetime.now(timezone.utc)}}
    )

    # Neues Dokument erstellen
    doc_type = old_doc.get("document_type", "other")
    safe_name = sanitize_filename(filename)
    new_doc_id = str(ObjectId())
    storage_key = build_storage_key(app_id, doc_type, new_doc_id, safe_name)

    stored = False
    try:
        await storage().upload(storage_key, file_bytes, content_type)
        stored = True
    except Exception as e:
        logger.warning(f"[DOC_REPLACE] S3-Upload fehlgeschlagen: {e}")

    new_doc = {
        "application_id": app_id,
        "document_type": doc_type,
        "filename": safe_name,
        "content_type": content_type,
        "status": "uploaded",
        "uploaded_at": datetime.now(timezone.utc),
        "uploaded_by": user["id"],
        "storage_key": storage_key if stored else None,
        "file_size": len(file_bytes),
        "has_binary": True,
        "replaces_document_id": document_id,
    }

    if not stored:
        new_doc["file_data"] = base64.b64encode(file_bytes).decode()

    result = await db.documents.insert_one(new_doc)
    new_id = str(result.inserted_id)

    await write_audit_log("document_replaced", user["id"], "document", new_id,
                          details={"old_id": document_id, "filename": safe_name, "type": doc_type})

    return {
        "id": new_id,
        "application_id": app_id,
        "document_type": doc_type,
        "filename": safe_name,
        "status": "uploaded",
        "uploaded_at": new_doc["uploaded_at"].isoformat(),
        "replaces": document_id,
    }
