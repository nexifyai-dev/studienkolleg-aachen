"""
W2G Platform Security Hardening Tests - Iteration 2
Tests: RBAC, auth flows, brute force, lead-claiming, workspaces, applications
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASS = "Admin@2026!"

UID = uuid.uuid4().hex[:8]
TEST_APPLICANT_EMAIL = f"TEST_applicant_{UID}@example.com"
TEST_APPLICANT_PASS = "Applicant@2026!"
TEST_LEAD_EMAIL = f"TEST_lead_{UID}@example.com"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_session(session):
    r = session.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    s = requests.Session()
    s.cookies.update(session.cookies)
    s.headers.update({"Content-Type": "application/json"})
    # copy cookies from login response
    for c in r.cookies:
        s.cookies.set(c.name, c.value)
    return s


@pytest.fixture(scope="module")
def applicant_data(session):
    """Register a test applicant and return session + user data"""
    r = session.post(f"{BASE_URL}/api/auth/register", json={
        "email": TEST_APPLICANT_EMAIL,
        "password": TEST_APPLICANT_PASS,
        "full_name": "Test Applicant"
    })
    assert r.status_code == 200, f"Applicant register failed: {r.text}"
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    for c in r.cookies:
        s.cookies.set(c.name, c.value)
    return {"session": s, "user": r.json()}


# ── 1. HEALTH CHECK ──────────────────────────────────────────────────────────
class TestHealth:
    def test_health_ok(self, session):
        r = session.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        d = r.json()
        assert d.get("status") == "ok"
        assert d.get("version") == "1.1.0"
        assert d.get("email_enabled") == False
        assert d.get("storage_backend") == "local"
        print(f"PASS: health → {d}")


# ── 2. AUTH FLOWS ─────────────────────────────────────────────────────────────
class TestAuthFlows:
    def test_admin_login_role(self, session):
        r = session.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        assert r.status_code == 200
        d = r.json()
        assert d.get("role") == "superadmin", f"Expected superadmin, got {d.get('role')}"
        print(f"PASS: admin role = {d.get('role')}")

    def test_register_applicant(self, session):
        email = f"TEST_reg_{uuid.uuid4().hex[:6]}@example.com"
        r = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": "Register@2026!",
            "full_name": "Reg Test"
        })
        assert r.status_code == 200
        d = r.json()
        assert d.get("role") == "applicant"
        print(f"PASS: register applicant {email}")

    def test_token_refresh(self, session):
        # Login first to get cookies
        s = requests.Session()
        r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        assert r.status_code == 200
        for c in r.cookies:
            s.cookies.set(c.name, c.value)
        # Refresh
        r2 = s.post(f"{BASE_URL}/api/auth/refresh")
        assert r2.status_code == 200
        assert "access_token" in r2.cookies or r2.json().get("message") == "Token refreshed"
        print(f"PASS: token refresh → {r2.json()}")

    def test_logout_clears_cookies(self, session):
        s = requests.Session()
        r = s.post(f"{BASE_URL}/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASS})
        assert r.status_code == 200
        for c in r.cookies:
            s.cookies.set(c.name, c.value)
        r2 = s.post(f"{BASE_URL}/api/auth/logout")
        assert r2.status_code == 200
        # Check cookies deleted
        assert "access_token" not in r2.cookies or r2.cookies.get("access_token") == ""
        print(f"PASS: logout cookies cleared")

    def test_brute_force_lockout(self, session):
        """5 wrong attempts → 6th should be 429"""
        brute_email = f"TEST_brute_{uuid.uuid4().hex[:6]}@example.com"
        for i in range(5):
            r = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": brute_email, "password": "WrongPass1!"
            })
            assert r.status_code == 401, f"Attempt {i+1} should be 401"
        # 6th attempt
        r = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": brute_email, "password": "WrongPass1!"
        })
        assert r.status_code == 429, f"6th attempt should be 429, got {r.status_code}: {r.text}"
        print(f"PASS: brute force lockout after 5 attempts → 429")

    def test_lead_claiming_flow(self, session):
        """Apply (lead ingest) then register with same email → 200 not 409"""
        lead_email = TEST_LEAD_EMAIL
        # Step 1: Lead ingest via /apply
        r = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "email": lead_email,
            "full_name": "Lead Claimer",
            "phone": "+49123456789",
            "area_interest": "studienkolleg",
            "country": "Egypt"
        })
        # Lead ingest may 200 or 201
        assert r.status_code in [200, 201], f"Lead ingest failed: {r.text}"
        print(f"Lead ingest status: {r.status_code}")

        # Step 2: Register with same email → should claim (200) not 409
        r2 = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": lead_email,
            "password": "LeadClaim@2026!",
            "full_name": "Lead Claimer"
        })
        assert r2.status_code == 200, f"Lead claiming returned {r2.status_code}: {r2.text}"
        print(f"PASS: lead claiming → {r2.json()}")


# ── 3. SECURITY / RBAC ───────────────────────────────────────────────────────
class TestRBAC:
    def test_unauthenticated_workspace_post_401(self, session):
        s = requests.Session()
        r = s.post(f"{BASE_URL}/api/workspaces", json={"name": "test", "slug": "test"})
        assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"
        print(f"PASS: unauth POST /workspaces → 401")

    def test_applicant_cannot_get_audit_logs(self, applicant_data):
        s = applicant_data["session"]
        r = s.get(f"{BASE_URL}/api/audit-logs")
        assert r.status_code == 403, f"Expected 403, got {r.status_code}: {r.text}"
        print(f"PASS: applicant GET /audit-logs → 403")

    def test_applicant_cannot_get_users(self, applicant_data):
        s = applicant_data["session"]
        r = s.get(f"{BASE_URL}/api/users")
        assert r.status_code == 403, f"Expected 403, got {r.status_code}: {r.text}"
        print(f"PASS: applicant GET /users → 403")

    def test_applicant_cannot_update_other_user(self, applicant_data, admin_session):
        s = applicant_data["session"]
        # Get admin's ID from /me
        r = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 200
        admin_id = r.json().get("id")
        r2 = s.put(f"{BASE_URL}/api/users/{admin_id}", json={"full_name": "Hacked"})
        assert r2.status_code == 403, f"Expected 403, got {r2.status_code}: {r2.text}"
        print(f"PASS: applicant PUT /users/:admin_id → 403")


# ── 4. WORKSPACES ────────────────────────────────────────────────────────────
class TestWorkspaces:
    def test_get_workspaces_returns_4(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/workspaces")
        assert r.status_code == 200
        data = r.json()
        workspaces = data if isinstance(data, list) else data.get("workspaces", data.get("items", []))
        slugs = [w.get("slug") for w in workspaces]
        for slug in ["studienkolleg", "sprachkurse", "pflege", "arbeit"]:
            assert slug in slugs, f"Missing workspace: {slug}. Found: {slugs}"
        print(f"PASS: 4 workspaces → {slugs}")


# ── 5. APPLICATIONS ──────────────────────────────────────────────────────────
class TestApplications:
    def test_staff_can_get_applications(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/applications")
        assert r.status_code == 200
        data = r.json()
        apps = data if isinstance(data, list) else data.get("applications", data.get("items", []))
        print(f"PASS: GET /applications → {len(apps)} applications")


# ── 6. TASK OWNERSHIP ────────────────────────────────────────────────────────
class TestTaskOwnership:
    def test_task_update_ownership_check(self, applicant_data, admin_session):
        """Staff cannot update tasks belonging to others → 403 or 404"""
        # Create a task as admin
        r = admin_session.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_task_ownership",
            "description": "Ownership test",
            "status": "open"
        })
        if r.status_code not in [200, 201]:
            pytest.skip(f"Task creation not supported or failed: {r.status_code} {r.text}")
        task_id = r.json().get("id")
        # Applicant tries to update
        s = applicant_data["session"]
        r2 = s.put(f"{BASE_URL}/api/tasks/{task_id}", json={"title": "Hacked"})
        assert r2.status_code in [403, 404], f"Expected 403/404, got {r2.status_code}: {r2.text}"
        print(f"PASS: applicant PUT /tasks/:id → {r2.status_code}")
