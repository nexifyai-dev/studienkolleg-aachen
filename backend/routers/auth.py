"""
Auth router: login, register, logout, me, refresh, invite, password reset.
Security notes:
- Brute force: 5 failed attempts → 15 min lockout per IP:email combo
- Cookies: httponly=True, secure=COOKIE_SECURE (env-controlled)
- Refresh tokens: 7-day TTL, auto-cleared by MongoDB TTL index
- No token blacklisting (MVP): logout deletes cookies only.
  [KNOWN LIMITATION] Outstanding access tokens remain valid until expiry (60 min max).
  Mitigation: short TTL (60 min) + server-side user.active check on every request.
"""
import secrets
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse

from config import (
    JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_TTL_MINUTES,
    REFRESH_TOKEN_TTL_DAYS, COOKIE_SECURE, COOKIE_SAMESITE, APP_URL
)
from database import get_db
from deps import get_current_user, ADMIN_ROLES
from models.schemas import LoginRequest, RegisterRequest, InviteRequest, ForgotPasswordRequest, ResetPasswordRequest
from services.audit import write_audit_log
from services.email import send_welcome, send_password_reset, send_invite
from bson import ObjectId

router = APIRouter(prefix="/api/auth", tags=["auth"])


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _access_token(user_id: str, email: str, role: str) -> str:
    return jwt.encode(
        {"sub": user_id, "email": email, "role": role, "type": "access",
         "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)},
        JWT_SECRET, algorithm=JWT_ALGORITHM,
    )


def _refresh_token(user_id: str) -> str:
    return jwt.encode(
        {"sub": user_id, "type": "refresh",
         "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_TTL_DAYS)},
        JWT_SECRET, algorithm=JWT_ALGORITHM,
    )


def _set_auth_cookies(response: JSONResponse, access: str, refresh: str):
    """Attach auth cookies with consistent security settings."""
    common = dict(httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE, path="/")
    response.set_cookie("access_token", access, max_age=ACCESS_TOKEN_TTL_MINUTES * 60, **common)
    response.set_cookie("refresh_token", refresh, max_age=REFRESH_TOKEN_TTL_DAYS * 86400, **common)


JsonResponseType = JSONResponse


# ─── Login ────────────────────────────────────────────────────────────────────
@router.post("/login")
async def login(data: LoginRequest, request: Request):
    db = get_db()
    email = data.email.lower().strip()
    client_ip = request.headers.get("X-Forwarded-For", "")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host
    else:
        client_ip = "unknown"
    identifier = f"{client_ip}:{email}"

    # Brute force check
    attempts = await db.login_attempts.find_one({"identifier": identifier})
    if attempts and attempts.get("count", 0) >= 5:
        lockout = attempts.get("locked_until")
        if lockout:
            # Ensure timezone-aware comparison
            if lockout.tzinfo is None:
                from datetime import timezone as tz
                lockout = lockout.replace(tzinfo=tz.utc)
            if lockout > datetime.now(timezone.utc):
                raise HTTPException(status_code=429, detail="Zu viele Versuche. Bitte in 15 Minuten erneut versuchen.")

    user = await db.users.find_one({"email": email})
    if not user or not user.get("password_hash") or not _verify(data.password, user["password_hash"]):
        count = (attempts.get("count", 0) + 1) if attempts else 1
        await db.login_attempts.update_one(
            {"identifier": identifier},
            {"$set": {
                "identifier": identifier,
                "count": count,
                "last_attempt": datetime.now(timezone.utc),
                "locked_until": (
                    datetime.now(timezone.utc) + timedelta(minutes=15) if count >= 5 else None
                ),
            }},
            upsert=True,
        )
        raise HTTPException(status_code=401, detail="Ungültige E-Mail oder Passwort")

    if not user.get("active", True):
        raise HTTPException(status_code=403, detail="Konto ist deaktiviert")

    await db.login_attempts.delete_one({"identifier": identifier})

    user_id = str(user["_id"])
    access = _access_token(user_id, email, user["role"])
    refresh = _refresh_token(user_id)
    await write_audit_log("user_login", user_id, "user", user_id)

    resp = JSONResponse(content={
        "id": user_id, "email": email, "full_name": user.get("full_name"),
        "role": user.get("role"), "language_pref": user.get("language_pref", "de"),
    })
    _set_auth_cookies(resp, access, refresh)
    return resp


# ─── Register ─────────────────────────────────────────────────────────────────
@router.post("/register")
async def register(data: RegisterRequest):
    db = get_db()
    email = data.email.lower().strip()

    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 8 Zeichen haben")

    role = "applicant"
    organization_id = None
    workspace_id = None

    if data.invite_token:
        invite = await db.invite_tokens.find_one({
            "token": data.invite_token,
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)},
        })
        if not invite:
            raise HTTPException(status_code=400, detail="Ungültiger oder abgelaufener Einladungslink")
        invite_email = invite.get("email", "").lower()
        if invite_email and invite_email != email:
            raise HTTPException(status_code=400, detail="E-Mail stimmt nicht mit der Einladung überein")
        role = invite.get("role", "applicant")
        organization_id = invite.get("organization_id")
        workspace_id = invite.get("workspace_id")

    existing = await db.users.find_one({"email": email})
    if existing:
        if existing.get("password_hash"):
            raise HTTPException(status_code=409, detail="E-Mail bereits registriert. Bitte anmelden.")
        # Lead-Claiming: user was created by lead ingest (no password)
        hashed = _hash(data.password)
        await db.users.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "password_hash": hashed,
                "full_name": data.full_name or existing.get("full_name"),
                "role": role,
                "active": True,
                "claimed_at": datetime.now(timezone.utc),
            }},
        )
        user_id = str(existing["_id"])
        if workspace_id:
            mem = await db.workspace_members.find_one({"user_id": user_id, "workspace_id": workspace_id})
            if not mem:
                await db.workspace_members.insert_one({
                    "user_id": user_id, "workspace_id": workspace_id,
                    "role": role, "status": "active", "joined_at": datetime.now(timezone.utc),
                })
        if data.invite_token:
            await db.invite_tokens.update_one({"token": data.invite_token}, {"$set": {"used": True, "used_by": user_id}})
        await write_audit_log("user_claimed", user_id, "user", user_id, {"role": role})
        send_welcome(email, data.full_name or existing.get("full_name", ""))
        access = _access_token(user_id, email, role)
        refresh = _refresh_token(user_id)
        resp = JSONResponse(content={"id": user_id, "email": email, "full_name": data.full_name, "role": role})
        _set_auth_cookies(resp, access, refresh)
        return resp

    # Fresh registration
    user_doc = {
        "email": email,
        "password_hash": _hash(data.password),
        "full_name": data.full_name,
        "role": role,
        "language_pref": "de",
        "active": True,
        "organization_id": organization_id,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    if data.invite_token:
        await db.invite_tokens.update_one({"token": data.invite_token}, {"$set": {"used": True, "used_by": user_id}})
    if workspace_id:
        await db.workspace_members.insert_one({
            "user_id": user_id, "workspace_id": workspace_id,
            "role": role, "status": "active", "joined_at": datetime.now(timezone.utc),
        })

    await write_audit_log("user_register", user_id, "user", user_id, {"role": role})
    send_welcome(email, data.full_name)

    access = _access_token(user_id, email, role)
    refresh = _refresh_token(user_id)
    resp = JSONResponse(content={"id": user_id, "email": email, "full_name": data.full_name, "role": role})
    _set_auth_cookies(resp, access, refresh)
    return resp


# ─── Logout ──────────────────────────────────────────────────────────────────
@router.post("/logout")
async def logout(user: dict = Depends(get_current_user)):
    await write_audit_log("user_logout", user["id"], "user", user["id"])
    resp = JSONResponse(content={"message": "Abgemeldet"})
    resp.delete_cookie("access_token", path="/")
    resp.delete_cookie("refresh_token", path="/")
    return resp


# ─── Me ───────────────────────────────────────────────────────────────────────
@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user


# ─── Token Refresh ────────────────────────────────────────────────────────────
@router.post("/refresh")
async def refresh(request: Request):
    db = get_db()
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Kein Refresh-Token")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Ungültiger Token-Typ")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user or not user.get("active", True):
            raise HTTPException(status_code=401, detail="Nutzer nicht gefunden oder deaktiviert")
        user_id = str(user["_id"])
        new_access = _access_token(user_id, user["email"], user["role"])
        resp = JSONResponse(content={"message": "Token refreshed"})
        resp.set_cookie("access_token", new_access,
                        max_age=ACCESS_TOKEN_TTL_MINUTES * 60,
                        httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE, path="/")
        return resp
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh-Token abgelaufen. Bitte neu anmelden.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ungültiger Refresh-Token")


# ─── Invite ──────────────────────────────────────────────────────────────────
@router.post("/invite")
async def create_invite(data: InviteRequest, user: dict = Depends(get_current_user)):
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Nur Admins können einladen")

    db = get_db()
    token = secrets.token_urlsafe(32)
    await db.invite_tokens.insert_one({
        "token": token,
        "email": data.email.lower().strip(),
        "full_name": data.full_name,
        "role": data.role,
        "workspace_id": data.workspace_id,
        "organization_id": data.organization_id,
        "created_by": user["id"],
        "used": False,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc),
    })
    invite_url = f"{APP_URL}/auth/register?token={token}"
    send_invite(data.email, data.full_name, invite_url, data.role)
    await write_audit_log("invite_created", user["id"], "invite", token, {"email": data.email, "role": data.role})
    return {"token": token, "invite_url": invite_url, "email": data.email}


# ─── Forgot / Reset Password ──────────────────────────────────────────────────
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    db = get_db()
    email = data.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if user:
        token = secrets.token_urlsafe(32)
        await db.password_reset_tokens.insert_one({
            "token": token, "user_id": str(user["_id"]), "used": False,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "created_at": datetime.now(timezone.utc),
        })
        reset_url = f"{APP_URL}/auth/reset-password?token={token}"
        sent = send_password_reset(email, reset_url)
        if not sent:
            import logging; logging.getLogger(__name__).info(f"[RESET] {email}: {reset_url}")
    # Always return same response (no user enumeration)
    return {"message": "Wenn diese E-Mail existiert, wurde ein Reset-Link gesendet"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    db = get_db()
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Passwort muss mindestens 8 Zeichen haben")
    record = await db.password_reset_tokens.find_one({
        "token": data.token, "used": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)},
    })
    if not record:
        raise HTTPException(status_code=400, detail="Ungültiger oder abgelaufener Reset-Token")
    await db.users.update_one(
        {"_id": ObjectId(record["user_id"])},
        {"$set": {"password_hash": _hash(data.new_password), "updated_at": datetime.now(timezone.utc)}},
    )
    await db.password_reset_tokens.update_one({"token": data.token}, {"$set": {"used": True}})
    await write_audit_log("password_reset", record["user_id"], "user", record["user_id"])
    return {"message": "Passwort erfolgreich aktualisiert"}
