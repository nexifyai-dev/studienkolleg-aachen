"""Drive-/Pflichtenheft-basierte Screening-Regelmatrix.

Source-Basis (lokal repliziert aus Projektdokumentation):
- 10_funktions_und_modulmatrix.md
- 12_datenmodell_und_source_of_truth.md
- 02_verifikationsmatrix.md

Wichtig:
- Upload allein erzeugt niemals eine Zulassungsannahme.
- Die Regelmatrix trennt Vollständigkeit, formale Vorprüfung und KI-Empfehlung.
"""
from __future__ import annotations

from typing import Optional

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

COURSE_LANGUAGE_REQUIREMENTS = {
    "M-Course": "B1",
    "T-Course": "B1",
    "W-Course": "B1",
    "M/T-Course": "B1",
    "Language Course": "A1",
}

REQUIRED_DOCUMENT_TYPES = ["language_certificate", "highschool_diploma", "passport"]
REQUIRED_DOC_LABELS = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}

ANABIN_COUNTRY_HINTS = {
    "h_plus": [
        "deutschland", "österreich", "schweiz", "usa", "kanada", "australien",
        "großbritannien", "frankreich", "niederlande", "belgien", "schweden",
        "norwegen", "dänemark", "finnland", "japan", "südkorea", "neuseeland",
        "united states", "canada", "united kingdom", "france", "netherlands",
        "austria", "switzerland", "sweden", "norway", "denmark", "finland",
        "japan", "south korea", "australia", "new zealand",
    ],
    "h": [
        "china", "indien", "brasilien", "türkei", "russland", "ukraine",
        "ägypten", "marokko", "tunesien", "iran", "vietnam", "thailand",
        "mexico", "argentinien", "kolumbien", "chile", "indonesia", "malaysia",
        "india", "brazil", "turkey", "russia", "egypt", "morocco", "tunisia",
        "china", "vietnam", "thailand", "mexico", "argentina", "colombia",
        "chile", "indonesia", "malaysia",
    ],
    "d": [
        "afghanistan", "irak", "syrien", "libyen", "somalia", "jemen",
        "eritrea", "äthiopien", "nigeria", "ghana", "kamerun", "senegal",
        "mali", "niger", "burkina faso", "demokratische republik kongo",
        "iraq", "syria", "libya", "somalia", "yemen", "eritrea", "ethiopia",
        "nigeria", "ghana", "cameroon", "senegal",
    ],
}


def _has_value(value: Optional[str]) -> bool:
    return bool(value and str(value).strip())


def get_anabin_category(country: Optional[str]) -> dict:
    if not country:
        return {"category": "unbekannt", "label": "Herkunftsland nicht angegeben – manuelle Prüfung erforderlich"}
    country_lower = country.lower().strip()
    if country_lower in ANABIN_COUNTRY_HINTS["h_plus"]:
        return {"category": "H+", "label": f"Hohe Anerkennungswahrscheinlichkeit ({country})."}
    if country_lower in ANABIN_COUNTRY_HINTS["h"]:
        return {"category": "H", "label": f"Anerkennbar mit möglichen Auflagen ({country})."}
    if country_lower in ANABIN_COUNTRY_HINTS["d"]:
        return {"category": "D", "label": f"Eingeschränkte Anerkennung ({country}) – intensive Einzelfallprüfung erforderlich."}
    return {"category": "prüfen", "label": f"Herkunftsland '{country}' nicht in lokaler Referenzmatrix."}


def check_language_level(course_type: Optional[str], language_level: Optional[str]) -> dict:
    if not course_type or not language_level:
        return {"ok": False, "note": "Kurstyp oder Sprachniveau nicht angegeben."}
    required = COURSE_LANGUAGE_REQUIREMENTS.get(course_type)
    if not required:
        return {"ok": False, "note": f"Kurstyp '{course_type}' nicht in Regelmatrix hinterlegt."}
    try:
        required_idx = CEFR_LEVELS.index(required)
        actual_idx = CEFR_LEVELS.index(language_level)
        if actual_idx >= required_idx:
            return {"ok": True, "note": f"Sprachniveau {language_level} erfüllt Mindestanforderung {required}.", "required": required}
        return {
            "ok": False,
            "note": f"Sprachniveau {language_level} unzureichend für {course_type} (Mindest: {required}).",
            "required": required,
        }
    except ValueError:
        return {"ok": False, "note": f"Ungültiges Sprachniveau '{language_level}'.", "required": required}


def check_document_completeness(docs: list) -> dict:
    uploaded_types = {
        d.get("document_type")
        for d in docs
        if d.get("status") not in ("rejected", "superseded")
    }
    missing = [t for t in REQUIRED_DOCUMENT_TYPES if t not in uploaded_types]
    present = [t for t in REQUIRED_DOCUMENT_TYPES if t in uploaded_types]
    return {
        "complete": len(missing) == 0,
        "missing_types": missing,
        "missing_labels": [REQUIRED_DOC_LABELS[t] for t in missing],
        "present_labels": [REQUIRED_DOC_LABELS[t] for t in present],
        "total_required": len(REQUIRED_DOCUMENT_TYPES),
        "total_present": len(present),
    }


def evaluate_screening_criteria(application: dict, applicant: dict, docs: list) -> dict:
    completeness = check_document_completeness(docs)
    anabin = get_anabin_category(application.get("degree_country"))
    language = check_language_level(application.get("course_type"), application.get("language_level"))

    required_fields = {
        "full_name": applicant.get("full_name"),
        "email": applicant.get("email"),
        "course_type": application.get("course_type"),
        "desired_start": application.get("desired_start"),
        "language_level": application.get("language_level"),
        "degree_country": application.get("degree_country"),
    }

    fields_missing = [k for k, v in required_fields.items() if not _has_value(v)]
    criteria_checked = []
    criteria_failed = []
    criteria_missing = []
    risk_flags = []

    def _mark(rule_id: str, status: str, note: str):
        item = {"rule_id": rule_id, "status": status, "note": note}
        criteria_checked.append(item)
        if status == "failed":
            criteria_failed.append(item)
        if status == "missing":
            criteria_missing.append(item)

    if fields_missing:
        _mark("required_fields", "missing", f"Fehlende Pflichtfelder: {', '.join(fields_missing)}")
        risk_flags.append("incomplete_mandatory_fields")
    else:
        _mark("required_fields", "passed", "Alle Kernpflichtfelder für Vorprüfung vorhanden.")

    if completeness["complete"]:
        _mark("required_documents", "passed", "Alle Pflichtdokumente liegen in prüffähigem Status vor.")
    else:
        _mark("required_documents", "failed", f"Fehlende Pflichtdokumente: {', '.join(completeness['missing_labels'])}")
        risk_flags.append("missing_required_documents")

    if language["ok"]:
        _mark("language_threshold", "passed", language["note"])
    else:
        # missing vs failed trennen
        status = "missing" if "nicht angegeben" in language["note"] else "failed"
        _mark("language_threshold", status, language["note"])
        risk_flags.append("language_requirement_not_met")

    if anabin["category"] == "D":
        _mark("degree_reference", "failed", anabin["label"])
        risk_flags.append("anabin_restricted")
    elif anabin["category"] in ("H", "H+"):
        _mark("degree_reference", "passed", anabin["label"])
    else:
        _mark("degree_reference", "missing", anabin["label"])
        risk_flags.append("anabin_manual_check_required")

    formal_result = "manual_review_required"
    if not fields_missing and completeness["complete"] and language["ok"] and anabin["category"] in ("H", "H+"):
        formal_result = "precheck_passed"
    elif completeness["complete"] and not language["ok"]:
        formal_result = "language_gap"
    elif not completeness["complete"]:
        formal_result = "documents_missing"

    suggested_next_step = "staff_formal_review"
    if formal_result == "documents_missing":
        suggested_next_step = "request_missing_documents"
    elif formal_result == "language_gap":
        suggested_next_step = "offer_language_pathway"

    evidence = {
        "required_fields": required_fields,
        "documents": {
            "required": [REQUIRED_DOC_LABELS[d] for d in REQUIRED_DOCUMENT_TYPES],
            "present": completeness["present_labels"],
            "missing": completeness["missing_labels"],
        },
        "language": {
            "course_type": application.get("course_type"),
            "provided_level": application.get("language_level"),
            "required_level": language.get("required"),
            "note": language["note"],
        },
        "degree_reference": {
            "country": application.get("degree_country"),
            "anabin_category": anabin["category"],
            "note": anabin["label"],
            "reference_mode": "local_rulebase_from_drive_docs",
        },
    }

    return {
        "completeness": completeness,
        "anabin_assessment": anabin,
        "language_level_check": language,
        "criteria_checked": criteria_checked,
        "criteria_failed": criteria_failed,
        "criteria_missing": criteria_missing,
        "formal_result": formal_result,
        "risk_flags": sorted(set(risk_flags)),
        "suggested_next_step": suggested_next_step,
        "evidence": evidence,
    }
