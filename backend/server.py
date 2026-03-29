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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_URL, APP_URL
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="W2G Platform API",
    version="1.1.0",
    description="Studienkolleg Aachen / Way2Germany – Multi-tenant applicant management platform",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000"],
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

# ─── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await connect()
    await seed_workspaces()
    await seed_admin()
    logger.info("W2G Platform API v1.1.0 started successfully")


@app.on_event("shutdown")
async def shutdown():
    await disconnect()
