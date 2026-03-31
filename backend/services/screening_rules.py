"""
Regelbasierte Screening-Logik für Bewerbervorprüfung.

Ziele:
- Saubere Trennung zwischen Vollständigkeit, formaler Vorprüfung, KI-Empfehlung und Staff-Entscheid.
- Keine faktische Anerkennungsentscheidung aus Upload-Existenz ableiten.
- Extern versionierte, dokumentierte Heuristik ohne Live-Anabin-Call.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
RULE_MATRIX_FILE = Path(__file__).resolve().parents[1] / "rules" / "screening_rule_matrix.v1.0.json"

REQUIRED_DOC_LABELS = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}
MIN_CLASSIFICATION_CONFIDENCE = 0.6


@lru_cache(maxsize=1)
def _load_rule_matrix_file() -> dict:
    with RULE_MATRIX_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_rule_set(version: Optional[str] = None) -> tuple[str, dict, dict]:
    payload = _load_rule_matrix_file()
    active_version = payload["active_version"]
    selected_version = version or active_version
    rule_sets = payload.get("versioned_rule_sets", {})
    if selected_version not in rule_sets:
        raise ValueError(f"Unbekannte Regelmatrix-Version: {selected_version}")
    return selected_version, rule_sets[selected_version], payload


def get_rule_matrix_versioning() -> dict:
    payload = _load_rule_matrix_file()
    return {
        "matrix_id": payload.get("matrix_id"),
        "matrix_semver": payload.get("matrix_semver"),
        "active_version": payload.get("active_version"),
        "deprecated_versions": payload.get("deprecated_versions", []),
    }


def get_active_rule_set() -> dict:
    version, rule_set, _ = _resolve_rule_set()
    return {"version": version, "rule_set": rule_set}


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


def _get_anabin_category(country: Optional[str], anabin_hints: dict) -> dict:
    if not country:
        return {"category": "unbekannt", "label": "Herkunftsland nicht angegeben – manuelle Prüfung erforderlich"}

    country_lower = country.lower().strip()
    if country_lower in anabin_hints.get("h_plus", []):
        return {
            "category": "H+",
            "label": f"Hohe Anerkennungswahrscheinlichkeit ({country}) – entspricht typischerweise deutschen Standards.",
        }
    if country_lower in anabin_hints.get("h", []):
        return {
            "category": "H",
            "label": f"Anerkennbar mit möglichen Auflagen ({country}) – Einzelfallprüfung empfohlen.",
        }
    if country_lower in anabin_hints.get("d", []):
        return {
            "category": "D",
            "label": f"Eingeschränkte Anerkennung ({country}) – intensive Einzelfallprüfung erforderlich.",
        }
    return {
        "category": "prüfen",
        "label": f"Herkunftsland '{country}' nicht in Standardreferenz – Anabin-Datenbank manuell prüfen.",
    }


def _check_language_level(course_type: Optional[str], language_level: Optional[str], course_rule_matrix: dict) -> dict:
    normalized = _normalize_level(language_level)
    if not course_type:
        return {"ok": False, "note": "Kurstyp nicht angegeben.", "required": None, "actual": normalized}

    required = (course_rule_matrix.get(course_type) or {}).get("language_min")
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


def _check_completeness(docs: list, course_type: Optional[str], course_rule_matrix: Optional[dict] = None) -> dict:
    course_rules = (course_rule_matrix or {}).get(course_type, {})
    required_types = course_rules.get("required_docs", ["language_certificate", "highschool_diploma", "passport"])
    uploaded_types = {}
    evidence = []

    for doc in docs:
        classified_type = doc.get("classified_type")
        doc_type = doc.get("document_type")
        if not classified_type:
            evidence.append(
                {
                    "declared_document_type": doc_type,
                    "classified_type": None,
                    "classification_confidence": float(doc.get("classification_confidence") or 0.0),
                    "quality_ok": False,
                    "type_mismatch": bool(doc.get("type_mismatch")),
                    "status": doc.get("status", "unknown"),
                    "bucket": _doc_status_bucket(doc.get("status")),
                    "source": "document_classification_missing",
                }
            )
            continue
        confidence = float(doc.get("classification_confidence") or 0.0)
        quality_ok = confidence >= MIN_CLASSIFICATION_CONFIDENCE
        status_bucket = _doc_status_bucket(doc.get("status"))
        if quality_ok:
            uploaded_types.setdefault(classified_type, set()).add(status_bucket)
        evidence.append(
            {
                "declared_document_type": doc_type,
                "classified_type": classified_type,
                "classification_confidence": confidence,
                "quality_ok": quality_ok,
                "type_mismatch": bool(doc.get("type_mismatch")),
                "status": doc.get("status", "unknown"),
                "bucket": status_bucket,
                "source": "document_classification",
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
        "total_required": len(required_types),
        "reasons": reasons,
        "evidence": evidence,
    }


def _build_formal_precheck(completeness: dict, language_check: dict, anabin_info: dict, application: dict) -> dict:
    evidence = [
        {"criterion": "degree_country", "value": application.get("degree_country"), "source": "application_form"},
        {"criterion": "course_type", "value": application.get("course_type"), "source": "application_form"},
        {"criterion": "language_level", "value": application.get("language_level"), "source": "application_form"},
        {"criterion": "anabin_category", "value": anabin_info["category"], "source": "versioned_rule_matrix"},
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


def _evaluate_rule(rule: dict, completeness: dict, language_check: dict, anabin_info: dict) -> dict:
    evaluation_key = rule.get("evaluation_key")
    if evaluation_key == "required_documents_complete":
        ok = completeness["complete"]
        detail = "; ".join(completeness["reasons"])
    elif evaluation_key == "language_minimum_met":
        ok = language_check["ok"]
        detail = language_check["note"]
    elif evaluation_key == "degree_country_classified":
        ok = anabin_info["category"] not in ("prüfen", "unbekannt")
        detail = anabin_info["label"]
    else:
        ok = False
        detail = f"Unbekannter Evaluator: {evaluation_key}"

    mapping_key = "pass" if ok else "fail"
    next_action = (rule.get("next_action_mapping") or {}).get(mapping_key)
    return {
        "rule_id": rule.get("rule_id"),
        "ok": ok,
        "detail": detail,
        "severity": rule.get("severity"),
        "scope": rule.get("scope"),
        "source": rule.get("source", {}),
        "next_action": next_action,
    }


def evaluate_screening_criteria(
    application: dict,
    applicant: dict,
    docs: list,
    matrix_version: Optional[str] = None,
) -> dict:
    resolved_version, rule_set, versioning_payload = _resolve_rule_set(matrix_version)
    course_rule_matrix = rule_set.get("course_rule_matrix", {})

    completeness = _check_completeness(docs, application.get("course_type"), course_rule_matrix)
    anabin_info = _get_anabin_category(application.get("degree_country"), rule_set.get("anabin_country_hints", {}))
    language_check = _check_language_level(application.get("course_type"), application.get("language_level"), course_rule_matrix)
    formal_precheck = _build_formal_precheck(completeness, language_check, anabin_info, application)

    rules = rule_set.get("rules", [])
    criteria_checked = [_evaluate_rule(rule, completeness, language_check, anabin_info) for rule in rules]
    criteria_failed = [c for c in criteria_checked if not c["ok"] and c.get("severity") == "critical"]

    criteria_missing = []
    if not completeness["complete"]:
        criteria_missing.append(
            {
                "rule_id": "docs_required_uploaded",
                "detail": ", ".join(completeness["missing_labels"]) or "nicht spezifiziert",
            }
        )

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
        "manual_only_rules": rule_set.get("manual_only_rules", []),
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
            "mode": "versioned_rule_matrix",
            "version": resolved_version,
            "matrix_id": versioning_payload.get("matrix_id"),
            "active_version": versioning_payload.get("active_version"),
            "deprecated_versions": versioning_payload.get("deprecated_versions", []),
            "rule_source": rule_set.get("source", {}),
            "live_reference_connected": False,
            "note": "Keine Live-Anbindung an externe Referenzsysteme; Ergebnisse sind Vorprüfungshinweise.",
        },
    }


DEFAULT_RULE_SET = get_active_rule_set()
COURSE_RULE_MATRIX = DEFAULT_RULE_SET["rule_set"].get("course_rule_matrix", {})
REQUIRED_DOCUMENT_TYPES = ["language_certificate", "highschool_diploma", "passport"]
