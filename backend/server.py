from dotenv import load_dotenv
load_dotenv()

import os
import bcrypt
import jwt
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Any
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Config ──────────────────────────────────────────────────────────────────
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@studienkolleg-aachen.de")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin@2026!")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
APP_URL = os.environ.get("APP_URL", "http://localhost:8001")

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="W2G Platform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── DB ──────────────────────────────────────────────────────────────────────
client: AsyncIOMotorClient = None
db = None

def get_db():
    return db

# ─── Helpers ─────────────────────────────────────────────────────────────────
def to_str_id(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id, "email": email, "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["id"] = str(user.pop("_id"))
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_roles(*roles):
    async def checker(user: dict = Depends(get_current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker

ADMIN_ROLES = ["superadmin", "admin"]
STAFF_ROLES = ["superadmin", "admin", "staff", "accounting_staff"]
ALL_INTERNAL = ["superadmin", "admin", "staff", "accounting_staff"]
PARTNER_ROLES = ["agency_admin", "agency_agent", "affiliate"]

async def write_audit_log(action: str, actor_id: str, target_type: str, target_id: str, details: dict = None):
    try:
        await db.audit_logs.insert_one({
            "action": action,
            "actor_id": actor_id,
            "target_type": target_type,
            "target_id": target_id,
            "details": details or {},
            "occurred_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.error(f"Audit log write failed: {e}")

# ─── Pydantic Models ──────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "applicant"
    invite_token: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class InviteRequest(BaseModel):
    email: str
    full_name: str
    role: str
    workspace_id: Optional[str] = None
    organization_id: Optional[str] = None

class ApplicationCreate(BaseModel):
    applicant_id: Optional[str] = None
    workspace_id: str
    source: str = "direct"
    notes: Optional[str] = None

class ApplicationUpdate(BaseModel):
    current_stage: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None

class DocumentStatusUpdate(BaseModel):
    status: str
    rejection_reason: Optional[str] = None
    comment: Optional[str] = None

class LeadIngest(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    country: Optional[str] = None
    area_interest: str = "studienkolleg"
    desired_start: Optional[str] = None
    language_level: Optional[str] = None
    notes: Optional[str] = None
    source: str = "website_form"
    referral_code: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    application_id: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "normal"
    visibility: str = "internal"

class WorkspaceCreate(BaseModel):
    name: str
    area: str
    description: Optional[str] = None

class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    recipient_id: Optional[str] = None
    application_id: Optional[str] = None
    content: str
    visibility: str = "public"

class ConsentCapture(BaseModel):
    consent_type: str
    version: str = "1.0"
    granted: bool = True

# ─── Startup / Seed ───────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    # Indexes
    await db.users.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.invite_tokens.create_index("token", unique=True)
    await db.applications.create_index("applicant_id")
    await db.applications.create_index("workspace_id")
    await db.audit_logs.create_index("occurred_at")
    await db.audit_logs.create_index("actor_id")
    await db.webhook_events.create_index("event_id", unique=True, sparse=True)

    # Seed workspaces
    await seed_workspaces()
    # Seed admin
    await seed_admin()
    logger.info("W2G Platform API started successfully")

@app.on_event("shutdown")
async def shutdown():
    if client:
        client.close()

async def seed_workspaces():
    workspaces = [
        {"slug": "studienkolleg", "name": "Studienkolleg Aachen", "area": "studienkolleg", "active": True,
         "pipeline_stages": ["lead_new","contacted","docs_requested","docs_received","docs_review",
                             "invoice_open","payment_received","process_next","completed","dormant","archived"],
         "created_at": datetime.now(timezone.utc)},
        {"slug": "sprachkurse", "name": "Sprachkurse", "area": "language_courses", "active": True,
         "pipeline_stages": ["lead_new","interested","enrolled","active","completed","archived"],
         "created_at": datetime.now(timezone.utc)},
        {"slug": "pflege", "name": "Pflegefachschule", "area": "nursing", "active": False,
         "pipeline_stages": ["lead_new","qualified","docs_submitted","enrolled","completed","archived"],
         "created_at": datetime.now(timezone.utc)},
        {"slug": "arbeit", "name": "Arbeit & Ausbildung", "area": "work_training", "active": False,
         "pipeline_stages": ["lead_new","qualified","docs_submitted","matched","completed","archived"],
         "created_at": datetime.now(timezone.utc)},
    ]
    for ws in workspaces:
        existing = await db.workspaces.find_one({"slug": ws["slug"]})
        if not existing:
            await db.workspaces.insert_one(ws)

async def seed_admin():
    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if existing is None:
        hashed = hash_password(ADMIN_PASSWORD)
        await db.users.insert_one({
            "email": ADMIN_EMAIL,
            "password_hash": hashed,
            "full_name": "System Admin",
            "role": "superadmin",
            "language_pref": "de",
            "active": True,
            "created_at": datetime.now(timezone.utc),
        })
        logger.info(f"Admin seeded: {ADMIN_EMAIL}")
    elif not verify_password(ADMIN_PASSWORD, existing.get("password_hash", "")):
        await db.users.update_one(
            {"email": ADMIN_EMAIL},
            {"$set": {"password_hash": hash_password(ADMIN_PASSWORD)}}
        )
        logger.info("Admin password updated")

# ─── Auth Routes ──────────────────────────────────────────────────────────────
@app.post("/api/auth/login")
async def login(data: LoginRequest, response: JSONResponse = None, request: Request = None):
    from fastapi.responses import JSONResponse as JR
    email = data.email.lower().strip()
    
    # Brute force check
    identifier = f"{request.client.host if request else 'unknown'}:{email}"
    attempts = await db.login_attempts.find_one({"identifier": identifier})
    if attempts and attempts.get("count", 0) >= 5:
        lockout_until = attempts.get("locked_until")
        if lockout_until and lockout_until > datetime.now(timezone.utc):
            raise HTTPException(status_code=429, detail="Account temporarily locked. Please try again later.")
    
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(data.password, user.get("password_hash", "")):
        # Increment failed attempts
        await db.login_attempts.update_one(
            {"identifier": identifier},
            {"$inc": {"count": 1}, "$set": {"last_attempt": datetime.now(timezone.utc),
             "locked_until": datetime.now(timezone.utc) + timedelta(minutes=15) if (attempts and attempts.get("count",0) >= 4) else None}},
            upsert=True
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.get("active", True):
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Clear failed attempts
    await db.login_attempts.delete_one({"identifier": identifier})
    
    user_id = str(user["_id"])
    access_token = create_access_token(user_id, email, user["role"])
    refresh_token = create_refresh_token(user_id)
    
    await write_audit_log("user_login", user_id, "user", user_id)
    
    resp_data = {
        "id": user_id, "email": email, "full_name": user.get("full_name"),
        "role": user.get("role"), "language_pref": user.get("language_pref", "de"),
    }
    resp = JR(content=resp_data)
    resp.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return resp

@app.post("/api/auth/register")
async def register(data: RegisterRequest, request: Request):
    from fastapi.responses import JSONResponse as JR
    email = data.email.lower().strip()
    
    # Validate invite token if role is not applicant
    organization_id = None
    workspace_id = None
    role = "applicant"
    
    if data.invite_token:
        invite = await db.invite_tokens.find_one({
            "token": data.invite_token,
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        if not invite:
            raise HTTPException(status_code=400, detail="Invalid or expired invite token")
        role = invite.get("role", "applicant")
        organization_id = invite.get("organization_id")
        workspace_id = invite.get("workspace_id")
        email_from_invite = invite.get("email", "").lower()
        if email_from_invite and email_from_invite != email:
            raise HTTPException(status_code=400, detail="Email does not match invite")
    
    existing = await db.users.find_one({"email": email})
    if existing:
        # If existing user was created by lead ingest (no password), allow claiming account
        if existing.get("password_hash"):
            raise HTTPException(status_code=409, detail="Email bereits registriert. Bitte melde dich an.")
        # Lead record without password: claim the account
        hashed = hash_password(data.password)
        await db.users.update_one(
            {"_id": existing["_id"]},
            {"$set": {"password_hash": hashed, "full_name": data.full_name or existing.get("full_name"),
                      "role": role, "active": True, "claimed_at": datetime.now(timezone.utc)}}
        )
        user_id = str(existing["_id"])
        if workspace_id:
            existing_mem = await db.workspace_members.find_one({"user_id": user_id, "workspace_id": workspace_id})
            if not existing_mem:
                await db.workspace_members.insert_one({"user_id": user_id, "workspace_id": workspace_id,
                    "role": role, "status": "active", "joined_at": datetime.now(timezone.utc)})
        if data.invite_token:
            await db.invite_tokens.update_one({"token": data.invite_token}, {"$set": {"used": True, "used_by": user_id}})
        await write_audit_log("user_claimed", user_id, "user", user_id, {"role": role})
        access_token = create_access_token(user_id, email, role)
        refresh_token = create_refresh_token(user_id)
        resp_data = {"id": user_id, "email": email, "full_name": data.full_name or existing.get("full_name"), "role": role}
        resp = JR(content=resp_data)
        resp.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
        resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
        return resp
    
    hashed = hash_password(data.password)
    user_doc = {
        "email": email,
        "password_hash": hashed,
        "full_name": data.full_name,
        "role": role,
        "language_pref": "en",
        "active": True,
        "organization_id": organization_id,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Mark invite as used
    if data.invite_token:
        await db.invite_tokens.update_one({"token": data.invite_token}, {"$set": {"used": True, "used_by": user_id}})
    
    # Create workspace membership if workspace specified
    if workspace_id:
        await db.workspace_members.insert_one({
            "user_id": user_id, "workspace_id": workspace_id,
            "role": role, "status": "active", "joined_at": datetime.now(timezone.utc)
        })
    
    await write_audit_log("user_register", user_id, "user", user_id, {"role": role})
    
    access_token = create_access_token(user_id, email, role)
    refresh_token = create_refresh_token(user_id)
    
    resp_data = {"id": user_id, "email": email, "full_name": data.full_name, "role": role}
    resp = JR(content=resp_data)
    resp.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    resp.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return resp

@app.post("/api/auth/logout")
async def logout(user: dict = Depends(get_current_user)):
    from fastapi.responses import JSONResponse as JR
    await write_audit_log("user_logout", user["id"], "user", user["id"])
    resp = JR(content={"message": "Logged out"})
    resp.delete_cookie("access_token", path="/")
    resp.delete_cookie("refresh_token", path="/")
    return resp

@app.get("/api/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    return user

@app.post("/api/auth/refresh")
async def refresh_token_endpoint(request: Request):
    from fastapi.responses import JSONResponse as JR
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user_id = str(user["_id"])
        new_access = create_access_token(user_id, user["email"], user["role"])
        resp = JR(content={"message": "Token refreshed"})
        resp.set_cookie("access_token", new_access, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
        return resp
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/api/auth/invite")
async def create_invite(data: InviteRequest, user: dict = Depends(require_roles(*ADMIN_ROLES))):
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
    logger.info(f"Invite created for {data.email}: {invite_url}")
    return {"token": token, "invite_url": invite_url, "email": data.email}

@app.post("/api/auth/forgot-password")
async def forgot_password(request: Request):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    user = await db.users.find_one({"email": email})
    if user:
        token = secrets.token_urlsafe(32)
        await db.password_reset_tokens.insert_one({
            "token": token, "user_id": str(user["_id"]), "used": False,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "created_at": datetime.now(timezone.utc),
        })
        reset_url = f"{APP_URL}/auth/reset-password?token={token}"
        logger.info(f"Password reset for {email}: {reset_url}")
    return {"message": "If this email exists, a reset link has been sent"}

@app.post("/api/auth/reset-password")
async def reset_password(request: Request):
    body = await request.json()
    token = body.get("token", "")
    new_password = body.get("new_password", "")
    if not new_password or len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    record = await db.password_reset_tokens.find_one({
        "token": token, "used": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    await db.users.update_one(
        {"_id": ObjectId(record["user_id"])},
        {"$set": {"password_hash": hash_password(new_password)}}
    )
    await db.password_reset_tokens.update_one({"token": token}, {"$set": {"used": True}})
    return {"message": "Password updated successfully"}

# ─── User / Profile Routes ────────────────────────────────────────────────────
@app.get("/api/users")
async def list_users(user: dict = Depends(require_roles(*ADMIN_ROLES))):
    users = await db.users.find({}, {"password_hash": 0}).to_list(200)
    return [to_str_id(u) for u in users]

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["id"] != user_id and current_user["role"] not in ADMIN_ROLES + STAFF_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return to_str_id(user)

@app.put("/api/users/{user_id}")
async def update_user(user_id: str, request: Request, current_user: dict = Depends(get_current_user)):
    if current_user["id"] != user_id and current_user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Forbidden")
    body = await request.json()
    allowed = ["full_name", "phone", "country", "language_pref", "avatar_url", "bio"]
    if current_user["role"] in ADMIN_ROLES:
        allowed += ["role", "active"]
    update = {k: v for k, v in body.items() if k in allowed}
    if not update:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    update["updated_at"] = datetime.now(timezone.utc)
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update})
    await write_audit_log("user_updated", current_user["id"], "user", user_id, {"fields": list(update.keys())})
    return {"message": "Updated"}

# ─── Workspace Routes ─────────────────────────────────────────────────────────
@app.get("/api/workspaces")
async def list_workspaces(user: dict = Depends(get_current_user)):
    workspaces = await db.workspaces.find({}).to_list(50)
    return [to_str_id(w) for w in workspaces]

@app.post("/api/workspaces")
async def create_workspace(data: WorkspaceCreate, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    ws = {
        "name": data.name, "area": data.area, "description": data.description,
        "slug": data.name.lower().replace(" ", "-"), "active": True,
        "pipeline_stages": ["lead_new","qualified","docs_requested","docs_received","completed","archived"],
        "created_by": user["id"], "created_at": datetime.now(timezone.utc)
    }
    result = await db.workspaces.insert_one(ws)
    ws["id"] = str(result.inserted_id)
    return ws

# ─── Lead Ingest ─────────────────────────────────────────────────────────────
@app.post("/api/leads/ingest")
async def ingest_lead(data: LeadIngest):
    email = data.email.lower().strip()
    
    # Duplicate check
    existing_user = await db.users.find_one({"email": email})
    duplicate_flag = False
    user_id = None
    
    if existing_user:
        user_id = str(existing_user["_id"])
        duplicate_flag = True
        await write_audit_log("lead_duplicate_flagged", "system", "lead", user_id, {"email": email})
    else:
        # Create profile
        result = await db.users.insert_one({
            "email": email, "full_name": data.full_name,
            "phone": data.phone, "country": data.country,
            "role": "applicant", "language_pref": "en",
            "active": True, "created_at": datetime.now(timezone.utc),
        })
        user_id = str(result.inserted_id)
    
    # Get workspace
    workspace = await db.workspaces.find_one({"area": data.area_interest.replace("-", "_").replace("studienkolleg", "studienkolleg")})
    if not workspace:
        workspace = await db.workspaces.find_one({"slug": "studienkolleg"})
    workspace_id = str(workspace["_id"]) if workspace else None
    
    # Create application if not duplicate or if no active one exists
    existing_app = None
    if workspace_id:
        existing_app = await db.applications.find_one({
            "applicant_id": user_id, "workspace_id": workspace_id,
            "current_stage": {"$nin": ["completed", "archived"]}
        })
    
    application_id = None
    if not existing_app and workspace_id:
        app_doc = {
            "applicant_id": user_id, "workspace_id": workspace_id,
            "current_stage": "lead_new", "source": data.source,
            "desired_start": data.desired_start, "language_level": data.language_level,
            "notes": data.notes, "priority": "normal",
            "duplicate_flag": duplicate_flag,
            "created_at": datetime.now(timezone.utc), "last_activity_at": datetime.now(timezone.utc),
        }
        result = await db.applications.insert_one(app_doc)
        application_id = str(result.inserted_id)
        await write_audit_log("lead_created", "system", "application", application_id,
                              {"source": data.source, "email": email, "duplicate": duplicate_flag})
    
    return {
        "success": True, "user_id": user_id, "application_id": application_id,
        "duplicate_flag": duplicate_flag,
        "message": "Your application has been received. We will contact you shortly."
    }

# ─── Application Routes ────────────────────────────────────────────────────────
@app.get("/api/applications")
async def list_applications(request: Request, user: dict = Depends(get_current_user)):
    query = {}
    workspace_id = request.query_params.get("workspace_id")
    stage = request.query_params.get("stage")
    
    if user["role"] == "applicant":
        query["applicant_id"] = user["id"]
    elif user["role"] in PARTNER_ROLES:
        query["organization_id"] = user.get("organization_id")
    elif user["role"] in STAFF_ROLES and workspace_id:
        query["workspace_id"] = workspace_id
    
    if stage:
        query["current_stage"] = stage
    
    apps = await db.applications.find(query).sort("last_activity_at", -1).to_list(200)
    
    # Enrich with applicant name
    result = []
    for app in apps:
        app_dict = to_str_id(app)
        if user["role"] in STAFF_ROLES + ADMIN_ROLES:
            applicant = await db.users.find_one({"_id": ObjectId(app_dict["applicant_id"])}, {"full_name": 1, "email": 1, "phone": 1, "country": 1}) if app_dict.get("applicant_id") else None
            if applicant:
                app_dict["applicant"] = to_str_id(applicant)
            ws = await db.workspaces.find_one({"_id": ObjectId(app_dict["workspace_id"])}, {"name": 1}) if app_dict.get("workspace_id") else None
            if ws:
                app_dict["workspace_name"] = ws.get("name")
        result.append(app_dict)
    return result

@app.post("/api/applications")
async def create_application(data: ApplicationCreate, user: dict = Depends(get_current_user)):
    applicant_id = data.applicant_id if data.applicant_id and user["role"] in STAFF_ROLES + ADMIN_ROLES else user["id"]
    workspace = await db.workspaces.find_one({"_id": ObjectId(data.workspace_id)})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    app_doc = {
        "applicant_id": applicant_id, "workspace_id": data.workspace_id,
        "current_stage": "lead_new", "source": data.source,
        "notes": data.notes, "priority": "normal",
        "created_at": datetime.now(timezone.utc), "last_activity_at": datetime.now(timezone.utc),
        "created_by": user["id"]
    }
    result = await db.applications.insert_one(app_doc)
    app_id = str(result.inserted_id)
    await write_audit_log("application_created", user["id"], "application", app_id)
    return {**app_doc, "id": app_id}

@app.get("/api/applications/{app_id}")
async def get_application(app_id: str, user: dict = Depends(get_current_user)):
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    app_dict = to_str_id(app)
    if user["role"] == "applicant" and app_dict["applicant_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return app_dict

@app.put("/api/applications/{app_id}")
async def update_application(app_id: str, data: ApplicationUpdate, user: dict = Depends(require_roles(*STAFF_ROLES + ADMIN_ROLES))):
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    old_stage = app.get("current_stage")
    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["last_activity_at"] = datetime.now(timezone.utc)
    update["updated_by"] = user["id"]
    await db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": update})
    if data.current_stage and data.current_stage != old_stage:
        await write_audit_log("stage_changed", user["id"], "application", app_id,
                              {"old_stage": old_stage, "new_stage": data.current_stage})
        # Record activity
        await db.application_activities.insert_one({
            "application_id": app_id, "action": "stage_changed",
            "old_value": old_stage, "new_value": data.current_stage,
            "actor_id": user["id"], "occurred_at": datetime.now(timezone.utc)
        })
    return {"message": "Updated", "id": app_id}

# ─── Document Routes ──────────────────────────────────────────────────────────
@app.get("/api/applications/{app_id}/documents")
async def list_documents(app_id: str, user: dict = Depends(get_current_user)):
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if user["role"] == "applicant" and str(app["applicant_id"]) != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    docs = await db.documents.find({"application_id": app_id}).to_list(100)
    return [to_str_id(d) for d in docs]

@app.post("/api/applications/{app_id}/documents/upload")
async def upload_document(app_id: str, request: Request, user: dict = Depends(get_current_user)):
    import base64
    body = await request.json()
    doc_type = body.get("document_type", "other")
    filename = body.get("filename", "document")
    file_data = body.get("file_data")  # base64 encoded
    
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if user["role"] == "applicant" and str(app["applicant_id"]) != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # In production: store in private storage bucket
    # MVP: store reference with metadata
    doc = {
        "application_id": app_id, "document_type": doc_type, "filename": filename,
        "status": "uploaded", "uploaded_by": user["id"],
        "uploaded_at": datetime.now(timezone.utc),
        "visibility": "private",
        "storage_path": f"documents/{app_id}/{doc_type}/{filename}",
    }
    result = await db.documents.insert_one(doc)
    doc_id = str(result.inserted_id)
    await write_audit_log("document_uploaded", user["id"], "document", doc_id, {"doc_type": doc_type})
    await db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": {"last_activity_at": datetime.now(timezone.utc)}})
    return {**doc, "id": doc_id}

@app.put("/api/documents/{doc_id}/review")
async def review_document(doc_id: str, data: DocumentStatusUpdate, user: dict = Depends(require_roles(*STAFF_ROLES + ADMIN_ROLES))):
    doc = await db.documents.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    allowed_statuses = ["in_review", "approved", "rejected", "superseded"]
    if data.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")
    update = {"status": data.status, "reviewed_by": user["id"], "reviewed_at": datetime.now(timezone.utc)}
    if data.rejection_reason:
        update["rejection_reason"] = data.rejection_reason
    if data.comment:
        await db.comments.insert_one({
            "document_id": doc_id, "application_id": doc.get("application_id"),
            "content": data.comment, "author_id": user["id"],
            "visibility": "internal", "created_at": datetime.now(timezone.utc)
        })
    await db.documents.update_one({"_id": ObjectId(doc_id)}, {"$set": update})
    await write_audit_log(f"document_{data.status}", user["id"], "document", doc_id)
    return {"message": f"Document {data.status}", "id": doc_id}

# ─── Task Routes ──────────────────────────────────────────────────────────────
@app.get("/api/tasks")
async def list_tasks(request: Request, user: dict = Depends(get_current_user)):
    query = {}
    if user["role"] == "applicant":
        apps = await db.applications.find({"applicant_id": user["id"]}).to_list(50)
        app_ids = [str(a["_id"]) for a in apps]
        query = {"application_id": {"$in": app_ids}, "visibility": "public"}
    else:
        app_id = request.query_params.get("application_id")
        if app_id:
            query["application_id"] = app_id
        else:
            query["assigned_to"] = user["id"]
    tasks = await db.tasks.find(query).sort("created_at", -1).to_list(100)
    return [to_str_id(t) for t in tasks]

@app.post("/api/tasks")
async def create_task(data: TaskCreate, user: dict = Depends(require_roles(*STAFF_ROLES + ADMIN_ROLES + ["applicant"]))):
    task = {
        "title": data.title, "description": data.description,
        "application_id": data.application_id, "assigned_to": data.assigned_to or user["id"],
        "due_date": data.due_date, "priority": data.priority, "visibility": data.visibility,
        "status": "open", "created_by": user["id"], "created_at": datetime.now(timezone.utc)
    }
    result = await db.tasks.insert_one(task)
    return {**task, "id": str(result.inserted_id)}

@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, request: Request, user: dict = Depends(get_current_user)):
    body = await request.json()
    allowed = ["status", "title", "description", "assigned_to", "due_date", "priority"]
    update = {k: v for k, v in body.items() if k in allowed}
    update["updated_at"] = datetime.now(timezone.utc)
    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": update})
    return {"message": "Updated"}

# ─── Messaging Routes ─────────────────────────────────────────────────────────
@app.get("/api/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    if user["role"] == "applicant":
        convs = await db.conversations.find({"participants": user["id"]}).to_list(50)
    else:
        convs = await db.conversations.find({}).sort("last_message_at", -1).to_list(100)
    return [to_str_id(c) for c in convs]

@app.post("/api/messages")
async def send_message(data: MessageCreate, user: dict = Depends(get_current_user)):
    conv_id = data.conversation_id
    if not conv_id:
        # Create conversation
        participants = [user["id"]]
        if data.recipient_id:
            participants.append(data.recipient_id)
        conv_result = await db.conversations.insert_one({
            "participants": participants, "application_id": data.application_id,
            "created_at": datetime.now(timezone.utc), "last_message_at": datetime.now(timezone.utc)
        })
        conv_id = str(conv_result.inserted_id)
    
    msg = {
        "conversation_id": conv_id, "content": data.content,
        "sender_id": user["id"], "visibility": data.visibility,
        "sent_at": datetime.now(timezone.utc), "read": False
    }
    result = await db.messages.insert_one(msg)
    await db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"last_message_at": datetime.now(timezone.utc)}}
    )
    return {**msg, "id": str(result.inserted_id), "conversation_id": conv_id}

@app.get("/api/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, user: dict = Depends(get_current_user)):
    if user["role"] == "applicant":
        conv = await db.conversations.find_one({"_id": ObjectId(conv_id)})
        if not conv or user["id"] not in conv.get("participants", []):
            raise HTTPException(status_code=403, detail="Forbidden")
    msgs = await db.messages.find({"conversation_id": conv_id}).sort("sent_at", 1).to_list(200)
    return [to_str_id(m) for m in msgs]

# ─── Notifications & Consent ──────────────────────────────────────────────────
@app.get("/api/notifications")
async def list_notifications(user: dict = Depends(get_current_user)):
    notifs = await db.notifications.find({"user_id": user["id"]}).sort("created_at", -1).to_list(50)
    return [to_str_id(n) for n in notifs]

@app.post("/api/consent")
async def capture_consent(data: ConsentCapture, user: dict = Depends(get_current_user)):
    await db.user_consents.update_one(
        {"user_id": user["id"], "consent_type": data.consent_type},
        {"$set": {"version": data.version, "granted": data.granted,
                  "recorded_at": datetime.now(timezone.utc), "user_id": user["id"],
                  "consent_type": data.consent_type}},
        upsert=True
    )
    return {"message": "Consent recorded"}

# ─── Audit & Monitoring ────────────────────────────────────────────────────────
@app.get("/api/audit-logs")
async def get_audit_logs(request: Request, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    target_id = request.query_params.get("target_id")
    actor_id = request.query_params.get("actor_id")
    query = {}
    if target_id:
        query["target_id"] = target_id
    if actor_id:
        query["actor_id"] = actor_id
    logs = await db.audit_logs.find(query).sort("occurred_at", -1).to_list(200)
    return [to_str_id(l) for l in logs]

@app.get("/api/dashboard/stats")
async def dashboard_stats(user: dict = Depends(get_current_user)):
    if user["role"] == "applicant":
        apps = await db.applications.find({"applicant_id": user["id"]}).to_list(20)
        tasks = await db.tasks.count_documents({"assigned_to": user["id"], "status": "open", "visibility": "public"})
        return {
            "applications": len(apps),
            "open_tasks": tasks,
            "stages": [{"stage": a.get("current_stage"), "id": str(a["_id"])} for a in apps]
        }
    else:
        total_leads = await db.applications.count_documents({})
        open_leads = await db.applications.count_documents({"current_stage": {"$nin": ["completed", "archived"]}})
        open_tasks = await db.tasks.count_documents({"status": "open"})
        pending_docs = await db.documents.count_documents({"status": "uploaded"})
        return {
            "total_leads": total_leads, "open_leads": open_leads,
            "open_tasks": open_tasks, "pending_documents": pending_docs
        }

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "W2G Platform API", "version": "1.0.0"}
