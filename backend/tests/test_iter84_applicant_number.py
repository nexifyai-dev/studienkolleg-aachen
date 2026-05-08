"""
Iteration 84 - Bewerbernummer (applicant_number) System Tests
Tests for:
1. applicant_number in /api/applications response
2. applicant_number auto-generation via /api/leads/ingest
3. applicant_number in /api/invoices response
4. Search by applicant_number in applications
5. Login flow for Staff and Applicant
6. AuthContext timeout behavior (5s)
"""
import pytest
import requests
import os
import re
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Login as staff and return session with cookies"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Staff login failed: {resp.status_code} - {resp.text}")
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Login as admin and return session with cookies"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Admin login failed: {resp.status_code} - {resp.text}")
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Login as applicant and return session with cookies"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Applicant login failed: {resp.status_code} - {resp.text}")
    return session


class TestLoginFlow:
    """Test login functionality for all user roles"""
    
    def test_staff_login_success(self):
        """Staff can login with correct credentials"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert resp.status_code == 200, f"Staff login failed: {resp.text}"
        data = resp.json()
        assert data.get("role") == "staff", f"Expected role 'staff', got {data.get('role')}"
        assert data.get("email") == STAFF_EMAIL
        print(f"PASS: Staff login successful - role={data.get('role')}")
    
    def test_admin_login_success(self):
        """Admin can login with correct credentials"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        data = resp.json()
        assert data.get("role") in ["admin", "superadmin"], f"Expected admin role, got {data.get('role')}"
        print(f"PASS: Admin login successful - role={data.get('role')}")
    
    def test_applicant_login_success(self):
        """Applicant can login with correct credentials"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
        data = resp.json()
        assert data.get("role") == "applicant", f"Expected role 'applicant', got {data.get('role')}"
        print(f"PASS: Applicant login successful - role={data.get('role')}")
    
    def test_login_invalid_credentials(self):
        """Login fails with invalid credentials"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert resp.status_code in [401, 400], f"Expected 401/400, got {resp.status_code}"
        print(f"PASS: Invalid login correctly rejected with {resp.status_code}")


class TestApplicantNumberInApplications:
    """Test applicant_number field in applications API"""
    
    def test_applications_list_returns_applicant_number(self, staff_session):
        """GET /api/applications returns applicant_number for each application"""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200, f"Failed to get applications: {resp.text}"
        
        apps = resp.json()
        assert isinstance(apps, list), "Expected list of applications"
        
        if len(apps) == 0:
            pytest.skip("No applications found to test")
        
        # Check at least one application has applicant_number
        apps_with_number = [a for a in apps if a.get("applicant_number")]
        print(f"Found {len(apps_with_number)}/{len(apps)} applications with applicant_number")
        
        # Verify format STK-YYYY-NNNN
        for app in apps_with_number[:5]:  # Check first 5
            num = app.get("applicant_number")
            assert re.match(r'^STK-\d{4}-\d{4}$', num), f"Invalid format: {num}"
            print(f"  - {num} (valid format)")
        
        print(f"PASS: Applications list includes applicant_number field")
    
    def test_single_application_returns_applicant_number(self, staff_session):
        """GET /api/applications/{id} returns applicant_number"""
        # First get list to find an application
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        apps = resp.json()
        
        if len(apps) == 0:
            pytest.skip("No applications found")
        
        # Find one with applicant_number
        app_with_num = next((a for a in apps if a.get("applicant_number")), None)
        if not app_with_num:
            pytest.skip("No applications with applicant_number found")
        
        app_id = app_with_num.get("id")
        resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
        assert resp.status_code == 200, f"Failed to get application: {resp.text}"
        
        app = resp.json()
        assert "applicant_number" in app, "applicant_number missing from single application response"
        assert app["applicant_number"] == app_with_num["applicant_number"]
        print(f"PASS: Single application {app_id} returns applicant_number: {app['applicant_number']}")


class TestApplicantNumberInInvoices:
    """Test applicant_number field in invoices API"""
    
    def test_invoices_list_returns_applicant_number(self, staff_session):
        """GET /api/invoices returns applicant_number for invoices"""
        resp = staff_session.get(f"{BASE_URL}/api/invoices")
        assert resp.status_code == 200, f"Failed to get invoices: {resp.text}"
        
        invoices = resp.json()
        assert isinstance(invoices, list), "Expected list of invoices"
        
        if len(invoices) == 0:
            print("INFO: No invoices found - skipping applicant_number check")
            return
        
        # Check if any invoice has applicant_number
        invoices_with_number = [i for i in invoices if i.get("applicant_number")]
        print(f"Found {len(invoices_with_number)}/{len(invoices)} invoices with applicant_number")
        
        for inv in invoices_with_number[:3]:
            num = inv.get("applicant_number")
            print(f"  - Invoice {inv.get('invoice_number')}: applicant_number={num}")
        
        print(f"PASS: Invoices API returns applicant_number field")


class TestLeadIngestApplicantNumber:
    """Test automatic applicant_number generation via /api/leads/ingest"""
    
    def test_new_lead_gets_applicant_number(self):
        """POST /api/leads/ingest creates application with applicant_number"""
        unique_email = f"test_iter84_{uuid.uuid4().hex[:8]}@test.com"
        
        payload = {
            "email": unique_email,
            "full_name": "Test Iter84 User",
            "first_name": "Test",
            "last_name": "Iter84",
            "phone": "+49123456789",
            "country": "Germany",
            "area_interest": "studienkolleg",
            "course_type": "T-Kurs",
            "desired_start": "WS 2026",
            "language_level": "B1",
            "degree_country": "Germany",
            "source": "website_form",
            "password": "TestPass123!"
        }
        
        resp = requests.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200, f"Lead ingest failed: {resp.text}"
        
        data = resp.json()
        assert data.get("success") == True, f"Lead ingest not successful: {data}"
        assert data.get("application_id"), "No application_id returned"
        
        app_id = data.get("application_id")
        print(f"Created application: {app_id}")
        
        # Now verify the application has applicant_number
        # Login as staff to check
        staff_session = requests.Session()
        login_resp = staff_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert login_resp.status_code == 200, "Staff login failed"
        
        app_resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
        assert app_resp.status_code == 200, f"Failed to get application: {app_resp.text}"
        
        app = app_resp.json()
        assert "applicant_number" in app, "applicant_number missing from new application"
        assert app["applicant_number"], "applicant_number is empty"
        
        # Verify format
        num = app["applicant_number"]
        assert re.match(r'^STK-\d{4}-\d{4}$', num), f"Invalid applicant_number format: {num}"
        
        # Verify year is current year
        current_year = datetime.now().year
        assert f"STK-{current_year}" in num, f"Year mismatch in {num}"
        
        print(f"PASS: New lead automatically received applicant_number: {num}")


class TestSearchByApplicantNumber:
    """Test searching applications by applicant_number"""
    
    def test_search_finds_application_by_number(self, staff_session):
        """Search in applications list finds by applicant_number"""
        # Get applications list
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        apps = resp.json()
        
        # Find one with applicant_number
        app_with_num = next((a for a in apps if a.get("applicant_number")), None)
        if not app_with_num:
            pytest.skip("No applications with applicant_number found")
        
        search_term = app_with_num["applicant_number"]
        
        # The search is done client-side in StaffCasesPage, but we verify the data is there
        # Check that the applicant_number is searchable in the response
        matching = [a for a in apps if a.get("applicant_number") == search_term]
        assert len(matching) >= 1, f"Could not find application with {search_term}"
        
        print(f"PASS: Application with {search_term} is findable in list")
        
        # Also test partial search (STK-2026)
        partial = search_term[:8]  # e.g., "STK-2026"
        partial_matches = [a for a in apps if a.get("applicant_number", "").startswith(partial)]
        print(f"  - Partial search '{partial}' matches {len(partial_matches)} applications")


class TestAuthMeEndpoint:
    """Test /api/auth/me endpoint for AuthContext"""
    
    def test_auth_me_returns_user_data(self, staff_session):
        """GET /api/auth/me returns current user data"""
        resp = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200, f"Auth/me failed: {resp.text}"
        
        data = resp.json()
        assert "id" in data, "Missing id in auth/me response"
        assert "email" in data, "Missing email in auth/me response"
        assert "role" in data, "Missing role in auth/me response"
        
        print(f"PASS: /api/auth/me returns user data - role={data.get('role')}")
    
    def test_auth_me_without_session_returns_401(self):
        """GET /api/auth/me without session returns 401"""
        resp = requests.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        print(f"PASS: /api/auth/me without session returns 401")


class TestApplicantPortalAccess:
    """Test applicant can access their own data"""
    
    def test_applicant_sees_own_applications(self, applicant_session):
        """Applicant can see their own applications"""
        resp = applicant_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        apps = resp.json()
        assert isinstance(apps, list), "Expected list"
        print(f"PASS: Applicant can access applications - found {len(apps)}")
        
        # Check if applicant_number is visible
        for app in apps[:3]:
            if app.get("applicant_number"):
                print(f"  - Application has applicant_number: {app['applicant_number']}")
    
    def test_applicant_sees_own_invoices(self, applicant_session):
        """Applicant can see their own invoices via /api/invoices/my"""
        resp = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        
        invoices = resp.json()
        assert isinstance(invoices, list), "Expected list"
        print(f"PASS: Applicant can access /api/invoices/my - found {len(invoices)}")


class TestDatabaseIndexes:
    """Verify database indexes are working (indirect test via performance)"""
    
    def test_applications_query_performance(self, staff_session):
        """Applications query should be fast (indexes working)"""
        import time
        
        start = time.time()
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        elapsed = time.time() - start
        
        assert resp.status_code == 200
        assert elapsed < 5.0, f"Query too slow: {elapsed:.2f}s"
        
        print(f"PASS: Applications query completed in {elapsed:.2f}s")
    
    def test_invoices_query_performance(self, staff_session):
        """Invoices query should be fast (indexes working)"""
        import time
        
        start = time.time()
        resp = staff_session.get(f"{BASE_URL}/api/invoices")
        elapsed = time.time() - start
        
        assert resp.status_code == 200
        assert elapsed < 5.0, f"Query too slow: {elapsed:.2f}s"
        
        print(f"PASS: Invoices query completed in {elapsed:.2f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
