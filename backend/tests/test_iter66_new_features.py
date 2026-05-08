"""
Iteration 66 - New Features Testing

Tests for:
1. Support Chat Widget UI changes (KI text initials, CSS dots typing indicator)
2. DocumentsPage (Portal) - Drag&Drop Upload, In-Browser Preview, Status Badges
3. ApplicantDetailPage (Staff) - StaffDocUpload Widget, Document Preview
4. support_chat.py - Role-based system prompts, applicant context
5. documents.py - Inline Content-Disposition for PDFs/images
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
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
def staff_session(api_client):
    """Authenticated staff session"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    if response.status_code == 200:
        return api_client
    pytest.skip("Staff authentication failed")


@pytest.fixture(scope="module")
def admin_session(api_client):
    """Authenticated admin session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return session
    pytest.skip("Admin authentication failed")


@pytest.fixture(scope="module")
def applicant_session():
    """Authenticated applicant session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    if response.status_code == 200:
        return session
    pytest.skip("Applicant authentication failed")


class TestSupportChatAPI:
    """Tests for POST /api/support/chat endpoint"""

    def test_support_chat_public_access(self, api_client):
        """Support chat should work without authentication (visitor context)"""
        response = api_client.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Was ist das Studienkolleg?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "reply" in data, "Response should contain 'reply'"
        assert "role_context" in data, "Response should contain 'role_context'"
        assert data["role_context"] == "visitor", f"Expected visitor context, got {data['role_context']}"
        print(f"PASS: Public chat returns visitor context with reply")

    def test_support_chat_staff_context(self, staff_session):
        """Support chat should return staff context for staff users"""
        response = staff_session.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Wie viele Bewerbungen gibt es?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["role_context"] == "staff", f"Expected staff context, got {data['role_context']}"
        print(f"PASS: Staff chat returns staff context")

    def test_support_chat_admin_context(self, admin_session):
        """Support chat should return admin context for admin users"""
        response = admin_session.post(f"{BASE_URL}/api/support/chat", json={
            "message": "System-Status?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["role_context"] == "admin", f"Expected admin context, got {data['role_context']}"
        print(f"PASS: Admin chat returns admin context")

    def test_support_chat_applicant_context(self, applicant_session):
        """Support chat should return applicant context for applicant users"""
        response = applicant_session.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Was ist mein Bewerbungsstatus?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["role_context"] == "applicant", f"Expected applicant context, got {data['role_context']}"
        print(f"PASS: Applicant chat returns applicant context")

    def test_support_chat_english_language(self, api_client):
        """Support chat should respond in English when requested"""
        response = api_client.post(f"{BASE_URL}/api/support/chat", json={
            "message": "What is Studienkolleg?",
            "history": [],
            "language": "en"
        })
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        print(f"PASS: Chat responds to English language request")

    def test_support_chat_with_history(self, api_client):
        """Support chat should accept conversation history"""
        response = api_client.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Und wie lange dauert das?",
            "history": [
                {"role": "user", "content": "Was ist das Studienkolleg?"},
                {"role": "assistant", "content": "Das Studienkolleg ist eine Bildungseinrichtung..."}
            ],
            "language": "de"
        })
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        print(f"PASS: Chat accepts conversation history")

    def test_support_chat_empty_message_rejected(self, api_client):
        """Support chat should reject empty messages"""
        response = api_client.post(f"{BASE_URL}/api/support/chat", json={
            "message": "",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 422, f"Expected 422 for empty message, got {response.status_code}"
        print(f"PASS: Empty message rejected with 422")


class TestDocumentsAPI:
    """Tests for documents API endpoints"""

    def test_documents_my_endpoint(self, applicant_session):
        """GET /api/documents/my should return applicant's documents"""
        response = applicant_session.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: /api/documents/my returns {len(data)} documents")

    def test_documents_my_requires_auth(self, api_client):
        """GET /api/documents/my should require authentication"""
        # Create a fresh session without auth
        fresh_session = requests.Session()
        response = fresh_session.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: /api/documents/my requires authentication")

    def test_document_download_inline_pdf(self, staff_session):
        """Document download should return inline Content-Disposition for PDFs"""
        # First get a document list
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        if apps_response.status_code != 200:
            pytest.skip("Could not get applications")
        
        apps = apps_response.json()
        if not apps:
            pytest.skip("No applications found")
        
        # Get documents for first application
        app_id = apps[0].get("id")
        docs_response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/documents")
        if docs_response.status_code != 200:
            pytest.skip("Could not get documents")
        
        docs = docs_response.json()
        pdf_doc = next((d for d in docs if d.get("content_type") == "application/pdf" and d.get("has_binary")), None)
        
        if not pdf_doc:
            print("SKIP: No PDF document with binary found for inline test")
            return
        
        # Download and check Content-Disposition
        download_response = staff_session.get(f"{BASE_URL}/api/documents/{pdf_doc['id']}/download")
        if download_response.status_code == 200:
            content_disp = download_response.headers.get("Content-Disposition", "")
            assert "inline" in content_disp, f"Expected inline disposition, got: {content_disp}"
            print(f"PASS: PDF download returns inline Content-Disposition")
        else:
            print(f"SKIP: Document download returned {download_response.status_code}")


class TestApplicationDocumentsAPI:
    """Tests for application documents endpoints"""

    def test_get_application_documents(self, staff_session):
        """GET /api/applications/{id}/documents should return documents"""
        # Get first application
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        if apps_response.status_code != 200:
            pytest.skip("Could not get applications")
        
        apps = apps_response.json()
        if not apps:
            pytest.skip("No applications found")
        
        app_id = apps[0].get("id")
        response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/documents")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # Check document structure
        if data:
            doc = data[0]
            assert "id" in doc, "Document should have id"
            assert "document_type" in doc, "Document should have document_type"
            assert "filename" in doc, "Document should have filename"
            assert "status" in doc, "Document should have status"
            assert "storage_key" not in doc, "storage_key should not be exposed"
        
        print(f"PASS: Application documents endpoint returns {len(data)} documents")

    def test_document_upload_endpoint(self, applicant_session):
        """POST /api/applications/{id}/documents/upload should accept uploads"""
        # Get applicant's application
        apps_response = applicant_session.get(f"{BASE_URL}/api/applications")
        if apps_response.status_code != 200:
            pytest.skip("Could not get applications")
        
        apps = apps_response.json()
        if not apps:
            pytest.skip("No applications found for applicant")
        
        app_id = apps[0].get("id")
        
        # Test upload with minimal data (no binary)
        response = applicant_session.post(f"{BASE_URL}/api/applications/{app_id}/documents/upload", json={
            "document_type": "other",
            "filename": "test_iter66.pdf",
            "content_type": "application/pdf"
        })
        
        # Should succeed (metadata only upload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Response should contain document id"
        print(f"PASS: Document upload endpoint works, created doc {data.get('id')}")


class TestDocumentReviewAPI:
    """Tests for document review endpoints (staff only)"""

    def test_document_review_approve(self, staff_session):
        """PUT /api/documents/{id}/review should allow approval"""
        # Get a document to review
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        if apps_response.status_code != 200:
            pytest.skip("Could not get applications")
        
        apps = apps_response.json()
        if not apps:
            pytest.skip("No applications found")
        
        app_id = apps[0].get("id")
        docs_response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/documents")
        if docs_response.status_code != 200:
            pytest.skip("Could not get documents")
        
        docs = docs_response.json()
        if not docs:
            pytest.skip("No documents found")
        
        doc_id = docs[0].get("id")
        
        # Test review endpoint
        response = staff_session.put(f"{BASE_URL}/api/documents/{doc_id}/review", json={
            "status": "approved"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"PASS: Document review approve works")

    def test_document_review_reject_with_reason(self, staff_session):
        """PUT /api/documents/{id}/review should allow rejection with reason"""
        # Get a document to review
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        if apps_response.status_code != 200:
            pytest.skip("Could not get applications")
        
        apps = apps_response.json()
        if not apps:
            pytest.skip("No applications found")
        
        app_id = apps[0].get("id")
        docs_response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/documents")
        if docs_response.status_code != 200:
            pytest.skip("Could not get documents")
        
        docs = docs_response.json()
        if not docs:
            pytest.skip("No documents found")
        
        doc_id = docs[0].get("id")
        
        # Test reject with reason
        response = staff_session.put(f"{BASE_URL}/api/documents/{doc_id}/review", json={
            "status": "rejected",
            "rejection_reason": "Test rejection from iteration 66"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print(f"PASS: Document review reject with reason works")


class TestAuthEndpoints:
    """Basic auth tests to ensure login works"""

    def test_staff_login(self, api_client):
        """Staff login should work"""
        response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        # Login returns user data directly (not wrapped in "user" key)
        assert "role" in data, "Response should contain role"
        assert data["role"] == "staff", f"Expected staff role, got {data['role']}"
        print(f"PASS: Staff login successful")

    def test_applicant_login(self):
        """Applicant login should work"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        # Login returns user data directly (not wrapped in "user" key)
        assert data["role"] == "applicant", f"Expected applicant role, got {data['role']}"
        print(f"PASS: Applicant login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
