"""
Phase 3.5 backend tests for W2G Platform:
- POST /api/leads/ingest with all new fields
- GET /api/applications/{id}/ai-screenings
- POST /api/applications/{id}/ai-screen
- GET /api/users (admin - filter tabs)
- PUT /api/users/{id} (activate/deactivate)
- POST /api/auth/invite (staff invitation)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def session():
    """Shared requests session"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_session(session):
    """Authenticated admin session (httpOnly cookies)"""
    res = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if res.status_code != 200:
        pytest.skip(f"Admin login failed: {res.status_code} – {res.text[:200]}")
    return session


@pytest.fixture(scope="module")
def test_application_id(admin_session):
    """Fetch or create an application ID for AI screening tests"""
    res = admin_session.get(f"{BASE_URL}/api/applications", params={"limit": 5})
    if res.status_code == 200 and res.json():
        apps = res.json()
        if apps:
            return apps[0]["id"]
    pytest.skip("No applications available for screening tests")


# ─── Health ───────────────────────────────────────────────────────────────────

class TestHealth:
    """Basic connectivity"""

    def test_backend_reachable(self, session):
        res = session.get(f"{BASE_URL}/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        assert data.get("status") == "ok"
        print("PASS: backend health OK")


# ─── Leads Ingest ─────────────────────────────────────────────────────────────

class TestLeadsIngest:
    """POST /api/leads/ingest – all Phase 3.5 fields"""

    def test_ingest_minimal(self, session):
        """Minimal required fields only"""
        unique = str(uuid.uuid4())[:8]
        payload = {
            "full_name": f"TEST_Minimal {unique}",
            "email": f"TEST_minimal_{unique}@example.com",
            "area_interest": "studienkolleg",
        }
        res = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert res.status_code == 200, f"Ingest failed: {res.text}"
        data = res.json()
        assert data.get("success") is True
        assert "user_id" in data
        print(f"PASS: minimal ingest → user_id={data['user_id']}")

    def test_ingest_all_new_fields(self, session):
        """All Phase 3.5 fields: course_type, degree_country, combo_option, language_level, desired_start, date_of_birth"""
        unique = str(uuid.uuid4())[:8]
        payload = {
            "full_name": f"TEST_FullFields {unique}",
            "email": f"TEST_fullfields_{unique}@example.com",
            "phone": "+491234567890",
            "country": "Iran",
            "date_of_birth": "2000-05-15",
            "area_interest": "studienkolleg",
            "course_type": "T-Course",
            "desired_start": "Winter Semester 2026/27",
            "combo_option": "Sprachkurs",
            "language_level": "B1",
            "degree_country": "Iran",
            "notes": "Test note from Phase 3.5",
            "source": "website_form",
        }
        res = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert res.status_code == 200, f"Ingest with all fields failed: {res.text}"
        data = res.json()
        assert data.get("success") is True
        assert data.get("application_id") is not None, "Expected application_id to be created"
        assert data.get("duplicate_flag") is False
        print(f"PASS: full-field ingest → app_id={data['application_id']}")

    def test_ingest_duplicate_detection(self, session):
        """Submitting same email twice should flag duplicate"""
        unique = str(uuid.uuid4())[:8]
        email = f"TEST_dup_{unique}@example.com"
        payload = {
            "full_name": f"TEST_Dup {unique}",
            "email": email,
            "area_interest": "studienkolleg",
            "course_type": "M-Course",
        }
        # First submit
        res1 = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert res1.status_code == 200
        # Second submit with same email
        res2 = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2.get("duplicate_flag") is True, "Expected duplicate_flag=True for second submission"
        print("PASS: duplicate detection works")

    def test_ingest_with_document_metadata(self, session):
        """Test ingest with document upload metadata"""
        unique = str(uuid.uuid4())[:8]
        payload = {
            "full_name": f"TEST_WithDoc {unique}",
            "email": f"TEST_withdoc_{unique}@example.com",
            "area_interest": "studienkolleg",
            "course_type": "W-Course",
            "documents": [
                {
                    "document_type": "language_certificate",
                    "filename": "test_cert.pdf",
                    "content_type": "application/pdf"
                }
            ]
        }
        res = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert res.status_code == 200, f"Ingest with doc failed: {res.text}"
        data = res.json()
        assert data.get("success") is True
        print(f"PASS: ingest with document metadata → app_id={data.get('application_id')}")

    def test_ingest_returns_message(self, session):
        """Response message should be present"""
        unique = str(uuid.uuid4())[:8]
        payload = {
            "full_name": f"TEST_Msg {unique}",
            "email": f"TEST_msg_{unique}@example.com",
            "area_interest": "studienkolleg",
        }
        res = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "message" in data
        assert len(data["message"]) > 0
        print(f"PASS: response includes message: {data['message'][:50]}")


# ─── AI Screenings ────────────────────────────────────────────────────────────

class TestAIScreenings:
    """GET /api/applications/{id}/ai-screenings"""

    def test_get_screenings_requires_auth(self, session, test_application_id):
        """Unauthenticated access should be rejected"""
        fresh = requests.Session()
        res = fresh.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert res.status_code in [401, 403], f"Expected 401/403, got {res.status_code}"
        print("PASS: unauthenticated screening GET rejected")

    def test_get_screenings_staff_can_access(self, admin_session, test_application_id):
        """Staff can list AI screenings"""
        res = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert res.status_code == 200, f"Screening GET failed: {res.text}"
        data = res.json()
        assert isinstance(data, list), "Expected list of screenings"
        print(f"PASS: screenings list returned ({len(data)} items)")

    def test_get_screenings_structure(self, admin_session, test_application_id):
        """Each screening should have required fields"""
        res = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert res.status_code == 200
        data = res.json()
        if data:
            s = data[0]
            # Check expected screening fields
            for field in ["application_id", "is_complete", "anabin_category", "suggested_stage"]:
                assert field in s, f"Missing field '{field}' in screening"
            print(f"PASS: screening structure valid — anabin={s.get('anabin_category')}, complete={s.get('is_complete')}")
        else:
            print("INFO: No screenings yet for this application (acceptable)")

    def test_run_ai_screening(self, admin_session, test_application_id):
        """POST ai-screen should create a new screening result"""
        res = admin_session.post(
            f"{BASE_URL}/api/applications/{test_application_id}/ai-screen",
            json={}
        )
        assert res.status_code == 200, f"AI screen POST failed: {res.status_code} – {res.text[:300]}"
        data = res.json()
        assert "is_complete" in data
        assert "anabin_category" in data
        assert "suggested_stage" in data
        assert "screening_id" in data
        print(f"PASS: AI screening run — anabin={data['anabin_category']}, complete={data['is_complete']}, stage={data['suggested_stage']}")

    def test_screening_persists_after_run(self, admin_session, test_application_id):
        """After running AI screen, GET screenings should return at least 1 result"""
        res = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 1, "Expected at least 1 screening after running"
        print(f"PASS: screening persisted, total count: {len(data)}")


# ─── Users / Admin ────────────────────────────────────────────────────────────

class TestUsersAdmin:
    """Admin UsersPage API tests"""

    def test_get_users_admin_only(self, session):
        """Unauthenticated users cannot access /api/users"""
        fresh = requests.Session()
        res = fresh.get(f"{BASE_URL}/api/users")
        assert res.status_code in [401, 403], f"Expected 401/403, got {res.status_code}"
        print("PASS: unauthenticated GET /api/users rejected")

    def test_get_users_list(self, admin_session):
        """Admin can fetch users list"""
        res = admin_session.get(f"{BASE_URL}/api/users")
        assert res.status_code == 200, f"GET /api/users failed: {res.text}"
        data = res.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least 1 user (admin)"
        print(f"PASS: GET /api/users → {len(data)} users")

    def test_users_contain_required_fields(self, admin_session):
        """User objects contain expected fields"""
        res = admin_session.get(f"{BASE_URL}/api/users")
        assert res.status_code == 200
        data = res.json()
        assert data
        u = data[0]
        for field in ["id", "email", "role"]:
            assert field in u, f"Missing field '{field}' in user"
        assert "_id" not in u, "MongoDB _id should not be exposed"
        print(f"PASS: user structure OK — role={u.get('role')}")

    def test_toggle_user_active_status(self, admin_session):
        """PUT /api/users/{id} should allow toggling active status"""
        # Get a non-superadmin user
        res = admin_session.get(f"{BASE_URL}/api/users")
        assert res.status_code == 200
        users = res.json()
        target = next((u for u in users if u.get("role") != "superadmin" and u.get("role") == "applicant"), None)
        if not target:
            pytest.skip("No applicant user found to toggle")
        
        user_id = target["id"]
        current_active = target.get("active", True)
        
        # Toggle
        res2 = admin_session.put(f"{BASE_URL}/api/users/{user_id}", json={"active": not current_active})
        assert res2.status_code == 200, f"Toggle failed: {res2.text}"
        
        # Verify change
        res3 = admin_session.get(f"{BASE_URL}/api/users/{user_id}")
        assert res3.status_code == 200
        updated = res3.json()
        assert updated.get("active") == (not current_active), "Active status not updated"
        
        # Restore original state
        admin_session.put(f"{BASE_URL}/api/users/{user_id}", json={"active": current_active})
        print(f"PASS: toggle user active from {current_active} → {not current_active} and restored")

    def test_invite_creates_link(self, admin_session):
        """POST /api/auth/invite should return invite_url"""
        unique = str(uuid.uuid4())[:8]
        payload = {
            "email": f"TEST_invite_{unique}@example.com",
            "full_name": f"TEST Invite {unique}",
            "role": "staff"
        }
        res = admin_session.post(f"{BASE_URL}/api/auth/invite", json=payload)
        assert res.status_code == 200, f"Invite failed: {res.status_code} – {res.text}"
        data = res.json()
        assert "invite_url" in data, "Expected invite_url in response"
        assert len(data["invite_url"]) > 10
        print(f"PASS: invite created → url starts with {data['invite_url'][:50]}")

    def test_users_has_staff_roles(self, admin_session):
        """Users list should contain staff roles"""
        res = admin_session.get(f"{BASE_URL}/api/users")
        assert res.status_code == 200
        users = res.json()
        roles = {u.get("role") for u in users}
        assert "superadmin" in roles or "admin" in roles, f"No staff roles found: {roles}"
        print(f"PASS: found roles in users: {roles}")


# ─── Applications API ─────────────────────────────────────────────────────────

class TestApplicationsAPI:
    """Applications endpoint sanity checks"""

    def test_get_applications_requires_auth(self, session):
        fresh = requests.Session()
        res = fresh.get(f"{BASE_URL}/api/applications")
        assert res.status_code in [401, 403]
        print("PASS: unauthenticated GET /api/applications rejected")

    def test_get_applications_staff(self, admin_session):
        res = admin_session.get(f"{BASE_URL}/api/applications")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        print(f"PASS: GET /api/applications → {len(data)} applications")

    def test_application_has_stage_field(self, admin_session):
        res = admin_session.get(f"{BASE_URL}/api/applications")
        assert res.status_code == 200
        apps = res.json()
        if apps:
            a = apps[0]
            assert "current_stage" in a, "Missing current_stage in application"
            assert "id" in a, "Missing id in application"
            print(f"PASS: application has current_stage={a.get('current_stage')}")
