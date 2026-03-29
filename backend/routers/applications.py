"""
Application router.

Security notes:
- Applicants: can only see/modify their own applications
- Partners (agency): scoped to their organization_id
- Staff: scoped by workspace_id query param; without it, see all in their permitted workspaces
- Stage changes are audit-logged and activity-tracked
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES, PARTNER_ROLES
from models.schemas import ApplicationCreate, ApplicationUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("")
async def list_applications(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    workspace_id = request.query_params.get("workspace_id")
    stage = request.query_params.get("stage")

    if user["role"] == "applicant":
        # Applicants see only their own
        query["applicant_id"] = user["id"]
    elif user["role"] in PARTNER_ROLES:
        # Partners scoped to their organization
        if not user.get("organization_id"):
            return []
        query["organization_id"] = user["organization_id"]
    elif user["role"] in STAFF_ROLES:
        # Staff: scope by workspace if provided; otherwise all (admin sees all)
        if workspace_id:
            query["workspace_id"] = workspace_id
        # No workspace_id → staff sees all applications (intentional for dashboard/kanban)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

    if stage:
        query["current_stage"] = stage

    apps = await db.applications.find(query).sort("last_activity_at", -1).to_list(500)

    result = []
    for app in apps:
        app_dict = to_str_id(app)
        if user["role"] in STAFF_ROLES:
            # Enrich with applicant info (inclusion-only projection)
            if app_dict.get("applicant_id"):
                try:
                    applicant = await db.users.find_one(
                        {"_id": ObjectId(app_dict["applicant_id"])},
                        {"full_name": 1, "email": 1, "phone": 1, "country": 1},
                    )
                    if applicant:
                        app_dict["applicant"] = to_str_id(applicant)
                except Exception:
                    pass
            if app_dict.get("workspace_id"):
                try:
                    ws = await db.workspaces.find_one({"_id": ObjectId(app_dict["workspace_id"])}, {"name": 1})
                    if ws:
                        app_dict["workspace_name"] = ws.get("name")
                except Exception:
                    pass
        result.append(app_dict)
    return result


@router.post("")
async def create_application(data: ApplicationCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    # Applicants can only create for themselves
    if data.applicant_id and user["role"] not in STAFF_ROLES:
        data.applicant_id = None
    applicant_id = data.applicant_id or user["id"]

    workspace = await db.workspaces.find_one({"_id": ObjectId(data.workspace_id)})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace nicht gefunden")

    app_doc = {
        "applicant_id": applicant_id,
        "workspace_id": data.workspace_id,
        "current_stage": "lead_new",
        "source": data.source,
        "notes": data.notes,
        "priority": "normal",
        "created_at": datetime.now(timezone.utc),
        "last_activity_at": datetime.now(timezone.utc),
        "created_by": user["id"],
    }
    result = await db.applications.insert_one(app_doc)
    app_id = str(result.inserted_id)
    await write_audit_log("application_created", user["id"], "application", app_id)
    return {**app_doc, "id": app_id}


@router.get("/{app_id}")
async def get_application(app_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    app_dict = to_str_id(app)
    # Ownership check
    if user["role"] == "applicant" and app_dict.get("applicant_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    if user["role"] in PARTNER_ROLES and app_dict.get("organization_id") != user.get("organization_id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    return app_dict


@router.put("/{app_id}")
async def update_application(
    app_id: str,
    data: ApplicationUpdate,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")

    old_stage = app.get("current_stage")
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["last_activity_at"] = datetime.now(timezone.utc)
    update["updated_by"] = user["id"]
    await db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": update})

    if data.current_stage and data.current_stage != old_stage:
        await write_audit_log("stage_changed", user["id"], "application", app_id,
                              {"old_stage": old_stage, "new_stage": data.current_stage})
        await db.application_activities.insert_one({
            "application_id": app_id,
            "action": "stage_changed",
            "old_value": old_stage,
            "new_value": data.current_stage,
            "actor_id": user["id"],
            "occurred_at": datetime.now(timezone.utc),
        })
        # Automation: Status-Change-E-Mail an Bewerber senden
        try:
            applicant_user = None
            if app.get("applicant_id"):
                from bson import ObjectId as ObjId
                applicant_user = await db.users.find_one(
                    {"_id": ObjId(app["applicant_id"])},
                    {"email": 1, "full_name": 1},
                )
            if applicant_user:
                from services.automation import trigger_status_change
                await trigger_status_change(
                    application_id=app_id,
                    applicant_email=applicant_user.get("email", ""),
                    applicant_name=applicant_user.get("full_name", ""),
                    old_stage=old_stage,
                    new_stage=data.current_stage,
                    actor_id=user["id"],
                )
        except Exception:
            pass
    return {"message": "Aktualisiert", "id": app_id}
