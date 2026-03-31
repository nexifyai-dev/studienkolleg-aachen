"""
Tasks router – Full operational task management.

Endpoints:
- GET    /api/tasks              – List tasks (filtered by role)
- POST   /api/tasks              – Create task
- GET    /api/tasks/{id}         – Get task detail (with notes, history)
- PUT    /api/tasks/{id}         – Update task
- DELETE /api/tasks/{id}         – Delete task
- POST   /api/tasks/{id}/notes   – Add note
- GET    /api/tasks/{id}/notes   – List notes
- POST   /api/tasks/{id}/attachments – Upload attachment
- GET    /api/tasks/{id}/attachments – List attachments
- GET    /api/tasks/{id}/attachments/{att_id} – Download attachment
- GET    /api/tasks/{id}/history – Get status history
"""
import base64
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import Response
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES, ADMIN_ROLES
from models.schemas import TaskCreate, TaskUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _serialize_task(task: dict) -> dict:
    """Clean MongoDB task document for JSON response."""
    t = to_str_id(task) if "_id" in task else dict(task)
    for field in ("created_at", "updated_at", "due_date"):
        v = t.get(field)
        if v and hasattr(v, "isoformat"):
            t[field] = v.isoformat()
    return t


async def _authorize_task_access(task_id: str, user: dict, mode: str = "read") -> dict:
    """
    Centralized task access guard.

    Rules:
    - Task must exist.
    - Applicant: only tasks for own applications and only public visibility.
    - Staff/Admin: read allowed for admins or creator/assignee.
    - Write: only admin or creator/assignee.
    """
    if mode not in {"read", "write"}:
        raise HTTPException(status_code=500, detail="Ungueltiger Zugriffsmodus")

    db = get_db()
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige Task-ID")

    if not task:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")

    role = user.get("role")
    if role == "applicant":
        app_id = task.get("application_id")
        if not app_id or not ObjectId.is_valid(app_id):
            raise HTTPException(status_code=403, detail="Forbidden")
        app = await db.applications.find_one({"_id": ObjectId(app_id)}, {"applicant_id": 1})
        if not app or str(app.get("applicant_id")) != user["id"] or task.get("visibility") != "public":
            raise HTTPException(status_code=403, detail="Forbidden")
        if mode == "write":
            raise HTTPException(status_code=403, detail="Forbidden")
        return task

    if role in ADMIN_ROLES:
        return task

    if mode == "read":
        if task.get("assigned_to") != user["id"] and task.get("created_by") != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")
        return task

    if task.get("assigned_to") != user["id"] and task.get("created_by") != user["id"]:
        raise HTTPException(
            status_code=403,
            detail="Nur der Ersteller oder zugewiesene Person kann diese Aufgabe bearbeiten",
        )
    return task


@router.get("")
async def list_tasks(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    if user["role"] == "applicant":
        apps = await db.applications.find({"applicant_id": user["id"]}).to_list(50)
        app_ids = [str(a["_id"]) for a in apps]
        query = {"application_id": {"$in": app_ids}, "visibility": "public"}
    else:
        app_id = request.query_params.get("application_id")
        if app_id:
            query = {"application_id": app_id}
        elif user["role"] in ADMIN_ROLES:
            query = {}
        else:
            query = {"assigned_to": user["id"]}
    tasks = await db.tasks.find(query).sort("created_at", -1).to_list(200)

    # Batch-fetch user names for assigned_to
    user_ids = list(set(t.get("assigned_to") for t in tasks if t.get("assigned_to")))
    user_map = {}
    if user_ids:
        try:
            users = await db.users.find(
                {"_id": {"$in": [ObjectId(uid) for uid in user_ids]}},
                {"full_name": 1, "email": 1},
            ).to_list(None)
            user_map = {str(u["_id"]): u.get("full_name", u.get("email", "")) for u in users}
        except Exception:
            pass

    result = []
    app_ids = list(set(t.get("application_id") for t in tasks if t.get("application_id")))
    app_map = {}
    if app_ids:
        apps = await db.applications.find(
            {"_id": {"$in": [ObjectId(aid) for aid in app_ids if ObjectId.is_valid(aid)]}},
            {"intake_type": 1, "current_stage": 1},
        ).to_list(None)
        app_map = {str(a["_id"]): a for a in apps}
    for t in tasks:
        td = _serialize_task(t)
        td["assigned_name"] = user_map.get(td.get("assigned_to"), "")
        app_ctx = app_map.get(td.get("application_id"))
        if app_ctx:
            td["intake_type"] = app_ctx.get("intake_type", "structured_application")
            td["application_stage"] = app_ctx.get("current_stage")
        result.append(td)
    return result


@router.post("")
async def create_task(data: TaskCreate, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    now = datetime.now(timezone.utc)
    intake_type = "structured_application"
    if data.application_id and ObjectId.is_valid(data.application_id):
        app = await db.applications.find_one({"_id": ObjectId(data.application_id)}, {"intake_type": 1})
        intake_type = (app or {}).get("intake_type", intake_type)
    task = {
        "title": data.title,
        "description": data.description,
        "application_id": data.application_id,
        "assigned_to": data.assigned_to or user["id"],
        "due_date": data.due_date,
        "priority": data.priority,
        "visibility": data.visibility,
        "status": "open",
        "created_by": user["id"],
        "created_at": now,
        "intake_type": intake_type,
    }
    result = await db.tasks.insert_one(task)
    task_id = str(result.inserted_id)

    # History entry
    await db.task_history.insert_one({
        "task_id": task_id,
        "action": "created",
        "old_value": None,
        "new_value": "open",
        "actor_id": user["id"],
        "actor_name": user.get("full_name", user.get("email", "")),
        "occurred_at": now,
    })

    response = {k: v for k, v in task.items() if k != "_id"}
    response["id"] = task_id
    for f in ("created_at", "due_date"):
        if response.get(f) and hasattr(response[f], "isoformat"):
            response[f] = response[f].isoformat()
    return response


@router.get("/{task_id}")
async def get_task(task_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    task = await _authorize_task_access(task_id, user, mode="read")
    td = _serialize_task(task)
    # Get assigned user name
    if td.get("assigned_to"):
        try:
            u = await db.users.find_one({"_id": ObjectId(td["assigned_to"])}, {"full_name": 1, "email": 1})
            td["assigned_name"] = u.get("full_name", u.get("email", "")) if u else ""
        except Exception:
            pass
    # Get creator name
    if td.get("created_by"):
        try:
            u = await db.users.find_one({"_id": ObjectId(td["created_by"])}, {"full_name": 1, "email": 1})
            td["created_by_name"] = u.get("full_name", u.get("email", "")) if u else ""
        except Exception:
            pass
    if td.get("application_id") and ObjectId.is_valid(td["application_id"]):
        app = await db.applications.find_one(
            {"_id": ObjectId(td["application_id"])},
            {"intake_type": 1, "current_stage": 1},
        )
        if app:
            td["intake_type"] = app.get("intake_type", "structured_application")
            td["application_stage"] = app.get("current_stage")
    return td


@router.put("/{task_id}")
async def update_task(task_id: str, data: TaskUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    task = await _authorize_task_access(task_id, user, mode="write")

    now = datetime.now(timezone.utc)
    update = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    update["updated_at"] = now
    update["updated_by"] = user["id"]

    # Track status changes in history
    if "status" in update and update["status"] != task.get("status"):
        await db.task_history.insert_one({
            "task_id": task_id,
            "action": "status_changed",
            "old_value": task.get("status"),
            "new_value": update["status"],
            "actor_id": user["id"],
            "actor_name": user.get("full_name", user.get("email", "")),
            "occurred_at": now,
        })

    # Track assignment changes
    if "assigned_to" in update and update["assigned_to"] != task.get("assigned_to"):
        await db.task_history.insert_one({
            "task_id": task_id,
            "action": "reassigned",
            "old_value": task.get("assigned_to"),
            "new_value": update["assigned_to"],
            "actor_id": user["id"],
            "actor_name": user.get("full_name", user.get("email", "")),
            "occurred_at": now,
        })

    # Track priority changes
    if "priority" in update and update["priority"] != task.get("priority"):
        await db.task_history.insert_one({
            "task_id": task_id,
            "action": "priority_changed",
            "old_value": task.get("priority"),
            "new_value": update["priority"],
            "actor_id": user["id"],
            "actor_name": user.get("full_name", user.get("email", "")),
            "occurred_at": now,
        })

    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update})
    updated = await db.tasks.find_one({"_id": ObjectId(task_id)})
    return _serialize_task(updated)


@router.delete("/{task_id}")
async def delete_task(task_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    try:
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    return {"message": "Geloescht"}


# ── Task Notes ──────────────────────────────────────────────────────────────

@router.post("/{task_id}/notes")
async def add_task_note(task_id: str, body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    await _authorize_task_access(task_id, user, mode="write")
    content = body.get("content", "").strip()
    if not content:
        raise HTTPException(status_code=400, detail="Inhalt erforderlich")
    now = datetime.now(timezone.utc)
    note = {
        "task_id": task_id,
        "content": content,
        "author_id": user["id"],
        "author_name": user.get("full_name", user.get("email", "")),
        "created_at": now,
    }
    result = await db.task_notes.insert_one(note)
    await db.task_history.insert_one({
        "task_id": task_id, "action": "note_added",
        "new_value": content[:80], "actor_id": user["id"],
        "actor_name": user.get("full_name", ""), "occurred_at": now,
    })
    return {"id": str(result.inserted_id), "content": content,
            "author_name": note["author_name"], "created_at": now.isoformat()}


@router.get("/{task_id}/notes")
async def list_task_notes(task_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await _authorize_task_access(task_id, user, mode="read")
    notes = await db.task_notes.find({"task_id": task_id}).sort("created_at", -1).to_list(100)
    result = []
    for n in notes:
        nd = to_str_id(n)
        if nd.get("created_at") and hasattr(nd["created_at"], "isoformat"):
            nd["created_at"] = nd["created_at"].isoformat()
        result.append(nd)
    return result


# ── Task Attachments ────────────────────────────────────────────────────────

@router.post("/{task_id}/attachments")
async def upload_task_attachment(task_id: str, body: dict, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
    await _authorize_task_access(task_id, user, mode="write")
    filename = body.get("filename", "")
    file_data = body.get("file_data", "")
    content_type = body.get("content_type", "application/octet-stream")
    if not filename or not file_data:
        raise HTTPException(status_code=400, detail="filename und file_data erforderlich")
    try:
        raw = base64.b64decode(file_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige Base64-Daten")
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Datei zu gross (max 10MB)")
    now = datetime.now(timezone.utc)
    att = {
        "task_id": task_id,
        "filename": filename,
        "content_type": content_type,
        "file_data": file_data,
        "file_size": len(raw),
        "uploaded_by": user["id"],
        "uploaded_by_name": user.get("full_name", user.get("email", "")),
        "uploaded_at": now,
    }
    result = await db.task_attachments.insert_one(att)
    await db.task_history.insert_one({
        "task_id": task_id, "action": "attachment_added",
        "new_value": filename, "actor_id": user["id"],
        "actor_name": user.get("full_name", ""), "occurred_at": now,
    })
    return {"id": str(result.inserted_id), "filename": filename,
            "file_size": len(raw), "content_type": content_type,
            "uploaded_by_name": att["uploaded_by_name"], "uploaded_at": now.isoformat()}


@router.get("/{task_id}/attachments")
async def list_task_attachments(task_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await _authorize_task_access(task_id, user, mode="read")
    atts = await db.task_attachments.find(
        {"task_id": task_id},
        {"file_data": 0}  # Don't return binary data in listing
    ).sort("uploaded_at", -1).to_list(50)
    result = []
    for a in atts:
        ad = to_str_id(a)
        if ad.get("uploaded_at") and hasattr(ad["uploaded_at"], "isoformat"):
            ad["uploaded_at"] = ad["uploaded_at"].isoformat()
        result.append(ad)
    return result


@router.get("/{task_id}/attachments/{att_id}")
async def download_task_attachment(task_id: str, att_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await _authorize_task_access(task_id, user, mode="read")
    try:
        att = await db.task_attachments.find_one({"_id": ObjectId(att_id), "task_id": task_id})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not att:
        raise HTTPException(status_code=404, detail="Anhang nicht gefunden")
    try:
        raw = base64.b64decode(att["file_data"])
    except Exception:
        raise HTTPException(status_code=500, detail="Daten korrumpiert")
    return Response(
        content=raw,
        media_type=att.get("content_type", "application/octet-stream"),
        headers={"Content-Disposition": f'attachment; filename="{att.get("filename", "download")}"'},
    )


# ── Task History ────────────────────────────────────────────────────────────

@router.get("/{task_id}/history")
async def get_task_history(task_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    await _authorize_task_access(task_id, user, mode="read")
    entries = await db.task_history.find({"task_id": task_id}).sort("occurred_at", -1).to_list(100)
    result = []
    for e in entries:
        ed = to_str_id(e)
        if ed.get("occurred_at") and hasattr(ed["occurred_at"], "isoformat"):
            ed["occurred_at"] = ed["occurred_at"].isoformat()
        result.append(ed)
    return result
