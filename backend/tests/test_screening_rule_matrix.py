import asyncio
import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.ai_screening import _suggest_stage, run_ai_screening
from services.screening_rules import (
    _build_formal_precheck,
    _check_completeness,
    _check_language_level,
)


def test_completeness_is_course_specific_language_course():
    docs = [
        {"document_type": "passport", "status": "approved"},
    ]
    result = _check_completeness(docs, "Language Course")
    assert result["complete"] is True
    assert result["required_types"] == ["passport"]


def test_formal_precheck_marks_critical_for_d_category_and_missing_language():
    completeness = {"invalid_types": [], "complete": True}
    language = {"ok": False}
    anabin = {"category": "D", "label": "critical"}
    precheck = _build_formal_precheck(
        completeness,
        language,
        anabin,
        {
            "degree_country": "X",
            "course_type": "M-Course",
            "language_level": "A2",
        },
    )
    assert precheck["status"] == "critical"
    assert precheck["risks"]


def test_suggest_stage_is_not_in_review_by_default_when_plausible():
    stage = _suggest_stage({"formal_result": "precheck_passed"}, {"status": "plausible"})
    assert stage == "interview_scheduled"


def test_language_check_returns_required_actual():
    result = _check_language_level("M-Course", "B1")
    assert result["ok"] is True
    assert result["required"] == "B1"
    assert result["actual"] == "B1"


def test_screening_breakdown_contains_all_four_mandatory_areas(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "services.deepseek_provider",
        SimpleNamespace(is_enabled=lambda: False, chat_completion=None),
    )

    result = asyncio.run(
        run_ai_screening(
            application={
                "id": "app-1",
                "course_type": "M-Course",
                "degree_country": "Germany",
                "language_level": "B1",
            },
            applicant={"id": "appl-1", "full_name": "Max Mustermann"},
            docs=[
                {"document_type": "passport", "status": "approved"},
                {"document_type": "highschool_diploma", "status": "approved"},
                {"document_type": "language_certificate", "status": "approved"},
            ],
            messages=[],
        )
    )

    breakdown = result["screening_breakdown"]
    assert "completeness" in breakdown
    assert "formal_precheck" in breakdown
    assert "ai_recommendation" in breakdown
    assert "staff_decision" in breakdown


def test_negative_upload_presence_never_implies_final_admission(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "services.deepseek_provider",
        SimpleNamespace(is_enabled=lambda: False, chat_completion=None),
    )

    result = asyncio.run(
        run_ai_screening(
            application={
                "id": "app-2",
                "course_type": "M-Course",
                "degree_country": "Germany",
                "language_level": "B1",
            },
            applicant={"id": "appl-2", "full_name": "Erika Beispiel"},
            docs=[
                {"document_type": "passport", "status": "approved"},
                {"document_type": "highschool_diploma", "status": "approved"},
                {"document_type": "language_certificate", "status": "approved"},
            ],
            messages=[{"content": "Alle Dokumente hochgeladen"}],
        )
    )

    assert result["local_checks"]["completeness"]["complete"] is True
    assert result["decision_scope"] == "vorpruefung_only_no_final_admission_decision"
    assert "keine finale" in result["screening_breakdown"]["ai_recommendation"]["note"].lower()
    assert result["screening_breakdown"]["staff_decision"]["status"] == "pending"


def test_negative_upload_presence_with_gaps_requires_staff_actions(monkeypatch):
    monkeypatch.setitem(
        sys.modules,
        "services.deepseek_provider",
        SimpleNamespace(is_enabled=lambda: False, chat_completion=None),
    )

    result = asyncio.run(
        run_ai_screening(
            application={
                "id": "app-3",
                "course_type": "M-Course",
                "degree_country": "Germany",
                "language_level": "A2",
            },
            applicant={"id": "appl-3", "full_name": "Ali Example"},
            docs=[{"document_type": "passport", "status": "uploaded"}],
            messages=[],
        )
    )

    assert result["staff_action_required"] is True
    assert result["formal_result"] in {"documents_missing", "language_gap", "manual_review_required"}
    assert result["screening_breakdown"]["staff_decision"]["status"] == "pending"
    assert "Staff" in result["decision_note"]
