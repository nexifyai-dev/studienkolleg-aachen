"""
Tasks router.

Security notes:
- Applicants see only public tasks linked to their applications
- Staff/admin can create/update all tasks
- Update: ownership check – staff can only modify tasks in their scope
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, STAFF_ROLES, ADMIN_ROLES
from models.schemas import TaskCreate, TaskUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


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
        else:
            # Staff sees tasks assigned to them OR all if admin
            if user["role"] in ADMIN_ROLES:
                query = {}
            else:
                query = {"assigned_to": user["id"]}
    tasks = await db.tasks.find(query).sort("created_at", -1).to_list(200)
    return [to_str_id(t) for t in tasks]


@router.post("")
async def create_task(data: TaskCreate, user: dict = Depends(require_roles(*STAFF_ROLES))):
    db = get_db()
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
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.tasks.insert_one(task)
    # Serialize response - remove _id (added by insert_one) and convert datetime
    response = {k: v for k, v in task.items() if k != "_id"}
    response["id"] = str(result.inserted_id)
    if response.get("created_at") and hasattr(response["created_at"], "isoformat"):
        response["created_at"] = response["created_at"].isoformat()
    if response.get("due_date") and hasattr(response["due_date"], "isoformat"):
        response["due_date"] = response["due_date"].isoformat()
    return response


@router.put("/{task_id}")
async def update_task(task_id: str, data: TaskUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not task:
        raise HTTPException(status_code=404, detail="Aufgabe nicht gefunden")

    # Ownership check: applicants cannot update tasks; staff only assigned tasks unless admin
    if user["role"] == "applicant":
        raise HTTPException(status_code=403, detail="Forbidden")
    if user["role"] not in ADMIN_ROLES:
        if task.get("assigned_to") != user["id"] and task.get("created_by") != user["id"]:
            raise HTTPException(status_code=403, detail="Nur der Ersteller oder zugewiesene Person kann diese Aufgabe bearbeiten")

    update = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    update["updated_at"] = datetime.now(timezone.utc)
    update["updated_by"] = user["id"]
    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update})
    return {"message": "Aktualisiert"}
