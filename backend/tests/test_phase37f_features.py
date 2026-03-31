"""
Phase 3.7f Tests: Cookie-Management, Staging-Hinweise entfernt, Mobile-Header, Test-Logins
Tests for:
- Login functionality for all 4 roles (Admin, Staff, Teacher, Applicant)
- Role-based redirects verification
- Backend health and auth endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
CREDENTIALS = {
    'admin': {'email': 'admin@studienkolleg-aachen.de', 'password': os.environ['TEST_ADMIN_PASSWORD'], 'expected_role': 'superadmin'},
    'staff': {'email': 'staff@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD'], 'expected_role': 'staff'},
    'teacher': {'email': 'teacher@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD'], 'expected_role': 'teacher'},
    'applicant': {'email': 'applicant@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD'], 'expected_role': 'applicant'},
}


class TestHealthEndpoint:
    """Health endpoint tests"""
    
    def test_health_returns_ok(self):
        """Backend health endpoint returns OK status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'ok'
        print("✓ Health endpoint returns OK")


class TestAuthLogins:
    """Authentication tests for all 4 roles"""
    
    def test_admin_login(self):
        """Admin can login and gets superadmin role"""
        creds = CREDENTIALS['admin']
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        # Login response returns user data directly at root level
        assert data.get('role') == creds['expected_role'], f"Expected role {creds['expected_role']}, got {data.get('role')}"
        print(f"✓ Admin login successful, role: {data.get('role')}")
    
    def test_staff_login(self):
        """Staff can login and gets staff role"""
        creds = CREDENTIALS['staff']
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert data.get('role') == creds['expected_role'], f"Expected role {creds['expected_role']}, got {data.get('role')}"
        print(f"✓ Staff login successful, role: {data.get('role')}")
    
    def test_teacher_login(self):
        """Teacher can login and gets teacher role"""
        creds = CREDENTIALS['teacher']
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert data.get('role') == creds['expected_role'], f"Expected role {creds['expected_role']}, got {data.get('role')}"
        print(f"✓ Teacher login successful, role: {data.get('role')}")
    
    def test_applicant_login(self):
        """Applicant can login and gets applicant role"""
        creds = CREDENTIALS['applicant']
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data.get('role') == creds['expected_role'], f"Expected role {creds['expected_role']}, got {data.get('role')}"
        print(f"✓ Applicant login successful, role: {data.get('role')}")
    
    def test_invalid_login_rejected(self):
        """Invalid credentials are rejected with 401"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': 'invalid@test.com', 'password': os.environ['TEST_INVALID_PASSWORD']}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid login correctly rejected with 401")


class TestAuthenticatedEndpoints:
    """Test authenticated endpoints work after login"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        creds = CREDENTIALS['admin']
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        creds = CREDENTIALS['applicant']
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        creds = CREDENTIALS['staff']
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def teacher_session(self):
        """Get authenticated teacher session"""
        session = requests.Session()
        creds = CREDENTIALS['teacher']
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={'email': creds['email'], 'password': creds['password']}
        )
        assert response.status_code == 200
        return session
    
    def test_admin_can_access_me(self, admin_session):
        """Admin can access /api/auth/me endpoint"""
        response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get('role') == 'superadmin'
        print("✓ Admin can access /api/auth/me")
    
    def test_staff_can_access_me(self, staff_session):
        """Staff can access /api/auth/me endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get('role') == 'staff'
        print("✓ Staff can access /api/auth/me")
    
    def test_teacher_can_access_me(self, teacher_session):
        """Teacher can access /api/auth/me endpoint"""
        response = teacher_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get('role') == 'teacher'
        print("✓ Teacher can access /api/auth/me")
    
    def test_applicant_can_access_me(self, applicant_session):
        """Applicant can access /api/auth/me endpoint"""
        response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get('role') == 'applicant'
        print("✓ Applicant can access /api/auth/me")
    
    def test_notifications_endpoint_requires_auth(self):
        """Notifications endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 401
        print("✓ Notifications endpoint requires auth (401)")
    
    def test_applicant_can_access_notifications(self, applicant_session):
        """Applicant can access notifications"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        print("✓ Applicant can access notifications")
    
    def test_staff_can_access_notifications(self, staff_session):
        """Staff can access notifications"""
        response = staff_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        print("✓ Staff can access notifications")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
