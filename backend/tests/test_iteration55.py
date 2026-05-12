"""
Iteration 55 - System Audit Tests
Testing: Footer links, Booking page, Courses page, Services page, Staff portal, Auth
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://live-demo-fix.preview.emergentagent.com').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"


class TestHealthAndBasicEndpoints:
    """Basic health and public endpoint tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns 200"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        print("PASS: Health endpoint returns 200")
    
    def test_public_slots_endpoint(self):
        """Test booking slots endpoint"""
        response = requests.get(f"{BASE_URL}/api/appointments/public-slots?date=2026-02-15", timeout=10)
        assert response.status_code == 200, f"Public slots failed: {response.status_code}"
        data = response.json()
        assert "slots" in data, "Response should contain 'slots' key"
        print(f"PASS: Public slots endpoint returns {len(data.get('slots', []))} slots")


class TestStaffAuthentication:
    """Staff login and authentication tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Create authenticated staff session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Staff login failed: {response.status_code} - {response.text}")
        return session
    
    def test_staff_login(self):
        """Test staff login returns user data"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200, f"Staff login failed: {response.status_code}"
        data = response.json()
        assert "user" in data or "email" in data, "Response should contain user data"
        print(f"PASS: Staff login successful")
    
    def test_staff_me_endpoint(self, staff_session):
        """Test /api/auth/me returns current user"""
        response = staff_session.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert response.status_code == 200, f"Auth/me failed: {response.status_code}"
        data = response.json()
        assert data.get("email") == STAFF_EMAIL, "Email should match"
        print(f"PASS: Auth/me returns correct user: {data.get('email')}")


class TestStaffDashboardAPIs:
    """Staff dashboard API tests (TanStack Query endpoints)"""
    
    @pytest.fixture
    def staff_session(self):
        """Create authenticated staff session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Staff login failed: {response.status_code}")
        return session
    
    def test_dashboard_stats(self, staff_session):
        """Test dashboard stats endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats", timeout=10)
        assert response.status_code == 200, f"Dashboard stats failed: {response.status_code}"
        data = response.json()
        # Should have pipeline data
        assert "pipeline" in data or "total_leads" in data, "Should have dashboard data"
        print(f"PASS: Dashboard stats loaded - {data.keys()}")
    
    def test_applications_list(self, staff_session):
        """Test applications list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/applications", timeout=10)
        assert response.status_code == 200, f"Applications list failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Should return list of applications"
        print(f"PASS: Applications list returns {len(data)} items")
    
    def test_tasks_list(self, staff_session):
        """Test tasks list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/tasks", timeout=10)
        assert response.status_code == 200, f"Tasks list failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Should return list of tasks"
        print(f"PASS: Tasks list returns {len(data)} items")
    
    def test_invoices_list(self, staff_session):
        """Test invoices list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/invoices", timeout=10)
        assert response.status_code == 200, f"Invoices list failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Should return list of invoices"
        print(f"PASS: Invoices list returns {len(data)} items")
    
    def test_invoices_stats(self, staff_session):
        """Test invoices stats endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/stats", timeout=10)
        assert response.status_code == 200, f"Invoices stats failed: {response.status_code}"
        data = response.json()
        assert "total_count" in data or "by_status" in data, "Should have stats data"
        print(f"PASS: Invoices stats loaded")
    
    def test_conversations_list(self, staff_session):
        """Test conversations list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/conversations", timeout=10)
        assert response.status_code == 200, f"Conversations list failed: {response.status_code}"
        print(f"PASS: Conversations endpoint returns 200")


class TestInvoicePDF:
    """Invoice PDF generation tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Create authenticated staff session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
            timeout=10
        )
        if response.status_code != 200:
            pytest.skip(f"Staff login failed: {response.status_code}")
        return session
    
    def test_invoice_pdf_generation(self, staff_session):
        """Test invoice PDF can be generated"""
        # First get list of invoices
        response = staff_session.get(f"{BASE_URL}/api/invoices", timeout=10)
        if response.status_code != 200:
            pytest.skip("Could not get invoices list")
        
        invoices = response.json()
        if not invoices:
            pytest.skip("No invoices available for PDF test")
        
        # Get first invoice number
        invoice_number = invoices[0].get("invoice_number") or invoices[0].get("id")
        
        # Try to download PDF
        pdf_response = staff_session.get(
            f"{BASE_URL}/api/invoices/{invoice_number}/pdf",
            timeout=15
        )
        assert pdf_response.status_code == 200, f"PDF generation failed: {pdf_response.status_code}"
        assert pdf_response.headers.get("content-type") == "application/pdf", "Should return PDF"
        assert len(pdf_response.content) > 1000, "PDF should have content"
        print(f"PASS: Invoice PDF generated ({len(pdf_response.content)} bytes)")


class TestAdminAuthentication:
    """Admin login tests"""
    
    def test_admin_login(self):
        """Test admin login"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200, f"Admin login failed: {response.status_code}"
        data = response.json()
        assert "user" in data or "email" in data, "Response should contain user data"
        print(f"PASS: Admin login successful")


class TestPublicPages:
    """Test public page endpoints return 200"""
    
    def test_homepage_loads(self):
        """Test homepage loads"""
        response = requests.get(f"{BASE_URL}/", timeout=10)
        assert response.status_code == 200, f"Homepage failed: {response.status_code}"
        print("PASS: Homepage loads")
    
    def test_courses_page_loads(self):
        """Test courses page loads"""
        response = requests.get(f"{BASE_URL}/courses", timeout=10)
        assert response.status_code == 200, f"Courses page failed: {response.status_code}"
        print("PASS: Courses page loads")
    
    def test_services_page_loads(self):
        """Test services page loads"""
        response = requests.get(f"{BASE_URL}/services", timeout=10)
        assert response.status_code == 200, f"Services page failed: {response.status_code}"
        print("PASS: Services page loads")
    
    def test_booking_page_loads(self):
        """Test booking page loads"""
        response = requests.get(f"{BASE_URL}/booking", timeout=10)
        assert response.status_code == 200, f"Booking page failed: {response.status_code}"
        print("PASS: Booking page loads")
    
    def test_contact_page_loads(self):
        """Test contact page loads"""
        response = requests.get(f"{BASE_URL}/contact", timeout=10)
        assert response.status_code == 200, f"Contact page failed: {response.status_code}"
        print("PASS: Contact page loads")
    
    def test_apply_page_loads(self):
        """Test apply page loads"""
        response = requests.get(f"{BASE_URL}/apply", timeout=10)
        assert response.status_code == 200, f"Apply page failed: {response.status_code}"
        print("PASS: Apply page loads")
    
    def test_legal_page_loads(self):
        """Test legal/impressum page loads"""
        response = requests.get(f"{BASE_URL}/legal", timeout=10)
        assert response.status_code == 200, f"Legal page failed: {response.status_code}"
        print("PASS: Legal page loads")
    
    def test_privacy_page_loads(self):
        """Test privacy page loads"""
        response = requests.get(f"{BASE_URL}/privacy", timeout=10)
        assert response.status_code == 200, f"Privacy page failed: {response.status_code}"
        print("PASS: Privacy page loads")
    
    def test_agb_page_loads(self):
        """Test AGB page loads"""
        response = requests.get(f"{BASE_URL}/agb", timeout=10)
        assert response.status_code == 200, f"AGB page failed: {response.status_code}"
        print("PASS: AGB page loads")
    
    def test_knowledge_page_loads(self):
        """Test knowledge center page loads"""
        response = requests.get(f"{BASE_URL}/knowledge", timeout=10)
        assert response.status_code == 200, f"Knowledge page failed: {response.status_code}"
        print("PASS: Knowledge page loads")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
