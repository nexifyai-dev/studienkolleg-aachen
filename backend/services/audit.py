"""
Audit log service – append-only, never raises.
All domain actions must call write_audit_log.
"""
import logging
from datetime import datetime, timezone
from database import get_db

logger = logging.getLogger(__name__)


async def write_audit_log(
    action: str,
    actor_id: str,
    target_type: str,
    target_id: str,
    details: dict = None,
) -> None:
    """
    Write an audit log entry. Never raises – log failures are non-blocking.
    actor_id = "system" for automated/ingest actions.
    """
    try:
        db = get_db()
        await db.audit_logs.insert_one({
            "action": action,
            "actor_id": actor_id,
            "target_type": target_type,
            "target_id": target_id,
            "details": details or {},
            "occurred_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.error(f"[AUDIT] Write failed for action={action}: {e}")
