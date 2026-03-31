import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.ai_screening import _suggest_stage
from services.document_analysis import analyze_documents_for_screening
from services.screening_rules import (
    _build_formal_precheck,
    _check_completeness,
    _doc_status_bucket,
    _check_language_level,
    evaluate_screening_criteria,
    get_rule_matrix_versioning,
)


def test_completeness_is_course_specific_language_course():
    docs = [
        {"document_type": "passport", "status": "approved"},
    ]
    result = _check_completeness(docs, "Language Course", {"Language Course": {"required_docs": ["passport"]}})
    assert result["complete"] is True
    assert result["total_required"] == 1


def test_doc_status_bucket_treats_uploaded_as_unverified():
    assert _doc_status_bucket("approved") == "present"
    assert _doc_status_bucket("in_review") == "present"
    assert _doc_status_bucket("uploaded") == "uploaded_unverified"


def test_completeness_uploaded_only_is_not_complete_and_flagged_unverified():
    docs = [{"document_type": "passport", "status": "uploaded"}]
    result = _check_completeness(docs, "Language Course", {"Language Course": {"required_docs": ["passport"]}})

    assert result["complete"] is False
    assert result["missing_types"] == ["passport"]
    assert result["uploaded_but_unverified_types"] == ["passport"]


def test_formal_precheck_marks_critical_for_d_category_and_missing_language():
    completeness = {"invalid_types": [], "complete": True}
    language = {"ok": False}
    anabin = {"category": "D", "label": "critical"}
    precheck = _build_formal_precheck(completeness, language, anabin, {
        "degree_country": "X",
        "course_type": "M-Course",
        "language_level": "A2",
    })
    assert precheck["status"] == "critical"
    assert precheck["risks"]


def test_suggest_stage_is_not_in_review_by_default_when_plausible():
    stage = _suggest_stage({"formal_result": "precheck_passed"}, {"status": "plausible"})
    assert stage == "interview_scheduled"


def test_language_check_returns_required_actual():
    result = _check_language_level("M-Course", "B1", {"M-Course": {"language_min": "B1"}})
    assert result["ok"] is True
    assert result["required"] == "B1"
    assert result["actual"] == "B1"


def test_evaluate_uses_active_matrix_version_and_metadata():
    result = evaluate_screening_criteria(
        application={"course_type": "M-Course", "degree_country": "Deutschland", "language_level": "B1"},
        applicant={"id": "abc"},
        docs=[
            {"document_type": "language_certificate", "status": "approved"},
            {"document_type": "highschool_diploma", "status": "approved"},
            {"document_type": "passport", "status": "approved"},
        ],
    )

    assert result["reference_basis"]["version"] == get_rule_matrix_versioning()["active_version"]
    assert result["criteria_checked"][0]["rule_id"] == "docs_required_uploaded"
    assert result["criteria_checked"][0]["source"]["pflichtenheft"]


def test_deprecated_version_is_still_resolvable_for_backwards_compatibility():
    result = evaluate_screening_criteria(
        application={"course_type": "Language Course", "degree_country": "USA", "language_level": "A1"},
        applicant={"id": "legacy"},
        docs=[{"document_type": "passport", "status": "approved"}],
        matrix_version="0.9.0",
    )

    assert result["reference_basis"]["version"] == "0.9.0"
    assert "0.9.0" in result["reference_basis"]["deprecated_versions"]
    assert result["formal_result"] == "precheck_passed"


def test_evidence_documents_contains_document_analysis_payload():
    application = {"course_type": "M-Course", "degree_country": "Deutschland", "language_level": "B1", "date_of_birth": "2002-01-01"}
    applicant = {"id": "abc", "full_name": "Erika Mustermann"}
    docs = [
        {
            "id": "doc1",
            "document_type": "passport",
            "status": "approved",
            "filename": "passport.jpg",
            "content_type": "image/jpeg",
            "extracted_text": "Passport Erika Mustermann 2002-01-01 issued by authority",
        },
        {"id": "doc2", "document_type": "highschool_diploma", "status": "approved", "extracted_text": "Diploma Erika Mustermann issued by school 2020-06-30"},
        {"id": "doc3", "document_type": "language_certificate", "status": "approved", "extracted_text": "TELC B1 Erika Mustermann exam 2023-05-02 issued by Goethe"},
    ]

    doc_analysis = analyze_documents_for_screening(application, applicant, docs)
    result = evaluate_screening_criteria(application, applicant, docs, document_analysis=doc_analysis)

    assert result["evidence"]["documents"]
    assert "core_fields" in result["evidence"]["documents"][0]
    assert result["verification_category"] in {
        "technically_verified",
        "plausible",
        "unclear",
        "critical",
        "manual_review_required",
    }
