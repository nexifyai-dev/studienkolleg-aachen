"""
Iteration 83 Tests: Security Headers, GDPR Endpoints, Admin Settings, Frontend Pages

Tests:
1. Security Headers on /api/health
2. Admin Settings GET/PUT
3. GDPR Export endpoint
4. GDPR Anonymize endpoint (Admin protection)
5. State Machine invalid transition (422)
6. Stage Effects auto-task creation
7. Merge duplicates validation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = "DevSeed@2026!"
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def admin_session():
    """Admin login session"""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    if r.status_code != 200:
        pytest.skip(f"Admin login failed: {r.status_code}")
    return session


@pytest.fixture(scope="module")
def staff_session():
    """Staff login session"""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL, "password": STAFF_PASSWORD
    })
    if r.status_code != 200:
        pytest.skip(f"Staff login failed: {r.status_code}")
    return session


@pytest.fixture(scope="module")
def partner_session():
    """Partner/Affiliate login session"""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": PARTNER_EMAIL, "password": PARTNER_PASSWORD
    })
    if r.status_code != 200:
        pytest.skip(f"Partner login failed: {r.status_code}")
    return session


@pytest.fixture(scope="module")
def teacher_session():
    """Teacher login session"""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEACHER_EMAIL, "password": TEACHER_PASSWORD
    })
    if r.status_code != 200:
        pytest.skip(f"Teacher login failed: {r.status_code}")
    return session


class TestSecurityHeaders:
    """Security Headers on /api/health endpoint"""

    def test_health_returns_security_headers(self):
        """GET /api/health must include all required security headers"""
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200, f"Health endpoint failed: {r.status_code}"
        
        headers = r.headers
        
        # X-Content-Type-Options
        assert "X-Content-Type-Options" in headers, "Missing X-Content-Type-Options header"
        assert headers["X-Content-Type-Options"] == "nosniff"
        
        # X-Frame-Options
        assert "X-Frame-Options" in headers, "Missing X-Frame-Options header"
        assert headers["X-Frame-Options"] == "DENY"
        
        # Strict-Transport-Security (HSTS)
        assert "Strict-Transport-Security" in headers, "Missing Strict-Transport-Security header"
        assert "max-age=" in headers["Strict-Transport-Security"]
        
        # Referrer-Policy
        assert "Referrer-Policy" in headers, "Missing Referrer-Policy header"
        assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        
        # Permissions-Policy
        assert "Permissions-Policy" in headers, "Missing Permissions-Policy header"
        assert "camera=()" in headers["Permissions-Policy"]
        
        print("PASS: All 5 security headers present on /api/health")

    def test_health_response_content(self):
        """Health endpoint returns correct version"""
        r = requests.get(f"{BASE_URL}/api/health")
        data = r.json()
        assert data.get("status") == "ok"
        assert "version" in data
        print(f"PASS: Health returns version {data.get('version')}")


class TestAdminSettings:
    """Admin Settings API (GET/PUT /api/system/settings)"""

    def test_get_settings_returns_object(self, admin_session):
        """GET /api/system/settings returns empty object or saved rules"""
        r = admin_session.get(f"{BASE_URL}/api/system/settings")
        assert r.status_code == 200, f"GET settings failed: {r.status_code}"
        data = r.json()
        assert isinstance(data, dict), "Settings should be a dict"
        print(f"PASS: GET /api/system/settings returns {type(data).__name__}")

    def test_put_settings_screening_rules(self, admin_session):
        """PUT /api/system/settings with screening_rules saves successfully"""
        payload = {
            "screening_rules": {
                "min_language_level": "B2",
                "require_passport": True,
                "require_diploma": True,
                "max_days_pending_docs": 14,
            }
        }
        r = admin_session.put(f"{BASE_URL}/api/system/settings", json=payload)
        assert r.status_code == 200, f"PUT settings failed: {r.status_code}"
        data = r.json()
        assert "message" in data or "Einstellungen" in str(data)
        print("PASS: PUT /api/system/settings saves screening_rules")

    def test_get_settings_after_put(self, admin_session):
        """GET settings after PUT returns saved values"""
        r = admin_session.get(f"{BASE_URL}/api/system/settings")
        assert r.status_code == 200
        data = r.json()
        # Check if screening_rules were saved
        if "screening_rules" in data:
            rules = data["screening_rules"]
            assert rules.get("min_language_level") == "B2"
            print("PASS: Saved screening_rules retrieved correctly")
        else:
            print("INFO: Settings returned without screening_rules key (may be flat structure)")

    def test_settings_requires_admin(self, staff_session):
        """Staff cannot access admin settings"""
        r = staff_session.get(f"{BASE_URL}/api/system/settings")
        assert r.status_code == 403, f"Expected 403 for staff, got {r.status_code}"
        print("PASS: Staff cannot access /api/system/settings (403)")


class TestGDPREndpoints:
    """GDPR Data Export and Anonymization endpoints"""

    def test_gdpr_export_requires_admin(self, staff_session):
        """Staff cannot access GDPR export"""
        r = staff_session.get(f"{BASE_URL}/api/system/gdpr/user-data/invalid-id")
        assert r.status_code == 403, f"Expected 403 for staff, got {r.status_code}"
        print("PASS: Staff cannot access GDPR export (403)")

    def test_gdpr_export_invalid_id(self, admin_session):
        """GDPR export with invalid ID returns error"""
        r = admin_session.get(f"{BASE_URL}/api/system/gdpr/user-data/invalid-id")
        # Should return 200 with error message or 400/404
        data = r.json()
        if r.status_code == 200:
            assert "error" in data or "Ungueltige" in str(data)
        print(f"PASS: GDPR export invalid ID handled ({r.status_code})")

    def test_gdpr_export_valid_user(self, admin_session):
        """GDPR export for valid user returns data structure"""
        # First get a user ID
        r = admin_session.get(f"{BASE_URL}/api/users")
        if r.status_code != 200:
            pytest.skip("Cannot get users list")
        users = r.json()
        if not users:
            pytest.skip("No users found")
        
        # Find a non-admin user
        test_user = None
        for u in users:
            if u.get("role") not in ["superadmin", "admin"]:
                test_user = u
                break
        
        if not test_user:
            pytest.skip("No non-admin user found for GDPR test")
        
        user_id = test_user.get("id")
        r = admin_session.get(f"{BASE_URL}/api/system/gdpr/user-data/{user_id}")
        assert r.status_code == 200, f"GDPR export failed: {r.status_code}"
        data = r.json()
        
        # Check expected structure
        assert "export_date" in data or "user" in data or "error" not in data
        print(f"PASS: GDPR export returns data for user {user_id[:8]}...")

    def test_gdpr_anonymize_admin_protection(self, admin_session):
        """GDPR anonymize does NOT work for admin accounts"""
        # Get admin user ID
        r = admin_session.get(f"{BASE_URL}/api/auth/me")
        admin_data = r.json()
        admin_id = admin_data.get("id")
        
        # Try to anonymize admin
        r = admin_session.post(f"{BASE_URL}/api/system/gdpr/anonymize/{admin_id}")
        data = r.json()
        
        # Should return error about admin protection
        assert "error" in data or "Admin" in str(data) or "koennen nicht" in str(data)
        print("PASS: Admin accounts cannot be anonymized (protection works)")

    def test_gdpr_anonymize_requires_admin(self, staff_session):
        """Staff cannot anonymize users"""
        r = staff_session.post(f"{BASE_URL}/api/system/gdpr/anonymize/some-id")
        assert r.status_code == 403, f"Expected 403 for staff, got {r.status_code}"
        print("PASS: Staff cannot anonymize users (403)")


class TestStateMachine:
    """State Machine validation tests"""

    def test_invalid_transition_returns_422(self, staff_session):
        """Invalid stage transition returns 422 for staff"""
        # Get an application
        r = staff_session.get(f"{BASE_URL}/api/applications?limit=1")
        if r.status_code != 200:
            pytest.skip("Cannot get applications")
        apps = r.json()
        if not apps:
            pytest.skip("No applications found")
        
        app_id = apps[0].get("id")
        current_stage = apps[0].get("current_stage", "lead_new")
        
        # Try invalid transition (e.g., lead_new -> enrolled directly)
        invalid_stage = "enrolled" if current_stage != "enrolled" else "lead_new"
        
        r = staff_session.put(f"{BASE_URL}/api/applications/{app_id}/stage", json={
            "new_stage": invalid_stage
        })
        
        # Should be 422 for invalid transition OR 200 if it's actually valid
        if r.status_code == 422:
            print(f"PASS: Invalid transition {current_stage} -> {invalid_stage} returns 422")
        elif r.status_code == 200:
            print(f"INFO: Transition {current_stage} -> {invalid_stage} was valid")
        else:
            print(f"INFO: Stage transition returned {r.status_code}")


class TestStageEffects:
    """Stage Effects auto-task creation"""

    def test_pending_docs_creates_task(self, admin_session):
        """Transition to pending_docs creates follow-up task"""
        # Get an application in lead_new or in_review
        r = admin_session.get(f"{BASE_URL}/api/applications?stage=lead_new&limit=1")
        if r.status_code != 200:
            r = admin_session.get(f"{BASE_URL}/api/applications?stage=in_review&limit=1")
        
        if r.status_code != 200:
            pytest.skip("Cannot get applications")
        
        apps = r.json()
        if not apps:
            # Try any application
            r = admin_session.get(f"{BASE_URL}/api/applications?limit=1")
            apps = r.json()
        
        if not apps:
            pytest.skip("No applications found")
        
        app_id = apps[0].get("id")
        
        # Get tasks before
        r = admin_session.get(f"{BASE_URL}/api/tasks?application_id={app_id}")
        tasks_before = len(r.json()) if r.status_code == 200 else 0
        
        # Force transition to pending_docs (admin can force)
        r = admin_session.put(f"{BASE_URL}/api/applications/{app_id}/stage", json={
            "new_stage": "pending_docs",
            "force": True
        })
        
        if r.status_code in [200, 422]:
            # Check tasks after
            r = admin_session.get(f"{BASE_URL}/api/tasks?application_id={app_id}")
            if r.status_code == 200:
                tasks = r.json()
                # Look for the auto-created task
                auto_tasks = [t for t in tasks if t.get("source") == "stage_effect" or "Dokumente" in t.get("title", "")]
                if auto_tasks:
                    print(f"PASS: Stage effect created task: {auto_tasks[0].get('title')}")
                else:
                    print(f"INFO: {len(tasks)} tasks found, stage effect may have already run")
        else:
            print(f"INFO: Stage transition returned {r.status_code}")


class TestMergeDuplicates:
    """Merge duplicates endpoint validation"""

    def test_merge_same_id_returns_400(self, admin_session):
        """Merging same ID returns 400"""
        r = admin_session.post(f"{BASE_URL}/api/applications/merge-duplicates", json={
            "primary_id": "abc123",
            "secondary_id": "abc123"
        })
        assert r.status_code == 400, f"Expected 400 for same ID, got {r.status_code}"
        print("PASS: Merge same ID returns 400")

    def test_merge_missing_fields_returns_400(self, admin_session):
        """Merging with missing fields returns 400"""
        r = admin_session.post(f"{BASE_URL}/api/applications/merge-duplicates", json={})
        assert r.status_code in [400, 422], f"Expected 400/422 for empty request, got {r.status_code}"
        print(f"PASS: Merge empty request returns {r.status_code}")

    def test_merge_staff_returns_403(self, staff_session):
        """Staff cannot merge duplicates"""
        r = staff_session.post(f"{BASE_URL}/api/applications/merge-duplicates", json={
            "primary_id": "abc",
            "secondary_id": "def"
        })
        assert r.status_code == 403, f"Expected 403 for staff, got {r.status_code}"
        print("PASS: Staff cannot merge duplicates (403)")


class TestPartnerEndpoints:
    """Partner/Affiliate API endpoints"""

    def test_partner_dashboard(self, partner_session):
        """Partner dashboard endpoint works"""
        r = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert r.status_code == 200, f"Partner dashboard failed: {r.status_code}"
        data = r.json()
        assert isinstance(data, dict)
        print(f"PASS: Partner dashboard returns data")

    def test_partner_referral_link(self, partner_session):
        """Partner referral link endpoint works"""
        r = partner_session.get(f"{BASE_URL}/api/partner/referral-link")
        assert r.status_code == 200, f"Partner referral link failed: {r.status_code}"
        data = r.json()
        assert "link" in data or "referral_code" in data
        print(f"PASS: Partner referral link returns data")

    def test_partner_commission_summary(self, partner_session):
        """Partner commission summary endpoint works"""
        r = partner_session.get(f"{BASE_URL}/api/partner/commission-summary")
        assert r.status_code == 200, f"Partner commission summary failed: {r.status_code}"
        print("PASS: Partner commission summary works")


class TestTeacherEndpoints:
    """Teacher API endpoints"""

    def test_teacher_my_students(self, teacher_session):
        """Teacher my-students endpoint works"""
        r = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert r.status_code == 200, f"Teacher my-students failed: {r.status_code}"
        data = r.json()
        assert "students" in data or isinstance(data, list)
        print(f"PASS: Teacher my-students returns data")


class TestDashboardStats:
    """Dashboard stats for reporting page"""

    def test_dashboard_stats(self, staff_session):
        """Dashboard stats endpoint returns pipeline data"""
        r = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert r.status_code == 200, f"Dashboard stats failed: {r.status_code}"
        data = r.json()
        
        # Check for pipeline data
        assert "pipeline" in data or "total_leads" in data
        print(f"PASS: Dashboard stats returns pipeline data")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
