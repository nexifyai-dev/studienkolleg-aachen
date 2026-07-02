"""
Application router.

Security notes:
- Applicants: can only see/modify their own applications
- Partners (agency): scoped to their organization_id
- Staff: scoped by workspace_id query param; without it, see all in their permitted workspaces
- Stage changes are audit-logged and activity-tracked
"""
from datetime import datetime, timezone
import asyncio
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db, get_next_applicant_number
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES, PARTNER_ROLES
from models.schemas import ApplicationCreate, ApplicationUpdate, CaseNoteCreate, CaseEmailSend, to_str_id
from services.audit import write_audit_log
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("")
async def list_applications(request: Request, user: dict = Depends(get_current_user)):
    db = get_db()
    query = {}
    workspace_id = request.query_params.get("workspace_id")
    stage = request.query_params.get("stage")

    if user["role"] == "applicant":
        # Applicants see only their own
        query["applicant_id"] = user["id"]
    elif user["role"] in PARTNER_ROLES:
        # Partners scoped to their organization
        if not user.get("organization_id"):
            return []
        query["organization_id"] = user["organization_id"]
    elif user["role"] in STAFF_ROLES:
        # Staff: scope by workspace if provided; otherwise all (admin sees all)
        if workspace_id:
            query["workspace_id"] = workspace_id
        # No workspace_id → staff sees all applications (intentional for dashboard/kanban)
    else:
        raise HTTPException(status_code=403, detail="Forbidden")

    if stage:
        query["current_stage"] = stage

    # ── Textsuche (Name, E-Mail, Telefon, Bewerbernummer, Land) ──
    search = request.query_params.get("search")
    if search and search.strip():
        search = search.strip()
        # Suche ueber verknuepfte Bewerber-Daten UND Bewerbungs-Felder
        search_users = await db.users.find(
            {"$or": [
                {"full_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
            ]},
            {"_id": 1}
        ).to_list(200)
        user_ids = [str(u["_id"]) for u in search_users]

        search_conditions = [
            {"applicant_number": {"$regex": search, "$options": "i"}},
            {"degree_country": {"$regex": search, "$options": "i"}},
            {"course_type": {"$regex": search, "$options": "i"}},
        ]
        if user_ids:
            search_conditions.append({"applicant_id": {"$in": user_ids}})

        if query:
            query = {"$and": [query, {"$or": search_conditions}]}
        else:
            query = {"$or": search_conditions}

    apps = await db.applications.find(query).sort("last_activity_at", -1).to_list(500)

    result = []
    if user["role"] in STAFF_ROLES and apps:
        # Batch-fetch applicants and workspaces (avoid N+1)
        applicant_ids = list(set(str(a.get("applicant_id", "")) for a in apps if a.get("applicant_id")))
        workspace_ids = list(set(str(a.get("workspace_id", "")) for a in apps if a.get("workspace_id")))

        applicant_map = {}
        if applicant_ids:
            try:
                applicants = await db.users.find(
                    {"_id": {"$in": [ObjectId(aid) for aid in applicant_ids]}},
                    {"full_name": 1, "email": 1, "phone": 1, "country": 1},
                ).to_list(None)
                applicant_map = {str(a["_id"]): a for a in applicants}
            except Exception:
                pass

        ws_map = {}
        if workspace_ids:
            try:
                workspaces = await db.workspaces.find(
                    {"_id": {"$in": [ObjectId(wid) for wid in workspace_ids]}},
                    {"name": 1},
                ).to_list(None)
                ws_map = {str(w["_id"]): w.get("name") for w in workspaces}
            except Exception:
                pass

        for app in apps:
            app_dict = to_str_id(app)
            aid = app_dict.get("applicant_id")
            if aid and aid in applicant_map:
                app_dict["applicant"] = to_str_id(applicant_map[aid])
            wid = app_dict.get("workspace_id")
            if wid and wid in ws_map:
                app_dict["workspace_name"] = ws_map[wid]
            result.append(app_dict)
    else:
        result = [to_str_id(a) for a in apps]
    return result


@router.post("")
async def create_application(data: ApplicationCreate, user: dict = Depends(get_current_user)):
    db = get_db()
    # Applicants can only create for themselves
    if data.applicant_id and user["role"] not in STAFF_ROLES:
        data.applicant_id = None
    applicant_id = data.applicant_id or user["id"]

    workspace = await db.workspaces.find_one({"_id": ObjectId(data.workspace_id)})
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace nicht gefunden")

    # ── Dubletten-Pruefung: E-Mail / Telefon Match ──────────────
    applicant_user = await db.users.find_one({"_id": ObjectId(applicant_id)}, {"_id": 0, "email": 1, "phone": 1, "full_name": 1})
    duplicate_info = None
    if applicant_user:
        dup_query = {"$or": []}
        if applicant_user.get("email"):
            dup_query["$or"].append({"applicant_id": {"$ne": applicant_id}, "applicant_email": applicant_user["email"]})
        if applicant_user.get("phone") and len(applicant_user["phone"]) > 5:
            dup_query["$or"].append({"applicant_id": {"$ne": applicant_id}, "applicant_phone": applicant_user["phone"]})
        if dup_query["$or"]:
            # Check if any existing application has the same email/phone via user join
            existing_apps = await db.applications.find(
                {"applicant_id": {"$ne": applicant_id}, "current_stage": {"$nin": ["archived", "declined"]}},
                {"_id": 1, "applicant_id": 1, "current_stage": 1, "applicant_number": 1}
            ).to_list(500)
            for eapp in existing_apps:
                euser = await db.users.find_one({"_id": ObjectId(eapp["applicant_id"])}, {"_id": 0, "email": 1, "phone": 1, "full_name": 1})
                if not euser:
                    continue
                email_match = applicant_user.get("email") and euser.get("email") and applicant_user["email"].lower() == euser["email"].lower()
                phone_match = applicant_user.get("phone") and euser.get("phone") and applicant_user["phone"] == euser["phone"] and len(applicant_user["phone"]) > 5
                if email_match or phone_match:
                    duplicate_info = {
                        "existing_app_id": str(eapp["_id"]),
                        "existing_applicant_number": eapp.get("applicant_number"),
                        "existing_name": euser.get("full_name"),
                        "match_type": "email" if email_match else "phone",
                    }
                    break

    app_doc = {
        "applicant_id": applicant_id,
        "workspace_id": data.workspace_id,
        "current_stage": "lead_new",
        "source": data.source,
        "notes": data.notes,
        "priority": "normal",
        "applicant_number": await get_next_applicant_number(),
        "duplicate_flag": bool(duplicate_info),
        "duplicate_info": duplicate_info,
        "created_at": datetime.now(timezone.utc),
        "last_activity_at": datetime.now(timezone.utc),
        "created_by": user["id"],
    }
    result = await db.applications.insert_one(app_doc)
    app_id = str(result.inserted_id)
    await write_audit_log("application_created", user["id"], "application", app_id)

    # Dubletten-Alert: Admin-Task erstellen
    if duplicate_info:
        import uuid as _uuid
        now_iso = datetime.now(timezone.utc).isoformat()
        admins = await db.users.find({"role": {"$in": ["superadmin", "admin"]}}, {"_id": 1}).to_list(10)
        for adm in admins:
            await db.tasks.insert_one({
                "id": str(_uuid.uuid4()),
                "application_id": app_id,
                "assigned_to": str(adm["_id"]),
                "title": f"Dubletten-Pruefung: {applicant_user.get('full_name', 'Bewerber')} ({duplicate_info['match_type'].upper()}-Match)",
                "description": (
                    f"Neue Bewerbung {app_doc['applicant_number']} hat eine moegliche Dublette: "
                    f"Bestehende Bewerbung {duplicate_info.get('existing_applicant_number', '?')} "
                    f"({duplicate_info.get('existing_name', '?')}). "
                    f"Match-Typ: {duplicate_info['match_type']}. "
                    f"Bitte pruefen und ggf. zusammenfuehren."
                ),
                "status": "open",
                "priority": "high",
                "type": "duplicate_review",
                "category": "admin",
                "created_at": now_iso,
                "created_by": "system",
            })
        await db.notifications.insert_one({
            "id": str(_uuid.uuid4()),
            "user_id": str(admins[0]["_id"]) if admins else "system",
            "type": "duplicate_detected",
            "title": "Dublette erkannt",
            "message": f"Bewerbung {app_doc['applicant_number']}: {duplicate_info['match_type'].upper()}-Match mit {duplicate_info.get('existing_applicant_number', '?')}",
            "read": False,
            "created_at": now_iso,
        })
        logger.warning(f"[DUPLICATE] Detected: app={app_id} match={duplicate_info}")

    app_doc.pop("_id", None)
    return {**app_doc, "id": app_id}


@router.get("/{app_id}")
async def get_application(app_id: str, user: dict = Depends(get_current_user)):
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Bewerbungs-ID")
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    app_dict = to_str_id(app)
    # Ownership check
    if user["role"] == "applicant" and app_dict.get("applicant_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    if user["role"] in PARTNER_ROLES and app_dict.get("organization_id") != user.get("organization_id"):
        raise HTTPException(status_code=403, detail="Forbidden")
    # Join applicant user data for staff
    if user["role"] in STAFF_ROLES and app_dict.get("applicant_id"):
        try:
            applicant = await db.users.find_one(
                {"_id": ObjectId(app_dict["applicant_id"])},
                {"full_name": 1, "email": 1, "phone": 1, "country": 1,
                 "first_name": 1, "last_name": 1, "date_of_birth": 1, "language_pref": 1},
            )
            if applicant:
                app_dict["applicant"] = to_str_id(dict(applicant))
        except Exception:
            pass
    # Join workspace name
    if app_dict.get("workspace_id"):
        try:
            ws = await db.workspaces.find_one({"_id": ObjectId(app_dict["workspace_id"])}, {"name": 1})
            if ws:
                app_dict["workspace_name"] = ws.get("name")
        except Exception:
            pass
    return app_dict


@router.put("/{app_id}")
async def update_application(
    app_id: str,
    data: ApplicationUpdate,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige ID")
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")

    old_stage = app.get("current_stage")

    # State-Machine-Validierung bei Statuswechsel
    if data.current_stage and data.current_stage != old_stage:
        from services.state_machine import validate_transition
        force = user["role"] in ADMIN_ROLES
        is_valid, error_msg = validate_transition(old_stage, data.current_stage, force=force)
        if not is_valid:
            raise HTTPException(status_code=422, detail=error_msg)

    update = {k: v for k, v in data.model_dump().items() if v is not None}
    update["last_activity_at"] = datetime.now(timezone.utc)
    update["updated_by"] = user["id"]
    await db.applications.update_one({"_id": ObjectId(app_id)}, {"$set": update})

    if data.current_stage and data.current_stage != old_stage:
        await write_audit_log("stage_changed", user["id"], "application", app_id,
                              {"old_stage": old_stage, "new_stage": data.current_stage})
        await db.application_activities.insert_one({
            "application_id": app_id,
            "action": "stage_changed",
            "old_value": old_stage,
            "new_value": data.current_stage,
            "actor_id": user["id"],
            "occurred_at": datetime.now(timezone.utc),
        })
        # Brain-Memory: Statuswechsel lernen
        try:
            from services.brain_memory import ingest_application_event
            await ingest_application_event(app_id, app.get("applicant_id", ""), "stage_changed",
                                           {"old_stage": old_stage, "new_stage": data.current_stage})
        except Exception:
            pass
        # Automation: Status-Change E-Mail + Notification (DE/EN)
        try:
            if app.get("applicant_id"):
                from bson import ObjectId as ObjId
                applicant_user = await db.users.find_one(
                    {"_id": ObjId(app["applicant_id"])},
                    {"email": 1, "full_name": 1},
                )
                if applicant_user:
                    from services.automation import trigger_status_change
                    await trigger_status_change(
                        application_id=app_id,
                        applicant_email=applicant_user.get("email", ""),
                        applicant_name=applicant_user.get("full_name", ""),
                        old_stage=old_stage,
                        new_stage=data.current_stage,
                        actor_id=user["id"],
                        applicant_id=app["applicant_id"],
                    )
        except Exception:
            pass

        # Stage-Effects ausfuehren (Auto-Tasks, Aufgaben schliessen, etc.)
        try:
            from services.stage_effects import execute_stage_effects
            await execute_stage_effects(app_id, old_stage, data.current_stage, user["id"])
        except Exception:
            pass

    return {"message": "Aktualisiert", "id": app_id}


@router.get("/{app_id}/allowed-transitions")
async def get_allowed_transitions(app_id: str, user: dict = Depends(get_current_user)):
    """Gibt die erlaubten Zielstatus fuer eine Bewerbung zurueck."""
    db = get_db()
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)}, {"current_stage": 1})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige ID")
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")

    from services.state_machine import get_allowed_transitions as get_transitions, STAGE_LABELS_DE
    current = app.get("current_stage", "lead_new")
    allowed = get_transitions(current)
    return {
        "current_stage": current,
        "allowed_transitions": [
            {"stage": s, "label": STAGE_LABELS_DE.get(s, s)} for s in allowed
        ],
    }


# ─── Case Notes (Internal / Shared) ──────────────────────────────────────────

@router.post("/{app_id}/notes")
async def add_case_note(
    app_id: str,
    data: CaseNoteCreate,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Add an internal or shared note to a case."""
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    content = data.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Notiz darf nicht leer sein")

    note_doc = {
        "application_id": app_id,
        "author_id": user["id"],
        "author_name": user.get("full_name", user.get("email", "")),
        "author_role": user["role"],
        "content": content,
        "visibility": data.visibility,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.case_notes.insert_one(note_doc)
    note_doc["id"] = str(result.inserted_id)

    await db.application_activities.insert_one({
        "application_id": app_id,
        "action": "note_added",
        "old_value": None,
        "new_value": content[:80],
        "actor_id": user["id"],
        "actor_name": user.get("full_name", ""),
        "occurred_at": datetime.now(timezone.utc),
    })
    await write_audit_log("case_note_added", user["id"], "application", app_id,
                          {"visibility": data.visibility})
    # Brain-Memory: Notiz lernen
    try:
        app = await db.applications.find_one({"_id": ObjectId(app_id)}, {"applicant_id": 1})
        if app:
            from services.brain_memory import ingest_application_event
            await ingest_application_event(app_id, app.get("applicant_id", ""), "note_added", {"content": content})
    except Exception:
        pass
    return to_str_id(note_doc)


@router.get("/{app_id}/notes")
async def list_case_notes(app_id: str, user: dict = Depends(get_current_user)):
    """List all notes for a case. Applicants only see 'shared' notes."""
    db = get_db()
    query = {"application_id": app_id}
    if user["role"] == "applicant":
        query["visibility"] = "shared"
    notes = await db.case_notes.find(query).sort("created_at", -1).to_list(200)
    return [to_str_id(n) for n in notes]


# ─── Activity History ─────────────────────────────────────────────────────────

@router.get("/{app_id}/activities")
async def list_activities(app_id: str, user: dict = Depends(get_current_user)):
    """Unified activity stream for a case."""
    db = get_db()
    # Merge application_activities + audit_logs for this case
    activities = await db.application_activities.find(
        {"application_id": app_id}
    ).sort("occurred_at", -1).to_list(100)

    audit_entries = await db.audit_logs.find(
        {"target_id": app_id, "target_type": "application"}
    ).sort("occurred_at", -1).to_list(100)

    # Also fetch email events
    email_events = await db.email_events.find(
        {"application_id": app_id}
    ).sort("sent_at", -1).to_list(50)

    result = []
    for a in activities:
        result.append({
            "type": "activity",
            "action": a.get("action"),
            "old_value": a.get("old_value"),
            "new_value": a.get("new_value"),
            "actor_id": a.get("actor_id"),
            "actor_name": a.get("actor_name", ""),
            "occurred_at": a.get("occurred_at"),
        })
    for a in audit_entries:
        # Skip duplicates (stage changes are in both collections)
        if a.get("action") in ("stage_changed",):
            continue
        result.append({
            "type": "audit",
            "action": a.get("action"),
            "actor_id": a.get("actor_id"),
            "details": a.get("details"),
            "occurred_at": a.get("occurred_at"),
        })
    for e in email_events:
        result.append({
            "type": "email",
            "action": "email_sent",
            "subject": e.get("subject"),
            "to": e.get("to"),
            "status": e.get("status", "sent"),
            "occurred_at": e.get("sent_at"),
        })

    result.sort(key=lambda x: x.get("occurred_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return result[:80]


# ─── Applicant Profile Edit (Staff/Admin) ────────────────────────────────────

@router.put("/{app_id}/profile")
async def update_applicant_profile(
    app_id: str,
    data: dict,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Update applicant's user profile fields from case context."""
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")
    applicant_id = app.get("applicant_id")
    if not applicant_id:
        raise HTTPException(status_code=400, detail="Kein Bewerber zugeordnet")

    body = await __import__("starlette.requests").Request.json() if False else data
    ALLOWED = {"full_name", "phone", "country", "date_of_birth", "email"}
    changes = {}
    for k, v in body.items():
        if k in ALLOWED and v is not None:
            changes[k] = v

    if not changes:
        return {"status": "no_changes"}

    # Fetch old values for audit
    old_user = await db.users.find_one({"_id": ObjectId(applicant_id)}, {k: 1 for k in ALLOWED})
    old_vals = {k: (old_user or {}).get(k) for k in changes}

    await db.users.update_one({"_id": ObjectId(applicant_id)}, {"$set": changes})

    for field, new_val in changes.items():
        await db.application_activities.insert_one({
            "application_id": app_id,
            "action": "profile_field_changed",
            "old_value": f"{field}: {old_vals.get(field, '–')}",
            "new_value": f"{field}: {new_val}",
            "actor_id": user["id"],
            "actor_name": user.get("full_name", ""),
            "occurred_at": datetime.now(timezone.utc),
        })
    await write_audit_log("applicant_profile_updated", user["id"], "application", app_id,
                          {"changed_fields": list(changes.keys())})
    return {"status": "updated", "changed": list(changes.keys())}


# ─── Case Email (Send from case context) ─────────────────────────────────────

@router.post("/{app_id}/send-email")
async def send_case_email(
    app_id: str,
    data: CaseEmailSend,
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    """Send an ad-hoc email to the applicant from the case context."""
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Nicht gefunden")

    applicant_id = app.get("applicant_id")
    if not applicant_id:
        raise HTTPException(status_code=400, detail="Kein Bewerber zugeordnet")

    applicant = await db.users.find_one({"_id": ObjectId(applicant_id)}, {"email": 1, "full_name": 1})
    if not applicant:
        raise HTTPException(status_code=404, detail="Bewerber nicht gefunden")

    to_email = applicant.get("email")
    to_name = applicant.get("full_name", "")

    try:
        from services.email import send_case_email as _send_case_email
        lang = data.lang

        sender_name = user.get("full_name", "Staff")
        await asyncio.to_thread(_send_case_email, to_email, to_name, data.subject, data.body, lang)

        # Log the email event
        await db.email_events.insert_one({
            "application_id": app_id,
            "to": to_email,
            "subject": data.subject,
            "body_preview": data.body[:200],
            "sender_id": user["id"],
            "sender_name": sender_name,
            "status": "sent",
            "lang": lang,
            "sent_at": datetime.now(timezone.utc),
        })

        await db.application_activities.insert_one({
            "application_id": app_id,
            "action": "email_sent",
            "old_value": None,
            "new_value": f"An: {to_email} – {data.subject}",
            "actor_id": user["id"],
            "actor_name": sender_name,
            "occurred_at": datetime.now(timezone.utc),
        })
        await write_audit_log("case_email_sent", user["id"], "application", app_id,
                              {"to": to_email, "subject": data.subject})
        return {"status": "sent", "to": to_email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"E-Mail-Versand fehlgeschlagen: {str(e)}")



# ═══ Fallakte PDF Export ═══════════════════════════════════════════════════════
@router.get("/{app_id}/pdf")
async def download_case_file_pdf(app_id: str, user: dict = Depends(get_current_user)):
    """Generates a comprehensive case file PDF for an applicant."""
    if user["role"] not in STAFF_ROLES and user["role"] not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")

    db = get_db()
    app_doc = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app_doc:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")

    # Gather all related data
    applicant = None
    if app_doc.get("applicant_id"):
        applicant = await db.users.find_one({"_id": ObjectId(app_doc["applicant_id"])}, {"password_hash": 0})

    documents = await db.documents.find({"application_id": app_id}).to_list(50)
    tasks = await db.tasks.find({"application_id": app_id}).to_list(50)
    notes = await db.case_notes.find({"application_id": app_id}).sort("created_at", -1).to_list(20)
    screenings = await db.ai_screenings.find({"application_id": app_id}).sort("created_at", -1).to_list(5)
    invoices_cursor = db.invoices.find({})
    all_invoices = await invoices_cursor.to_list(200)
    applicant_invoices = [i for i in all_invoices if i.get("applicant_id") == app_doc.get("applicant_id")]

    # Load company settings
    settings_doc = await db.invoice_settings.find_one({})
    cs = settings_doc or {}

    COMPANY_NAME = cs.get("company_name", "W2G Academy GmbH")
    COMPANY_STREET = cs.get("street", "Theaterstrasse 24")
    COMPANY_CITY = cs.get("city", "52062 Aachen")
    COMPANY_COUNTRY = cs.get("country", "Deutschland")
    COMPANY_PHONE = cs.get("phone", "+49 (0) 241 990 322 92")
    COMPANY_EMAIL = cs.get("email", "info@stk-aachen.de")
    COMPANY_REGISTRY = cs.get("registry", "Amtsgericht Aachen, HRB 23610")
    COMPANY_MD = cs.get("managing_director", "Laura Saboor")
    COMPANY_TAX_ID = cs.get("tax_id", "DE333306663")

    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas
    from fastapi.responses import StreamingResponse

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    primary = HexColor("#113655")
    grey = HexColor("#64748B")
    dark = HexColor("#1E293B")
    light_grey = HexColor("#F1F5F9")
    white = HexColor("#FFFFFF")
    border_color = HexColor("#E2E8F0")
    green = HexColor("#16A34A")
    red = HexColor("#DC2626")
    amber = HexColor("#D97706")

    ML = 20 * mm
    MR = w - 20 * mm
    TABLE_LEFT = 18 * mm
    TABLE_RIGHT = w - 18 * mm
    SECTION_GAP = 8 * mm

    stage_labels = {
        'lead_new': 'Neue Anfrage', 'in_review': 'In Bearbeitung', 'pending_docs': 'Docs ausstehend',
        'interview_scheduled': 'Interview geplant', 'conditional_offer': 'Bedingtes Angebot',
        'offer_sent': 'Angebot versendet', 'enrolled': 'Eingeschrieben',
        'declined': 'Abgelehnt', 'on_hold': 'Pausiert', 'archived': 'Archiviert',
    }

    def fmt_date(val):
        if not val:
            return "-"
        if isinstance(val, str) and "T" in val:
            try:
                from datetime import datetime as dt_cls
                d = dt_cls.fromisoformat(val.replace("Z", "+00:00"))
                return d.strftime("%d.%m.%Y")
            except Exception:
                return val[:10] if len(val) >= 10 else val
        if hasattr(val, 'strftime'):
            return val.strftime("%d.%m.%Y")
        return str(val)

    def draw_section_title(canvas_obj, y_pos, title):
        canvas_obj.setFillColor(primary)
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawString(ML, y_pos, title)
        y_pos -= 1.5 * mm
        canvas_obj.setStrokeColor(primary)
        canvas_obj.setLineWidth(0.8)
        canvas_obj.line(ML, y_pos, MR, y_pos)
        return y_pos - 4 * mm

    def check_page_break(canvas_obj, y_pos, needed=30 * mm):
        if y_pos < needed:
            draw_footer(canvas_obj)
            canvas_obj.showPage()
            return h - 25 * mm
        return y_pos

    def draw_footer(canvas_obj):
        footer_y = 15 * mm
        canvas_obj.setStrokeColor(border_color)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(TABLE_LEFT, footer_y + 4 * mm, TABLE_RIGHT, footer_y + 4 * mm)
        canvas_obj.setFillColor(grey)
        canvas_obj.setFont("Helvetica", 5.5)
        f1 = f"{COMPANY_NAME}  |  {COMPANY_STREET}  |  {COMPANY_CITY}  |  {COMPANY_COUNTRY}"
        f2 = f"Registergericht: {COMPANY_REGISTRY}  |  Geschaeftsfuehrung: {COMPANY_MD}  |  USt-IdNr.: {COMPANY_TAX_ID}"
        f3 = f"E-Mail: {COMPANY_EMAIL}  |  Tel: {COMPANY_PHONE}"
        canvas_obj.drawCentredString(w / 2, footer_y, f1)
        canvas_obj.drawCentredString(w / 2, footer_y - 2.8 * mm, f2)
        canvas_obj.drawCentredString(w / 2, footer_y - 5.6 * mm, f3)

    applicant_name = applicant.get("full_name", "Unbekannt") if applicant else app_doc.get("applicant_name", "Unbekannt")
    current_stage = app_doc.get("current_stage", "lead_new")

    # ─── HEADER BAR ───────────────────────────────────────────────
    c.setFillColor(primary)
    c.rect(0, h - 32 * mm, w, 32 * mm, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(ML, h - 16 * mm, "FALLAKTE")
    c.setFont("Helvetica", 9)
    c.drawString(ML, h - 22 * mm, f"Bewerber: {applicant_name}")
    c.setFont("Helvetica", 7.5)
    c.drawString(ML, h - 27 * mm, f"Erstellt am: {fmt_date(datetime.now(timezone.utc).isoformat())}  |  Aktenzeichen: {str(app_doc['_id'])[-8:].upper()}")
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(MR, h - 16 * mm, stage_labels.get(current_stage, current_stage).upper())
    c.setFont("Helvetica", 8)
    c.drawRightString(MR, h - 22 * mm, "Studienkolleg Aachen")

    # ─── PERSOENLICHE DATEN + BEWERBUNGSDATEN ─────────────────────
    y = h - 42 * mm

    # Left column: Personal data
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(ML, y, "PERSOENLICHE DATEN")
    c.setFont("Helvetica", 8)
    c.setFillColor(dark)
    fields_personal = [
        ("Name:", applicant_name),
        ("E-Mail:", applicant.get("email", "-") if applicant else "-"),
        ("Telefon:", applicant.get("phone", "-") if applicant else "-"),
        ("Land:", applicant.get("country", "-") if applicant else "-"),
        ("Geb.-Datum:", fmt_date(app_doc.get("date_of_birth"))),
    ]
    py = y - 5 * mm
    for label, val in fields_personal:
        c.setFillColor(grey)
        c.setFont("Helvetica", 7.5)
        c.drawString(ML, py, label)
        c.setFillColor(dark)
        c.setFont("Helvetica", 7.5)
        c.drawString(ML + 25 * mm, py, str(val) if val else "-")
        py -= 3.8 * mm

    # Right column: Application data
    mid_x = w / 2 + 5 * mm
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(mid_x, y, "BEWERBUNGSDATEN")
    c.setFont("Helvetica", 8)
    fields_app = [
        ("Kurstyp:", app_doc.get("course_type", "-")),
        ("Semester:", app_doc.get("desired_start", "-")),
        ("Deutschniveau:", app_doc.get("language_level", "-")),
        ("Abschlussland:", app_doc.get("degree_country", "-")),
        ("Kombination:", app_doc.get("combo_option", "-")),
        ("Quelle:", app_doc.get("source", "-")),
    ]
    ay = y - 5 * mm
    for label, val in fields_app:
        c.setFillColor(grey)
        c.setFont("Helvetica", 7.5)
        c.drawString(mid_x, ay, label)
        c.setFillColor(dark)
        c.setFont("Helvetica", 7.5)
        c.drawString(mid_x + 28 * mm, ay, str(val) if val else "-")
        ay -= 3.8 * mm

    y = min(py, ay) - SECTION_GAP

    # ─── DOKUMENTE ────────────────────────────────────────────────
    y = check_page_break(c, y)
    y = draw_section_title(c, y, f"DOKUMENTE ({len(documents)})")

    if documents:
        # Table header
        header_h = 6 * mm
        c.setFillColor(primary)
        c.rect(TABLE_LEFT, y - 1 * mm, TABLE_RIGHT - TABLE_LEFT, header_h, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(ML, y + 0.5 * mm, "Dateiname")
        c.drawString(ML + 55 * mm, y + 0.5 * mm, "Typ")
        c.drawString(ML + 95 * mm, y + 0.5 * mm, "Status")
        c.drawString(ML + 125 * mm, y + 0.5 * mm, "Validierung")

        for i, doc in enumerate(documents):
            y -= 6 * mm
            y = check_page_break(c, y)
            if i % 2 == 0:
                c.setFillColor(light_grey)
                c.rect(TABLE_LEFT, y - 1.5 * mm, TABLE_RIGHT - TABLE_LEFT, 5.5 * mm, fill=1, stroke=0)

            c.setFillColor(dark)
            c.setFont("Helvetica", 7)
            fname = doc.get("filename", doc.get("document_type", "?"))
            if len(fname) > 30:
                fname = fname[:28] + "..."
            c.drawString(ML, y, fname)
            c.drawString(ML + 55 * mm, y, doc.get("document_type", "-"))

            status = doc.get("status", "uploaded")
            status_color = green if status == "approved" else red if status == "rejected" else amber if status == "in_review" else grey
            c.setFillColor(status_color)
            c.setFont("Helvetica-Bold", 7)
            status_labels = {"uploaded": "Hochgeladen", "in_review": "In Pruefung", "approved": "Akzeptiert", "rejected": "Abgelehnt"}
            c.drawString(ML + 95 * mm, y, status_labels.get(status, status))

            c.setFillColor(grey)
            c.setFont("Helvetica", 7)
            c.drawString(ML + 125 * mm, y, doc.get("validation_status", "-"))
    else:
        c.setFillColor(grey)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(ML, y, "Keine Dokumente hochgeladen")
        y -= 5 * mm

    y -= SECTION_GAP

    # ─── AUFGABEN ─────────────────────────────────────────────────
    y = check_page_break(c, y)
    y = draw_section_title(c, y, f"AUFGABEN ({len(tasks)})")

    if tasks:
        for t in tasks:
            y = check_page_break(c, y)
            status = t.get("status", "open")
            c.setFillColor(green if status == "done" else amber if status == "in_progress" else dark)
            c.setFont("Helvetica", 7.5)
            status_label = {"open": "Offen", "in_progress": "In Arbeit", "done": "Erledigt"}.get(status, status)
            title = t.get("title", "-")
            if len(title) > 60:
                title = title[:58] + "..."
            c.drawString(ML, y, f"[{status_label}] {title}")
            c.setFillColor(grey)
            c.setFont("Helvetica", 6.5)
            prio = t.get("priority", "normal")
            due = fmt_date(t.get("due_date"))
            c.drawRightString(MR, y, f"Prioritaet: {prio}  |  Faellig: {due}")
            y -= 4.5 * mm
    else:
        c.setFillColor(grey)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(ML, y, "Keine Aufgaben vorhanden")
        y -= 5 * mm

    y -= SECTION_GAP

    # ─── RECHNUNGEN ───────────────────────────────────────────────
    y = check_page_break(c, y)
    y = draw_section_title(c, y, f"RECHNUNGEN ({len(applicant_invoices)})")

    if applicant_invoices:
        for inv in applicant_invoices:
            y = check_page_break(c, y)
            c.setFillColor(dark)
            c.setFont("Helvetica", 7.5)
            inv_nr = inv.get("invoice_number", "-")
            inv_status = inv.get("status", "draft")
            inv_amount = inv.get("amount", 0)
            fmt_amount = f"{inv_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " EUR"
            status_labels = {"draft": "Entwurf", "sent": "Versendet", "paid": "Bezahlt", "overdue": "Ueberfaellig", "cancelled": "Storniert"}
            c.drawString(ML, y, f"{inv_nr}  |  {status_labels.get(inv_status, inv_status)}  |  {fmt_amount}")
            y -= 4.5 * mm
    else:
        c.setFillColor(grey)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(ML, y, "Keine Rechnungen vorhanden")
        y -= 5 * mm

    y -= SECTION_GAP

    # ─── KI-SCREENING ─────────────────────────────────────────────
    y = check_page_break(c, y)
    y = draw_section_title(c, y, f"KI-SCREENING ({len(screenings)})")

    if screenings:
        latest = screenings[0]
        c.setFillColor(dark)
        c.setFont("Helvetica", 7.5)
        is_complete = latest.get("is_complete", False)
        anabin = latest.get("anabin_category", "-")
        lang_ok = latest.get("language_level_ok")
        recommended = latest.get("recommended_stage", "-")
        c.drawString(ML, y, f"Vollstaendigkeit: {'Ja' if is_complete else 'Nein'}  |  Anabin: {anabin}  |  Sprache OK: {'Ja' if lang_ok else 'Nein' if lang_ok is False else '-'}")
        y -= 4 * mm
        c.drawString(ML, y, f"Empfohlener Status: {stage_labels.get(recommended, recommended)}  |  Datum: {fmt_date(latest.get('created_at'))}")
        y -= 4 * mm
        summary = latest.get("summary", "")
        if summary:
            c.setFillColor(grey)
            c.setFont("Helvetica-Oblique", 7)
            if len(summary) > 120:
                summary = summary[:118] + "..."
            c.drawString(ML, y, summary)
            y -= 4 * mm
    else:
        c.setFillColor(grey)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(ML, y, "Kein KI-Screening durchgefuehrt")
        y -= 5 * mm

    y -= SECTION_GAP

    # ─── NOTIZEN ──────────────────────────────────────────────────
    y = check_page_break(c, y)
    y = draw_section_title(c, y, f"INTERNE NOTIZEN ({len(notes)})")

    if notes:
        for n in notes[:8]:
            y = check_page_break(c, y)
            c.setFillColor(dark)
            c.setFont("Helvetica", 7)
            content = n.get("content", "")
            if len(content) > 100:
                content = content[:98] + "..."
            c.drawString(ML, y, content)
            c.setFillColor(grey)
            c.setFont("Helvetica", 6)
            author = n.get("author_name", "")
            date = fmt_date(n.get("created_at"))
            c.drawRightString(MR, y, f"{author}  |  {date}")
            y -= 4.5 * mm
    else:
        c.setFillColor(grey)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(ML, y, "Keine Notizen vorhanden")
        y -= 5 * mm

    # ─── Footer ───────────────────────────────────────────────────
    draw_footer(c)
    c.save()
    buf.seek(0)

    safe_name = applicant_name.replace(" ", "_").replace("/", "_")
    filename = f"Fallakte_{safe_name}_{str(app_doc['_id'])[-6:]}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )



# ─── Duplicate Merge ──────────────────────────────────────────────────────────

@router.post("/merge-duplicates")
async def merge_duplicate_applications(
    data: dict,
    user: dict = Depends(require_roles(*ADMIN_ROLES)),
):
    """
    Pflichtlogik aus 10_funktions_und_modulmatrix: Dublettenprufung → merged.
    Fuehrt zwei Applications zusammen. Die primaere behaelt alle Daten,
    die sekundaere wird als 'merged' archiviert.
    """
    db = get_db()
    primary_id = data.get("primary_id")
    secondary_id = data.get("secondary_id")

    if not primary_id or not secondary_id:
        raise HTTPException(status_code=400, detail="primary_id und secondary_id erforderlich")
    if primary_id == secondary_id:
        raise HTTPException(status_code=400, detail="Primaer und Sekundaer duerfen nicht identisch sein")

    try:
        primary = await db.applications.find_one({"_id": ObjectId(primary_id)})
        secondary = await db.applications.find_one({"_id": ObjectId(secondary_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Ungueltige IDs")

    if not primary or not secondary:
        raise HTTPException(status_code=404, detail="Eine oder beide Applications nicht gefunden")

    now = datetime.now(timezone.utc)

    # 1. Dokumente der sekundaeren Application auf die primaere uebertragen
    moved_docs = await db.documents.update_many(
        {"application_id": secondary_id},
        {"$set": {
            "application_id": primary_id,
            "merged_from": secondary_id,
            "updated_at": now.isoformat(),
        }},
    )

    # 2. Aufgaben uebertragen
    moved_tasks = await db.tasks.update_many(
        {"application_id": secondary_id},
        {"$set": {
            "application_id": primary_id,
            "merged_from": secondary_id,
            "updated_at": now.isoformat(),
        }},
    )

    # 3. Nachrichten/Konversationen uebertragen
    moved_convs = await db.conversations.update_many(
        {"application_id": secondary_id},
        {"$set": {
            "application_id": primary_id,
            "merged_from": secondary_id,
        }},
    )

    # 4. Rechnungen uebertragen
    moved_invs = await db.invoices.update_many(
        {"application_id": secondary_id},
        {"$set": {
            "application_id": primary_id,
            "merged_from": secondary_id,
        }},
    )

    # 5. Sekundaere Application als merged archivieren
    await db.applications.update_one(
        {"_id": ObjectId(secondary_id)},
        {"$set": {
            "current_stage": "archived",
            "duplicate_flag": False,
            "merge_status": "merged_into",
            "merged_into": primary_id,
            "merged_at": now.isoformat(),
            "merged_by": user["id"],
            "updated_by": user["id"],
            "last_activity_at": now,
        }},
    )

    # 6. Primaere Application: Merge-Referenz + Duplikat-Flag entfernen
    await db.applications.update_one(
        {"_id": ObjectId(primary_id)},
        {"$set": {
            "duplicate_flag": False,
            "merge_status": "primary",
            "merged_secondary_ids": [secondary_id],
            "last_activity_at": now,
            "updated_by": user["id"],
        }},
    )

    # 7. Audit
    await write_audit_log(
        "duplicate_merged", user["id"], "application", primary_id,
        {
            "secondary_id": secondary_id,
            "docs_moved": moved_docs.modified_count,
            "tasks_moved": moved_tasks.modified_count,
            "convs_moved": moved_convs.modified_count,
            "invoices_moved": moved_invs.modified_count,
        },
    )

    return {
        "message": "Dubletten zusammengefuehrt",
        "primary_id": primary_id,
        "secondary_id": secondary_id,
        "merged": {
            "documents": moved_docs.modified_count,
            "tasks": moved_tasks.modified_count,
            "conversations": moved_convs.modified_count,
            "invoices": moved_invs.modified_count,
        },
    }


@router.get("/{app_id}/qualification-path")
async def get_qualification_path(app_id: str, user: dict = Depends(get_current_user)):
    """Gibt den berechneten Qualifizierungspfad einer Bewerbung zurueck."""
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id)}, {"_id": 0, "qualification_path": 1, "qualification_path_updated_at": 1})
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    return app.get("qualification_path") or {"recommended_path": "not_computed", "path_label_de": "Noch nicht berechnet", "path_label_en": "Not yet computed"}


@router.post("/{app_id}/compute-qualification")
async def compute_qualification(app_id: str, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Berechnet den Qualifizierungspfad einer Bewerbung neu (Staff-only)."""
    db = get_db()
    app = await db.applications.find_one({"_id": ObjectId(app_id)})
    if not app:
        raise HTTPException(status_code=404, detail="Bewerbung nicht gefunden")
    app_dict = to_str_id(app)
    applicant = await db.users.find_one({"_id": ObjectId(app_dict["applicant_id"])})
    if not applicant:
        raise HTTPException(status_code=404, detail="Bewerber nicht gefunden")
    applicant_dict = to_str_id(dict(applicant))

    from services.anabin_knowledge import lookup_knowledge
    from services.qualification_engine import compute_qualification_path
    anabin = await lookup_knowledge(
        applicant_dict.get("country") or applicant_dict.get("nationality", ""),
        app_dict.get("degree_type"),
        app_id,
    )
    result = await compute_qualification_path(app_dict, applicant_dict, anabin)
    return result


# ═══ Bulk-Aktionen (Staff/Admin) ═══════════════════════════════════════════════

@router.post("/bulk-update")
async def bulk_update_applications(request: Request, user: dict = Depends(require_roles(*STAFF_ROLES))):
    """Bulk-Aktion auf mehrere Bewerbungen: set_stage, assign_staff, set_priority, archive."""
    body = await request.json()
    ids = body.get("ids") or []
    action = body.get("action")
    value = body.get("value")

    if not isinstance(ids, list) or not ids or len(ids) > 100:
        raise HTTPException(status_code=400, detail="ids: 1-100 Bewerbungs-IDs erforderlich")
    if action not in ("set_stage", "assign_staff", "set_priority", "archive"):
        raise HTTPException(status_code=400, detail="Ungueltige action")

    now = datetime.now(timezone.utc)
    update = {"last_activity_at": now}
    if action == "set_stage":
        from services.state_machine import ALL_STAGES
        if value not in ALL_STAGES:
            raise HTTPException(status_code=400, detail=f"Ungueltige Stage: {value}")
        update["current_stage"] = value
    elif action == "archive":
        update["current_stage"] = "archived"
    elif action == "assign_staff":
        db_check = get_db()
        try:
            staff_user = await db_check.users.find_one({"_id": ObjectId(value)}, {"role": 1})
        except Exception:
            raise HTTPException(status_code=400, detail="Ungueltige Staff-ID")
        if not staff_user or staff_user.get("role") not in ("superadmin", "admin", "staff", "accounting_staff", "teacher"):
            raise HTTPException(status_code=400, detail="Staff-Nutzer nicht gefunden")
        update["assigned_staff_id"] = value
    elif action == "set_priority":
        if value not in ("low", "normal", "high", "urgent"):
            raise HTTPException(status_code=400, detail="Ungueltige Prioritaet")
        update["priority"] = value

    oids = []
    for i in ids:
        try:
            oids.append(ObjectId(i))
        except Exception:
            continue
    if not oids:
        raise HTTPException(status_code=400, detail="Keine gueltigen IDs")

    db = get_db()
    res = await db.applications.update_many({"_id": {"$in": oids}}, {"$set": update})

    activity_docs = [{
        "application_id": str(oid),
        "action": f"bulk_{action}",
        "old_value": None,
        "new_value": str(value) if value else action,
        "actor_id": user["id"],
        "actor_name": user.get("full_name", user.get("email", "")),
        "occurred_at": now,
    } for oid in oids]
    if activity_docs:
        await db.application_activities.insert_many(activity_docs)

    await write_audit_log("applications_bulk_update", user["id"], "application", "bulk",
                          {"action": action, "value": str(value), "count": res.modified_count})
    return {"updated": res.modified_count, "action": action}
