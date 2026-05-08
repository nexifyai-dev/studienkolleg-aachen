"""
Workspaces router – workspace management (admin only for writes).
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from database import get_db
from deps import get_current_user, require_roles, ADMIN_ROLES
from models.schemas import WorkspaceCreate, to_str_id

router = APIRouter(prefix="/api/workspaces", tags=["workspaces"])


@router.get("")
async def list_workspaces(user: dict = Depends(get_current_user)):
    db = get_db()
    workspaces = await db.workspaces.find({}).to_list(50)
    return [to_str_id(w) for w in workspaces]


@router.post("")
async def create_workspace(data: WorkspaceCreate, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    db = get_db()
    ws = {
        "name": data.name,
        "area": data.area,
        "description": data.description,
        "slug": data.name.lower().replace(" ", "-"),
        "active": True,
        "pipeline_stages": ["lead_new", "qualified", "docs_requested", "docs_received", "completed", "archived"],
        "created_by": user["id"],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.workspaces.insert_one(ws)
    ws["id"] = str(result.inserted_id)
    return ws
