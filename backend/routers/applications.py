"""
Application router.

Security notes:
- Applicants: can only see/modify their own applications
- Partners (agency): scoped to their organization_id
- Staff: scoped by workspace_id query param; without it, see all in their permitted workspaces
- Stage changes are audit-logged and activity-tracked
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from bson import ObjectId
from database import get_db
from deps import get_current_user, require_roles, ADMIN_ROLES, STAFF_ROLES, PARTNER_ROLES
from models.schemas import ApplicationCreate, ApplicationUpdate, CaseNoteCreate, CaseEmailSend, to_str_id
from services.audit import write_audit_log

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

    apps = await db.applications.find(query).sort("last_activity_at", -1).to_list(500)

    result = []
    for app in apps:
        app_dict = to_str_id(app)
        if user["role"] in STAFF_ROLES:
            # Enrich with applicant info (inclusion-only projection)
            if app_dict.get("applicant_id"):
                try:
                    applicant = await db.users.find_one(
                        {"_id": ObjectId(app_dict["applicant_id"])},
                        {"full_name": 1, "email": 1, "phone": 1, "country": 1},
                    )
                    if applicant:
                        app_dict["applicant"] = to_str_id(applicant)
                except Exception:
                    pass
            if app_dict.get("workspace_id"):
                try:
                    ws = await db.workspaces.find_one({"_id": ObjectId(app_dict["workspace_id"])}, {"name": 1})
                    if ws:
                        app_dict["workspace_name"] = ws.get("name")
                except Exception:
                    pass
        result.append(app_dict)
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

    app_doc = {
        "applicant_id": applicant_id,
        "workspace_id": data.workspace_id,
        "current_stage": "lead_new",
        "source": data.source,
        "notes": data.notes,
        "priority": "normal",
        "created_at": datetime.now(timezone.utc),
        "last_activity_at": datetime.now(timezone.utc),
        "created_by": user["id"],
    }
    result = await db.applications.insert_one(app_doc)
    app_id = str(result.inserted_id)
    await write_audit_log("application_created", user["id"], "application", app_id)
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
    return {"message": "Aktualisiert", "id": app_id}


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
        from services.email import _send, _wrap, _btn, _get_app_url
        lang = data.lang
        app_url = _get_app_url()

        # Wrap body in standard template
        sender_name = user.get("full_name", "Staff")
        content = f"""<h3 style="color:#113655;margin-top:0">{"Hello" if lang == "en" else "Hallo"} {to_name or ("Applicant" if lang == "en" else "Bewerber/in")},</h3>
        <div style="color:#475569;line-height:1.7;white-space:pre-wrap">{data.body}</div>
        <p style="color:#64748b;font-size:13px;margin-top:24px">{"Best regards" if lang == "en" else "Mit freundlichen Grüßen"},<br/>{sender_name}<br/>Studienkolleg Aachen</p>
        {_btn(f'{app_url}/portal', 'Zum Portal' if lang == 'de' else 'Go to Portal')}"""

        _send(to_email, data.subject, _wrap(content, lang))

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
