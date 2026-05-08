"""
Autonome KI-Dokumentenvalidierungs-Pipeline (v2.0).

Architektur:
  Upload → Sicherheitspruefung → Vision-Analyse (Llama-4-Scout)
  → Klassifikation → Echtheitsbewertung → Datenextraktion
  → DB-Feld-Mapping → Wissensabgleich → KI-Pruefbericht

Vision-Provider: nscale Llama-4-Scout-17B (Multimodal)
Text-Provider: DeepSeek (Strukturierte Analyse)

Dokumenttypen:
  - passport: Reisepass / Personalausweis
  - highschool_diploma: Schulabschlusszeugnis
  - transcript: Notenuebersicht / Transcript
  - language_certificate: Sprachzertifikat (Goethe, TestDaF, telc, DSH)
  - photo: Passfoto
  - receipt: Zahlungsbeleg
  - other: Sonstiges / Nicht erkannt

Status-Codes:
  - validated: Dokument erkannt, geeignet, lesbar
  - needs_review: Automatisch nicht sicher → Staff-Review
  - rejected: Kein gueltiges Dokument / offensichtlich falsch
  - processing: Validierung laeuft
  - error: Technischer Fehler bei Validierung
"""
import logging
import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Zentrale Typ-Definitionen
VALID_DOC_TYPES = frozenset([
    "passport", "highschool_diploma", "transcript",
    "language_certificate", "photo", "receipt", "other",
])

VALIDATION_STATUSES = frozenset([
    "validated", "needs_review", "rejected",
    "processing", "error", "uploaded",
])

DOC_TYPE_LABELS = {
    "de": {
        "passport": "Reisepass / Ausweis",
        "highschool_diploma": "Schulabschlusszeugnis",
        "transcript": "Notenuebersicht",
        "language_certificate": "Sprachzertifikat",
        "photo": "Passfoto",
        "receipt": "Zahlungsbeleg",
        "other": "Sonstiges",
    },
    "en": {
        "passport": "Passport / ID",
        "highschool_diploma": "High School Diploma",
        "transcript": "Transcript / Grades",
        "language_certificate": "Language Certificate",
        "photo": "Passport Photo",
        "receipt": "Payment Receipt",
        "other": "Other",
    },
}

REJECTION_REASONS = {
    "de": {
        "empty_file": "Die Datei ist leer oder beschaedigt.",
        "wrong_type": "Der Dokumenttyp stimmt nicht mit dem erkannten Inhalt ueberein.",
        "unreadable": "Das Dokument ist nicht lesbar (zu unscharf, abgeschnitten oder falsch formatiert).",
        "irrelevant": "Das hochgeladene Bild ist kein erkennbares Dokument.",
        "too_small": "Die Datei ist zu klein fuer ein gueltiges Dokument.",
        "no_text": "Aus dem PDF konnte kein Text extrahiert werden.",
        "fraudulent": "Das Dokument weist Anzeichen von Faelschung oder Manipulation auf.",
    },
    "en": {
        "empty_file": "The file is empty or corrupted.",
        "wrong_type": "The document type does not match the detected content.",
        "unreadable": "The document is not readable.",
        "irrelevant": "The uploaded image is not a recognizable document.",
        "too_small": "The file is too small for a valid document.",
        "no_text": "No text could be extracted from the PDF.",
        "fraudulent": "The document shows signs of forgery or manipulation.",
    },
}

MIN_FILE_SIZES = {
    "passport": 30_000,
    "highschool_diploma": 20_000,
    "transcript": 15_000,
    "language_certificate": 20_000,
    "photo": 10_000,
    "receipt": 5_000,
    "other": 1_000,
}

# Felder die aus Dokumenten extrahiert und auf die Application gemappt werden
EXTRACTABLE_FIELDS = {
    "passport": [
        "full_name", "date_of_birth", "nationality", "passport_number",
        "issuing_country", "expiry_date", "gender",
    ],
    "highschool_diploma": [
        "full_name", "institution_name", "issuing_country",
        "graduation_date", "degree_type", "gpa_or_grade",
        "subjects",
    ],
    "transcript": [
        "full_name", "institution_name", "issuing_country",
        "subjects_and_grades", "gpa_or_grade", "semester",
    ],
    "language_certificate": [
        "full_name", "language_level", "certificate_type",
        "issuing_institution", "exam_date", "score",
        "issuing_country",
    ],
}

# DB-Feld-Mapping: Extrahiertes Feld → Application-Feld
FIELD_TO_APPLICATION_MAP = {
    "full_name": "extracted_full_name",
    "date_of_birth": "extracted_date_of_birth",
    "nationality": "extracted_nationality",
    "issuing_country": "extracted_issuing_country",
    "language_level": "extracted_language_level",
    "certificate_type": "extracted_certificate_type",
    "institution_name": "extracted_institution",
    "graduation_date": "extracted_graduation_date",
    "degree_type": "extracted_degree_type",
    "gpa_or_grade": "extracted_gpa",
    "subjects_and_grades": "extracted_subjects",
}


def compute_file_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:32]


def _extract_pdf_text(data: bytes) -> str:
    try:
        from io import BytesIO
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(data))
        text = ""
        for page in reader.pages[:5]:
            text += (page.extract_text() or "")
        return text[:5000]
    except Exception as e:
        logger.warning(f"[DOC_VALIDATION] PDF-Text-Extraktion fehlgeschlagen: {e}")
        return ""


def _safe_parse_json(text: str) -> Optional[dict]:
    """Extrahiert JSON aus KI-Antworten (auch wenn in Markdown-Bloecke eingebettet)."""
    if not text:
        return None
    # Versuche direkt
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Suche nach JSON-Block in Markdown
    match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Suche nach erstem { bis letztem }
    start = text.find('{')
    end = text.rfind('}')
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    return None


# ══════════════════════════════════════════════════════════════════════
# VISION-ANALYSE: Bilder und PDF-Seiten mit Llama-4-Scout analysieren
# ══════════════════════════════════════════════════════════════════════

VISION_CLASSIFICATION_PROMPT = """Du bist ein hochpraezises Dokumentenerkennungssystem fuer ein deutsches Studienkolleg.
Analysiere das vorgelegte Dokument-Bild und antworte AUSSCHLIESSLICH im JSON-Format.

WICHTIG: Sei extrem streng bei der Echtheitsbewertung.
- Ein Foto einer Landschaft ist KEIN Reisepass.
- Ein Screenshot einer Website ist KEIN Zeugnis.
- Ein Einkaufszettel oder eine Notiz ist KEIN offizielles Dokument.
- Nur echte, offizielle Dokumente (Paesse, Zeugnisse, Zertifikate) als solche erkennen.

Antwortstruktur (STRIKT JSON):
{
  "document_type": "passport|highschool_diploma|transcript|language_certificate|photo|receipt|other",
  "confidence": "high|medium|low",
  "is_authentic_document": true/false,
  "authenticity_reasoning": "Begruendung der Echtheitsbewertung auf Deutsch",
  "issuing_country": "Landesname oder 'unbekannt'",
  "issuing_country_code": "ISO 3166-1 alpha-2 oder 'XX'",
  "document_language": "Sprache des Dokuments",
  "readability": "high|medium|low",
  "visual_quality": "Kurze Bewertung der Bildqualitaet",
  "detected_elements": ["Liste erkannter Elemente: Wappen, Stempel, MRZ, Noten, etc."],
  "issues": ["Liste von Problemen oder Auffaelligkeiten"],
  "summary": "Kurze Zusammenfassung auf Deutsch"
}"""

VISION_EXTRACTION_PROMPT_TEMPLATE = """Du bist ein praezises OCR- und Datenextraktionssystem.
Extrahiere alle relevanten strukturierten Daten aus diesem {doc_type_label}.

Antworte AUSSCHLIESSLICH im JSON-Format mit folgenden Feldern (sofern erkennbar):
{{
  {fields_json}
  "raw_text_excerpt": "Die ersten 500 Zeichen des erkannten Textes",
  "extraction_confidence": "high|medium|low",
  "extraction_notes": "Hinweise zu unsicheren Extraktionen"
}}

Regeln:
- Datumsformate: DD.MM.YYYY
- Namen: Vor- und Nachname getrennt wenn moeglich
- Noten: Im Originalformat des Dokuments
- Sprachniveau: CEFR-Format (A1-C2) wenn moeglich
- Bei Unsicherheit: Feld mit null belassen und in extraction_notes erwaehnen"""


async def _run_vision_classification(image_data: bytes, content_type: str) -> Optional[dict]:
    """Klassifiziert ein Dokument-Bild mit Llama-4-Scout Vision."""
    from services.nscale_vision_provider import analyze_image, is_vision_enabled
    if not is_vision_enabled():
        return None

    result = await analyze_image(
        image_data=image_data,
        content_type=content_type,
        system_prompt=VISION_CLASSIFICATION_PROMPT,
        user_prompt="Analysiere dieses Dokument. Klassifiziere Typ, Echtheit und Ausstellungsland.",
        max_tokens=1500,
        temperature=0.1,
    )
    if result.get("error") or not result.get("content"):
        logger.warning(f"[VISION_CLASS] Fehler: {result.get('error')}")
        return None

    parsed = _safe_parse_json(result["content"])
    if parsed:
        parsed["_vision_model"] = result.get("model")
        parsed["_vision_tokens"] = result.get("tokens_used", 0)
    return parsed


async def _run_vision_extraction(
    image_data: bytes,
    content_type: str,
    doc_type: str,
) -> Optional[dict]:
    """Extrahiert strukturierte Daten aus einem Dokument-Bild."""
    from services.nscale_vision_provider import analyze_image, is_vision_enabled
    if not is_vision_enabled():
        return None

    fields = EXTRACTABLE_FIELDS.get(doc_type, [])
    if not fields:
        return None

    fields_json = "\n  ".join(f'"{f}": "...",  ' for f in fields)
    doc_label = DOC_TYPE_LABELS["de"].get(doc_type, doc_type)

    prompt = VISION_EXTRACTION_PROMPT_TEMPLATE.format(
        doc_type_label=doc_label,
        fields_json=fields_json,
    )

    result = await analyze_image(
        image_data=image_data,
        content_type=content_type,
        system_prompt=prompt,
        user_prompt=f"Extrahiere alle strukturierten Daten aus diesem {doc_label}.",
        max_tokens=2000,
        temperature=0.05,
    )
    if result.get("error") or not result.get("content"):
        logger.warning(f"[VISION_EXTRACT] Fehler: {result.get('error')}")
        return None

    parsed = _safe_parse_json(result["content"])
    if parsed:
        parsed["_extraction_model"] = result.get("model")
        parsed["_extraction_tokens"] = result.get("tokens_used", 0)
    return parsed


async def _run_pdf_vision_analysis(pdf_bytes: bytes) -> tuple:
    """Analysiert PDF-Seiten als Bilder mit Vision."""
    from services.nscale_vision_provider import pdf_to_images
    pages = pdf_to_images(pdf_bytes, max_pages=3, dpi=200)
    if not pages:
        return None, None

    # Erste Seite fuer Klassifikation
    first_page_bytes, first_page_type = pages[0]
    classification = await _run_vision_classification(first_page_bytes, first_page_type)
    return classification, pages


# ══════════════════════════════════════════════════════════════════════
# TEXT-BASIERTE ANALYSE: DeepSeek fuer tiefe Textanalyse
# ══════════════════════════════════════════════════════════════════════

async def _run_text_deep_analysis(
    text: str,
    declared_type: str,
    filename: str,
) -> Optional[dict]:
    """Tiefe Textanalyse via OpenRouter (deepseek-v4-flash) oder Fallback."""
    # Primaer: OpenRouter
    from services.openrouter_provider import chat_completion as or_chat, is_enabled as or_enabled
    if or_enabled() and text and len(text.strip()) >= 30:
        system_prompt = """Du bist ein Dokumentenpruefungssystem fuer ein deutsches Studienkolleg.
Analysiere den folgenden Dokumenttext und antworte AUSSCHLIESSLICH im JSON-Format.

Antwortstruktur:
{
  "document_type": "passport|highschool_diploma|transcript|language_certificate|receipt|photo|other",
  "confidence": "high|medium|low",
  "is_authentic_document": true,
  "issuing_country": "Landesname oder unbekannt",
  "issuing_country_code": "ISO-Code oder XX",
  "key_data": {
    "full_name": "...",
    "date_of_birth": "...",
    "institution_name": "...",
    "language_level": "...",
    "gpa_or_grade": "...",
    "graduation_date": "...",
    "subjects_and_grades": [{"subject": "...", "grade": "..."}]
  },
  "issues": [],
  "summary": "Kurze Zusammenfassung auf Deutsch"
}

Sei streng: Ein Foto von einer Landschaft ist KEIN Reisepass. Nur echte Dokumente erkennen."""

        user_prompt = f"""Deklarierter Typ: {declared_type}
Dateiname: {filename}
Extrahierter Text (max 3000 Zeichen):
{text[:3000]}

Klassifiziere und pruefe dieses Dokument."""

        result = await or_chat(
            system_message=system_prompt,
            user_message=user_prompt,
            task="doc_classification",
            temperature=0.1,
        )
        if not result.get("error") and result.get("content"):
            parsed = _safe_parse_json(result["content"])
            if parsed:
                parsed["_text_model"] = result.get("model", "deepseek-v4-flash")
                parsed["_text_tokens"] = result.get("tokens_used", 0)
            return parsed
        logger.warning(f"[DOC_AI] OpenRouter fehlgeschlagen: {result.get('error')}, Fallback DeepSeek")

    # Fallback: DeepSeek (nscale)
    from services.nscale_provider import chat_completion, is_enabled
    if not is_enabled() or not text or len(text.strip()) < 30:
        return None

    system_prompt = """Du bist ein Dokumentenpruefungssystem fuer ein deutsches Studienkolleg.
Analysiere den folgenden Dokumenttext und antworte AUSSCHLIESSLICH im JSON-Format.

Antwortstruktur:
{
  "document_type": "passport|highschool_diploma|transcript|language_certificate|receipt|photo|other",
  "confidence": "high|medium|low",
  "is_authentic_document": true,
  "issuing_country": "Landesname oder unbekannt",
  "issuing_country_code": "ISO-Code oder XX",
  "key_data": {
    "full_name": "...",
    "date_of_birth": "...",
    "institution_name": "...",
    "language_level": "...",
    "gpa_or_grade": "...",
    "graduation_date": "...",
    "subjects_and_grades": [{"subject": "...", "grade": "..."}]
  },
  "issues": [],
  "summary": "Kurze Zusammenfassung auf Deutsch"
}

Sei streng: Ein Foto von einer Landschaft ist KEIN Reisepass. Nur echte Dokumente erkennen."""

    user_prompt = f"""Deklarierter Typ: {declared_type}
Dateiname: {filename}
Extrahierter Text (max 3000 Zeichen):
{text[:3000]}

Klassifiziere und pruefe dieses Dokument."""

    result = await chat_completion(
        task="classification",
        system_message=system_prompt,
        user_message=user_prompt,
    )
    if result.get("error") or not result.get("content"):
        return None
    parsed = _safe_parse_json(result["content"])
    if parsed:
        parsed["_text_model"] = result.get("model")
        parsed["_text_tokens"] = result.get("tokens_used", 0)
    return parsed


# ══════════════════════════════════════════════════════════════════════
# WISSENSABGLEICH: Deep Fetch gegen Anabin + Anforderungen
# ══════════════════════════════════════════════════════════════════════

async def _deep_knowledge_match(
    extracted_data: dict,
    classification: dict,
    application: dict,
) -> dict:
    """
    Tiefer Abgleich der extrahierten Daten gegen Wissensquellen.
    Prueft: Anabin-Kategorie, Sprachanforderungen, Abschluss-Aequivalenz.
    """
    from services.anabin_knowledge import lookup_knowledge
    from services.ai_screening import _check_language_level, COURSE_LANGUAGE_REQUIREMENTS

    result = {
        "anabin_match": None,
        "language_match": None,
        "consistency_checks": [],
        "risk_flags": [],
        "recommendations": [],
    }

    # 1. Anabin-Abgleich mit extrahiertem Land
    country = (
        classification.get("issuing_country")
        or extracted_data.get("issuing_country")
        or application.get("degree_country")
        or ""
    )
    degree_type = (
        extracted_data.get("degree_type")
        or application.get("degree_type")
        or application.get("course_type")
    )

    if country and country.lower() != "unbekannt":
        anabin = await lookup_knowledge(country, degree_type, application.get("id"))
        result["anabin_match"] = {
            "country": country,
            "category": anabin.get("category"),
            "confidence": anabin.get("confidence"),
            "match_type": anabin.get("match_type"),
            "requires_staff": anabin.get("requires_staff_decision", False),
            "label": anabin.get("label", ""),
        }

        if anabin.get("category") == "D":
            result["risk_flags"].append(
                f"Anabin-Kategorie D fuer '{country}' – eingeschraenkte Anerkennung"
            )
        elif anabin.get("category") in ("pruefen", "unbekannt"):
            result["risk_flags"].append(
                f"Anabin: '{country}' nicht eindeutig klassifiziert"
            )

    # 2. Sprachniveau-Abgleich
    extracted_level = extracted_data.get("language_level")
    declared_level = application.get("language_level")
    course_type = application.get("course_type")

    if extracted_level and course_type:
        lang_check = _check_language_level(course_type, extracted_level)
        result["language_match"] = {
            "extracted_level": extracted_level,
            "declared_level": declared_level,
            "required_level": COURSE_LANGUAGE_REQUIREMENTS.get(course_type),
            "is_sufficient": lang_check["ok"],
            "note": lang_check["note"],
        }
        if not lang_check["ok"]:
            result["risk_flags"].append(
                f"Sprachniveau {extracted_level} ungenuegend fuer {course_type}"
            )

    # 3. Konsistenzpruefungen
    app_name = (application.get("applicant_name") or "").lower().strip()
    ext_name = (extracted_data.get("full_name") or "").lower().strip()
    if app_name and ext_name:
        name_parts = app_name.split()
        match_count = sum(1 for p in name_parts if p in ext_name)
        if match_count == 0 and len(name_parts) > 0:
            result["consistency_checks"].append({
                "field": "name",
                "status": "mismatch",
                "detail": f"Bewerbername '{app_name}' stimmt nicht mit extrahiertem Namen '{ext_name}' ueberein",
            })
            result["risk_flags"].append("Namensabweichung zwischen Bewerbung und Dokument")
        else:
            result["consistency_checks"].append({
                "field": "name",
                "status": "match",
                "detail": f"Name stimmt ueberein ({match_count}/{len(name_parts)} Teile)",
            })

    # Geburtsdatum
    app_dob = application.get("date_of_birth", "")
    ext_dob = extracted_data.get("date_of_birth", "")
    if app_dob and ext_dob and app_dob != ext_dob:
        result["consistency_checks"].append({
            "field": "date_of_birth",
            "status": "mismatch",
            "detail": f"Geburtsdatum Bewerbung: {app_dob}, Dokument: {ext_dob}",
        })
        result["risk_flags"].append("Geburtsdatum-Abweichung")

    # Sprachniveau-Konsistenz (deklariert vs. extrahiert)
    if extracted_level and declared_level and extracted_level != declared_level:
        result["consistency_checks"].append({
            "field": "language_level",
            "status": "mismatch",
            "detail": f"Deklariert: {declared_level}, Extrahiert: {ext_dob}",
        })

    return result


# ══════════════════════════════════════════════════════════════════════
# KI-PRUEFBERICHT: Zusammenfassung aller Analysen
# ══════════════════════════════════════════════════════════════════════

async def _generate_ai_report(
    classification: dict,
    extracted_data: dict,
    knowledge_match: dict,
    declared_type: str,
    filename: str,
    institutional_knowledge: str = "",
) -> Optional[str]:
    """Erzeugt den finalen KI-Pruefbericht via OpenRouter (deepseek-v4-flash) oder Fallback."""
    system_prompt = """Du bist ein erfahrener Dokumentenpruefungsexperte bei einem deutschen Studienkolleg.
Erstelle einen strukturierten Pruefbericht auf Deutsch.

BERICHTSSTRUKTUR (zwingend einhalten):
1. DOKUMENTIDENTIFIKATION: Typ, Ausstellungsland, Sprache
2. ECHTHEITSBEWERTUNG: Einschaetzung der Authentizitaet mit Begruendung
3. DATENEXTRAKTION: Welche Daten wurden erfolgreich extrahiert?
4. WISSENSABGLEICH: Ergebnis des Abgleichs mit Anabin/Anforderungen
5. KONSISTENZPRUEFUNG: Stimmen extrahierte Daten mit Bewerberprofil ueberein?
6. RISIKOBEWERTUNG: Identifizierte Risiken und Auffaelligkeiten
7. EMPFEHLUNG: Annahme / Ablehnung / Manuelle Nachpruefung mit Begruendung
8. NAECHSTE SCHRITTE: Konkrete Aktionen fuer Staff

Sei praezise, fachlich korrekt und begruende jede Einschaetzung."""

    context_parts = [
        f"DOKUMENT: {filename} (Deklarierter Typ: {declared_type})",
        f"\nKLASSIFIKATION:\n{json.dumps(classification, ensure_ascii=False, indent=2)}",
        f"\nEXTRAHIERTE DATEN:\n{json.dumps(extracted_data, ensure_ascii=False, indent=2)}",
        f"\nWISSENSABGLEICH:\n{json.dumps(knowledge_match, ensure_ascii=False, indent=2)}",
    ]
    if institutional_knowledge:
        context_parts.append(f"\nINSTITUTIONELLES WISSEN:\n{institutional_knowledge}")

    user_message = "\n".join(context_parts) + "\n\nErstelle den vollstaendigen Pruefbericht."

    # Primaer: OpenRouter
    from services.openrouter_provider import chat_completion as or_chat, is_enabled as or_enabled
    if or_enabled():
        result = await or_chat(
            system_message=system_prompt,
            user_message=user_message,
            task="doc_report",
            override_max_tokens=2500,
            temperature=0.3,
        )
        if not result.get("error") and result.get("content"):
            return result["content"]
        logger.warning(f"[DOC_AI] OpenRouter Report fehlgeschlagen: {result.get('error')}, Fallback DeepSeek")

    # Fallback: DeepSeek
    from services.nscale_provider import chat_completion, is_enabled
    if not is_enabled():
        return None

    result = await chat_completion(
        task="screening",
        system_message=system_prompt,
        user_message=user_message,
        override_max_tokens=2500,
    )
    return result.get("content")


# ══════════════════════════════════════════════════════════════════════
# HAUPT-PIPELINE: Orchestriert alle Analyseschritte
# ══════════════════════════════════════════════════════════════════════

async def validate_document(
    file_data: bytes,
    filename: str,
    content_type: str,
    declared_type: str,
    applicant_profile: Optional[dict] = None,
) -> dict:
    """
    Basis-Dokumentvalidierung (schnell, ohne KI).
    Fuer den initialen Upload-Flow. Schnelle Sicherheits- und Heuristik-Checks.
    """
    evidence = {
        "declared_type": declared_type,
        "filename": filename,
        "content_type": content_type,
        "file_size": len(file_data),
        "file_hash": compute_file_hash(file_data),
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    warnings = []
    errors = []

    # 1. Sicherheitspruefung
    if len(file_data) == 0:
        return _build_result("rejected", evidence, warnings, ["empty_file"],
                             detected_type="other", confidence="none")

    min_size = MIN_FILE_SIZES.get(declared_type, 1000)
    if len(file_data) < min_size:
        warnings.append("too_small")

    # 2. Basis-Klassifikation
    is_pdf = content_type == "application/pdf" or (filename or "").lower().endswith(".pdf")
    is_image = content_type in ("image/jpeg", "image/jpg", "image/png", "image/webp")

    extracted_text = ""
    classification = {}

    if is_pdf:
        extracted_text = _extract_pdf_text(file_data)
        if extracted_text and len(extracted_text.strip()) > 20:
            classification = _classify_by_text(extracted_text)
        else:
            warnings.append("no_text")
            classification = _classify_by_filename(filename, declared_type)
    elif is_image:
        classification = _classify_by_filename(filename, declared_type)
        try:
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(file_data))
            w, h = img.size
            evidence["image_dimensions"] = f"{w}x{h}"
            if w < 200 or h < 200:
                warnings.append("unreadable")
            if w < 100 and h < 100:
                errors.append("too_small")
        except Exception:
            warnings.append("unreadable")
    else:
        classification = _classify_by_filename(filename, declared_type)

    evidence["classification"] = classification
    detected_type = classification.get("detected_type", "other")
    confidence = classification.get("confidence", "low")
    evidence["detected_type"] = detected_type
    evidence["confidence"] = confidence

    type_match = (detected_type == declared_type) or detected_type == "other"
    if not type_match and confidence in ("high", "medium"):
        warnings.append("wrong_type")

    extracted_data = {}
    if extracted_text:
        extracted_data = _extract_key_data(extracted_text, detected_type)
        evidence["extracted_data"] = extracted_data

    consistency = {"checked": False}
    if applicant_profile and extracted_data:
        consistency = _check_consistency(extracted_data, applicant_profile)
        evidence["consistency"] = consistency

    if errors:
        status = "rejected"
    elif confidence == "high" and type_match and not warnings:
        status = "validated"
    elif confidence == "medium" and type_match and len(warnings) <= 1:
        status = "validated"
    else:
        status = "needs_review"

    if detected_type in ("other",) and declared_type not in ("photo", "receipt", "other"):
        status = "needs_review"
    if consistency.get("has_mismatch"):
        status = "needs_review"
        warnings.append("profile_mismatch")

    return _build_result(status, evidence, warnings, errors,
                         detected_type=detected_type, confidence=confidence)


async def validate_document_with_ai(
    file_data: bytes,
    filename: str,
    content_type: str,
    declared_type: str,
    applicant_profile: Optional[dict] = None,
    application: Optional[dict] = None,
    application_id: Optional[str] = None,
) -> dict:
    """
    Vollstaendige KI-gestuetzte Dokumentenvalidierung.

    Pipeline:
    1. Basis-Sicherheitspruefung
    2. Vision-Analyse (Llama-4-Scout) fuer Bilder/PDF-Scans
    3. Text-Analyse (DeepSeek) fuer PDF-Text
    4. Strukturierte Datenextraktion
    5. DB-Feld-Mapping
    6. Tiefer Wissensabgleich (Anabin, Sprachanforderungen)
    7. KI-Pruefbericht mit institutionellem Wissen
    """
    is_pdf = content_type == "application/pdf" or (filename or "").lower().endswith(".pdf")
    is_image = content_type in ("image/jpeg", "image/jpg", "image/png", "image/webp")

    # Schneller Sicherheitscheck
    if len(file_data) == 0:
        return _build_result(
            "rejected",
            {"file_size": 0, "filename": filename, "validated_at": datetime.now(timezone.utc).isoformat()},
            [], ["empty_file"], detected_type="other", confidence="none",
        )

    # ── SCHRITT 0: Ingestion & Normalisierung (EXIF-Strip, DPI) ────
    from services.document_ingestion import preprocess_document
    processed_data = preprocess_document(file_data, content_type)

    evidence = {
        "declared_type": declared_type,
        "filename": filename,
        "content_type": content_type,
        "file_size": len(file_data),
        "processed_file_size": len(processed_data),
        "file_hash": compute_file_hash(processed_data),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "ai_pipeline": "v2.2_full_pipeline",
    }
    warnings = []
    errors = []
    ai_classification = None
    ai_extraction = None
    ai_report = None
    knowledge_match = None
    total_tokens = 0

    # ── SCHRITT 1: Vision-Analyse ──────────────────────────────────
    vision_image = None
    if is_image:
        vision_image = (processed_data, content_type)
    elif is_pdf:
        # PDF-Seiten als Bilder konvertieren
        from services.nscale_vision_provider import pdf_to_images, is_vision_enabled
        if is_vision_enabled():
            pages = pdf_to_images(processed_data, max_pages=3, dpi=200)
            if pages:
                vision_image = pages[0]  # Erste Seite fuer Klassifikation
                evidence["pdf_pages_analyzed"] = len(pages)

    if vision_image:
        img_bytes, img_type = vision_image
        ai_classification = await _run_vision_classification(img_bytes, img_type)
        if ai_classification:
            total_tokens += ai_classification.get("_vision_tokens", 0)
            evidence["vision_classification"] = {
                k: v for k, v in ai_classification.items() if not k.startswith("_")
            }
            logger.info(f"[DOC_AI] Vision-Klassifikation: {ai_classification.get('document_type')} "
                        f"(Konfidenz: {ai_classification.get('confidence')})")

    # ── SCHRITT 2: Text-Analyse (fuer PDFs mit extrahierbarem Text) ─
    extracted_text = ""
    text_analysis = None
    if is_pdf:
        extracted_text = _extract_pdf_text(processed_data)
        if extracted_text and len(extracted_text.strip()) > 30:
            text_analysis = await _run_text_deep_analysis(extracted_text, declared_type, filename)
            if text_analysis:
                total_tokens += text_analysis.get("_text_tokens", 0)
                evidence["text_analysis"] = {
                    k: v for k, v in text_analysis.items() if not k.startswith("_")
                }

    # ── SCHRITT 3: Konsolidierte Klassifikation ────────────────────
    final_classification = _consolidate_classification(
        ai_classification, text_analysis, declared_type, filename
    )
    evidence["final_classification"] = final_classification
    detected_type = final_classification.get("document_type", "other")
    confidence = final_classification.get("confidence", "low")

    # ── SCHRITT 4: Strukturierte Datenextraktion ───────────────────
    extracted_data = {}
    if vision_image and detected_type in EXTRACTABLE_FIELDS:
        img_bytes, img_type = vision_image
        ai_extraction = await _run_vision_extraction(img_bytes, img_type, detected_type)
        if ai_extraction:
            total_tokens += ai_extraction.get("_extraction_tokens", 0)
            extracted_data = {
                k: v for k, v in ai_extraction.items()
                if not k.startswith("_") and v is not None and v != ""
            }

    # Fallback: Text-basierte Extraktion
    if not extracted_data and text_analysis and text_analysis.get("key_data"):
        extracted_data = text_analysis["key_data"]
    if not extracted_data and extracted_text:
        extracted_data = _extract_key_data(extracted_text, detected_type)

    evidence["extracted_data"] = extracted_data

    # ── SCHRITT 5: DB-Feld-Mapping vorbereiten ─────────────────────
    db_field_updates = {}
    for ext_field, db_field in FIELD_TO_APPLICATION_MAP.items():
        value = extracted_data.get(ext_field)
        if value and value != "unbekannt" and value != "null":
            db_field_updates[db_field] = value

    evidence["db_field_mapping"] = db_field_updates

    # ── SCHRITT 5b: MRZ-Erkennung (Reisepaesse) ───────────────────
    mrz_data = None
    if detected_type == "passport" and extracted_text:
        from services.document_ingestion import detect_mrz_lines, parse_mrz
        mrz_lines = detect_mrz_lines(extracted_text)
        if mrz_lines:
            mrz_data = parse_mrz(mrz_lines)
            if mrz_data:
                evidence["mrz"] = mrz_data
                # MRZ-Daten in Extraktion einfliessen lassen
                if not extracted_data.get("full_name") and mrz_data.get("full_name"):
                    extracted_data["full_name"] = mrz_data["full_name"]
                if not extracted_data.get("passport_number") and mrz_data.get("passport_number"):
                    extracted_data["passport_number"] = mrz_data["passport_number"]
                if not extracted_data.get("date_of_birth") and mrz_data.get("date_of_birth"):
                    extracted_data["date_of_birth"] = mrz_data["date_of_birth"]
                if not extracted_data.get("expiry_date") and mrz_data.get("expiry_date"):
                    extracted_data["expiry_date"] = mrz_data["expiry_date"]
                if not extracted_data.get("nationality") and mrz_data.get("nationality"):
                    extracted_data["nationality"] = mrz_data["nationality"]

    # ── SCHRITT 5c: Plausibilitaets-Checks ─────────────────────────
    from services.document_ingestion import run_plausibility_checks
    plausibility = await run_plausibility_checks(
        extracted_data=extracted_data,
        classification=final_classification,
        applicant_profile=applicant_profile,
        mrz_data=mrz_data,
    )
    evidence["plausibility_checks"] = plausibility

    # ── SCHRITT 6: Tiefer Wissensabgleich ──────────────────────────
    app_context = application or {}
    if applicant_profile:
        app_context["applicant_name"] = applicant_profile.get("full_name", "")

    knowledge_match = await _deep_knowledge_match(
        extracted_data, final_classification, app_context
    )
    evidence["knowledge_match"] = knowledge_match

    # ── SCHRITT 7: Institutionelles Wissen laden ───────────────────
    institutional_knowledge = ""
    if application_id:
        try:
            from services.ai_learning import gather_institutional_knowledge, format_knowledge_for_prompt
            knowledge = await gather_institutional_knowledge(application_id)
            institutional_knowledge = format_knowledge_for_prompt(knowledge)
        except Exception as e:
            logger.warning(f"[DOC_AI] Institutionelles Wissen nicht ladbar: {e}")

    # ── SCHRITT 8: KI-Pruefbericht generieren ──────────────────────
    ai_report = await _generate_ai_report(
        classification=final_classification,
        extracted_data=extracted_data,
        knowledge_match=knowledge_match,
        declared_type=declared_type,
        filename=filename,
        institutional_knowledge=institutional_knowledge,
    )

    evidence["ai_report"] = ai_report
    evidence["total_ai_tokens"] = total_tokens

    # ── SCHRITT 9: Status-Entscheidung ─────────────────────────────
    status = _determine_final_status(
        final_classification, extracted_data, knowledge_match,
        declared_type, warnings, errors,
    )

    # Echtheitsflag
    is_authentic = final_classification.get("is_authentic_document", True)
    if is_authentic is False:
        status = "rejected"
        errors.append("fraudulent")

    # Typ-Mismatch
    type_match = (detected_type == declared_type) or detected_type == "other"
    if not type_match and confidence in ("high", "medium"):
        warnings.append("wrong_type")

    # Mindestgroesse
    min_size = MIN_FILE_SIZES.get(declared_type, 1000)
    if len(processed_data) < min_size:
        warnings.append("too_small")

    # Risiko-Flags aus Wissensabgleich
    if knowledge_match and knowledge_match.get("risk_flags"):
        for flag in knowledge_match["risk_flags"]:
            warnings.append(f"risk:{flag[:80]}")

    # Plausibilitaets-Warnings
    if plausibility and not plausibility.get("all_passed"):
        for check in plausibility.get("results", []):
            if not check.get("valid", True) and not check.get("match", True):
                sev = check.get("severity", "warning")
                if sev == "critical":
                    warnings.append(f"plausibility_critical:{check['check']}")
                else:
                    warnings.append(f"plausibility:{check['check']}")
                if sev == "critical" and status == "validated":
                    status = "needs_review"

    # Lernereignis speichern
    if application_id:
        try:
            from services.ai_learning import store_learning_event
            await store_learning_event("document_validated", application_id, {
                "doc_type": detected_type,
                "confidence": confidence,
                "status": status,
                "extracted_fields": list(extracted_data.keys()),
                "knowledge_match_category": (knowledge_match or {}).get("anabin_match", {}).get("category") if knowledge_match else None,
            })
        except Exception:
            pass

    result = _build_result(
        status, evidence, warnings, errors,
        detected_type=detected_type, confidence=confidence,
    )
    result["ai_classification"] = final_classification
    result["ai_extraction"] = extracted_data
    result["ai_report"] = ai_report
    result["knowledge_match"] = knowledge_match
    result["db_field_updates"] = db_field_updates
    result["total_ai_tokens"] = total_tokens
    result["plausibility"] = plausibility
    if mrz_data:
        result["mrz_data"] = mrz_data
    return result


# ══════════════════════════════════════════════════════════════════════
# HILFS-FUNKTIONEN
# ══════════════════════════════════════════════════════════════════════

def _consolidate_classification(
    vision_result: Optional[dict],
    text_result: Optional[dict],
    declared_type: str,
    filename: str,
) -> dict:
    """Konsolidiert Klassifikationsergebnisse aus Vision und Text."""
    final = {
        "document_type": declared_type,
        "confidence": "low",
        "is_authentic_document": True,
        "issuing_country": "unbekannt",
        "issuing_country_code": "XX",
        "source": "fallback",
    }

    # Vision hat hoechste Prioritaet (sieht das tatsaechliche Dokument)
    if vision_result:
        final["document_type"] = vision_result.get("document_type", declared_type)
        final["confidence"] = vision_result.get("confidence", "medium")
        final["is_authentic_document"] = vision_result.get("is_authentic_document", True)
        final["issuing_country"] = vision_result.get("issuing_country", "unbekannt")
        final["issuing_country_code"] = vision_result.get("issuing_country_code", "XX")
        final["authenticity_reasoning"] = vision_result.get("authenticity_reasoning", "")
        final["detected_elements"] = vision_result.get("detected_elements", [])
        final["visual_quality"] = vision_result.get("visual_quality", "")
        final["document_language"] = vision_result.get("document_language", "")
        final["readability"] = vision_result.get("readability", "medium")
        final["source"] = "vision_llama4"

    # Text-Analyse als Ergaenzung/Korrektur
    if text_result:
        # Wenn Vision keinen Typ erkannt hat, Text nutzen
        if final.get("document_type") == "other" and text_result.get("document_type") != "other":
            final["document_type"] = text_result["document_type"]
            final["source"] = "text_deepseek"

        # Wenn Vision low confidence hat, Text upgraden
        if final.get("confidence") == "low" and text_result.get("confidence") in ("high", "medium"):
            final["confidence"] = text_result["confidence"]

        # Land aus Text wenn Vision es nicht erkannt hat
        if final.get("issuing_country") == "unbekannt" and text_result.get("issuing_country"):
            ic = text_result["issuing_country"]
            if ic.lower() != "unbekannt":
                final["issuing_country"] = ic
                final["issuing_country_code"] = text_result.get("issuing_country_code", "XX")

    # Keine KI verfuegbar → Heuristik
    if not vision_result and not text_result:
        heuristic = _classify_by_filename(filename, declared_type)
        final["document_type"] = heuristic.get("detected_type", declared_type)
        final["confidence"] = "low"
        final["source"] = "heuristic_fallback"

    return final


def _determine_final_status(
    classification: dict,
    extracted_data: dict,
    knowledge_match: Optional[dict],
    declared_type: str,
    warnings: list,
    errors: list,
) -> str:
    """Bestimmt den finalen Validierungsstatus."""
    if errors:
        return "rejected"

    confidence = classification.get("confidence", "low")
    is_authentic = classification.get("is_authentic_document", True)
    detected_type = classification.get("document_type", "other")
    type_match = (detected_type == declared_type) or detected_type == "other"

    # Klare Ablehnung bei Faelschung
    if is_authentic is False:
        return "rejected"

    # Hohe Konfidenz + Typ passt + keine Warnungen → validiert
    if confidence == "high" and type_match and not warnings:
        # Aber nur wenn keine kritischen Risiko-Flags
        risk_flags = (knowledge_match or {}).get("risk_flags", [])
        if not risk_flags:
            return "validated"
        return "needs_review"

    # Mittlere Konfidenz + Typ passt → validiert (mit Vorbehalt)
    if confidence == "medium" and type_match and len(warnings) <= 1:
        return "validated"

    # Alles andere → Staff Review
    return "needs_review"


# ── Legacy-Heuristiken (fuer Fallback ohne KI) ────────────────────

CLASSIFICATION_KEYWORDS = {
    "passport": [
        "passport", "reisepass", "travel document", "passeport",
        "republic", "nationality", "surname", "given names",
        "date of birth", "geburtsdatum", "staatsangehoerigkeit",
        "machine readable", "mrz", "p<", "id card", "personalausweis",
    ],
    "highschool_diploma": [
        "certificate", "diploma", "zeugnis", "abschluss", "abitur",
        "secondary school", "high school", "baccalaureate", "tawjihi",
        "examination", "board of education", "ministry of education",
    ],
    "transcript": [
        "transcript", "grades", "noten", "marks", "subject",
        "credit", "gpa", "cgpa", "semester", "course",
    ],
    "language_certificate": [
        "goethe", "testdaf", "telc", "dsh", "ielts", "toefl",
        "cambridge", "delf", "dalf", "sprachzertifikat", "language certificate",
        "deutsch", "german", "b1", "b2", "c1", "c2", "a1", "a2",
    ],
}


def _classify_by_text(text: str) -> dict:
    text_lower = text.lower()
    scores = {}
    for doc_type, keywords in CLASSIFICATION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score > 0:
            scores[doc_type] = score
    if not scores:
        return {"detected_type": "other", "confidence": "low", "method": "keyword_heuristic"}
    best = max(scores, key=scores.get)
    best_score = scores[best]
    confidence = "high" if best_score >= 4 else "medium" if best_score >= 2 else "low"
    return {"detected_type": best, "confidence": confidence, "method": "keyword_heuristic", "score": best_score}


def _classify_by_filename(filename: str, declared_type: str) -> dict:
    fn = (filename or "").lower()
    type_hints = {
        "passport": ["pass", "passport", "reisepass", "ausweis", "id_card"],
        "highschool_diploma": ["diploma", "zeugnis", "certificate", "abschluss", "abitur", "school"],
        "transcript": ["transcript", "noten", "grades", "marks", "record"],
        "language_certificate": ["goethe", "testdaf", "telc", "dsh", "ielts", "toefl", "sprach", "language"],
    }
    for doc_type, hints in type_hints.items():
        if any(h in fn for h in hints):
            return {"detected_type": doc_type, "confidence": "low", "method": "filename_heuristic"}
    return {"detected_type": declared_type or "other", "confidence": "low", "method": "declared_type_fallback"}


def _extract_key_data(text: str, doc_type: str) -> dict:
    data = {}
    dates = re.findall(r'\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2}', text)
    if dates:
        data["dates_found"] = dates[:5]
    levels = re.findall(r'\b([A-C][12])\b', text, re.IGNORECASE)
    if levels:
        data["language_levels"] = list(set(lv.upper() for lv in levels))
        if len(data["language_levels"]) == 1:
            data["language_level"] = data["language_levels"][0]
    grades = re.findall(r'\b(\d{1,2}[,\.]\d{1,2})\b', text)
    if grades:
        data["grades_found"] = grades[:10]
    if doc_type in ("passport", "highschool_diploma", "language_certificate"):
        text_lines = text.strip().split("\n")
        for line in text_lines[:10]:
            clean = line.strip()
            if len(clean) > 3 and len(clean) < 60 and not any(c.isdigit() for c in clean[:5]):
                data["full_name"] = clean
                break
    return data


def _check_consistency(extracted_data: dict, profile: dict) -> dict:
    result = {"checked": True, "has_mismatch": False, "details": []}
    applicant_name = (profile.get("full_name") or "").lower().strip()
    possible_name = (extracted_data.get("full_name") or extracted_data.get("possible_name") or "").lower().strip()
    if applicant_name and possible_name:
        name_parts = applicant_name.split()
        match_score = sum(1 for part in name_parts if part in possible_name)
        if match_score == 0 and len(name_parts) > 0:
            result["has_mismatch"] = True
            result["details"].append("name_mismatch")
    return result


def _build_result(
    status: str, evidence: dict, warnings: list, errors: list,
    detected_type: str = "other", confidence: str = "low",
) -> dict:
    if status == "rejected":
        next_action = "reupload_required"
    elif status == "needs_review":
        next_action = "staff_review_required"
    elif status == "validated":
        next_action = "none"
    else:
        next_action = "unknown"

    staff_required = status in ("needs_review",) or confidence == "low"

    return {
        "validation_status": status,
        "detected_type": detected_type,
        "confidence": confidence,
        "evidence": evidence,
        "warnings": warnings,
        "errors": errors,
        "next_action": next_action,
        "staff_decision_required": staff_required,
    }
