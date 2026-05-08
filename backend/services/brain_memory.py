"""
Brain Memory Service – Persistente KI-Gedächtnisschicht für das gesamte W2G-System.

Architektur:
- mem0 OSS als Memory-Framework
- MongoDB als Backend-Store (kein externes Qdrant nötig)
- OpenRouter deepseek/deepseek-v4-flash als LLM fuer Memory-Extraktion + Antworten
- 4 Memory-Ebenen:
  1. entity_memory:       Pro Bewerber/Staff – Fakten, Präferenzen, Historie
  2. institutional_memory: Globale Policies, Standardprozesse, Studienkolleg-Wissen
  3. email_memory:        E-Mail-Kontext, Kommunikationsmuster
  4. process_memory:      Vorgänge, Entscheidungen, Audit-Trail

Alle Vorgänge (Bewerbung, Dokumente, Rechnungen, Aufgaben, E-Mails)
speisen automatisch Fakten in die Memory-Schicht ein.
"""
import os
import logging
import json
from datetime import datetime, timezone
from typing import Optional
from database import get_db

logger = logging.getLogger(__name__)

# ── Memory-Kategorien ──────────────────────────────────────────────────────────
CATEGORIES = {
    "applicant_profile": "Bewerberdaten, persoenliche Informationen, Praeferenzen",
    "application_status": "Bewerbungsstatus, Statuswechsel, Timeline",
    "document_review": "Dokumentenpruefung, Ergebnisse, Nachforderungen",
    "communication": "E-Mails, Portal-Nachrichten, Gespraechsverlauf",
    "financial": "Rechnungen, Zahlungen, offene Betraege",
    "task_activity": "Aufgaben, Anfragen, Wiedervorlagen",
    "decision": "Entscheidungen, Genehmigungen, Ablehnungen",
    "institutional": "Policies, Standardantworten, Prozessregeln",
    "appointment": "Termine, Buchungen, Absagen",
}


async def _get_openrouter_client():
    """OpenRouter-Client fuer Memory-Extraktion."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return None
    from openai import AsyncOpenAI
    return AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


async def extract_facts(text: str, context_type: str = "general") -> list:
    """Extrahiert strukturierte Fakten aus Text via Gemini Flash Lite (guenstig)."""
    client = await _get_openrouter_client()
    if not client:
        return []

    try:
        response = await client.chat.completions.create(
            model="deepseek/deepseek-v4-flash",
            messages=[
                {"role": "system", "content": f"""Du bist ein Fakten-Extraktor fuer ein Studienkolleg-CRM.
Extrahiere ALLE relevanten Fakten aus dem folgenden Text.
Kontext-Typ: {context_type}

Gib ein JSON-Array von Objekten zurueck:
[{{"fact": "...", "category": "...", "confidence": 0.0-1.0}}]

Kategorien: {', '.join(CATEGORIES.keys())}
Nur valides JSON. Keine Erklaerungen."""},
                {"role": "user", "content": text[:3000]}
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        return json.loads(content)
    except Exception as e:
        logger.warning(f"[BRAIN] Fakten-Extraktion fehlgeschlagen: {e}")
        return []


async def remember(entity_id: str, entity_type: str, facts: list, source: str = "system"):
    """Speichert Fakten in die Memory-Datenbank."""
    db = get_db()
    now = datetime.now(timezone.utc)

    memories = []
    for fact in facts:
        if isinstance(fact, str):
            fact = {"fact": fact, "category": "general", "confidence": 0.8}

        memory_doc = {
            "entity_id": entity_id,
            "entity_type": entity_type,  # applicant, staff, institution, email_thread
            "fact": fact.get("fact", str(fact)),
            "category": fact.get("category", "general"),
            "confidence": fact.get("confidence", 0.8),
            "source": source,
            "created_at": now,
            "active": True,
        }
        memories.append(memory_doc)

    if memories:
        await db.brain_memories.insert_many(memories)
        logger.info(f"[BRAIN] {len(memories)} Fakten gespeichert fuer {entity_type}:{entity_id} (Quelle: {source})")

    return len(memories)


async def recall(entity_id: str, entity_type: str = None, category: str = None,
                 limit: int = 50, min_confidence: float = 0.5) -> list:
    """Ruft gespeicherte Fakten ab."""
    db = get_db()
    query = {"entity_id": entity_id, "active": True, "confidence": {"$gte": min_confidence}}
    if entity_type:
        query["entity_type"] = entity_type
    if category:
        query["category"] = category

    memories = await db.brain_memories.find(query, {"_id": 0}).sort("created_at", -1).to_list(limit)
    return memories


async def recall_context(entity_id: str, max_chars: int = 4000) -> str:
    """Generiert einen kompakten Kontext-String aus allen Erinnerungen."""
    memories = await recall(entity_id, limit=80)
    if not memories:
        return ""

    by_category = {}
    for m in memories:
        cat = m.get("category", "general")
        by_category.setdefault(cat, []).append(m["fact"])

    parts = []
    for cat, facts in by_category.items():
        label = CATEGORIES.get(cat, cat)
        unique_facts = list(dict.fromkeys(facts))  # Deduplizieren
        parts.append(f"[{label}]\n" + "\n".join(f"- {f}" for f in unique_facts[:10]))

    context = "\n\n".join(parts)
    return context[:max_chars]


async def search_memories(query: str, entity_type: str = None, limit: int = 20) -> list:
    """Textsuche ueber alle Memories."""
    db = get_db()
    search_query = {"active": True, "fact": {"$regex": query, "$options": "i"}}
    if entity_type:
        search_query["entity_type"] = entity_type
    return await db.brain_memories.find(search_query, {"_id": 0}).sort("created_at", -1).to_list(limit)


async def forget(entity_id: str, category: str = None):
    """Markiert Erinnerungen als inaktiv (Soft-Delete)."""
    db = get_db()
    query = {"entity_id": entity_id}
    if category:
        query["category"] = category
    result = await db.brain_memories.update_many(query, {"$set": {"active": False}})
    return result.modified_count


# ── Automatische Wissens-Ingestion ─────────────────────────────────────────────

async def ingest_application_event(application_id: str, applicant_id: str, event_type: str, data: dict):
    """Wird bei jedem Bewerbungs-Event aufgerufen – speichert Fakten."""
    facts = []

    if event_type == "stage_changed":
        facts.append({
            "fact": f"Bewerbungsstatus geaendert: {data.get('old_stage','?')} → {data.get('new_stage','?')}",
            "category": "application_status", "confidence": 1.0
        })
        if data.get("reason"):
            facts.append({
                "fact": f"Grund fuer Statusaenderung: {data['reason']}",
                "category": "decision", "confidence": 0.95
            })

    elif event_type == "document_reviewed":
        facts.append({
            "fact": f"Dokument '{data.get('doc_type','')}' wurde {data.get('status','bearbeitet')}",
            "category": "document_review", "confidence": 1.0
        })

    elif event_type == "note_added":
        content = data.get("content", "")[:200]
        extracted = await extract_facts(content, "staff_note")
        facts.extend(extracted)
        if not extracted:
            facts.append({"fact": f"Notiz: {content}", "category": "communication", "confidence": 0.9})

    elif event_type == "task_created":
        facts.append({
            "fact": f"Aufgabe erstellt: {data.get('title','')}",
            "category": "task_activity", "confidence": 1.0
        })

    elif event_type == "invoice_created":
        facts.append({
            "fact": f"Rechnung {data.get('invoice_number','')} ueber {data.get('amount',0)} EUR erstellt",
            "category": "financial", "confidence": 1.0
        })

    elif event_type == "appointment_booked":
        facts.append({
            "fact": f"Termin am {data.get('date','')} um {data.get('time','')}: {data.get('type','Beratung')}",
            "category": "appointment", "confidence": 1.0
        })

    elif event_type == "email_received":
        text = f"E-Mail von {data.get('from','')}. Betreff: {data.get('subject','')}. Inhalt: {data.get('body','')[:500]}"
        extracted = await extract_facts(text, "email_communication")
        facts.extend(extracted)
        if not extracted:
            facts.append({"fact": f"E-Mail erhalten: {data.get('subject','')}", "category": "communication", "confidence": 0.9})

    elif event_type == "email_sent":
        facts.append({
            "fact": f"E-Mail gesendet an Bewerber. Betreff: {data.get('subject','')}",
            "category": "communication", "confidence": 1.0
        })

    elif event_type == "message_portal":
        facts.append({
            "fact": f"Portal-Nachricht: {data.get('content','')[:150]}",
            "category": "communication", "confidence": 0.9
        })

    elif event_type == "screening_completed":
        facts.append({
            "fact": f"KI-Screening abgeschlossen. Empfehlung: {data.get('recommendation','')}",
            "category": "decision", "confidence": 0.9
        })

    if facts:
        await remember(applicant_id, "applicant", facts, source=f"event:{event_type}")


async def ingest_email_to_memory(email_data: dict, applicant_id: str = None):
    """Speichert eine E-Mail vollstaendig in der Memory-Schicht."""
    db = get_db()

    # E-Mail in eigene Collection speichern
    email_doc = {
        "message_id": email_data.get("message_id", ""),
        "from_addr": email_data.get("from", ""),
        "to_addr": email_data.get("to", ""),
        "subject": email_data.get("subject", ""),
        "body": email_data.get("body", ""),
        "date": email_data.get("date", ""),
        "direction": email_data.get("direction", "inbound"),  # inbound/outbound
        "applicant_id": applicant_id,
        "processed": False,
        "created_at": datetime.now(timezone.utc),
    }

    # Duplikat-Check via message_id
    if email_doc["message_id"]:
        existing = await db.brain_emails.find_one({"message_id": email_doc["message_id"]})
        if existing:
            return None

    result = await db.brain_emails.insert_one(email_doc)
    email_id = str(result.inserted_id)

    # Fakten extrahieren und dem Bewerber zuordnen
    if applicant_id:
        await ingest_application_event(
            application_id="", applicant_id=applicant_id,
            event_type="email_received" if email_doc["direction"] == "inbound" else "email_sent",
            data=email_data
        )

    # Als verarbeitet markieren
    await db.brain_emails.update_one({"_id": result.inserted_id}, {"$set": {"processed": True}})
    return email_id


async def generate_response(entity_id: str, context_text: str, query: str,
                            tone: str = "professional", lang: str = "de") -> dict:
    """Generiert eine KI-Antwort mit vollem Memory-Kontext via Gemini Flash."""
    client = await _get_openrouter_client()
    if not client:
        return {"content": None, "error": "OpenRouter nicht konfiguriert"}

    # Memory-Kontext laden
    memory_context = await recall_context(entity_id)

    # Institutionelles Wissen laden
    institutional = await recall("institution", entity_type="institution", limit=20)
    inst_text = "\n".join(f"- {m['fact']}" for m in institutional) if institutional else "Keine institutionellen Regeln hinterlegt."

    lang_instruction = "Antworte IMMER auf Deutsch." if lang == "de" else "Always respond in English."

    system_prompt = f"""Du bist der interne KI-Assistent des Studienkolleg Aachen.
Du sprichst wie ein erfahrener Kollege – direkt, knapp, hilfreich. Duze die Mitarbeiter.
{lang_instruction}

WICHTIG: Antworte IMMER in der Sprache der Frage. Wenn die Frage auf Englisch ist, antworte auf Englisch. Wenn auf Deutsch, antworte auf Deutsch.

KRITISCHE REGEL FUER ZAHLEN:
- Nenne NUR Zahlen, die im AKTUELLEN KONTEXT unten stehen.
- Erfinde KEINE Zahlen. Halluziniere NICHT.
- Wenn eine Zahl nicht im Kontext steht, sage "keine Daten vorhanden".
- Unterscheide klar zwischen "offen/in Bearbeit" und "gesamt".

DEIN GEDAECHTNIS ZU DIESER PERSON:
{memory_context or 'Noch keine Erinnerungen vorhanden.'}

WISSENSREGELN:
{inst_text}

AKTUELLER KONTEXT:
{context_text[:3000]}

DEIN CHARAKTER:
- Komm direkt zum Punkt, keine Floskeln
- Gib konkrete Zahlen und Handlungsempfehlungen
- Jede Zahl MUSS aus dem Kontext oben stammen
- Bei Tabellen: Verwende Markdown-Tabellen (| Spalte | Wert |)
- Fettdruck mit **Text** fuer Wichtiges
- Listen mit - Punkt fuer Aufzaehlungen
- Keine Emojis, keine SVG, keine Checkboxen
- Halte Antworten kompakt – maximal 3-4 Absaetze
- Wenn du etwas nicht weisst, sag es direkt"""

    model = "deepseek/deepseek-v4-flash"
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.4,
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0

        # Fakten aus der Antwort lernen
        try:
            new_facts = await extract_facts(f"Frage: {query}\nAntwort: {content[:500]}", "ai_interaction")
            if new_facts and entity_id:
                await remember(entity_id, "applicant", new_facts, source="ai_response")
        except Exception:
            pass

        return {"content": content, "model": model, "tokens": tokens, "error": None}
    except Exception as e:
        logger.error(f"[BRAIN] Response-Generierung fehlgeschlagen: {e}")
        return {"content": None, "error": str(e)}


async def get_brain_stats() -> dict:
    """Statistiken ueber das Brain-System."""
    db = get_db()
    total = await db.brain_memories.count_documents({"active": True})
    by_type = await db.brain_memories.aggregate([
        {"$match": {"active": True}},
        {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}}
    ]).to_list(20)
    by_category = await db.brain_memories.aggregate([
        {"$match": {"active": True}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}}
    ]).to_list(20)
    emails_total = await db.brain_emails.count_documents({})
    emails_processed = await db.brain_emails.count_documents({"processed": True})

    return {
        "total_memories": total,
        "by_entity_type": {t["_id"]: t["count"] for t in by_type},
        "by_category": {c["_id"]: c["count"] for c in by_category},
        "emails_ingested": emails_total,
        "emails_processed": emails_processed,
    }
