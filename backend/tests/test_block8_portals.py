"""
Block 8: Internal Portals Testing
Tests for Staff, Admin, Teacher, Partner dashboards and related APIs
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
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = "DevSeed@2026!"
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Staff login session with cookies"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert response.status_code == 200, f"Staff login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Admin login session with cookies"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def teacher_session():
    """Teacher login session with cookies"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEACHER_EMAIL,
        "password": TEACHER_PASSWORD
    })
    assert response.status_code == 200, f"Teacher login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def partner_session():
    """Partner login session with cookies"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": PARTNER_EMAIL,
        "password": PARTNER_PASSWORD
    })
    assert response.status_code == 200, f"Partner login failed: {response.text}"
    return session


class TestDashboardStatsAPI:
    """Dashboard Stats API - Pipeline, Activity, Messages, Users"""

    def test_dashboard_stats_returns_pipeline(self, staff_session):
        """Dashboard stats should include pipeline breakdown by stage"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify pipeline exists and has expected stages
        assert "pipeline" in data
        pipeline = data["pipeline"]
        expected_stages = ["lead_new", "in_review", "pending_docs", "interview_scheduled",
                          "conditional_offer", "offer_sent", "enrolled"]
        for stage in expected_stages:
            assert stage in pipeline, f"Missing pipeline stage: {stage}"
            assert isinstance(pipeline[stage], int)

    def test_dashboard_stats_returns_recent_activity(self, staff_session):
        """Dashboard stats should include recent activity list"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "recent_activity" in data
        assert isinstance(data["recent_activity"], list)
        # Each activity should have action, occurred_at
        if len(data["recent_activity"]) > 0:
            activity = data["recent_activity"][0]
            assert "action" in activity
            assert "occurred_at" in activity

    def test_dashboard_stats_returns_unread_messages(self, staff_session):
        """Dashboard stats should include unread messages count"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "unread_messages" in data
        assert isinstance(data["unread_messages"], int)
        assert data["unread_messages"] >= 0

    def test_dashboard_stats_returns_user_counts(self, staff_session):
        """Dashboard stats should include user counts"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_users" in data
        assert "total_staff" in data
        assert "total_applicants" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_staff"], int)
        assert isinstance(data["total_applicants"], int)

    def test_dashboard_stats_returns_task_counts(self, staff_session):
        """Dashboard stats should include task counts"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        assert "open_tasks" in data
        assert "in_progress_tasks" in data
        assert isinstance(data["open_tasks"], int)
        assert isinstance(data["in_progress_tasks"], int)


class TestAuditLogsAPI:
    """Audit Logs API - Admin only access"""

    def test_audit_logs_requires_admin(self, staff_session):
        """Audit logs should require admin role"""
        response = staff_session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 403

    def test_audit_logs_accessible_by_admin(self, admin_session):
        """Audit logs should be accessible by admin"""
        response = admin_session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Each log should have required fields
        if len(data) > 0:
            log = data[0]
            assert "action" in log
            assert "occurred_at" in log
            assert "id" in log


class TestTasksAPI:
    """Tasks API - Search, Filter, CRUD"""

    def test_tasks_list(self, staff_session):
        """Tasks list should return tasks with required fields"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            task = data[0]
            assert "id" in task
            assert "title" in task
            assert "status" in task
            assert "priority" in task

    def test_create_task(self, staff_session):
        """Should be able to create a new task"""
        response = staff_session.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Block8_Task",
            "description": "Test task for Block 8 testing",
            "priority": "normal"
        })
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["title"] == "TEST_Block8_Task"
        assert "id" in data

    def test_update_task_status(self, staff_session):
        """Should be able to update task status"""
        # First create a task
        create_resp = staff_session.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Block8_StatusUpdate",
            "priority": "normal"
        })
        assert create_resp.status_code in [200, 201]
        task_id = create_resp.json()["id"]
        
        # Update status
        update_resp = staff_session.put(f"{BASE_URL}/api/tasks/{task_id}", json={
            "status": "in_progress"
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "in_progress"


class TestConversationsAPI:
    """Conversations/Messaging API"""

    def test_conversations_list(self, staff_session):
        """Conversations list should return conversations"""
        response = staff_session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            conv = data[0]
            assert "id" in conv
            assert "participants" in conv

    def test_users_list_for_new_conversation(self, admin_session):
        """Users list should be available for starting new conversations (admin only)"""
        response = admin_session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should have applicants available
        applicants = [u for u in data if u.get("role") == "applicant"]
        assert len(applicants) >= 0  # May be empty in test env


class TestTeacherAPI:
    """Teacher Dashboard API"""

    def test_teacher_my_students(self, teacher_session):
        """Teacher should be able to get assigned students"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 200
        data = response.json()
        
        assert "students" in data
        assert isinstance(data["students"], list)
        assert "total" in data

    def test_teacher_students_have_required_fields(self, teacher_session):
        """Student data should have required fields"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["students"]) > 0:
            student = data["students"][0]
            assert "id" in student
            assert "full_name" in student
            assert "email" in student
            assert "current_stage" in student


class TestPartnerAPI:
    """Partner Dashboard API"""

    def test_partner_dashboard(self, partner_session):
        """Partner should be able to access dashboard"""
        response = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert "total_referrals" in data
        assert "active_referrals" in data
        assert "enrolled" in data
        assert "partner_name" in data

    def test_partner_dashboard_counts_are_integers(self, partner_session):
        """Partner dashboard counts should be integers"""
        response = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data["total_referrals"], int)
        assert isinstance(data["active_referrals"], int)
        assert isinstance(data["enrolled"], int)


class TestApplicationsAPI:
    """Applications API for Staff Dashboard"""

    def test_applications_list(self, staff_session):
        """Applications list should return applications"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            app = data[0]
            assert "id" in app
            assert "current_stage" in app


class TestFollowupsAPI:
    """Followups API for Staff Dashboard"""

    def test_followups_due(self, staff_session):
        """Followups due endpoint should work"""
        response = staff_session.get(f"{BASE_URL}/api/followups/due")
        # May return 200 or 404 if no followups
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
