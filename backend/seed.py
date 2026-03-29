"""
Database seeding – workspaces and admin user.
Called once at startup. Idempotent.
"""
import logging
import bcrypt
from datetime import datetime, timezone
from database import get_db
from config import ADMIN_EMAIL, ADMIN_PASSWORD

logger = logging.getLogger(__name__)


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


WORKSPACE_SEEDS = [
    {
        "slug": "studienkolleg",
        "name": "Studienkolleg Aachen",
        "area": "studienkolleg",
        "active": True,
        "pipeline_stages": [
            "lead_new", "contacted", "docs_requested", "docs_received",
            "docs_review", "invoice_open", "payment_received",
            "process_next", "completed", "dormant", "archived",
        ],
    },
    {
        "slug": "sprachkurse",
        "name": "Sprachkurse",
        "area": "language_courses",
        "active": True,
        "pipeline_stages": ["lead_new", "interested", "enrolled", "active", "completed", "archived"],
    },
    {
        "slug": "pflege",
        "name": "Pflegefachschule",
        "area": "nursing",
        "active": False,  # Not in MVP scope
        "pipeline_stages": ["lead_new", "qualified", "docs_submitted", "enrolled", "completed", "archived"],
    },
    {
        "slug": "arbeit",
        "name": "Arbeit & Ausbildung",
        "area": "work_training",
        "active": False,  # Not in MVP scope
        "pipeline_stages": ["lead_new", "qualified", "docs_submitted", "matched", "completed", "archived"],
    },
]


async def seed_workspaces() -> None:
    db = get_db()
    for ws in WORKSPACE_SEEDS:
        existing = await db.workspaces.find_one({"slug": ws["slug"]})
        if not existing:
            await db.workspaces.insert_one({
                **ws,
                "created_at": datetime.now(timezone.utc),
            })
            logger.info(f"[SEED] Workspace created: {ws['slug']}")


async def seed_admin() -> None:
    """
    Seed the initial superadmin.
    Credentials come from environment variables (ADMIN_EMAIL, ADMIN_PASSWORD).
    No password defaults in code – ADMIN_PASSWORD is required in .env.

    This function is idempotent:
    - If admin already exists with correct password → no-op.
    - If admin exists with different password → updates hash (useful for secret rotation).
    - If admin does not exist → creates it.

    To DISABLE seeding in production, remove ADMIN_EMAIL/ADMIN_PASSWORD from .env
    and handle initial admin creation via a one-time migration script instead.
    """
    db = get_db()
    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if existing is None:
        await db.users.insert_one({
            "email": ADMIN_EMAIL,
            "password_hash": _hash(ADMIN_PASSWORD),
            "full_name": "System Admin",
            "role": "superadmin",
            "language_pref": "de",
            "active": True,
            "created_at": datetime.now(timezone.utc),
            "seeded": True,
        })
        logger.info(f"[SEED] Admin created: {ADMIN_EMAIL}")
    elif not _verify(ADMIN_PASSWORD, existing.get("password_hash", "")):
        await db.users.update_one(
            {"email": ADMIN_EMAIL},
            {"$set": {"password_hash": _hash(ADMIN_PASSWORD)}},
        )
        logger.info(f"[SEED] Admin password rotated: {ADMIN_EMAIL}")
    else:
        logger.info(f"[SEED] Admin already exists, no changes: {ADMIN_EMAIL}")
