"""
Invoice router – CRUD for invoices.

- Staff/Admin: create, list all, update status, view detail
- Applicant: list own invoices, view detail
- Invoice numbers are auto-generated (INV-YYYYMM-XXXX)
"""
from datetime import datetime, timezone, timedelta
from io import BytesIO
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
from models.schemas import InvoiceCreate, InvoiceUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.get("/applicants")
async def list_invoice_applicants(user: dict = Depends(get_current_user)):
    """Return applicant users for invoice creation (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    applicants = await db.users.find(
        {"role": "applicant"},
        {"_id": 1, "full_name": 1, "email": 1}
    ).to_list(500)
    return [{"id": str(a.pop("_id")), **a} for a in applicants]


@router.get("/settings")
async def get_invoice_settings(user: dict = Depends(get_current_user)):
    """Get invoice numbering settings (Staff/Admin)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    settings = await _get_invoice_settings(db)
    # Generate preview
    preview = await _generate_invoice_number(db)
    settings["preview"] = preview
    return settings


@router.put("/settings")
async def update_invoice_settings(body: dict, user: dict = Depends(get_current_user)):
    """Update invoice numbering settings (Admin only)."""
    if user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin only")
    db = get_db()
    allowed = {"prefix", "start_number", "suffix", "include_date"}
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields")
    updates["type"] = "invoice_numbering"
    await db.settings.update_one(
        {"type": "invoice_numbering"}, {"$set": updates}, upsert=True
    )
    await write_audit_log("invoice_settings_updated", user["id"], "settings", "invoice_numbering", updates)
    # Return new settings + preview
    settings = await _get_invoice_settings(db)
    preview = await _generate_invoice_number(db)
    settings["preview"] = preview
    return settings




async def _get_invoice_settings(db) -> dict:
    """Load invoice numbering settings from DB or return defaults."""
    settings = await db.settings.find_one({"type": "invoice_numbering"})
    if settings:
        return {
            "prefix": settings.get("prefix", "INV"),
            "start_number": settings.get("start_number", 1),
            "suffix": settings.get("suffix", ""),
            "include_date": settings.get("include_date", True),
        }
    return {"prefix": "INV", "start_number": 1, "suffix": "", "include_date": True}


async def _generate_invoice_number(db) -> str:
    """Generate sequential invoice number based on settings."""
    cfg = await _get_invoice_settings(db)
    now = datetime.now(timezone.utc)

    if cfg["include_date"]:
        base = f"{cfg['prefix']}-{now.strftime('%Y%m')}"
    else:
        base = cfg["prefix"]

    suffix_str = f"-{cfg['suffix']}" if cfg["suffix"] else ""

    # Find last invoice matching this base pattern
    last = await db.invoices.find_one(
        {"invoice_number": {"$regex": f"^{base}-\\d+"}},
        sort=[("created_at", -1)],
        projection={"invoice_number": 1}
    )

    if last:
        try:
            # Extract the numeric part: base-NNNN or base-NNNN-suffix
            num_part = last["invoice_number"].replace(base + "-", "").replace(suffix_str, "")
            seq = int(num_part) + 1
        except (ValueError, IndexError):
            seq = cfg["start_number"]
    else:
        seq = cfg["start_number"]

    return f"{base}-{seq:04d}{suffix_str}"


def _serialize_invoice(doc: dict) -> dict:
    """Convert MongoDB invoice document to JSON-safe dict."""
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return {k: v for k, v in doc.items()}


@router.post("")
async def create_invoice(body: InvoiceCreate, user: dict = Depends(get_current_user)):
    """Create a new invoice (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = get_db()

    # Validate applicant exists
    applicant = await db.users.find_one({"_id": ObjectId(body.applicant_id)})
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    invoice_number = await _generate_invoice_number(db)
    now = datetime.now(timezone.utc).isoformat()

    # Build line items — prefer body.items, fallback to body.line_items
    items = body.items or body.line_items or [{"description": body.description or "Kursgebühr", "quantity": 1, "unit_price": body.amount or 0}]

    # Auto-calculate amount from line items if not explicitly provided
    calculated_amount = round(sum(
        float(item.get("quantity", 1)) * float(item.get("unit_price", 0))
        for item in items
    ), 2)
    final_amount = body.amount if body.amount is not None else calculated_amount

    # Default due_date: +30 days from now if not provided
    final_due_date = body.due_date
    if not final_due_date:
        final_due_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")

    invoice_doc = {
        "invoice_number": invoice_number,
        "applicant_id": body.applicant_id,
        "applicant_name": applicant.get("full_name", applicant.get("email", "")),
        "applicant_email": applicant.get("email", ""),
        "application_id": body.application_id,
        "description": body.description,
        "items": items,
        "amount": final_amount,
        "currency": body.currency,
        "status": "draft",
        "due_date": final_due_date,
        "created_by": user["id"],
        "created_by_name": user.get("full_name", user.get("email", "")),
        "created_at": now,
        "updated_at": now,
        "paid_at": None,
        "notes": "",
    }

    # Bewerbernummer und Bewerbersprache ermitteln
    app_query = {"applicant_id": body.applicant_id}
    if body.application_id:
        app_query["_id"] = ObjectId(body.application_id)
    application = await db.applications.find_one(app_query, {"applicant_number": 1, "degree_country": 1, "_id": 0})
    if application and application.get("applicant_number"):
        invoice_doc["applicant_number"] = application["applicant_number"]

    # Rechnungssprache: Default EN, DE nur fuer deutsche Bewerber
    applicant_country = (applicant.get("country") or "").lower()
    degree_country = (application.get("degree_country", "") if application else "").lower() if application else ""
    is_german = any(c in ("germany", "deutschland", "de", "deu") for c in [applicant_country, degree_country])
    if is_german:
        invoice_doc["applicant_language"] = "de"
    else:
        invoice_doc["applicant_language"] = applicant.get("language_pref", "en")

    result = await db.invoices.insert_one(invoice_doc)
    invoice_doc["id"] = str(result.inserted_id)

    # Audit log
    await write_audit_log(
        "invoice_created",
        user["id"],
        "invoice",
        invoice_doc["id"],
        {"invoice_number": invoice_number, "amount": final_amount, "applicant_id": body.applicant_id},
    )

    return _serialize_invoice(invoice_doc)


@router.get("/my")
async def list_my_invoices(user: dict = Depends(get_current_user)):
    """List invoices for the current applicant."""
    db = get_db()
    invoices = await db.invoices.find(
        {"applicant_id": user["id"]}
    ).sort("created_at", -1).to_list(100)
    result = []
    for inv in invoices:
        inv["id"] = str(inv.pop("_id"))
        result.append(inv)
    return result



@router.get("")
async def list_invoices(request: Request, user: dict = Depends(get_current_user)):
    """List invoices. Applicants see own, Staff see all."""
    db = get_db()
    query = {}

    if user["role"] == "applicant":
        query["applicant_id"] = user["id"]
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Optional filters
    status = request.query_params.get("status")
    if status:
        query["status"] = status

    applicant_id = request.query_params.get("applicant_id")
    if applicant_id and user["role"] in STAFF_ROLES:
        query["applicant_id"] = applicant_id

    cursor = db.invoices.find(query).sort("created_at", -1)
    invoices = await cursor.to_list(length=500)

    result = []
    for inv in invoices:
        inv["id"] = str(inv.pop("_id"))
        result.append(inv)

    return result


@router.get("/stats")
async def invoice_stats(user: dict = Depends(get_current_user)):
    """Get invoice statistics."""
    db = get_db()
    query = {}

    if user["role"] == "applicant":
        query["applicant_id"] = user["id"]
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$status",
            "count": {"$sum": 1},
            "total": {"$sum": "$amount"},
        }},
    ]
    results = await db.invoices.aggregate(pipeline).to_list(length=20)

    stats = {"total_count": 0, "total_amount": 0, "by_status": {}}
    for r in results:
        stats["by_status"][r["_id"]] = {"count": r["count"], "total": r["total"]}
        stats["total_count"] += r["count"]
        stats["total_amount"] += r["total"]

    return stats


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(invoice_id: str, user: dict = Depends(get_current_user)):
    """Generate and return D/A/CH-compliant invoice PDF.

    Rechtliche Pflichtangaben gemaess UStG / HGB:
    - Vollstaendiger Name und Anschrift des Rechnungsstellers
    - Rechtsform, Sitz, Registergericht, Handelsregisternummer
    - Geschaeftsfuehrung
    - Steuernummer oder USt-IdNr (offen markiert, falls nicht verifiziert)
    - Fortlaufende Rechnungsnummer
    - Rechnungsdatum
    - Leistungsbeschreibung
    - Entgelt und Steuerbetrag
    - Name und Anschrift des Leistungsempfaengers
    """
    db = get_db()
    inv = await db.invoices.find_one(
        {"$or": [{"invoice_number": invoice_id}, {"_id": ObjectId(invoice_id) if len(invoice_id) == 24 else None}]}
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        if str(inv.get("applicant_id")) != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

    # Load company settings from DB (fallback to verified defaults)
    company_settings = await db.settings.find_one({"type": "company_info"}) or {}

    # --- VERIFIZIERTE ANGABEN (Quelle: Impressum / HRB 23610 Amtsgericht Aachen) ---
    COMPANY_NAME = company_settings.get("company_name", "W2G Academy GmbH")
    COMPANY_STREET = company_settings.get("street", "Theaterstraße 24")
    COMPANY_CITY = company_settings.get("city", "52062 Aachen")
    COMPANY_COUNTRY = company_settings.get("country", "Deutschland")
    COMPANY_PHONE = company_settings.get("phone", "+49 (0) 241 990 322 92")
    COMPANY_EMAIL = company_settings.get("email", "info@stk-aachen.de")
    COMPANY_REGISTRY = company_settings.get("registry", "Amtsgericht Aachen, HRB 23610")
    COMPANY_MD = company_settings.get("managing_director", "Laura Saboor")
    # --- OFFENE ANGABEN (projektseitig vorgegeben) ---
    COMPANY_TAX_ID = company_settings.get("tax_id", "DE333306663")  # USt-IdNr. – projektseitig vorgegeben
    COMPANY_BANK_NAME = company_settings.get("bank_name", "")
    COMPANY_IBAN = company_settings.get("iban", "")
    COMPANY_BIC = company_settings.get("bic", "")

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    primary = HexColor("#113655")
    grey = HexColor("#64748B")
    dark = HexColor("#1E293B")
    light_grey = HexColor("#F1F5F9")
    white = HexColor("#FFFFFF")
    border_color = HexColor("#E2E8F0")

    # ─── Feste Layoutkonstanten (robust gegen Textlaengen) ────────
    ML = 20*mm           # Margin left
    MR = w - 20*mm       # Margin right (190mm)
    TABLE_LEFT = 18*mm   # Table container left edge
    TABLE_RIGHT = w - 18*mm  # Table container right edge

    # Tabellenspalten – feste Positionen (rechtsbuendig fuer Zahlen)
    COL_POS = ML                  # 20mm – Pos. Nummer
    COL_DESC = ML + 12*mm         # 32mm – Beschreibung (links)
    COL_QTY = 115*mm              # Menge (rechts)
    COL_UNIT = 150*mm             # Einzelpreis (rechts)
    COL_TOTAL = MR                # Betrag (rechts, 190mm)

    # Summenblock – Label rechts von Mitte, Wert ganz rechts
    SUM_LABEL_X = 150*mm          # Labels enden bei 150mm
    SUM_VALUE_X = MR              # Werte enden bei 190mm

    ROW_H = 5.5*mm               # Tabellen-Zeilenhoehe
    SECTION_GAP = 8*mm            # Abstand zwischen Sektionen

    def fmt_eur(val):
        """Format number as German EUR string."""
        s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s} EUR"

    def draw_text_wrapped(c, x, y, text, max_width, font="Helvetica", size=8.5):
        """Draw text, truncate with ... if too wide."""
        c.setFont(font, size)
        tw = c.stringWidth(text, font, size)
        if tw <= max_width:
            c.drawString(x, y, text)
            return
        while tw > max_width and len(text) > 3:
            text = text[:-1]
            tw = c.stringWidth(text + "...", font, size)
        c.drawString(x, y, text + "...")

    # ─── Sprache bestimmen (DE default, EN fuer nicht-deutsche Bewerber) ──
    applicant_lang = inv.get("applicant_language", "de")
    is_en = applicant_lang == "en"

    # i18n-Labels
    L = {
        "invoice": "INVOICE" if is_en else "RECHNUNG",
        "status_draft": "DRAFT" if is_en else "ENTWURF",
        "status_sent": "SENT" if is_en else "VERSENDET",
        "status_paid": "PAID" if is_en else "BEZAHLT",
        "status_overdue": "OVERDUE" if is_en else "UEBERFAELLIG",
        "status_cancelled": "CANCELLED" if is_en else "STORNIERT",
        "invoice_no": "Invoice No.:" if is_en else "Rechnungsnr.:",
        "invoice_date": "Invoice Date:" if is_en else "Rechnungsdatum:",
        "due_date": "Due Date:" if is_en else "Faelligkeitsdatum:",
        "payment_status": "Payment Status:" if is_en else "Zahlungsstatus:",
        "applicant_no": "Applicant No.:" if is_en else "Bewerbernr.:",
        "recipient": "INVOICE RECIPIENT" if is_en else "RECHNUNGSEMPFAENGER",
        "description_header": "SERVICE DESCRIPTION" if is_en else "LEISTUNGSBESCHREIBUNG",
        "pos": "Pos." if is_en else "Pos.",
        "desc": "Description" if is_en else "Beschreibung",
        "qty": "Qty" if is_en else "Menge",
        "unit_price": "Unit Price" if is_en else "Einzelpreis",
        "amount_col": "Amount" if is_en else "Betrag",
        "subtotal": "Subtotal" if is_en else "Zwischensumme",
        "total": "Total" if is_en else "Gesamtbetrag",
        "course_fee": "Course Fee" if is_en else "Kursgebuehr",
        "notes_header": "NOTES" if is_en else "HINWEISE",
        "payment_info": "PAYMENT INFORMATION" if is_en else "ZAHLUNGSINFORMATIONEN",
        "bank_transfer": "Bank Transfer:" if is_en else "Bankueberweisung:",
        "reference": "Payment Reference:" if is_en else "Verwendungszweck:",
        "thank_you": "Thank you for your trust." if is_en else "Vielen Dank fuer Ihr Vertrauen.",
        "footer": "This invoice was generated electronically." if is_en else "Diese Rechnung wurde maschinell erstellt.",
    }

    # ─── Header Bar ──────────────────────────────────────────────
    c.setFillColor(primary)
    c.rect(0, h - 32*mm, w, 32*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(ML, h - 18*mm, L["invoice"])
    c.setFont("Helvetica", 9)
    c.drawString(ML, h - 25*mm, inv.get("invoice_number", ""))
    # Status
    status_map = {"draft": L["status_draft"], "sent": L["status_sent"], "paid": L["status_paid"], "overdue": L["status_overdue"], "cancelled": L["status_cancelled"]}
    status_text = status_map.get(inv.get("status", ""), inv.get("status", "").upper())
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(MR, h - 18*mm, status_text)

    # ─── Rechnungssteller (links) ────────────────────────────────
    y = h - 42*mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(ML, y, COMPANY_NAME)
    c.setFont("Helvetica", 8)
    c.setFillColor(grey)
    company_lines = [
        f"{COMPANY_STREET}, {COMPANY_CITY}",
        f"Tel: {COMPANY_PHONE}",
        f"E-Mail: {COMPANY_EMAIL}",
        f"Registergericht: {COMPANY_REGISTRY}",
        f"Geschäftsführung: {COMPANY_MD}",
    ]
    if COMPANY_TAX_ID:
        company_lines.append(f"USt-IdNr.: {COMPANY_TAX_ID}")
    for line in company_lines:
        y -= 3.8*mm
        c.drawString(ML, y, line)

    # ─── Rechnungsdetails (rechts, feste Spalten) ─────────────────
    details_y = h - 42*mm
    invoice_date = inv.get("created_at", "")
    if isinstance(invoice_date, str) and "T" in invoice_date:
        try:
            dt = datetime.fromisoformat(invoice_date.replace("Z", "+00:00"))
            invoice_date = dt.strftime("%d.%m.%Y")
        except Exception:
            invoice_date = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    else:
        invoice_date = datetime.now(timezone.utc).strftime("%d.%m.%Y")

    due_date_raw = inv.get("due_date", "")
    due_date_display = due_date_raw
    if isinstance(due_date_raw, str) and "-" in due_date_raw:
        try:
            dt = datetime.fromisoformat(due_date_raw.replace("Z", "+00:00"))
            due_date_display = dt.strftime("%d.%m.%Y")
        except Exception:
            pass

    DETAIL_LABEL_X = w - 58*mm   # Labels enden hier (152mm)
    DETAIL_VALUE_X = MR           # Werte enden hier (190mm)

    detail_rows = [
        (L["invoice_no"], inv.get("invoice_number", "")),
        (L["invoice_date"], invoice_date),
        (L["due_date"], due_date_display),
        (L["payment_status"], status_text),
    ]
    # Bewerbernummer wenn vorhanden
    if inv.get("applicant_number"):
        detail_rows.append((L["applicant_no"], inv["applicant_number"]))
    for label, val in detail_rows:
        c.setFillColor(grey)
        c.setFont("Helvetica", 8)
        c.drawRightString(DETAIL_LABEL_X, details_y, label)
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(DETAIL_VALUE_X, details_y, str(val))
        details_y -= 4.2*mm

    # ─── Rechnungsempfaenger ──────────────────────────────────────
    y -= 10*mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(ML, y, L["recipient"])
    c.setFont("Helvetica", 8.5)
    c.setFillColor(dark)
    y -= 4.5*mm
    c.drawString(ML, y, inv.get("applicant_name", ""))
    y -= 3.8*mm
    c.setFillColor(grey)
    c.setFont("Helvetica", 8)
    c.drawString(ML, y, inv.get("applicant_email", ""))
    if inv.get("applicant_number"):
        y -= 3.8*mm
        c.drawString(ML, y, f"{L['applicant_no']} {inv['applicant_number']}")

    # ─── Leistungsbeschreibung ────────────────────────────────────
    y -= SECTION_GAP + 2*mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(ML, y, L["description_header"])
    c.setFont("Helvetica", 8.5)
    c.setFillColor(dark)
    y -= 4.5*mm
    description = inv.get("description", L["course_fee"])
    draw_text_wrapped(c, ML, y, description, 140*mm)

    # ─── Positionstabelle ─────────────────────────────────────────
    y -= SECTION_GAP + 2*mm

    # Table header background
    header_h = 7*mm
    c.setFillColor(primary)
    c.rect(TABLE_LEFT, y - 1.5*mm, TABLE_RIGHT - TABLE_LEFT, header_h, fill=1, stroke=0)

    # Table header text
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(COL_POS, y + 0.5*mm, L["pos"])
    c.drawString(COL_DESC, y + 0.5*mm, L["desc"])
    c.drawRightString(COL_QTY, y + 0.5*mm, L["qty"])
    c.drawRightString(COL_UNIT, y + 0.5*mm, L["unit_price"])
    c.drawRightString(COL_TOTAL, y + 0.5*mm, L["amount_col"])

    # Items
    items = inv.get("items") or [{"description": description, "quantity": 1, "unit_price": inv.get("amount", 0)}]
    subtotal = 0
    desc_max_width = COL_QTY - COL_DESC - 8*mm  # Max width for description text

    for idx, item in enumerate(items, 1):
        y -= ROW_H + 2.5*mm
        qty = item.get("quantity", 1)
        unit_price = item.get("unit_price", 0)
        line_total = qty * unit_price
        subtotal += line_total

        # Alternating row bg
        if idx % 2 == 0:
            c.setFillColor(HexColor("#F8FAFC"))
            c.rect(TABLE_LEFT, y - 1.5*mm, TABLE_RIGHT - TABLE_LEFT, ROW_H + 2*mm, fill=1, stroke=0)

        c.setFillColor(dark)
        c.setFont("Helvetica", 8)
        c.drawString(COL_POS, y, str(idx))
        draw_text_wrapped(c, COL_DESC, y, item.get("description", ""), desc_max_width)
        c.drawRightString(COL_QTY, y, str(qty))

        c.setFont("Helvetica", 8)
        c.drawRightString(COL_UNIT, y, fmt_eur(unit_price))

        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(COL_TOTAL, y, fmt_eur(line_total))

    # ─── Tabellen-Trennlinie ──────────────────────────────────────
    y -= 4*mm
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.line(TABLE_LEFT, y, TABLE_RIGHT, y)

    # ─── Summenblock (rechtsbuendig, klar getrennt) ───────────────
    amount = inv.get("amount", subtotal)

    y -= 6*mm
    c.setFont("Helvetica", 8)
    c.setFillColor(grey)
    c.drawRightString(SUM_LABEL_X, y, f"{L['subtotal']}:")
    c.setFillColor(dark)
    c.setFont("Helvetica", 8)
    c.drawRightString(SUM_VALUE_X, y, fmt_eur(amount))

    y -= 6*mm
    c.setFillColor(grey)
    c.setFont("Helvetica-Oblique", 6.5)
    c.drawRightString(SUM_VALUE_X, y, "Ggf. umsatzsteuerbefreit gem. § 4 Nr. 21 UStG")

    # Gesamtbetrag – hervorgehoben mit Box
    y -= 10*mm
    total_box_h = 10*mm
    c.setFillColor(light_grey)
    c.rect(100*mm, y - 2*mm, MR - 100*mm + 2*mm, total_box_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(primary)
    c.drawRightString(SUM_LABEL_X, y + 1.5*mm, f"{L['total']}:")
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(SUM_VALUE_X, y + 1.5*mm, fmt_eur(amount))

    # ─── Bankverbindung (wenn konfiguriert) ───────────────────────
    if COMPANY_IBAN:
        y -= 12*mm
        bank_box_h = 16*mm
        c.setFillColor(light_grey)
        c.rect(TABLE_LEFT, y - 3*mm, TABLE_RIGHT - TABLE_LEFT, bank_box_h, fill=1, stroke=0)
        c.setFillColor(primary)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(ML, y + 7*mm, L["payment_info"])
        c.setFont("Helvetica", 7.5)
        c.setFillColor(dark)
        bank_lines = []
        if COMPANY_BANK_NAME:
            bank_lines.append(f"Bank: {COMPANY_BANK_NAME}")
        bank_lines.append(f"IBAN: {COMPANY_IBAN}")
        if COMPANY_BIC:
            bank_lines.append(f"BIC: {COMPANY_BIC}")
        bank_lines.append(f"Kontoinhaber: {COMPANY_NAME}")
        by = y + 3.5*mm
        for bl in bank_lines:
            c.drawString(ML, by, bl)
            by -= 3.2*mm

    # ─── Hilfehinweis ─────────────────────────────────────────────
    y -= 16*mm if not COMPANY_IBAN else 6*mm
    c.setFillColor(grey)
    c.setFont("Helvetica", 7)
    c.drawString(ML, y, L["thank_you"] if not is_en else "Next steps after payment: We will check the payment receipt and inform you via the portal.")
    y -= 3.5*mm
    c.drawString(ML, y, f"{'Questions' if is_en else 'Bei Fragen'}: {COMPANY_EMAIL} {'or' if is_en else 'oder'} Tel. {COMPANY_PHONE}")

    # ─── Rechtlicher Footer ───────────────────────────────────────
    footer_y = 18*mm
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.line(TABLE_LEFT, footer_y + 5*mm, TABLE_RIGHT, footer_y + 5*mm)

    c.setFillColor(grey)
    c.setFont("Helvetica", 6)
    footer_line1 = f"{COMPANY_NAME}  |  {COMPANY_STREET}  |  {COMPANY_CITY}  |  {COMPANY_COUNTRY}"
    footer_line2 = f"Registergericht: {COMPANY_REGISTRY}  |  Geschäftsführung: {COMPANY_MD}"
    footer_line3 = f"E-Mail: {COMPANY_EMAIL}  |  Tel: {COMPANY_PHONE}"
    if COMPANY_TAX_ID:
        footer_line2 += f"  |  USt-IdNr.: {COMPANY_TAX_ID}"

    c.drawCentredString(w/2, footer_y, footer_line1)
    c.drawCentredString(w/2, footer_y - 3*mm, footer_line2)
    c.drawCentredString(w/2, footer_y - 6*mm, footer_line3)

    c.save()
    buf.seek(0)

    filename = f"{inv.get('invoice_number', 'rechnung')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/{invoice_id}/send")
async def send_invoice_email(invoice_id: str, user: dict = Depends(get_current_user)):
    """Send invoice PDF via email to the applicant.

    - Generates PDF
    - Sends via Resend with PDF attachment
    - Updates status to 'sent' if currently 'draft'
    """
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = get_db()
    inv = await db.invoices.find_one(
        {"$or": [{"invoice_number": invoice_id}, {"_id": ObjectId(invoice_id) if len(invoice_id) == 24 else None}]}
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    applicant_email = inv.get("applicant_email")
    if not applicant_email:
        raise HTTPException(status_code=400, detail="Keine E-Mail-Adresse fuer den Bewerber hinterlegt")

    # Generate PDF in memory using the same logic as download
    pdf_response = await download_invoice_pdf(invoice_id, user)
    pdf_bytes = b""
    async for chunk in pdf_response.body_iterator:
        pdf_bytes += chunk if isinstance(chunk, bytes) else chunk.encode()

    # Send via Resend
    import os
    import base64
    try:
        from config import EMAIL_ENABLED, RESEND_API_KEY, EMAIL_FROM, REPLY_TO
    except ImportError:
        raise HTTPException(status_code=500, detail="E-Mail-Konfiguration fehlt")

    if not EMAIL_ENABLED:
        raise HTTPException(status_code=400, detail="E-Mail-Versand ist deaktiviert")

    try:
        import resend
        resend.api_key = RESEND_API_KEY

        invoice_number = inv.get("invoice_number", "Rechnung")
        applicant_name = inv.get("applicant_name", "")
        amount = inv.get("amount", 0)

        amount_str = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"

        html = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #113655; padding: 24px 32px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; font-size: 20px; margin: 0;">Rechnung {invoice_number}</h1>
            </div>
            <div style="padding: 32px; border: 1px solid #E2E8F0; border-top: none; border-radius: 0 0 8px 8px;">
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                    Guten Tag{(' ' + applicant_name) if applicant_name else ''},
                </p>
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                    anbei erhalten Sie Ihre Rechnung <strong>{invoice_number}</strong>
                    ueber <strong>{amount_str}</strong>.
                </p>
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                    Die Rechnung finden Sie als PDF im Anhang dieser E-Mail.
                    Bei Fragen wenden Sie sich bitte an <a href="mailto:info@stk-aachen.de" style="color: #113655;">info@stk-aachen.de</a>.
                </p>
                <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 24px 0;" />
                <p style="color: #94A3B8; font-size: 11px;">
                    W2G Academy GmbH | Theaterstr. 24 | 52062 Aachen<br/>
                    Amtsgericht Aachen HRB 23610 | Geschaeftsfuehrung: Laura Saboor<br/>
                    USt-IdNr.: DE333306663
                </p>
            </div>
        </div>
        """

        resend.Emails.send({
            "from": f"Studienkolleg Aachen <{EMAIL_FROM}>",
            "to": [applicant_email],
            "reply_to": REPLY_TO,
            "subject": f"Rechnung {invoice_number} - Studienkolleg Aachen",
            "html": html,
            "attachments": [{
                "filename": f"{invoice_number}.pdf",
                "content": base64.b64encode(pdf_bytes).decode("utf-8"),
                "content_type": "application/pdf",
            }],
        })

        import logging
        logging.getLogger(__name__).info(f"[EMAIL] Invoice {invoice_number} sent to {applicant_email}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"E-Mail-Versand fehlgeschlagen: {str(e)}")

    # Update status to 'sent' if currently draft
    filter_q = {"invoice_number": inv.get("invoice_number")}
    now = datetime.now(timezone.utc).isoformat()
    update_fields = {"updated_at": now, "sent_at": now}
    if inv.get("status") == "draft":
        update_fields["status"] = "sent"
    await db.invoices.update_one(filter_q, {"$set": update_fields})

    # Audit
    await write_audit_log(
        "invoice_sent",
        user["id"],
        "invoice",
        str(inv.get("_id", "")),
        {"invoice_number": inv.get("invoice_number"), "sent_to": applicant_email},
    )

    return {"ok": True, "sent_to": applicant_email, "status": update_fields.get("status", inv.get("status"))}


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str, user: dict = Depends(get_current_user)):
    """Get single invoice by ID or invoice_number."""
    db = get_db()

    # Try by invoice_number first, then by ObjectId
    invoice = await db.invoices.find_one({"invoice_number": invoice_id}, {"_id": 0})
    if not invoice:
        try:
            invoice = await db.invoices.find_one({"_id": ObjectId(invoice_id)})
            if invoice:
                invoice["id"] = str(invoice.pop("_id"))
        except Exception:
            pass

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Access control
    if user["role"] == "applicant" and invoice.get("applicant_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES and user["role"] != "applicant":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    if "id" not in invoice:
        invoice["id"] = invoice.get("invoice_number", "")

    return invoice


@router.patch("/{invoice_id}")
async def update_invoice(invoice_id: str, body: InvoiceUpdate, user: dict = Depends(get_current_user)):
    """Update invoice (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = get_db()

    # Find by invoice_number or ObjectId
    filter_q = {"invoice_number": invoice_id}
    existing = await db.invoices.find_one(filter_q)
    if not existing:
        try:
            filter_q = {"_id": ObjectId(invoice_id)}
            existing = await db.invoices.find_one(filter_q)
        except Exception:
            pass

    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")

    updates = {k: v for k, v in body.dict(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    # If items provided, recalculate amount from line items
    if "items" in updates and updates["items"]:
        total = sum(
            float(item.get("quantity", 1)) * float(item.get("unit_price", 0))
            for item in updates["items"]
        )
        updates["amount"] = round(total, 2)

    # If marking as paid, set paid_at
    if updates.get("status") == "paid" and not updates.get("paid_at"):
        updates["paid_at"] = datetime.now(timezone.utc).isoformat()

    await db.invoices.update_one(filter_q, {"$set": updates})

    # Audit
    inv_id = str(existing["_id"])
    await write_audit_log(
        "invoice_updated",
        user["id"],
        "invoice",
        inv_id,
        {"invoice_number": existing.get("invoice_number"), "changes": updates},
    )

    updated = await db.invoices.find_one(filter_q, {"_id": 0})
    if updated and "id" not in updated:
        updated["id"] = updated.get("invoice_number", inv_id)
    return updated


@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str, user: dict = Depends(get_current_user)):
    """Delete invoice (Admin only, only drafts)."""
    if user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")

    db = get_db()

    filter_q = {"invoice_number": invoice_id}
    existing = await db.invoices.find_one(filter_q)
    if not existing:
        try:
            filter_q = {"_id": ObjectId(invoice_id)}
            existing = await db.invoices.find_one(filter_q)
        except Exception:
            pass

    if not existing:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if existing.get("status") not in ("draft", None):
        raise HTTPException(status_code=400, detail="Only draft invoices can be deleted")

    await db.invoices.delete_one(filter_q)

    await write_audit_log(
        "invoice_deleted",
        user["id"],
        "invoice",
        str(existing["_id"]),
        {"invoice_number": existing.get("invoice_number")},
    )

    return {"ok": True}
