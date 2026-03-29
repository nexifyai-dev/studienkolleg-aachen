"""
Database seeding – workspaces, admin, and dev/test accounts.
Called once at startup. Idempotent.

Security note:
- All credentials come from environment variables.
- ADMIN_PASSWORD is required; DEV seed accounts use SEED_DEV_PASSWORD.
- Never hardcode credentials in this file.
"""
import logging
import os
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
            "lead_new", "in_review", "pending_docs", "interview_scheduled",
            "conditional_offer", "offer_sent", "enrolled",
            "declined", "on_hold", "archived",
        ],
        "available_courses": ["T-Course", "M-Course", "W-Course", "M/T-Course"],
    },
    {
        "slug": "sprachkurse",
        "name": "Sprachkurse (A1-C1)",
        "area": "language_courses",
        "active": True,
        "pipeline_stages": [
            "lead_new", "in_review", "pending_docs", "offer_sent", "enrolled", "declined", "archived",
        ],
        "available_courses": ["Language Course"],
    },
    {
        "slug": "pflege",
        "name": "Pflegefachschule",
        "area": "nursing",
        "active": False,
        "pipeline_stages": ["lead_new", "in_review", "enrolled", "declined", "archived"],
        "available_courses": [],
    },
    {
        "slug": "arbeit",
        "name": "Arbeit & Ausbildung",
        "area": "work_training",
        "active": False,
        "pipeline_stages": ["lead_new", "in_review", "enrolled", "declined", "archived"],
        "available_courses": [],
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

    # Seed dev/test accounts (only if SEED_DEV_PASSWORD is set in env)
    seed_pw = os.environ.get("SEED_DEV_PASSWORD", "")
    if not seed_pw:
        logger.info("[SEED] SEED_DEV_PASSWORD not set, skipping dev accounts")
        return

    dev_accounts = [
        {
            "email": "staff@studienkolleg-aachen.de",
            "full_name": "Maria Schmidt",
            "role": "staff",
        },
        {
            "email": "teacher@studienkolleg-aachen.de",
            "full_name": "Dr. Thomas Mueller",
            "role": "teacher",
        },
        {
            "email": "applicant@studienkolleg-aachen.de",
            "full_name": "Ahmed Hassan",
            "role": "applicant",
        },
    ]

    for acct in dev_accounts:
        existing = await db.users.find_one({"email": acct["email"]})
        if existing is None:
            await db.users.insert_one({
                "email": acct["email"],
                "password_hash": _hash(seed_pw),
                "full_name": acct["full_name"],
                "role": acct["role"],
                "language_pref": "de",
                "active": True,
                "created_at": datetime.now(timezone.utc),
                "seeded": True,
            })
            logger.info(f"[SEED] Dev account created: {acct['email']} ({acct['role']})")
        elif not _verify(seed_pw, existing.get("password_hash", "")):
            await db.users.update_one(
                {"email": acct["email"]},
                {"$set": {
                    "password_hash": _hash(seed_pw),
                    "role": acct["role"],
                    "full_name": acct["full_name"],
                }},
            )
            logger.info(f"[SEED] Dev account password synced: {acct['email']}")
        else:
            logger.info(f"[SEED] Dev account exists, no changes: {acct['email']}")
