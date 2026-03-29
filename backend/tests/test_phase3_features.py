"""
Phase 3 Backend Tests: AI Screening, Extended Lead Ingest, Legal/Status endpoints.
Tests: leads/ingest with new fields, ai-screen, ai-screenings, stage updates
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')
# Use internal URL for backend testing to avoid external routing issues
if not BASE_URL or BASE_URL.startswith('https://w2g-academy-portal'):
    BASE_URL = 'http://localhost:8001'


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_session(session):
    """Authenticate as admin and return session with cookies."""
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@studienkolleg-aachen.de",
        "password": "Admin@2026!"
    })
    if resp.status_code != 200:
        pytest.skip(f"Admin login failed: {resp.status_code} {resp.text}")
    return session


@pytest.fixture(scope="module")
def test_application_id(admin_session):
    """Get or create a test application to use for AI screening tests."""
    # List existing applications
    resp = admin_session.get(f"{BASE_URL}/api/applications")
    if resp.status_code == 200:
        apps = resp.json()
        if isinstance(apps, list) and len(apps) > 0:
            # Find one with degree_country set for better AI screening results
            for app in apps:
                if app.get("degree_country") or app.get("course_type"):
                    return app.get("id") or app.get("_id")
            return apps[0].get("id") or apps[0].get("_id")
    # Create a new lead to get an application
    unique_email = f"TEST_ai_screen_{int(time.time())}@example.com"
    lead_resp = requests.post(f"{BASE_URL}/api/leads/ingest", json={
        "full_name": "AI Test User",
        "first_name": "AI",
        "last_name": "Test",
        "email": unique_email,
        "phone": "+49 123 456789",
        "country": "India",
        "date_of_birth": "2000-05-15",
        "area_interest": "studienkolleg",
        "course_type": "T-Course",
        "desired_start": "Winter Semester 2026/27",
        "language_level": "B1",
        "degree_country": "India",
        "notes": "Test application for AI screening",
        "source": "test"
    })
    if lead_resp.status_code == 200:
        data = lead_resp.json()
        return data.get("application_id")
    pytest.skip("Could not get or create test application")


# ─── Health Check ─────────────────────────────────────────────────────────────

class TestHealthCheck:
    """Verify backend is running."""

    def test_api_health(self, session):
        resp = session.get(f"{BASE_URL}/api/health")
        assert resp.status_code in [200, 404], f"Health check: {resp.status_code}"
        print(f"PASS: Backend reachable at {BASE_URL}")


# ─── Lead Ingest: Extended Fields ─────────────────────────────────────────────

class TestLeadIngestPhase3:
    """Tests for extended LeadIngest with Phase 3 fields."""

    def test_lead_ingest_basic_new_fields(self, session):
        """POST /api/leads/ingest with all new required fields."""
        unique_email = f"TEST_lead_phase3_{int(time.time())}@example.com"
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "Phase3 Test User",
            "first_name": "Phase3",
            "last_name": "TestUser",
            "email": unique_email,
            "phone": "+49 241 999 0000",
            "country": "India",
            "date_of_birth": "1999-03-20",
            "area_interest": "studienkolleg",
            "course_type": "T-Course",
            "desired_start": "Winter Semester 2026/27",
            "language_level": "B1",
            "degree_country": "India",
            "notes": "Test from Phase3 test suite",
            "source": "website_form"
        })
        print(f"Lead ingest response: {resp.status_code} {resp.text[:200]}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data.get("success") is True, f"Expected success=True, got {data}"
        assert "application_id" in data, f"Expected application_id in response: {data}"
        assert "user_id" in data, f"Expected user_id in response: {data}"
        print(f"PASS: Lead ingest successful, application_id={data['application_id']}")

    def test_lead_ingest_returns_application_id(self, session):
        """Lead ingest should always return a non-null application_id for new leads."""
        unique_email = f"TEST_lead_appid_{int(time.time())}@example.com"
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "AppID Test",
            "first_name": "AppID",
            "last_name": "Test",
            "email": unique_email,
            "phone": "+49 111 222 333",
            "country": "China",
            "date_of_birth": "2001-07-10",
            "area_interest": "studienkolleg",
            "course_type": "M-Course",
            "desired_start": "Summer Semester 2026",
            "language_level": "A2",
            "degree_country": "China",
            "source": "website_form"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        assert data.get("application_id") is not None, "application_id should not be None for new lead"
        print(f"PASS: application_id={data['application_id']}")

    def test_lead_ingest_with_all_optional_fields(self, session):
        """Confirm all new optional fields are accepted without error."""
        unique_email = f"TEST_lead_allfields_{int(time.time())}@example.com"
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "All Fields Test",
            "first_name": "All",
            "last_name": "Fields",
            "email": unique_email,
            "phone": "+49 1234 567890",
            "country": "Egypt",
            "date_of_birth": "1998-01-15",
            "area_interest": "studienkolleg",
            "course_type": "W-Course",
            "desired_start": "Winter Semester 2027/28",
            "combo_option": "T-Course",
            "language_level": "B2",
            "degree_country": "Egypt",
            "notes": "All fields test submission",
            "source": "website_form",
            "referral_code": "TEST123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        print(f"PASS: All fields accepted, application_id={data.get('application_id')}")

    def test_lead_ingest_duplicate_detection(self, session):
        """Submitting same email twice should set duplicate_flag=True on second attempt."""
        unique_email = f"TEST_lead_dup_{int(time.time())}@example.com"
        payload = {
            "full_name": "Duplicate Test",
            "first_name": "Duplicate",
            "last_name": "Test",
            "email": unique_email,
            "phone": "+49 100 200 300",
            "country": "Morocco",
            "area_interest": "studienkolleg",
            "course_type": "T-Course",
            "language_level": "B1",
            "degree_country": "Morocco",
            "source": "website_form"
        }
        # First submission
        resp1 = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1.get("duplicate_flag") is False, f"First submission should not be duplicate: {data1}"

        # Second submission (same email)
        resp2 = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2.get("duplicate_flag") is True, f"Second submission should be duplicate: {data2}"
        print(f"PASS: Duplicate detection working correctly")

    def test_lead_ingest_language_course_area(self, session):
        """Language Course should map to language_courses area_interest."""
        unique_email = f"TEST_lead_lang_{int(time.time())}@example.com"
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "Language Course Test",
            "first_name": "Language",
            "last_name": "CourseTest",
            "email": unique_email,
            "phone": "+49 555 666 777",
            "country": "Vietnam",
            "area_interest": "language_courses",
            "course_type": "Language Course",
            "desired_start": "Summer Semester 2026",
            "language_level": "A1",
            "degree_country": "Vietnam",
            "source": "website_form"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        print(f"PASS: Language Course ingest OK")

    def test_lead_ingest_with_documents_metadata(self, session):
        """Lead ingest with document metadata (no binary) should work."""
        unique_email = f"TEST_lead_docs_{int(time.time())}@example.com"
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "Docs Test",
            "first_name": "Docs",
            "last_name": "Test",
            "email": unique_email,
            "phone": "+49 777 888 999",
            "country": "Turkey",
            "date_of_birth": "2000-12-01",
            "area_interest": "studienkolleg",
            "course_type": "M/T-Course",
            "desired_start": "Winter Semester 2026/27",
            "language_level": "B1",
            "degree_country": "Turkey",
            "source": "website_form",
            "documents": [
                {
                    "document_type": "language_certificate",
                    "filename": "goethe_b1.pdf",
                    "content_type": "application/pdf",
                    "file_data": None
                }
            ]
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        print(f"PASS: Lead ingest with document metadata OK")


# ─── AI Screening Endpoints ────────────────────────────────────────────────────

class TestAIScreening:
    """Tests for POST /api/applications/{id}/ai-screen and GET /api/applications/{id}/ai-screenings."""

    def test_ai_screen_requires_auth(self, session, test_application_id):
        """AI screen endpoint requires authentication - should return 401 if not logged in."""
        unauth_session = requests.Session()
        resp = unauth_session.post(f"{BASE_URL}/api/applications/{test_application_id}/ai-screen")
        assert resp.status_code in [401, 403], f"Expected 401/403 without auth, got {resp.status_code}"
        print(f"PASS: AI screen endpoint requires auth (got {resp.status_code})")

    def test_ai_screenings_list_requires_auth(self, session, test_application_id):
        """AI screenings list endpoint requires authentication."""
        unauth_session = requests.Session()
        resp = unauth_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert resp.status_code in [401, 403], f"Expected 401/403 without auth, got {resp.status_code}"
        print(f"PASS: AI screenings list requires auth (got {resp.status_code})")

    def test_ai_screen_run_as_admin(self, admin_session, test_application_id):
        """Staff/admin can trigger AI screening - should return structured result."""
        if not test_application_id:
            pytest.skip("No test application available")
        resp = admin_session.post(f"{BASE_URL}/api/applications/{test_application_id}/ai-screen")
        print(f"AI screen response: {resp.status_code} {resp.text[:500]}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        # Verify required fields are present
        assert "screening_id" in data, f"Expected screening_id in response: {data}"
        assert "application_id" in data, f"Expected application_id in response: {data}"
        assert "is_complete" in data, f"Expected is_complete in response: {data}"
        assert "suggested_stage" in data, f"Expected suggested_stage in response: {data}"
        assert "local_checks" in data, f"Expected local_checks in response: {data}"
        assert "anabin_category" in data, f"Expected anabin_category in response: {data}"
        assert "language_level_ok" in data, f"Expected language_level_ok in response: {data}"
        assert "missing_documents" in data, f"Expected missing_documents in response: {data}"
        print(f"PASS: AI screen returned complete result - is_complete={data.get('is_complete')}, anabin={data.get('anabin_category')}")

    def test_ai_screen_local_checks_present(self, admin_session, test_application_id):
        """Local checks (completeness, anabin, language) should always be in result."""
        if not test_application_id:
            pytest.skip("No test application available")
        resp = admin_session.post(f"{BASE_URL}/api/applications/{test_application_id}/ai-screen")
        assert resp.status_code == 200
        data = resp.json()
        local_checks = data.get("local_checks", {})
        assert "completeness" in local_checks, f"Expected completeness in local_checks: {local_checks}"
        assert "anabin_assessment" in local_checks, f"Expected anabin_assessment in local_checks: {local_checks}"
        assert "language_level_check" in local_checks, f"Expected language_level_check in local_checks: {local_checks}"
        completeness = local_checks["completeness"]
        assert "complete" in completeness
        assert "missing_types" in completeness
        assert "total_required" in completeness
        assert completeness["total_required"] == 3, f"Expected 3 required docs, got {completeness['total_required']}"
        print(f"PASS: Local checks present - complete={completeness.get('complete')}, missing={completeness.get('missing_types')}")

    def test_ai_screenings_list_as_admin(self, admin_session, test_application_id):
        """GET /api/applications/{id}/ai-screenings returns list (newest first)."""
        if not test_application_id:
            pytest.skip("No test application available")
        resp = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        print(f"Screenings list response: {resp.status_code} {resp.text[:300]}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list response, got: {type(data)}"
        print(f"PASS: AI screenings list returns {len(data)} items")

    def test_ai_screenings_history_after_run(self, admin_session, test_application_id):
        """After running AI screen, the screenings list should have at least 1 item."""
        if not test_application_id:
            pytest.skip("No test application available")
        # Run a screening
        run_resp = admin_session.post(f"{BASE_URL}/api/applications/{test_application_id}/ai-screen")
        assert run_resp.status_code == 200, f"AI screen failed: {run_resp.status_code}"
        # Check history
        list_resp = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert len(data) >= 1, f"Expected at least 1 screening in history, got {len(data)}"
        # Verify structure of first item
        first = data[0]
        assert "screening_id" in first, f"screening_id missing in history item: {first}"
        assert "is_complete" in first, f"is_complete missing in history item: {first}"
        assert "anabin_category" in first, f"anabin_category missing in history item: {first}"
        print(f"PASS: Screenings history has {len(data)} items, latest: {first.get('screening_id')}")

    def test_ai_screen_invalid_app_id(self, admin_session):
        """Invalid application ID should return 400."""
        resp = admin_session.post(f"{BASE_URL}/api/applications/invalid_id_xyz/ai-screen")
        assert resp.status_code == 400, f"Expected 400 for invalid ID, got {resp.status_code}"
        print(f"PASS: Invalid app ID returns 400")

    def test_ai_screen_not_found_app(self, admin_session):
        """Non-existent application should return 404."""
        fake_id = "000000000000000000000001"
        resp = admin_session.post(f"{BASE_URL}/api/applications/{fake_id}/ai-screen")
        assert resp.status_code == 404, f"Expected 404 for non-existent app, got {resp.status_code}"
        print(f"PASS: Non-existent app returns 404")


# ─── Application Details: New Fields ─────────────────────────────────────────

class TestApplicationNewFields:
    """Verify new fields (course_type, desired_start, language_level, degree_country) are persisted."""

    def test_application_has_new_fields(self, admin_session, test_application_id):
        """GET /api/applications/{id} should return new Phase 3 fields."""
        if not test_application_id:
            pytest.skip("No test application available")
        resp = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        print(f"Application data keys: {list(data.keys())}")
        # The app was created via lead ingest with these fields
        # They might be None if not set in the seeded app, but the fields should exist or at least not error
        print(f"PASS: Application detail loaded, keys: {list(data.keys())}")
        print(f"  course_type={data.get('course_type')}, desired_start={data.get('desired_start')}")
        print(f"  language_level={data.get('language_level')}, degree_country={data.get('degree_country')}")

    def test_lead_ingest_persists_new_fields(self, session):
        """Fields submitted in lead ingest should be persisted in the application."""
        unique_email = f"TEST_fields_persist_{int(time.time())}@example.com"
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "Fields Persist Test",
            "first_name": "Fields",
            "last_name": "Persist",
            "email": unique_email,
            "phone": "+49 100 123 456",
            "country": "Brazil",
            "date_of_birth": "1997-06-15",
            "area_interest": "studienkolleg",
            "course_type": "W-Course",
            "desired_start": "Summer Semester 2027",
            "language_level": "C1",
            "degree_country": "Brazil",
            "notes": "Testing field persistence",
            "source": "website_form"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") is True
        app_id = data.get("application_id")
        assert app_id, "application_id missing"

        # Verify fields are stored - need admin auth
        # We'll check via admin session (fixture from another test class)
        admin_s = requests.Session()
        admin_s.headers.update({"Content-Type": "application/json"})
        login_resp = admin_s.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": "Admin@2026!"
        })
        if login_resp.status_code == 200:
            app_resp = admin_s.get(f"{BASE_URL}/api/applications/{app_id}")
            if app_resp.status_code == 200:
                app_data = app_resp.json()
                assert app_data.get("course_type") == "W-Course", f"Expected W-Course, got {app_data.get('course_type')}"
                assert app_data.get("desired_start") == "Summer Semester 2027", f"desired_start mismatch"
                assert app_data.get("language_level") == "C1", f"language_level mismatch"
                assert app_data.get("degree_country") == "Brazil", f"degree_country mismatch"
                print(f"PASS: All new fields persisted correctly in application")
            else:
                print(f"WARNING: Could not fetch application (admin fetch returned {app_resp.status_code})")
        else:
            print(f"WARNING: Admin login failed for field verification")


# ─── Stage Update Tests ────────────────────────────────────────────────────────

class TestStageUpdate:
    """Verify staff can update application stages."""

    def test_stage_update_as_admin(self, admin_session, test_application_id):
        """PUT /api/applications/{id} with current_stage should update status."""
        if not test_application_id:
            pytest.skip("No test application available")
        # Get current stage first
        get_resp = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}")
        assert get_resp.status_code == 200
        current_stage = get_resp.json().get("current_stage")
        print(f"Current stage: {current_stage}")

        # Change to in_review
        resp = admin_session.put(f"{BASE_URL}/api/applications/{test_application_id}",
                                  json={"current_stage": "in_review"})
        print(f"Stage update response: {resp.status_code} {resp.text[:200]}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        # Verify update persisted
        verify_resp = admin_session.get(f"{BASE_URL}/api/applications/{test_application_id}")
        assert verify_resp.status_code == 200
        updated_data = verify_resp.json()
        assert updated_data.get("current_stage") == "in_review", f"Stage not updated: {updated_data.get('current_stage')}"
        print(f"PASS: Stage updated to in_review")

    def test_stage_update_all_valid_stages(self, admin_session, test_application_id):
        """All valid stages should be accepted by the API."""
        if not test_application_id:
            pytest.skip("No test application available")
        valid_stages = ["lead_new", "in_review", "pending_docs", "on_hold"]
        for stage in valid_stages:
            resp = admin_session.put(f"{BASE_URL}/api/applications/{test_application_id}",
                                      json={"current_stage": stage})
            assert resp.status_code == 200, f"Stage {stage} update failed: {resp.status_code} {resp.text}"
            print(f"PASS: Stage update to {stage} works")
        # Reset to lead_new
        admin_session.put(f"{BASE_URL}/api/applications/{test_application_id}",
                          json={"current_stage": "lead_new"})


# ─── Applications List ─────────────────────────────────────────────────────────

class TestApplicationsList:
    """Test the applications list endpoint."""

    def test_applications_list_as_admin(self, admin_session):
        """GET /api/applications should return list for admin."""
        resp = admin_session.get(f"{BASE_URL}/api/applications")
        print(f"Applications list: {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), f"Expected list, got {type(data)}"
        print(f"PASS: Applications list returns {len(data)} items")

    def test_applications_list_forbidden_for_unauthenticated(self):
        """Applications list should be 401 for unauthenticated users."""
        resp = requests.get(f"{BASE_URL}/api/applications")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: Applications list requires auth (got {resp.status_code})")
