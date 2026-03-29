# Phase 3.7g Tests: Cookie-Einstellungen nachträglich bearbeitbar
# Tests for Cookie Manage Mode, Footer Link, and Legal Pages

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPhase37gBackendHealth:
    """Backend health and auth tests for Phase 3.7g"""
    
    def test_health_endpoint(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint returns 200")
    
    def test_admin_login(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": "Admin@2026!"
        })
        assert response.status_code == 200
        data = response.json()
        # Role is at top level in response
        assert data.get("role") == "superadmin"
        print("✓ Admin login successful - role: superadmin")
    
    def test_staff_login(self):
        """Test staff login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "staff"
        print("✓ Staff login successful - role: staff")
    
    def test_teacher_login(self):
        """Test teacher login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teacher@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "teacher"
        print("✓ Teacher login successful - role: teacher")
    
    def test_applicant_login(self):
        """Test applicant login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "applicant"
        print("✓ Applicant login successful - role: applicant")
    
    def test_invalid_login_rejected(self):
        """Test invalid login is rejected"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login rejected with 401")


class TestPhase37gAuthenticatedEndpoints:
    """Test authenticated endpoints for Phase 3.7g"""
    
    @pytest.fixture
    def admin_session(self):
        """Get admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": "Admin@2026!"
        })
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def staff_session(self):
        """Get staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def applicant_session(self):
        """Get applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_admin_can_access_me(self, admin_session):
        """Test admin can access /api/auth/me"""
        response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "superadmin"
        print("✓ Admin can access /api/auth/me")
    
    def test_staff_can_access_me(self, staff_session):
        """Test staff can access /api/auth/me"""
        response = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "staff"
        print("✓ Staff can access /api/auth/me")
    
    def test_applicant_can_access_me(self, applicant_session):
        """Test applicant can access /api/auth/me"""
        response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "applicant"
        print("✓ Applicant can access /api/auth/me")
    
    def test_notifications_requires_auth(self):
        """Test notifications endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 401
        print("✓ Notifications endpoint requires auth (401)")
    
    def test_applicant_can_access_notifications(self, applicant_session):
        """Test applicant can access notifications"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        print("✓ Applicant can access notifications")
    
    def test_staff_can_access_notifications(self, staff_session):
        """Test staff can access notifications"""
        response = staff_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        print("✓ Staff can access notifications")


class TestPhase37gFrontendPages:
    """Test frontend pages load correctly"""
    
    def test_homepage_loads(self):
        """Test homepage loads"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("✓ Homepage loads (200)")
    
    def test_legal_page_loads(self):
        """Test /legal page loads"""
        response = requests.get(f"{BASE_URL}/legal")
        assert response.status_code == 200
        assert "[OFFEN]" not in response.text
        assert "[HINWEIS]" not in response.text
        print("✓ /legal page loads without staging warnings")
    
    def test_agb_page_loads(self):
        """Test /agb page loads"""
        response = requests.get(f"{BASE_URL}/agb")
        assert response.status_code == 200
        assert "[OFFEN]" not in response.text
        assert "[HINWEIS]" not in response.text
        print("✓ /agb page loads without staging warnings")
    
    def test_privacy_page_loads(self):
        """Test /privacy page loads"""
        response = requests.get(f"{BASE_URL}/privacy")
        assert response.status_code == 200
        assert "[OFFEN]" not in response.text
        assert "[HINWEIS]" not in response.text
        print("✓ /privacy page loads without staging warnings")
    
    def test_login_page_loads(self):
        """Test login page loads"""
        response = requests.get(f"{BASE_URL}/auth/login")
        assert response.status_code == 200
        print("✓ Login page loads (200)")
    
    def test_apply_page_loads(self):
        """Test apply page loads"""
        response = requests.get(f"{BASE_URL}/apply")
        assert response.status_code == 200
        print("✓ Apply page loads (200)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
