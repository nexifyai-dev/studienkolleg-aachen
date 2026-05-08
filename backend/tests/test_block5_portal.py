"""
Block 5: Applicant Portal Tests
- GET /api/documents/my - returns applicant documents
- GET /api/invoices/my - returns applicant invoices
- POST /api/documents - creates new document entry
- Regression: Staff Dashboard, Kanban, Admin Users
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"


class TestApplicantAuth:
    """Test applicant authentication"""
    
    def test_applicant_login(self):
        """Applicant can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "user" in data or "email" in data
        print("PASSED: Applicant login successful")


class TestDocumentsMyEndpoint:
    """Test GET /api/documents/my endpoint"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_get_my_documents(self, applicant_session):
        """GET /api/documents/my returns applicant's documents"""
        response = applicant_session.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of documents"
        print(f"PASSED: GET /api/documents/my returned {len(data)} documents")
    
    def test_documents_my_unauthenticated(self):
        """GET /api/documents/my requires authentication"""
        response = requests.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: /api/documents/my requires authentication")


class TestInvoicesMyEndpoint:
    """Test GET /api/invoices/my endpoint"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_get_my_invoices(self, applicant_session):
        """GET /api/invoices/my returns applicant's invoices"""
        response = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of invoices"
        # Verify invoice structure if any exist
        if len(data) > 0:
            inv = data[0]
            assert "invoice_number" in inv or "amount" in inv, "Invoice should have invoice_number or amount"
        print(f"PASSED: GET /api/invoices/my returned {len(data)} invoices")
    
    def test_invoices_my_unauthenticated(self):
        """GET /api/invoices/my requires authentication"""
        response = requests.get(f"{BASE_URL}/api/invoices/my")
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print("PASSED: /api/invoices/my requires authentication")


class TestDocumentCreation:
    """Test POST /api/documents endpoint"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_create_document_requires_application_id(self, applicant_session):
        """POST /api/documents requires application_id"""
        response = applicant_session.post(f"{BASE_URL}/api/documents", json={
            "document_type": "passport",
            "filename": "test_passport.pdf"
        })
        # Should fail without application_id
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASSED: POST /api/documents requires application_id")
    
    def test_create_document_with_application(self, applicant_session):
        """POST /api/documents creates document entry with valid application_id"""
        # First get applicant's applications
        apps_response = applicant_session.get(f"{BASE_URL}/api/applications")
        assert apps_response.status_code == 200
        apps = apps_response.json()
        
        if len(apps) == 0:
            pytest.skip("No applications found for applicant")
        
        app_id = apps[0].get("id") or apps[0].get("_id")
        
        # Create document
        response = applicant_session.post(f"{BASE_URL}/api/documents", json={
            "application_id": app_id,
            "document_type": "other",
            "filename": f"TEST_block5_doc_{os.urandom(4).hex()}.pdf",
            "status": "uploaded"
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain document id"
        assert data.get("status") == "uploaded"
        print(f"PASSED: POST /api/documents created document {data.get('id')}")


class TestStaffDashboardRegression:
    """Regression: Staff Dashboard still works"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_staff_login(self, staff_session):
        """Staff can login"""
        response = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "staff"
        print("PASSED: Staff login and /api/auth/me works")
    
    def test_staff_dashboard_stats(self, staff_session):
        """Staff can access dashboard stats"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # Should have some stats
        assert isinstance(data, dict)
        print("PASSED: Staff dashboard stats accessible")
    
    def test_staff_applications_list(self, staff_session):
        """Staff can list applications"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Staff can list applications ({len(data)} found)")


class TestStaffKanbanRegression:
    """Regression: Staff Kanban still works"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_kanban_applications(self, staff_session):
        """Staff can access applications for Kanban view"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        apps = response.json()
        # Verify applications have stage info for Kanban
        if len(apps) > 0:
            app = apps[0]
            assert "current_stage" in app or "stage" in app, "Application should have stage info"
        print("PASSED: Kanban applications accessible")


class TestAdminUsersRegression:
    """Regression: Admin Users still works"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_admin_login(self, admin_session):
        """Admin can login"""
        response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") in ["admin", "superadmin"]
        print("PASSED: Admin login works")
    
    def test_admin_list_users(self, admin_session):
        """Admin can list users"""
        response = admin_session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0, "Should have at least one user"
        print(f"PASSED: Admin can list users ({len(data)} found)")
    
    def test_admin_audit_logs(self, admin_session):
        """Admin can access audit logs"""
        response = admin_session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Admin can access audit logs ({len(data)} entries)")


class TestApplicantPortalEndpoints:
    """Test applicant portal specific endpoints"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_applicant_applications(self, applicant_session):
        """Applicant can list their applications"""
        response = applicant_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Applicant applications list ({len(data)} found)")
    
    def test_applicant_conversations(self, applicant_session):
        """Applicant can access conversations"""
        response = applicant_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Applicant conversations accessible ({len(data)} found)")
    
    def test_applicant_support_conversation(self, applicant_session):
        """Applicant can get/create support conversation"""
        response = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "id" in data, "Support conversation should have id"
        print("PASSED: Applicant support conversation accessible")
    
    def test_applicant_consents(self, applicant_session):
        """Applicant can access consents"""
        response = applicant_session.get(f"{BASE_URL}/api/consents/my")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASSED: Applicant consents accessible ({len(data)} found)")
    
    def test_applicant_update_profile(self, applicant_session):
        """Applicant can update their profile via /api/users/{id}"""
        # First get user id
        me_response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        user_id = me_response.json().get("id")
        
        # Update profile using PUT
        response = applicant_session.put(f"{BASE_URL}/api/users/{user_id}", json={
            "full_name": "Ahmed Hassan",
            "language_pref": "de"
        })
        assert response.status_code == 200, f"Failed: {response.text}"
        print("PASSED: Applicant can update profile")


class TestInvoicePdfDownload:
    """Test invoice PDF download"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_invoice_pdf_download(self, applicant_session):
        """Applicant can download invoice PDF"""
        # First get invoices
        inv_response = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert inv_response.status_code == 200
        invoices = inv_response.json()
        
        if len(invoices) == 0:
            pytest.skip("No invoices found for applicant")
        
        invoice_number = invoices[0].get("invoice_number")
        if not invoice_number:
            pytest.skip("Invoice has no invoice_number")
        
        # Download PDF
        response = applicant_session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        assert response.status_code == 200, f"Failed: {response.status_code}"
        assert "application/pdf" in response.headers.get("content-type", "")
        assert len(response.content) > 0, "PDF should have content"
        print(f"PASSED: Invoice PDF download works ({len(response.content)} bytes)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
