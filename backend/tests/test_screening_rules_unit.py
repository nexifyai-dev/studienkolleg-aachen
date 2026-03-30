from services.screening_rules import evaluate_screening_criteria


def _base_application(**overrides):
    app = {
        "course_type": "M-Course",
        "desired_start": "WS 2026",
        "language_level": "B1",
        "degree_country": "Deutschland",
    }
    app.update(overrides)
    return app


def _base_applicant(**overrides):
    applicant = {"full_name": "Max Mustermann", "email": "max@example.com"}
    applicant.update(overrides)
    return applicant


def test_upload_only_does_not_imply_precheck_passed_when_language_fails():
    docs = [
        {"document_type": "language_certificate", "status": "uploaded"},
        {"document_type": "highschool_diploma", "status": "uploaded"},
        {"document_type": "passport", "status": "uploaded"},
    ]
    result = evaluate_screening_criteria(
        _base_application(language_level="A2"),
        _base_applicant(),
        docs,
    )

    assert result["completeness"]["complete"] is True
    assert result["formal_result"] == "language_gap"
    assert any(c["rule_id"] == "language_threshold" for c in result["criteria_failed"])


def test_language_course_uses_course_specific_required_docs():
    docs = [{"document_type": "passport", "status": "uploaded"}]
    result = evaluate_screening_criteria(
        _base_application(course_type="Language Course", language_level="A1"),
        _base_applicant(),
        docs,
    )

    assert result["completeness"]["complete"] is True
    assert result["completeness"]["required_types"] == ["passport"]


def test_missing_required_docs_sets_next_step_request_documents():
    docs = [{"document_type": "passport", "status": "uploaded"}]
    result = evaluate_screening_criteria(_base_application(), _base_applicant(), docs)

    assert result["formal_result"] == "documents_missing"
    assert result["suggested_next_step"] == "request_missing_documents"
    assert "missing_required_documents" in result["risk_flags"]
