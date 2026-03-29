"""
KI-gestützte Bewerberprüfung (AI Application Screening)

Provider: nscale (NSCall) – alle KI-Inferenzen laufen über die nscale API.
Kein anderer Modellprovider wird für Produktiv-KI genutzt.

Funktion:
- Vollständigkeit der Unterlagen prüfen (regelbasiert)
- Formale Eignung auf Basis von Anabin-Kriterien bewerten (regelbasiert)
- Kursempfehlung vorbereiten (KI-gestützt via nscale)
- Risiken / Unklarheiten markieren (KI-gestützt via nscale)
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

# Anabin-Referenzwissen (vereinfacht)
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

COURSE_LANGUAGE_REQUIREMENTS = {
    "M-Course": "B1", "T-Course": "B1", "W-Course": "B1",
    "M/T-Course": "B1", "Language Course": "A1",
}

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

REQUIRED_DOCUMENT_TYPES = ["language_certificate", "highschool_diploma", "passport"]
REQUIRED_DOC_LABELS = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}


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
    if not course_type or not language_level:
        return {"ok": False, "note": "Kurstyp oder Sprachniveau nicht angegeben."}
    required = COURSE_LANGUAGE_REQUIREMENTS.get(course_type)
    if not required:
        return {"ok": True, "note": "Kurstyp unbekannt – manuelle Prüfung."}
    try:
        required_idx = CEFR_LEVELS.index(required)
        actual_idx = CEFR_LEVELS.index(language_level)
        if actual_idx >= required_idx:
            return {"ok": True, "note": f"Sprachniveau {language_level} erfüllt Mindestanforderung {required} für {course_type}."}
        else:
            return {"ok": False, "note": f"Sprachniveau {language_level} unzureichend für {course_type} (Mindest: {required}). Vorgelagerter Sprachkurs empfohlen."}
    except ValueError:
        return {"ok": False, "note": f"Ungültiges Sprachniveau '{language_level}' – manuelle Prüfung."}


def _check_completeness(docs: list) -> dict:
    uploaded_types = {d.get("document_type") for d in docs if d.get("status") not in ("rejected",)}
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


async def run_ai_screening(
    application: dict,
    applicant: dict,
    docs: list,
    messages: list,
) -> dict:
    """
    KI-gestützte Vorprüfung via nscale (NSCall).
    Alle KI-Inferenzen laufen über die nscale-API.
    """
    from services.nscale_provider import chat_completion, is_enabled

    # Lokale regelbasierte Checks
    completeness = _check_completeness(docs)
    anabin_info = _get_anabin_category(application.get("degree_country"))
    language_check = _check_language_level(
        application.get("course_type"),
        application.get("language_level"),
    )

    local_summary = {
        "completeness": completeness,
        "anabin_assessment": anabin_info,
        "language_level_check": language_check,
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
            logger.error(f"[AI_SCREENING] nscale error: {e}")
            ai_error = str(e)
    else:
        ai_report = "KI-Prüfung nicht verfügbar (NSCALE_API_KEY nicht konfiguriert). Lokale Prüfung abgeschlossen."

    suggested_stage = _suggest_stage(completeness, language_check, anabin_info)

    return {
        "screening_id": str(uuid.uuid4()),
        "application_id": application.get("id"),
        "screened_at": datetime.now(timezone.utc).isoformat(),
        "screened_by": "ai_system",
        "ai_provider": "nscale",
        "ai_model": ai_model_used,
        "ai_tokens_used": ai_tokens_used,
        "local_checks": local_summary,
        "ai_report": ai_report,
        "ai_error": ai_error,
        "suggested_stage": suggested_stage,
        "is_complete": completeness["complete"],
        "missing_documents": completeness["missing_labels"],
        "anabin_category": anabin_info["category"],
        "language_level_ok": language_check["ok"],
        "decision_note": "KI-Vorprüfung via nscale. Keine bindende Entscheidung. Staff-Review erforderlich.",
    }


def _suggest_stage(completeness: dict, language_check: dict, anabin_info: dict) -> str:
    if not completeness["complete"]:
        return "pending_docs"
    if not language_check["ok"]:
        return "in_review"
    if anabin_info["category"] == "D":
        return "in_review"
    if anabin_info["category"] in ("H", "H+"):
        return "in_review"
    return "in_review"
