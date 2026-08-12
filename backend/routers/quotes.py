"""
Quote router – CRUD fuer Angebote (Quotes).

- Staff/Admin: create, list all, update status, view detail, PDF, send
- Applicant: list own quotes, view detail
- Quote numbers are auto-generated (QUO-YYYYMM-NNNN)
- Positionen stammen aus dem Tarifkatalog (/api/products) – Tarif-Dropdown
"""
from datetime import datetime, timezone, timedelta
from io import BytesIO
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
from models.schemas import QuoteCreate, QuoteUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

QUOTE_STATUSES = ("draft", "sent", "accepted", "declined", "invoiced")


@router.get("/applicants")
async def list_quote_applicants(user: dict = Depends(get_current_user)):
    """Applicant-Liste fuer Angebotserstellung (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    applicants = await db.users.find(
        {"role": "applicant"},
        {"_id": 1, "full_name": 1, "email": 1}
    ).to_list(500)
    return [{"id": str(a.pop("_id")), **a} for a in applicants]


@router.get("/settings")
async def get_quote_settings(user: dict = Depends(get_current_user)):
    """Nummerierungs-Settings fuer Angebote (Staff/Admin)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    settings = await _get_quote_settings(db)
    settings["preview"] = await _generate_quote_number(db)
    return settings


async def _get_quote_settings(db) -> dict:
    settings = await db.settings.find_one({"type": "quote_numbering"})
    if settings:
        return {
            "prefix": settings.get("prefix", "QUO"),
            "start_number": settings.get("start_number", 1),
            "suffix": settings.get("suffix", ""),
            "include_date": settings.get("include_date", True),
        }
    return {"prefix": "QUO", "start_number": 1, "suffix": "", "include_date": True}


async def _generate_quote_number(db) -> str:
    cfg = await _get_quote_settings(db)
    now = datetime.now(timezone.utc)
    base = f"{cfg['prefix']}-{now.strftime('%Y%m')}" if cfg["include_date"] else cfg["prefix"]
    suffix_str = f"-{cfg['suffix']}" if cfg["suffix"] else ""
    last = await db.quotes.find_one(
        {"quote_number": {"$regex": f"^{base}-\\d+"}},
        sort=[("created_at", -1)],
        projection={"quote_number": 1},
    )
    if last:
        try:
            num_part = last["quote_number"].replace(base + "-", "").replace(suffix_str, "")
            seq = int(num_part) + 1
        except (ValueError, IndexError):
            seq = cfg["start_number"]
    else:
        seq = cfg["start_number"]
    return f"{base}-{seq:04d}{suffix_str}"


def _serialize_quote(doc: dict) -> dict:
    if not doc:
        return doc
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return {k: v for k, v in doc.items()}


@router.post("")
async def create_quote(body: QuoteCreate, user: dict = Depends(get_current_user)):
    """Angebot erstellen (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    applicant = await db.users.find_one({"_id": ObjectId(body.applicant_id)})
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")

    quote_number = await _generate_quote_number(db)
    now = datetime.now(timezone.utc).isoformat()

    items = body.items or body.line_items or [{"description": body.description or "Kursgebühr", "quantity": 1, "unit_price": body.amount or 0}]
    calculated_amount = round(sum(
        float(item.get("quantity", 1)) * float(item.get("unit_price", 0))
        for item in items
    ), 2)
    final_amount = body.amount if body.amount is not None else calculated_amount

    final_valid_until = body.valid_until
    if not final_valid_until:
        final_valid_until = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")

    quote_doc = {
        "quote_number": quote_number,
        "applicant_id": body.applicant_id,
        "applicant_name": applicant.get("full_name", applicant.get("email", "")),
        "applicant_email": applicant.get("email", ""),
        "application_id": body.application_id,
        "description": body.description,
        "items": items,
        "amount": final_amount,
        "currency": body.currency,
        "status": "draft",
        "valid_until": final_valid_until,
        "created_by": user["id"],
        "created_by_name": user.get("full_name", user.get("email", "")),
        "created_at": now,
        "updated_at": now,
        "sent_at": None,
        "notes": body.notes or "",
    }

    app_query = {"applicant_id": body.applicant_id}
    if body.application_id:
        app_query["_id"] = ObjectId(body.application_id)
    application = await db.applications.find_one(app_query, {"applicant_number": 1, "_id": 0})
    if application and application.get("applicant_number"):
        quote_doc["applicant_number"] = application["applicant_number"]

    result = await db.quotes.insert_one(quote_doc)
    quote_doc["id"] = str(result.inserted_id)

    await write_audit_log(
        "quote_created",
        user["id"],
        "quote",
        quote_doc["id"],
        {"quote_number": quote_number, "amount": final_amount, "applicant_id": body.applicant_id},
    )
    return _serialize_quote(quote_doc)


@router.get("/my")
async def list_my_quotes(user: dict = Depends(get_current_user)):
    """Eigene Angebote des Bewerbers."""
    db = get_db()
    quotes = await db.quotes.find({"applicant_id": user["id"]}).sort("created_at", -1).to_list(100)
    return [_serialize_quote(q) for q in quotes]


@router.get("")
async def list_quotes(request: Request, user: dict = Depends(get_current_user)):
    """Angebote listen. Applicants sehen eigene, Staff alle."""
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
    if applicant_id and user["role"] in STAFF_ROLES:
        query["applicant_id"] = applicant_id

    quotes = await db.quotes.find(query).sort("created_at", -1).to_list(500)
    return [_serialize_quote(q) for q in quotes]


@router.get("/stats")
async def quote_stats(user: dict = Depends(get_current_user)):
    """Angebots-Statistiken."""
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


@router.get("/{quote_id}")
async def get_quote(quote_id: str, user: dict = Depends(get_current_user)):
    """Einzelnes Angebot per Nummer oder ID."""
    db = get_db()
    quote = await db.quotes.find_one({"quote_number": quote_id}, {"_id": 0})
    if not quote:
        try:
            quote = await db.quotes.find_one({"_id": ObjectId(quote_id)})
            if quote:
                quote["id"] = str(quote.pop("_id"))
        except Exception:
            pass
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if user["role"] == "applicant" and quote.get("applicant_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    elif user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES and user["role"] != "applicant":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    if "id" not in quote:
        quote["id"] = quote.get("quote_number", "")
    return quote


@router.patch("/{quote_id}")
async def update_quote(quote_id: str, body: QuoteUpdate, user: dict = Depends(get_current_user)):
    """Angebot aktualisieren (Staff/Admin only)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    filter_q = {"quote_number": quote_id}
    existing = await db.quotes.find_one(filter_q)
    if not existing:
        try:
            filter_q = {"_id": ObjectId(quote_id)}
            existing = await db.quotes.find_one(filter_q)
        except Exception:
            pass
    if not existing:
        raise HTTPException(status_code=404, detail="Quote not found")

    updates = {k: v for k, v in body.dict(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "status" in updates and updates["status"] not in QUOTE_STATUSES:
        raise HTTPException(status_code=400, detail=f"Ungueltiger Status. Erlaubt: {', '.join(QUOTE_STATUSES)}")
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    if "items" in updates and updates["items"]:
        total = sum(float(i.get("quantity", 1)) * float(i.get("unit_price", 0)) for i in updates["items"])
        updates["amount"] = round(total, 2)
    if updates.get("status") == "sent" and not updates.get("sent_at"):
        updates["sent_at"] = datetime.now(timezone.utc).isoformat()

    await db.quotes.update_one(filter_q, {"$set": updates})
    await write_audit_log(
        "quote_updated",
        user["id"],
        "quote",
        str(existing["_id"]),
        {"quote_number": existing.get("quote_number"), "changes": updates},
    )
    updated = await db.quotes.find_one(filter_q, {"_id": 0})
    if updated and "id" not in updated:
        updated["id"] = updated.get("quote_number", str(existing["_id"]))
    return updated


@router.delete("/{quote_id}")
async def delete_quote(quote_id: str, user: dict = Depends(get_current_user)):
    """Angebot loeschen (Admin only, nur Entwuerfe)."""
    if user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin access required")
    db = get_db()
    filter_q = {"quote_number": quote_id}
    existing = await db.quotes.find_one(filter_q)
    if not existing:
        try:
            filter_q = {"_id": ObjectId(quote_id)}
            existing = await db.quotes.find_one(filter_q)
        except Exception:
            pass
    if not existing:
        raise HTTPException(status_code=404, detail="Quote not found")
    if existing.get("status") not in ("draft", None):
        raise HTTPException(status_code=400, detail="Only draft quotes can be deleted")
    await db.quotes.delete_one(filter_q)
    await write_audit_log(
        "quote_deleted",
        user["id"],
        "quote",
        str(existing["_id"]),
        {"quote_number": existing.get("quote_number")},
    )
    return {"ok": True}


@router.get("/{quote_id}/pdf")
async def download_quote_pdf(quote_id: str, user: dict = Depends(get_current_user)):
    """Angebot als PDF (ReportLab, DE/EN)."""
    db = get_db()
    quote = await db.quotes.find_one(
        {"$or": [{"quote_number": quote_id}, {"_id": ObjectId(quote_id) if len(quote_id) == 24 else None}]}
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        if str(quote.get("applicant_id")) != user["id"]:
            raise HTTPException(status_code=403, detail="Forbidden")

    company_settings = await db.settings.find_one({"type": "company_info"}) or {}
    COMPANY_NAME = company_settings.get("company_name", "W2G Academy GmbH")
    COMPANY_STREET = company_settings.get("street", "Theaterstraße 24")
    COMPANY_CITY = company_settings.get("city", "52062 Aachen")
    COMPANY_COUNTRY = company_settings.get("country", "Deutschland")
    COMPANY_EMAIL = company_settings.get("email", "info@stk-aachen.de")
    COMPANY_PHONE = company_settings.get("phone", "+49 (0) 241 990 322 92")
    COMPANY_REGISTRY = company_settings.get("registry", "Amtsgericht Aachen, HRB 23610")
    COMPANY_MD = company_settings.get("md", "Laura Saboor")
    COMPANY_TAX_ID = company_settings.get("tax_id", "")

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas

    is_en = (quote.get("applicant_language") or "de") == "en"
    L = {
        "doc_title": "OFFER" if is_en else "ANGEBOT",
        "no": "Offer no." if is_en else "Angebot Nr.",
        "date": "Date" if is_en else "Datum",
        "valid": "Valid until" if is_en else "Gültig bis",
        "bill_to": "Prepared for" if is_en else "Angebot für",
        "items": "Items" if is_en else "Positionen",
        "qty": "Qty" if is_en else "Menge",
        "unit": "Unit price" if is_en else "Einzelpreis",
        "total_col": "Total" if is_en else "Gesamt",
        "subtotal": "Subtotal" if is_en else "Zwischensumme",
        "total": "Total" if is_en else "Gesamtbetrag",
        "notes": "Notes" if is_en else "Hinweise",
        "thank_you": "Thank you for your interest!" if is_en else "Vielen Dank für Ihr Interesse!",
        "questions": "Questions" if is_en else "Bei Fragen",
    }

    w, h = A4
    ML, MR, MT, MB = 18 * mm, 18 * mm, 20 * mm, 16 * mm
    primary = HexColor("#113655")
    dark = HexColor("#1E293B")
    grey = HexColor("#64748B")
    border_color = HexColor("#E2E8F0")

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Angebot {quote.get('quote_number', '')}")

    c.setFillColor(primary)
    c.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 13)
    c.drawString(ML, h - 9 * mm, COMPANY_NAME)
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#CBD5E1"))
    c.drawString(ML, h - 12 * mm, L["doc_title"])

    c.setFillColor(dark)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(ML, h - 32 * mm, f"{L['doc_title']} {quote.get('quote_number', '')}")
    c.setFont("Helvetica", 9)
    c.setFillColor(grey)
    c.drawString(ML, h - 37 * mm, f"{L['date']}: {quote.get('created_at', '')[:10]}   |   {L['valid']}: {quote.get('valid_until', '')}")

    # Adressblock
    y = h - 55 * mm
    c.setFillColor(grey)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(ML, y, L["bill_to"].upper())
    y -= 5 * mm
    c.setFillColor(dark)
    c.setFont("Helvetica", 10)
    for line in [quote.get("applicant_name", ""), quote.get("applicant_email", "")]:
        c.drawString(ML, y, line)
        y -= 4.5 * mm

    # Tabelle
    TABLE_LEFT, TABLE_RIGHT = ML, MR
    COL_DESC = ML
    COL_QTY = 150 * mm
    COL_UNIT = 165 * mm
    COL_TOTAL = 192 * mm

    y -= 8 * mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(COL_DESC, y, L["items"])
    c.drawRightString(COL_QTY, y, L["qty"])
    c.drawRightString(COL_UNIT, y, L["unit"])
    c.drawRightString(COL_TOTAL, y, L["total_col"])
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    y -= 2 * mm
    c.line(TABLE_LEFT, y, TABLE_RIGHT, y)

    def fmt_eur(val):
        return f"{float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"

    items = quote.get("items") or []
    subtotal = 0.0
    c.setFont("Helvetica", 9)
    for item in items:
        y -= 6 * mm
        if y < 40 * mm:
            c.showPage()
            y = h - MT
        desc = item.get("description", "")
        c.setFillColor(dark)
        c.drawString(COL_DESC, y, desc[:70])
        qty = float(item.get("quantity", 1))
        unit_price = float(item.get("unit_price", 0))
        line_total = qty * unit_price
        subtotal += line_total
        c.setFillColor(grey)
        c.drawRightString(COL_QTY, y, str(qty))
        c.drawRightString(COL_UNIT, y, fmt_eur(unit_price))
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(COL_TOTAL, y, fmt_eur(line_total))
        c.setFont("Helvetica", 9)

    y -= 4 * mm
    c.setStrokeColor(border_color)
    c.line(TABLE_LEFT, y, TABLE_RIGHT, y)

    amount = quote.get("amount", subtotal)
    y -= 6 * mm
    c.setFont("Helvetica", 8)
    c.setFillColor(grey)
    c.drawRightString(150 * mm, y, f"{L['subtotal']}:")
    c.setFillColor(dark)
    c.drawRightString(192 * mm, y, fmt_eur(amount))

    y -= 10 * mm
    c.setFillColor(HexColor("#F1F5F9"))
    c.rect(100 * mm, y - 2 * mm, 192 * mm - 100 * mm + 2 * mm, 10 * mm, fill=1, stroke=0)
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(150 * mm, y + 1.5 * mm, f"{L['total']}:")
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(192 * mm, y + 1.5 * mm, fmt_eur(amount))

    if quote.get("notes"):
        y -= 14 * mm
        c.setFillColor(grey)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(ML, y, L["notes"])
        c.setFont("Helvetica", 8)
        c.drawString(ML, y - 4 * mm, str(quote.get("notes"))[:120])

    y -= 14 * mm
    c.setFillColor(grey)
    c.setFont("Helvetica", 7)
    c.drawString(ML, y, L["thank_you"])
    y -= 3.5 * mm
    c.drawString(ML, y, f"{L['questions']}: {COMPANY_EMAIL} oder Tel. {COMPANY_PHONE}")

    footer_y = 18 * mm
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.line(ML, footer_y + 5 * mm, 192 * mm, footer_y + 5 * mm)
    c.setFillColor(grey)
    c.setFont("Helvetica", 6)
    footer_line1 = f"{COMPANY_NAME}  |  {COMPANY_STREET}  |  {COMPANY_CITY}  |  {COMPANY_COUNTRY}"
    footer_line2 = f"Registergericht: {COMPANY_REGISTRY}  |  Geschäftsführung: {COMPANY_MD}"
    if COMPANY_TAX_ID:
        footer_line2 += f"  |  USt-IdNr.: {COMPANY_TAX_ID}"
    footer_line3 = f"E-Mail: {COMPANY_EMAIL}  |  Tel: {COMPANY_PHONE}"
    c.drawCentredString(w / 2, footer_y, footer_line1)
    c.drawCentredString(w / 2, footer_y - 3 * mm, footer_line2)
    c.drawCentredString(w / 2, footer_y - 6 * mm, footer_line3)

    c.save()
    buf.seek(0)
    filename = f"{quote.get('quote_number', 'angebot')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/{quote_id}/send")
async def send_quote_email(quote_id: str, user: dict = Depends(get_current_user)):
    """Angebot per E-Mail versenden (PDF-Anhang, Status -> sent)."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    db = get_db()
    quote = await db.quotes.find_one(
        {"$or": [{"quote_number": quote_id}, {"_id": ObjectId(quote_id) if len(quote_id) == 24 else None}]}
    )
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    applicant_email = quote.get("applicant_email")
    if not applicant_email:
        raise HTTPException(status_code=400, detail="Keine E-Mail-Adresse fuer den Bewerber hinterlegt")

    pdf_response = await download_quote_pdf(quote_id, user)
    pdf_bytes = b""
    async for chunk in pdf_response.body_iterator:
        pdf_bytes += chunk if isinstance(chunk, bytes) else chunk.encode()

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
        quote_number = quote.get("quote_number", "Angebot")
        applicant_name = quote.get("applicant_name", "")
        amount = quote.get("amount", 0)
        amount_str = f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"

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
                    anbei erhalten Sie Ihr Angebot <strong>{quote_number}</strong>
                    ueber <strong>{amount_str}</strong>,
                    gueltig bis <strong>{quote.get('valid_until', '')}</strong>.
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
        import logging
        logging.getLogger(__name__).info(f"[EMAIL] Quote {quote_number} sent to {applicant_email}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"E-Mail-Versand fehlgeschlagen: {str(e)}")

    now = datetime.now(timezone.utc).isoformat()
    update_fields = {"updated_at": now, "sent_at": now}
    if quote.get("status") == "draft":
        update_fields["status"] = "sent"
    await db.quotes.update_one({"quote_number": quote.get("quote_number")}, {"$set": update_fields})
    await write_audit_log(
        "quote_sent",
        user["id"],
        "quote",
        str(quote.get("_id", "")),
        {"quote_number": quote.get("quote_number"), "sent_to": applicant_email},
    )
    return {"ok": True, "sent_to": applicant_email, "status": update_fields.get("status", quote.get("status"))}
