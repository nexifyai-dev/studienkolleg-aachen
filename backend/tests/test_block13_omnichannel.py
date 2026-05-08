"""
Block 13 Tests: Omnichannel Messaging, Conversation Stats, Channel Filtering
Tests for:
- GET /api/conversations/stats - channel counts and unread count
- GET /api/conversations?channel=portal - filter by channel
- PUT /api/conversations/{conv_id}/read-all - mark messages as read
- POST /api/messages with channel field
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Create authenticated staff session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert response.status_code == 200, f"Staff login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Create authenticated applicant session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    assert response.status_code == 200, f"Applicant login failed: {response.text}"
    return session


class TestConversationStats:
    """Test GET /api/conversations/stats endpoint"""
    
    def test_stats_returns_channel_counts(self, staff_session):
        """Stats endpoint should return portal, email, whatsapp counts"""
        response = staff_session.get(f"{BASE_URL}/api/conversations/stats")
        assert response.status_code == 200, f"Stats failed: {response.text}"
        
        data = response.json()
        # Verify required fields exist
        assert "portal" in data, "Missing 'portal' count in stats"
        assert "email" in data, "Missing 'email' count in stats"
        assert "whatsapp" in data, "Missing 'whatsapp' count in stats"
        assert "total" in data, "Missing 'total' count in stats"
        assert "unread" in data, "Missing 'unread' count in stats"
        
        # Verify types
        assert isinstance(data["portal"], int), "portal count should be int"
        assert isinstance(data["email"], int), "email count should be int"
        assert isinstance(data["whatsapp"], int), "whatsapp count should be int"
        assert isinstance(data["total"], int), "total count should be int"
        assert isinstance(data["unread"], int), "unread count should be int"
        
        print(f"Stats: portal={data['portal']}, email={data['email']}, whatsapp={data['whatsapp']}, total={data['total']}, unread={data['unread']}")


class TestChannelFiltering:
    """Test GET /api/conversations?channel=X filtering"""
    
    def test_list_all_conversations(self, staff_session):
        """List all conversations without filter"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200, f"List conversations failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Total conversations: {len(data)}")
    
    def test_filter_by_portal_channel(self, staff_session):
        """Filter conversations by portal channel"""
        response = staff_session.get(f"{BASE_URL}/api/conversations?channel=portal")
        assert response.status_code == 200, f"Filter by portal failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        # All returned conversations should have channel=portal or no channel (defaults to portal)
        for conv in data:
            channel = conv.get("channel", "portal")
            assert channel == "portal", f"Expected portal channel, got {channel}"
        print(f"Portal conversations: {len(data)}")
    
    def test_filter_by_email_channel(self, staff_session):
        """Filter conversations by email channel"""
        response = staff_session.get(f"{BASE_URL}/api/conversations?channel=email")
        assert response.status_code == 200, f"Filter by email failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        for conv in data:
            assert conv.get("channel") == "email", f"Expected email channel, got {conv.get('channel')}"
        print(f"Email conversations: {len(data)}")
    
    def test_filter_by_whatsapp_channel(self, staff_session):
        """Filter conversations by whatsapp channel"""
        response = staff_session.get(f"{BASE_URL}/api/conversations?channel=whatsapp")
        assert response.status_code == 200, f"Filter by whatsapp failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        for conv in data:
            assert conv.get("channel") == "whatsapp", f"Expected whatsapp channel, got {conv.get('channel')}"
        print(f"WhatsApp conversations: {len(data)}")


class TestMessageWithChannel:
    """Test POST /api/messages with channel field"""
    
    def test_create_message_with_portal_channel(self, staff_session):
        """Create a message with portal channel"""
        # First get or create a conversation
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        
        convs = response.json()
        if len(convs) == 0:
            # Create a new conversation by sending a message
            response = staff_session.post(f"{BASE_URL}/api/messages", json={
                "content": "TEST_Block13_Portal_Message",
                "channel": "portal"
            })
            assert response.status_code == 200, f"Create message failed: {response.text}"
            msg = response.json()
            assert msg.get("channel") == "portal", f"Expected portal channel, got {msg.get('channel')}"
            print(f"Created new message with portal channel: {msg.get('id')}")
        else:
            # Use existing conversation
            conv_id = convs[0]["id"]
            response = staff_session.post(f"{BASE_URL}/api/messages", json={
                "conversation_id": conv_id,
                "content": "TEST_Block13_Portal_Message",
                "channel": "portal"
            })
            assert response.status_code == 200, f"Create message failed: {response.text}"
            msg = response.json()
            assert msg.get("channel") == "portal", f"Expected portal channel, got {msg.get('channel')}"
            print(f"Created message in conversation {conv_id} with portal channel")
    
    def test_message_channel_defaults_to_portal(self, staff_session):
        """Message without channel should default to portal"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        
        convs = response.json()
        if len(convs) > 0:
            conv_id = convs[0]["id"]
            response = staff_session.post(f"{BASE_URL}/api/messages", json={
                "conversation_id": conv_id,
                "content": "TEST_Block13_Default_Channel"
            })
            assert response.status_code == 200, f"Create message failed: {response.text}"
            msg = response.json()
            # Should default to portal
            assert msg.get("channel") == "portal", f"Expected portal channel (default), got {msg.get('channel')}"
            print("Message without channel defaults to portal - PASS")


class TestReadAllMessages:
    """Test PUT /api/conversations/{conv_id}/read-all endpoint"""
    
    def test_mark_conversation_read(self, staff_session):
        """Mark all messages in a conversation as read"""
        # Get conversations
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        
        convs = response.json()
        if len(convs) == 0:
            pytest.skip("No conversations to test read-all")
        
        conv_id = convs[0]["id"]
        
        # Mark all as read
        response = staff_session.put(f"{BASE_URL}/api/conversations/{conv_id}/read-all")
        assert response.status_code == 200, f"Read-all failed: {response.text}"
        
        data = response.json()
        assert data.get("status") == "ok", f"Expected status=ok, got {data}"
        print(f"Marked conversation {conv_id} as read - PASS")


class TestConversationEnrichment:
    """Test that conversations include channel info and badges"""
    
    def test_conversations_have_channel_field(self, staff_session):
        """Conversations should include channel field"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        
        convs = response.json()
        for conv in convs[:5]:  # Check first 5
            # Channel should exist (defaults to portal if not set)
            channel = conv.get("channel", "portal")
            assert channel in ["portal", "email", "whatsapp"], f"Invalid channel: {channel}"
            
            # Should have participant_names
            assert "participant_names" in conv, "Missing participant_names"
            
            # Should have participant_roles
            assert "participant_roles" in conv, "Missing participant_roles"
        
        print(f"Checked {min(5, len(convs))} conversations for channel enrichment - PASS")


class TestHealthAndAuth:
    """Basic health and auth tests"""
    
    def test_health_endpoint(self):
        """Health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("Health check - PASS")
    
    def test_staff_auth_me(self, staff_session):
        """Staff should be able to get their profile"""
        response = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        
        data = response.json()
        assert data.get("email") == STAFF_EMAIL
        assert data.get("role") in ["staff", "admin", "superadmin"]
        print(f"Staff auth verified: {data.get('email')} ({data.get('role')})")
    
    def test_applicant_auth_me(self, applicant_session):
        """Applicant should be able to get their profile"""
        response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200, f"Auth me failed: {response.text}"
        
        data = response.json()
        assert data.get("email") == APPLICANT_EMAIL
        assert data.get("role") == "applicant"
        print(f"Applicant auth verified: {data.get('email')} ({data.get('role')})")
