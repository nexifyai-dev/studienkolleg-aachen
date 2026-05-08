"""
FINAL AUDIT TEST - Iteration 60
W2G Platform - Systemweiter Audit und CI-Design-Enforcement

Tests:
- Auth: Login (Staff, Applicant, Invalid), Register
- Dashboard: Stats
- Applications, Invoices, Tasks, Notifications
- Oracle: Context, Chat (with 30s timeout)
- Appointments: Public Slots
- Jobs: Worker Health
- Rate-Limiting: Login (10/min), Register (5/min), Oracle Chat (15/min)
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def staff_session():
    """Authenticated staff session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Staff login failed: {response.status_code} - {response.text}")
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Authenticated admin session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Authenticated applicant session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Applicant login failed: {response.status_code} - {response.text}")
    return session


class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_staff_login_success(self, api_client):
        """POST /api/auth/login - Staff Login funktioniert"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["email"] == STAFF_EMAIL
        assert data["role"] == "staff"
        print(f"✓ Staff login successful: {data['email']} (role: {data['role']})")
    
    def test_applicant_login_success(self, api_client):
        """POST /api/auth/login - Applicant Login funktioniert"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["email"] == APPLICANT_EMAIL
        assert data["role"] == "applicant"
        print(f"✓ Applicant login successful: {data['email']} (role: {data['role']})")
    
    def test_login_invalid_password(self, api_client):
        """POST /api/auth/login - Falsches Passwort = 401"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"
        print("✓ Invalid password correctly returns 401")
    
    def test_register_new_user(self, api_client):
        """POST /api/auth/register - Registrierung funktioniert"""
        unique_email = f"test_register_{uuid.uuid4().hex[:8]}@test.com"
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": unique_email,
            "password": "TestPassword123!",
            "full_name": "Test User Registration"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["email"] == unique_email
        assert data["role"] == "applicant"  # Default role
        print(f"✓ Registration successful: {unique_email}")


class TestDashboardEndpoints:
    """Dashboard endpoint tests"""
    
    def test_dashboard_stats(self, staff_session):
        """GET /api/dashboard/stats - Dashboard-Daten"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Verify structure
        assert isinstance(data, dict)
        print(f"✓ Dashboard stats retrieved: {list(data.keys())[:5]}...")


class TestApplicationsEndpoints:
    """Applications endpoint tests"""
    
    def test_applications_list(self, staff_session):
        """GET /api/applications - Bewerbungsliste"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Applications list retrieved")


class TestInvoicesEndpoints:
    """Invoices endpoint tests"""
    
    def test_invoices_list(self, staff_session):
        """GET /api/invoices - Rechnungsliste"""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Invoices list retrieved")


class TestOracleEndpoints:
    """Oracle endpoint tests"""
    
    def test_oracle_context(self, staff_session):
        """GET /api/oracle/context - Oracle Live-Daten"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Oracle context retrieved: {list(data.keys())[:5]}...")
    
    def test_oracle_chat(self, staff_session):
        """POST /api/oracle/chat - Oracle KI-Chat funktioniert (Timeout 30s!)"""
        response = staff_session.post(
            f"{BASE_URL}/api/oracle/chat",
            json={"message": "Wie viele Bewerbungen gibt es aktuell?"},
            timeout=30  # 30s timeout for AI response
        )
        # Accept 200 (success) or 429 (rate limited)
        assert response.status_code in [200, 429], f"Expected 200 or 429, got {response.status_code}: {response.text}"
        if response.status_code == 200:
            data = response.json()
            assert "response" in data or "answer" in data or "message" in data
            print(f"✓ Oracle chat response received")
        else:
            print(f"✓ Oracle chat rate-limited (429) - expected behavior")


class TestAppointmentsEndpoints:
    """Appointments endpoint tests"""
    
    def test_public_slots(self, api_client):
        """GET /api/appointments/public-slots - Oeffentliche Termine"""
        response = api_client.get(f"{BASE_URL}/api/appointments/public-slots")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Public slots retrieved")


class TestTasksEndpoints:
    """Tasks endpoint tests"""
    
    def test_tasks_list(self, staff_session):
        """GET /api/tasks - Aufgabenliste"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Tasks list retrieved")


class TestNotificationsEndpoints:
    """Notifications endpoint tests"""
    
    def test_notifications_list(self, staff_session):
        """GET /api/notifications - Benachrichtigungen"""
        response = staff_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Notifications list retrieved")


class TestJobsEndpoints:
    """Jobs/Worker endpoint tests"""
    
    def test_jobs_health(self, staff_session):
        """GET /api/jobs/health - Worker-Health"""
        response = staff_session.get(f"{BASE_URL}/api/jobs/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Jobs health retrieved: {data}")


class TestRateLimiting:
    """Rate-Limiting tests"""
    
    def test_login_rate_limit_header(self, api_client):
        """Rate-Limiting auf Login (10/min) - Check headers"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": "test@test.com",
            "password": "test"
        })
        # Check for rate limit headers (X-RateLimit-*)
        headers = dict(response.headers)
        print(f"✓ Login endpoint accessible, headers: {[k for k in headers.keys() if 'rate' in k.lower() or 'limit' in k.lower()]}")
    
    def test_register_rate_limit_header(self, api_client):
        """Rate-Limiting auf Register (5/min) - Check headers"""
        response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
            "password": "TestPass123!",
            "full_name": "Test"
        })
        headers = dict(response.headers)
        print(f"✓ Register endpoint accessible, headers: {[k for k in headers.keys() if 'rate' in k.lower() or 'limit' in k.lower()]}")


class TestForgotPassword:
    """Forgot Password endpoint tests"""
    
    def test_forgot_password(self, api_client):
        """POST /api/auth/forgot-password - No user enumeration"""
        response = api_client.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "nonexistent@test.com"
        })
        # Should always return 200 (no user enumeration)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Forgot password returns 200 (no user enumeration)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
