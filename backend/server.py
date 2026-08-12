"""
W2G Platform API – main entry point.

This file is the application factory only.
All business logic lives in routers/, services/, models/, seed.py.

Structure:
  config.py       – environment config (fails fast on missing required vars)
  database.py     – MongoDB client + index creation
  deps.py         – FastAPI dependency injectors (auth, role checks)
  seed.py         – idempotent workspace + admin seeding
  models/         – Pydantic schemas
  routers/        – route modules by domain
  services/       – audit, email, storage
"""
from dotenv import load_dotenv
load_dotenv()

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import FRONTEND_URL, APP_URL, COOKIE_SECURE
from database import connect, disconnect
from seed import seed_workspaces, seed_admin

# Routers
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.workspaces import router as workspaces_router
from routers.leads import router as leads_router
from routers.applications import router as applications_router
from routers.documents import router as documents_router
from routers.tasks import router as tasks_router
from routers.messaging import router as messaging_router
from routers.system import audit_router, dashboard_router, notif_router, system_router
from routers.notifications import router as notifications_router
from routers.ai_screening import router as ai_screening_router
from routers.cost_simulator import router as cost_simulator_router
from routers.consents import router as consent_router
from routers.teacher import router as teacher_router
from routers.followups import router as followups_router
from routers.export import router as export_router
from routers.partner import router as partner_router
from routers.invoices import router as invoices_router
from routers.appointments import router as appointments_router
from routers.anabin_admin import router as anabin_admin_router
from routers.brain import router as brain_router
from routers.jobs import router as jobs_router
from routers.oracle import router as oracle_router
from routers.support_chat import router as support_chat_router
from routers.lms import router as lms_router
from routers.products import router as products_router
from routers.quotes import router as quotes_router
from routers.payments import router as payments_router
from routers.payments import webhook_router as stripe_webhook_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Rate Limiter ─────────────────────────────────────────────────────────────
from rate_limiter import limiter

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="W2G Platform API",
    version="1.4.0",
    description="Studienkolleg Aachen / Way2Germany – Multi-tenant applicant management platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─── CSRF Double-Submit Cookie ────────────────────────────────────────────────
import secrets

CSRF_COOKIE_NAME = "csrf_token"
CSRF_HEADER_NAME = "x-csrf-token"
CSRF_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

@app.middleware("http")
async def csrf_protection(request, call_next):
    """CSRF-Schutz via Double-Submit Cookie Pattern."""
    # Safe methods und Webhooks/API-Docs ueberspringen
    path = request.url.path
    if (request.method in CSRF_SAFE_METHODS
        or path.startswith("/api/webhooks")
        or path.startswith("/api/docs")
        or path.startswith("/api/redoc")
        or path.startswith("/api/openapi")
        or path.startswith("/api/health")
        or path.startswith("/api/auth/login")
        or path.startswith("/api/auth/register")
        or path.startswith("/api/public")):
        response = await call_next(request)
        # CSRF-Token setzen wenn noch nicht vorhanden
        if CSRF_COOKIE_NAME not in request.cookies:
            token = secrets.token_hex(32)
            response.set_cookie(
                CSRF_COOKIE_NAME, token,
                httponly=False,  # JS muss Token lesen koennen
                secure=COOKIE_SECURE,
                samesite="Lax",
                max_age=86400,
            )
        return response

    # Fuer unsafe methods: Token pruefen
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)

    # Wenn kein Cookie gesetzt, Token erstellen und durchlassen (erste Anfrage)
    if not cookie_token:
        response = await call_next(request)
        token = secrets.token_hex(32)
        response.set_cookie(
            CSRF_COOKIE_NAME, token,
            httponly=False,
            secure=COOKIE_SECURE,
            samesite="Lax",
            max_age=86400,
        )
        return response

    # Token-Vergleich (Header muss mit Cookie uebereinstimmen)
    if not header_token or header_token != cookie_token:
        logger.warning(f"[CSRF] Token mismatch BLOCKED: path={path} method={request.method}")
        return JSONResponse(
            status_code=403,
            content={"detail": "CSRF token missing or invalid"},
        )

    response = await call_next(request)
    return response


# ─── Security Headers Middleware ──────────────────────────────────────────────

# Endpoints that legitimately need to be embedded in an <iframe> or <img> from
# the frontend (PDF previews, invoice PDFs, document/message attachments).
# These must NOT receive X-Frame-Options: DENY, otherwise browsers refuse to
# render them inside the staff/applicant document preview modals.
_FRAMEABLE_PATH_FRAGMENTS = (
    "/documents/",        # /api/documents/{id}/download, /api/applications/{id}/documents/...
    "/invoices/",         # /api/invoices/{id}/pdf, /api/invoices/{number}/pdf
    "/applications/",     # /api/applications/{id}/pdf (Fallakte-PDF)
    "/messages/",         # /api/messages/{id}/attachment
)

def _is_frameable_path(path: str) -> bool:
    return any(frag in path for frag in _FRAMEABLE_PATH_FRAGMENTS)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if COOKIE_SECURE:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Allow embedding of file-preview endpoints in our own frontend iframes.
    # Everything else stays strictly DENY to prevent clickjacking.
    if _is_frameable_path(request.url.path):
        # CSP frame-ancestors is the modern replacement and also allows custom domains.
        response.headers["Content-Security-Policy"] = "frame-ancestors *"
    else:
        response.headers["X-Frame-Options"] = "DENY"
    return response


# ─── CORS ─────────────────────────────────────────────────────────────────────
_cors_origins = os.environ.get("CORS_ORIGINS", "")
if _cors_origins == "*":
    _allowed_origins = ["*"]
elif _cors_origins:
    _allowed_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
else:
    _allowed_origins = [FRONTEND_URL, "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workspaces_router)
app.include_router(leads_router)
app.include_router(applications_router)
app.include_router(documents_router)
app.include_router(tasks_router)
app.include_router(messaging_router)
app.include_router(audit_router)
app.include_router(dashboard_router)
app.include_router(notif_router)
app.include_router(system_router)
app.include_router(ai_screening_router)
app.include_router(cost_simulator_router)
app.include_router(consent_router)
app.include_router(teacher_router)
app.include_router(notifications_router)
app.include_router(followups_router)
app.include_router(export_router)
app.include_router(partner_router)
app.include_router(appointments_router)
app.include_router(invoices_router)
app.include_router(anabin_admin_router)
app.include_router(brain_router)
app.include_router(jobs_router)
app.include_router(oracle_router)
app.include_router(support_chat_router)
app.include_router(products_router)
app.include_router(quotes_router)
app.include_router(lms_router)
app.include_router(payments_router)
app.include_router(stripe_webhook_router)

# ─── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await connect()
    await seed_workspaces()
    await seed_admin()
    # Seed Anabin knowledge base (retrieval-first)
    from services.anabin_knowledge import seed_anabin_knowledge
    await seed_anabin_knowledge()
    # Start Background Worker only if NOT in serverless environment
    if not os.environ.get("VERCEL_SERVERLESS"):
        import asyncio
        from services.worker import start_worker
        from services.scheduler import start_scheduler
        asyncio.create_task(start_worker())
        asyncio.create_task(start_scheduler())
    logger.info("W2G Platform API v1.4.0 started successfully")


@app.on_event("shutdown")
async def shutdown():
    from services.worker import stop_worker
    from services.scheduler import stop_scheduler
    await stop_worker()
    await stop_scheduler()
    await disconnect()
