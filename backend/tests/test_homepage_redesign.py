"""
Test Suite: Homepage Redesign nach Edma-Moodle-Vorlage
Tests for iteration_45 - New homepage sections and existing feature regression
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHomepageBackendAPIs:
    """Backend API tests for homepage and regression features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with staff authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"}
        )
        assert login_response.status_code == 200, f"Staff login failed: {login_response.text}"
        self.staff_user = login_response.json()
        print(f"Logged in as: {self.staff_user.get('email')}")
    
    # ═══ HOMEPAGE API TESTS ═══════════════════════════════════════════════
    
    def test_homepage_loads(self):
        """Test that homepage route returns 200"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Homepage failed to load: {response.status_code}"
        print("SUCCESS: Homepage loads correctly")
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print(f"SUCCESS: Health check passed")
    
    # ═══ INVOICE PDF REGRESSION TESTS ═════════════════════════════════════
    
    def test_invoice_list(self):
        """Test invoice listing for staff"""
        response = self.session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Invoice list failed: {response.text}"
        invoices = response.json()
        assert isinstance(invoices, list), "Invoices should be a list"
        print(f"SUCCESS: Found {len(invoices)} invoices")
        return invoices
    
    def test_invoice_pdf_download(self):
        """Test invoice PDF download - critical regression test"""
        # First get an invoice
        invoices = self.test_invoice_list()
        if not invoices:
            pytest.skip("No invoices available for PDF test")
        
        invoice_number = invoices[0].get('invoice_number')
        assert invoice_number, "Invoice should have invoice_number"
        
        # Download PDF
        response = self.session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        assert response.status_code == 200, f"PDF download failed: {response.status_code}"
        
        # Verify it's a PDF
        content_type = response.headers.get('content-type', '')
        assert 'pdf' in content_type.lower(), f"Expected PDF, got: {content_type}"
        
        # Check PDF signature
        assert response.content[:4] == b'%PDF', "Response should be a valid PDF"
        print(f"SUCCESS: Invoice PDF downloaded for {invoice_number}")
    
    def test_invoice_stats(self):
        """Test invoice statistics endpoint"""
        response = self.session.get(f"{BASE_URL}/api/invoices/stats")
        assert response.status_code == 200, f"Invoice stats failed: {response.text}"
        stats = response.json()
        assert 'total_count' in stats, "Stats should have total_count"
        print(f"SUCCESS: Invoice stats - {stats.get('total_count')} total invoices")
    
    # ═══ STAFF DASHBOARD REGRESSION TESTS ═════════════════════════════════
    
    def test_staff_dashboard_stats(self):
        """Test staff dashboard statistics"""
        response = self.session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        stats = response.json()
        print(f"SUCCESS: Dashboard stats loaded")
    
    def test_staff_users_list(self):
        """Test users listing - staff may have limited access"""
        response = self.session.get(f"{BASE_URL}/api/users")
        # Staff might not have permission to list all users
        assert response.status_code in [200, 403], f"Users list unexpected error: {response.text}"
        if response.status_code == 200:
            users = response.json()
            print(f"SUCCESS: Found {len(users) if isinstance(users, list) else 'N/A'} users")
        else:
            print(f"INFO: Staff doesn't have permission to list all users (expected behavior)")
    
    # ═══ AUTH REGRESSION TESTS ════════════════════════════════════════════
    
    def test_auth_me(self):
        """Test auth/me endpoint"""
        response = self.session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth/me failed: {response.text}"
        user = response.json()
        assert user.get('email') == 'staff@studienkolleg-aachen.de'
        print(f"SUCCESS: Auth/me returns correct user")
    
    def test_admin_login(self):
        """Test admin login works"""
        admin_session = requests.Session()
        response = admin_session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@studienkolleg-aachen.de", "password": "Admin@2026!"}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        admin_user = response.json()
        assert admin_user.get('role') in ['admin', 'superadmin'], f"Should be admin role, got: {admin_user.get('role')}"
        print(f"SUCCESS: Admin login works - role: {admin_user.get('role')}")


class TestApplicantPortal:
    """Test applicant portal features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with applicant authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as applicant
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "applicant@studienkolleg-aachen.de", "password": "DevSeed@2026!"}
        )
        assert login_response.status_code == 200, f"Applicant login failed: {login_response.text}"
        self.applicant_user = login_response.json()
        print(f"Logged in as applicant: {self.applicant_user.get('email')}")
    
    def test_applicant_my_invoices(self):
        """Test applicant can view own invoices"""
        response = self.session.get(f"{BASE_URL}/api/invoices/my")
        assert response.status_code == 200, f"My invoices failed: {response.text}"
        invoices = response.json()
        assert isinstance(invoices, list), "Should return list of invoices"
        print(f"SUCCESS: Applicant can view {len(invoices)} own invoices")
    
    def test_applicant_documents(self):
        """Test applicant documents endpoint"""
        response = self.session.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code == 200, f"My documents failed: {response.text}"
        print(f"SUCCESS: Applicant documents endpoint works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
