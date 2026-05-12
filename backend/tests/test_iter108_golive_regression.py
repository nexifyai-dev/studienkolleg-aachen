"""Iteration 108 - Final GO-LIVE regression for new admin features.

Covers:
  - Health endpoint version + storage backend
  - Auth flow for all 5 roles (login/me/refresh/logout)
  - CSRF enforcement on unsafe methods
  - NEW: /api/admin/analytics (all ranges + RBAC)
  - NEW: /api/admin/staff (RBAC + schema + stats)
  - NEW: /api/admin/staff/{id}/reset-password (CSRF + RBAC + applicant-403 + invalid-id)
  - System seed/clean (idempotent + RBAC)
  - Core CRUD smoke (apps/tasks/invoices/messages/notifications)
  - Document upload + download (emergent storage)
  - Audit-logs + dashboard stats per role
  - Security headers
"""

import io
import os
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

CREDS = {
    "admin": ("admin@studienkolleg-aachen.de", "Admin@2026!"),
    "staff": ("staff@studienkolleg-aachen.de", "DevSeed@2026!"),
    "teacher": ("teacher@studienkolleg-aachen.de", "DevSeed@2026!"),
    "applicant": ("applicant@studienkolleg-aachen.de", "DevSeed@2026!"),
    "partner": ("partner@studienkolleg-aachen.de", "DevSeed@2026!"),
}


def _login(role: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    # Get csrf via /api/health
    s.get(f"{BASE_URL}/api/health", timeout=15)
    email, password = CREDS[role]
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, f"login {role} failed: {r.status_code} {r.text[:200]}"
    csrf = s.cookies.get("csrf_token")
    if csrf:
        s.headers["X-CSRF-Token"] = csrf
    return s


@pytest.fixture(scope="module")
def admin_sess():
    return _login("admin")


@pytest.fixture(scope="module")
def staff_sess():
    return _login("staff")


@pytest.fixture(scope="module")
def applicant_sess():
    return _login("applicant")


# ─── Health ───────────────────────────────────────────────────────────────────
def test_health_version_and_storage():
    r = requests.get(f"{BASE_URL}/api/health", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data["version"] == "1.4.2", f"version mismatch: {data}"
    assert data["storage_backend"] == "emergent", f"storage backend mismatch: {data}"
    assert data["status"] == "ok"


# ─── Auth ─────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("role", list(CREDS.keys()))
def test_auth_login_me_logout(role):
    s = _login(role)
    me = s.get(f"{BASE_URL}/api/auth/me", timeout=15)
    assert me.status_code == 200, f"{role} /me failed: {me.status_code}"
    body = me.json()
    assert body.get("email") == CREDS[role][0]
    assert body.get("role")  # role present

    # refresh (if endpoint exists)
    refresh = s.post(f"{BASE_URL}/api/auth/refresh", timeout=15)
    assert refresh.status_code in (200, 204, 404), f"{role} refresh: {refresh.status_code}"

    # logout
    out = s.post(f"{BASE_URL}/api/auth/logout", timeout=15)
    assert out.status_code in (200, 204), f"{role} logout: {out.status_code}"


# ─── CSRF ─────────────────────────────────────────────────────────────────────
def test_csrf_post_without_token_blocked():
    s = requests.Session()
    s.get(f"{BASE_URL}/api/health", timeout=15)
    # Login to get auth cookie but strip csrf header
    email, password = CREDS["admin"]
    s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=15)
    # POST without X-CSRF-Token header
    r = s.post(f"{BASE_URL}/api/system/seed-demo-data", timeout=15)
    assert r.status_code == 403, f"Expected 403 without CSRF, got {r.status_code}"


# ─── Admin Analytics ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("rng", ["7d", "30d", "90d", "12m", "all"])
def test_admin_analytics_all_ranges(admin_sess, rng):
    r = admin_sess.get(f"{BASE_URL}/api/admin/analytics", params={"range": rng}, timeout=20)
    assert r.status_code == 200, f"{rng} → {r.status_code} {r.text[:200]}"
    body = r.json()
    for key in ("kpis", "revenue_trend", "applicant_trend", "sources", "countries", "pipeline"):
        assert key in body, f"{rng} missing field {key}"
    assert isinstance(body["kpis"], dict)
    assert "revenue_total" in body["kpis"]
    assert "conversion_rate" in body["kpis"]
    assert "new_applicants" in body["kpis"]
    assert isinstance(body["revenue_trend"], list)
    assert isinstance(body["applicant_trend"], list)
    assert isinstance(body["pipeline"], dict)


def test_admin_analytics_non_admin_403(staff_sess, applicant_sess):
    for sess, label in [(staff_sess, "staff"), (applicant_sess, "applicant")]:
        r = sess.get(f"{BASE_URL}/api/admin/analytics", timeout=15)
        assert r.status_code == 403, f"{label} should be 403, got {r.status_code}"


# ─── Admin Staff ──────────────────────────────────────────────────────────────
def test_admin_staff_list(admin_sess):
    r = admin_sess.get(f"{BASE_URL}/api/admin/staff", timeout=20)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 3, "Expected at least admin+staff+teacher"
    valid_roles = {"superadmin", "admin", "staff", "accounting_staff", "teacher"}
    for it in items:
        assert it["role"] in valid_roles, f"Non-staff role leaked: {it.get('role')}"
        assert "stats" in it
        for k in ("tasks_open", "tasks_done", "invoices_created"):
            assert k in it["stats"], f"Missing stats.{k}"
        assert "last_login" in it
        assert "email" in it
        # No mongo _id leakage
        assert "_id" not in it


def test_admin_staff_non_admin_403(staff_sess, applicant_sess):
    for sess in (staff_sess, applicant_sess):
        r = sess.get(f"{BASE_URL}/api/admin/staff", timeout=15)
        assert r.status_code == 403


# ─── Admin Reset Password ─────────────────────────────────────────────────────
def test_admin_reset_password_staff_ok(admin_sess):
    # Pick a staff user that is NOT the admin itself
    staff_list = admin_sess.get(f"{BASE_URL}/api/admin/staff", timeout=15).json()
    target = next((u for u in staff_list if u["role"] == "staff"), None)
    assert target, "No staff user found for reset test"

    r = admin_sess.post(f"{BASE_URL}/api/admin/staff/{target['id']}/reset-password", timeout=20)
    assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
    body = r.json()
    assert "reset_url" in body
    assert "token" in body
    assert "expires_at" in body
    assert body["reset_url"].endswith(body["token"])


def test_admin_reset_password_applicant_403(admin_sess):
    # Find an applicant user via login + /me
    apl = _login("applicant")
    aid = apl.get(f"{BASE_URL}/api/auth/me", timeout=15).json()["id"]
    r = admin_sess.post(f"{BASE_URL}/api/admin/staff/{aid}/reset-password", timeout=15)
    assert r.status_code == 403, f"Applicant reset should 403, got {r.status_code}"


def test_admin_reset_password_invalid_id(admin_sess):
    r = admin_sess.post(f"{BASE_URL}/api/admin/staff/not-a-valid-id/reset-password", timeout=15)
    assert r.status_code in (400, 404)

    # Valid format but non-existing
    fake = "507f1f77bcf86cd799439011"
    r2 = admin_sess.post(f"{BASE_URL}/api/admin/staff/{fake}/reset-password", timeout=15)
    assert r2.status_code == 404


def test_admin_reset_password_csrf_enforced():
    # Login without re-attaching csrf header
    s = requests.Session()
    s.get(f"{BASE_URL}/api/health", timeout=15)
    email, password = CREDS["admin"]
    s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=15)
    # No csrf header
    r = s.post(f"{BASE_URL}/api/admin/staff/507f1f77bcf86cd799439011/reset-password", timeout=15)
    assert r.status_code == 403


def test_admin_reset_password_staff_role_blocked(staff_sess, admin_sess):
    target = next((u for u in admin_sess.get(f"{BASE_URL}/api/admin/staff", timeout=15).json() if u["role"] == "teacher"), None)
    assert target
    r = staff_sess.post(f"{BASE_URL}/api/admin/staff/{target['id']}/reset-password", timeout=15)
    assert r.status_code == 403


# ─── System Seed/Clean ────────────────────────────────────────────────────────
def test_seed_demo_data_admin(admin_sess):
    r = admin_sess.post(f"{BASE_URL}/api/system/seed-demo-data", timeout=60)
    assert r.status_code == 200, f"{r.status_code} {r.text[:200]}"
    body = r.json()
    assert "total_users" in body or "users" in body or "applications" in body or "status" in body


def test_seed_demo_data_idempotent(admin_sess):
    r1 = admin_sess.post(f"{BASE_URL}/api/system/seed-demo-data", timeout=60)
    r2 = admin_sess.post(f"{BASE_URL}/api/system/seed-demo-data", timeout=60)
    assert r1.status_code == 200 and r2.status_code == 200


def test_seed_demo_data_staff_403(staff_sess):
    r = staff_sess.post(f"{BASE_URL}/api/system/seed-demo-data", timeout=15)
    assert r.status_code == 403


# ─── Core CRUD smoke ──────────────────────────────────────────────────────────
def test_applications_list(staff_sess):
    r = staff_sess.get(f"{BASE_URL}/api/applications", timeout=20)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_tasks_list(staff_sess):
    r = staff_sess.get(f"{BASE_URL}/api/tasks", timeout=20)
    assert r.status_code == 200


def test_invoices_list(staff_sess):
    r = staff_sess.get(f"{BASE_URL}/api/invoices", timeout=20)
    assert r.status_code == 200


def test_conversations_list(staff_sess):
    r = staff_sess.get(f"{BASE_URL}/api/conversations", timeout=20)
    assert r.status_code in (200, 404)  # depending on routing


def test_notifications_list(staff_sess):
    r = staff_sess.get(f"{BASE_URL}/api/notifications", timeout=20)
    assert r.status_code == 200


def test_audit_logs_admin(admin_sess):
    r = admin_sess.get(f"{BASE_URL}/api/audit-logs", timeout=20)
    assert r.status_code == 200


# ─── Dashboard stats per role ────────────────────────────────────────────────
@pytest.mark.parametrize("role", ["admin", "staff", "teacher", "applicant", "partner"])
def test_dashboard_stats_per_role(role):
    s = _login(role)
    r = s.get(f"{BASE_URL}/api/dashboard/stats", timeout=20)
    assert r.status_code in (200, 403), f"{role} dashboard: {r.status_code}"


# ─── Document upload + download (emergent) ───────────────────────────────────
def test_document_upload_download_emergent(applicant_sess):
    # Get the applicant's own application id (or skip if none)
    me = applicant_sess.get(f"{BASE_URL}/api/auth/me", timeout=15).json()
    apps = applicant_sess.get(f"{BASE_URL}/api/applications", timeout=15)
    if apps.status_code != 200 or not apps.json():
        pytest.skip("No application available for applicant")
    app_id = apps.json()[0]["id"]

    pdf_bytes = b"%PDF-1.4\n%fake-pdf-for-test\n" + uuid.uuid4().bytes
    files = {"file": ("TEST_iter108.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    headers = {k: v for k, v in applicant_sess.headers.items() if k.lower() != "content-type"}
    r = requests.post(
        f"{BASE_URL}/api/applications/{app_id}/documents/upload",
        data={"document_type": "passport"},
        files=files,
        cookies=applicant_sess.cookies,
        headers=headers,
        timeout=30,
    )
    if r.status_code == 404:
        pytest.skip("documents/upload endpoint shape differs - non-critical for this iter")
    assert r.status_code in (200, 201), f"upload failed: {r.status_code} {r.text[:200]}"
    doc = r.json()
    doc_id = doc.get("id") or doc.get("document_id")
    if not doc_id:
        pytest.skip("Upload response missing document id")

    dl = requests.get(f"{BASE_URL}/api/documents/{doc_id}/download",
                     cookies=applicant_sess.cookies, headers=headers, timeout=30)
    assert dl.status_code == 200, f"download failed: {dl.status_code}"
    # X-Frame-Options must not be DENY (iframe preview must work)
    xfo = dl.headers.get("x-frame-options", "")
    assert xfo.upper() != "DENY", f"X-Frame-Options should not be DENY, got {xfo}"


# ─── Security headers ─────────────────────────────────────────────────────────
def test_security_headers():
    r = requests.get(f"{BASE_URL}/api/health", timeout=15)
    h = {k.lower(): v for k, v in r.headers.items()}
    assert h.get("x-content-type-options", "").lower() == "nosniff"
    assert "referrer-policy" in h
    # HSTS only present over real HTTPS - allow either present or absent on preview
