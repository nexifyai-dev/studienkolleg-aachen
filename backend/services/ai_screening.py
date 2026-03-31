"""
KI-gestützte Bewerberprüfung (AI Application Screening)

Provider: DeepSeek – alle KI-Inferenzen laufen über DeepSeek.
Kein anderer Modellprovider wird für Produktiv-KI genutzt.
"""
import logging
import uuid
from datetime import datetime, timezone

from services.screening_rules import REQUIRED_DOCUMENT_TYPES, evaluate_screening_criteria

logger = logging.getLogger(__name__)


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

    local_summary = evaluate_screening_criteria(application, applicant, docs)
    completeness = local_summary["completeness"]
    anabin_info = local_summary["anabin_assessment"]
    language_check = local_summary["language_level_check"]
    formal_precheck = local_summary["formal_precheck"]

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

REGELBASIERTE VORPRÜFUNG (bindend für formale Vorsortierung):
- formal_result: {local_summary['formal_result']}
- criteria_failed: {', '.join([c['rule_id'] for c in local_summary['criteria_failed']]) or 'keine'}
- criteria_missing: {', '.join([c['rule_id'] for c in local_summary['criteria_missing']]) or 'keine'}
- suggested_next_step: {local_summary['suggested_next_step']}

ANABIN-EINSCHÄTZUNG:
- Kategorie: {anabin_info['category']}
- Einschätzung: {anabin_info['label']}

SPRACHNIVEAU-PRÜFUNG:
- Ausreichend: {language_check['ok']}
- Hinweis: {language_check['note']}

DOKUMENTE ({len(docs)} vorhanden):
{doc_summary}

FEHLENDE PFLICHTDOKUMENTE: {', '.join(completeness['missing_labels']) if completeness['missing_labels'] else 'Alle vorhanden'}

ERWARTETE PFLICHTDOKUMENTE (Standard): {', '.join(REQUIRED_DOCUMENT_TYPES)}

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

        except Exception as exc:
            logger.error("[AI_SCREENING] DeepSeek error: %s", exc)
            ai_error = str(exc)
    else:
        ai_report = "KI-Prüfung nicht verfügbar (DEEPSEEK_API_KEY nicht konfiguriert). Lokale Vorprüfung abgeschlossen."

    suggested_stage = _suggest_stage(local_summary, formal_precheck)
    next_actions = _suggest_next_actions(
        completeness,
        formal_precheck,
        suggested_stage,
        local_summary["suggested_next_step"],
    )

    precheck_status = "ok" if local_summary["formal_result"] == "precheck_passed" else "action_required"
    matrix_version = local_summary.get("reference_basis", {}).get("version")

    return {
        "screening_id": str(uuid.uuid4()),
        "application_id": application.get("id"),
        "screened_at": datetime.now(timezone.utc).isoformat(),
        "screened_by": "ai_system",
        "ai_provider": "deepseek",
        "ai_model": ai_model_used,
        "ai_tokens_used": ai_tokens_used,
        "local_checks": {
            "completeness": completeness,
            "anabin_assessment": anabin_info,
            "language_level_check": language_check,
        },
        "evidence": local_summary["evidence"],
        "criteria_checked": local_summary["criteria_checked"],
        "criteria_failed": local_summary["criteria_failed"],
        "criteria_missing": local_summary["criteria_missing"],
        "formal_result": local_summary["formal_result"],
        "risk_flags": local_summary["risk_flags"],
        "staff_action_required": local_summary["formal_result"] != "precheck_passed",
        "suggested_next_step": local_summary["suggested_next_step"],
        "decision_scope": "vorpruefung_only_no_final_admission_decision",
        "confidence_scope": "high_for_documented_formal_rules_manual_review_for_exceptions",
        "screening_breakdown": {
            "completeness": {
                "status": "complete" if completeness["complete"] else "incomplete",
                "missing_documents": completeness["missing_labels"],
                "present_documents": completeness["present_labels"],
                "reasons": completeness["reasons"],
                "evidence": completeness["evidence"],
            },
            "formal_precheck": {
                "status": local_summary["formal_result"],
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
        "rule_matrix_version": matrix_version,
        "decision_note": "Regelbasierte Vorprüfung + KI-Empfehlung via DeepSeek. Keine bindende Entscheidung. Staff-Review erforderlich.",
    }


def _suggest_stage(local_summary: dict, formal_precheck: dict) -> str:
    if local_summary["formal_result"] == "documents_missing":
        return "documents_requested"
    if local_summary["formal_result"] in {"language_gap", "manual_review_required"}:
        return "school_degree_assessed"
    if formal_precheck["status"] == "critical":
        return "alternative_path_advisory"
    if formal_precheck["status"] == "unclear":
        return "school_degree_assessed"
    return "language_course_recommended"


def _suggest_next_actions(
    completeness: dict,
    formal_precheck: dict,
    suggested_stage: str,
    suggested_next_step: str,
) -> list:
    actions = []
    if not completeness["complete"]:
        actions.append("Fehlende Pflichtunterlagen beim Bewerber anfordern.")
    if completeness["invalid_types"]:
        actions.append("Ungültige/abgelehnte Dokumente durch neue Nachweise ersetzen lassen.")
    if formal_precheck["status"] == "critical":
        actions.append("Fall an erfahrenes Staff-Mitglied zur vertieften Anerkennungsprüfung eskalieren.")
    if formal_precheck["status"] in ("critical", "unclear"):
        actions.append("Externe Referenzprüfung (z. B. Anabin) manuell durchführen und dokumentieren.")
    if formal_precheck["status"] == "plausible":
        actions.append("Interview oder Beratungsgespräch terminieren und Ergebnis dokumentieren.")
    actions.append(f"Nächster Prozessschritt laut Regelmatrix: {suggested_next_step}.")
    actions.append(f"Staff entscheidet final über Stage-Wechsel ({suggested_stage}).")
    return actions
