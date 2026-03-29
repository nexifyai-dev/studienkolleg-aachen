"""
KI-gestützte Bewerberprüfung (AI Application Screening)

Funktion:
- Vollständigkeit der Unterlagen prüfen
- Formale Eignung auf Basis von Anabin-Kriterien bewerten
- Kursempfehlung vorbereiten
- Risiken / Unklarheiten markieren
- Statusvorschlag + nächste Aktion generieren
- Audit-Trail speichern

Ausgabe: Auf Deutsch (Staff-Oberfläche)
Klaretrennung: AI suggestion vs. Staff decision vs. Final status
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Anabin-Referenzwissen (vereinfacht, architektonisch integriert)
# Quelle: https://anabin.kmk.org/db/schulabschluesse-mit-hochschulzugang
ANABIN_COUNTRY_HINTS = {
    # Kategorie H+ / H = volle Anerkennung wahrscheinlich
    "h_plus": [
        "deutschland", "österreich", "schweiz", "usa", "kanada", "australien",
        "großbritannien", "frankreich", "niederlande", "belgien", "schweden",
        "norwegen", "dänemark", "finnland", "japan", "südkorea", "neuseeland",
        "united states", "canada", "united kingdom", "france", "netherlands",
        "austria", "switzerland", "sweden", "norway", "denmark", "finland",
        "japan", "south korea", "australia", "new zealand",
    ],
    # Kategorie H = Anerkennung mit Einschränkungen
    "h": [
        "china", "indien", "brasilien", "türkei", "russland", "ukraine",
        "ägypten", "marokko", "tunesien", "iran", "vietnam", "thailand",
        "mexico", "argentinien", "kolumbien", "chile", "indonesia", "malaysia",
        "india", "brazil", "turkey", "russia", "egypt", "morocco", "tunisia",
        "china", "vietnam", "thailand", "mexico", "argentina", "colombia",
        "chile", "indonesia", "malaysia",
    ],
    # Kategorie D = Bedingte Anerkennung / Einzelfallprüfung erforderlich
    "d": [
        "afghanistan", "irak", "syrien", "libyen", "somalia", "jemen",
        "eritrea", "äthiopien", "nigeria", "ghana", "kamerun", "senegal",
        "mali", "niger", "burkina faso", "demokratische republik kongo",
        "iraq", "syria", "libya", "somalia", "yemen", "eritrea", "ethiopia",
        "nigeria", "ghana", "cameroon", "senegal",
    ],
}

# Kurs-Sprachanforderungen
COURSE_LANGUAGE_REQUIREMENTS = {
    "M-Course": "B1",
    "T-Course": "B1",
    "W-Course": "B1",
    "M/T-Course": "B1",
    "Language Course": "A1",
}

# CEFR-Level-Reihenfolge
CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

REQUIRED_DOCUMENT_TYPES = [
    "language_certificate",
    "highschool_diploma",
    "passport",
]

REQUIRED_DOC_LABELS = {
    "language_certificate": "Deutsches Sprachzertifikat",
    "highschool_diploma": "Schulzeugnis / Hochschulzugangsberechtigung",
    "passport": "Reisepass / Personalausweis",
}


def _get_anabin_category(country: Optional[str]) -> dict:
    """Gibt Anabin-Einschätzung für das Herkunftsland des Abschlusses zurück."""
    if not country:
        return {"category": "unbekannt", "label": "Herkunftsland nicht angegeben – manuelle Prüfung erforderlich"}
    country_lower = country.lower().strip()
    if country_lower in ANABIN_COUNTRY_HINTS["h_plus"]:
        return {
            "category": "H+",
            "label": f"Hohe Anerkennungswahrscheinlichkeit ({country}) – Abschluss entspricht typischerweise deutschen Standards.",
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
    """Prüft ob das Sprachniveau für den gewünschten Kurs ausreicht."""
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
            return {
                "ok": False,
                "note": f"Sprachniveau {language_level} unzureichend für {course_type} (Mindest: {required}). Vorgelagerter Sprachkurs empfohlen.",
            }
    except ValueError:
        return {"ok": False, "note": f"Ungültiges Sprachniveau '{language_level}' – manuelle Prüfung."}


def _check_completeness(docs: list) -> dict:
    """Prüft ob alle Pflichtdokumente vorhanden sind."""
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
    Führt KI-gestützte Vorprüfung durch.
    Gibt strukturiertes Prüfergebnis zurück und speichert es in der DB.
    """
    from config import EMERGENT_LLM_KEY, AI_SCREENING_ENABLED

    # Lokale Checks (unabhängig von LLM)
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

    if AI_SCREENING_ENABLED:
        try:
            from emergentintegrations.llm.chat import LlmChat, UserMessage

            # Kontext aufbauen
            doc_summary = ", ".join(
                f"{d.get('document_type')} ({d.get('status', 'unbekannt')})" for d in docs
            ) or "Keine Dokumente vorhanden"

            msg_summary = ""
            if messages:
                recent = messages[-5:]  # letzte 5 Nachrichten
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
- Anmerkungen vom Bewerber: {application.get('notes', 'Keine')}

ANABIN-EINSCHÄTZUNG (automatisch):
- Kategorie: {anabin_info['category']}
- Einschätzung: {anabin_info['label']}

SPRACHNIVEAU-PRÜFUNG (automatisch):
- Ausreichend: {language_check['ok']}
- Hinweis: {language_check['note']}

DOKUMENTE ({len(docs)} vorhanden):
{doc_summary}

FEHLENDE PFLICHTDOKUMENTE: {', '.join(completeness['missing_labels']) if completeness['missing_labels'] else 'Alle vorhanden'}

KOMMUNIKATIONSVERLAUF (letzte Nachrichten):
{msg_summary if msg_summary else 'Kein Verlauf vorhanden'}

Erstelle einen strukturierten Vorprüfungsbericht mit diesen Abschnitten:
1. VOLLSTÄNDIGKEIT: Beurteilung ob alle Unterlagen vorhanden und vollständig sind
2. FORMALE EIGNUNG: Bewertung der formalen Voraussetzungen (Sprachniveau, Herkunftsabschluss)
3. ANABIN-EINSCHÄTZUNG: Detailbewertung des Herkunftslandes und was das für die Zulassung bedeutet
4. KURSEMPFEHLUNG: Empfehlungen welcher Kurs am besten passt und warum
5. RISIKEN & UNKLARHEITEN: Was noch offen ist oder manuell geprüft werden muss
6. STATUSVORSCHLAG: Empfohlener nächster Status (lead_new / in_review / pending_docs / interview_scheduled / conditional_offer / offer_sent / enrolled / declined / on_hold)
7. NÄCHSTE AKTION: Konkrete nächste Schritte für das Staff-Team

WICHTIG: Alle Entscheidungen sind Empfehlungen. Die finale Entscheidung trifft das Staff-Team."""

            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"screening-{application.get('id', uuid.uuid4().hex)}",
                system_message=system_prompt,
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")

            response = await chat.send_message(UserMessage(text=user_prompt))
            ai_report = str(response)

        except Exception as e:
            logger.error(f"[AI_SCREENING] Fehler bei KI-Prüfung: {e}")
            ai_error = str(e)
    else:
        ai_report = "KI-Prüfung nicht verfügbar (EMERGENT_LLM_KEY nicht konfiguriert). Lokale Prüfung abgeschlossen."

    # Statusvorschlag (regelbasiert, ergänzt durch KI)
    suggested_stage = _suggest_stage(completeness, language_check, anabin_info)

    result = {
        "screening_id": str(uuid.uuid4()),
        "application_id": application.get("id"),
        "screened_at": datetime.now(timezone.utc).isoformat(),
        "screened_by": "ai_system",
        "local_checks": local_summary,
        "ai_report": ai_report,
        "ai_error": ai_error,
        "suggested_stage": suggested_stage,
        "is_complete": completeness["complete"],
        "missing_documents": completeness["missing_labels"],
        "anabin_category": anabin_info["category"],
        "language_level_ok": language_check["ok"],
        "decision_note": "KI-Vorprüfung. Keine bindende Entscheidung. Staff-Review erforderlich.",
    }
    return result


def _suggest_stage(completeness: dict, language_check: dict, anabin_info: dict) -> str:
    """Regelbasierter Statusvorschlag."""
    if not completeness["complete"]:
        return "pending_docs"
    if not language_check["ok"]:
        return "in_review"
    if anabin_info["category"] == "D":
        return "in_review"
    if anabin_info["category"] in ("H", "H+"):
        return "in_review"
    return "in_review"
