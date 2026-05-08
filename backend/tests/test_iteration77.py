"""
Iteration 77 - Backend API Tests
Testing: Auth, Dashboard, Invoices (CRUD, PDF, Settings), Oracle
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://invoice-fix-31.preview.emergentagent.com')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestAuth:
    """Authentication endpoint tests"""
    
    def test_staff_login_success(self):
        """Test staff login returns 200 and sets cookies"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        # Response returns user object directly (not wrapped in "user" key)
        assert "email" in data, "Response should contain email"
        assert data["email"] == STAFF_EMAIL
        assert data["role"] == "staff"
        print(f"PASS: Staff login successful - role: {data['role']}")
    
    def test_admin_login_success(self):
        """Test admin login returns 200"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["role"] in ["admin", "superadmin"], f"Expected admin/superadmin role, got {data['role']}"
        print(f"PASS: Admin login successful - role: {data['role']}")
    
    def test_applicant_login_success(self):
        """Test applicant login returns 200"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data["role"] == "applicant"
        print(f"PASS: Applicant login successful - role: {data['role']}")
    
    def test_login_invalid_credentials(self):
        """Test login with wrong password returns 401"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Invalid credentials correctly rejected")


class TestDashboard:
    """Dashboard endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_dashboard_stats(self, staff_session):
        """Test dashboard stats endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        data = response.json()
        # Verify structure
        assert "pipeline" in data or "total_applications" in data or isinstance(data, dict)
        print(f"PASS: Dashboard stats returned successfully")
    
    def test_applications_list(self, staff_session):
        """Test applications list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Applications list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Applications list returned {len(data)} items")
    
    def test_tasks_list(self, staff_session):
        """Test tasks list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200, f"Tasks list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Tasks list returned {len(data)} items")


class TestInvoices:
    """Invoice CRUD and PDF tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_invoices_list(self, staff_session):
        """Test invoices list endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Invoices list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Invoices list returned {len(data)} items")
        return data
    
    def test_invoices_stats(self, staff_session):
        """Test invoices stats endpoint"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/stats")
        assert response.status_code == 200, f"Invoice stats failed: {response.text}"
        data = response.json()
        assert "total_count" in data
        assert "total_amount" in data
        assert "by_status" in data
        print(f"PASS: Invoice stats - total: {data['total_count']}, amount: {data['total_amount']}")
    
    def test_invoices_filter_by_status(self, staff_session):
        """Test invoices filter by status"""
        for status in ['draft', 'sent', 'paid', 'overdue']:
            response = staff_session.get(f"{BASE_URL}/api/invoices?status={status}")
            assert response.status_code == 200, f"Filter by {status} failed: {response.text}"
            data = response.json()
            # All returned invoices should have the filtered status
            for inv in data:
                assert inv.get('status') == status, f"Invoice {inv.get('invoice_number')} has status {inv.get('status')}, expected {status}"
            print(f"PASS: Filter by status '{status}' returned {len(data)} invoices")
    
    def test_invoice_settings_get(self, staff_session):
        """Test GET invoice settings"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/settings")
        assert response.status_code == 200, f"Get settings failed: {response.text}"
        data = response.json()
        assert "prefix" in data
        assert "start_number" in data
        assert "include_date" in data
        assert "preview" in data
        print(f"PASS: Invoice settings - prefix: {data['prefix']}, preview: {data['preview']}")
    
    def test_invoice_settings_update(self, admin_session):
        """Test PUT invoice settings (Admin only)"""
        # First get current settings
        get_response = admin_session.get(f"{BASE_URL}/api/invoices/settings")
        assert get_response.status_code == 200
        original = get_response.json()
        
        # Update settings
        response = admin_session.put(f"{BASE_URL}/api/invoices/settings", json={
            "prefix": "INV",
            "start_number": original.get("start_number", 1),
            "suffix": "",
            "include_date": True
        })
        assert response.status_code == 200, f"Update settings failed: {response.text}"
        data = response.json()
        assert "preview" in data
        print(f"PASS: Invoice settings updated - new preview: {data['preview']}")
    
    def test_invoice_applicants_list(self, staff_session):
        """Test list applicants for invoice creation"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert response.status_code == 200, f"Applicants list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "email" in data[0]
        print(f"PASS: Invoice applicants list returned {len(data)} applicants")
        return data
    
    def test_invoice_create_and_pdf(self, staff_session):
        """Test create invoice and download PDF"""
        # First get an applicant
        applicants_response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert applicants_response.status_code == 200
        applicants = applicants_response.json()
        
        if len(applicants) == 0:
            pytest.skip("No applicants available for invoice creation")
        
        applicant = applicants[0]
        
        # Create invoice
        create_response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant["id"],
            "description": "TEST_Iteration77_Kursgebuehr",
            "amount": 1500.00,
            "due_date": "2026-02-28",
            "items": [
                {"description": "TEST_Kursgebuehr Semester 1", "quantity": 1, "unit_price": 1500.00}
            ]
        })
        assert create_response.status_code == 200, f"Create invoice failed: {create_response.text}"
        invoice = create_response.json()
        assert "invoice_number" in invoice
        assert invoice["amount"] == 1500.00
        assert invoice["status"] == "draft"
        print(f"PASS: Invoice created - {invoice['invoice_number']}")
        
        # Download PDF
        pdf_response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice['invoice_number']}/pdf")
        assert pdf_response.status_code == 200, f"PDF download failed: {pdf_response.text}"
        assert pdf_response.headers.get('content-type') == 'application/pdf'
        # Check PDF magic bytes
        pdf_content = pdf_response.content
        assert pdf_content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"PASS: PDF downloaded successfully - {len(pdf_content)} bytes")
        
        # Return invoice number for cleanup
        return invoice['invoice_number']
    
    def test_invoice_get_single(self, staff_session):
        """Test get single invoice by number"""
        # First list invoices
        list_response = staff_session.get(f"{BASE_URL}/api/invoices")
        invoices = list_response.json()
        
        if len(invoices) == 0:
            pytest.skip("No invoices available")
        
        invoice_number = invoices[0].get('invoice_number')
        response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}")
        assert response.status_code == 200, f"Get invoice failed: {response.text}"
        data = response.json()
        assert data.get('invoice_number') == invoice_number
        print(f"PASS: Single invoice retrieved - {invoice_number}")
    
    def test_invoice_update_status(self, staff_session):
        """Test update invoice status"""
        # Get a draft invoice
        list_response = staff_session.get(f"{BASE_URL}/api/invoices?status=draft")
        invoices = list_response.json()
        
        if len(invoices) == 0:
            pytest.skip("No draft invoices available")
        
        invoice = invoices[0]
        invoice_number = invoice.get('invoice_number')
        
        # Update to sent
        response = staff_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={
            "status": "sent"
        })
        assert response.status_code == 200, f"Update status failed: {response.text}"
        data = response.json()
        assert data.get('status') == 'sent'
        print(f"PASS: Invoice status updated to 'sent' - {invoice_number}")
        
        # Revert to draft for cleanup
        staff_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={"status": "draft"})


class TestOracle:
    """Oracle/KI endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_oracle_conversations_list(self, staff_session):
        """Test oracle conversations list"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/conversations")
        assert response.status_code == 200, f"Oracle conversations failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Oracle conversations returned {len(data)} items")


class TestCleanup:
    """Cleanup test data"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_cleanup_test_invoices(self, admin_session):
        """Delete TEST_ prefixed invoices"""
        response = admin_session.get(f"{BASE_URL}/api/invoices")
        invoices = response.json()
        
        deleted = 0
        for inv in invoices:
            desc = inv.get('description', '')
            if 'TEST_' in desc and inv.get('status') == 'draft':
                inv_num = inv.get('invoice_number')
                del_response = admin_session.delete(f"{BASE_URL}/api/invoices/{inv_num}")
                if del_response.status_code in [200, 204]:
                    deleted += 1
                    print(f"Deleted test invoice: {inv_num}")
        
        print(f"PASS: Cleanup completed - deleted {deleted} test invoices")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
