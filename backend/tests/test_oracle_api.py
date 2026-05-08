"""
Oracle API Tests – Iteration 58
Tests for the new Oracle feature (zentrale Wissensquelle mit Live-Daten und KI-Chat).

Endpoints tested:
- POST /api/oracle/chat - Send message, get AI response
- GET /api/oracle/context - Get live system snapshot
- GET /api/oracle/conversations - List all conversations
- GET /api/oracle/conversations/{id} - Get single conversation
- DELETE /api/oracle/conversations/{id} - Delete conversation
- Auth: Only staff roles have access (403 for applicants)
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
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestOracleAuth:
    """Test Oracle API authentication and authorization"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        return session
    
    def test_oracle_context_requires_auth(self):
        """Test that /api/oracle/context requires authentication"""
        response = requests.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_oracle_context_forbidden_for_applicant(self, applicant_session):
        """Test that applicants cannot access Oracle context"""
        response = applicant_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 403, f"Expected 403 for applicant, got {response.status_code}"
    
    def test_oracle_chat_forbidden_for_applicant(self, applicant_session):
        """Test that applicants cannot use Oracle chat"""
        response = applicant_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "Test message"
        })
        assert response.status_code == 403, f"Expected 403 for applicant, got {response.status_code}"
    
    def test_oracle_conversations_forbidden_for_applicant(self, applicant_session):
        """Test that applicants cannot list Oracle conversations"""
        response = applicant_session.get(f"{BASE_URL}/api/oracle/conversations")
        assert response.status_code == 403, f"Expected 403 for applicant, got {response.status_code}"


class TestOracleContext:
    """Test Oracle context endpoint (live system snapshot)"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        return session
    
    def test_oracle_context_returns_live_data(self, staff_session):
        """Test that /api/oracle/context returns live system data"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify structure
        assert "timestamp" in data, "Missing timestamp in context"
        assert "applications" in data, "Missing applications in context"
        assert "tasks" in data, "Missing tasks in context"
        assert "invoices" in data, "Missing invoices in context"
        assert "documents" in data, "Missing documents in context"
        assert "users" in data, "Missing users in context"
        
        # Verify applications structure
        assert "total" in data["applications"], "Missing total in applications"
        assert "pipeline" in data["applications"], "Missing pipeline in applications"
        assert isinstance(data["applications"]["total"], int), "applications.total should be int"
        
        # Verify tasks structure
        assert "total" in data["tasks"], "Missing total in tasks"
        assert "open" in data["tasks"], "Missing open in tasks"
        assert "overdue" in data["tasks"], "Missing overdue in tasks"
        
        # Verify invoices structure
        assert "total" in data["invoices"], "Missing total in invoices"
        assert "by_status" in data["invoices"], "Missing by_status in invoices"
        
        # Verify documents structure
        assert "total" in data["documents"], "Missing total in documents"
        assert "pending_review" in data["documents"], "Missing pending_review in documents"
        
        print(f"Context data: applications={data['applications']['total']}, tasks={data['tasks']['total']}, invoices={data['invoices']['total']}")


class TestOracleChat:
    """Test Oracle chat endpoint (AI-powered Q&A)"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        return session
    
    def test_oracle_chat_creates_conversation(self, staff_session):
        """Test that sending a chat message creates a new conversation"""
        response = staff_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "TEST_ORACLE: Wie viele Bewerbungen gibt es aktuell?"
        }, timeout=60)  # Long timeout for AI inference
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "conversation_id" in data, "Missing conversation_id in response"
        assert "response" in data, "Missing response in response"
        assert "context_snapshot" in data, "Missing context_snapshot in response"
        
        # Verify conversation_id is valid
        assert data["conversation_id"] is not None, "conversation_id should not be None"
        assert len(data["conversation_id"]) > 0, "conversation_id should not be empty"
        
        # Verify AI response exists
        assert data["response"] is not None, "AI response should not be None"
        assert len(data["response"]) > 0, "AI response should not be empty"
        
        # Verify context snapshot
        assert "total_applications" in data["context_snapshot"], "Missing total_applications in context_snapshot"
        assert "open_tasks" in data["context_snapshot"], "Missing open_tasks in context_snapshot"
        
        print(f"Chat response: conversation_id={data['conversation_id']}, response_length={len(data['response'])}")
        
        # Store conversation_id for cleanup
        self.__class__.test_conversation_id = data["conversation_id"]
    
    def test_oracle_chat_continues_conversation(self, staff_session):
        """Test that sending a message with conversation_id continues the conversation"""
        # First create a conversation
        response1 = staff_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "TEST_ORACLE: Gib mir eine kurze Zusammenfassung."
        }, timeout=60)
        
        assert response1.status_code == 200, f"First message failed: {response1.text}"
        conv_id = response1.json()["conversation_id"]
        
        # Continue the conversation
        response2 = staff_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "TEST_ORACLE: Und wie viele offene Aufgaben?",
            "conversation_id": conv_id
        }, timeout=60)
        
        assert response2.status_code == 200, f"Second message failed: {response2.text}"
        
        data = response2.json()
        assert data["conversation_id"] == conv_id, "conversation_id should remain the same"
        assert data["response"] is not None, "AI response should not be None"
        
        print(f"Continued conversation: {conv_id}")
        
        # Store for cleanup
        self.__class__.continued_conversation_id = conv_id
    
    def test_oracle_chat_validates_message(self, staff_session):
        """Test that empty messages are rejected"""
        response = staff_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": ""
        })
        
        # Should return 422 (validation error) for empty message
        assert response.status_code == 422, f"Expected 422 for empty message, got {response.status_code}"


class TestOracleConversations:
    """Test Oracle conversations management endpoints"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        return session
    
    def test_list_conversations(self, staff_session):
        """Test listing all Oracle conversations"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/conversations")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        # If there are conversations, verify structure
        if len(data) > 0:
            conv = data[0]
            assert "id" in conv, "Missing id in conversation"
            assert "title" in conv, "Missing title in conversation"
            assert "created_at" in conv, "Missing created_at in conversation"
            assert "updated_at" in conv, "Missing updated_at in conversation"
            print(f"Found {len(data)} conversations, first: {conv.get('title', 'N/A')[:50]}")
        else:
            print("No conversations found (this is OK for fresh database)")
    
    def test_get_single_conversation(self, staff_session):
        """Test getting a single conversation with messages"""
        # First create a conversation
        chat_response = staff_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "TEST_ORACLE: Kurze Testfrage fuer Konversationsabruf."
        }, timeout=60)
        
        assert chat_response.status_code == 200, f"Chat failed: {chat_response.text}"
        conv_id = chat_response.json()["conversation_id"]
        
        # Get the conversation
        response = staff_session.get(f"{BASE_URL}/api/oracle/conversations/{conv_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Missing id in conversation"
        assert "title" in data, "Missing title in conversation"
        assert "messages" in data, "Missing messages in conversation"
        assert isinstance(data["messages"], list), "messages should be a list"
        assert len(data["messages"]) >= 2, "Should have at least 2 messages (user + assistant)"
        
        # Verify message structure
        user_msg = data["messages"][0]
        assert user_msg["role"] == "user", "First message should be from user"
        assert "content" in user_msg, "Missing content in message"
        
        assistant_msg = data["messages"][1]
        assert assistant_msg["role"] == "assistant", "Second message should be from assistant"
        
        print(f"Conversation {conv_id} has {len(data['messages'])} messages")
        
        # Store for cleanup
        self.__class__.single_conv_id = conv_id
    
    def test_get_nonexistent_conversation(self, staff_session):
        """Test getting a non-existent conversation returns 404"""
        fake_id = "000000000000000000000000"  # Valid ObjectId format but doesn't exist
        response = staff_session.get(f"{BASE_URL}/api/oracle/conversations/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_get_invalid_conversation_id(self, staff_session):
        """Test getting with invalid ID format returns 400"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/conversations/invalid-id")
        
        assert response.status_code == 400, f"Expected 400 for invalid ID, got {response.status_code}"
    
    def test_delete_conversation(self, staff_session):
        """Test deleting a conversation"""
        # First create a conversation to delete
        chat_response = staff_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "TEST_ORACLE: Diese Konversation wird geloescht."
        }, timeout=60)
        
        assert chat_response.status_code == 200, f"Chat failed: {chat_response.text}"
        conv_id = chat_response.json()["conversation_id"]
        
        # Delete the conversation
        delete_response = staff_session.delete(f"{BASE_URL}/api/oracle/conversations/{conv_id}")
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        data = delete_response.json()
        assert data.get("status") == "deleted", "Response should confirm deletion"
        
        # Verify it's actually deleted
        get_response = staff_session.get(f"{BASE_URL}/api/oracle/conversations/{conv_id}")
        assert get_response.status_code == 404, "Deleted conversation should return 404"
        
        print(f"Successfully deleted conversation {conv_id}")
    
    def test_delete_nonexistent_conversation(self, staff_session):
        """Test deleting a non-existent conversation returns 404"""
        fake_id = "000000000000000000000000"
        response = staff_session.delete(f"{BASE_URL}/api/oracle/conversations/{fake_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestOracleAdminAccess:
    """Test that admin role also has Oracle access"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    def test_admin_can_access_context(self, admin_session):
        """Test that admin can access Oracle context"""
        response = admin_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 200, f"Admin should access context, got {response.status_code}"
        
        data = response.json()
        assert "applications" in data, "Missing applications in context"
        print("Admin can access Oracle context")
    
    def test_admin_can_use_chat(self, admin_session):
        """Test that admin can use Oracle chat"""
        response = admin_session.post(f"{BASE_URL}/api/oracle/chat", json={
            "message": "TEST_ORACLE_ADMIN: Kurze Testfrage vom Admin."
        }, timeout=60)
        
        assert response.status_code == 200, f"Admin should use chat, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "conversation_id" in data, "Missing conversation_id"
        assert "response" in data, "Missing response"
        print(f"Admin chat successful, conversation_id={data['conversation_id']}")


# Cleanup fixture to remove test conversations
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_conversations():
    """Cleanup test conversations after all tests"""
    yield
    
    # Login as staff to cleanup
    session = requests.Session()
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    
    if response.status_code == 200:
        # Get all conversations
        convs_response = session.get(f"{BASE_URL}/api/oracle/conversations")
        if convs_response.status_code == 200:
            convs = convs_response.json()
            for conv in convs:
                if conv.get("title", "").startswith("TEST_ORACLE"):
                    session.delete(f"{BASE_URL}/api/oracle/conversations/{conv['id']}")
                    print(f"Cleaned up test conversation: {conv['id']}")
