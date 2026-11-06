"""
Quote router – Angebote (Quotes) CRUD.

- Staff/Admin: create, list all, update status, view detail, send, PDF
- Applicant: list own quotes, view detail
- Quote numbers are auto-generated (QUO-YYYYMM-NNNN)
- Statuses: draft, sent, accepted, rejected, expired
"""
from datetime import datetime, timezone, timedelta
from io import BytesIO
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
from services.audit import write_audit_log

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

QUOTE_STATUSES = ("draft", "sent", "accepted", "rejected", "expired")


async def _generate_quote_number(db) -> str:
    """Generate sequential quote number QUO-YYYYMM-NNNN."""
    now = datetime.now(timezone.utc)
    base = f"QUO-{now.strftime('%Y%m')}"
    last = await db.quotes.find_one(
        {"quote_number": {"$regex": f"^{base}-\\d+"}},
        sort=[("created_at", -1)],
        projection={"quote_number": 1},
    )
    if last:
        try:
            seq = int(last["quote_number"].replace(base + "-", "")) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f"{base}-{seq:04d}"


def _serialize(doc: dict) -> dict:
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


async def _find_quote(db, quote_id: str):
    quote = await db.quotes.find_one({"quote_number": quote_id})
    if not quote and len(quote_id) == 24:
        try:
            quote = await db.quotes.find_one({"_id": ObjectId(quote_id)})
        except Exception:
            pass
    return quote


@router.post("")
async def create_quote(request: Request, user: dict = Depends(get_current_user)):
    """Create a new quote (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    body = await request.json()
    applicant_id = body.get("applicant_id")
    if not applicant_id:
        raise HTTPException(status_code=400, detail="applicant_id ist erforderlich")

    db = get_db()
    try:
        applicant = await db.users.find_one({"_id": ObjectId(applicant_id)})
    except Exception:
        applicant = None
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    items = body.get("items") or []
    if not items:
        raise HTTPException(status_code=400, detail="Mindestens eine Position ist erforderlich")

    calculated_amount = round(sum(
        float(i.get("quantity", 1)) * float(i.get("unit_price", 0)) for i in items
    ), 2)

    valid_until = body.get("valid_until")
    if not valid_until:
        valid_until = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")

    quote_number = await _generate_quote_number(db)
    now = datetime.now(timezone.utc).isoformat()

    doc = {
        "quote_number": quote_number,
        "applicant_id": applicant_id,
        "applicant_name": applicant.get("full_name", applicant.get("email", "")),
        "applicant_email": applicant.get("email", ""),
        "application_id": body.get("application_id"),
        "description": body.get("description", ""),
        "items": [{
            "description": i.get("description", ""),
            "quantity": float(i.get("quantity", 1)),
            "unit_price": float(i.get("unit_price", 0)),
        } for i in items],
        "amount": calculated_amount,
        "currency": body.get("currency", "EUR"),
        "status": "draft",
        "valid_until": valid_until,
        "notes": body.get("notes", ""),
        "created_by": user["id"],
        "created_by_name": user.get("full_name", user.get("email", "")),
        "created_at": now,
        "updated_at": now,
    }

    # Bewerbernummer und Sprache ermitteln (analog zu Rechnungen)
    application = await db.applications.find_one(
        {"applicant_id": applicant_id}, {"applicant_number": 1, "degree_country": 1, "_id": 0}
    )
    if application and application.get("applicant_number"):
        doc["applicant_number"] = application["applicant_number"]

    applicant_country = (applicant.get("country") or "").lower()
    degree_country = (application.get("degree_country", "") if application else "").lower()
    is_german = any(c in ("germany", "deutschland", "de", "deu") for c in [applicant_country, degree_country])
    doc["applicant_language"] = "de" if is_german else applicant.get("language_pref", "en")

    result = await db.quotes.insert_one(doc)
    doc["id"] = str(result.inserted_id)

    await write_audit_log(
        "quote_created", user["id"], "quote", doc["id"],
        {"quote_number": quote_number, "amount": calculated_amount, "applicant_id": applicant_id},
    )
    return _serialize(doc)


@router.get("")
async def list_quotes(request: Request, user: dict = Depends(get_current_user)):
    """List quotes. Applicants see own, Staff/Admin see all."""
    db = get_db()
    query = {}
    if user["role"] == "applicant":
        query["applicant_id"] = user["id"]
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    status = request.query_params.get("status")
    if status:
        query["status"] = status
    applicant_id = request.query_params.get("applicant_id")
    if applicant_id and (user["role"] in STAFF_ROLES or user["role"] in ADMIN_ROLES):
        query["applicant_id"] = applicant_id

    quotes = await db.quotes.find(query).sort("created_at", -1).to_list(500)
    return [_serialize(q) for q in quotes]


@router.get("/stats")
async def quote_stats(user: dict = Depends(get_current_user)):
    """Quote statistics grouped by status."""
    db = get_db()
    query = {}
    if user["role"] == "applicant":
        query["applicant_id"] = user["id"]
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    pipeline = [
        {"$match": query},
        {"$group": {"_id": "$status", "count": {"$sum": 1}, "total": {"$sum": "$amount"}}},
    ]
    results = await db.quotes.aggregate(pipeline).to_list(length=20)
    stats = {"total_count": 0, "total_amount": 0, "by_status": {}}
    for r in results:
        stats["by_status"][r["_id"]] = {"count": r["count"], "total": r["total"]}
        stats["total_count"] += r["count"]
        stats["total_amount"] += r["total"]
    return stats


@router.get("/{quote_id}/pdf")
async def download_quote_pdf(quote_id: str, user: dict = Depends(get_current_user)):
    """Generate and return quote PDF (Angebot)."""
    db = get_db()
    q = await _find_quote(db, quote_id)
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")

    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        if str(q.get("applicant_id")) != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

    company_settings = await db.settings.find_one({"type": "company_info"}) or {}
    COMPANY_NAME = company_settings.get("company_name", "W2G Academy GmbH")
    COMPANY_STREET = company_settings.get("street", "Theaterstraße 24")
    COMPANY_CITY = company_settings.get("city", "52062 Aachen")
    COMPANY_COUNTRY = company_settings.get("country", "Deutschland")
    COMPANY_PHONE = company_settings.get("phone", "+49 (0) 241 990 322 92")
    COMPANY_EMAIL = company_settings.get("email", "info@stk-aachen.de")
    COMPANY_REGISTRY = company_settings.get("registry", "Amtsgericht Aachen, HRB 23610")
    COMPANY_MD = company_settings.get("managing_director", "Laura Saboor")
    COMPANY_TAX_ID = company_settings.get("tax_id", "DE333306663")

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

    ML = 20*mm
    MR = w - 20*mm
    TABLE_LEFT = 18*mm
    TABLE_RIGHT = w - 18*mm
    COL_POS = ML
    COL_DESC = ML + 12*mm
    COL_QTY = 115*mm
    COL_UNIT = 150*mm
    COL_TOTAL = MR
    SUM_LABEL_X = 150*mm
    SUM_VALUE_X = MR
    ROW_H = 5.5*mm
    SECTION_GAP = 8*mm

    def fmt_eur(val):
        s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s} EUR"

    def draw_text_wrapped(c, x, y, text, max_width, font="Helvetica", size=8.5):
        c.setFont(font, size)
        tw = c.stringWidth(text, font, size)
        if tw <= max_width:
            c.drawString(x, y, text)
            return
        while tw > max_width and len(text) > 3:
            text = text[:-1]
            tw = c.stringWidth(text + "...", font, size)
        c.drawString(x, y, text + "...")

    is_en = q.get("applicant_language", "de") == "en"
    L = {
        "quote": "QUOTATION" if is_en else "ANGEBOT",
        "status_draft": "DRAFT" if is_en else "ENTWURF",
        "status_sent": "SENT" if is_en else "VERSENDET",
        "status_accepted": "ACCEPTED" if is_en else "ANGENOMMEN",
        "status_rejected": "REJECTED" if is_en else "ABGELEHNT",
        "status_expired": "EXPIRED" if is_en else "ABGELAUFEN",
        "quote_no": "Quote No.:" if is_en else "Angebotsnr.:",
        "quote_date": "Quote Date:" if is_en else "Angebotsdatum:",
        "valid_until": "Valid Until:" if is_en else "Gueltig bis:",
        "status_label": "Status:" if is_en else "Status:",
        "applicant_no": "Applicant No.:" if is_en else "Bewerbernr.:",
        "recipient": "QUOTE RECIPIENT" if is_en else "ANGEBOTSEMPFAENGER",
        "description_header": "SERVICE DESCRIPTION" if is_en else "LEISTUNGSBESCHREIBUNG",
        "pos": "Pos.",
        "desc": "Description" if is_en else "Beschreibung",
        "qty": "Qty" if is_en else "Menge",
        "unit_price": "Unit Price" if is_en else "Einzelpreis",
        "amount_col": "Amount" if is_en else "Betrag",
        "subtotal": "Subtotal" if is_en else "Zwischensumme",
        "total": "Total" if is_en else "Gesamtbetrag",
        "validity_note": "This quotation is valid until" if is_en else "Dieses Angebot ist gueltig bis",
        "no_invoice_note": "This is a non-binding quotation, not an invoice." if is_en else "Dies ist ein unverbindliches Angebot, keine Rechnung.",
        "thank_you": "We look forward to your acceptance." if is_en else "Wir freuen uns auf Ihre Auftragserteilung.",
    }

    # Header Bar
    c.setFillColor(primary)
    c.rect(0, h - 32*mm, w, 32*mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(ML, h - 18*mm, L["quote"])
    c.setFont("Helvetica", 9)
    c.drawString(ML, h - 25*mm, q.get("quote_number", ""))
    status_map = {
        "draft": L["status_draft"], "sent": L["status_sent"], "accepted": L["status_accepted"],
        "rejected": L["status_rejected"], "expired": L["status_expired"],
    }
    status_text = status_map.get(q.get("status", ""), q.get("status", "").upper())
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(MR, h - 18*mm, status_text)

    # Absender links
    y = h - 42*mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawString(ML, y, COMPANY_NAME)
    c.setFont("Helvetica", 8)
    c.setFillColor(grey)
    for line in [
        f"{COMPANY_STREET}, {COMPANY_CITY}",
        f"Tel: {COMPANY_PHONE}",
        f"E-Mail: {COMPANY_EMAIL}",
        f"Registergericht: {COMPANY_REGISTRY}",
        f"Geschäftsführung: {COMPANY_MD}",
        f"USt-IdNr.: {COMPANY_TAX_ID}",
    ]:
        y -= 3.8*mm
        c.drawString(ML, y, line)

    # Details rechts
    details_y = h - 42*mm
    quote_date = q.get("created_at", "")
    if isinstance(quote_date, str) and "T" in quote_date:
        try:
            quote_date = datetime.fromisoformat(quote_date.replace("Z", "+00:00")).strftime("%d.%m.%Y")
        except Exception:
            quote_date = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    else:
        quote_date = datetime.now(timezone.utc).strftime("%d.%m.%Y")

    valid_raw = q.get("valid_until", "")
    valid_display = valid_raw
    if isinstance(valid_raw, str) and "-" in valid_raw:
        try:
            valid_display = datetime.fromisoformat(valid_raw.replace("Z", "+00:00")).strftime("%d.%m.%Y")
        except Exception:
            pass

    DETAIL_LABEL_X = w - 58*mm
    DETAIL_VALUE_X = MR
    detail_rows = [
        (L["quote_no"], q.get("quote_number", "")),
        (L["quote_date"], quote_date),
        (L["valid_until"], valid_display),
        (L["status_label"], status_text),
    ]
    if q.get("applicant_number"):
        detail_rows.append((L["applicant_no"], q["applicant_number"]))
    for label, val in detail_rows:
        c.setFillColor(grey)
        c.setFont("Helvetica", 8)
        c.drawRightString(DETAIL_LABEL_X, details_y, label)
        c.setFillColor(dark)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(DETAIL_VALUE_X, details_y, str(val))
        details_y -= 4.2*mm

    # Empfaenger
    y -= 10*mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(ML, y, L["recipient"])
    c.setFont("Helvetica", 8.5)
    c.setFillColor(dark)
    y -= 4.5*mm
    c.drawString(ML, y, q.get("applicant_name", ""))
    y -= 3.8*mm
    c.setFillColor(grey)
    c.setFont("Helvetica", 8)
    c.drawString(ML, y, q.get("applicant_email", ""))
    if q.get("applicant_number"):
        y -= 3.8*mm
        c.drawString(ML, y, f"{L['applicant_no']} {q['applicant_number']}")

    # Leistungsbeschreibung
    y -= SECTION_GAP + 2*mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(ML, y, L["description_header"])
    c.setFont("Helvetica", 8.5)
    c.setFillColor(dark)
    y -= 4.5*mm
    description = q.get("description") or ", ".join(i.get("description", "") for i in q.get("items", []))
    draw_text_wrapped(c, ML, y, description, 140*mm)

    # Positionstabelle
    y -= SECTION_GAP + 2*mm
    header_h = 7*mm
    c.setFillColor(primary)
    c.rect(TABLE_LEFT, y - 1.5*mm, TABLE_RIGHT - TABLE_LEFT, header_h, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(COL_POS, y + 0.5*mm, L["pos"])
    c.drawString(COL_DESC, y + 0.5*mm, L["desc"])
    c.drawRightString(COL_QTY, y + 0.5*mm, L["qty"])
    c.drawRightString(COL_UNIT, y + 0.5*mm, L["unit_price"])
    c.drawRightString(COL_TOTAL, y + 0.5*mm, L["amount_col"])

    items = q.get("items") or []
    subtotal = 0
    desc_max_width = COL_QTY - COL_DESC - 8*mm
    for idx, item in enumerate(items, 1):
        y -= ROW_H + 2.5*mm
        qty = item.get("quantity", 1)
        unit_price = item.get("unit_price", 0)
        line_total = qty * unit_price
        subtotal += line_total
        if idx % 2 == 0:
            c.setFillColor(HexColor("#F8FAFC"))
            c.rect(TABLE_LEFT, y - 1.5*mm, TABLE_RIGHT - TABLE_LEFT, ROW_H + 2*mm, fill=1, stroke=0)
        c.setFillColor(dark)
        c.setFont("Helvetica", 8)
        c.drawString(COL_POS, y, str(idx))
        draw_text_wrapped(c, COL_DESC, y, item.get("description", ""), desc_max_width)
        c.drawRightString(COL_QTY, y, str(int(qty) if qty == int(qty) else qty))
        c.drawRightString(COL_UNIT, y, fmt_eur(unit_price))
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(COL_TOTAL, y, fmt_eur(line_total))

    y -= 4*mm
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.line(TABLE_LEFT, y, TABLE_RIGHT, y)

    amount = q.get("amount", subtotal)
    y -= 6*mm
    c.setFont("Helvetica", 8)
    c.setFillColor(grey)
    c.drawRightString(SUM_LABEL_X, y, f"{L['subtotal']}:")
    c.setFillColor(dark)
    c.drawRightString(SUM_VALUE_X, y, fmt_eur(amount))

    y -= 6*mm
    c.setFillColor(grey)
    c.setFont("Helvetica-Oblique", 6.5)
    c.drawRightString(SUM_VALUE_X, y, "Ggf. umsatzsteuerbefreit gem. § 4 Nr. 21 UStG")

    y -= 10*mm
    total_box_h = 10*mm
    c.setFillColor(light_grey)
    c.rect(100*mm, y - 2*mm, MR - 100*mm + 2*mm, total_box_h, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(primary)
    c.drawRightString(SUM_LABEL_X, y + 1.5*mm, f"{L['total']}:")
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(SUM_VALUE_X, y + 1.5*mm, fmt_eur(amount))

    # Gueltigkeitshinweis
    y -= 14*mm
    c.setFillColor(grey)
    c.setFont("Helvetica", 7.5)
    c.drawString(ML, y, f"{L['validity_note']}: {valid_display}")
    y -= 4*mm
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(ML, y, L["no_invoice_note"])
    y -= 4*mm
    c.setFont("Helvetica", 7)
    c.drawString(ML, y, L["thank_you"])

    # Footer
    footer_y = 18*mm
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.line(TABLE_LEFT, footer_y + 5*mm, TABLE_RIGHT, footer_y + 5*mm)
    c.setFillColor(grey)
    c.setFont("Helvetica", 6)
    c.drawCentredString(w/2, footer_y, f"{COMPANY_NAME}  |  {COMPANY_STREET}  |  {COMPANY_CITY}  |  {COMPANY_COUNTRY}")
    c.drawCentredString(w/2, footer_y - 3*mm, f"Registergericht: {COMPANY_REGISTRY}  |  Geschäftsführung: {COMPANY_MD}  |  USt-IdNr.: {COMPANY_TAX_ID}")
    c.drawCentredString(w/2, footer_y - 6*mm, f"E-Mail: {COMPANY_EMAIL}  |  Tel: {COMPANY_PHONE}")

    c.save()
    buf.seek(0)
    filename = f"{q.get('quote_number', 'angebot')}.pdf"
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/{quote_id}/send")
async def send_quote_email(quote_id: str, user: dict = Depends(get_current_user)):
    """Send quote PDF via email to the applicant. Status draft -> sent."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    db = get_db()
    q = await _find_quote(db, quote_id)
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")

    applicant_email = q.get("applicant_email")
    if not applicant_email:
        raise HTTPException(status_code=400, detail="Keine E-Mail-Adresse fuer den Bewerber hinterlegt")

    pdf_response = await download_quote_pdf(quote_id, user)
    pdf_bytes = b""
    async for chunk in pdf_response.body_iterator:
        pdf_bytes += chunk if isinstance(chunk, bytes) else chunk.encode()

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

        quote_number = q.get("quote_number", "Angebot")
        applicant_name = q.get("applicant_name", "")
        amount = q.get("amount", 0)
        amount_str = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"
        valid_until = q.get("valid_until", "")

        html = f"""
        <div style="font-family: 'Inter', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #113655; padding: 24px 32px; border-radius: 8px 8px 0 0;">
                <h1 style="color: white; font-size: 20px; margin: 0;">Angebot {quote_number}</h1>
            </div>
            <div style="padding: 32px; border: 1px solid #E2E8F0; border-top: none; border-radius: 0 0 8px 8px;">
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                    Guten Tag{(' ' + applicant_name) if applicant_name else ''},
                </p>
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                    anbei erhalten Sie unser Angebot <strong>{quote_number}</strong>
                    ueber <strong>{amount_str}</strong>.
                    {f'Das Angebot ist gueltig bis <strong>{valid_until}</strong>.' if valid_until else ''}
                </p>
                <p style="color: #334155; font-size: 14px; line-height: 1.6;">
                    Das Angebot finden Sie als PDF im Anhang dieser E-Mail.
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
            "subject": f"Angebot {quote_number} - Studienkolleg Aachen",
            "html": html,
            "attachments": [{
                "filename": f"{quote_number}.pdf",
                "content": base64.b64encode(pdf_bytes).decode("utf-8"),
                "content_type": "application/pdf",
            }],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"E-Mail-Versand fehlgeschlagen: {str(e)}")

    now = datetime.now(timezone.utc).isoformat()
    update_fields = {"updated_at": now, "sent_at": now}
    if q.get("status") == "draft":
        update_fields["status"] = "sent"
    await db.quotes.update_one({"quote_number": q["quote_number"]}, {"$set": update_fields})

    await write_audit_log(
        "quote_sent", user["id"], "quote", str(q.get("_id", "")),
        {"quote_number": q.get("quote_number"), "sent_to": applicant_email},
    )
    return {"ok": True, "sent_to": applicant_email, "status": update_fields.get("status", q.get("status"))}


@router.get("/{quote_id}")
async def get_quote(quote_id: str, user: dict = Depends(get_current_user)):
    """Get single quote by ID or quote_number."""
    db = get_db()
    q = await _find_quote(db, quote_id)
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")

    if user["role"] == "applicant" and str(q.get("applicant_id")) != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES and user["role"] != "applicant":
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    return _serialize(q)


@router.patch("/{quote_id}")
async def update_quote(quote_id: str, request: Request, user: dict = Depends(get_current_user)):
    """Update quote (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    body = await request.json()
    db = get_db()
    existing = await _find_quote(db, quote_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Quote not found")

    allowed = {"description", "items", "valid_until", "notes", "status"}
    updates = {k: v for k, v in body.items() if k in allowed and v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "status" in updates and updates["status"] not in QUOTE_STATUSES:
        raise HTTPException(status_code=400, detail=f"Ungueltiger Status. Erlaubt: {', '.join(QUOTE_STATUSES)}")

    if "items" in updates and updates["items"]:
        updates["items"] = [{
            "description": i.get("description", ""),
            "quantity": float(i.get("quantity", 1)),
            "unit_price": float(i.get("unit_price", 0)),
        } for i in updates["items"]]
        updates["amount"] = round(sum(
            i["quantity"] * i["unit_price"] for i in updates["items"]
        ), 2)

    if updates.get("status") == "accepted":
        updates["accepted_at"] = datetime.now(timezone.utc).isoformat()

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.quotes.update_one({"_id": existing["_id"]}, {"$set": updates})

    await write_audit_log(
        "quote_updated", user["id"], "quote", str(existing["_id"]),
        {"quote_number": existing.get("quote_number"), "changes": {k: v for k, v in updates.items() if k != "items"}},
    )

    updated = await db.quotes.find_one({"_id": existing["_id"]})
    return _serialize(updated)


@router.delete("/{quote_id}")
async def delete_quote(quote_id: str, user: dict = Depends(get_current_user)):
    """Delete quote (Admin only, only drafts)."""
    if user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")

    db = get_db()
    existing = await _find_quote(db, quote_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Quote not found")

    if existing.get("status") not in ("draft", None):
        raise HTTPException(status_code=400, detail="Only draft quotes can be deleted")

    await db.quotes.delete_one({"_id": existing["_id"]})
    await write_audit_log(
        "quote_deleted", user["id"], "quote", str(existing["_id"]),
        {"quote_number": existing.get("quote_number")},
    )
    return {"ok": True}
