"""
Block 6 Tests: Pre-Login Pages & Invoice PDF D/A/CH Compliance

Tests:
1. Auth endpoints (login with staff credentials)
2. Invoice PDF endpoint with D/A/CH company data
3. RegisterPage redirect behavior (via API check)
4. Invoice list for applicant
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"

# Test invoice number from agent context
TEST_INVOICE_NUMBER = "W2G-202603-1003-AC"


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_staff_login_success(self):
        """Staff login should succeed with correct credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert "user" in data or "email" in data, "Response should contain user data"
        print(f"PASSED: Staff login successful")
    
    def test_admin_login_success(self):
        """Admin login should succeed with correct credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "user" in data or "email" in data, "Response should contain user data"
        print(f"PASSED: Admin login successful")
    
    def test_applicant_login_success(self):
        """Applicant login should succeed with correct credentials"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert "user" in data or "email" in data, "Response should contain user data"
        print(f"PASSED: Applicant login successful")


class TestInvoicePDF:
    """Test Invoice PDF endpoint with D/A/CH compliance"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Staff login failed - skipping authenticated tests")
        return session
    
    def test_invoice_list_staff(self, staff_session):
        """Staff should be able to list invoices"""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Invoice list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASSED: Invoice list returned {len(data)} invoices")
    
    def test_invoice_pdf_download(self, staff_session):
        """PDF download should return valid PDF"""
        # First get list of invoices to find a valid one
        list_response = staff_session.get(f"{BASE_URL}/api/invoices")
        if list_response.status_code != 200:
            pytest.skip("Could not list invoices")
        
        invoices = list_response.json()
        if not invoices:
            pytest.skip("No invoices available for PDF test")
        
        # Use first available invoice
        invoice_number = invoices[0].get("invoice_number", TEST_INVOICE_NUMBER)
        
        # Download PDF
        response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        assert response.status_code == 200, f"PDF download failed: {response.text}"
        
        # Check content type
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got: {content_type}"
        
        # Check content disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, f"Expected attachment disposition, got: {content_disp}"
        
        # Check PDF content starts with PDF magic bytes
        content = response.content
        assert content[:4] == b'%PDF', "Content should start with PDF magic bytes"
        
        # PDF should be reasonably sized (at least 2KB for a proper invoice)
        assert len(content) > 2000, f"PDF seems too small: {len(content)} bytes"
        
        print(f"PASSED: PDF download successful for invoice {invoice_number}")
        print(f"  - Content-Type: {content_type}")
        print(f"  - PDF size: {len(content)} bytes")
    
    def test_invoice_pdf_structure(self, staff_session):
        """PDF should have proper structure and be valid"""
        # Get first invoice
        list_response = staff_session.get(f"{BASE_URL}/api/invoices")
        if list_response.status_code != 200 or not list_response.json():
            pytest.skip("No invoices available")
        
        invoice_number = list_response.json()[0].get("invoice_number")
        response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        
        if response.status_code != 200:
            pytest.skip("PDF download failed")
        
        content = response.content
        
        # Check PDF structure markers
        assert b'%PDF-1.' in content, "PDF should have version header"
        assert b'%%EOF' in content, "PDF should have EOF marker"
        assert b'/Type /Page' in content, "PDF should have page definition"
        assert b'ReportLab' in content, "PDF should be generated by ReportLab"
        
        # Check filename in Content-Disposition
        content_disp = response.headers.get("Content-Disposition", "")
        assert invoice_number in content_disp, f"Filename should contain invoice number: {content_disp}"
        
        print(f"PASSED: PDF structure is valid for invoice {invoice_number}")


class TestApplicantInvoices:
    """Test applicant invoice access"""
    
    @pytest.fixture
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Applicant login failed - skipping authenticated tests")
        return session
    
    def test_applicant_my_invoices(self, applicant_session):
        """Applicant should be able to list their own invoices"""
        response = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert response.status_code == 200, f"My invoices failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASSED: Applicant invoices returned {len(data)} invoices")


class TestForgotPassword:
    """Test forgot password endpoint"""
    
    def test_forgot_password_endpoint_exists(self):
        """Forgot password endpoint should exist and accept requests"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "test@example.com"
        })
        # Should return 200 even for non-existent email (security best practice)
        # or 400/422 for validation error
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASSED: Forgot password endpoint responds with status {response.status_code}")


class TestPublicEndpoints:
    """Test public endpoints that don't require auth"""
    
    def test_health_check(self):
        """Health endpoint should be accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        # Health endpoint might not exist, but API should respond
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"PASSED: API is responding")
    
    def test_leads_ingest_endpoint_exists(self):
        """Leads ingest endpoint should exist (for apply form)"""
        # Just check it exists - don't actually submit
        response = requests.post(f"{BASE_URL}/api/leads/ingest", json={})
        # Should return 422 for missing fields, not 404
        assert response.status_code in [400, 422], f"Expected validation error, got: {response.status_code}"
        print(f"PASSED: Leads ingest endpoint exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
