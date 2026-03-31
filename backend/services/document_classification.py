from __future__ import annotations

import re
from typing import Any, Iterable

SUPPORTED_TYPES = {
    "passport",
    "id",
    "highschool_diploma",
    "transcript",
    "language_certificate",
    "cv",
    "motivation",
    "other",
    "unsupported",
}

TARGET_TYPES = [
    "passport",
    "id",
    "highschool_diploma",
    "transcript",
    "language_certificate",
    "cv",
    "motivation",
    "other",
    "unsupported",
]

_KEYWORDS = {
    "passport": [
        "passport", "reisepass", "passnummer", "passport no", "nationality", "issuing country",
    ],
    "id": [
        "identity card", "personalausweis", "id card", "identitätskarte", "personal id", "card number",
    ],
    "highschool_diploma": [
        "high school diploma", "secondary school", "abitur", "zeugnis", "diploma", "graduation certificate",
    ],
    "transcript": [
        "transcript", "grade report", "grades", "record of achievement", "notenspiegel", "academic record",
    ],
    "language_certificate": [
        "goethe", "telc", "testdaf", "language certificate", "sprachzertifikat", "cefr", "b2", "c1",
    ],
    "cv": [
        "curriculum vitae", "lebenslauf", "resume", "work experience", "education", "skills",
    ],
    "motivation": [
        "motivation letter", "cover letter", "personal statement", "motivationsschreiben", "why i want",
    ],
}


_DEF_NON_TEXT_MIME_PREFIXES = (
    "image/",
    "application/pdf",
    "text/",
)


def _normalize(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _collect_text_candidates(doc: dict[str, Any]) -> Iterable[str]:
    direct_text_fields = (
        "extracted_text",
        "ocr_text",
        "content_text",
        "plain_text",
        "text",
        "analysis_text",
    )
    for field in direct_text_fields:
        text = doc.get(field)
        if isinstance(text, str) and text.strip():
            yield text

    extraction = doc.get("extraction_result")
    if isinstance(extraction, dict):
        for value in extraction.values():
            if isinstance(value, str) and value.strip():
                yield value
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.strip():
                        yield item
                    elif isinstance(item, dict):
                        for nested in item.values():
                            if isinstance(nested, str) and nested.strip():
                                yield nested


def _score_text(text: str) -> dict[str, float]:
    text_norm = _normalize(text)
    scores: dict[str, float] = {k: 0.0 for k in _KEYWORDS}
    for doc_type, words in _KEYWORDS.items():
        for keyword in words:
            if keyword in text_norm:
                scores[doc_type] += 1.0
    return scores


def _filename_hint(filename: str) -> tuple[str | None, float]:
    name = _normalize(filename)
    if not name:
        return None, 0.0

    hints = {
        "passport": ["passport", "reisepass", "pass"],
        "id": ["id_card", "identity", "personalausweis", "id"],
        "highschool_diploma": ["diploma", "abitur", "highschool", "zeugnis"],
        "transcript": ["transcript", "grades", "notenspiegel"],
        "language_certificate": ["goethe", "telc", "testdaf", "language", "sprach"],
        "cv": ["cv", "resume", "lebenslauf"],
        "motivation": ["motivation", "cover_letter", "personal_statement"],
    }
    for doc_type, keywords in hints.items():
        if any(k in name for k in keywords):
            return doc_type, 0.62
    return None, 0.0


def _mime_unsupported(content_type: str) -> bool:
    if not content_type:
        return False
    ct = _normalize(content_type)
    if ct.startswith(_DEF_NON_TEXT_MIME_PREFIXES):
        return False
    # very likely archives / executables etc.
    return bool(re.match(r"^(application/(x-msdownload|x-executable|zip|x-7z-compressed|x-rar-compressed))", ct))


def classify_document(doc: dict[str, Any], declared_type: str | None = None) -> dict[str, Any]:
    declared = _normalize(declared_type or doc.get("document_type") or "other")
    content_type = _normalize(doc.get("content_type"))

    if _mime_unsupported(content_type):
        classified = "unsupported"
        confidence = 0.99
    else:
        aggregated_scores: dict[str, float] = {k: 0.0 for k in _KEYWORDS}
        texts = list(_collect_text_candidates(doc))

        for text in texts:
            text_scores = _score_text(text)
            for k, v in text_scores.items():
                aggregated_scores[k] += v

        best_text_type = None
        best_text_score = 0.0
        for doc_type, score in aggregated_scores.items():
            if score > best_text_score:
                best_text_type = doc_type
                best_text_score = score

        filename_type, filename_conf = _filename_hint(doc.get("filename", ""))

        if best_text_type and best_text_score >= 1.0:
            classified = best_text_type
            confidence = min(0.55 + (best_text_score * 0.1), 0.95)
        elif filename_type:
            classified = filename_type
            confidence = filename_conf
        elif declared in SUPPORTED_TYPES:
            classified = declared
            confidence = 0.45
        else:
            classified = "other"
            confidence = 0.35

    type_mismatch = bool(declared and declared in SUPPORTED_TYPES and declared != classified)
    return {
        "declared_type": declared if declared in SUPPORTED_TYPES else "other",
        "classified_type": classified,
        "classification_confidence": round(float(confidence), 4),
        "type_mismatch": type_mismatch,
    }
