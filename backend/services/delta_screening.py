"""
Delta-Screening-Service – Vergleich alter und neuer KI-Bewertungen.

Ablauf:
1. Neues Screening-Ergebnis mit vorherigem vergleichen
2. Geaenderte Felder identifizieren
3. Konfidenz-Bewertung berechnen
4. Vergleichsergebnis persistieren
5. Folgelogik fuer Staff-Review / Eskalation ableiten
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

CONFIDENCE_LEVELS = {
    "high": "Hohe Sicherheit",
    "medium": "Mittlere Sicherheit – Pruefung empfohlen",
    "low": "Geringe Sicherheit – manuelle Pruefung erforderlich",
    "unknown": "Keine Einschaetzung moeglich",
}

RELEVANT_DOC_TYPES = {
    "language_certificate", "highschool_diploma", "passport",
    "transcript", "degree_certificate", "motivation_letter",
    "cv", "recommendation", "visa", "financial_proof",
}


def is_screening_relevant_upload(doc_type: str) -> bool:
    """Prueft ob ein Dokumenttyp ein Re-Screening ausloesen soll."""
    return doc_type in RELEVANT_DOC_TYPES


def compute_delta(previous: dict, current: dict) -> dict:
    """
    Vergleicht vorheriges und aktuelles Screening-Ergebnis.
    Gibt strukturierten Delta-Bericht zurueck.
    """
    if not previous:
        return {
            "has_previous": False,
            "is_initial": True,
            "changes": [],
            "summary": "Erstbewertung – kein Vergleich moeglich.",
            "risk_change": "neutral",
            "confidence": "medium",
        }

    changes = []

    # Vollstaendigkeit
    prev_complete = previous.get("is_complete", False)
    curr_complete = current.get("is_complete", False)
    if prev_complete != curr_complete:
        changes.append({
            "field": "completeness",
            "label": "Dokumentvollstaendigkeit",
            "previous": "Vollstaendig" if prev_complete else "Unvollstaendig",
            "current": "Vollstaendig" if curr_complete else "Unvollstaendig",
            "impact": "positive" if curr_complete and not prev_complete else "negative",
            "detail": "Alle Pflichtdokumente vorhanden" if curr_complete else "Dokumente fehlen weiterhin",
        })

    # Fehlende Dokumente
    prev_missing = set(previous.get("missing_documents", []))
    curr_missing = set(current.get("missing_documents", []))
    newly_provided = prev_missing - curr_missing
    newly_missing = curr_missing - prev_missing
    if newly_provided:
        changes.append({
            "field": "documents_added",
            "label": "Neu eingereichte Dokumente",
            "previous": f"{len(prev_missing)} fehlend",
            "current": f"{len(curr_missing)} fehlend",
            "impact": "positive",
            "detail": f"Nachgereicht: {', '.join(newly_provided)}",
        })
    if newly_missing:
        changes.append({
            "field": "documents_removed",
            "label": "Neue fehlende Dokumente",
            "previous": f"{len(prev_missing)} fehlend",
            "current": f"{len(curr_missing)} fehlend",
            "impact": "negative",
            "detail": f"Neu fehlend: {', '.join(newly_missing)}",
        })

    # Anabin-Kategorie
    prev_anabin = previous.get("anabin_category", "unbekannt")
    curr_anabin = current.get("anabin_category", "unbekannt")
    if prev_anabin != curr_anabin:
        anabin_order = {"H+": 4, "H+-": 3, "H-": 2, "D": 1, "pruefen": 0, "unbekannt": -1}
        prev_rank = anabin_order.get(prev_anabin, -1)
        curr_rank = anabin_order.get(curr_anabin, -1)
        changes.append({
            "field": "anabin_category",
            "label": "Anabin-Einstufung",
            "previous": prev_anabin,
            "current": curr_anabin,
            "impact": "positive" if curr_rank > prev_rank else "negative" if curr_rank < prev_rank else "neutral",
            "detail": f"Aenderung von {prev_anabin} auf {curr_anabin}",
        })

    # Sprachniveau
    prev_lang = previous.get("language_level_ok")
    curr_lang = current.get("language_level_ok")
    if prev_lang != curr_lang:
        changes.append({
            "field": "language_level",
            "label": "Sprachniveau-Pruefung",
            "previous": "Ausreichend" if prev_lang else "Ungenuegend",
            "current": "Ausreichend" if curr_lang else "Ungenuegend",
            "impact": "positive" if curr_lang and not prev_lang else "negative",
            "detail": "Sprachanforderung jetzt erfuellt" if curr_lang else "Sprachanforderung nicht mehr erfuellt",
        })

    # Status-Vorschlag
    prev_stage = previous.get("suggested_stage", "")
    curr_stage = current.get("suggested_stage", "")
    if prev_stage != curr_stage:
        changes.append({
            "field": "suggested_stage",
            "label": "Statusvorschlag",
            "previous": prev_stage,
            "current": curr_stage,
            "impact": "neutral",
            "detail": f"KI-Empfehlung geaendert: {prev_stage} → {curr_stage}",
        })

    # Staff-Entscheid
    prev_staff = previous.get("staff_decision_required", False)
    curr_staff = current.get("staff_decision_required", False)
    if prev_staff != curr_staff:
        changes.append({
            "field": "staff_decision",
            "label": "Staff-Entscheid",
            "previous": "Erforderlich" if prev_staff else "Nicht erforderlich",
            "current": "Erforderlich" if curr_staff else "Nicht erforderlich",
            "impact": "neutral",
            "detail": "Manuelle Pruefung jetzt noetig" if curr_staff else "Kein manueller Eingriff mehr noetig",
        })

    # Gesamtbewertung
    positive_count = sum(1 for c in changes if c["impact"] == "positive")
    negative_count = sum(1 for c in changes if c["impact"] == "negative")

    if negative_count > 0 and positive_count == 0:
        risk_change = "increased"
        confidence = "low"
    elif positive_count > 0 and negative_count == 0:
        risk_change = "decreased"
        confidence = "high"
    elif len(changes) == 0:
        risk_change = "unchanged"
        confidence = "high"
    else:
        risk_change = "mixed"
        confidence = "medium"

    summary_parts = []
    if len(changes) == 0:
        summary_parts.append("Keine relevanten Aenderungen seit der letzten Bewertung.")
    else:
        summary_parts.append(f"{len(changes)} Aenderung(en) erkannt.")
        if positive_count:
            summary_parts.append(f"{positive_count} positiv.")
        if negative_count:
            summary_parts.append(f"{negative_count} kritisch – manuelle Pruefung empfohlen.")

    return {
        "has_previous": True,
        "is_initial": False,
        "changes": changes,
        "changes_count": len(changes),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "summary": " ".join(summary_parts),
        "risk_change": risk_change,
        "confidence": confidence,
        "confidence_label": CONFIDENCE_LEVELS.get(confidence, ""),
        "previous_screened_at": previous.get("screened_at", ""),
        "previous_suggested_stage": previous.get("suggested_stage", ""),
    }


async def trigger_auto_rescreening(app_id: str, trigger_doc_type: str, trigger_filename: str, uploaded_by: str) -> Optional[dict]:
    """
    Wird nach einem relevanten Dokument-Upload aufgerufen.
    Fuehrt automatisches Re-Screening mit Delta-Vergleich durch.
    """
    from services.ai_screening import run_ai_screening
    from models.schemas import to_str_id
    from services.audit import write_audit_log
    from bson import ObjectId

    db = get_db()

    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        logger.error(f"[DELTA_SCREENING] Ungueltige app_id: {app_id}")
        return None

    if not app:
        logger.warning(f"[DELTA_SCREENING] Bewerbung nicht gefunden: {app_id}")
        return None

    app_dict = to_str_id(dict(app))

    # Bewerber laden
    applicant = {}
    if app_dict.get("applicant_id"):
        try:
            u = await db.users.find_one(
                {"_id": ObjectId(app_dict["applicant_id"])},
                {"full_name": 1, "email": 1, "country": 1, "phone": 1},
            )
            if u:
                applicant = to_str_id(u)
        except Exception:
            pass

    # Dokumente laden
    docs_raw = await db.documents.find({"application_id": app_id}).to_list(50)
    docs = [to_str_id(dict(d)) for d in docs_raw]
    for d in docs:
        d.pop("storage_key", None)

    # Nachrichten laden
    messages_raw = await db.messages.find({"application_id": app_id}).sort("created_at", 1).to_list(20)
    messages = [to_str_id(dict(m)) for m in messages_raw]

    # Vorheriges Screening laden
    previous_screening = await db.ai_screenings.find_one(
        {"application_id": app_id},
        sort=[("created_at", -1)],
    )
    previous_dict = to_str_id(dict(previous_screening)) if previous_screening else None

    # Neues Screening durchfuehren
    result = await run_ai_screening(app_dict, applicant, docs, messages)

    # Delta berechnen
    delta = compute_delta(previous_dict, result)

    # Ergebnis mit Delta speichern
    result_to_save = {
        **result,
        "triggered_by": "system_auto_rescreening",
        "trigger_reason": f"Dokument-Upload: {trigger_doc_type} ({trigger_filename})",
        "trigger_doc_type": trigger_doc_type,
        "trigger_doc_filename": trigger_filename,
        "uploaded_by": uploaded_by,
        "is_delta_screening": True,
        "delta": delta,
        "created_at": datetime.now(timezone.utc),
    }
    await db.ai_screenings.insert_one(result_to_save)

    # Audit-Log
    await write_audit_log(
        "auto_rescreening_triggered",
        "system",
        "application",
        app_id,
        {
            "screening_id": result["screening_id"],
            "trigger": f"doc_upload:{trigger_doc_type}",
            "changes_count": delta["changes_count"] if delta.get("has_previous") else 0,
            "risk_change": delta["risk_change"],
            "confidence": delta["confidence"],
        },
    )

    # Task fuer Staff erstellen wenn Pruefung noetig
    if delta.get("confidence") in ("low", "medium") or result.get("staff_decision_required"):
        task_title = f"Re-Screening pruefen: {applicant.get('full_name', app_id)}"
        task_desc_parts = [f"Automatisches Re-Screening nach Upload von: {trigger_filename} ({trigger_doc_type})."]
        if delta.get("changes"):
            task_desc_parts.append(f"{delta['changes_count']} Aenderung(en) erkannt.")
        if delta.get("confidence") == "low":
            task_desc_parts.append("Geringe Konfidenz – manuelle Pruefung dringend erforderlich.")

        await db.tasks.insert_one({
            "title": task_title,
            "description": " ".join(task_desc_parts),
            "application_id": app_id,
            "task_type": "rescreening_review",
            "priority": "high" if delta.get("confidence") == "low" else "medium",
            "status": "open",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system",
            "metadata": {
                "screening_id": result["screening_id"],
                "trigger_doc_type": trigger_doc_type,
                "delta_summary": delta.get("summary", ""),
                "risk_change": delta.get("risk_change", ""),
            },
        })

    logger.info(f"[DELTA_SCREENING] Auto-Rescreening fuer {app_id}: {delta['changes_count']} Aenderungen, Konfidenz={delta['confidence']}")
    return {**result, "delta": delta}
