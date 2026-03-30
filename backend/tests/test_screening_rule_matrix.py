import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.ai_screening import _check_completeness, _build_formal_precheck, _check_language_level, _suggest_stage


def test_completeness_is_course_specific_language_course():
    docs = [
        {"document_type": "passport", "status": "approved"},
    ]
    result = _check_completeness(docs, "Language Course")
    assert result["complete"] is True
    assert result["total_required"] == 1


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
    stage = _suggest_stage({"complete": True}, {"status": "plausible"})
    assert stage == "interview_scheduled"


def test_language_check_returns_required_actual():
    result = _check_language_level("M-Course", "B1")
    assert result["ok"] is True
    assert result["required"] == "B1"
    assert result["actual"] == "B1"


def test_completeness_tracks_unverified_documents_without_missing_them():
    docs = [
        {"document_type": "language_certificate", "status": "uploaded"},
        {"document_type": "highschool_diploma", "status": "in_review"},
        {"document_type": "passport", "status": "approved"},
    ]
    result = _check_completeness(docs, "M-Course")
    assert result["complete"] is True
    assert set(result["unverified_types"]) == {"language_certificate", "highschool_diploma"}
    assert result["total_verified"] == 1


def test_suggest_stage_stays_in_review_when_documents_are_unverified():
    completeness = {"invalid_types": [], "unverified_types": ["passport"], "complete": True}
    language = {"ok": True, "note": "ok"}
    anabin = {"category": "H+", "label": "ok"}
    precheck = _build_formal_precheck(completeness, language, anabin, {
        "degree_country": "Deutschland",
        "course_type": "M-Course",
        "language_level": "B2",
    })
    assert precheck["status"] == "unclear"
    stage = _suggest_stage(completeness, precheck)
    assert stage == "in_review"
