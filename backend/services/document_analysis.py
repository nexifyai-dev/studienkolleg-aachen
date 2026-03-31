"""Document analysis helpers for screening precheck.

This module does not make admission decisions. It extracts candidate signals and
marks confidence categories for staff review.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

ALLOWED_RESULT_CATEGORIES = {
    "technically_verified",
    "plausible",
    "unclear",
    "critical",
    "manual_review_required",
}

DOC_CLASS_REQUIREMENTS = {
    "passport": ["person_name", "date_of_birth", "issuer"],
    "highschool_diploma": ["person_name", "issuer", "degree_type", "exam_date"],
    "language_certificate": [
        "person_name",
        "issuer",
        "exam_authority",
        "cefr_level",
        "exam_date",
    ],
}

CEFR_PATTERN = re.compile(r"\b(A1|A2|B1|B2|C1|C2)\b", flags=re.IGNORECASE)
DATE_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{2}[./-]\d{2}[./-]\d{4})\b")


def _extract_text_source(doc: dict[str, Any]) -> tuple[str, str]:
    text_candidates = [
        doc.get("extracted_text"),
        doc.get("ocr_text"),
        doc.get("text"),
        doc.get("content_text"),
        doc.get("notes"),
    ]
    for value in text_candidates:
        if isinstance(value, str) and value.strip():
            return value.strip(), "document_embedded_text"

    return "", "no_machine_readable_text"


def _document_processing_mode(doc: dict[str, Any]) -> str:
    content_type = (doc.get("content_type") or "").lower()
    filename = (doc.get("filename") or "").lower()
    if content_type.startswith("image/") or filename.endswith((".png", ".jpg", ".jpeg", ".webp", ".tiff")):
        return "ocr"
    if content_type == "application/pdf" or filename.endswith(".pdf"):
        return "ocr_or_pdf_text"
    return "text_extraction"


def _first_date(text: str) -> str | None:
    match = DATE_PATTERN.search(text)
    if not match:
        return None
    raw = match.group(1)
    if re.match(r"\d{2}[./-]\d{2}[./-]\d{4}", raw):
        raw = raw.replace(".", "-").replace("/", "-")
        day, month, year = raw.split("-")
        return f"{year}-{month}-{day}"
    return raw


def _extract_core_fields(text: str, doc: dict[str, Any], application: dict[str, Any], applicant: dict[str, Any]) -> dict[str, Any]:
    if not text or len(text.strip()) < 3:
        return {
            "person_name": None,
            "date_of_birth": None,
            "issuer": None,
            "degree_type": None,
            "exam_authority": None,
            "cefr_level": None,
            "exam_date": None,
        }

    lowered = text.lower()
    person_name = applicant.get("full_name")
    if person_name and person_name.lower() not in lowered:
        person_name = None

    birth_date = application.get("date_of_birth")
    if birth_date and birth_date not in text:
        birth_date = None

    issuer = None
    for marker in ("issuer", "issued by", "behörde", "authority", "schule", "university"):
        if marker in lowered:
            issuer = marker
            break

    degree_type = None
    if any(token in lowered for token in ("diploma", "abitur", "zeugnis", "degree", "certificate")):
        degree_type = doc.get("document_type")

    exam_authority = None
    if any(token in lowered for token in ("telc", "goethe", "testdaf", "german exam")):
        exam_authority = "detected_exam_authority"

    cefr_match = CEFR_PATTERN.search(text)
    cefr_level = cefr_match.group(1).upper() if cefr_match else None

    exam_date = _first_date(text)

    return {
        "person_name": person_name,
        "date_of_birth": birth_date,
        "issuer": issuer,
        "degree_type": degree_type,
        "exam_authority": exam_authority,
        "cefr_level": cefr_level,
        "exam_date": exam_date,
    }


def _compute_relevance_score(doc_type: str, extracted: dict[str, Any]) -> float:
    required = DOC_CLASS_REQUIREMENTS.get(doc_type, ["person_name", "issuer"])
    if not required:
        return 0.0
    hits = sum(1 for field in required if extracted.get(field))
    return round(hits / len(required), 2)


def _classify_document(doc: dict[str, Any], content_readable: bool, has_required: bool, relevance_score: float) -> str:
    if doc.get("status") in {"rejected", "invalid"}:
        return "critical"
    if not content_readable:
        return "manual_review_required"
    if has_required and relevance_score >= 0.85:
        return "technically_verified"
    if has_required and relevance_score >= 0.5:
        return "plausible"
    if relevance_score > 0:
        return "unclear"
    return "manual_review_required"


def _build_document_analysis(doc: dict[str, Any], application: dict[str, Any], applicant: dict[str, Any]) -> dict[str, Any]:
    text, text_source = _extract_text_source(doc)
    process_mode = _document_processing_mode(doc)
    content_readable = bool(text and len(text.strip()) >= 3)
    extracted_fields = _extract_core_fields(text, doc, application, applicant)
    required_fields = DOC_CLASS_REQUIREMENTS.get(doc.get("document_type"), ["person_name", "issuer"])
    contains_required_fields = all(extracted_fields.get(field) for field in required_fields)
    relevance_score = _compute_relevance_score(doc.get("document_type"), extracted_fields)

    category = _classify_document(doc, content_readable, contains_required_fields, relevance_score)
    if not content_readable:
        category = "manual_review_required"
    if category not in ALLOWED_RESULT_CATEGORIES:
        category = "manual_review_required"

    return {
        "document_id": doc.get("id"),
        "document_type": doc.get("document_type"),
        "filename": doc.get("filename"),
        "processing": {
            "mode": process_mode,
            "text_source": text_source,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        },
        "core_fields": extracted_fields,
        "suitability": {
            "required_fields": required_fields,
            "content_readable": content_readable,
            "contains_required_fields": contains_required_fields,
            "relevance_score": relevance_score,
        },
        "category": category,
        "evidence": [
            {
                "kind": "processing_mode",
                "value": process_mode,
                "source": "document_metadata",
            },
            {
                "kind": "text_source",
                "value": text_source,
                "source": "document_metadata",
            },
            {
                "kind": "required_fields",
                "value": required_fields,
                "source": "document_class_definition",
            },
            {
                "kind": "content_verification",
                "value": (
                    "Nur Datei-Metadaten vorhanden, keine inhaltliche Verifikation"
                    if not content_readable
                    else "Inhaltliche Verifikation auf Basis extrahierten Texts"
                ),
                "source": "document_processing",
            },
        ],
    }


def classify_overall_document_set(document_analyses: list[dict[str, Any]]) -> str:
    categories = {item.get("category") for item in document_analyses}
    if "critical" in categories:
        return "critical"
    if "manual_review_required" in categories:
        return "manual_review_required"
    if "unclear" in categories:
        return "unclear"
    if categories and categories.issubset({"technically_verified"}):
        return "technically_verified"
    if categories:
        return "plausible"
    return "manual_review_required"


def analyze_documents_for_screening(application: dict[str, Any], applicant: dict[str, Any], docs: list[dict[str, Any]]) -> dict[str, Any]:
    analyses = [_build_document_analysis(doc, application, applicant) for doc in docs]
    overall_category = classify_overall_document_set(analyses)
    return {
        "documents": analyses,
        "overall_category": overall_category,
    }
