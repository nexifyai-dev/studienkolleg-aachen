"""
Regelbasierte Screening-Logik für Bewerbervorprüfung.

Ziele:
- Saubere Trennung zwischen Vollständigkeit, formaler Vorprüfung, KI-Empfehlung und Staff-Entscheid.
- Keine faktische Anerkennungsentscheidung aus Upload-Existenz ableiten.
- Lokale, dokumentierte Heuristik ohne Live-Anabin-Call.
"""
from typing import Optional

ANABIN_COUNTRY_HINTS = {
    "h_plus": [
        "deutschland", "österreich", "schweiz", "usa", "kanada", "australien",
        "großbritannien", "frankreich", "niederlande", "belgien", "schweden",
        "norwegen", "dänemark", "finnland", "japan", "südkorea", "neuseeland",
        "united states", "canada", "united kingdom", "france", "netherlands",
        "austria", "switzerland", "sweden", "norway", "denmark", "finland",
        "south korea", "australia", "new zealand",
    ],
    "h": [
        "china", "indien", "brasilien", "türkei", "russland", "ukraine",
        "ägypten", "marokko", "tunesien", "iran", "vietnam", "thailand",
        "mexico", "argentinien", "kolumbien", "chile", "indonesia", "malaysia",
        "india", "brazil", "turkey", "russia", "egypt", "morocco", "tunisia",
        "argentina", "colombia",
    ],
    "d": [
        "afghanistan", "irak", "syrien", "libyen", "somalia", "jemen",
        "eritrea", "äthiopien", "nigeria", "ghana", "kamerun", "senegal",
        "mali", "niger", "burkina faso", "demokratische republik kongo",
        "iraq", "syria", "libya", "yemen", "ethiopia", "cameroon",
    ],
}

COURSE_RULE_MATRIX = {
    "M-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
    },
    "T-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
    },
    "W-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
    },
    "M/T-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
    },
    "Language Course": {
        "language_min": "A1",
        "required_docs": ["passport"],
    },
}

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

REQUIRED_DOCUMENT_TYPES = ["language_certificate", "highschool_diploma", "passport"]
REQUIRED_DOC_LABELS = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}


def _normalize_level(level: Optional[str]) -> Optional[str]:
    if not level:
        return None
    clean = str(level).strip().upper()
    return clean if clean in CEFR_LEVELS else None


def _doc_status_bucket(doc_status: str) -> str:
    if doc_status in ("approved", "in_review", "uploaded"):
        return "present"
    if doc_status in ("rejected", "invalid"):
        return "invalid"
    return "unknown"


def _get_anabin_category(country: Optional[str]) -> dict:
    if not country:
        return {"category": "unbekannt", "label": "Herkunftsland nicht angegeben – manuelle Prüfung erforderlich"}

    country_lower = country.lower().strip()
    if country_lower in ANABIN_COUNTRY_HINTS["h_plus"]:
        return {
            "category": "H+",
            "label": f"Hohe Anerkennungswahrscheinlichkeit ({country}) – entspricht typischerweise deutschen Standards.",
        }
    if country_lower in ANABIN_COUNTRY_HINTS["h"]:
        return {
            "category": "H",
            "label": f"Anerkennbar mit möglichen Auflagen ({country}) – Einzelfallprüfung empfohlen.",
        }
    if country_lower in ANABIN_COUNTRY_HINTS["d"]:
        return {
            "category": "D",
            "label": f"Eingeschränkte Anerkennung ({country}) – intensive Einzelfallprüfung erforderlich.",
        }
    return {
        "category": "prüfen",
        "label": f"Herkunftsland '{country}' nicht in Standardreferenz – Anabin-Datenbank manuell prüfen.",
    }


def _check_language_level(course_type: Optional[str], language_level: Optional[str]) -> dict:
    normalized = _normalize_level(language_level)
    if not course_type:
        return {"ok": False, "note": "Kurstyp nicht angegeben.", "required": None, "actual": normalized}

    required = (COURSE_RULE_MATRIX.get(course_type) or {}).get("language_min")
    if not required:
        return {"ok": False, "note": "Kurstyp unbekannt – manuelle Prüfung.", "required": None, "actual": normalized}

    if not normalized:
        return {
            "ok": False,
            "note": "Sprachniveau fehlt oder ungültig.",
            "required": required,
            "actual": language_level,
        }

    required_idx = CEFR_LEVELS.index(required)
    actual_idx = CEFR_LEVELS.index(normalized)
    if actual_idx >= required_idx:
        return {
            "ok": True,
            "note": f"Sprachniveau {normalized} erfüllt Mindestanforderung {required} für {course_type}.",
            "required": required,
            "actual": normalized,
        }

    return {
        "ok": False,
        "note": f"Sprachniveau {normalized} unzureichend für {course_type} (Mindest: {required}).",
        "required": required,
        "actual": normalized,
    }


def _check_completeness(docs: list, course_type: Optional[str]) -> dict:
    course_rules = COURSE_RULE_MATRIX.get(course_type, {})
    required_types = course_rules.get("required_docs", REQUIRED_DOCUMENT_TYPES)
    uploaded_types = {}
    evidence = []

    for doc in docs:
        doc_type = doc.get("document_type")
        if not doc_type:
            continue
        status_bucket = _doc_status_bucket(doc.get("status"))
        uploaded_types.setdefault(doc_type, set()).add(status_bucket)
        evidence.append(
            {
                "document_type": doc_type,
                "status": doc.get("status", "unknown"),
                "bucket": status_bucket,
                "source": "uploaded_document_metadata",
            }
        )

    missing = [doc_type for doc_type in required_types if "present" not in uploaded_types.get(doc_type, set())]
    present = [doc_type for doc_type in required_types if "present" in uploaded_types.get(doc_type, set())]
    invalid = [doc_type for doc_type, states in uploaded_types.items() if "invalid" in states]

    reasons = (
        ["Alle Pflichtdokumente für diesen Kurstyp liegen mit prüfbarem Status vor."]
        if not missing
        else [f"Es fehlen Pflichtdokumente: {', '.join(REQUIRED_DOC_LABELS.get(t, t) for t in missing)}."]
    )

    return {
        "complete": len(missing) == 0,
        "missing_types": missing,
        "missing_labels": [REQUIRED_DOC_LABELS.get(doc_type, doc_type) for doc_type in missing],
        "present_labels": [REQUIRED_DOC_LABELS.get(doc_type, doc_type) for doc_type in present],
        "invalid_types": invalid,
        "required_types": required_types,
        "reasons": reasons,
        "evidence": evidence,
    }


def _build_formal_precheck(completeness: dict, language_check: dict, anabin_info: dict, application: dict) -> dict:
    evidence = [
        {"criterion": "degree_country", "value": application.get("degree_country"), "source": "application_form"},
        {"criterion": "course_type", "value": application.get("course_type"), "source": "application_form"},
        {"criterion": "language_level", "value": application.get("language_level"), "source": "application_form"},
        {"criterion": "anabin_category", "value": anabin_info["category"], "source": "local_rulebook_v1"},
    ]

    risks = []
    open_points = []
    reasons = []

    if not language_check["ok"]:
        risks.append("Sprachniveau unterschreitet Mindestanforderung oder ist unklar.")
        open_points.append("Valides Sprachzertifikat mit CEFR-Level erforderlich.")
    else:
        reasons.append("Sprachniveau erfüllt die Mindestanforderung.")

    if anabin_info["category"] == "D":
        risks.append("Herkunftsabschluss mit erhöhter Anerkennungsunsicherheit (D-Kategorie).")
        open_points.append("Manuelle Detailprüfung inkl. externer Referenzabgleich erforderlich.")
    elif anabin_info["category"] in ("prüfen", "unbekannt"):
        open_points.append("Herkunftsabschluss ist in lokaler Matrix nicht eindeutig zuordenbar.")
    else:
        reasons.append(f"Herkunftsland liegt in lokaler Kategorie {anabin_info['category']}.")

    if completeness["invalid_types"]:
        open_points.append("Mindestens ein Dokument liegt in abgelehntem/ungültigem Status vor.")

    if risks:
        status = "critical"
    elif open_points:
        status = "unclear"
    else:
        status = "plausible"

    return {
        "status": status,
        "reasons": reasons or ["Keine hinreichend belastbaren Positivkriterien vorhanden."],
        "risks": risks,
        "open_points": open_points,
        "evidence": evidence,
    }


def evaluate_screening_criteria(application: dict, applicant: dict, docs: list) -> dict:
    completeness = _check_completeness(docs, application.get("course_type"))
    anabin_info = _get_anabin_category(application.get("degree_country"))
    language_check = _check_language_level(application.get("course_type"), application.get("language_level"))
    formal_precheck = _build_formal_precheck(completeness, language_check, anabin_info, application)

    criteria_checked = [
        {
            "rule_id": "docs_required_uploaded",
            "ok": completeness["complete"],
            "detail": "; ".join(completeness["reasons"]),
        },
        {
            "rule_id": "language_min_met",
            "ok": language_check["ok"],
            "detail": language_check["note"],
        },
        {
            "rule_id": "degree_country_classified",
            "ok": anabin_info["category"] not in ("prüfen", "unbekannt"),
            "detail": anabin_info["label"],
        },
    ]

    criteria_failed = [
        c for c in criteria_checked if c["rule_id"] in {"language_min_met"} and not c["ok"]
    ]
    criteria_missing = [
        {
            "rule_id": "docs_required_uploaded",
            "detail": ", ".join(completeness["missing_labels"]) or "nicht spezifiziert",
        }
    ] if not completeness["complete"] else []

    if not completeness["complete"]:
        formal_result = "documents_missing"
        suggested_next_step = "request_missing_documents"
    elif not language_check["ok"]:
        formal_result = "language_gap"
        suggested_next_step = "request_language_proof_or_language_course"
    elif formal_precheck["status"] in ("critical", "unclear"):
        formal_result = "manual_review_required"
        suggested_next_step = "staff_manual_review"
    else:
        formal_result = "precheck_passed"
        suggested_next_step = "proceed_to_interview_or_consultation"

    risk_flags = list(dict.fromkeys(formal_precheck["risks"] + formal_precheck["open_points"]))

    return {
        "applicant_id": applicant.get("id") or application.get("applicant_id"),
        "completeness": completeness,
        "anabin_assessment": anabin_info,
        "language_level_check": language_check,
        "formal_precheck": formal_precheck,
        "criteria_checked": criteria_checked,
        "criteria_failed": criteria_failed,
        "criteria_missing": criteria_missing,
        "formal_result": formal_result,
        "risk_flags": risk_flags,
        "suggested_next_step": suggested_next_step,
        "evidence": {
            "application": {
                "course_type": application.get("course_type"),
                "degree_country": application.get("degree_country"),
                "language_level": application.get("language_level"),
            },
            "documents": completeness["evidence"],
            "formal_precheck": formal_precheck["evidence"],
        },
        "reference_basis": {
            "mode": "local_rulebook",
            "version": "screening_rules_v2",
            "live_reference_connected": False,
            "note": "Keine Live-Anbindung an externe Referenzsysteme; Ergebnisse sind Vorprüfungshinweise.",
        },
    }
