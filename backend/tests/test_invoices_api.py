"""
Invoice API Tests - W2G Platform
Tests for invoice CRUD operations, PDF generation, and status management.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://live-demo-fix.preview.emergentagent.com')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Create authenticated staff session."""
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
    )
    assert response.status_code == 200, f"Staff login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Create authenticated admin session."""
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Create authenticated applicant session."""
    session = requests.Session()
    response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD}
    )
    assert response.status_code == 200, f"Applicant login failed: {response.text}"
    return session


class TestInvoiceList:
    """Tests for invoice listing endpoints."""
    
    def test_staff_can_list_invoices(self, staff_session):
        """Staff should be able to list all invoices."""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"  - Found {len(data)} invoices")
    
    def test_invoice_list_has_required_fields(self, staff_session):
        """Invoice list items should have required fields."""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            invoice = data[0]
            required_fields = ['invoice_number', 'applicant_name', 'amount', 'status']
            for field in required_fields:
                assert field in invoice, f"Missing field: {field}"
            print(f"  - Invoice {invoice['invoice_number']} has all required fields")
    
    def test_invoice_filter_by_status(self, staff_session):
        """Should be able to filter invoices by status."""
        response = staff_session.get(f"{BASE_URL}/api/invoices?status=paid")
        assert response.status_code == 200
        data = response.json()
        
        for invoice in data:
            assert invoice['status'] == 'paid', f"Expected status 'paid', got '{invoice['status']}'"
        print(f"  - Found {len(data)} paid invoices")


class TestInvoiceStats:
    """Tests for invoice statistics endpoint."""
    
    def test_staff_can_get_invoice_stats(self, staff_session):
        """Staff should be able to get invoice statistics."""
        response = staff_session.get(f"{BASE_URL}/api/invoices/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert 'total_count' in data
        assert 'total_amount' in data
        assert 'by_status' in data
        print(f"  - Total: {data['total_count']} invoices, {data['total_amount']} EUR")


class TestInvoicePDF:
    """Tests for invoice PDF generation."""
    
    def test_staff_can_download_invoice_pdf(self, staff_session):
        """Staff should be able to download invoice PDF."""
        # First get an invoice number
        list_response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert list_response.status_code == 200
        invoices = list_response.json()
        
        if len(invoices) == 0:
            pytest.skip("No invoices available for PDF test")
        
        invoice_number = invoices[0]['invoice_number']
        
        # Download PDF
        pdf_response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        assert pdf_response.status_code == 200
        assert pdf_response.headers.get('content-type') == 'application/pdf'
        
        # Check PDF content starts with PDF header
        content = pdf_response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        print(f"  - Downloaded PDF for {invoice_number} ({len(content)} bytes)")


class TestInvoiceApplicants:
    """Tests for invoice applicants endpoint."""
    
    def test_staff_can_list_applicants_for_invoice(self, staff_session):
        """Staff should be able to list applicants for invoice creation."""
        response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        if len(data) > 0:
            applicant = data[0]
            assert 'id' in applicant
            assert 'email' in applicant
        print(f"  - Found {len(data)} applicants for invoice creation")


class TestInvoiceStatusBadges:
    """Tests for invoice status values."""
    
    def test_invoice_statuses_are_valid(self, staff_session):
        """All invoice statuses should be valid."""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        
        valid_statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
        
        for invoice in data:
            status = invoice.get('status')
            assert status in valid_statuses, f"Invalid status: {status}"
        
        # Count by status
        status_counts = {}
        for invoice in data:
            status = invoice.get('status')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"  - Status distribution: {status_counts}")


class TestDashboardStats:
    """Tests for dashboard statistics."""
    
    def test_staff_can_get_dashboard_stats(self, staff_session):
        """Staff should be able to get dashboard statistics."""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert 'total_leads' in data
        assert 'pipeline' in data
        print(f"  - Total leads: {data['total_leads']}")


class TestApplicantPortal:
    """Tests for applicant portal endpoints."""
    
    def test_applicant_can_view_own_invoices(self, applicant_session):
        """Applicant should be able to view their own invoices."""
        response = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"  - Applicant has {len(data)} invoices")


class TestKnowledgeBase:
    """Tests for admin knowledge base."""
    
    def test_admin_can_access_knowledge_stats(self, admin_session):
        """Admin should be able to access knowledge base stats."""
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert 'total' in data
        print(f"  - Knowledge base has {data['total']} entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
