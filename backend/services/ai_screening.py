"""
KI-gestuetzte Bewerberpruefung (AI Application Screening)

ARCHITEKTUR: Retrieval-First mit Delta-Orientierung

Provider: DeepSeek – alle KI-Inferenzen laufen ueber die DeepSeek API.

Arbeitsweise:
1. RETRIEVAL: Anabin-Wissensbasis aus MongoDB abrufen (nicht hartcodiert)
2. CACHE: Pruefen ob sich Daten seit letztem Screening geaendert haben
3. REGELBASIERT: Vollstaendigkeit, Sprachniveau, Anabin-Kategorie
4. KI-CALL: Nur wenn Daten sich geaendert haben (Delta-orientiert)
5. PERSISTENZ: Ergebnis + Fingerprint speichern fuer naechsten Lauf

Kostenersparnis: ~70-90% weniger KI-Calls durch Cache/Delta-Logik.

Ergebnisstruktur:
- Vollstaendigkeit der Unterlagen
- Dokumentgueltigkeit / Plausibilitaet
- Formale Vorpruefung (Anabin)
- Hochschulzugangs-/FSP-Vorpruefung
- Sprachstand
- Empfehlungspfad
- Risiken
- Offene Punkte
- Naechste Schritte
- Staff-Entscheid notwendig (ja/nein)

Ausgabe: Auf Deutsch (Staff-Oberflaeche)
Klare Trennung: AI suggestion vs. Staff decision vs. Final status
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

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


def _check_language_level(course_type: Optional[str], language_level: Optional[str]) -> dict:
    if not course_type or not language_level:
        return {"ok": False, "note": "Kurstyp oder Sprachniveau nicht angegeben."}
    required = COURSE_LANGUAGE_REQUIREMENTS.get(course_type)
    if not required:
        return {"ok": True, "note": "Kurstyp unbekannt – manuelle Pruefung."}
    try:
        required_idx = CEFR_LEVELS.index(required)
        actual_idx = CEFR_LEVELS.index(language_level)
        if actual_idx >= required_idx:
            return {"ok": True, "note": f"Sprachniveau {language_level} erfuellt Mindestanforderung {required} fuer {course_type}."}
        else:
            return {"ok": False, "note": f"Sprachniveau {language_level} unzureichend fuer {course_type} (Mindest: {required}). Vorgelagerter Sprachkurs empfohlen."}
    except ValueError:
        return {"ok": False, "note": f"Ungueltiges Sprachniveau '{language_level}' – manuelle Pruefung."}


def _check_completeness(docs: list) -> dict:
    """Pruefe Vollstaendigkeit: Nur Dokumente mit gueltiger Validierung zaehlen."""
    valid_statuses = {"uploaded", "approved", "validated", "in_review", "needs_review"}  # noqa: F841
    rejected_statuses = {"rejected"}
    uploaded_types = set()
    validated_types = set()
    for d in docs:
        dtype = d.get("document_type")
        dstatus = d.get("status", "")
        vstatus = d.get("validation_status", "")
        if dstatus not in rejected_statuses:
            uploaded_types.add(dtype)
        if vstatus == "validated" or dstatus == "approved":
            validated_types.add(dtype)
    missing = [t for t in REQUIRED_DOCUMENT_TYPES if t not in uploaded_types]
    present = [t for t in REQUIRED_DOCUMENT_TYPES if t in uploaded_types]
    validated = [t for t in REQUIRED_DOCUMENT_TYPES if t in validated_types]
    return {
        "complete": len(missing) == 0,
        "missing_types": missing,
        "missing_labels": [REQUIRED_DOC_LABELS[t] for t in missing],
        "present_labels": [REQUIRED_DOC_LABELS[t] for t in present],
        "validated_labels": [REQUIRED_DOC_LABELS[t] for t in validated],
        "total_required": len(REQUIRED_DOCUMENT_TYPES),
        "total_present": len(present),
        "total_validated": len(validated),
    }


async def run_ai_screening(
    application: dict,
    applicant: dict,
    docs: list,
    messages: list,
) -> dict:
    """
    KI-gestuetzte Vorpruefung – Retrieval-first + Delta-orientiert.

    Ablauf:
    1. Cache pruefen (Fingerprint-basiert)
    2. Anabin-Wissensbasis abfragen (MongoDB, nicht hartcodiert)
    3. Regelbasierte Checks (Vollstaendigkeit, Sprache)
    4. Institutionelles Wissen laden (Kommunikation, Entscheidungen)
    5. KI-Call nur bei geaenderten Daten (Delta)
    6. Ergebnis + Fingerprint persistieren
    """
    from services.anabin_knowledge import lookup_knowledge, create_queue_from_screening
    from services.screening_cache import get_cached_screening, _compute_fingerprint
    from services.ai_learning import gather_institutional_knowledge, format_knowledge_for_prompt

    app_id = application.get("id", "")

    # ── 1. CACHE CHECK ─────────────────────────────────────────────
    cache_result = await get_cached_screening(app_id, application, docs, len(messages))
    if cache_result["hit"]:
        logger.info(f"[AI_SCREENING] Cache HIT for {app_id} – returning cached result")
        return cache_result["screening"]

    fingerprint = cache_result["fingerprint"]
    previous = cache_result.get("previous_screening")

    # ── 2. ANABIN RETRIEVAL (erweitertes Degree-Matching aus MongoDB) ──
    degree_country = application.get("degree_country")
    degree_type = application.get("degree_type") or application.get("course_type")
    anabin_info = await lookup_knowledge(degree_country, degree_type, app_id)

    # ── 3. REGELBASIERTE CHECKS ────────────────────────────────────
    completeness = _check_completeness(docs)
    language_level = application.get("language_level") or applicant.get("language_level") or ""
    language_check = _check_language_level(
        application.get("course_type"),
        language_level,
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

    # ── 4. INSTITUTIONELLES WISSEN LADEN ──────────────────────────
    institutional_context = ""
    external_context = ""
    try:
        inst_knowledge = await gather_institutional_knowledge(app_id, applicant.get("id"))
        institutional_context = format_knowledge_for_prompt(inst_knowledge)
    except Exception:
        pass
    try:
        from services.external_knowledge import get_knowledge_context_for_ai
        external_context = get_knowledge_context_for_ai(task="screening")
    except Exception:
        pass
    except Exception as e:
        logger.warning(f"[AI_SCREENING] Institutionelles Wissen nicht ladbar: {e}")

    # ── 5. KI-CALL (Delta-orientiert) – OpenRouter primaer, DeepSeek Fallback
    from services.openrouter_provider import chat_completion as or_chat, is_enabled as or_enabled
    from services.nscale_provider import chat_completion, is_enabled

    ki_available = or_enabled() or is_enabled()
    if ki_available:
        try:
            doc_summary_parts = []
            for d in docs:
                dtype = d.get('document_type', 'unbekannt')
                dstatus = d.get('status', 'unbekannt')
                vstatus = d.get('validation_status', '')
                vconf = d.get('validation_confidence', '')
                det_type = d.get('detected_type', '')
                vwarns = d.get('validation_warnings', [])
                ai_class = d.get('ai_classification', {})
                ai_extract = d.get('ai_extraction', {})
                line = f"{dtype} (Status: {dstatus}"
                if vstatus:
                    line += f", Validierung: {vstatus}, Vertrauen: {vconf}"
                if det_type and det_type != dtype:
                    line += f", ERKANNT ALS: {det_type} (Typ-Abweichung!)"
                if vwarns:
                    line += f", Warnungen: {', '.join(vwarns[:3])}"
                # KI-Klassifikation einbinden
                if ai_class:
                    line += f", KI-Typ: {ai_class.get('document_type', '?')}"
                    line += f", Land: {ai_class.get('issuing_country', '?')}"
                    line += f", Echtheit: {'Ja' if ai_class.get('is_authentic_document') else 'Nein/Unklar'}"
                # Extrahierte Daten einbinden
                if ai_extract:
                    ext_fields = [f"{k}={v}" for k, v in ai_extract.items()
                                  if v and not k.startswith('_') and k not in ('raw_text_excerpt', 'extraction_notes')]
                    if ext_fields:
                        line += f", Extrahiert: {'; '.join(ext_fields[:5])}"
                line += ")"
                doc_summary_parts.append(line)
            doc_summary = "\n".join(doc_summary_parts) or "Keine Dokumente vorhanden"

            msg_summary = ""
            if messages:
                recent = messages[-5:]
                msg_summary = "\n".join(
                    f"- [{m.get('created_at', '')}] {m.get('content', '')[:200]}" for m in recent
                )

            # Delta-Kontext: Was hat sich seit letztem Screening geaendert?
            delta_context = ""
            if previous:
                delta_context = f"""
DELTA-KONTEXT (Aenderungen seit letzter Pruefung):
- Letzte Pruefung: {previous.get('screened_at', 'unbekannt')}
- Letzter Status-Vorschlag: {previous.get('suggested_stage', 'unbekannt')}
- Letzter Anabin-Kategorie: {previous.get('anabin_category', 'unbekannt')}
- Neue Dokumente oder Statusaenderungen wurden erkannt.
Bitte fokussiere dich auf die Aenderungen und aktualisiere die Bewertung."""

            system_prompt = """Du bist ein erfahrener Sachbearbeiter bei einem deutschen Studienkolleg.
Du fuehrst eine formale Vorpruefung von Bewerbungen durch.
Antworte IMMER auf Deutsch.
Sei praezise, fachlich korrekt und strukturiert.

ERGEBNISSTRUKTUR (zwingend einhalten):
1. VOLLSTAENDIGKEIT: Beurteilung der Unterlagen
2. DOKUMENTGUELTIGKEIT: Plausibilitaet der eingereichten Dokumente
3. FORMALE VORPRUEFUNG: Anabin-Einschaetzung, Hochschulzugangsberechtigung
4. FSP-VORPRUEFUNG: Feststellungspruefung-Relevanz
5. SPRACHSTAND: Aktuelles Niveau, Mindestanforderung, Empfehlung
6. EMPFEHLUNGSPFAD: Konkreter Kurs und Begruendung
7. RISIKEN: Identifizierte Probleme oder Unsicherheiten
8. OFFENE PUNKTE: Was noch zu klaeren ist
9. NAECHSTE SCHRITTE: Konkrete Aktionen fuer Staff
10. STAFF-ENTSCHEID NOTWENDIG: Ja/Nein mit Begruendung

Trenne klar: KI-Einschaetzung vs. Empfehlung vs. notwendige manuelle Pruefung.
Keine Endentscheidungen – nur Vorpruefung und Empfehlungen fuer Staff."""

            user_prompt = f"""Pruefe folgende Bewerbung fuer das Studienkolleg Aachen.

BEWERBERDATEN:
- Name: {applicant.get('full_name', 'Unbekannt')}
- Land: {applicant.get('country', 'Nicht angegeben')}
- Geburtsdatum: {application.get('date_of_birth', 'Nicht angegeben')}
- Gewuenschter Kurs: {application.get('course_type', 'Nicht angegeben')}
- Wunschsemester: {application.get('desired_start', 'Nicht angegeben')}
- Deutschniveau: {application.get('language_level', 'Nicht angegeben')}
- Land des letzten Abschlusses: {application.get('degree_country', 'Nicht angegeben')}
- Anmerkungen: {application.get('notes', 'Keine')}

ANABIN-WISSENSBASIS (Retrieval-Ergebnis):
- Kategorie: {anabin_info['category']}
- Einschaetzung: {anabin_info['label']}
- Match-Typ: {anabin_info.get('match_type', 'unbekannt')}
- Konfidenz: {anabin_info.get('confidence', 'unbekannt')}
- Operative Einstufung: {anabin_info.get('operational_classification', 'nicht festgelegt')}
- Staff-Entscheid noetig: {'Ja' if anabin_info.get('requires_staff_decision') else 'Nein'}
- Sonderfall: {'Ja' if anabin_info.get('is_special_case') else 'Nein'}
- Staff-Hinweis: {anabin_info.get('staff_note', 'keiner')}
- Quelle: {anabin_info.get('source', 'unbekannt')}

SPRACHNIVEAU-PRUEFUNG (regelbasiert):
- Ausreichend: {language_check['ok']}
- Hinweis: {language_check['note']}

DOKUMENTE ({len(docs)} vorhanden):
{doc_summary}

FEHLENDE PFLICHTDOKUMENTE: {', '.join(completeness['missing_labels']) if completeness['missing_labels'] else 'Alle vorhanden'}

KOMMUNIKATIONSVERLAUF:
{msg_summary if msg_summary else 'Kein Verlauf vorhanden'}
{delta_context}

INSTITUTIONELLES WISSEN (gelernt aus frueheren Faellen und Kommunikation):
{institutional_context if institutional_context else 'Keine vorherigen Erkenntnisse vorhanden.'}

EXTERNE WISSENSBASIS:
{external_context if external_context else 'Nicht verfuegbar.'}

Erstelle den strukturierten Vorpruefungsbericht gemaess der vorgegebenen Ergebnisstruktur."""

            # Primaer: OpenRouter (deepseek-v4-flash)
            if or_enabled():
                result = await or_chat(
                    system_message=system_prompt,
                    user_message=user_prompt,
                    task="screening",
                    override_max_tokens=3000,
                    temperature=0.3,
                )
            else:
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
        ai_report = "KI-Pruefung nicht verfuegbar (kein API-Key konfiguriert). Lokale Pruefung abgeschlossen."

    suggested_stage = _suggest_stage(completeness, language_check, anabin_info)

    staff_decision_required = (
        not completeness["complete"]
        or not language_check["ok"]
        or anabin_info["category"] in ("D", "pruefen", "unbekannt")
        or anabin_info.get("requires_staff_decision", False)
        or anabin_info.get("is_special_case", False)
    )

    screening_result = {
        "screening_id": str(uuid.uuid4()),
        "application_id": app_id,
        "screened_at": datetime.now(timezone.utc).isoformat(),
        "screened_by": "ai_system",
        "ai_provider": "deepseek",
        "ai_model": ai_model_used,
        "ai_tokens_used": ai_tokens_used,
        "local_checks": local_summary,
        "ai_report": ai_report,
        "ai_error": ai_error,
        "suggested_stage": suggested_stage,
        "is_complete": completeness["complete"],
        "missing_documents": completeness["missing_labels"],
        "anabin_category": anabin_info["category"],
        "anabin_match_type": anabin_info.get("match_type", "unknown"),
        "anabin_confidence": anabin_info.get("confidence", "unknown"),
        "language_level_ok": language_check["ok"],
        "decision_note": "KI-Vorpruefung (Retrieval-first + Delta). Keine bindende Entscheidung. Staff-Review erforderlich.",
        "data_fingerprint": fingerprint,
        "cache_hit": False,
        "staff_decision_required": staff_decision_required,
    }

    # ── 6. QUALIFIZIERUNGS-ENGINE: Pfad-Empfehlung berechnen ──────
    from services.qualification_engine import compute_qualification_path
    try:
        qual_path = await compute_qualification_path(application, applicant, anabin_info)
        screening_result["qualification_path"] = qual_path

        # Sprachniveau-Trigger ausfuehren
        if qual_path.get("auto_triggers"):
            from services.automation import trigger_language_level_action
            await trigger_language_level_action(
                application_id=app_id,
                applicant_id=applicant.get("id", ""),
                applicant_email=applicant.get("email", ""),
                applicant_name=applicant.get("full_name", ""),
                language_level=language_level or "",
                course_type=application.get("course_type", ""),
            )
    except Exception as e:
        logger.warning(f"[AI_SCREENING] Qualification engine error (non-fatal): {e}")

    # ── 7. AUTO-QUEUE bei Sonderfaellen / Unbekannten ──────────────
    if anabin_info.get("match_type") in ("unknown", "fuzzy"):
        reason = "no_mapping_found" if anabin_info["match_type"] == "unknown" else "fuzzy_match_only"
        await create_queue_from_screening(
            country=degree_country or "",
            degree_type=degree_type or "",
            application_id=app_id,
            reason=reason,
            screening_output=screening_result,
        )
        logger.info(f"[AI_SCREENING] Auto-Queue fuer {degree_country} ({reason}) erstellt")
    elif anabin_info.get("is_special_case"):
        await create_queue_from_screening(
            country=degree_country or "",
            degree_type=degree_type or "",
            application_id=app_id,
            reason="special_case",
            screening_output=screening_result,
        )
        logger.info(f"[AI_SCREENING] Sonderfall-Queue fuer {degree_country} erstellt")
    elif anabin_info.get("requires_staff_decision") and anabin_info.get("category") == "D":
        await create_queue_from_screening(
            country=degree_country or "",
            degree_type=degree_type or "",
            application_id=app_id,
            reason="staff_required",
            screening_output=screening_result,
        )
        logger.info(f"[AI_SCREENING] Staff-Review-Queue fuer {degree_country} (Kategorie D) erstellt")

    return screening_result


def _suggest_stage(completeness: dict, language_check: dict, anabin_info: dict) -> str:
    """Regelbasierter Status-Vorschlag basierend auf lokalen Checks und Anabin-Wissensbasis."""
    if not completeness["complete"]:
        return "pending_docs"
    if not language_check["ok"]:
        return "in_review"
    if anabin_info.get("is_special_case"):
        return "in_review"
    if anabin_info["category"] == "D":
        return "in_review"
    if anabin_info["category"] in ("pruefen", "unbekannt"):
        return "in_review"
    if anabin_info.get("match_type") in ("fuzzy", "unknown"):
        return "in_review"
    if anabin_info["category"] in ("H+",) and language_check["ok"] and completeness["complete"]:
        return "eligible"
    if anabin_info["category"] in ("H",) and language_check["ok"] and completeness["complete"]:
        if anabin_info.get("confidence") == "high":
            return "eligible"
        return "in_review"
    return "in_review"
