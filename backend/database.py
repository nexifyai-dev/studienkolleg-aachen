"""
MongoDB client and database accessor.
Single global client instance, injected at startup.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import MONGO_URL, DB_NAME

_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None


async def connect():
    global _client, _db
    _client = AsyncIOMotorClient(MONGO_URL)
    _db = _client[DB_NAME]
    await _create_indexes()


async def disconnect():
    global _client
    if _client:
        _client.close()


def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect() first.")
    return _db


async def _create_indexes():
    db = get_db()
    # Auth & Users
    await db.users.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.login_attempts.create_index("last_attempt", expireAfterSeconds=900)
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.invite_tokens.create_index("token", unique=True)
    await db.invite_tokens.create_index("expires_at", expireAfterSeconds=0)

    # Applications – Kernabfragen
    await db.applications.create_index("applicant_id")
    await db.applications.create_index("workspace_id")
    await db.applications.create_index([("workspace_id", 1), ("current_stage", 1)])
    await db.applications.create_index([("current_stage", 1), ("last_activity_at", -1)])
    await db.applications.create_index("applicant_number", unique=True, sparse=True)

    # Documents – Performance (status-basierte Abfragen, Bewerber-Ansicht)
    await db.documents.create_index("application_id")
    await db.documents.create_index([("application_id", 1), ("status", 1)])
    await db.documents.create_index([("application_id", 1), ("document_type", 1)])

    # Tasks – Filterung, Sortierung, Faelligkeit
    await db.tasks.create_index("application_id")
    await db.tasks.create_index("assigned_to")
    await db.tasks.create_index([("assigned_to", 1), ("status", 1)])
    await db.tasks.create_index([("status", 1), ("due_date", 1)])
    await db.tasks.create_index([("application_id", 1), ("status", 1)])

    # Messages & Conversations – Performance-kritisch
    await db.messages.create_index("conversation_id")
    await db.messages.create_index([("conversation_id", 1), ("sent_at", -1)])
    await db.conversations.create_index("participants")
    await db.conversations.create_index([("participants", 1), ("last_message_at", -1)])

    # Invoices – Bewerber-Zuordnung + Status
    await db.invoices.create_index("applicant_id")
    await db.invoices.create_index([("applicant_id", 1), ("status", 1)])
    await db.invoices.create_index("invoice_number", unique=True, sparse=True)

    # Notifications
    await db.notifications.create_index("user_id")
    await db.notifications.create_index([("user_id", 1), ("read", 1)])

    # Audit – Entity-basierte + zeitliche Abfragen
    await db.audit_logs.create_index("occurred_at")
    await db.audit_logs.create_index("actor_id")
    await db.audit_logs.create_index("target_id")
    await db.audit_logs.create_index([("entity_id", 1), ("action", 1)])

    # Misc
    await db.webhook_events.create_index("event_id", unique=True, sparse=True)
    await db.oracle_conversations.create_index("created_by")
    await db.oracle_conversations.create_index("updated_at")


async def get_next_applicant_number() -> str:
    """
    Generiert die naechste Bewerbernummer atomar via findOneAndUpdate.
    Format: STK-JJJJ-NNNN (z.B. STK-2026-0001)
    Thread-safe durch atomares $inc.
    """
    from datetime import datetime, timezone
    db = get_db()
    year = datetime.now(timezone.utc).year
    counter_id = f"applicant_number_{year}"

    result = await db.counters.find_one_and_update(
        {"_id": counter_id},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    seq = result["seq"]
    return f"STK-{year}-{seq:04d}"
