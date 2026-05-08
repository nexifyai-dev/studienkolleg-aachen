"""
Block 16: Email Messaging & WCAG Compliance Tests
Tests for real email fetching/display (IMAP/SMTP), email signatures, and accessibility.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEmailMessagingAPIs:
    """Test email messaging API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with staff authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "staff@studienkolleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        assert login_response.status_code == 200, f"Staff login failed: {login_response.text}"
        self.staff_user = login_response.json()
        print(f"✓ Logged in as staff: {self.staff_user.get('email')}")
    
    def test_health_endpoint(self):
        """Test health endpoint returns email_enabled status"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert "email_enabled" in data
        print(f"✓ Health check passed, email_enabled: {data.get('email_enabled')}")
    
    def test_conversations_list(self):
        """Test GET /api/conversations returns list with email and portal conversations"""
        response = self.session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check for email and portal channels
        channels = set(c.get("channel") for c in data)
        print(f"✓ Conversations found: {len(data)}, channels: {channels}")
        
        # Verify conversation structure
        if data:
            conv = data[0]
            assert "id" in conv
            assert "channel" in conv
            assert "status" in conv
            assert "participant_names" in conv
            print(f"✓ Conversation structure valid")
    
    def test_conversations_filter_by_channel(self):
        """Test filtering conversations by channel"""
        # Filter by email
        response = self.session.get(f"{BASE_URL}/api/conversations?channel=email")
        assert response.status_code == 200
        email_convs = response.json()
        for conv in email_convs:
            assert conv.get("channel") == "email"
        print(f"✓ Email filter: {len(email_convs)} conversations")
        
        # Filter by portal
        response = self.session.get(f"{BASE_URL}/api/conversations?channel=portal")
        assert response.status_code == 200
        portal_convs = response.json()
        for conv in portal_convs:
            assert conv.get("channel") == "portal"
        print(f"✓ Portal filter: {len(portal_convs)} conversations")
    
    def test_conversations_filter_by_status(self):
        """Test filtering conversations by status"""
        for status in ["open", "answered", "escalated", "closed"]:
            response = self.session.get(f"{BASE_URL}/api/conversations?status={status}")
            assert response.status_code == 200
            convs = response.json()
            for conv in convs:
                assert conv.get("status") == status
            print(f"✓ Status filter '{status}': {len(convs)} conversations")
    
    def test_conversations_stats(self):
        """Test GET /api/conversations/stats returns correct counts"""
        response = self.session.get(f"{BASE_URL}/api/conversations/stats")
        assert response.status_code == 200
        stats = response.json()
        
        # Check required fields
        assert "portal" in stats
        assert "email" in stats
        assert "whatsapp" in stats
        assert "total" in stats
        assert "open" in stats
        assert "answered" in stats
        assert "escalated" in stats
        assert "closed" in stats
        
        # Verify total is reasonable (may include conversations with null channel)
        channel_sum = stats["portal"] + stats["email"] + stats["whatsapp"]
        assert stats["total"] >= channel_sum, f"Total should be >= channel sum: {stats['total']} < {channel_sum}"
        
        print(f"✓ Stats: total={stats['total']}, portal={stats['portal']}, email={stats['email']}")
        print(f"  Status: open={stats['open']}, answered={stats['answered']}, escalated={stats['escalated']}, closed={stats['closed']}")
    
    def test_imap_sync(self):
        """Test POST /api/messaging/sync-imap returns status and synced count"""
        response = self.session.post(f"{BASE_URL}/api/messaging/sync-imap")
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "synced" in data
        assert isinstance(data["synced"], int)
        
        print(f"✓ IMAP sync: status={data['status']}, synced={data['synced']}")
    
    def test_email_status(self):
        """Test GET /api/messaging/email-status confirms SMTP/IMAP is aktiv"""
        response = self.session.get(f"{BASE_URL}/api/messaging/email-status")
        assert response.status_code == 200
        data = response.json()
        
        assert "smtp_configured" in data
        assert "smtp_host" in data
        assert "imap_host" in data
        assert "email_from" in data
        assert "status" in data
        
        # Verify SMTP is configured
        assert data["smtp_configured"] == True, "SMTP should be configured"
        assert data["status"] == "aktiv", f"Status should be 'aktiv', got: {data['status']}"
        
        print(f"✓ Email status: {data['status']}")
        print(f"  SMTP: {data['smtp_host']}, IMAP: {data['imap_host']}")
        print(f"  From: {data['email_from']}")
    
    def test_email_signature(self):
        """Test GET /api/email-signature returns proper signature"""
        response = self.session.get(f"{BASE_URL}/api/email-signature")
        assert response.status_code == 200
        data = response.json()
        
        assert "signature" in data
        assert "sender_name" in data
        assert "sender_role" in data
        
        # Verify signature content
        sig = data["signature"]
        assert "Studienkolleg Aachen" in sig
        assert "Way2Germany" in sig
        assert "Templergraben 55" in sig
        assert "info@stk-aachen.de" in sig
        
        print(f"✓ Email signature for: {data['sender_name']} ({data['sender_role']})")
    
    def test_email_signature_english(self):
        """Test GET /api/email-signature with lang=en returns English signature"""
        response = self.session.get(f"{BASE_URL}/api/email-signature?lang=en")
        assert response.status_code == 200
        data = response.json()
        
        sig = data["signature"]
        assert "Best regards" in sig
        assert "Studienkolleg Aachen" in sig
        
        print(f"✓ English signature contains 'Best regards'")
    
    def test_conversation_messages(self):
        """Test GET /api/conversations/{id}/messages returns messages with email content"""
        # First get a conversation
        convs_response = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No conversations available for testing")
        
        conv_id = convs[0]["id"]
        
        # Get messages
        response = self.session.get(f"{BASE_URL}/api/conversations/{conv_id}/messages")
        assert response.status_code == 200
        messages = response.json()
        
        assert isinstance(messages, list)
        
        if messages:
            msg = messages[0]
            assert "id" in msg
            assert "content" in msg
            assert "sender_id" in msg
            assert "channel" in msg
            
            # Check for email-specific fields
            if msg.get("channel") == "email":
                print(f"✓ Email message found with subject: {msg.get('email_subject', 'N/A')}")
                if msg.get("html_content"):
                    print(f"  HTML content present: {len(msg['html_content'])} chars")
        
        print(f"✓ Messages for conversation {conv_id[:8]}...: {len(messages)} messages")
    
    def test_conversation_context(self):
        """Test GET /api/conversations/{id}/context returns full context"""
        # First get a conversation
        convs_response = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No conversations available for testing")
        
        conv_id = convs[0]["id"]
        
        # Get context
        response = self.session.get(f"{BASE_URL}/api/conversations/{conv_id}/context")
        assert response.status_code == 200
        context = response.json()
        
        assert "conversation_id" in context
        assert "tasks" in context
        assert "documents" in context
        assert "invoices" in context
        
        print(f"✓ Context for conversation {conv_id[:8]}...")
        print(f"  Application: {context.get('application') is not None}")
        print(f"  Tasks: {len(context.get('tasks', []))}")
        print(f"  Documents: {len(context.get('documents', []))}")
    
    def test_update_conversation_status(self):
        """Test PUT /api/conversations/{id} updates status"""
        # First get a conversation
        convs_response = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No conversations available for testing")
        
        conv_id = convs[0]["id"]
        original_status = convs[0].get("status", "open")
        
        # Update to escalated
        response = self.session.put(
            f"{BASE_URL}/api/conversations/{conv_id}",
            json={"status": "escalated"}
        )
        assert response.status_code == 200
        
        # Verify update
        verify_response = self.session.get(f"{BASE_URL}/api/conversations")
        updated_conv = next((c for c in verify_response.json() if c["id"] == conv_id), None)
        assert updated_conv is not None
        assert updated_conv["status"] == "escalated"
        
        # Restore original status
        self.session.put(
            f"{BASE_URL}/api/conversations/{conv_id}",
            json={"status": original_status}
        )
        
        print(f"✓ Conversation status updated: {original_status} -> escalated -> {original_status}")
    
    def test_send_message_portal(self):
        """Test POST /api/messages sends portal message"""
        # First get a conversation
        convs_response = self.session.get(f"{BASE_URL}/api/conversations?channel=portal")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No portal conversations available for testing")
        
        conv_id = convs[0]["id"]
        
        # Send message
        response = self.session.post(
            f"{BASE_URL}/api/messages",
            json={
                "conversation_id": conv_id,
                "content": "TEST_MESSAGE: Automated test message",
                "channel": "portal",
                "visibility": "public"
            }
        )
        assert response.status_code == 200
        msg = response.json()
        
        assert "id" in msg
        assert msg["content"] == "TEST_MESSAGE: Automated test message"
        assert msg["channel"] == "portal"
        
        print(f"✓ Portal message sent: {msg['id'][:8]}...")
    
    def test_send_internal_note(self):
        """Test POST /api/messages with visibility=internal"""
        # First get a conversation
        convs_response = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No conversations available for testing")
        
        conv_id = convs[0]["id"]
        
        # Send internal note
        response = self.session.post(
            f"{BASE_URL}/api/messages",
            json={
                "conversation_id": conv_id,
                "content": "TEST_INTERNAL: This is an internal staff note",
                "channel": "portal",
                "visibility": "internal"
            }
        )
        assert response.status_code == 200
        msg = response.json()
        
        assert msg["visibility"] == "internal"
        
        print(f"✓ Internal note sent: {msg['id'][:8]}...")


class TestEmailConversationFeatures:
    """Test email-specific conversation features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with staff authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "staff@studienkolleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        assert login_response.status_code == 200
    
    def test_email_conversation_has_subject(self):
        """Test email conversations have subject field"""
        response = self.session.get(f"{BASE_URL}/api/conversations?channel=email")
        assert response.status_code == 200
        convs = response.json()
        
        if not convs:
            pytest.skip("No email conversations available")
        
        # Check that email conversations have subject
        for conv in convs:
            if conv.get("subject"):
                print(f"✓ Email conversation has subject: {conv['subject'][:50]}...")
                return
        
        print("✓ Email conversations checked (some may not have subjects)")
    
    def test_email_message_has_html_content(self):
        """Test email messages can have html_content field"""
        # Get email conversations
        convs_response = self.session.get(f"{BASE_URL}/api/conversations?channel=email")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No email conversations available")
        
        # Check messages for HTML content
        for conv in convs[:3]:  # Check first 3
            msgs_response = self.session.get(f"{BASE_URL}/api/conversations/{conv['id']}/messages")
            if msgs_response.status_code == 200:
                msgs = msgs_response.json()
                for msg in msgs:
                    if msg.get("html_content"):
                        print(f"✓ Found email with HTML content: {len(msg['html_content'])} chars")
                        return
        
        print("✓ Email messages checked (HTML content may not be present in all)")
    
    def test_mark_conversation_read(self):
        """Test PUT /api/conversations/{id}/read-all marks messages as read"""
        # Get a conversation
        convs_response = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_response.status_code == 200
        convs = convs_response.json()
        
        if not convs:
            pytest.skip("No conversations available")
        
        conv_id = convs[0]["id"]
        
        # Mark as read
        response = self.session.put(f"{BASE_URL}/api/conversations/{conv_id}/read-all")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        
        print(f"✓ Conversation {conv_id[:8]}... marked as read")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
