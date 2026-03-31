import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.document_classification import classify_document
from services.screening_rules import _check_completeness


def test_classification_uses_extracted_text_over_declared_type_when_mismatch():
    result = classify_document(
        {
            "document_type": "passport",
            "filename": "my_cv.pdf",
            "extracted_text": "Curriculum Vitae\nWork Experience\nEducation",
            "content_type": "application/pdf",
        },
        declared_type="passport",
    )
    assert result["classified_type"] == "cv"
    assert result["classification_confidence"] >= 0.6
    assert result["type_mismatch"] is True


def test_completeness_requires_classified_type_and_confidence_quality():
    docs = [
        {
            "document_type": "passport",
            "classified_type": "passport",
            "classification_confidence": 0.55,
            "status": "approved",
        }
    ]
    completeness = _check_completeness(docs, "Language Course", {"Language Course": {"required_docs": ["passport"]}})
    assert completeness["complete"] is False
    assert "passport" in completeness["missing_types"]
