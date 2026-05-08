"""
Iteration 67 Tests: CI-Button Concept Extension
Tests for:
1. PUT /api/documents/{id}/review endpoint
2. POST /api/support/chat endpoint
3. Staff login functionality
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


class TestStaffLogin:
    """Test staff login functionality"""
    
    def test_staff_login_success(self):
        """Test successful staff login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "user" in data or "id" in data, "Response should contain user data"
        print(f"PASS: Staff login successful")
    
    def test_staff_login_invalid_password(self):
        """Test login with invalid password"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": "wrongpassword"}
        )
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"
        print(f"PASS: Invalid password correctly rejected")


class TestSupportChatAPI:
    """Test POST /api/support/chat endpoint"""
    
    def test_support_chat_public_access(self):
        """Test support chat works without authentication (visitor context)"""
        response = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "Hello, I need help with my application"}
        )
        assert response.status_code == 200, f"Support chat failed: {response.text}"
        data = response.json()
        assert "response" in data or "message" in data or "reply" in data, "Response should contain AI reply"
        print(f"PASS: Support chat public access works")
    
    def test_support_chat_with_history(self):
        """Test support chat with conversation history"""
        response = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={
                "message": "What documents do I need?",
                "history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hello! How can I help you?"}
                ]
            }
        )
        assert response.status_code == 200, f"Support chat with history failed: {response.text}"
        print(f"PASS: Support chat with history works")
    
    def test_support_chat_empty_message_rejected(self):
        """Test that empty messages are rejected"""
        response = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": ""}
        )
        assert response.status_code in [400, 422], f"Expected 400/422 for empty message, got {response.status_code}"
        print(f"PASS: Empty message correctly rejected")
    
    def test_support_chat_with_staff_auth(self):
        """Test support chat with staff authentication"""
        # Login first
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_response.status_code == 200, "Staff login failed"
        
        # Get cookies from login
        cookies = login_response.cookies
        
        # Make chat request with auth
        response = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "What are my pending tasks?"},
            cookies=cookies
        )
        assert response.status_code == 200, f"Support chat with auth failed: {response.text}"
        data = response.json()
        # Check for role_context in response
        if "role_context" in data:
            assert data["role_context"] in ["staff", "admin"], f"Expected staff/admin context, got {data.get('role_context')}"
            print(f"PASS: Support chat with staff auth returns correct role_context: {data['role_context']}")
        else:
            print(f"PASS: Support chat with staff auth works (no role_context in response)")


class TestDocumentReviewAPI:
    """Test PUT /api/documents/{id}/review endpoint"""
    
    @pytest.fixture
    def staff_session(self):
        """Create authenticated staff session"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert response.status_code == 200, "Staff login failed"
        return session
    
    def test_get_applications_list(self, staff_session):
        """Test getting applications list to find documents"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Failed to get applications: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Applications should be a list"
        print(f"PASS: Got {len(data)} applications")
        return data
    
    def test_get_application_documents(self, staff_session):
        """Test getting documents for an application"""
        # First get applications
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        assert apps_response.status_code == 200
        apps = apps_response.json()
        
        if len(apps) == 0:
            pytest.skip("No applications found")
        
        # Get documents for first application
        app_id = apps[0].get("id")
        response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/documents")
        assert response.status_code == 200, f"Failed to get documents: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Documents should be a list"
        print(f"PASS: Got {len(data)} documents for application {app_id}")
        return data
    
    def test_document_review_approve(self, staff_session):
        """Test approving a document via review endpoint"""
        # Get applications and documents
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        apps = apps_response.json()
        
        if len(apps) == 0:
            pytest.skip("No applications found")
        
        # Find a document to review
        doc_id = None
        for app in apps[:5]:  # Check first 5 apps
            docs_response = staff_session.get(f"{BASE_URL}/api/applications/{app.get('id')}/documents")
            if docs_response.status_code == 200:
                docs = docs_response.json()
                if len(docs) > 0:
                    doc_id = docs[0].get("id")
                    break
        
        if not doc_id:
            pytest.skip("No documents found to review")
        
        # Test approve endpoint
        response = staff_session.put(
            f"{BASE_URL}/api/documents/{doc_id}/review",
            json={"status": "approved"}
        )
        assert response.status_code in [200, 201], f"Document review approve failed: {response.text}"
        print(f"PASS: Document {doc_id} review approve endpoint works")
    
    def test_document_review_reject_with_reason(self, staff_session):
        """Test rejecting a document with reason"""
        # Get applications and documents
        apps_response = staff_session.get(f"{BASE_URL}/api/applications")
        apps = apps_response.json()
        
        if len(apps) == 0:
            pytest.skip("No applications found")
        
        # Find a document to review
        doc_id = None
        for app in apps[:5]:
            docs_response = staff_session.get(f"{BASE_URL}/api/applications/{app.get('id')}/documents")
            if docs_response.status_code == 200:
                docs = docs_response.json()
                if len(docs) > 0:
                    doc_id = docs[0].get("id")
                    break
        
        if not doc_id:
            pytest.skip("No documents found to review")
        
        # Test reject endpoint with reason
        response = staff_session.put(
            f"{BASE_URL}/api/documents/{doc_id}/review",
            json={
                "status": "rejected",
                "rejection_reason": "Test rejection - document quality insufficient"
            }
        )
        assert response.status_code in [200, 201], f"Document review reject failed: {response.text}"
        print(f"PASS: Document {doc_id} review reject with reason works")
    
    def test_document_review_unauthorized(self):
        """Test that unauthenticated users cannot review documents"""
        response = requests.put(
            f"{BASE_URL}/api/documents/test-id/review",
            json={"status": "approved"}
        )
        assert response.status_code in [401, 403], f"Expected 401/403, got {response.status_code}"
        print(f"PASS: Unauthenticated document review correctly rejected")


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Test API is responding"""
        response = requests.get(f"{BASE_URL}/api/health")
        # Some APIs use /health, some use /api/health
        if response.status_code == 404:
            response = requests.get(f"{BASE_URL}/health")
        
        # If still 404, try root
        if response.status_code == 404:
            response = requests.get(f"{BASE_URL}/")
        
        assert response.status_code in [200, 301, 302], f"API not responding: {response.status_code}"
        print(f"PASS: API is responding")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
