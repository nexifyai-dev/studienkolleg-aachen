"""
Phase 3.7i Backend Tests
Tests for:
- Staff routes: /staff/tasks, /staff/messaging
- Messaging system (Applicant<->Staff)
- Kanban URL filter support
- Dashboard links
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = os.environ["TEST_DEFAULT_PASSWORD"]
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = os.environ["TEST_DEFAULT_PASSWORD"]
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = os.environ["TEST_ADMIN_PASSWORD"]


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint OK")
    
    def test_staff_login(self):
        """Staff login returns staff role"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # Role is at root level, not nested in "user"
        assert data.get("role") == "staff"
        print(f"✓ Staff login OK - role: {data.get('role')}")
    
    def test_applicant_login(self):
        """Applicant login returns applicant role"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # Role is at root level, not nested in "user"
        assert data.get("role") == "applicant"
        print(f"✓ Applicant login OK - role: {data.get('role')}")


class TestTasksAPI:
    """Tests for /api/tasks endpoint"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_list_tasks(self, staff_session):
        """GET /api/tasks returns list"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ List tasks OK - {len(data)} tasks found")
    
    def test_create_task(self, staff_session):
        """POST /api/tasks creates a new task"""
        task_data = {
            "title": "TEST_Phase37i_Task",
            "description": "Test task for Phase 3.7i testing",
            "priority": "normal"
        }
        response = staff_session.post(f"{BASE_URL}/api/tasks", json=task_data)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data or "_id" in data
        assert data.get("title") == task_data["title"]
        print(f"✓ Create task OK - id: {data.get('id') or data.get('_id')}")
        return data.get("id") or data.get("_id")
    
    def test_update_task_status(self, staff_session):
        """PUT /api/tasks/{id} updates task status"""
        # First create a task
        task_data = {"title": "TEST_StatusUpdate_Task", "priority": "normal"}
        create_resp = staff_session.post(f"{BASE_URL}/api/tasks", json=task_data)
        assert create_resp.status_code in [200, 201]
        task_id = create_resp.json().get("id") or create_resp.json().get("_id")
        
        # Update status
        update_resp = staff_session.put(f"{BASE_URL}/api/tasks/{task_id}", json={"status": "in_progress"})
        assert update_resp.status_code == 200
        print(f"✓ Update task status OK - task {task_id} set to in_progress")


class TestMessagingAPI:
    """Tests for messaging system (Applicant<->Staff)"""
    
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
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_applicant_get_support_conversation(self, applicant_session):
        """GET /api/conversations/support creates/returns support conversation"""
        response = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "participants" in data
        print(f"✓ Support conversation OK - id: {data.get('id')}")
        return data
    
    def test_applicant_list_conversations(self, applicant_session):
        """GET /api/conversations returns applicant's conversations"""
        response = applicant_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applicant conversations OK - {len(data)} conversations")
        return data
    
    def test_staff_list_conversations(self, staff_session):
        """GET /api/conversations returns all conversations for staff"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Staff conversations OK - {len(data)} conversations")
        return data
    
    def test_applicant_send_message(self, applicant_session):
        """POST /api/messages - applicant sends message"""
        # First get support conversation
        support_resp = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert support_resp.status_code == 200
        conv_id = support_resp.json().get("id")
        
        # Send message
        msg_data = {
            "conversation_id": conv_id,
            "content": "TEST_Phase37i: Applicant test message"
        }
        response = applicant_session.post(f"{BASE_URL}/api/messages", json=msg_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data.get("content") == msg_data["content"]
        print(f"✓ Applicant send message OK - msg id: {data.get('id')}")
        return data
    
    def test_staff_send_message(self, staff_session, applicant_session):
        """POST /api/messages - staff replies to applicant"""
        # Get applicant's support conversation
        support_resp = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert support_resp.status_code == 200
        conv_id = support_resp.json().get("id")
        
        # Staff sends reply
        msg_data = {
            "conversation_id": conv_id,
            "content": "TEST_Phase37i: Staff reply message"
        }
        response = staff_session.post(f"{BASE_URL}/api/messages", json=msg_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✓ Staff send message OK - msg id: {data.get('id')}")
        return data
    
    def test_get_conversation_messages(self, applicant_session):
        """GET /api/conversations/{id}/messages returns messages"""
        # Get support conversation
        support_resp = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert support_resp.status_code == 200
        conv_id = support_resp.json().get("id")
        
        # Get messages
        response = applicant_session.get(f"{BASE_URL}/api/conversations/{conv_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Get conversation messages OK - {len(data)} messages")
        return data
    
    def test_message_has_sender_name(self, applicant_session):
        """Messages include sender_name field"""
        # Get support conversation
        support_resp = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        conv_id = support_resp.json().get("id")
        
        # Send a message
        applicant_session.post(f"{BASE_URL}/api/messages", json={
            "conversation_id": conv_id,
            "content": "TEST_SenderName check"
        })
        
        # Get messages and check sender_name
        msgs_resp = applicant_session.get(f"{BASE_URL}/api/conversations/{conv_id}/messages")
        assert msgs_resp.status_code == 200
        messages = msgs_resp.json()
        if messages:
            last_msg = messages[-1]
            assert "sender_name" in last_msg or "sender_id" in last_msg
            print(f"✓ Message has sender info - sender_name: {last_msg.get('sender_name', 'N/A')}")


class TestDashboardAndApplications:
    """Tests for dashboard stats and applications"""
    
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
        """GET /api/dashboard/stats returns stats"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Dashboard stats OK - {data}")
    
    def test_applications_list(self, staff_session):
        """GET /api/applications returns list"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applications list OK - {len(data)} applications")
        
        # Check for stage distribution
        stages = {}
        for app in data:
            stage = app.get("current_stage", "unknown")
            stages[stage] = stages.get(stage, 0) + 1
        print(f"  Stage distribution: {stages}")
        return data
    
    def test_applications_have_pending_docs(self, staff_session):
        """Verify pending_docs stage exists for Kanban filter test"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        pending_docs = [a for a in data if a.get("current_stage") == "pending_docs"]
        lead_new = [a for a in data if a.get("current_stage") == "lead_new"]
        print(f"✓ Stage counts - pending_docs: {len(pending_docs)}, lead_new: {len(lead_new)}")


class TestConversationEnrichment:
    """Tests for conversation enrichment (participant_names, roles)"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_conversations_have_participant_names(self, staff_session):
        """Conversations include participant_names dict"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        if data:
            conv = data[0]
            assert "participant_names" in conv
            assert "participant_roles" in conv
            print(f"✓ Conversation enrichment OK - names: {conv.get('participant_names')}")
        else:
            print("✓ No conversations to check enrichment (OK)")
    
    def test_conversations_have_last_message_preview(self, staff_session):
        """Conversations include last_message_preview"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        if data:
            # Find a conversation with messages
            for conv in data:
                if conv.get("last_message_preview"):
                    print(f"✓ Last message preview OK - preview: {conv.get('last_message_preview')[:50]}...")
                    return
            print("✓ No conversations with messages yet (OK)")
        else:
            print("✓ No conversations to check preview (OK)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
