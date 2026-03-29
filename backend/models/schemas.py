"""
Shared Pydantic schemas and helper utilities.
"""
from typing import Optional, List
from pydantic import BaseModel


# ─── Helpers ─────────────────────────────────────────────────────────────────
def to_str_id(doc: dict) -> dict:
    """Convert MongoDB _id to string id in-place."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


# ─── Auth schemas ─────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    invite_token: Optional[str] = None


class InviteRequest(BaseModel):
    email: str
    full_name: str
    role: str
    workspace_id: Optional[str] = None
    organization_id: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# ─── Application schemas ──────────────────────────────────────────────────────
class ApplicationCreate(BaseModel):
    applicant_id: Optional[str] = None
    workspace_id: str
    source: str = "direct"
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    current_stage: Optional[str] = None
    assigned_staff_id: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    # Editable case fields (Staff/Admin only)
    course_type: Optional[str] = None
    desired_start: Optional[str] = None
    language_level: Optional[str] = None
    degree_country: Optional[str] = None
    combo_option: Optional[str] = None
    source: Optional[str] = None
    date_of_birth: Optional[str] = None


class CaseNoteCreate(BaseModel):
    content: str
    visibility: str = "internal"  # internal | shared


class CaseEmailSend(BaseModel):
    subject: str
    body: str
    lang: str = "de"


# ─── Document schemas ─────────────────────────────────────────────────────────
class DocumentStatusUpdate(BaseModel):
    status: str  # in_review | approved | rejected | superseded
    rejection_reason: Optional[str] = None
    comment: Optional[str] = None


# ─── Lead schemas ─────────────────────────────────────────────────────────────
class LeadDocumentUpload(BaseModel):
    """Inline document upload within a lead submission."""
    document_type: str  # language_certificate | highschool_diploma | passport | other
    filename: str
    content_type: str = "application/octet-stream"
    file_data: Optional[str] = None  # base64 encoded


class LeadIngest(BaseModel):
    # Personal data
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    country: Optional[str] = None
    # Account creation (Bewerbung + Registrierung gekoppelt)
    password: Optional[str] = None  # wenn gesetzt, wird ein Account erstellt
    # Application specifics
    area_interest: str = "studienkolleg"
    course_type: Optional[str] = None       # M-Course | T-Course | W-Course | M/T-Course | Language Course
    desired_start: Optional[str] = None     # Winter Semester 2026/27 etc.
    combo_option: Optional[str] = None      # additional combo course
    language_level: Optional[str] = None   # A1 | A2 | B1 | B2 | C1 | C2
    degree_country: Optional[str] = None   # country where last degree was obtained
    notes: Optional[str] = None
    source: str = "website_form"
    referral_code: Optional[str] = None
    # Inline document uploads (optional)
    documents: Optional[List[LeadDocumentUpload]] = None


# ─── Followup / Wiedervorlage schemas ─────────────────────────────────────────
class FollowupCreate(BaseModel):
    application_id: str
    due_date: str
    reason: str
    assigned_to: Optional[str] = None


class FollowupUpdate(BaseModel):
    status: Optional[str] = None  # pending | done | dismissed
    due_date: Optional[str] = None
    reason: Optional[str] = None


# ─── Task schemas ─────────────────────────────────────────────────────────────
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    application_id: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "normal"
    visibility: str = "internal"


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


# ─── Workspace schemas ────────────────────────────────────────────────────────
class WorkspaceCreate(BaseModel):
    name: str
    area: str
    description: Optional[str] = None


# ─── Messaging schemas ────────────────────────────────────────────────────────
class MessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    recipient_id: Optional[str] = None
    application_id: Optional[str] = None
    content: str
    visibility: str = "public"


# ─── Consent schema ───────────────────────────────────────────────────────────
class ConsentCapture(BaseModel):
    consent_type: str
    version: str = "1.0"
    granted: bool = True


# ─── User update schema ───────────────────────────────────────────────────────
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    language_pref: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    # Admin-only fields (enforced in route):
    role: Optional[str] = None
    active: Optional[bool] = None
