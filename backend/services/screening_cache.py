"""
Screening Cache – Delta-orientierte KI-Pruefungslogik.

Strategie:
- Vor jedem KI-Screening wird geprueft, ob sich relevante Daten geaendert haben
- Wenn nichts geaendert → cached result zurueckgeben (kein KI-Call)
- Wenn Aenderungen → nur geaenderte Daten an KI senden (Delta)
- Fingerprint basiert auf: Dokumente, Bewerbungsdaten, Sprachniveau

Kostenersparnis: ~70-90% weniger KI-Calls fuer ungeaenderte Bewerbungen.
"""
import hashlib
import json
import logging
from database import get_db

logger = logging.getLogger(__name__)


def _compute_fingerprint(application: dict, docs: list, messages_count: int) -> str:
    """Compute a hash fingerprint of relevant data for delta detection."""
    relevant = {
        "course_type": application.get("course_type"),
        "language_level": application.get("language_level"),
        "degree_country": application.get("degree_country"),
        "current_stage": application.get("current_stage"),
        "date_of_birth": application.get("date_of_birth"),
        "doc_types": sorted([d.get("document_type", "") for d in docs]),
        "doc_statuses": sorted([f"{d.get('document_type')}:{d.get('status')}" for d in docs]),
        "messages_count": messages_count,
    }
    raw = json.dumps(relevant, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


async def get_cached_screening(app_id: str, application: dict, docs: list, messages_count: int) -> dict:
    """
    Check if a valid cached screening exists for unchanged data.

    Returns:
        {"hit": True, "screening": {...}} if cache valid
        {"hit": False, "fingerprint": "...", "previous_screening": {...} or None} if cache miss
    """
    db = get_db()
    fingerprint = _compute_fingerprint(application, docs, messages_count)

    # Find most recent screening for this application
    last = await db.ai_screenings.find_one(
        {"application_id": app_id},
        sort=[("created_at", -1)],
    )

    if last and last.get("data_fingerprint") == fingerprint:
        logger.info(f"[SCREENING_CACHE] HIT for {app_id} (fingerprint={fingerprint})")
        from models.schemas import to_str_id
        cached = to_str_id(dict(last))
        cached["cache_hit"] = True
        return {"hit": True, "screening": cached}

    # Cache miss – return previous screening for delta context
    previous = None
    if last:
        from models.schemas import to_str_id
        previous = to_str_id(dict(last))

    logger.info(f"[SCREENING_CACHE] MISS for {app_id} (fingerprint={fingerprint})")
    return {
        "hit": False,
        "fingerprint": fingerprint,
        "previous_screening": previous,
    }
