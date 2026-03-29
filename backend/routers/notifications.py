"""
Notification router – In-App notifications for all roles.

Endpoints:
- GET  /api/notifications          – list user's notifications (paginated, filterable)
- GET  /api/notifications/unread-count – unread count for badge
- PATCH /api/notifications/{id}/read  – mark single as read
- PATCH /api/notifications/read-all   – mark all as read
"""
from fastapi import APIRouter, Depends, Query
from bson import ObjectId
from database import get_db
from deps import get_current_user
from models.schemas import to_str_id

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(30, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    """List notifications for the current user, newest first."""
    db = get_db()
    query = {"recipient_id": user["id"]}
    if unread_only:
        query["read"] = False

    notifs = await db.notifications.find(query).sort("created_at", -1).to_list(limit)
    return [to_str_id(n) for n in notifs]


@router.get("/unread-count")
async def unread_count(user: dict = Depends(get_current_user)):
    """Return the number of unread notifications for badge display."""
    db = get_db()
    count = await db.notifications.count_documents({"recipient_id": user["id"], "read": False})
    return {"count": count}


@router.patch("/{notif_id}/read")
async def mark_read(notif_id: str, user: dict = Depends(get_current_user)):
    """Mark a single notification as read."""
    db = get_db()
    result = await db.notifications.update_one(
        {"_id": ObjectId(notif_id), "recipient_id": user["id"]},
        {"$set": {"read": True}},
    )
    if result.matched_count == 0:
        return {"status": "not_found"}
    return {"status": "ok"}


@router.patch("/read-all")
async def mark_all_read(user: dict = Depends(get_current_user)):
    """Mark all notifications as read for the current user."""
    db = get_db()
    result = await db.notifications.update_many(
        {"recipient_id": user["id"], "read": False},
        {"$set": {"read": True}},
    )
    return {"status": "ok", "updated": result.modified_count}
