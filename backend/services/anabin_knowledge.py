"""
Anabin Knowledge Base – Persistente Wissensbasis fuer Laenderanerkennungen.

Strategie: Retrieval-first
- Daten werden in MongoDB Collection 'anabin_knowledge' persistiert
- Initiales Seeding aus statischen Referenzdaten
- Erweiterbar durch Staff via Admin-UI oder manuelle Eintraege
- KI-Screening greift immer zuerst auf die DB zu (Cache-first)
- Nur bei unbekannten Laendern wird eine Neurecherche angestossen

Erweiterung v2: Degree-Type-Matching, Confidence, Queue-Automation
- Matching: Land + Abschluss + Varianten / Synonyme
- Confidence-Logik aus Wissensbasis
- Auto-Queue-Erstellung bei unknown/uncertain/special_case
- Feedback-Loop: Staff-Entscheidungen fliessen in Wissensbasis zurueck
"""
import logging
import uuid
from datetime import datetime, timezone
from database import get_db

logger = logging.getLogger(__name__)


async def lookup_knowledge(country: str, degree_type: str = None, application_id: str = None) -> dict:
    """
    Erweiterter Wissensbasis-Lookup:
    1. Exakter Match: Land + Abschlusstyp
    2. Land-Match: Nur Land (degree_type='Allgemein')
    3. Fuzzy: Synonyme / degree_variants
    4. Unknown: Auto-Queue + Auto-Flag

    Gibt strukturierte Wissensbasis-Antwort zurueck mit:
    - category, confidence, operational_classification
    - requires_staff_decision, is_special_case
    - standard_response, staff_note
    - match_type (exact, country_only, variant, fuzzy, unknown)
    """
    if not country:
        return {
            "category": "unbekannt",
            "confidence": "unknown",
            "label": "Herkunftsland nicht angegeben – manuelle Pruefung erforderlich",
            "source": "missing_data",
            "match_type": "none",
            "requires_staff_decision": True,
            "is_special_case": False,
            "operational_classification": "",
            "standard_response": "",
            "staff_note": "",
            "knowledge_id": None,
        }

    db = get_db()
    country_lower = country.lower().strip()
    degree_lower = (degree_type or "").lower().strip() if degree_type else None

    # ── 1. EXAKT: Land + Abschlusstyp ─────────────────────────────
    if degree_lower:
        entry = await db.anabin_knowledge.find_one({
            "country_lower": country_lower,
            "$or": [
                {"degree_type": {"$regex": f"^{degree_type}$", "$options": "i"}},
                {"degree_variants": {"$regex": degree_lower, "$options": "i"}},
            ],
            "status": {"$ne": "locked"},
        })
        if entry:
            await _increment_usage(db, entry["_id"])
            return _build_result(entry, "exact")

    # ── 2. LAND-MATCH (Allgemein) ─────────────────────────────────
    entry = await db.anabin_knowledge.find_one(
        {"country_lower": country_lower, "status": {"$ne": "locked"}},
    )
    if entry:
        await _increment_usage(db, entry["_id"])
        match_type = "country_only" if degree_lower else "exact"
        return _build_result(entry, match_type)

    # ── 3. FUZZY: Erste 4 Zeichen ─────────────────────────────────
    if len(country_lower) >= 4:
        entry = await db.anabin_knowledge.find_one(
            {"country_lower": {"$regex": f"^{country_lower[:4]}"}, "status": {"$ne": "locked"}},
        )
        if entry:
            await _increment_usage(db, entry["_id"])
            result = _build_result(entry, "fuzzy")
            result["label"] = f"{result['label']} – Aehnlichkeitstreffer fuer '{country}'"
            result["confidence"] = "low"
            result["requires_staff_decision"] = True
            return result

    # ── 4. UNKNOWN: Auto-Flag + Auto-Queue ────────────────────────
    now = datetime.now(timezone.utc).isoformat()

    # Eintrag als 'pruefen' anlegen (idempotent)
    await db.anabin_knowledge.update_one(
        {"country_lower": country_lower},
        {"$setOnInsert": {
            "country": country,
            "country_lower": country_lower,
            "degree_type": degree_type or "Allgemein",
            "degree_variants": [],
            "category": "pruefen",
            "confidence": "unknown",
            "status": "in_review",
            "is_special_case": False,
            "staff_note": "",
            "source": "auto_flagged",
            "source_url": "",
            "operational_classification": "",
            "standard_response": "",
            "requires_staff_decision": True,
            "notes": f"Automatisch erkannt: '{country}' – nicht in Wissensbasis. Manuelle Pruefung erforderlich.",
            "last_verified": now,
            "last_verified_by": "system",
            "version": 1,
            "change_history": [{"action": "auto_created", "by": "system", "at": now, "fields": ["all"]}],
            "usage_count": 1,
            "created_at": now,
            "updated_at": now,
        }},
        upsert=True,
    )

    # Auto-Queue erstellen (idempotent: nur wenn kein offener Eintrag)
    await _auto_create_queue_entry(db, country, degree_type, application_id, "no_mapping_found")

    return {
        "category": "pruefen",
        "confidence": "unknown",
        "label": f"Land '{country}' nicht in Wissensbasis – manuelle Pruefung erforderlich",
        "source": "auto_flagged",
        "match_type": "unknown",
        "requires_staff_decision": True,
        "is_special_case": False,
        "operational_classification": "",
        "standard_response": "",
        "staff_note": "",
        "knowledge_id": None,
    }


def _build_result(entry: dict, match_type: str) -> dict:
    """Baut strukturierte Antwort aus Wissensbasis-Eintrag."""
    return {
        "category": entry.get("category", "pruefen"),
        "confidence": entry.get("confidence", "medium"),
        "label": f"{entry.get('notes', '')} ({entry.get('country', '')})",
        "source": entry.get("source", "anabin_seed"),
        "last_verified": entry.get("last_verified"),
        "match_type": match_type,
        "requires_staff_decision": entry.get("requires_staff_decision", False),
        "is_special_case": entry.get("is_special_case", False),
        "operational_classification": entry.get("operational_classification", ""),
        "standard_response": entry.get("standard_response", ""),
        "staff_note": entry.get("staff_note", ""),
        "degree_type": entry.get("degree_type", "Allgemein"),
        "knowledge_id": str(entry["_id"]) if "_id" in entry else None,
    }


async def _increment_usage(db, entry_id):
    """Erhoeht den Nutzungszaehler und setzt updated_at."""
    try:
        await db.anabin_knowledge.update_one(
            {"_id": entry_id},
            {"$inc": {"usage_count": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
        )
    except Exception:
        pass


async def _auto_create_queue_entry(db, country: str, degree_type: str, application_id: str, reason: str):
    """Erstellt idempotent einen Review-Queue-Eintrag fuer unbekannte Kombinationen."""
    # Pruefe ob bereits offener Eintrag existiert
    existing = await db.anabin_review_queue.find_one({
        "country": country,
        "status": {"$in": ["open", "in_progress"]},
    })
    if existing:
        # Aktualisiere statt Duplikat
        update = {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        if application_id:
            update["$addToSet"] = {"related_applications": application_id}
        await db.anabin_review_queue.update_one({"_id": existing["_id"]}, update)
        logger.info(f"[ANABIN_QUEUE] Updated existing queue entry for {country}")
        return

    now = datetime.now(timezone.utc).isoformat()
    reason_labels = {
        "no_mapping_found": f"Kein belastbares Mapping fuer '{country}' gefunden",
        "low_confidence": f"Niedrige Konfidenz fuer '{country}' – Pruefung empfohlen",
        "special_case": f"Sonderfall erkannt fuer '{country}'",
        "fuzzy_match_only": f"Nur unscharfer Treffer fuer '{country}'",
        "staff_required": f"Staff-Entscheid erforderlich fuer '{country}'",
    }

    item = {
        "queue_id": str(uuid.uuid4())[:8],
        "application_id": application_id,
        "related_applications": [application_id] if application_id else [],
        "applicant_name": "",
        "country": country,
        "degree_type": degree_type or "Unbekannt",
        "reason": reason,
        "reason_label": reason_labels.get(reason, reason),
        "suggested_matches": [],
        "last_screening_output": {},
        "owner": None,
        "status": "open",
        "priority": "high" if reason == "no_mapping_found" else "medium",
        "priority_order": 1 if reason == "no_mapping_found" else 2,
        "next_action": "Anabin pruefen und operative Einstufung vornehmen",
        "resolution": None,
        "resolved_at": None,
        "resolved_by": None,
        "created_at": now,
        "created_by": "system",
        "updated_at": now,
    }
    await db.anabin_review_queue.insert_one(item)
    logger.info(f"[ANABIN_QUEUE] Auto-created queue entry for {country} ({reason})")


async def create_queue_from_screening(country: str, degree_type: str, application_id: str, reason: str, screening_output: dict = None):
    """Oeffentliche Funktion: Queue-Eintrag aus Screening-Ergebnis erstellen."""
    db = get_db()
    await _auto_create_queue_entry(db, country, degree_type, application_id, reason)
    # Falls Screening-Output vorhanden, an Queue-Eintrag anhaengen
    if screening_output:
        await db.anabin_review_queue.update_one(
            {"country": country, "status": {"$in": ["open", "in_progress"]}},
            {"$set": {"last_screening_output": {
                "suggested_stage": screening_output.get("suggested_stage"),
                "anabin_category": screening_output.get("anabin_category"),
                "confidence": screening_output.get("confidence"),
                "is_complete": screening_output.get("is_complete"),
            }}},
        )


async def resolve_queue_with_feedback(queue_item_id: str, resolution: dict, resolved_by: str) -> dict:
    """
    Loest einen Queue-Eintrag und schreibt das Ergebnis in die Wissensbasis zurueck.
    Feedback-Loop: Staff-Entscheidung → Wissensbasis → Folge-Screenings.
    """
    from bson import ObjectId
    db = get_db()

    # Queue-Eintrag laden
    try:
        item = await db.anabin_review_queue.find_one({"_id": ObjectId(queue_item_id)})
    except Exception:
        return {"error": "Ungueltige ID"}
    if not item:
        return {"error": "Queue-Eintrag nicht gefunden"}

    now = datetime.now(timezone.utc).isoformat()

    # Queue als resolved markieren
    await db.anabin_review_queue.update_one(
        {"_id": ObjectId(queue_item_id)},
        {"$set": {
            "status": "resolved",
            "resolution": resolution.get("resolution_note", "Mapping geprueft und akzeptiert"),
            "resolved_at": now,
            "resolved_by": resolved_by,
        }},
    )

    # Wissensbasis aktualisieren wenn Mapping-Daten mitgegeben
    if resolution.get("update_knowledge"):
        kb_update = resolution["update_knowledge"]
        country_lower = item.get("country", "").lower().strip()

        update_fields = {}
        for field in ["category", "confidence", "status", "is_special_case", "staff_note",
                       "operational_classification", "standard_response", "requires_staff_decision", "notes"]:
            if field in kb_update:
                update_fields[field] = kb_update[field]

        if update_fields:
            update_fields["updated_at"] = now
            update_fields["last_verified"] = now
            update_fields["last_verified_by"] = resolved_by

            result = await db.anabin_knowledge.update_one(
                {"country_lower": country_lower},
                {
                    "$set": update_fields,
                    "$inc": {"version": 1},
                    "$push": {"change_history": {
                        "action": "queue_resolution_feedback",
                        "by": resolved_by,
                        "at": now,
                        "fields": list(update_fields.keys()),
                        "queue_id": queue_item_id,
                    }},
                },
            )

            if result.modified_count > 0:
                logger.info(f"[ANABIN_FEEDBACK] Knowledge base updated for {item.get('country')} via queue resolution")

    # Audit-Eintrag
    from services.audit import write_audit_log
    await write_audit_log(
        "queue_resolved_with_feedback",
        resolved_by,
        "anabin_review_queue",
        queue_item_id,
        {
            "country": item.get("country"),
            "degree_type": item.get("degree_type"),
            "resolution": resolution.get("resolution_note", ""),
            "knowledge_updated": bool(resolution.get("update_knowledge")),
        },
    )

    return {"resolved": True, "knowledge_updated": bool(resolution.get("update_knowledge"))}

# Static seed data – will be inserted if collection is empty
ANABIN_SEED = [
    # H+ countries (high recognition probability)
    *[{"country": c, "category": "H+", "notes": "Hohe Anerkennungswahrscheinlichkeit"} for c in [
        "Deutschland", "Oesterreich", "Schweiz", "USA", "Kanada", "Australien",
        "Grossbritannien", "Frankreich", "Niederlande", "Belgien", "Schweden",
        "Norwegen", "Daenemark", "Finnland", "Japan", "Suedkorea", "Neuseeland",
        "Irland", "Italien", "Spanien", "Portugal", "Polen", "Tschechien",
        "Luxemburg", "Island", "Singapur", "Israel",
    ]],
    # H countries (recognizable with conditions)
    *[{"country": c, "category": "H", "notes": "Anerkennbar mit moeglichen Auflagen – Einzelfallpruefung"} for c in [
        "China", "Indien", "Brasilien", "Tuerkei", "Russland", "Ukraine",
        "Aegypten", "Marokko", "Tunesien", "Iran", "Vietnam", "Thailand",
        "Mexiko", "Argentinien", "Kolumbien", "Chile", "Indonesien", "Malaysia",
        "Pakistan", "Bangladesch", "Sri Lanka", "Philippinen", "Suedafrika",
        "Jordanien", "Libanon", "Kasachstan", "Usbekistan", "Georgien",
        "Moldawien", "Serbien", "Bosnien-Herzegowina", "Nordmazedonien",
        "Albanien", "Kosovo", "Montenegro",
    ]],
    # D countries (restricted recognition)
    *[{"country": c, "category": "D", "notes": "Eingeschraenkte Anerkennung – intensive Einzelfallpruefung erforderlich"} for c in [
        "Afghanistan", "Irak", "Syrien", "Libyen", "Somalia", "Jemen",
        "Eritrea", "Aethiopien", "Nigeria", "Ghana", "Kamerun", "Senegal",
        "Mali", "Niger", "Burkina Faso", "DR Kongo", "Suedsudan", "Tschad",
    ]],
]


async def seed_anabin_knowledge():
    """Seed Anabin knowledge base if empty, or migrate existing entries to extended schema."""
    db = get_db()
    count = await db.anabin_knowledge.count_documents({})

    if count == 0:
        entries = []
        now = datetime.now(timezone.utc).isoformat()
        for item in ANABIN_SEED:
            entries.append({
                "country": item["country"],
                "country_lower": item["country"].lower().strip(),
                "degree_type": "Allgemein",
                "degree_variants": [],
                "category": item["category"],
                "confidence": "high" if item["category"] in ("H+", "D") else "medium",
                "status": "verified",
                "is_special_case": False,
                "staff_note": "",
                "source": "anabin_seed",
                "source_url": "",
                "operational_classification": "",
                "standard_response": "",
                "requires_staff_decision": item["category"] == "D",
                "notes": item["notes"],
                "last_verified": now,
                "last_verified_by": "system",
                "version": 1,
                "change_history": [{"action": "seeded", "by": "system", "at": now, "fields": ["all"]}],
                "usage_count": 0,
                "created_at": now,
                "updated_at": now,
            })

        if entries:
            await db.anabin_knowledge.insert_many(entries)
            await db.anabin_knowledge.create_index("country_lower")
            await db.anabin_knowledge.create_index("category")
            await db.anabin_knowledge.create_index("status")
            await db.anabin_knowledge.create_index("confidence")
            logger.info(f"[ANABIN] Seeded {len(entries)} country entries with extended schema")
    else:
        # Migration: add missing fields to existing entries
        sample = await db.anabin_knowledge.find_one({})
        if sample and "status" not in sample:
            now = datetime.now(timezone.utc).isoformat()
            await db.anabin_knowledge.update_many(
                {"status": {"$exists": False}},
                {"$set": {
                    "degree_type": "Allgemein",
                    "degree_variants": [],
                    "confidence": "medium",
                    "status": "verified",
                    "is_special_case": False,
                    "staff_note": "",
                    "source_url": "",
                    "operational_classification": "",
                    "standard_response": "",
                    "requires_staff_decision": False,
                    "last_verified_by": "system",
                    "version": 1,
                    "change_history": [{"action": "migrated", "by": "system", "at": now, "fields": ["schema_v2"]}],
                    "usage_count": 0,
                    "created_at": now,
                    "updated_at": now,
                }},
            )
            # Create indexes
            await db.anabin_knowledge.create_index("category")
            await db.anabin_knowledge.create_index("status")
            await db.anabin_knowledge.create_index("confidence")
            logger.info(f"[ANABIN] Migrated {count} existing entries to extended schema")
        else:
            logger.info(f"[ANABIN] Knowledge base already has extended schema ({count} entries)")


async def lookup_country(country: str) -> dict:
    """Legacy-Wrapper: Ruft lookup_knowledge auf (abwaertskompatibel)."""
    result = await lookup_knowledge(country)
    return result


async def get_all_entries():
    """Get all Anabin knowledge entries for admin/staff review."""
    db = get_db()
    entries = await db.anabin_knowledge.find({}, {"_id": 0}).sort("country", 1).to_list(500)
    return entries
