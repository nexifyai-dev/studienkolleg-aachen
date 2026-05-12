"""
Iteration 107 - Pre-GO-LIVE Regression
Tests new endpoints: /api/system/seed-demo-data, /api/system/clean-demo-data
Verifies storage_backend='emergent' in /api/health
Smoke tests core APIs across 5 roles.
"""
import os
import io
import time
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

CREDS = {
    "admin": ("admin@studienkolleg-aachen.de", "Admin@2026!"),
    "staff": ("staff@studienkolleg-aachen.de", "DevSeed@2026!"),
    "teacher": ("teacher@studienkolleg-aachen.de", "DevSeed@2026!"),
    "applicant": ("applicant@studienkolleg-aachen.de", "DevSeed@2026!"),
    "partner": ("partner@studienkolleg-aachen.de", "DevSeed@2026!"),
}


def _new_session():
    s = requests.Session()
    # bootstrap CSRF
    s.get(f"{BASE_URL}/api/health", timeout=15)
    return s


def _csrf_headers(s):
    token = s.cookies.get("csrf_token")
    return {"x-csrf-token": token} if token else {}


def login(role):
    s = _new_session()
    email, pw = CREDS[role]
    r = s.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": pw},
        headers={"Content-Type": "application/json", **_csrf_headers(s)},
        timeout=20,
    )
    assert r.status_code == 200, f"login {role} -> {r.status_code} {r.text[:200]}"
    return s


# ───────────────────────── HEALTH ─────────────────────────
def test_health_storage_backend_emergent():
    r = requests.get(f"{BASE_URL}/api/health", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert data.get("storage_backend") == "emergent", f"got {data.get('storage_backend')}"


# ───────────────────────── AUTH 5 ROLES ─────────────────────────
@pytest.mark.parametrize("role", list(CREDS.keys()))
def test_auth_login_me_logout(role):
    s = login(role)
    me = s.get(f"{BASE_URL}/api/auth/me", timeout=15)
    assert me.status_code == 200
    assert me.json().get("email") == CREDS[role][0]
    # logout
    r = s.post(f"{BASE_URL}/api/auth/logout", headers=_csrf_headers(s), timeout=15)
    assert r.status_code in (200, 204)


# ───────────────────────── CSRF ENFORCEMENT ─────────────────────────
def test_csrf_blocks_post_without_token():
    # Login is intentionally CSRF-exempt (no prior session). Use a state-changing
    # admin endpoint instead to verify CSRF enforcement on authenticated POST.
    s = login("admin")
    r = s.post(f"{BASE_URL}/api/system/seed-demo-data", timeout=30)  # NO csrf header
    assert r.status_code in (401, 403), f"CSRF expected reject, got {r.status_code}"


# ───────────────────────── SEED / CLEAN DEMO ─────────────────────────
def test_seed_demo_data_admin_only():
    s = login("admin")
    r = s.post(f"{BASE_URL}/api/system/seed-demo-data", headers=_csrf_headers(s), timeout=120)
    assert r.status_code == 200, r.text[:300]
    data = r.json()
    summary = data.get("summary", {})
    assert summary.get("total_users", 0) >= 5
    assert summary.get("total_applications", 0) >= 12
    # tasks may already exist - either created>0 or some still present
    assert summary.get("total_tasks", 0) >= 1


def test_seed_demo_data_idempotent():
    s = login("admin")
    r1 = s.post(f"{BASE_URL}/api/system/seed-demo-data", headers=_csrf_headers(s), timeout=120)
    assert r1.status_code == 200
    users_after_first = r1.json()["summary"]["total_users"]
    apps_after_first = r1.json()["summary"]["total_applications"]
    r2 = s.post(f"{BASE_URL}/api/system/seed-demo-data", headers=_csrf_headers(s), timeout=120)
    assert r2.status_code == 200
    users_after_second = r2.json()["summary"]["total_users"]
    apps_after_second = r2.json()["summary"]["total_applications"]
    assert users_after_second == users_after_first, "users duplicated"
    assert apps_after_second == apps_after_first, "applications duplicated"


def test_seed_demo_data_forbidden_for_non_admin():
    s = login("staff")
    r = s.post(f"{BASE_URL}/api/system/seed-demo-data", headers=_csrf_headers(s), timeout=30)
    assert r.status_code == 403, f"staff should not seed, got {r.status_code}"

    s2 = login("applicant")
    r2 = s2.post(f"{BASE_URL}/api/system/seed-demo-data", headers=_csrf_headers(s2), timeout=30)
    assert r2.status_code == 403


def test_clean_demo_data_forbidden_for_non_admin():
    s = login("staff")
    r = s.post(f"{BASE_URL}/api/system/clean-demo-data", headers=_csrf_headers(s), timeout=30)
    assert r.status_code == 403


# ───────────────────────── APPLICATIONS ─────────────────────────
def test_applications_list_for_staff():
    s = login("staff")
    r = s.get(f"{BASE_URL}/api/applications", timeout=20)
    assert r.status_code == 200
    apps = r.json()
    assert isinstance(apps, list)
    assert len(apps) >= 1, "expect demo applications after seeding"


# ───────────────────────── DOCUMENT UPLOAD/DOWNLOAD (emergent storage) ───
def test_document_upload_download_emergent_storage():
    s = login("admin")
    apps_r = s.get(f"{BASE_URL}/api/applications", timeout=15)
    assert apps_r.status_code == 200 and apps_r.json(), "no applications to attach doc"
    app_id = apps_r.json()[0]["id"]

    pdf_bytes = b"%PDF-1.4\n%test\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    files = {"file": ("test_iter107.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    data = {"document_type": "passport"}
    r = s.post(
        f"{BASE_URL}/api/applications/{app_id}/documents/upload",
        files=files, data=data,
        headers=_csrf_headers(s), timeout=60,
    )
    assert r.status_code in (200, 201), f"upload failed {r.status_code} {r.text[:300]}"
    doc = r.json()
    doc_id = doc.get("id") or doc.get("document_id") or doc.get("_id")
    assert doc_id, f"no doc id returned: {doc}"

    # download
    time.sleep(0.5)
    dl = s.get(f"{BASE_URL}/api/documents/{doc_id}/download", timeout=30)
    assert dl.status_code == 200, f"download {dl.status_code}"
    assert len(dl.content) > 10
    # iframe-friendly headers
    assert dl.headers.get("X-Frame-Options", "").upper() != "DENY"


# ───────────────────────── TASKS / INVOICES / MESSAGES / NOTIFS ─────────
def test_tasks_list():
    s = login("staff")
    r = s.get(f"{BASE_URL}/api/tasks", timeout=15)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_invoices_list():
    s = login("staff")
    r = s.get(f"{BASE_URL}/api/invoices", timeout=15)
    assert r.status_code == 200


def test_conversations_list():
    s = login("staff")
    r = s.get(f"{BASE_URL}/api/conversations", timeout=15)
    assert r.status_code == 200


def test_notifications_list():
    s = login("applicant")
    r = s.get(f"{BASE_URL}/api/notifications", timeout=15)
    assert r.status_code == 200


# ───────────────────────── DASHBOARD STATS PER ROLE ─────────────────────
@pytest.mark.parametrize("role", ["admin", "staff", "teacher", "applicant", "partner"])
def test_dashboard_stats(role):
    s = login(role)
    r = s.get(f"{BASE_URL}/api/dashboard/stats", timeout=20)
    assert r.status_code == 200, f"{role} dashboard {r.status_code}"


# ───────────────────────── AUDIT LOGS / GDPR ─────────────────────────────
def test_audit_logs_admin():
    s = login("admin")
    r = s.get(f"{BASE_URL}/api/audit-logs", timeout=15)
    # endpoint may be /api/audit/logs or /api/audit-logs
    if r.status_code == 404:
        r = s.get(f"{BASE_URL}/api/audit/logs", timeout=15)
    assert r.status_code == 200, f"audit logs {r.status_code}"


def test_gdpr_user_data():
    s = login("applicant")
    r = s.get(f"{BASE_URL}/api/gdpr/user-data", timeout=20)
    assert r.status_code in (200, 404), f"gdpr user-data {r.status_code}"


# ───────────────────────── SECURITY HEADERS ─────────────────────────────
def test_security_headers_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=15)
    h = {k.lower(): v for k, v in r.headers.items()}
    assert "x-content-type-options" in h
    assert h.get("x-content-type-options", "").lower() == "nosniff"
    assert "referrer-policy" in h


# ───────────────────────── STRIPE CHECKOUT ─────────────────────────────
def test_stripe_checkout_init():
    s = login("admin")
    # ensure we have an unpaid invoice; if none, skip
    inv_r = s.get(f"{BASE_URL}/api/invoices", timeout=15)
    if inv_r.status_code != 200:
        pytest.skip("invoices not accessible")
    invs = inv_r.json()
    if not invs:
        pytest.skip("no invoices to test stripe")
    inv_id = invs[0].get("id") or invs[0].get("_id")
    r = s.post(
        f"{BASE_URL}/api/payments/stripe/create-checkout",
        json={"invoice_id": inv_id},
        headers={"Content-Type": "application/json", **_csrf_headers(s)},
        timeout=30,
    )
    # 200 or 400 acceptable (e.g. already paid); 500 not
    assert r.status_code in (200, 400, 404), f"stripe checkout {r.status_code} {r.text[:200]}"
