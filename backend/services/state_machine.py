"""
State Machine – Valide Statusuebergaenge fuer Bewerbungen.

Architekturentscheidung:
- Definiert erlaubte Transitionen pro Stage
- Verhindert ungueltigen Statuswechsel im Application Layer
- Staff mit ADMIN_ROLES koennen erzwungene Transitionen durchfuehren (force=True)
- Alle Transitionen werden audit-geloggt

Statusmaschine:
  lead_new -> in_review, declined, archived
  in_review -> pending_docs, interview_scheduled, conditional_offer, declined, on_hold, archived
  pending_docs -> in_review, interview_scheduled, conditional_offer, declined, on_hold, archived
  interview_scheduled -> conditional_offer, offer_sent, declined, on_hold, in_review, archived
  conditional_offer -> offer_sent, enrolled, declined, on_hold, archived
  offer_sent -> enrolled, declined, on_hold, archived
  enrolled -> archived, on_hold
  declined -> in_review (Wiederaufnahme)
  on_hold -> in_review, lead_new, archived
  archived -> (Endstatus, nur Admin-Force)
"""
import logging

logger = logging.getLogger(__name__)

# Erlaubte Statusuebergaenge: Von -> Set erlaubter Ziele
VALID_TRANSITIONS: dict[str, set[str]] = {
    "lead_new": {"in_review", "declined", "archived"},
    "in_review": {"pending_docs", "interview_scheduled", "conditional_offer",
                  "offer_sent", "declined", "on_hold", "archived"},
    "pending_docs": {"in_review", "interview_scheduled", "conditional_offer",
                     "declined", "on_hold", "archived"},
    "interview_scheduled": {"conditional_offer", "offer_sent", "declined",
                            "on_hold", "in_review", "archived"},
    "conditional_offer": {"offer_sent", "enrolled", "declined", "on_hold", "archived"},
    "offer_sent": {"enrolled", "declined", "on_hold", "archived"},
    "enrolled": {"archived", "on_hold"},
    "declined": {"in_review"},
    "on_hold": {"in_review", "lead_new", "archived"},
    "archived": set(),
}

ALL_STAGES = set(VALID_TRANSITIONS.keys())

# Labels fuer UI und Logging
STAGE_LABELS_DE: dict[str, str] = {
    "lead_new": "Neue Anfrage",
    "in_review": "In Bearbeitung",
    "pending_docs": "Dokumente ausstehend",
    "interview_scheduled": "Interview geplant",
    "conditional_offer": "Bedingtes Angebot",
    "offer_sent": "Angebot versendet",
    "enrolled": "Eingeschrieben",
    "declined": "Abgelehnt",
    "on_hold": "Pausiert",
    "archived": "Archiviert",
}


def validate_transition(current_stage: str, new_stage: str, force: bool = False) -> tuple[bool, str]:
    """
    Prueft ob ein Statusuebergang gueltig ist.
    
    Returns:
        (is_valid, error_message)
    """
    if current_stage == new_stage:
        return True, ""

    if new_stage not in ALL_STAGES:
        return False, f"Unbekannter Zielstatus: {new_stage}"

    if current_stage not in VALID_TRANSITIONS:
        return False, f"Unbekannter Ausgangsstatus: {current_stage}"

    allowed = VALID_TRANSITIONS[current_stage]
    if new_stage in allowed:
        return True, ""

    if force:
        logger.warning(
            f"[STATE_MACHINE] Erzwungener Uebergang: {current_stage} -> {new_stage}"
        )
        return True, ""

    current_label = STAGE_LABELS_DE.get(current_stage, current_stage)
    new_label = STAGE_LABELS_DE.get(new_stage, new_stage)
    allowed_labels = [STAGE_LABELS_DE.get(s, s) for s in sorted(allowed)]

    return False, (
        f"Ungueltiger Statusuebergang: {current_label} -> {new_label}. "
        f"Erlaubt: {', '.join(allowed_labels) or 'keine (Endstatus)'}"
    )


def get_allowed_transitions(current_stage: str) -> list[str]:
    """Gibt die erlaubten Zielstatus fuer eine Stage zurueck."""
    return sorted(VALID_TRANSITIONS.get(current_stage, set()))
