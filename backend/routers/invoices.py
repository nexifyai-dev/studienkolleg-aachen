"""
Invoice router – CRUD for invoices.

- Staff/Admin: create, list all, update status, view detail
- Applicant: list own invoices, view detail
- Invoice numbers are auto-generated (INV-YYYYMM-XXXX)
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, STAFF_ROLES, ADMIN_ROLES
from models.schemas import InvoiceCreate, InvoiceUpdate, to_str_id
from services.audit import write_audit_log

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


async def _generate_invoice_number(db) -> str:
    """Generate sequential invoice number: INV-YYYYMM-XXXX."""
    now = datetime.now(timezone.utc)
    prefix = f"INV-{now.strftime('%Y%m')}-"
    last = await db.invoices.find_one(
        {"invoice_number": {"$regex": f"^{prefix}"}},
        sort=[("invoice_number", -1)],
        projection={"invoice_number": 1}
    )
    if last:
        try:
            seq = int(last["invoice_number"].split("-")[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


def _serialize_invoice(doc: dict) -> dict:
    """Convert MongoDB invoice document to JSON-safe dict."""
    if not doc:
        return doc
    doc = {k: v for k, v in doc.items() if k != "_id"}
    if "id" not in doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


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

    # Build line items
    items = body.items or [{"description": body.description, "quantity": 1, "unit_price": body.amount}]

    invoice_doc = {
        "invoice_number": invoice_number,
        "applicant_id": body.applicant_id,
        "applicant_name": applicant.get("full_name", applicant.get("email", "")),
        "applicant_email": applicant.get("email", ""),
        "application_id": body.application_id,
        "description": body.description,
        "items": items,
        "amount": body.amount,
        "currency": body.currency,
        "status": "draft",
        "due_date": body.due_date,
        "created_by": user["id"],
        "created_by_name": user.get("full_name", user.get("email", "")),
        "created_at": now,
        "updated_at": now,
        "paid_at": None,
        "notes": "",
    }

    result = await db.invoices.insert_one(invoice_doc)
    invoice_doc["id"] = str(result.inserted_id)

    # Audit log
    await write_audit_log(
        db,
        actor_id=user["id"],
        action="invoice_created",
        target_type="invoice",
        target_id=invoice_doc["id"],
        details={"invoice_number": invoice_number, "amount": body.amount, "applicant_id": body.applicant_id},
    )

    return _serialize_invoice(invoice_doc)


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

    cursor = db.invoices.find(query, {"_id": 0}).sort("created_at", -1)
    invoices = await cursor.to_list(length=500)

    # Ensure all have id field
    for inv in invoices:
        if "id" not in inv:
            inv["id"] = inv.get("invoice_number", "")

    return invoices


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

    # If marking as paid, set paid_at
    if updates.get("status") == "paid" and not updates.get("paid_at"):
        updates["paid_at"] = datetime.now(timezone.utc).isoformat()

    await db.invoices.update_one(filter_q, {"$set": updates})

    # Audit
    inv_id = str(existing["_id"])
    await write_audit_log(
        db,
        actor_id=user["id"],
        action="invoice_updated",
        target_type="invoice",
        target_id=inv_id,
        details={"invoice_number": existing.get("invoice_number"), "changes": updates},
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
        db,
        actor_id=user["id"],
        action="invoice_deleted",
        target_type="invoice",
        target_id=str(existing["_id"]),
        details={"invoice_number": existing.get("invoice_number")},
    )

    return {"ok": True}
