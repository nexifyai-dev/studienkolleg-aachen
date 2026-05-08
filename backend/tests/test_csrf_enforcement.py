"""
CSRF Double-Submit Cookie Tests - Iteration 98
Tests CSRF enforcement mode where missing/invalid tokens return 403.

Test Coverage:
- Login is CSRF-exempt (should work without token)
- POST/PUT/DELETE with valid CSRF token should work
- POST/PUT/DELETE without CSRF token should return 403
- GET requests are exempt (safe methods)
- Public endpoints are exempt
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://invoice-fix-31.preview.emergentagent.com"

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestCSRFExemptEndpoints:
    """Test endpoints that should work WITHOUT CSRF token"""
    
    def test_login_exempt_from_csrf(self):
        """Login endpoint should work without CSRF token"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "email" in data or "id" in data, "Login response missing user data"
        print(f"✓ Login works without CSRF token, user: {data.get('email')}")
        
    def test_login_sets_csrf_cookie(self):
        """After login, csrf_token cookie should be set"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert response.status_code == 200
        
        # Check if csrf_token cookie is set
        csrf_cookie = session.cookies.get('csrf_token')
        assert csrf_cookie is not None, "csrf_token cookie not set after login"
        assert len(csrf_cookie) > 0, "csrf_token cookie is empty"
        print(f"✓ csrf_token cookie set after login: {csrf_cookie[:16]}...")
        
    def test_register_exempt_from_csrf(self):
        """Register endpoint should work without CSRF token (but may fail for other reasons)"""
        session = requests.Session()
        # Use unique email to avoid duplicate errors
        import time
        unique_email = f"test_csrf_{int(time.time())}@example.com"
        response = session.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": unique_email,
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        # Should NOT be 403 (CSRF error) - other errors are acceptable
        assert response.status_code != 403, f"Register blocked by CSRF: {response.text}"
        print(f"✓ Register endpoint not blocked by CSRF (status: {response.status_code})")
        
    def test_health_exempt_from_csrf(self):
        """Health endpoint should work without CSRF token"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint works without CSRF")
        
    def test_get_requests_exempt(self):
        """GET requests should work without CSRF token"""
        session = requests.Session()
        # Login first to get auth
        session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        
        # GET request should work without CSRF header
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"GET /api/auth/me failed: {response.text}"
        print("✓ GET requests work without CSRF header")


class TestCSRFEnforcement:
    """Test that CSRF is enforced on protected endpoints"""
    
    def test_logout_without_csrf_returns_403(self):
        """POST /api/auth/logout without CSRF token should return 403"""
        session = requests.Session()
        # Login first
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_resp.status_code == 200
        
        # Get the CSRF cookie but DON'T send it as header
        csrf_cookie = session.cookies.get('csrf_token')
        assert csrf_cookie is not None, "No CSRF cookie set"
        
        # Try logout WITHOUT CSRF header - should fail with 403
        response = session.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        assert "CSRF" in response.text or "csrf" in response.text.lower(), "Error should mention CSRF"
        print("✓ POST without CSRF header correctly returns 403")
        
    def test_logout_with_wrong_csrf_returns_403(self):
        """POST with wrong CSRF token should return 403"""
        session = requests.Session()
        # Login first
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_resp.status_code == 200
        
        # Send wrong CSRF token
        response = session.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"x-csrf-token": "wrong_token_12345"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        print("✓ POST with wrong CSRF token correctly returns 403")
        
    def test_logout_with_valid_csrf_works(self):
        """POST /api/auth/logout with valid CSRF token should work"""
        session = requests.Session()
        # Login first
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_resp.status_code == 200
        
        # Get CSRF token from cookie
        csrf_token = session.cookies.get('csrf_token')
        assert csrf_token is not None, "No CSRF cookie set"
        
        # Logout WITH correct CSRF header
        response = session.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"x-csrf-token": csrf_token}
        )
        assert response.status_code == 200, f"Logout failed: {response.text}"
        print("✓ POST with valid CSRF token works (200)")


class TestCSRFWithMutations:
    """Test CSRF with various mutation endpoints"""
    
    @pytest.fixture
    def authenticated_session(self):
        """Create authenticated session with CSRF token"""
        session = requests.Session()
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_resp.status_code == 200
        csrf_token = session.cookies.get('csrf_token')
        return session, csrf_token
    
    def test_put_without_csrf_returns_403(self, authenticated_session):
        """PUT request without CSRF should return 403"""
        session, csrf_token = authenticated_session
        
        # Try PUT without CSRF header
        response = session.put(
            f"{BASE_URL}/api/users/me",
            json={"first_name": "Test"}
        )
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ PUT without CSRF header returns 403")
        
    def test_put_with_csrf_works(self, authenticated_session):
        """PUT request with valid CSRF should work (not blocked by CSRF)"""
        session, csrf_token = authenticated_session
        
        # First get user info to get user_id
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        user_id = me_resp.json().get('id')
        
        response = session.put(
            f"{BASE_URL}/api/users/{user_id}",
            json={"first_name": "TestUpdate"},
            headers={"x-csrf-token": csrf_token}
        )
        # Should not be 403 with "CSRF" in message - other 403s (permission) are OK
        if response.status_code == 403:
            # Check if it's CSRF error or permission error
            resp_text = response.text.lower()
            assert "csrf" not in resp_text, f"PUT blocked by CSRF: {response.text}"
            print(f"✓ PUT with CSRF token not blocked by CSRF (403 is permission, not CSRF)")
        else:
            print(f"✓ PUT with CSRF token works (status: {response.status_code})")
        
    def test_delete_without_csrf_returns_403(self, authenticated_session):
        """DELETE request without CSRF should return 403"""
        session, csrf_token = authenticated_session
        
        # Try DELETE without CSRF header (use a non-existent resource to avoid side effects)
        response = session.delete(f"{BASE_URL}/api/notifications/nonexistent123")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        print("✓ DELETE without CSRF header returns 403")


class TestApplicantCSRF:
    """Test CSRF for applicant role"""
    
    def test_applicant_login_and_csrf(self):
        """Applicant login should set CSRF cookie"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD}
        )
        assert response.status_code == 200
        
        csrf_token = session.cookies.get('csrf_token')
        assert csrf_token is not None, "CSRF cookie not set for applicant"
        print(f"✓ Applicant login sets CSRF cookie")
        
    def test_applicant_logout_with_csrf(self):
        """Applicant logout should work with CSRF token"""
        session = requests.Session()
        login_resp = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD}
        )
        assert login_resp.status_code == 200
        
        csrf_token = session.cookies.get('csrf_token')
        
        # Logout with CSRF
        response = session.post(
            f"{BASE_URL}/api/auth/logout",
            headers={"x-csrf-token": csrf_token}
        )
        assert response.status_code == 200, f"Applicant logout failed: {response.text}"
        print("✓ Applicant logout works with CSRF token")


class TestPublicEndpointsCSRF:
    """Test that public endpoints are CSRF-exempt"""
    
    def test_public_cost_simulator(self):
        """Public cost simulator should work without CSRF"""
        response = requests.post(
            f"{BASE_URL}/api/public/cost-simulator",
            json={"country": "Germany", "duration_months": 12}
        )
        # Should not be 403
        assert response.status_code != 403, f"Public endpoint blocked by CSRF: {response.text}"
        print(f"✓ Public cost simulator not blocked by CSRF (status: {response.status_code})")
        
    def test_public_appointments(self):
        """Public appointments should work without CSRF"""
        response = requests.get(f"{BASE_URL}/api/public/appointments/slots")
        # Should not be 403
        assert response.status_code != 403, f"Public endpoint blocked by CSRF"
        print(f"✓ Public appointments not blocked by CSRF (status: {response.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
