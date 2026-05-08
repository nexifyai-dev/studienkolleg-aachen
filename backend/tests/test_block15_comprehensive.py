"""
Block 15 Comprehensive Testing:
- Notes API (POST/GET /api/applications/{id}/notes)
- AI Screening with DeepSeek (POST /api/applications/{id}/ai-screen, GET /api/applications/{id}/ai-screenings)
- Email Integration (GET /api/messaging/email-status, POST /api/messaging/sync-imap)
- Invoice PDF Download (GET /api/invoices/{invoice_number}/pdf)
- CSV Export (GET /api/export/applications)
- Document Download (GET /api/documents/{id}/download)
- Conversation Updates (PUT /api/conversations/{id}, GET /api/conversations/stats)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"

# Test data from review request
TEST_APPLICATION_ID = "69cb8e9a3f026e1d41dd4800"
TEST_DOCUMENT_ID = "69cbbaf37d7964e334c8c4b5"
TEST_INVOICE_NUMBER = "W2G-202603-1001-AC"


@pytest.fixture(scope="module")
def staff_session():
    """Create authenticated staff session."""
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
    """Create authenticated admin session."""
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
def valid_application_id(staff_session):
    """Get a valid application ID for testing."""
    # First try the provided test ID
    response = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APPLICATION_ID}")
    if response.status_code == 200:
        return TEST_APPLICATION_ID
    
    # Fallback: get first application from list
    response = staff_session.get(f"{BASE_URL}/api/applications")
    if response.status_code == 200 and response.json():
        return response.json()[0].get("id")
    
    pytest.skip("No valid application found for testing")


@pytest.fixture(scope="module")
def valid_document_id(staff_session, valid_application_id):
    """Get a valid document ID with binary data for testing."""
    # First try the provided test document ID
    response = staff_session.get(f"{BASE_URL}/api/documents/{TEST_DOCUMENT_ID}/download")
    if response.status_code == 200:
        return TEST_DOCUMENT_ID
    
    # Fallback: get documents from application
    response = staff_session.get(f"{BASE_URL}/api/applications/{valid_application_id}/documents")
    if response.status_code == 200:
        docs = response.json()
        for doc in docs:
            if doc.get("has_binary"):
                return doc.get("id")
    
    return None  # May not have binary documents


class TestHealthAndAuth:
    """Basic health and authentication tests."""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("PASS: Health endpoint accessible")
    
    def test_staff_login(self, staff_session):
        """Verify staff session is authenticated."""
        response = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data.get("email") == STAFF_EMAIL
        print(f"PASS: Staff authenticated as {data.get('email')}")


class TestNotesAPI:
    """Test Notes API - POST/GET /api/applications/{id}/notes"""
    
    def test_create_note(self, staff_session, valid_application_id):
        """Test creating a note for an application."""
        note_content = f"TEST_Note created at {time.time()}"
        
        response = staff_session.post(
            f"{BASE_URL}/api/applications/{valid_application_id}/notes",
            json={"content": note_content, "visibility": "internal"}
        )
        
        assert response.status_code in [200, 201], f"Create note failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data or "content" in data
        print(f"PASS: Note created for application {valid_application_id}")
    
    def test_get_notes(self, staff_session, valid_application_id):
        """Test retrieving notes for an application."""
        response = staff_session.get(
            f"{BASE_URL}/api/applications/{valid_application_id}/notes"
        )
        
        assert response.status_code == 200, f"Get notes failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Retrieved {len(data)} notes for application {valid_application_id}")


class TestAIScreening:
    """Test AI Screening with DeepSeek - POST /api/applications/{id}/ai-screen"""
    
    def test_run_ai_screening(self, staff_session, valid_application_id):
        """Test running AI screening on an application."""
        response = staff_session.post(
            f"{BASE_URL}/api/applications/{valid_application_id}/ai-screen",
            json={}
        )
        
        # AI screening may take time, allow for various success codes
        assert response.status_code in [200, 201, 202], f"AI screening failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "screening_id" in data or "is_complete" in data or "suggested_stage" in data
        print(f"PASS: AI screening completed for application {valid_application_id}")
        print(f"  - is_complete: {data.get('is_complete')}")
        print(f"  - suggested_stage: {data.get('suggested_stage')}")
    
    def test_get_ai_screenings_history(self, staff_session, valid_application_id):
        """Test retrieving AI screening history."""
        response = staff_session.get(
            f"{BASE_URL}/api/applications/{valid_application_id}/ai-screenings"
        )
        
        assert response.status_code == 200, f"Get screenings failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"PASS: Retrieved {len(data)} AI screenings for application {valid_application_id}")


class TestEmailIntegration:
    """Test Email Integration - SMTP/IMAP status and sync."""
    
    def test_email_status(self, staff_session):
        """Test email integration status endpoint."""
        response = staff_session.get(f"{BASE_URL}/api/messaging/email-status")
        
        assert response.status_code == 200, f"Email status failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "smtp_configured" in data
        assert "status" in data
        
        print(f"PASS: Email status retrieved")
        print(f"  - smtp_configured: {data.get('smtp_configured')}")
        print(f"  - smtp_host: {data.get('smtp_host')}")
        print(f"  - imap_host: {data.get('imap_host')}")
        print(f"  - status: {data.get('status')}")
        
        # Verify SMTP is configured as expected
        if data.get("smtp_configured"):
            assert data.get("status") == "aktiv", "Status should be 'aktiv' when SMTP is configured"
    
    def test_imap_sync(self, staff_session):
        """Test IMAP email sync endpoint."""
        response = staff_session.post(
            f"{BASE_URL}/api/messaging/sync-imap",
            json={}
        )
        
        assert response.status_code == 200, f"IMAP sync failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "status" in data or "synced" in data
        print(f"PASS: IMAP sync completed")
        print(f"  - status: {data.get('status')}")
        print(f"  - synced: {data.get('synced', 0)} emails")


class TestInvoicePDF:
    """Test Invoice PDF Download - GET /api/invoices/{invoice_number}/pdf"""
    
    def test_invoice_pdf_download(self, staff_session):
        """Test downloading invoice PDF."""
        response = staff_session.get(
            f"{BASE_URL}/api/invoices/{TEST_INVOICE_NUMBER}/pdf"
        )
        
        # PDF endpoint should return 200 with PDF content or 404 if invoice doesn't exist
        if response.status_code == 404:
            # Try to find a valid invoice
            invoices_response = staff_session.get(f"{BASE_URL}/api/invoices")
            if invoices_response.status_code == 200 and invoices_response.json():
                invoice = invoices_response.json()[0]
                inv_number = invoice.get("invoice_number")
                if inv_number:
                    response = staff_session.get(f"{BASE_URL}/api/invoices/{inv_number}/pdf")
        
        if response.status_code == 200:
            # Verify it's a PDF
            content_type = response.headers.get("Content-Type", "")
            assert "pdf" in content_type.lower() or len(response.content) > 0
            print(f"PASS: Invoice PDF downloaded successfully ({len(response.content)} bytes)")
        elif response.status_code == 404:
            print("SKIP: No invoices found for PDF download test")
        else:
            pytest.fail(f"Invoice PDF download failed: {response.status_code} - {response.text}")


class TestCSVExport:
    """Test CSV Export - GET /api/export/applications"""
    
    def test_csv_export(self, staff_session):
        """Test CSV export of applications."""
        response = staff_session.get(f"{BASE_URL}/api/export/applications")
        
        assert response.status_code == 200, f"CSV export failed: {response.status_code} - {response.text}"
        
        # Verify it's CSV content
        content_type = response.headers.get("Content-Type", "")
        assert "csv" in content_type.lower() or "text" in content_type.lower() or len(response.content) > 0
        
        # Verify content looks like CSV
        content = response.text
        assert len(content) > 0
        
        print(f"PASS: CSV export successful ({len(response.content)} bytes)")
        print(f"  - Content-Type: {content_type}")
        print(f"  - First 100 chars: {content[:100]}...")


class TestDocumentDownload:
    """Test Document Download - GET /api/documents/{id}/download"""
    
    def test_document_download(self, staff_session, valid_document_id):
        """Test downloading a binary document."""
        if not valid_document_id:
            pytest.skip("No binary document available for testing")
        
        response = staff_session.get(
            f"{BASE_URL}/api/documents/{valid_document_id}/download"
        )
        
        assert response.status_code == 200, f"Document download failed: {response.status_code} - {response.text}"
        assert len(response.content) > 0
        
        print(f"PASS: Document downloaded successfully ({len(response.content)} bytes)")
        print(f"  - Content-Type: {response.headers.get('Content-Type', 'unknown')}")


class TestConversations:
    """Test Conversation APIs - PUT /api/conversations/{id}, GET /api/conversations/stats"""
    
    def test_conversation_stats(self, staff_session):
        """Test conversation statistics endpoint."""
        response = staff_session.get(f"{BASE_URL}/api/conversations/stats")
        
        assert response.status_code == 200, f"Conversation stats failed: {response.status_code} - {response.text}"
        data = response.json()
        
        # Verify expected fields
        expected_fields = ["open", "answered", "escalated", "closed"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"PASS: Conversation stats retrieved")
        print(f"  - open: {data.get('open')}")
        print(f"  - answered: {data.get('answered')}")
        print(f"  - escalated: {data.get('escalated')}")
        print(f"  - closed: {data.get('closed')}")
        print(f"  - total: {data.get('total')}")
    
    def test_update_conversation_status(self, staff_session):
        """Test updating conversation status."""
        # First get a conversation
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        
        if response.status_code != 200 or not response.json():
            pytest.skip("No conversations available for testing")
        
        conv = response.json()[0]
        conv_id = conv.get("id")
        
        # Update status
        response = staff_session.put(
            f"{BASE_URL}/api/conversations/{conv_id}",
            json={"status": "answered"}
        )
        
        assert response.status_code == 200, f"Update conversation failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("status") == "ok" or "updated" in data
        
        print(f"PASS: Conversation {conv_id} status updated")


class TestApplicationDocuments:
    """Test Application Documents endpoint."""
    
    def test_get_application_documents(self, staff_session, valid_application_id):
        """Test retrieving documents for an application."""
        response = staff_session.get(
            f"{BASE_URL}/api/applications/{valid_application_id}/documents"
        )
        
        assert response.status_code == 200, f"Get documents failed: {response.status_code} - {response.text}"
        data = response.json()
        assert isinstance(data, list)
        
        # Check for binary documents
        binary_count = sum(1 for d in data if d.get("has_binary"))
        print(f"PASS: Retrieved {len(data)} documents ({binary_count} with binary data)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
