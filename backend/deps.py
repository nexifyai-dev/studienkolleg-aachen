"""
Shared dependencies: auth, role enforcement.
"""
import jwt
from fastapi import Request, HTTPException, Depends
from bson import ObjectId
from database import get_db
from config import JWT_SECRET, JWT_ALGORITHM

# ─── Role groups ─────────────────────────────────────────────────────────────
ADMIN_ROLES = frozenset(["superadmin", "admin"])
STAFF_ROLES = frozenset(["superadmin", "admin", "staff", "accounting_staff"])
PARTNER_ROLES = frozenset(["agency_admin", "agency_agent", "affiliate"])
ALL_PORTAL_ROLES = frozenset(["applicant", "agency_admin", "agency_agent", "affiliate"])


async def get_current_user(request: Request) -> dict:
    """Extract and validate JWT from cookie or Authorization header."""
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.get("active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user["id"] = str(user.pop("_id"))
    user.pop("password_hash", None)
    return user


def require_roles(*roles):
    """Dependency factory that restricts access to specific roles."""
    role_set = frozenset(roles)

    async def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in role_set:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return checker


def require_self_or_roles(user_id_param: str, *admin_roles):
    """Allow access if user is accessing their own resource OR has an admin role."""
    admin_set = frozenset(admin_roles)

    async def checker(request: Request, user: dict = Depends(get_current_user)):
        target_id = request.path_params.get(user_id_param)
        if user["id"] != target_id and user.get("role") not in admin_set:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return checker
