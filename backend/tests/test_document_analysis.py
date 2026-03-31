import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from services.document_analysis import analyze_documents_for_screening


def test_document_analysis_extracts_core_fields_and_categories():
    application = {"date_of_birth": "2001-02-03"}
    applicant = {"full_name": "Max Mustermann"}
    docs = [
        {
            "id": "doc-pass",
            "document_type": "passport",
            "filename": "passport.png",
            "content_type": "image/png",
            "status": "approved",
            "extracted_text": "Passport Max Mustermann DOB 2001-02-03 Issued by City Authority",
        },
        {
            "id": "doc-lang",
            "document_type": "language_certificate",
            "filename": "telc.pdf",
            "content_type": "application/pdf",
            "status": "uploaded",
            "extracted_text": "TELC Certificate Max Mustermann B2 exam 15.03.2025 issued by Goethe",
        },
    ]

    result = analyze_documents_for_screening(application, applicant, docs)
    assert result["overall_category"] in {
        "technically_verified",
        "plausible",
        "unclear",
        "critical",
        "manual_review_required",
    }
    assert len(result["documents"]) == 2
    assert result["documents"][0]["core_fields"]["person_name"] == "Max Mustermann"
    assert result["documents"][1]["core_fields"]["cefr_level"] == "B2"
    assert isinstance(result["documents"][0]["suitability"]["relevance_score"], float)
