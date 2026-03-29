"""
Partner / Sub-Agency Router – Affiliate portal endpoints.

Endpoints:
- GET  /api/partner/dashboard   – Overview stats for the partner
- GET  /api/partner/referrals   – List referred applications
- POST /api/partner/referral-link – Generate referral link
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from deps import get_current_user
from models.schemas import to_str_id

router = APIRouter(prefix="/api/partner", tags=["partner"])

AFFILIATE_ROLES = {"affiliate", "superadmin", "admin"}


def require_affiliate(user: dict):
    if user.get("role") not in AFFILIATE_ROLES:
        raise HTTPException(status_code=403, detail="Nur Partner-/Agentur-Zugang")
    return user


@router.get("/dashboard")
async def partner_dashboard(user: dict = Depends(get_current_user)):
    require_affiliate(user)
    db = get_db()
    uid = user["id"]

    total = await db.applications.count_documents({"referral_code": uid})
    active = await db.applications.count_documents({"referral_code": uid, "current_stage": {"$nin": ["declined", "archived"]}})
    enrolled = await db.applications.count_documents({"referral_code": uid, "current_stage": "enrolled"})

    return {
        "total_referrals": total,
        "active_referrals": active,
        "enrolled": enrolled,
        "partner_name": user.get("full_name", user.get("email")),
        "partner_id": uid,
    }


@router.get("/referrals")
async def list_referrals(user: dict = Depends(get_current_user)):
    require_affiliate(user)
    db = get_db()
    uid = user["id"]

    apps_raw = await db.applications.find(
        {"referral_code": uid},
        {"_id": 1, "applicant_id": 1, "current_stage": 1, "course_type": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(200)

    result = []
    for app in apps_raw:
        a = to_str_id(dict(app))
        # Get applicant name
        if a.get("applicant_id"):
            try:
                from bson import ObjectId
                u = await db.users.find_one({"_id": ObjectId(a["applicant_id"])}, {"full_name": 1, "email": 1, "_id": 0})
                if u:
                    a["applicant_name"] = u.get("full_name", u.get("email", ""))
            except Exception:
                pass
        if isinstance(a.get("created_at"), datetime):
            a["created_at"] = a["created_at"].isoformat()
        result.append(a)

    return result


@router.get("/referral-link")
async def get_referral_link(user: dict = Depends(get_current_user)):
    require_affiliate(user)
    return {
        "referral_code": user["id"],
        "link": f"/apply?ref={user['id']}",
    }
