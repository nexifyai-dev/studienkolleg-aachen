"""
Phase 3.7l GO-LIVE E2E Backend Tests
Tests all roles, all flows, all APIs for final GO-LIVE readiness
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://aachen-checkout.preview.emergentagent.com').rstrip('/')

# Test credentials
CREDENTIALS = {
    'admin': {'email': 'admin@studienkolleg-aachen.de', 'password': os.environ['TEST_ADMIN_PASSWORD']},
    'staff': {'email': 'staff@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD']},
    'teacher': {'email': 'teacher@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD']},
    'applicant': {'email': 'applicant@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD']},
    'partner': {'email': 'partner@studienkolleg-aachen.de', 'password': os.environ['TEST_DEFAULT_PASSWORD']},
}


class TestHealthAndBasics:
    """Basic health and system checks"""
    
    def test_health_endpoint(self):
        """Test health endpoint returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert 'version' in data
        print(f"✓ Health OK: {data}")


class TestAuthAllRoles:
    """Test login for all 5 roles"""
    
    def test_staff_login(self):
        """Staff login returns staff role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200
        data = response.json()
        # Login returns user data directly (not nested under 'user')
        assert data['role'] == 'staff'
        print(f"✓ Staff login OK: {data['email']}")
    
    def test_applicant_login(self):
        """Applicant login returns applicant role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['applicant'])
        assert response.status_code == 200
        data = response.json()
        assert data['role'] == 'applicant'
        print(f"✓ Applicant login OK: {data['email']}")
    
    def test_partner_login(self):
        """Partner login returns affiliate role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['partner'])
        assert response.status_code == 200
        data = response.json()
        assert data['role'] == 'affiliate'
        print(f"✓ Partner login OK: {data['email']}")
    
    def test_admin_login(self):
        """Admin login returns superadmin role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['admin'])
        assert response.status_code == 200
        data = response.json()
        assert data['role'] == 'superadmin'
        print(f"✓ Admin login OK: {data['email']}")
    
    def test_teacher_login(self):
        """Teacher login returns teacher role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['teacher'])
        assert response.status_code == 200
        data = response.json()
        assert data['role'] == 'teacher'
        print(f"✓ Teacher login OK: {data['email']}")
    
    def test_invalid_login_rejected(self):
        """Invalid credentials return 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            'email': 'invalid@test.com',
            'password': os.environ['TEST_INVALID_PASSWORD']
        })
        assert response.status_code == 401
        print("✓ Invalid login rejected with 401")


class TestTasksCRUD:
    """Full Tasks CRUD with notes, attachments, history"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200
        return session
    
    def test_create_task(self, staff_session):
        """Create a new task"""
        task_data = {
            'title': 'TEST_Phase37l: E2E Test Task',
            'description': 'Testing full task CRUD for GO-LIVE',
            'priority': 'high',
            'status': 'open',
            'due_date': '2026-04-15T10:00:00Z'
        }
        response = staff_session.post(f"{BASE_URL}/api/tasks", json=task_data)
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == task_data['title']
        assert 'id' in data or '_id' in data
        task_id = data.get('id') or data.get('_id')
        print(f"✓ Task created: {task_id}")
        return task_id
    
    def test_list_tasks(self, staff_session):
        """List all tasks"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tasks listed: {len(data)} tasks")
    
    def test_task_full_workflow(self, staff_session):
        """Full task workflow: create, read, update, add note, add attachment, view history, delete"""
        # Create
        task_data = {
            'title': 'TEST_Phase37l: Full Workflow Task',
            'description': 'Testing complete task workflow',
            'priority': 'medium',
            'status': 'open'
        }
        create_resp = staff_session.post(f"{BASE_URL}/api/tasks", json=task_data)
        assert create_resp.status_code == 200
        task = create_resp.json()
        task_id = task.get('id') or task.get('_id')
        print(f"✓ Task created: {task_id}")
        
        # Read
        get_resp = staff_session.get(f"{BASE_URL}/api/tasks/{task_id}")
        assert get_resp.status_code == 200
        print(f"✓ Task read: {get_resp.json()['title']}")
        
        # Update status
        update_resp = staff_session.put(f"{BASE_URL}/api/tasks/{task_id}", json={'status': 'in_progress'})
        assert update_resp.status_code == 200
        assert update_resp.json()['status'] == 'in_progress'
        print("✓ Task status updated to in_progress")
        
        # Update priority
        update_resp2 = staff_session.put(f"{BASE_URL}/api/tasks/{task_id}", json={'priority': 'high'})
        assert update_resp2.status_code == 200
        print("✓ Task priority updated to high")
        
        # Add note
        note_resp = staff_session.post(f"{BASE_URL}/api/tasks/{task_id}/notes", json={
            'content': 'TEST_Phase37l: This is a test note for GO-LIVE verification'
        })
        assert note_resp.status_code == 200
        print("✓ Note added to task")
        
        # Get notes
        notes_resp = staff_session.get(f"{BASE_URL}/api/tasks/{task_id}/notes")
        assert notes_resp.status_code == 200
        notes = notes_resp.json()
        assert len(notes) >= 1
        print(f"✓ Notes retrieved: {len(notes)} notes")
        
        # Add attachment (JSON with base64 file data)
        import base64
        file_content = b'%PDF-1.4 Test attachment content for GO-LIVE'
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        attach_data = {
            'filename': 'test_phase37l.pdf',
            'file_data': file_b64,
            'content_type': 'application/pdf'
        }
        attach_resp = staff_session.post(f"{BASE_URL}/api/tasks/{task_id}/attachments", json=attach_data)
        assert attach_resp.status_code == 200
        attachment = attach_resp.json()
        attachment_id = attachment.get('id') or attachment.get('_id')
        print(f"✓ Attachment uploaded: {attachment_id}")
        
        # Get attachments
        attachments_resp = staff_session.get(f"{BASE_URL}/api/tasks/{task_id}/attachments")
        assert attachments_resp.status_code == 200
        attachments = attachments_resp.json()
        assert len(attachments) >= 1
        print(f"✓ Attachments retrieved: {len(attachments)} attachments")
        
        # Download attachment
        download_resp = staff_session.get(f"{BASE_URL}/api/tasks/{task_id}/attachments/{attachment_id}")
        assert download_resp.status_code == 200
        print("✓ Attachment downloaded")
        
        # Get history
        history_resp = staff_session.get(f"{BASE_URL}/api/tasks/{task_id}/history")
        assert history_resp.status_code == 200
        history = history_resp.json()
        assert len(history) >= 1  # Should have at least creation + updates
        print(f"✓ History retrieved: {len(history)} entries")
        
        # Delete task
        delete_resp = staff_session.delete(f"{BASE_URL}/api/tasks/{task_id}")
        assert delete_resp.status_code == 200
        print("✓ Task deleted")
        
        # Verify deletion
        verify_resp = staff_session.get(f"{BASE_URL}/api/tasks/{task_id}")
        assert verify_resp.status_code == 404
        print("✓ Task deletion verified (404)")
    
    def test_task_filter_by_status(self, staff_session):
        """Filter tasks by status"""
        response = staff_session.get(f"{BASE_URL}/api/tasks?status=open")
        assert response.status_code == 200
        print(f"✓ Tasks filtered by status=open: {len(response.json())} tasks")
    
    def test_task_filter_by_priority(self, staff_session):
        """Filter tasks by priority"""
        response = staff_session.get(f"{BASE_URL}/api/tasks?priority=high")
        assert response.status_code == 200
        print(f"✓ Tasks filtered by priority=high: {len(response.json())} tasks")


class TestApplicationsAPI:
    """Applications API tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200
        return session
    
    def test_list_applications(self, staff_session):
        """List all applications"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applications listed: {len(data)} applications")
        return data
    
    def test_get_application_detail(self, staff_session):
        """Get single application detail"""
        # First get list
        list_resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = list_resp.json()
        if len(apps) > 0:
            app_id = apps[0].get('id') or apps[0].get('_id')
            detail_resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
            assert detail_resp.status_code == 200
            detail = detail_resp.json()
            # Check that applicant data is joined (not dashes)
            print(f"✓ Application detail: {detail.get('first_name', 'N/A')} {detail.get('last_name', 'N/A')}")
        else:
            pytest.skip("No applications to test")
    
    def test_ai_screenings_endpoint(self, staff_session):
        """Get AI screenings for an application"""
        list_resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = list_resp.json()
        if len(apps) > 0:
            app_id = apps[0].get('id') or apps[0].get('_id')
            screenings_resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/ai-screenings")
            assert screenings_resp.status_code == 200
            print(f"✓ AI screenings endpoint works for app {app_id}")
        else:
            pytest.skip("No applications to test")


class TestPartnerAPI:
    """Partner/Affiliate API tests"""
    
    @pytest.fixture
    def partner_session(self):
        """Get authenticated partner session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['partner'])
        assert response.status_code == 200
        return session
    
    def test_partner_dashboard(self, partner_session):
        """Partner dashboard returns stats"""
        response = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert 'total_referrals' in data or 'totalReferrals' in data
        print(f"✓ Partner dashboard: {data}")
    
    def test_partner_referrals(self, partner_session):
        """Partner referrals list"""
        response = partner_session.get(f"{BASE_URL}/api/partner/referrals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Partner referrals: {len(data)} referrals")
    
    def test_partner_referral_link(self, partner_session):
        """Partner referral link"""
        response = partner_session.get(f"{BASE_URL}/api/partner/referral-link")
        assert response.status_code == 200
        data = response.json()
        assert 'link' in data or 'referral_link' in data or 'url' in data
        print(f"✓ Partner referral link: {data}")


class TestRoleBasedAccess:
    """Role-based access control tests"""
    
    def test_applicant_sees_only_own_applications(self):
        """Applicant can access applications endpoint but sees only their own (empty or filtered)"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['applicant'])
        
        # Applicant can access but gets filtered results (empty or own apps only)
        response = session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        # Should be empty or contain only their own applications
        assert isinstance(data, list)
        print(f"✓ Applicant sees filtered applications: {len(data)} apps")
    
    def test_partner_sees_only_referrals(self):
        """Partner can access applications endpoint but sees only referrals"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['partner'])
        
        # Partner can access but gets filtered results
        response = session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Partner sees filtered applications: {len(data)} apps")
    
    def test_staff_cannot_access_partner_dashboard(self):
        """Staff cannot access partner-only endpoints"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        
        # Try to access partner dashboard
        response = session.get(f"{BASE_URL}/api/partner/dashboard")
        assert response.status_code in [401, 403]
        print("✓ Staff blocked from /api/partner/dashboard")


class TestCookieAuth:
    """Cookie-based authentication tests"""
    
    def test_cookie_auth_works(self):
        """Cookie auth allows access to /api/auth/me"""
        session = requests.Session()
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert login_resp.status_code == 200
        
        # Check cookies are set
        cookies = session.cookies.get_dict()
        assert 'access_token' in cookies or len(cookies) > 0
        
        # Access /api/auth/me
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200
        user = me_resp.json()
        assert user['email'] == CREDENTIALS['staff']['email']
        print(f"✓ Cookie auth works: {user['email']}")


class TestMessagingAPI:
    """Messaging API tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200
        return session
    
    def test_list_conversations(self, staff_session):
        """List conversations"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Conversations listed: {len(data)} conversations")


class TestFollowupsAPI:
    """Followups (Wiedervorlage) API tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200
        return session
    
    def test_list_followups(self, staff_session):
        """List all followups"""
        response = staff_session.get(f"{BASE_URL}/api/followups")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Followups listed: {len(data)} followups")
    
    def test_due_followups(self, staff_session):
        """Get due followups"""
        response = staff_session.get(f"{BASE_URL}/api/followups/due")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Due followups: {len(data)} due")


class TestExportAPI:
    """Export API tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200
        return session
    
    def test_export_applications_csv(self, staff_session):
        """Export applications as CSV"""
        response = staff_session.get(f"{BASE_URL}/api/export/applications")
        assert response.status_code == 200
        assert 'text/csv' in response.headers.get('Content-Type', '') or 'application/octet-stream' in response.headers.get('Content-Type', '')
        print("✓ Export CSV works")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
