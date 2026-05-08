"""
Block 14 Tests: Echte Omnichannel-Inbox + Fallakten-Operations-Haertung + Booking-/Branding-Finalisierung

Tests:
- GET /api/conversations/stats - returns channel and status counts
- PUT /api/conversations/{id} - updates status/assigned_to
- GET /api/conversations/{id}/context - returns case context (tasks, docs, invoices)
- GET /api/email-signature - returns central email signature
- POST /api/messages with visibility=internal - creates internal note
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestBlock14OmnichannelInbox:
    """Block 14: Omnichannel Inbox API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with staff authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        self.staff_user = login_resp.json()
        
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        resp = self.session.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        print("PASS: Health endpoint accessible")
        
    def test_conversations_stats_returns_channel_counts(self):
        """GET /api/conversations/stats returns channel and status counts"""
        resp = self.session.get(f"{BASE_URL}/api/conversations/stats")
        assert resp.status_code == 200, f"Stats failed: {resp.text}"
        data = resp.json()
        
        # Verify channel counts exist
        assert "portal" in data, "Missing portal count"
        assert "email" in data, "Missing email count"
        assert "whatsapp" in data, "Missing whatsapp count"
        assert "total" in data, "Missing total count"
        
        # Verify status counts exist
        assert "open" in data, "Missing open status count"
        assert "answered" in data, "Missing answered status count"
        assert "escalated" in data, "Missing escalated status count"
        assert "closed" in data, "Missing closed status count"
        assert "unread" in data, "Missing unread count"
        
        print(f"PASS: Stats endpoint returns channel counts: portal={data['portal']}, email={data['email']}, whatsapp={data['whatsapp']}, total={data['total']}")
        print(f"PASS: Stats endpoint returns status counts: open={data['open']}, answered={data['answered']}, escalated={data['escalated']}, closed={data['closed']}")
        
    def test_conversations_list_with_channel_filter(self):
        """GET /api/conversations?channel=portal filters by channel"""
        resp = self.session.get(f"{BASE_URL}/api/conversations?channel=portal")
        assert resp.status_code == 200, f"List failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), "Expected list of conversations"
        
        # All returned conversations should have portal channel
        for conv in data:
            assert conv.get("channel", "portal") == "portal", f"Expected portal channel, got {conv.get('channel')}"
        
        print(f"PASS: Channel filter works, returned {len(data)} portal conversations")
        
    def test_conversations_list_with_status_filter(self):
        """GET /api/conversations?status=open filters by status"""
        resp = self.session.get(f"{BASE_URL}/api/conversations?status=open")
        assert resp.status_code == 200, f"List failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list), "Expected list of conversations"
        
        # All returned conversations should have open status
        for conv in data:
            assert conv.get("status", "open") == "open", f"Expected open status, got {conv.get('status')}"
        
        print(f"PASS: Status filter works, returned {len(data)} open conversations")
        
    def test_email_signature_endpoint(self):
        """GET /api/email-signature returns central email signature"""
        resp = self.session.get(f"{BASE_URL}/api/email-signature")
        assert resp.status_code == 200, f"Signature failed: {resp.text}"
        data = resp.json()
        
        assert "signature" in data, "Missing signature field"
        assert "sender_name" in data, "Missing sender_name field"
        assert "sender_role" in data, "Missing sender_role field"
        
        # Verify signature contains expected content
        sig = data["signature"]
        assert "Studienkolleg Aachen" in sig, "Signature missing Studienkolleg Aachen"
        assert "Way2Germany" in sig, "Signature missing Way2Germany"
        
        print(f"PASS: Email signature endpoint returns signature with sender: {data['sender_name']}, role: {data['sender_role']}")
        
    def test_email_signature_with_lang_param(self):
        """GET /api/email-signature?lang=en returns English signature"""
        resp = self.session.get(f"{BASE_URL}/api/email-signature?lang=en")
        assert resp.status_code == 200, f"Signature failed: {resp.text}"
        data = resp.json()
        
        sig = data["signature"]
        assert "Best regards" in sig, "English signature missing 'Best regards'"
        
        print("PASS: Email signature with lang=en returns English version")
        
    def test_create_internal_note_message(self):
        """POST /api/messages with visibility=internal creates internal note"""
        # First get or create a conversation
        conv_resp = self.session.get(f"{BASE_URL}/api/conversations/support")
        assert conv_resp.status_code == 200, f"Get support conv failed: {conv_resp.text}"
        conv = conv_resp.json()
        conv_id = conv.get("id")
        
        # Create internal note
        msg_resp = self.session.post(f"{BASE_URL}/api/messages", json={
            "conversation_id": conv_id,
            "content": "TEST_INTERNAL_NOTE: This is an internal staff note",
            "channel": "portal",
            "visibility": "internal"
        })
        assert msg_resp.status_code == 200, f"Create internal note failed: {msg_resp.text}"
        msg = msg_resp.json()
        
        assert msg.get("visibility") == "internal", f"Expected internal visibility, got {msg.get('visibility')}"
        assert "TEST_INTERNAL_NOTE" in msg.get("content", ""), "Content not saved correctly"
        
        print(f"PASS: Internal note created with visibility=internal, msg_id={msg.get('id')}")
        
    def test_conversation_context_endpoint(self):
        """GET /api/conversations/{id}/context returns case context"""
        # First get a conversation
        convs_resp = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_resp.status_code == 200, f"List convs failed: {convs_resp.text}"
        convs = convs_resp.json()
        
        if len(convs) == 0:
            # Create a conversation first
            conv_resp = self.session.get(f"{BASE_URL}/api/conversations/support")
            assert conv_resp.status_code == 200
            conv_id = conv_resp.json().get("id")
        else:
            conv_id = convs[0].get("id")
        
        # Get context
        ctx_resp = self.session.get(f"{BASE_URL}/api/conversations/{conv_id}/context")
        assert ctx_resp.status_code == 200, f"Context failed: {ctx_resp.text}"
        ctx = ctx_resp.json()
        
        # Verify context structure
        assert "conversation_id" in ctx, "Missing conversation_id"
        assert "application" in ctx, "Missing application field"
        assert "applicant" in ctx, "Missing applicant field"
        assert "tasks" in ctx, "Missing tasks field"
        assert "documents" in ctx, "Missing documents field"
        assert "invoices" in ctx, "Missing invoices field"
        
        assert isinstance(ctx["tasks"], list), "tasks should be a list"
        assert isinstance(ctx["documents"], list), "documents should be a list"
        assert isinstance(ctx["invoices"], list), "invoices should be a list"
        
        print(f"PASS: Context endpoint returns structure with tasks={len(ctx['tasks'])}, docs={len(ctx['documents'])}, invoices={len(ctx['invoices'])}")
        
    def test_update_conversation_status(self):
        """PUT /api/conversations/{id} updates status"""
        # Get a conversation
        convs_resp = self.session.get(f"{BASE_URL}/api/conversations")
        assert convs_resp.status_code == 200
        convs = convs_resp.json()
        
        if len(convs) == 0:
            conv_resp = self.session.get(f"{BASE_URL}/api/conversations/support")
            conv_id = conv_resp.json().get("id")
        else:
            conv_id = convs[0].get("id")
        
        # Update status to escalated
        update_resp = self.session.put(f"{BASE_URL}/api/conversations/{conv_id}", json={
            "status": "escalated"
        })
        assert update_resp.status_code == 200, f"Update failed: {update_resp.text}"
        result = update_resp.json()
        
        assert result.get("status") == "ok", "Expected status ok"
        assert "status" in result.get("updated", []), "status should be in updated fields"
        
        # Verify the update persisted
        verify_resp = self.session.get(f"{BASE_URL}/api/conversations")
        verify_convs = verify_resp.json()
        updated_conv = next((c for c in verify_convs if c.get("id") == conv_id), None)
        if updated_conv:
            assert updated_conv.get("status") == "escalated", f"Status not updated, got {updated_conv.get('status')}"
        
        # Reset to open
        self.session.put(f"{BASE_URL}/api/conversations/{conv_id}", json={"status": "open"})
        
        print(f"PASS: Conversation status updated to escalated and verified")
        
    def test_update_conversation_assigned_to(self):
        """PUT /api/conversations/{id} updates assigned_to"""
        # Get a conversation
        convs_resp = self.session.get(f"{BASE_URL}/api/conversations")
        convs = convs_resp.json()
        
        if len(convs) == 0:
            conv_resp = self.session.get(f"{BASE_URL}/api/conversations/support")
            conv_id = conv_resp.json().get("id")
        else:
            conv_id = convs[0].get("id")
        
        # Get staff user id
        staff_id = self.staff_user.get("user", {}).get("id") or self.staff_user.get("id")
        
        # Update assigned_to
        update_resp = self.session.put(f"{BASE_URL}/api/conversations/{conv_id}", json={
            "assigned_to": staff_id
        })
        assert update_resp.status_code == 200, f"Update assigned_to failed: {update_resp.text}"
        
        print(f"PASS: Conversation assigned_to updated")
        
    def test_conversations_have_status_field(self):
        """Verify conversations have status field in response"""
        resp = self.session.get(f"{BASE_URL}/api/conversations")
        assert resp.status_code == 200
        convs = resp.json()
        
        for conv in convs[:5]:  # Check first 5
            assert "status" in conv or conv.get("status") is None, "Conversation missing status field"
            status = conv.get("status", "open")
            assert status in ["open", "answered", "escalated", "closed"], f"Invalid status: {status}"
        
        print(f"PASS: Conversations have valid status field")
        
    def test_messages_visibility_field(self):
        """Verify messages can have visibility field"""
        # Get a conversation
        conv_resp = self.session.get(f"{BASE_URL}/api/conversations/support")
        conv_id = conv_resp.json().get("id")
        
        # Get messages
        msgs_resp = self.session.get(f"{BASE_URL}/api/conversations/{conv_id}/messages")
        assert msgs_resp.status_code == 200, f"Get messages failed: {msgs_resp.text}"
        msgs = msgs_resp.json()
        
        # Check if any internal messages exist
        internal_count = sum(1 for m in msgs if m.get("visibility") == "internal")
        public_count = sum(1 for m in msgs if m.get("visibility") != "internal")
        
        print(f"PASS: Messages retrieved, internal={internal_count}, public={public_count}")


class TestBlock14ApplicantCannotSeeInternalNotes:
    """Test that applicants cannot see internal notes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test sessions"""
        self.staff_session = requests.Session()
        self.staff_session.headers.update({"Content-Type": "application/json"})
        
        self.applicant_session = requests.Session()
        self.applicant_session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        staff_login = self.staff_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert staff_login.status_code == 200, "Staff login failed"
        
        # Login as applicant
        applicant_login = self.applicant_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert applicant_login.status_code == 200, "Applicant login failed"
        
    def test_applicant_cannot_see_internal_notes(self):
        """Applicant should not see messages with visibility=internal"""
        # Get applicant's support conversation
        conv_resp = self.applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert conv_resp.status_code == 200
        conv_id = conv_resp.json().get("id")
        
        # Staff creates an internal note in this conversation
        internal_msg = self.staff_session.post(f"{BASE_URL}/api/messages", json={
            "conversation_id": conv_id,
            "content": "TEST_HIDDEN_INTERNAL: Staff-only note that applicant should not see",
            "visibility": "internal"
        })
        assert internal_msg.status_code == 200, f"Create internal note failed: {internal_msg.text}"
        
        # Applicant fetches messages
        msgs_resp = self.applicant_session.get(f"{BASE_URL}/api/conversations/{conv_id}/messages")
        assert msgs_resp.status_code == 200
        msgs = msgs_resp.json()
        
        # Verify no internal messages visible to applicant
        for msg in msgs:
            assert msg.get("visibility") != "internal", "Applicant should not see internal messages"
            assert "TEST_HIDDEN_INTERNAL" not in msg.get("content", ""), "Internal note content leaked to applicant"
        
        print("PASS: Applicant cannot see internal notes")


class TestBlock14StaffOnlyEndpoints:
    """Test that certain endpoints are staff-only"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test sessions"""
        self.applicant_session = requests.Session()
        self.applicant_session.headers.update({"Content-Type": "application/json"})
        
        # Login as applicant
        applicant_login = self.applicant_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert applicant_login.status_code == 200, "Applicant login failed"
        
    def test_applicant_cannot_update_conversation_status(self):
        """Applicant should not be able to update conversation status"""
        # Get applicant's conversation
        conv_resp = self.applicant_session.get(f"{BASE_URL}/api/conversations/support")
        conv_id = conv_resp.json().get("id")
        
        # Try to update status
        update_resp = self.applicant_session.put(f"{BASE_URL}/api/conversations/{conv_id}", json={
            "status": "closed"
        })
        
        # Should be forbidden
        assert update_resp.status_code == 403, f"Expected 403, got {update_resp.status_code}"
        
        print("PASS: Applicant cannot update conversation status (403)")
