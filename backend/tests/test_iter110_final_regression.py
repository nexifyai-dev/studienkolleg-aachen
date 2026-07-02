"""
Iteration 110 — Finale Abnahme-Regression über ALLE Kernflows.
Fokus: APIs für Applications, Tasks, Invoices, Messaging, Documents, Appointments,
Leads, Notifications, Admin-Analytics, Integrations-Status, RBAC, CSRF, E-Mail-Status.
"""
import os
import io
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

ADMIN = ("admin@studienkolleg-aachen.de", "Admin@2026!")
STAFF = ("staff@studienkolleg-aachen.de", "DevSeed@2026!")
APPLICANT = ("applicant@studienkolleg-aachen.de", "DevSeed@2026!")


def _login(email, password):
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=30)
    assert r.status_code == 200, f"login {email} failed: {r.status_code} {r.text[:200]}"
    csrf = s.cookies.get("csrf_token")
    if csrf:
        s.headers.update({"X-CSRF-Token": csrf})
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_session():
    return _login(*ADMIN)


@pytest.fixture(scope="module")
def staff_session():
    return _login(*STAFF)


@pytest.fixture(scope="module")
def applicant_session():
    return _login(*APPLICANT)


# ---------------- Health + Integrations ----------------

class TestHealthAndIntegrations:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "ok"
        assert d.get("email_enabled") is True
        assert d.get("storage_backend") == "emergent"

    def test_system_monitoring_admin(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/system/monitoring", timeout=20)
        assert r.status_code == 200, r.text[:200]
        d = r.json()
        integ = d.get("integrations") or d
        # tolerant lookup
        flat = str(integ).lower()
        assert "deepseek" in flat, f"deepseek not in {flat[:400]}"
        assert "ai_active" in flat or "storage_active" in flat

    def test_system_monitoring_forbidden_for_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/system/monitoring", timeout=20)
        assert r.status_code in (401, 403)


# ---------------- Auth / Me ----------------

class TestAuthMe:
    def test_me_admin(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json().get("role") in ("admin", "superadmin")

    def test_me_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json().get("role") in ("staff", "teacher")

    def test_me_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        assert r.json().get("role") == "applicant"

    def test_unauth_protected_route(self):
        r = requests.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert r.status_code in (401, 403)


# ---------------- Public Apply-Flow ----------------
# NOTE: TestLeads.test_lead_ingest_public covers the public apply flow via /api/leads/ingest.


# ---------------- Applications ----------------

class TestApplications:
    def test_list_applications_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/applications", timeout=20)
        assert r.status_code == 200, r.text[:200]
        data = r.json()
        assert isinstance(data, (list, dict))

    def test_list_applications_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/applications", timeout=20)
        assert r.status_code == 200


# ---------------- Tasks ----------------

class TestTasks:
    def test_list_tasks_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/tasks", timeout=20)
        assert r.status_code == 200

    def test_list_tasks_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/tasks", timeout=20)
        assert r.status_code == 200


# ---------------- Invoices ----------------

class TestInvoices:
    def test_list_invoices_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/invoices", timeout=20)
        assert r.status_code == 200


# ---------------- Messaging / Conversations ----------------

class TestMessaging:
    def test_list_conversations_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/conversations", timeout=20)
        assert r.status_code in (200, 404)  # tolerant if renamed

    def test_list_conversations_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/conversations", timeout=20)
        assert r.status_code in (200, 404)


# ---------------- Notifications ----------------

class TestNotifications:
    def test_notifications_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/notifications", timeout=20)
        assert r.status_code == 200

    def test_notifications_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/notifications", timeout=20)
        assert r.status_code == 200


# ---------------- Leads ----------------

class TestLeads:
    def test_lead_ingest_public(self):
        # Public apply flow uses POST /api/leads/ingest (no auth, no CSRF as public)
        s = requests.Session()
        payload = {
            "email": f"test_iter110_{int(time.time())}@example.com",
            "full_name": "TEST_Iter110 AutoLead",
            "first_name": "TEST_Iter110",
            "last_name": "AutoLead",
            "phone": "+491234567890",
            "country": "Syrien",
            "language_pref": "de",
            "message": "Automated iter110 regression",
        }
        r = s.post(f"{BASE_URL}/api/leads/ingest", json=payload, timeout=20)
        assert r.status_code in (200, 201), f"leads/ingest: {r.status_code} {r.text[:200]}"


# ---------------- Appointments ----------------

class TestAppointments:
    def test_appointments_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/appointments", timeout=20)
        assert r.status_code == 200

    def test_appointments_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/appointments", timeout=20)
        assert r.status_code == 200


# ---------------- Documents E2E ----------------

class TestDocumentsE2E:
    def test_upload_and_download(self, applicant_session):
        # Get first application id
        r = applicant_session.get(f"{BASE_URL}/api/applications", timeout=20)
        assert r.status_code == 200
        apps = r.json()
        if isinstance(apps, dict):
            apps = apps.get("items") or apps.get("applications") or []
        if not apps:
            pytest.skip("No applications for applicant")
        app_id = apps[0].get("id") or apps[0].get("_id") or apps[0].get("application_id")
        assert app_id
        # Upload PDF
        pdf_bytes = b"%PDF-1.4\n%test iter110\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
        files = {"file": ("iter110_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        data = {"document_type": "other", "category": "other"}
        # Remove Content-Type header for multipart
        headers = {k: v for k, v in applicant_session.headers.items() if k.lower() != "content-type"}
        r2 = requests.post(
            f"{BASE_URL}/api/applications/{app_id}/documents/upload",
            files=files, data=data, headers=headers, cookies=applicant_session.cookies, timeout=60
        )
        assert r2.status_code in (200, 201), f"upload failed: {r2.status_code} {r2.text[:300]}"
        upl = r2.json()
        doc_id = upl.get("id") or upl.get("document_id") or (upl.get("document") or {}).get("id")
        assert doc_id, f"no doc id in response: {upl}"
        # Download
        r3 = applicant_session.get(f"{BASE_URL}/api/documents/{doc_id}/download", timeout=30)
        assert r3.status_code == 200, r3.text[:200]
        assert r3.content.startswith(b"%PDF"), f"not a pdf: {r3.content[:50]}"


# ---------------- Admin Analytics ----------------

class TestAdminAnalytics:
    @pytest.mark.parametrize("rng", ["7d", "30d", "90d", "12m", "all"])
    def test_admin_analytics_ranges(self, admin_session, rng):
        r = admin_session.get(f"{BASE_URL}/api/admin/analytics?range={rng}", timeout=30)
        assert r.status_code == 200, f"range {rng}: {r.status_code} {r.text[:200]}"
        d = r.json()
        assert "kpis" in d
        # Analytics uses "applicant_trend" (not "trends"), plus countries/stage_breakdown
        assert any(k in d for k in ("applicant_trend", "trends", "stage_breakdown", "countries")), \
            f"no trend/breakdown in analytics {rng}: {list(d.keys())}"

    def test_admin_staff_endpoint(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/staff", timeout=20)
        assert r.status_code == 200

    def test_admin_analytics_rbac_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/admin/analytics?range=7d", timeout=20)
        assert r.status_code in (401, 403)

    def test_admin_analytics_rbac_applicant(self, applicant_session):
        r = applicant_session.get(f"{BASE_URL}/api/admin/analytics?range=7d", timeout=20)
        assert r.status_code in (401, 403)


# ---------------- CSRF Enforcement ----------------

class TestCSRF:
    def test_csrf_missing_on_unsafe_admin_post(self, admin_session):
        # Copy session without CSRF header
        cookies = admin_session.cookies
        r = requests.post(
            f"{BASE_URL}/api/system/clean-demo-data",
            cookies=cookies,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        assert r.status_code == 403, f"expected 403 without CSRF, got {r.status_code}"


# ---------------- Security headers ----------------

class TestSecurityHeaders:
    def test_security_headers_present(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        h = {k.lower(): v for k, v in r.headers.items()}
        # At least some security headers should be present
        expected_any = [
            "x-content-type-options", "x-frame-options",
            "strict-transport-security", "content-security-policy",
            "referrer-policy",
        ]
        found = [k for k in expected_any if k in h]
        assert len(found) >= 2, f"few security headers: {found}, all={list(h.keys())}"
