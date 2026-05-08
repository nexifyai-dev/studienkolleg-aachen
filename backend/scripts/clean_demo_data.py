"""
Pre-presentation cleanup: removes ALL operational/mock data while keeping
the 5 development accounts and system-essential reference data intact.

Keeps:
  - 5 dev users (admin@, staff@, teacher@, applicant@, partner@studienkolleg-aachen.de)
  - workspaces (system structure)
  - settings (system config)
  - anabin_knowledge (reference data)
  - brain_emails / brain_email_drafts (real IMAP mails)
  - brain_memories (AI long-term memory)

Wipes:
  - All other users (mock applicants)
  - applications, invoices, documents, messages, conversations
  - notifications, ai_screenings, batch_screenings, anabin_review_queue
  - application_activities, appointments, tasks*, payment_transactions
  - oracle_conversations, case_notes, followups, consents
  - audit_logs, background_jobs, system_metrics, email_events
  - login_attempts, password_reset_tokens, invite_tokens, webhook_events
  - lms_enrollments, teacher_assignments, temp_uploads, user_signatures
  - storage/documents and storage/messages files
  - resets counters

Usage:
    cd /app && python3 backend/scripts/clean_demo_data.py
"""
import asyncio
import os
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")

KEEP_USER_EMAILS = {
    "admin@studienkolleg-aachen.de",
    "staff@studienkolleg-aachen.de",
    "teacher@studienkolleg-aachen.de",
    "applicant@studienkolleg-aachen.de",
    "partner@studienkolleg-aachen.de",
}

# Collections to wipe completely
WIPE_COLLECTIONS = [
    "applications",
    "invoices",
    "documents",
    "messages",
    "conversations",
    "notifications",
    "ai_screenings",
    "batch_screenings",
    "anabin_review_queue",
    "application_activities",
    "appointments",
    "tasks",
    "task_history",
    "task_attachments",
    "task_notes",
    "payment_transactions",
    "oracle_conversations",
    "case_notes",
    "followups",
    "consents",
    "audit_logs",
    "background_jobs",
    "system_metrics",
    "email_events",
    "login_attempts",
    "password_reset_tokens",
    "invite_tokens",
    "webhook_events",
    "lms_enrollments",
    "teacher_assignments",
    "temp_uploads",
    "user_signatures",
]

# Collections explicitly preserved
KEEP_COLLECTIONS = {
    "users",  # filtered manually
    "workspaces",
    "settings",
    "counters",  # cleared to reset
    "anabin_knowledge",
    "brain_emails",
    "brain_email_drafts",
    "brain_memories",
}


async def main() -> None:
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    print("=" * 60)
    print("PRE-PRESENTATION DATA CLEANUP")
    print("=" * 60)

    # 1) Users: keep only the 5 dev accounts
    res = await db.users.delete_many({"email": {"$nin": list(KEEP_USER_EMAILS)}})
    print(f"users: removed {res.deleted_count} (kept {len(KEEP_USER_EMAILS)} dev accounts)")
    remaining = [u["email"] async for u in db.users.find({}, {"email": 1, "_id": 0})]
    print(f"  remaining: {sorted(remaining)}")

    # 2) Wipe operational collections
    for col in WIPE_COLLECTIONS:
        if col in await db.list_collection_names():
            res = await db[col].delete_many({})
            if res.deleted_count:
                print(f"{col}: removed {res.deleted_count}")

    # 3) Reset counters so applicant numbers, invoice numbers etc. start fresh
    await db.counters.delete_many({})
    print("counters: reset")

    # 4) Wipe storage files
    for sub in ("documents", "messages", "invoices"):
        path = os.path.join("/app/storage", sub)
        if os.path.isdir(path):
            for entry in os.listdir(path):
                full = os.path.join(path, entry)
                if os.path.isdir(full):
                    shutil.rmtree(full, ignore_errors=True)
                else:
                    try:
                        os.remove(full)
                    except OSError:
                        pass
            print(f"storage/{sub}: cleared")

    # 5) Final inventory
    print()
    print("--- AFTER CLEANUP ---")
    cols = sorted(await db.list_collection_names())
    for col in cols:
        n = await db[col].count_documents({})
        marker = " [KEPT]" if col in KEEP_COLLECTIONS else ""
        print(f"  {col}: {n}{marker}")

    client.close()
    print()
    print("Cleanup complete. System is demo-ready.")


if __name__ == "__main__":
    asyncio.run(main())
