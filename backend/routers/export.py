"""
Export router – CSV export for applications.
Staff-only access.
"""
import csv
import io
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from database import get_db
from deps import require_roles, STAFF_ROLES

router = APIRouter(prefix="/api/export", tags=["export"])

STAGE_LABELS = {
    "lead_new": "Neue Anfrage",
    "screening": "AI-Screening",
    "in_review": "In Prüfung",
    "pending_docs": "Docs ausstehend",
    "interview_scheduled": "Beratung geplant",
    "conditional_offer": "Bedingte Zusage",
    "offer_sent": "Angebot versendet",
    "enrolled": "Eingeschrieben",
    "on_hold": "Zurückgestellt",
    "declined": "Abgelehnt",
    "completed": "Abgeschlossen",
    "archived": "Archiviert",
}


@router.get("/applications")
async def export_applications(
    stage: str = Query(None, description="Filter by stage"),
    user: dict = Depends(require_roles(*STAFF_ROLES)),
):
    db = get_db()
    query = {}
    if stage:
        query["current_stage"] = stage

    apps = await db.applications.find(query).sort("created_at", -1).to_list(5000)

    # Resolve applicant names
    user_ids = list(set(a.get("applicant_id") for a in apps if a.get("applicant_id")))
    from bson import ObjectId
    users = {}
    for uid in user_ids:
        try:
            u = await db.users.find_one({"_id": ObjectId(uid)}, {"_id": 0, "full_name": 1, "email": 1, "phone": 1, "country": 1})
            if u:
                users[uid] = u
        except Exception:
            pass

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow([
        "Name", "E-Mail", "Telefon", "Land", "Kurs", "Semester",
        "Sprachniveau", "Status", "Erstellt am", "Letzte Aktivität",
    ])

    for app in apps:
        uid = app.get("applicant_id", "")
        u = users.get(uid, {})
        created = app.get("created_at")
        last_act = app.get("last_activity_at")
        writer.writerow([
            u.get("full_name", ""),
            u.get("email", ""),
            u.get("phone", ""),
            u.get("country", ""),
            app.get("course_type", ""),
            app.get("desired_start", ""),
            app.get("language_level", ""),
            STAGE_LABELS.get(app.get("current_stage", ""), app.get("current_stage", "")),
            created.strftime("%d.%m.%Y %H:%M") if hasattr(created, "strftime") else str(created or ""),
            last_act.strftime("%d.%m.%Y %H:%M") if hasattr(last_act, "strftime") else str(last_act or ""),
        ])

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"bewerbungen_export_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
