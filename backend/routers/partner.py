"""
Partner / Sub-Agency Router – Affiliate portal endpoints.

Endpoints:
- GET  /api/partner/dashboard       – Overview stats + Provisions-Zusammenfassung
- GET  /api/partner/referrals       – List referred applications
- GET  /api/partner/commissions     – Detaillierte Provisionsabrechnung
- GET  /api/partner/commission-summary – Aggregierte Provisionsuebersicht
- POST /api/partner/referral-link   – Generate referral link
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from database import get_db
from deps import get_current_user
from models.schemas import to_str_id

router = APIRouter(prefix="/api/partner", tags=["partner"])

AFFILIATE_ROLES = {"affiliate", "agency_admin", "agency_agent", "superadmin", "admin"}

COMMISSION_RATES = {
    "T-Course": 500.0,
    "M-Course": 500.0,
    "W-Course": 400.0,
    "default": 350.0,
}

COMMISSION_STAGES = {
    "enrolled": "earned",
    "paid_deposit": "earned",
    "completed": "earned",
}


def require_affiliate(user: dict):
    if user.get("role") not in AFFILIATE_ROLES:
        raise HTTPException(status_code=403, detail="Nur Partner-/Agentur-Zugang")
    return user


def _calc_commission(course_type, stage):
    """Berechnet Provision basierend auf Kurstyp und Bewerbungsstatus."""
    rate = COMMISSION_RATES.get(course_type, COMMISSION_RATES["default"])
    status = COMMISSION_STAGES.get(stage, "pending")
    return rate, status


@router.get("/dashboard")
async def partner_dashboard(user: dict = Depends(get_current_user)):
    require_affiliate(user)
    db = get_db()
    uid = user["id"]

    total = await db.applications.count_documents({"referral_code": uid})
    active = await db.applications.count_documents({"referral_code": uid, "current_stage": {"$nin": ["declined", "archived"]}})
    enrolled = await db.applications.count_documents({"referral_code": uid, "current_stage": "enrolled"})

    # Provisions-Berechnung
    apps = await db.applications.find(
        {"referral_code": uid},
        {"course_type": 1, "current_stage": 1}
    ).to_list(500)

    earned = 0.0
    pending = 0.0
    for app in apps:
        rate, status = _calc_commission(app.get("course_type"), app.get("current_stage"))
        if status == "earned":
            earned += rate
        elif app.get("current_stage") not in ("declined", "archived"):
            pending += rate

    # Ausbezahlte Provisionen
    paid = 0.0
    payouts = await db.partner_payouts.find(
        {"partner_id": uid, "status": "paid"}, {"amount": 1}
    ).to_list(500)
    for p in payouts:
        paid += p.get("amount", 0)

    return {
        "total_referrals": total,
        "active_referrals": active,
        "enrolled": enrolled,
        "partner_name": user.get("full_name", user.get("email")),
        "partner_id": uid,
        "commissions": {
            "earned": round(earned, 2),
            "pending": round(pending, 2),
            "paid": round(paid, 2),
            "balance": round(earned - paid, 2),
        },
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
        if a.get("applicant_id"):
            try:
                u = await db.users.find_one({"_id": ObjectId(a["applicant_id"])}, {"full_name": 1, "email": 1, "_id": 0})
                if u:
                    a["applicant_name"] = u.get("full_name", u.get("email", ""))
            except Exception:
                pass
        # Provision pro Referral berechnen
        rate, status = _calc_commission(a.get("course_type"), a.get("current_stage"))
        a["commission"] = {"amount": rate, "status": status}
        if isinstance(a.get("created_at"), datetime):
            a["created_at"] = a["created_at"].isoformat()
        result.append(a)

    return result


@router.get("/commissions")
async def list_commissions(user: dict = Depends(get_current_user)):
    """Detaillierte Provisionsabrechnung: Jede Bewerbung mit Provisionsstatus."""
    require_affiliate(user)
    db = get_db()
    uid = user["id"]

    apps = await db.applications.find(
        {"referral_code": uid},
        {"_id": 1, "applicant_id": 1, "current_stage": 1, "course_type": 1, "created_at": 1, "enrolled_at": 1}
    ).sort("created_at", -1).to_list(500)

    commissions = []
    for app in apps:
        a = to_str_id(dict(app))
        rate, status = _calc_commission(a.get("course_type"), a.get("current_stage"))
        name = ""
        if a.get("applicant_id"):
            try:
                u = await db.users.find_one({"_id": ObjectId(a["applicant_id"])}, {"full_name": 1, "_id": 0})
                name = u.get("full_name", "") if u else ""
            except Exception:
                pass
        commissions.append({
            "application_id": a["id"],
            "applicant_name": name,
            "course_type": a.get("course_type", ""),
            "stage": a.get("current_stage", ""),
            "commission_amount": rate,
            "commission_status": status,
            "created_at": a["created_at"].isoformat() if isinstance(a.get("created_at"), datetime) else a.get("created_at"),
            "enrolled_at": a["enrolled_at"].isoformat() if isinstance(a.get("enrolled_at"), datetime) else a.get("enrolled_at"),
        })

    return commissions


@router.get("/commission-summary")
async def commission_summary(user: dict = Depends(get_current_user)):
    """Aggregierte Provisionsuebersicht pro Monat."""
    require_affiliate(user)
    db = get_db()
    uid = user["id"]

    apps = await db.applications.find(
        {"referral_code": uid},
        {"course_type": 1, "current_stage": 1, "created_at": 1}
    ).to_list(500)

    monthly = {}
    total_earned = 0.0
    total_pending = 0.0
    for app in apps:
        rate, status = _calc_commission(app.get("course_type"), app.get("current_stage"))
        created = app.get("created_at")
        if isinstance(created, datetime):
            key = created.strftime("%Y-%m")
        else:
            key = "unbekannt"
        if key not in monthly:
            monthly[key] = {"month": key, "referrals": 0, "earned": 0.0, "pending": 0.0}
        monthly[key]["referrals"] += 1
        if status == "earned":
            monthly[key]["earned"] += rate
            total_earned += rate
        elif app.get("current_stage") not in ("declined", "archived"):
            monthly[key]["pending"] += rate
            total_pending += rate

    return {
        "by_month": sorted(monthly.values(), key=lambda x: x["month"], reverse=True),
        "totals": {
            "earned": round(total_earned, 2),
            "pending": round(total_pending, 2),
        },
        "rates": COMMISSION_RATES,
    }


@router.get("/referral-link")
async def get_referral_link(user: dict = Depends(get_current_user)):
    require_affiliate(user)
    return {
        "referral_code": user["id"],
        "link": f"/apply?ref={user['id']}",
    }
