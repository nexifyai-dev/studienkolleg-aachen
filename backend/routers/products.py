"""
Produkt-/Tarifkatalog fuer Angebote und Rechnungserstellung.

Tarife (= Produkte) werden DB-persistiert verwaltet (Admin: /admin/tariffs).
DEFAULT_PRODUCTS dienen als initialer Seed (is_active=true), danach liegt
alles in der Collection "products" (_id = code).
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from deps import get_current_user, get_db, STAFF_ROLES, ADMIN_ROLES

router = APIRouter(prefix="/api/products", tags=["products"])

DEFAULT_PRODUCTS = [
    {"code": "SK-TKURS", "name": "T-Kurs (Technik)", "description": "Studienkolleg Vorbereitungskurs Technik", "price": 4500, "currency": "EUR", "category": "kurs"},
    {"code": "SK-MKURS", "name": "M-Kurs (Medizin/Bio)", "description": "Studienkolleg Vorbereitungskurs Medizin/Biologie", "price": 4500, "currency": "EUR", "category": "kurs"},
    {"code": "SK-WKURS", "name": "W-Kurs (Wirtschaft)", "description": "Studienkolleg Vorbereitungskurs Wirtschaft", "price": 4500, "currency": "EUR", "category": "kurs"},
    {"code": "SK-GKURS", "name": "G-Kurs (Geistes-/Sozialwiss.)", "description": "Studienkolleg Vorbereitungskurs Geisteswissenschaften", "price": 4500, "currency": "EUR", "category": "kurs"},
    {"code": "SK-SKURS", "name": "S-Kurs (Sprachwiss.)", "description": "Studienkolleg Vorbereitungskurs Sprachwissenschaften", "price": 4500, "currency": "EUR", "category": "kurs"},
    {"code": "DSH-PREP", "name": "DSH-Vorbereitung", "description": "Intensivkurs Deutsche Sprachpruefung Hochschulzugang", "price": 2800, "currency": "EUR", "category": "sprache"},
    {"code": "TESTDAF", "name": "TestDaF-Vorbereitung", "description": "Intensivkurs TestDaF-Vorbereitung", "price": 2400, "currency": "EUR", "category": "sprache"},
    {"code": "B1-B2", "name": "Deutsch B1-B2 Kurs", "description": "Deutschkurs Niveau B1 bis B2", "price": 1800, "currency": "EUR", "category": "sprache"},
    {"code": "A1-A2", "name": "Deutsch A1-A2 Kurs", "description": "Deutschkurs Niveau A1 bis A2", "price": 1200, "currency": "EUR", "category": "sprache"},
    {"code": "FSP-GEBUEHR", "name": "Feststellungspruefung", "description": "Pruefungsgebuehr Feststellungspruefung", "price": 150, "currency": "EUR", "category": "pruefung"},
    {"code": "ANMELDEGEBUEHR", "name": "Anmeldegebuehr", "description": "Einmalige Anmeldegebuehr", "price": 250, "currency": "EUR", "category": "gebuehr"},
    {"code": "VISUM-SERVICE", "name": "Visum-Beratung & Service", "description": "Unterstuetzung bei Visumantrag und Dokumentenvorbereitung", "price": 350, "currency": "EUR", "category": "service"},
    {"code": "UNTERKUNFT-M", "name": "Unterkunft (pro Monat)", "description": "Studentenunterkunft Monatsmiete", "price": 450, "currency": "EUR", "category": "unterkunft"},
    {"code": "KOMBI-BASIC", "name": "Kombi-Paket Basic", "description": "Kurs + Anmeldegebuehr + DSH-Vorbereitung", "price": 7200, "currency": "EUR", "category": "kombi"},
    {"code": "KOMBI-PREMIUM", "name": "Kombi-Paket Premium", "description": "Kurs + Anmeldegebuehr + DSH + Visum-Service + 3 Monate Unterkunft", "price": 9500, "currency": "EUR", "category": "kombi"},
    {"code": "KOMBI-ALL-IN", "name": "All-Inclusive Paket", "description": "Vollstaendiges Paket mit Kurs, Sprache, Visum, Unterkunft (6 Monate), Betreuung", "price": 14500, "currency": "EUR", "category": "kombi"},
    {"code": "CUSTOM", "name": "Individuelle Position", "description": "Manuelle Rechnungsposition", "price": 0, "currency": "EUR", "category": "sonstig"},
]


def _serialize(doc: dict) -> dict:
    out = dict(doc)
    if "_id" in out:
        out["code"] = out["code"] or str(out.pop("_id"))
        out.pop("_id", None)
    return out


async def _seed_defaults(db) -> None:
    """Defaults einmalig in die DB schreiben (is_active=true)."""
    for p in DEFAULT_PRODUCTS:
        await db.products.update_one(
            {"_id": p["code"]},
            {"$setOnInsert": {**p, "_id": p["code"], "is_active": True, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )


@router.get("")
async def list_products(user: dict = Depends(get_current_user)):
    """Liste aller Tarife/Produkte inkl. inaktiver (authentifiziert)."""
    db = get_db()
    await _seed_defaults(db)
    docs = await db.products.find({}, {"_id": 0}).sort("category", 1).to_list(500)
    return [_serialize(d) for d in docs]


@router.get("/public")
async def list_public_products():
    """Oeffentliche Tarifliste – nur aktive Tarife (Website-Preise)."""
    db = get_db()
    await _seed_defaults(db)
    docs = await db.products.find({"is_active": True}, {"_id": 0}).sort("category", 1).to_list(500)
    return [_serialize(d) for d in docs]


@router.post("")
async def create_product(body: dict, user: dict = Depends(get_current_user)):
    """Neuen Tarif anlegen (Admin/Staff)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    code = str(body.get("code") or "").strip().upper()
    if not code or not body.get("name"):
        raise HTTPException(status_code=400, detail="code und name sind erforderlich")
    db = get_db()
    if await db.products.find_one({"_id": code}):
        raise HTTPException(status_code=409, detail=f"Tarif {code} existiert bereits")
    doc = {
        "_id": code,
        "code": code,
        "name": body.get("name"),
        "description": body.get("description", ""),
        "price": float(body.get("price", 0) or 0),
        "currency": body.get("currency", "EUR"),
        "category": body.get("category", "sonstig"),
        "is_active": body.get("is_active", True),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.products.insert_one(doc)
    return _serialize(doc)


@router.patch("/{code}")
async def update_product(code: str, body: dict, user: dict = Depends(get_current_user)):
    """Tarif aktualisieren (Admin/Staff)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    existing = await db.products.find_one({"_id": code.upper()})
    if not existing:
        raise HTTPException(status_code=404, detail=f"Tarif {code} nicht gefunden")
    allowed = {"name", "description", "price", "currency", "category", "is_active"}
    updates = {k: v for k, v in body.items() if k in allowed and v is not None}
    if "price" in updates:
        updates["price"] = float(updates["price"])
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.products.update_one({"_id": code.upper()}, {"$set": updates})
    updated = await db.products.find_one({"_id": code.upper()}, {"_id": 0})
    return _serialize(updated)


@router.delete("/{code}")
async def delete_product(code: str, user: dict = Depends(get_current_user)):
    """Tarif loeschen (Admin/Staff)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    res = await db.products.delete_one({"_id": code.upper()})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Tarif {code} nicht gefunden")
    return {"ok": True}
