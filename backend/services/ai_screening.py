"""
KI-gestützte Bewerberprüfung (AI Application Screening)

Provider: DeepSeek – alle KI-Inferenzen laufen über DeepSeek.
Kein anderer Modellprovider wird für Produktiv-KI genutzt.

Funktion:
- Vollständigkeit der Unterlagen prüfen (regelbasiert)
- Formale Eignung auf Basis von Anabin-Kriterien bewerten (regelbasiert)
- Kursempfehlung vorbereiten (KI-gestützt via DeepSeek)
- Risiken / Unklarheiten markieren (KI-gestützt via DeepSeek)
- Statusvorschlag + nächste Aktion generieren
- Audit-Trail speichern

Modellstrategie:
- Screening-Hauptanalyse: Qwen/Qwen3-235B-A22B-Instruct-2507 (stärkstes Modell)
- Fallback: meta-llama/Llama-3.3-70B-Instruct

Ausgabe: Auf Deutsch (Staff-Oberfläche)
Klare Trennung: AI suggestion vs. Staff decision vs. Final status
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Lokale Referenzbasis (kein Live-Anabin-Call)
# Hinweis: Diese Matrix ist eine dokumentierte Offline-Heuristik zur Vorprüfung.
# Sie ersetzt keine offizielle, tagesaktuelle Anerkennungsprüfung.
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

COURSE_RULE_MATRIX = {
    "M-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
        "preferred_docs": ["transcript", "university_record"],
        "focus": "mathematisch-naturwissenschaftliches Profil",
    },
    "T-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
        "preferred_docs": ["transcript", "university_record"],
        "focus": "technisch-naturwissenschaftliches Profil",
    },
    "W-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
        "preferred_docs": ["transcript", "university_record"],
        "focus": "wirtschaftswissenschaftliches Profil",
    },
    "M/T-Course": {
        "language_min": "B1",
        "required_docs": ["language_certificate", "highschool_diploma", "passport"],
        "preferred_docs": ["transcript", "university_record"],
        "focus": "hybrides M/T-Profil",
    },
    "Language Course": {
        "language_min": "A1",
        "required_docs": ["passport"],
        "preferred_docs": ["language_certificate", "highschool_diploma"],
        "focus": "Spracherwerb vor Fachkurs",
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
    if doc_status == "approved":
        return "verified"
    if doc_status in ("in_review", "uploaded"):
        return "provisional"
    if doc_status in ("rejected", "invalid"):
        return "invalid"
    return "unknown"


def _get_anabin_category(country: Optional[str]) -> dict:
    if not country:
        return {"category": "unbekannt", "label": "Herkunftsland nicht angegeben – manuelle Prüfung erforderlich"}
    country_lower = country.lower().strip()
    if country_lower in ANABIN_COUNTRY_HINTS["h_plus"]:
        return {"category": "H+", "label": f"Hohe Anerkennungswahrscheinlichkeit ({country}) – entspricht typischerweise deutschen Standards."}
    if country_lower in ANABIN_COUNTRY_HINTS["h"]:
        return {"category": "H", "label": f"Anerkennbar mit möglichen Auflagen ({country}) – Einzelfallprüfung empfohlen."}
    if country_lower in ANABIN_COUNTRY_HINTS["d"]:
        return {"category": "D", "label": f"Eingeschränkte Anerkennung ({country}) – intensive Einzelfallprüfung erforderlich."}
    return {"category": "prüfen", "label": f"Herkunftsland '{country}' nicht in Standardreferenz – Anabin-Datenbank manuell prüfen."}


def _check_language_level(course_type: Optional[str], language_level: Optional[str]) -> dict:
    normalized = _normalize_level(language_level)
    if not course_type:
        return {"ok": False, "note": "Kurstyp nicht angegeben.", "required": None, "actual": normalized}
    required = (COURSE_RULE_MATRIX.get(course_type) or {}).get("language_min")
    if not required:
        return {"ok": False, "note": "Kurstyp unbekannt – manuelle Prüfung.", "required": None, "actual": normalized}
    if not normalized:
        return {"ok": False, "note": "Sprachniveau fehlt oder ungültig.", "required": required, "actual": language_level}
    try:
        required_idx = CEFR_LEVELS.index(required)
        actual_idx = CEFR_LEVELS.index(normalized)
        if actual_idx >= required_idx:
            return {"ok": True, "note": f"Sprachniveau {normalized} erfüllt Mindestanforderung {required} für {course_type}.", "required": required, "actual": normalized}
        return {
            "ok": False,
            "note": f"Sprachniveau {normalized} unzureichend für {course_type} (Mindest: {required}).",
            "required": required,
            "actual": normalized,
        }
    except ValueError:
        return {"ok": False, "note": f"Ungültiges Sprachniveau '{language_level}' – manuelle Prüfung.", "required": required, "actual": language_level}


def _check_completeness(docs: list, course_type: Optional[str]) -> dict:
    course_rules = COURSE_RULE_MATRIX.get(course_type, {})
    required_types = course_rules.get("required_docs", REQUIRED_DOCUMENT_TYPES)
    uploaded_types = {}
    evidence = []
    for d in docs:
        doc_type = d.get("document_type")
        if not doc_type:
            continue
        status_bucket = _doc_status_bucket(d.get("status"))
        uploaded_types.setdefault(doc_type, set()).add(status_bucket)
        evidence.append({
            "document_type": doc_type,
            "status": d.get("status", "unknown"),
            "bucket": status_bucket,
            "source": "uploaded_document_metadata",
        })

    missing = [
        t for t in required_types
        if t not in uploaded_types or not uploaded_types.get(t, set()).intersection({"verified", "provisional"})
    ]
    present = [
        t for t in required_types
        if t in uploaded_types and uploaded_types.get(t, set()).intersection({"verified", "provisional"})
    ]
    verified = [t for t in required_types if t in uploaded_types and "verified" in uploaded_types.get(t, set())]
    unverified = [t for t in required_types if t in uploaded_types and "verified" not in uploaded_types.get(t, set())]
    invalid = [t for t, states in uploaded_types.items() if "invalid" in states]
    reasons = []
    if missing:
        reasons.append(f"Es fehlen Pflichtdokumente: {', '.join(REQUIRED_DOC_LABELS.get(t, t) for t in missing)}.")
    else:
        reasons.append("Alle Pflichtdokumente wurden hochgeladen oder zur Prüfung eingereicht.")
    if unverified:
        reasons.append(
            f"Folgende Pflichtdokumente sind noch nicht verifiziert: {', '.join(REQUIRED_DOC_LABELS.get(t, t) for t in unverified)}."
        )
    return {
        "complete": len(missing) == 0,
        "missing_types": missing,
        "missing_labels": [REQUIRED_DOC_LABELS[t] for t in missing],
        "present_labels": [REQUIRED_DOC_LABELS[t] for t in present],
        "verified_types": verified,
        "verified_labels": [REQUIRED_DOC_LABELS[t] for t in verified],
        "unverified_types": unverified,
        "unverified_labels": [REQUIRED_DOC_LABELS[t] for t in unverified],
        "invalid_types": invalid,
        "required_types": required_types,
        "total_required": len(required_types),
        "total_present": len(present),
        "total_verified": len(verified),
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

    if completeness.get("invalid_types"):
        open_points.append("Mindestens ein Dokument liegt in abgelehntem/ungültigem Status vor.")

    if completeness.get("unverified_types"):
        open_points.append("Pflichtdokumente sind vorhanden, aber noch nicht fachlich verifiziert.")

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


async def run_ai_screening(
    application: dict,
    applicant: dict,
    docs: list,
    messages: list,
) -> dict:
    """
    KI-gestützte Vorprüfung via DeepSeek.
    Alle KI-Inferenzen laufen über DeepSeek.
    """
    from services.deepseek_provider import chat_completion, is_enabled

    # Lokale regelbasierte Checks
    completeness = _check_completeness(docs, application.get("course_type"))
    anabin_info = _get_anabin_category(application.get("degree_country"))
    language_check = _check_language_level(
        application.get("course_type"),
        application.get("language_level"),
    )

    formal_precheck = _build_formal_precheck(completeness, language_check, anabin_info, application)

    local_summary = {
        "completeness": completeness,
        "anabin_assessment": anabin_info,
        "language_level_check": language_check,
        "formal_precheck": formal_precheck,
        "reference_basis": {
            "mode": "local_rulebook",
            "version": "screening_rules_v1",
            "live_reference_connected": False,
            "note": "Keine Live-Anbindung an externe Referenzsysteme; Ergebnisse sind Vorprüfungshinweise.",
        },
    }

    ai_report = None
    ai_error = None
    ai_model_used = None
    ai_tokens_used = 0

    if is_enabled():
        try:
            doc_summary = ", ".join(
                f"{d.get('document_type')} ({d.get('status', 'unbekannt')})" for d in docs
            ) or "Keine Dokumente vorhanden"

            msg_summary = ""
            if messages:
                recent = messages[-5:]
                msg_summary = "\n".join(
                    f"- [{m.get('created_at', '')}] {m.get('content', '')[:200]}" for m in recent
                )

            system_prompt = """Du bist ein erfahrener Sachbearbeiter bei einem deutschen Studienkolleg.
Du führst eine formale Vorprüfung von Bewerbungen durch.
Antworte IMMER auf Deutsch.
Sei präzise, fachlich korrekt und strukturiert.
Trenne klar zwischen: KI-Einschätzung, Empfehlung und notwendiger manueller Prüfung.
Keine Endentscheidungen – nur Vorprüfung und Empfehlungen für Staff."""

            user_prompt = f"""Bitte prüfe folgende Bewerbung für das Studienkolleg Aachen und erstelle einen strukturierten Vorprüfungsbericht.

BEWERBERDATEN:
- Name: {applicant.get('full_name', 'Unbekannt')}
- Land: {applicant.get('country', 'Nicht angegeben')}
- Geburtsdatum: {application.get('date_of_birth', 'Nicht angegeben')}
- Gewünschter Kurs: {application.get('course_type', 'Nicht angegeben')}
- Wunschsemester: {application.get('desired_start', 'Nicht angegeben')}
- Deutschniveau: {application.get('language_level', 'Nicht angegeben')}
- Land des letzten Abschlusses: {application.get('degree_country', 'Nicht angegeben')}
- Anmerkungen: {application.get('notes', 'Keine')}

ANABIN-EINSCHÄTZUNG (automatisch):
- Kategorie: {anabin_info['category']}
- Einschätzung: {anabin_info['label']}

SPRACHNIVEAU-PRÜFUNG (automatisch):
- Ausreichend: {language_check['ok']}
- Hinweis: {language_check['note']}

DOKUMENTE ({len(docs)} vorhanden):
{doc_summary}

FEHLENDE PFLICHTDOKUMENTE: {', '.join(completeness['missing_labels']) if completeness['missing_labels'] else 'Alle vorhanden'}

KOMMUNIKATIONSVERLAUF:
{msg_summary if msg_summary else 'Kein Verlauf vorhanden'}

Erstelle einen strukturierten Vorprüfungsbericht:
1. VOLLSTÄNDIGKEIT: Beurteilung der Unterlagen
2. FORMALE EIGNUNG: Sprachniveau, Herkunftsabschluss
3. ANABIN-EINSCHÄTZUNG: Detailbewertung Herkunftsland
4. KURSEMPFEHLUNG: Passender Kurs und Begründung
5. RISIKEN & UNKLARHEITEN: Offene Punkte
6. STATUSVORSCHLAG: Empfohlener nächster Status
7. NÄCHSTE AKTION: Konkrete Schritte für Staff

WICHTIG: Alle Entscheidungen sind Empfehlungen. Finale Entscheidung trifft das Staff-Team."""

            result = await chat_completion(
                task="screening",
                system_message=system_prompt,
                user_message=user_prompt,
            )

            if result["content"]:
                ai_report = result["content"]
                ai_model_used = result["model"]
                ai_tokens_used = result["tokens_used"]
            else:
                ai_error = result.get("error", "Unbekannter Fehler")

        except Exception as e:
            logger.error(f"[AI_SCREENING] DeepSeek error: {e}")
            ai_error = str(e)
    else:
        ai_report = "KI-Prüfung nicht verfügbar (DEEPSEEK_API_KEY nicht konfiguriert). Lokale Vorprüfung abgeschlossen."

    suggested_stage = _suggest_stage(completeness, formal_precheck)

    precheck_status = "ok" if completeness["complete"] and formal_precheck["status"] == "plausible" else "action_required"
    formal_precheck_status = formal_precheck["status"]
    next_actions = _suggest_next_actions(completeness, formal_precheck, suggested_stage)

    return {
        "screening_id": str(uuid.uuid4()),
        "application_id": application.get("id"),
        "screened_at": datetime.now(timezone.utc).isoformat(),
        "screened_by": "ai_system",
        "ai_provider": "deepseek",
        "ai_model": ai_model_used,
        "ai_tokens_used": ai_tokens_used,
        "local_checks": local_summary,
        "screening_breakdown": {
            "completeness": {
                "status": "complete" if completeness["complete"] else "incomplete",
                "missing_documents": completeness["missing_labels"],
                "present_documents": completeness["present_labels"],
                "verified_documents": completeness["verified_labels"],
                "unverified_documents": completeness["unverified_labels"],
                "reasons": completeness["reasons"],
                "evidence": completeness["evidence"],
            },
            "formal_precheck": {
                "status": formal_precheck_status,
                "language_level_ok": language_check["ok"],
                "anabin_category": anabin_info["category"],
                "notes": [language_check["note"], anabin_info["label"]],
                "reasons": formal_precheck["reasons"],
                "risks": formal_precheck["risks"],
                "open_points": formal_precheck["open_points"],
                "evidence": formal_precheck["evidence"],
            },
            "ai_recommendation": {
                "suggested_stage": suggested_stage,
                "status": "available" if ai_report else "unavailable",
                "note": "Nur Empfehlung – keine finale Zulassungsentscheidung.",
                "next_actions": next_actions,
            },
            "staff_decision": {
                "status": "pending",
                "note": "Finale Entscheidung erfolgt ausschließlich durch Staff.",
                "required_confirmation": [
                    "Manuelle Prüfung aller kritischen/unklaren Punkte",
                    "Explizite Staff-Freigabe des finalen Stages",
                ],
            },
        },
        "precheck_status": precheck_status,
        "ai_report": ai_report,
        "ai_error": ai_error,
        "suggested_stage": suggested_stage,
        "is_complete": completeness["complete"],
        "missing_documents": completeness["missing_labels"],
        "anabin_category": anabin_info["category"],
        "language_level_ok": language_check["ok"],
        "next_actions": next_actions,
        "reference_basis": local_summary["reference_basis"],
        "decision_note": "KI-Vorprüfung via DeepSeek. Keine bindende Entscheidung. Staff-Review erforderlich.",
    }


def _suggest_stage(completeness: dict, formal_precheck: dict) -> str:
    if not completeness["complete"]:
        return "pending_docs"
    if formal_precheck["status"] == "critical":
        return "on_hold"
    if formal_precheck["status"] == "unclear":
        return "in_review"
    return "interview_scheduled"


def _suggest_next_actions(completeness: dict, formal_precheck: dict, suggested_stage: str) -> list:
    actions = []
    if not completeness["complete"]:
        actions.append("Fehlende Pflichtunterlagen beim Bewerber anfordern.")
    if completeness.get("unverified_types"):
        actions.append("Eingereichte Pflichtdokumente fachlich prüfen und verifizieren, bevor eine finale Eignung angenommen wird.")
    if completeness.get("invalid_types"):
        actions.append("Ungültige/abgelehnte Dokumente durch neue Nachweise ersetzen lassen.")
    if formal_precheck["status"] == "critical":
        actions.append("Fall an erfahrenes Staff-Mitglied zur vertieften Anerkennungsprüfung eskalieren.")
    if formal_precheck["status"] in ("critical", "unclear"):
        actions.append("Externe Referenzprüfung (z. B. Anabin) manuell durchführen und dokumentieren.")
    if formal_precheck["status"] == "plausible":
        actions.append("Interview oder Beratungsgespräch terminieren und Ergebnis dokumentieren.")
    actions.append(f"Staff entscheidet final über Stage-Wechsel ({suggested_stage}).")
    return actions
