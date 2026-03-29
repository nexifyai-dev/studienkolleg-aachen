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
    await db.users.create_index("email", unique=True)
    await db.login_attempts.create_index("identifier")
    await db.login_attempts.create_index(
        "last_attempt", expireAfterSeconds=900  # auto-clear after 15 min
    )
    await db.password_reset_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.invite_tokens.create_index("token", unique=True)
    await db.invite_tokens.create_index("expires_at", expireAfterSeconds=0)
    await db.applications.create_index("applicant_id")
    await db.applications.create_index("workspace_id")
    await db.applications.create_index([("workspace_id", 1), ("current_stage", 1)])
    await db.documents.create_index("application_id")
    await db.tasks.create_index("application_id")
    await db.tasks.create_index("assigned_to")
    await db.messages.create_index("conversation_id")
    await db.conversations.create_index("participants")
    await db.notifications.create_index("user_id")
    await db.audit_logs.create_index("occurred_at")
    await db.audit_logs.create_index("actor_id")
    await db.audit_logs.create_index("target_id")
    await db.webhook_events.create_index("event_id", unique=True, sparse=True)
