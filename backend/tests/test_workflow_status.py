from services.workflow_status import (
    WORKFLOW_STATUSES,
    allowed_next_statuses,
    can_transition,
    normalize_workflow_status,
)


def test_all_required_workflow_statuses_present():
    expected = {
        "information_request",
        "documents_requested",
        "school_degree_assessed",
        "language_course_recommended",
        "language_course_booked",
        "studienkolleg_seat_reserved",
        "studienkolleg_enrollment_completed",
        "alternative_path_advisory",
        "vocational_training_recommended",
    }
    assert expected.issubset(set(WORKFLOW_STATUSES))


def test_legacy_alias_normalization():
    assert normalize_workflow_status("lead_new") == "information_request"
    assert normalize_workflow_status("pending_docs") == "documents_requested"


def test_transition_rules():
    assert can_transition("information_request", "documents_requested")
    assert not can_transition("documents_requested", "information_request")
    assert can_transition("pending_docs", "school_degree_assessed")
    assert "school_degree_assessed" in allowed_next_statuses("documents_requested")
