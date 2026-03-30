"""
Users router – profile management.

Security notes:
- Users can only update their own profile
- Admin-only fields (role, active) are explicitly gated
- Password is never returned in any response
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES
from models.schemas import UserUpdate, UsersBulkActiveUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/users", tags=["users"])

# Fields a user may update on their own profile
SELF_EDITABLE = frozenset(["full_name", "phone", "country", "language_pref", "avatar_url", "bio"])
# Additional fields only admins may set
ADMIN_EDITABLE = SELF_EDITABLE | frozenset(["role", "active"])


@router.get("")
async def list_users(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    db = get_db()
    users = await db.users.find({}, {"password_hash": 0}).to_list(500)
    return [to_str_id(u) for u in users]


@router.put("/bulk/active")
async def bulk_set_active(
    data: UsersBulkActiveUpdate,
    current_user: dict = Depends(require_roles(*ADMIN_ROLES)),
):
    user_ids = [uid for uid in data.user_ids if uid and uid != current_user["id"]]
    if not user_ids:
        raise HTTPException(status_code=400, detail="Keine gültigen Zielnutzer")

    object_ids = []
    for uid in user_ids:
        try:
            object_ids.append(ObjectId(uid))
        except Exception:
            raise HTTPException(status_code=400, detail=f"Ungültige ID: {uid}")

    db = get_db()
    users = await db.users.find(
        {"_id": {"$in": object_ids}},
        {"_id": 1, "role": 1},
    ).to_list(len(object_ids))
    superadmin_ids = {str(u["_id"]) for u in users if u.get("role") == "superadmin"}
    allowed_ids = [oid for oid in object_ids if str(oid) not in superadmin_ids]
    if not allowed_ids:
        raise HTTPException(status_code=400, detail="Keine änderbaren Nutzer im Batch")

    result = await db.users.update_many(
        {"_id": {"$in": allowed_ids}},
        {"$set": {"active": data.active, "updated_at": datetime.now(timezone.utc)}},
    )
    for user_id in [str(oid) for oid in allowed_ids]:
        await write_audit_log(
            "user_bulk_active_changed",
            current_user["id"],
            "user",
            user_id,
            {"active": data.active},
        )

    return {
        "message": "Batch-Update durchgeführt",
        "requested": len(user_ids),
        "updated": result.modified_count,
        "skipped_superadmin": len(superadmin_ids),
        "skipped_self": len(data.user_ids) - len(user_ids),
    }


@router.get("/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # Own profile OR staff/admin
    if current_user["id"] != user_id and current_user["role"] not in (ADMIN_ROLES | STAFF_ROLES):
        raise HTTPException(status_code=403, detail="Forbidden")
    db = get_db()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not user:
        raise HTTPException(status_code=404, detail="Nutzer nicht gefunden")
    return to_str_id(user)


@router.put("/{user_id}")
async def update_user(user_id: str, data: UserUpdate, current_user: dict = Depends(get_current_user)):
    # Only self or admin
    is_self = current_user["id"] == user_id
    is_admin = current_user["role"] in ADMIN_ROLES
    if not is_self and not is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")

    allowed = ADMIN_EDITABLE if is_admin else SELF_EDITABLE
    update = {k: v for k, v in data.model_dump(exclude_none=True).items() if k in allowed}
    if not update:
        raise HTTPException(status_code=400, detail="Keine gültigen Felder")

    update["updated_at"] = datetime.now(timezone.utc)
    db = get_db()
    try:
        await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    await write_audit_log("user_updated", current_user["id"], "user", user_id, {"fields": list(update.keys())})
    return {"message": "Aktualisiert"}

