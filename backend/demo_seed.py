"""
Demo data seed – creates realistic-looking data for customer presentation.
Run: python3 demo_seed.py
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import random

DEMO_APPLICANTS = [
    {"full_name": "Amira El-Khoury", "email": "amira.elkhoury@gmail.com", "country": "Libanon", "phone": "+961 71 234567"},
    {"full_name": "Yusuf Demir", "email": "yusuf.demir@hotmail.com", "country": "Türkei", "phone": "+90 532 1234567"},
    {"full_name": "Fatima Benali", "email": "fatima.benali@yahoo.com", "country": "Marokko", "phone": "+212 6 12345678"},
    {"full_name": "Chen Wei", "email": "chen.wei@outlook.com", "country": "China", "phone": "+86 138 1234 5678"},
    {"full_name": "Nguyen Thi Lan", "email": "ntlan.nguyen@gmail.com", "country": "Vietnam", "phone": "+84 91 234 5678"},
    {"full_name": "Mohammad Reza Hosseini", "email": "m.hosseini@gmail.com", "country": "Iran", "phone": "+98 912 345 6789"},
    {"full_name": "Priya Sharma", "email": "priya.sharma@gmail.com", "country": "Indien", "phone": "+91 98765 43210"},
    {"full_name": "Carlos Mendoza", "email": "c.mendoza@hotmail.com", "country": "Kolumbien", "phone": "+57 310 1234567"},
    {"full_name": "Olga Petrov", "email": "olga.petrov@mail.ru", "country": "Russland", "phone": "+7 916 123 4567"},
    {"full_name": "Samuel Okafor", "email": "samuel.okafor@gmail.com", "country": "Nigeria", "phone": "+234 803 1234567"},
    {"full_name": "Lina Al-Rashid", "email": "lina.alrashid@gmail.com", "country": "Irak", "phone": "+964 770 1234567"},
    {"full_name": "Ahmed Hassan", "email": "applicant@studienkolleg-aachen.de", "country": "Ägypten", "phone": "+20 100 1234567"},
]

DEMO_STAGES_DISTRIBUTION = [
    ("lead_new", 3),
    ("in_review", 2),
    ("pending_docs", 2),
    ("interview_scheduled", 1),
    ("conditional_offer", 1),
    ("offer_sent", 1),
    ("enrolled", 1),
]

DEMO_TASKS = [
    {"title": "Unterlagen von Amira El-Khoury prüfen", "description": "Zeugnis-Übersetzung und Sprachnachweis kontrollieren", "priority": "high", "status": "open"},
    {"title": "Beratungsgespräch Yusuf Demir planen", "description": "Termin für Online-Beratung koordinieren", "priority": "medium", "status": "open"},
    {"title": "Einschreibebestätigung versenden", "description": "Offizielle Bestätigung an Chen Wei senden", "priority": "high", "status": "in_progress"},
    {"title": "Sprachtest-Ergebnis nachverfolgen", "description": "B2-Nachweis von Fatima Benali anfordern", "priority": "medium", "status": "open"},
    {"title": "Visum-Unterstützungsschreiben erstellen", "description": "Für Mohammad Reza Hosseini vorbereiten", "priority": "high", "status": "open"},
]


async def seed():
    client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    db = client[os.environ.get("DB_NAME", "w2g_platform")]
    now = datetime.now(timezone.utc)

    # 1. Clean test tasks
    del_tasks = await db.tasks.delete_many({"title": {"$regex": "^TEST_"}})
    print(f"Deleted {del_tasks.deleted_count} test tasks")

    # 2. Clean test invoices
    del_inv = await db.invoices.delete_many({"description": {"$regex": "TEST_Block2"}})
    print(f"Deleted {del_inv.deleted_count} test invoices")

    # 3. Remove test users (keep seed users with @studienkolleg-aachen.de)
    del_users = await db.users.delete_many({
        "email": {"$regex": "test_|TEST_|nopass_|@example\\.com|@w2g\\.test|portal_test"},
        "email": {"$not": {"$regex": "@studienkolleg-aachen\\.de"}}
    })
    print(f"Deleted {del_users.deleted_count} test users")

    # 4. Remove orphaned applications (applicant_id references deleted users)
    seed_user_ids = set()
    seed_users = await db.users.find({}, {"_id": 1}).to_list(100)
    for u in seed_users:
        seed_user_ids.add(str(u["_id"]))

    all_apps = await db.applications.find({}).to_list(500)
    orphaned = [a["_id"] for a in all_apps if str(a.get("applicant_id", "")) not in seed_user_ids]
    if orphaned:
        del_apps = await db.applications.delete_many({"_id": {"$in": orphaned}})
        print(f"Deleted {del_apps.deleted_count} orphaned applications")

    # 5. Get workspace
    ws = await db.workspaces.find_one()
    ws_id = str(ws["_id"]) if ws else None

    # 6. Create demo applicant users (skip if email exists)
    stage_index = 0
    stage_pool = []
    for stage, count in DEMO_STAGES_DISTRIBUTION:
        stage_pool.extend([stage] * count)
    random.shuffle(stage_pool)

    for i, demo in enumerate(DEMO_APPLICANTS):
        existing = await db.users.find_one({"email": demo["email"]})
        if existing:
            # Update name/country if needed
            await db.users.update_one(
                {"_id": existing["_id"]},
                {"$set": {"full_name": demo["full_name"], "country": demo.get("country", ""), "phone": demo.get("phone", "")}}
            )
            user_id = str(existing["_id"])
        else:
            from bcrypt import hashpw, gensalt
            # ÄNDERUNG 2026-08-13 09:45 CEST — Default Seed-Default entfernt
            #   (Secret-Scanner-Fund 13.08.). Fail-fast statt bekanntem Default.
            seed_pw = os.environ.get("SEED_DEV_PASSWORD")
            if not seed_pw:
                raise RuntimeError("SEED_DEV_PASSWORD not configured")
            pw_hash = hashpw(seed_pw.encode(), gensalt()).decode()
            user_doc = {
                "email": demo["email"],
                "full_name": demo["full_name"],
                "password_hash": pw_hash,
                "role": "applicant",
                "active": True,
                "country": demo.get("country", ""),
                "phone": demo.get("phone", ""),
                "language_pref": "de",
                "created_at": now - timedelta(days=random.randint(5, 45)),
            }
            res = await db.users.insert_one(user_doc)
            user_id = str(res.inserted_id)

        # Create/update application
        existing_app = await db.applications.find_one({"applicant_id": user_id})
        stage = stage_pool[i % len(stage_pool)] if i < len(stage_pool) else "lead_new"
        days_ago = random.randint(1, 30)

        if existing_app:
            await db.applications.update_one(
                {"_id": existing_app["_id"]},
                {"$set": {
                    "current_stage": stage,
                    "last_activity_at": now - timedelta(days=random.randint(0, 3)),
                }}
            )
        else:
            app_doc = {
                "applicant_id": user_id,
                "workspace_id": ws_id,
                "current_stage": stage,
                "source": random.choice(["website_form", "partner_referral", "direct_inquiry"]),
                "priority": random.choice(["normal", "normal", "high"]),
                "created_at": now - timedelta(days=days_ago),
                "last_activity_at": now - timedelta(days=random.randint(0, 3)),
            }
            await db.applications.insert_one(app_doc)

        print(f"  Demo: {demo['full_name']} ({demo['country']}) → {stage}")

    # 7. Create demo tasks
    staff = await db.users.find_one({"role": "staff"})
    staff_id = str(staff["_id"]) if staff else None

    existing_demo_tasks = await db.tasks.count_documents({"title": {"$in": [t["title"] for t in DEMO_TASKS]}})
    if existing_demo_tasks == 0:
        for t in DEMO_TASKS:
            task_doc = {
                "title": t["title"],
                "description": t["description"],
                "priority": t["priority"],
                "status": t["status"],
                "assigned_to": staff_id,
                "created_by": staff_id,
                "workspace_id": ws_id,
                "created_at": now - timedelta(days=random.randint(1, 7)),
                "due_date": (now + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
                "history": [],
                "notes": [],
            }
            await db.tasks.insert_one(task_doc)
        print(f"Created {len(DEMO_TASKS)} demo tasks")

    # 8. Verify final state
    total_apps = await db.applications.count_documents({})
    total_tasks = await db.tasks.count_documents({})
    total_users = await db.users.count_documents({})
    total_inv = await db.invoices.count_documents({})
    print(f"\nFinal: {total_apps} apps, {total_tasks} tasks, {total_users} users, {total_inv} invoices")

asyncio.run(seed())
