"""
Qualifizierungs-Engine – Automatische Pfad-Empfehlung basierend auf Anabin + Sprachniveau + Dokumentenstatus.

Entscheidungslogik (aus Pflichtenheft):
1. Anabin-Kategorie pruefen:
   - H+ / H-analog → Direkter Hochschulzugang (bei ausreichendem Sprachniveau)
   - H+/- (bedingt) → Feststellungspruefung (FSP) am Studienkolleg erforderlich
   - H- → Kein direkter Zugang → TestAS-Empfehlung ODER Berufsausbildung
   - D (Defizit) → Anpassungslehrgang / Berufsanerkennung

2. Sprachniveau pruefen:
   - < B1 → Auto-Trigger: Sprachkursangebot + Platzreservierung
   - B1 → Studienkolleg-Zugang (FSP-Vorbereitung)
   - B2 → Pflegeausbildung moeglich / Berufsanerkennung
   - C1/TestDaF TDN4 → Direktes Fachstudium moeglich

3. Bewerbungstyp bestimmt Pfad:
   - studienkolleg → FSP-Pipeline
   - sprachkurs → Sprachkurs-Pipeline
   - pflegeausbildung → Pflege-Pipeline (B2 + mittlerer Schulabschluss)
   - fachstudium → Direkt-Studium-Pipeline
"""
import logging
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
CEFR_INDEX = {lv: i for i, lv in enumerate(CEFR_LEVELS)}


def _cefr_gte(actual: str, required: str) -> bool:
    """Prueft ob actual >= required auf CEFR-Skala."""
    return CEFR_INDEX.get(actual, -1) >= CEFR_INDEX.get(required, 99)


def _cefr_lt(actual: str, required: str) -> bool:
    return CEFR_INDEX.get(actual, -1) < CEFR_INDEX.get(required, 99)


# ── Pfad-Empfehlungen ──────────────────────────────────────────────

PATH_STUDIENKOLLEG = "studienkolleg"
PATH_SPRACHKURS = "sprachkurs_zuerst"
PATH_FSP = "feststellungspruefung"
PATH_TESTAS = "testas"
PATH_DIREKTSTUDIUM = "direktstudium"
PATH_PFLEGEAUSBILDUNG = "pflegeausbildung"
PATH_BERUFSAUSBILDUNG = "berufsausbildung"
PATH_ANPASSUNGSLEHRGANG = "anpassungslehrgang"
PATH_MANUAL = "manuelle_pruefung"


async def compute_qualification_path(
    application: dict,
    applicant: dict,
    anabin_result: dict,
) -> dict:
    """
    Berechnet den empfohlenen Qualifizierungspfad.

    Returns:
        {
            "recommended_path": str,
            "path_label_de": str,
            "path_label_en": str,
            "reason_de": str,
            "reason_en": str,
            "next_steps_de": [str],
            "next_steps_en": [str],
            "language_sufficient": bool,
            "language_action": str | None,
            "anabin_category": str,
            "confidence": str,
            "requires_staff_decision": bool,
            "auto_triggers": [str],
        }
    """
    course_type = application.get("course_type", "")
    language_level = applicant.get("language_level") or application.get("language_level") or ""
    nationality = applicant.get("nationality", "")
    anabin_cat = (anabin_result.get("category") or "").upper().strip()
    anabin_confidence = anabin_result.get("confidence", "unknown")
    requires_staff = anabin_result.get("requires_staff_decision", False)

    auto_triggers = []
    result = {
        "anabin_category": anabin_cat,
        "confidence": anabin_confidence,
        "requires_staff_decision": requires_staff,
        "language_level": language_level,
        "course_type": course_type,
    }

    # ── Sprachniveau-Check ──────────────────────────────────────
    lang_sufficient = True
    lang_action = None

    if not language_level:
        lang_sufficient = False
        lang_action = "sprachniveau_unbekannt"
    elif _cefr_lt(language_level, "B1"):
        lang_sufficient = False
        lang_action = "sprachkurs_empfohlen"
        auto_triggers.append("auto_sprachkurs_angebot")
    elif _cefr_lt(language_level, "B2") and course_type.lower() in ("pflegeausbildung", "pflege"):
        lang_sufficient = False
        lang_action = "b2_fuer_pflege_erforderlich"
        auto_triggers.append("auto_sprachkurs_angebot")

    result["language_sufficient"] = lang_sufficient
    result["language_action"] = lang_action

    # ── Anabin-basierte Pfad-Logik ──────────────────────────────
    if anabin_cat in ("H+", "H+ ANALOG", "H+/H-"):
        # Direkter Hochschulzugang
        if lang_sufficient and _cefr_gte(language_level, "C1"):
            path = PATH_DIREKTSTUDIUM
            reason_de = f"Abschluss aus {nationality} ist als H+ (direkt anerkannt) eingestuft. Sprachniveau {language_level} genuegt fuer Direktstudium."
            reason_en = f"Degree from {nationality} classified as H+ (directly recognized). Language level {language_level} sufficient for direct study."
            steps_de = ["Hochschulbewerbung vorbereiten", "uni-assist Antrag stellen", "Zulassungsbescheid abwarten"]
            steps_en = ["Prepare university application", "Submit uni-assist application", "Wait for admission letter"]
        elif lang_sufficient and _cefr_gte(language_level, "B1"):
            path = PATH_STUDIENKOLLEG
            reason_de = f"Abschluss H+ anerkannt, aber Sprachniveau {language_level} reicht noch nicht fuer Direktstudium (C1 erforderlich). Studienkolleg empfohlen."
            reason_en = f"Degree H+ recognized, but language level {language_level} not yet sufficient for direct study (C1 required). Studienkolleg recommended."
            steps_de = ["Studienkolleg-Bewerbung einreichen", "FSP-Vorbereitungskurs belegen", "Sprachniveau auf C1 steigern"]
            steps_en = ["Submit Studienkolleg application", "Take FSP preparation course", "Improve language level to C1"]
        else:
            path = PATH_SPRACHKURS
            reason_de = f"Abschluss H+ anerkannt, aber Sprachniveau {language_level or 'unbekannt'} unter B1. Zuerst Sprachkurs erforderlich."
            reason_en = f"Degree H+ recognized, but language level {language_level or 'unknown'} below B1. Language course required first."
            steps_de = ["Sprachkurs A1-B1 buchen", "Pruefung ablegen", "Danach Studienkolleg oder Direktstudium"]
            steps_en = ["Book language course A1-B1", "Take exam", "Then Studienkolleg or direct study"]
            auto_triggers.append("auto_sprachkurs_angebot")

    elif anabin_cat in ("H+/-", "H-/+", "BEDINGT"):
        # Bedingter Zugang → Feststellungspruefung
        if lang_sufficient:
            path = PATH_FSP
            reason_de = f"Abschluss aus {nationality} bedingt anerkannt (Kategorie {anabin_cat}). Feststellungspruefung (FSP) am Studienkolleg erforderlich."
            reason_en = f"Degree from {nationality} conditionally recognized (category {anabin_cat}). Assessment exam (FSP) at Studienkolleg required."
            steps_de = ["Studienkolleg-Bewerbung einreichen", "Aufnahmetest absolvieren", "FSP-Vorbereitungskurs belegen", "FSP ablegen"]
            steps_en = ["Submit Studienkolleg application", "Complete entrance test", "Take FSP preparation course", "Take FSP exam"]
        else:
            path = PATH_SPRACHKURS
            reason_de = f"Abschluss bedingt anerkannt ({anabin_cat}), aber Sprachniveau {language_level or 'unbekannt'} unzureichend. Zuerst Sprachkurs."
            reason_en = f"Degree conditionally recognized ({anabin_cat}), but language level {language_level or 'unknown'} insufficient. Language course first."
            steps_de = ["Sprachkurs bis B1 absolvieren", "Danach Studienkolleg-Bewerbung"]
            steps_en = ["Complete language course to B1", "Then submit Studienkolleg application"]
            auto_triggers.append("auto_sprachkurs_angebot")

    elif anabin_cat in ("H-", "NICHT ANERKANNT"):
        # Kein direkter Zugang → TestAS oder Berufsausbildung
        if course_type.lower() in ("pflegeausbildung", "pflege"):
            path = PATH_PFLEGEAUSBILDUNG
            reason_de = f"Abschluss aus {nationality} nicht direkt fuer Hochschulzugang anerkannt ({anabin_cat}). Pflegeausbildung als Alternativpfad."
            reason_en = f"Degree from {nationality} not directly recognized for university ({anabin_cat}). Nursing training as alternative path."
            steps_de = ["B2-Sprachzertifikat erwerben", "Pflegeausbildung beantragen", "Anerkennung pruefen"]
            steps_en = ["Obtain B2 language certificate", "Apply for nursing training", "Check recognition"]
            if not _cefr_gte(language_level, "B2"):
                auto_triggers.append("auto_sprachkurs_angebot")
        else:
            path = PATH_TESTAS
            reason_de = f"Abschluss aus {nationality} nicht anerkannt ({anabin_cat}). TestAS empfohlen als Nachweis der Studierfaehigkeit."
            reason_en = f"Degree from {nationality} not recognized ({anabin_cat}). TestAS recommended as proof of study ability."
            steps_de = ["TestAS-Anmeldung vorbereiten", "TestAS ablegen", "Mit Ergebnis Hochschulbewerbung starten"]
            steps_en = ["Prepare TestAS registration", "Take TestAS", "Start university application with results"]
            auto_triggers.append("auto_testas_info")

    elif anabin_cat in ("D", "DEFIZIT"):
        # Berufsanerkennung / Anpassungslehrgang
        path = PATH_ANPASSUNGSLEHRGANG
        reason_de = f"Abschluss aus {nationality} mit Defizitbescheid ({anabin_cat}). Anpassungslehrgang oder Kenntnisspruefung erforderlich."
        reason_en = f"Degree from {nationality} with deficit notice ({anabin_cat}). Adaptation course or knowledge exam required."
        steps_de = ["Defizitbescheid von Behoerde einholen", "Anpassungslehrgang finden", "Fehlende Module nachholen"]
        steps_en = ["Obtain deficit notice from authority", "Find adaptation course", "Complete missing modules"]
        requires_staff = True

    else:
        # Unbekannt → manuelle Pruefung
        path = PATH_MANUAL
        reason_de = f"Anabin-Kategorie '{anabin_cat or 'unbekannt'}' fuer {nationality} nicht automatisch zuordenbar. Manuelle Pruefung durch Staff erforderlich."
        reason_en = f"Anabin category '{anabin_cat or 'unknown'}' for {nationality} cannot be automatically assigned. Manual staff review required."
        steps_de = ["Staff prueft Unterlagen manuell", "Ggf. Anabin-Wissensbasis ergaenzen"]
        steps_en = ["Staff reviews documents manually", "Update Anabin knowledge base if needed"]
        requires_staff = True

    # ── Path Labels ──────────────────────────────────────────────
    PATH_LABELS = {
        PATH_DIREKTSTUDIUM: ("Direktes Fachstudium", "Direct University Studies"),
        PATH_STUDIENKOLLEG: ("Studienkolleg (FSP-Vorbereitung)", "Studienkolleg (FSP Preparation)"),
        PATH_FSP: ("Feststellungspruefung (FSP)", "Assessment Exam (FSP)"),
        PATH_TESTAS: ("TestAS – Studierfaehigkeitstest", "TestAS – Study Aptitude Test"),
        PATH_SPRACHKURS: ("Sprachkurs zuerst", "Language Course First"),
        PATH_PFLEGEAUSBILDUNG: ("Pflegeausbildung", "Nursing Training"),
        PATH_BERUFSAUSBILDUNG: ("Berufsausbildung", "Vocational Training"),
        PATH_ANPASSUNGSLEHRGANG: ("Anpassungslehrgang", "Adaptation Course"),
        PATH_MANUAL: ("Manuelle Pruefung erforderlich", "Manual Review Required"),
    }

    label_de, label_en = PATH_LABELS.get(path, ("Unbekannt", "Unknown"))

    result.update({
        "recommended_path": path,
        "path_label_de": label_de,
        "path_label_en": label_en,
        "reason_de": reason_de,
        "reason_en": reason_en,
        "next_steps_de": steps_de,
        "next_steps_en": steps_en,
        "requires_staff_decision": requires_staff,
        "auto_triggers": auto_triggers,
    })

    # Persistieren
    db = get_db()
    from bson import ObjectId as ObjId
    app_id = application.get("id") or str(application.get("_id", ""))
    if app_id:
        await db.applications.update_one(
            {"_id": ObjId(app_id)},
            {"$set": {
                "qualification_path": result,
                "qualification_path_updated_at": datetime.now(timezone.utc).isoformat(),
            }},
        )
        logger.info(f"[QUALIFICATION] app={app_id} path={path} anabin={anabin_cat} lang={language_level}")

    return result


from datetime import datetime, timezone  # noqa: E402
