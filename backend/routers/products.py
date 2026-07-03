"""
Produkt-/Tarifkatalog: dynamische Preise fuer Website, Bewerbung und Rechnungen.
Admin-CRUD unter /admin/tariffs, Soft-Delete via is_active=False.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from bson import ObjectId
from deps import get_current_user, require_roles, ADMIN_ROLES, get_db

router = APIRouter(prefix="/api/products", tags=["products"])

CATEGORIES = ("kurs", "sprache", "pruefung", "gebuehr", "service", "unterkunft", "kombi", "sonstig")

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


def _serialize(p: dict) -> dict:
    return {
        "id": str(p["_id"]),
        "code": p.get("code"),
        "name": p.get("name"),
        "description": p.get("description", ""),
        "price": p.get("price", 0),
        "currency": p.get("currency", "EUR"),
        "category": p.get("category", "sonstig"),
        "is_active": p.get("is_active", True),
    }


async def _ensure_seed(db):
    if await db.products.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        await db.products.insert_many([
            {**p, "is_active": True, "created_at": now} for p in DEFAULT_PRODUCTS
        ])


@router.get("/public")
async def list_public_products():
    """Oeffentlicher Katalog: nur aktive Produkte (fuer /courses, /services, /apply)."""
    db = get_db()
    await _ensure_seed(db)
    items = await db.products.find({"is_active": {"$ne": False}}).sort("category", 1).to_list(300)
    return [_serialize(p) for p in items]


@router.get("")
async def list_products(include_inactive: bool = False, user: dict = Depends(get_current_user)):
    """Interner Katalog (Rechnungen, Admin). include_inactive nur fuer Admins."""
    db = get_db()
    await _ensure_seed(db)
    query = {} if (include_inactive and user.get("role") in ADMIN_ROLES) else {"is_active": {"$ne": False}}
    items = await db.products.find(query).sort([("category", 1), ("name", 1)]).to_list(300)
    return [_serialize(p) for p in items]


@router.post("")
async def create_product(request: Request, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    body = await request.json()
    code = (body.get("code") or "").strip().upper()
    name = (body.get("name") or "").strip()
    if not code or not name:
        raise HTTPException(status_code=400, detail="code und name sind erforderlich")
    try:
        price = float(body.get("price", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Ungueltiger Preis")
    category = body.get("category") or "sonstig"
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Ungueltige Kategorie. Erlaubt: {', '.join(CATEGORIES)}")
    db = get_db()
    await _ensure_seed(db)
    if await db.products.find_one({"code": code}):
        raise HTTPException(status_code=409, detail=f"Produkt-Code '{code}' existiert bereits")
    doc = {
        "code": code, "name": name,
        "description": (body.get("description") or "").strip(),
        "price": price, "currency": body.get("currency") or "EUR",
        "category": category, "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "created_by": user["id"],
    }
    result = await db.products.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.put("/{product_id}")
async def update_product(product_id: str, request: Request, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    body = await request.json()
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    update = {}
    for field in ("name", "description", "currency"):
        if field in body:
            update[field] = (body[field] or "").strip()
    if "price" in body:
        try:
            update["price"] = float(body["price"])
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Ungueltiger Preis")
    if "category" in body:
        if body["category"] not in CATEGORIES:
            raise HTTPException(status_code=400, detail="Ungueltige Kategorie")
        update["category"] = body["category"]
    if "is_active" in body:
        update["is_active"] = bool(body["is_active"])
    if "code" in body:
        new_code = (body["code"] or "").strip().upper()
        existing = await db.products.find_one({"code": new_code, "_id": {"$ne": oid}})
        if existing:
            raise HTTPException(status_code=409, detail=f"Produkt-Code '{new_code}' existiert bereits")
        update["code"] = new_code
    if not update:
        raise HTTPException(status_code=400, detail="Keine Aenderungen")
    update["updated_at"] = datetime.now(timezone.utc)
    result = await db.products.update_one({"_id": oid}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    doc = await db.products.find_one({"_id": oid})
    return _serialize(doc)


@router.delete("/{product_id}")
async def archive_product(product_id: str, user: dict = Depends(require_roles(*ADMIN_ROLES))):
    """Soft-Delete: Produkt wird archiviert (is_active=False), nicht geloescht."""
    db = get_db()
    try:
        oid = ObjectId(product_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    result = await db.products.update_one(
        {"_id": oid},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produkt nicht gefunden")
    return {"status": "archived", "id": product_id}
