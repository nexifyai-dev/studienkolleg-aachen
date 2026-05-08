"""
Produkt-/Paketkatalog fuer Rechnungserstellung.
Systemweit als Auswahl-/Suchfeld verfuegbar.
"""
from fastapi import APIRouter, Depends, HTTPException
from deps import get_current_user, get_db

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


@router.get("")
async def list_products(user: dict = Depends(get_current_user)):
    """Liste aller verfuegbaren Produkte/Pakete."""
    db = get_db()
    custom = await db.products.find({}, {"_id": 0}).to_list(200)
    all_products = DEFAULT_PRODUCTS + custom if custom else DEFAULT_PRODUCTS
    return all_products
