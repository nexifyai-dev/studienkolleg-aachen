"""Canonical workflow status model and transition rules.

This module centralizes status validation and transitions so backend,
AI suggestions, and frontend can share the same process logic.
"""

from __future__ import annotations

from typing import Optional

WORKFLOW_STATUSES: list[str] = [
    "information_request",
    "documents_requested",
    "school_degree_assessed",
    "language_course_recommended",
    "language_course_booked",
    "studienkolleg_seat_reserved",
    "studienkolleg_enrollment_completed",
    "alternative_path_advisory",
    "vocational_training_recommended",
]

WORKFLOW_TRANSITIONS: dict[str, set[str]] = {
    "information_request": {"documents_requested", "alternative_path_advisory", "vocational_training_recommended"},
    "documents_requested": {"school_degree_assessed", "alternative_path_advisory", "vocational_training_recommended"},
    "school_degree_assessed": {
        "language_course_recommended",
        "studienkolleg_seat_reserved",
        "alternative_path_advisory",
        "vocational_training_recommended",
    },
    "language_course_recommended": {
        "language_course_booked",
        "studienkolleg_seat_reserved",
        "alternative_path_advisory",
    },
    "language_course_booked": {"studienkolleg_seat_reserved", "alternative_path_advisory"},
    "studienkolleg_seat_reserved": {"studienkolleg_enrollment_completed", "alternative_path_advisory"},
    "studienkolleg_enrollment_completed": set(),
    "alternative_path_advisory": {"vocational_training_recommended"},
    "vocational_training_recommended": set(),
}

# Backward compatibility for historical/legacy pipeline states.
LEGACY_STATUS_ALIASES: dict[str, str] = {
    "lead_new": "information_request",
    "contacted": "information_request",
    "pending_docs": "documents_requested",
    "docs_requested": "documents_requested",
    "docs_received": "documents_requested",
    "docs_review": "school_degree_assessed",
    "in_review": "school_degree_assessed",
    "interview_scheduled": "language_course_recommended",
    "conditional_offer": "studienkolleg_seat_reserved",
    "offer_sent": "studienkolleg_seat_reserved",
    "enrolled": "studienkolleg_enrollment_completed",
}


def normalize_workflow_status(stage: Optional[str]) -> Optional[str]:
    if not stage:
        return None
    if stage in WORKFLOW_STATUSES:
        return stage
    return LEGACY_STATUS_ALIASES.get(stage)


def is_valid_workflow_status(stage: Optional[str]) -> bool:
    return normalize_workflow_status(stage) is not None


def allowed_next_statuses(current_stage: Optional[str]) -> set[str]:
    normalized = normalize_workflow_status(current_stage)
    if normalized is None:
        return {WORKFLOW_STATUSES[0]}
    return set(WORKFLOW_TRANSITIONS.get(normalized, set()))


def can_transition(current_stage: Optional[str], next_stage: str) -> bool:
    normalized_next = normalize_workflow_status(next_stage)
    if normalized_next is None:
        return False

    normalized_current = normalize_workflow_status(current_stage)
    if normalized_current is None:
        # Unknown/empty current state: only allow process start.
        return normalized_next == WORKFLOW_STATUSES[0]

    if normalized_current == normalized_next:
        return True

    return normalized_next in WORKFLOW_TRANSITIONS.get(normalized_current, set())


def ai_suggestible_statuses() -> set[str]:
    return {
        "documents_requested",
        "school_degree_assessed",
        "language_course_recommended",
        "alternative_path_advisory",
    }
