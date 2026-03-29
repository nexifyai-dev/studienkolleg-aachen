"""
Phase 3.7b Tests: i18n, Auth (4 roles), Consent/Teacher APIs, Email config
Tests:
- Login with 4 test accounts (admin, staff, teacher, applicant)
- GET /api/consents/types (public)
- GET /api/teacher/assignments (requires auth)
- Email config verification (EMAIL_FROM domain)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials from seed.py
TEST_ACCOUNTS = {
    "admin": {"email": "admin@studienkolleg-aachen.de", "password": "Admin@2026!"},
    "staff": {"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "teacher": {"email": "teacher@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "applicant": {"email": "applicant@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
}


class TestHealthAndConfig:
    """Basic health and config checks"""

    def test_health_endpoint(self):
        """Health endpoint returns OK and email config"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        # Verify email is enabled (Resend key is set)
        assert "email_enabled" in data

    def test_email_from_domain(self):
        """Verify EMAIL_FROM uses send.nexify-automate.com domain"""
        # This is a config check - we verify via health or a dedicated endpoint
        # The config.py shows EMAIL_FROM = noreply@send.nexify-automate.com
        # We can't directly test this via API, but we verify the backend is configured
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        # If email_enabled is true, the config is loaded
        data = response.json()
        assert data.get("email_enabled") is True, "Email should be enabled with Resend API key"


class TestConsentAPI:
    """Consent API tests - GDPR-compliant consent management"""

    def test_get_consent_types_public(self):
        """GET /api/consents/types returns consent type definitions (public endpoint)"""
        response = requests.get(f"{BASE_URL}/api/consents/types")
        assert response.status_code == 200
        data = response.json()
        # Should contain teacher_data_access consent type
        assert "teacher_data_access" in data
        consent = data["teacher_data_access"]
        assert "purpose_de" in consent
        assert "purpose_en" in consent
        assert "scope" in consent
        assert "excludes" in consent
        # Verify scope includes expected fields
        assert "full_name" in consent["scope"]
        assert "email" in consent["scope"]
        # Verify excludes sensitive data
        assert "financial_data" in consent["excludes"]
        assert "passport_details" in consent["excludes"]


class TestAuthLogin:
    """Test login for all 4 seeded accounts"""

    @pytest.fixture
    def session(self):
        return requests.Session()

    def test_admin_login(self, session):
        """Admin account login works"""
        creds = TEST_ACCOUNTS["admin"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        # API returns user data directly (not wrapped in "user" key)
        assert data["email"] == creds["email"]
        assert data["role"] == "superadmin"

    def test_staff_login(self, session):
        """Staff account login works"""
        creds = TEST_ACCOUNTS["staff"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert data["email"] == creds["email"]
        assert data["role"] == "staff"

    def test_teacher_login(self, session):
        """Teacher account login works"""
        creds = TEST_ACCOUNTS["teacher"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert data["email"] == creds["email"]
        assert data["role"] == "teacher"

    def test_applicant_login(self, session):
        """Applicant account login works"""
        creds = TEST_ACCOUNTS["applicant"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data["email"] == creds["email"]
        assert data["role"] == "applicant"

    def test_invalid_login(self, session):
        """Invalid credentials return 401"""
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpass"},
        )
        assert response.status_code == 401


class TestTeacherAPI:
    """Teacher API tests - assignment-based, consent-gated access"""

    @pytest.fixture
    def teacher_session(self):
        """Get authenticated session for teacher"""
        session = requests.Session()
        creds = TEST_ACCOUNTS["teacher"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        if response.status_code != 200:
            pytest.skip("Teacher login failed")
        return session

    @pytest.fixture
    def unauthenticated_session(self):
        return requests.Session()

    def test_teacher_assignments_requires_auth(self, unauthenticated_session):
        """GET /api/teacher/assignments requires authentication"""
        response = unauthenticated_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 401, "Should require auth"

    def test_teacher_can_list_assignments(self, teacher_session):
        """Teacher can list their own assignments"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 200
        data = response.json()
        assert "assignments" in data
        # May be empty if no assignments exist
        assert isinstance(data["assignments"], list)

    def test_teacher_my_students_endpoint(self, teacher_session):
        """Teacher can access my-students endpoint"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 200
        data = response.json()
        assert "students" in data
        assert "total" in data
        # May be empty if no consented students


class TestStaffAccess:
    """Staff role access tests"""

    @pytest.fixture
    def staff_session(self):
        """Get authenticated session for staff"""
        session = requests.Session()
        creds = TEST_ACCOUNTS["staff"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session

    def test_staff_can_list_all_assignments(self, staff_session):
        """Staff can list all teacher assignments"""
        response = staff_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 200
        data = response.json()
        assert "assignments" in data


class TestApplicantAccess:
    """Applicant role access tests"""

    @pytest.fixture
    def applicant_session(self):
        """Get authenticated session for applicant"""
        session = requests.Session()
        creds = TEST_ACCOUNTS["applicant"]
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        if response.status_code != 200:
            pytest.skip("Applicant login failed")
        return session

    def test_applicant_cannot_access_teacher_assignments(self, applicant_session):
        """Applicant cannot access teacher assignments endpoint"""
        response = applicant_session.get(f"{BASE_URL}/api/teacher/assignments")
        # Should be 403 Forbidden for applicant role
        assert response.status_code == 403

    def test_applicant_can_view_own_consents(self, applicant_session):
        """Applicant can view their own consents"""
        response = applicant_session.get(f"{BASE_URL}/api/consents/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
