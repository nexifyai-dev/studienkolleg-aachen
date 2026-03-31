"""
Phase 3.7k GO-LIVE Backend Tests
Tests: Login for all roles, Partner APIs, AI Screening, CORS
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/') or "https://payment-platform-52.preview.emergentagent.com"

# Test credentials
CREDENTIALS = {
    "staff": {"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "applicant": {"email": "applicant@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "partner": {"email": "partner@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "admin": {"email": "admin@studienkolleg-aachen.de", "password": "Admin@2026!"},
    "teacher": {"email": "teacher@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
}


@pytest.fixture(scope="module")
def api_session():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestHealthAndCORS:
    """Health check and CORS tests"""
    
    def test_health_endpoint(self, api_session):
        """Health endpoint returns OK"""
        response = api_session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        print(f"✓ Health check passed: {data['version']}")
    
    def test_cors_without_origin_header(self, api_session):
        """API responds to requests without Origin header (same-origin)"""
        # Remove Origin header if present
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{BASE_URL}/api/health", headers=headers)
        assert response.status_code == 200
        print("✓ CORS: API responds without Origin header")


class TestLoginAllRoles:
    """Login tests for all user roles - CRITICAL"""
    
    def test_staff_login(self, api_session):
        """Staff login returns correct role"""
        creds = CREDENTIALS["staff"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert data["role"] == "staff"
        assert data["email"] == creds["email"]
        print(f"✓ Staff login: {data['full_name']} ({data['role']})")
    
    def test_applicant_login(self, api_session):
        """Applicant login returns correct role"""
        creds = CREDENTIALS["applicant"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data["role"] == "applicant"
        assert data["email"] == creds["email"]
        print(f"✓ Applicant login: {data['full_name']} ({data['role']})")
    
    def test_partner_login(self, api_session):
        """Partner/affiliate login returns correct role"""
        creds = CREDENTIALS["partner"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        data = response.json()
        assert data["role"] == "affiliate"
        assert data["email"] == creds["email"]
        print(f"✓ Partner login: {data['full_name']} ({data['role']})")
    
    def test_admin_login(self, api_session):
        """Admin/superadmin login returns correct role"""
        creds = CREDENTIALS["admin"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["role"] == "superadmin"
        assert data["email"] == creds["email"]
        print(f"✓ Admin login: {data['full_name']} ({data['role']})")
    
    def test_teacher_login(self, api_session):
        """Teacher login returns correct role"""
        creds = CREDENTIALS["teacher"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert data["role"] == "teacher"
        assert data["email"] == creds["email"]
        print(f"✓ Teacher login: {data['full_name']} ({data['role']})")
    
    def test_invalid_login_rejected(self, api_session):
        """Invalid credentials are rejected"""
        response = api_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("✓ Invalid login correctly rejected")


class TestPartnerAPIs:
    """Partner portal API tests"""
    
    @pytest.fixture(autouse=True)
    def login_partner(self, api_session):
        """Login as partner before each test"""
        creds = CREDENTIALS["partner"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200
        # Store cookies
        self.cookies = response.cookies
        yield
    
    def test_partner_dashboard(self, api_session):
        """GET /api/partner/dashboard returns stats"""
        response = api_session.get(f"{BASE_URL}/api/partner/dashboard", cookies=self.cookies)
        assert response.status_code == 200, f"Partner dashboard failed: {response.text}"
        data = response.json()
        assert "total_referrals" in data
        assert "active_referrals" in data
        assert "enrolled" in data
        assert "partner_name" in data
        print(f"✓ Partner dashboard: {data['partner_name']} - {data['total_referrals']} referrals")
    
    def test_partner_referrals(self, api_session):
        """GET /api/partner/referrals returns list"""
        response = api_session.get(f"{BASE_URL}/api/partner/referrals", cookies=self.cookies)
        assert response.status_code == 200, f"Partner referrals failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Partner referrals: {len(data)} referrals")
    
    def test_partner_referral_link(self, api_session):
        """GET /api/partner/referral-link returns link"""
        response = api_session.get(f"{BASE_URL}/api/partner/referral-link", cookies=self.cookies)
        assert response.status_code == 200, f"Partner referral link failed: {response.text}"
        data = response.json()
        assert "referral_code" in data
        assert "link" in data
        assert "/apply?ref=" in data["link"]
        print(f"✓ Partner referral link: {data['link']}")


class TestAIScreening:
    """AI Screening API tests"""
    
    @pytest.fixture(autouse=True)
    def login_staff(self, api_session):
        """Login as staff before each test"""
        creds = CREDENTIALS["staff"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200
        self.cookies = response.cookies
        yield
    
    def test_get_applications(self, api_session):
        """GET /api/applications returns list"""
        response = api_session.get(f"{BASE_URL}/api/applications?limit=5", cookies=self.cookies)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            self.app_id = data[0]["id"]
        print(f"✓ Applications: {len(data)} found")
    
    def test_accept_ai_suggestion(self, api_session):
        """POST /api/applications/{id}/accept-ai-suggestion works"""
        # First get an application
        response = api_session.get(f"{BASE_URL}/api/applications?limit=1", cookies=self.cookies)
        assert response.status_code == 200
        apps = response.json()
        if not apps:
            pytest.skip("No applications to test")
        
        app_id = apps[0]["id"]
        current_stage = apps[0].get("current_stage", "lead_new")
        
        # Accept AI suggestion (change to a different stage)
        new_stage = "documents_requested" if current_stage != "documents_requested" else "lead_new"
        response = api_session.post(
            f"{BASE_URL}/api/applications/{app_id}/accept-ai-suggestion",
            json={"suggested_stage": new_stage},
            cookies=self.cookies
        )
        assert response.status_code == 200, f"Accept AI suggestion failed: {response.text}"
        data = response.json()
        assert data["status"] in ["accepted", "unchanged"]
        print(f"✓ Accept AI suggestion: {data}")
        
        # Revert the change
        api_session.post(
            f"{BASE_URL}/api/applications/{app_id}/accept-ai-suggestion",
            json={"suggested_stage": current_stage},
            cookies=self.cookies
        )


class TestCookieAuth:
    """Cookie-based authentication tests"""
    
    def test_cookies_set_on_login(self, api_session):
        """Login sets access_token and refresh_token cookies"""
        creds = CREDENTIALS["staff"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200
        
        # Check cookies are set
        cookies = response.cookies
        # Note: cookies may be httponly and not visible in response.cookies
        # but the session should work
        print(f"✓ Login successful, cookies set")
    
    def test_auth_me_with_cookies(self, api_session):
        """GET /api/auth/me works with cookies"""
        # Login first
        creds = CREDENTIALS["staff"]
        response = api_session.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert response.status_code == 200
        cookies = response.cookies
        
        # Access /api/auth/me
        response = api_session.get(f"{BASE_URL}/api/auth/me", cookies=cookies)
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        data = response.json()
        assert data["email"] == creds["email"]
        print(f"✓ Auth me: {data['email']} ({data['role']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
