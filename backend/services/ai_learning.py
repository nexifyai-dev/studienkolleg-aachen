"""
KI-Lern-Engine – Kontextuelles Lernen aus allen Kommunikationsquellen.

Die Engine aggregiert Wissen aus:
1. Vorherige Screening-Ergebnisse und Staff-Entscheidungen
2. Kommunikationsverlaeufe (Portal-Messages, E-Mails)
3. Dokumenten-Review-Historien
4. Anabin-Queue-Resolutions (Feedback-Loop)
5. Audit-Logs (Statuswechsel, manuelle Eingriffe)

Dieses aggregierte Wissen wird als "Institutional Memory" beim KI-Screening
injiziert, damit die KI aus realen Faellen und Entscheidungsmustern lernt.
"""
import logging
from datetime import datetime, timezone
from database import get_db

logger = logging.getLogger(__name__)


async def gather_institutional_knowledge(application_id: str, applicant_id: str = None) -> dict:
    """
    Sammelt institutionelles Wissen fuer eine spezifische Bewerbung.
    Wird vor jedem KI-Screening aufgerufen.

    Returns:
        dict mit staff_patterns, communication_insights, similar_cases, decision_history
    """
    db = get_db()
    knowledge = {
        "staff_patterns": [],
        "communication_insights": [],
        "similar_cases": [],
        "decision_history": [],
        "document_review_history": [],
    }

    # 1. Kommunikationsverlauf (Portal-Messages)
    try:
        messages = await db.messages.find(
            {"application_id": application_id}
        ).sort("created_at", -1).to_list(30)

        for msg in messages:
            knowledge["communication_insights"].append({
                "channel": msg.get("channel", "portal"),
                "content_preview": (msg.get("content") or "")[:300],
                "sender_role": msg.get("sender_role", "unknown"),
                "created_at": str(msg.get("created_at", "")),
            })
    except Exception as e:
        logger.warning(f"[AI_LEARNING] Messages-Fehler: {e}")

    # 2. Audit-Log Muster (Statuswechsel, Entscheidungen)
    try:
        audits = await db.audit_logs.find(
            {"entity_id": application_id, "action": {"$in": [
                "stage_changed", "ai_suggestion_accepted",
                "document_approved", "document_rejected",
                "manual_rescreening", "queue_resolved_with_feedback",
            ]}}
        ).sort("created_at", -1).to_list(20)

        for a in audits:
            knowledge["decision_history"].append({
                "action": a.get("action"),
                "details": a.get("details", {}),
                "actor": a.get("actor_id", "system"),
                "at": str(a.get("created_at", "")),
            })
    except Exception as e:
        logger.warning(f"[AI_LEARNING] Audit-Fehler: {e}")

    # 3. Dokument-Review-Historie
    try:
        docs = await db.documents.find(
            {"application_id": application_id,
             "reviewed_by": {"$exists": True}}
        ).to_list(20)

        for d in docs:
            knowledge["document_review_history"].append({
                "doc_type": d.get("document_type"),
                "status": d.get("status"),
                "rejection_reason": d.get("rejection_reason"),
                "validation_status": d.get("validation_status"),
                "reviewed_by": d.get("reviewed_by"),
                "reviewed_at": str(d.get("reviewed_at", "")),
            })
    except Exception as e:
        logger.warning(f"[AI_LEARNING] Dokument-Historie-Fehler: {e}")

    # 4. Aehnliche Faelle (gleiches Land/Kurstyp) - nur abgeschlossene
    try:
        app = await db.applications.find_one(
            {"_id": __import__("bson").ObjectId(application_id)},
            {"degree_country": 1, "course_type": 1}
        )
        if app:
            country = app.get("degree_country")
            course = app.get("course_type")  # noqa: F841
            if country:
                similar = await db.ai_screenings.find(
                    {"$and": [
                        {"application_id": {"$ne": application_id}},
                        {"local_checks.anabin_assessment.match_type": {"$in": ["exact", "country_only"]}},
                    ]},
                    {"suggested_stage": 1, "anabin_category": 1,
                     "staff_decision_required": 1, "ai_report": 1,
                     "screened_at": 1, "_id": 0}
                ).sort("created_at", -1).to_list(5)

                for s in similar:
                    knowledge["similar_cases"].append({
                        "suggested_stage": s.get("suggested_stage"),
                        "anabin_category": s.get("anabin_category"),
                        "staff_decision_required": s.get("staff_decision_required"),
                        "report_snippet": (s.get("ai_report") or "")[:200],
                    })
    except Exception as e:
        logger.warning(f"[AI_LEARNING] Aehnliche-Faelle-Fehler: {e}")

    # 5. Staff-Entscheidungsmuster (global)
    try:
        recent_decisions = await db.audit_logs.find(
            {"action": "ai_suggestion_accepted"},
            {"details": 1, "_id": 0}
        ).sort("created_at", -1).to_list(10)

        for d in recent_decisions:
            details = d.get("details", {})
            knowledge["staff_patterns"].append({
                "old_stage": details.get("old_value"),
                "new_stage": details.get("new_value"),
                "source": details.get("source"),
            })
    except Exception as e:
        logger.warning(f"[AI_LEARNING] Staff-Pattern-Fehler: {e}")

    return knowledge


def format_knowledge_for_prompt(knowledge: dict) -> str:
    """
    Formatiert das institutionelle Wissen als Kontext-Block fuer KI-Prompts.
    """
    parts = []

    # Kommunikations-Einsichten
    if knowledge.get("communication_insights"):
        parts.append("KOMMUNIKATIONSVERLAUF (letztes Wissen aus Chats/E-Mails):")
        for ci in knowledge["communication_insights"][:10]:
            role = ci.get("sender_role", "?")
            ch = ci.get("channel", "?")
            parts.append(f"  [{ch}/{role}]: {ci['content_preview']}")

    # Entscheidungshistorie
    if knowledge.get("decision_history"):
        parts.append("\nENTSCHEIDUNGSHISTORIE (Staff-Aktionen):")
        for dh in knowledge["decision_history"][:8]:
            action = dh.get("action", "?")
            details = dh.get("details", {})
            parts.append(f"  - {action}: {details}")

    # Dokument-Reviews
    if knowledge.get("document_review_history"):
        parts.append("\nDOKUMENT-REVIEW-HISTORIE:")
        for dr in knowledge["document_review_history"][:5]:
            status = dr.get("status", "?")
            reason = dr.get("rejection_reason", "-")
            parts.append(f"  - {dr.get('doc_type')}: {status} (Grund: {reason})")

    # Aehnliche Faelle
    if knowledge.get("similar_cases"):
        parts.append("\nAEHNLICHE FAELLE (gleiche Herkunft/Kurs):")
        for sc in knowledge["similar_cases"][:3]:
            parts.append(f"  - Vorschlag: {sc.get('suggested_stage')}, Anabin: {sc.get('anabin_category')}")

    # Staff-Muster
    if knowledge.get("staff_patterns"):
        parts.append("\nSTAFF-ENTSCHEIDUNGSMUSTER (global):")
        accept_count = len(knowledge["staff_patterns"])
        parts.append(f"  - {accept_count} KI-Vorschlaege in letzter Zeit uebernommen")

    return "\n".join(parts) if parts else "Keine vorherigen Erkenntnisse vorhanden."


async def store_learning_event(event_type: str, application_id: str, data: dict):
    """Speichert ein Lernereignis fuer spaetere Analyse."""
    db = get_db()
    try:
        await db.ai_learning_events.insert_one({
            "event_type": event_type,
            "application_id": application_id,
            "data": data,
            "created_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.warning(f"[AI_LEARNING] Speichern fehlgeschlagen: {e}")
