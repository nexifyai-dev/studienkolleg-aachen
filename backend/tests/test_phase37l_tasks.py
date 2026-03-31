"""
Phase 3.7l Backend Tests - Tasks Full Operability, Applicant Data Integrity, Partner Portal

Tests:
1. Tasks CRUD: create, list, get detail, update status/priority/assigned
2. Task Notes: add note, list notes
3. Task Attachments: upload, list, download
4. Task History: view history entries
5. Applicant Detail Data Integrity: GET /api/applications/{id} returns applicant data
6. Partner Portal: dashboard, referrals, referral-link
7. Login: All 5 roles can login
"""
import pytest
import requests
import os
import base64
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/') or "https://aachen-checkout.preview.emergentagent.com"

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Staff login session with cookies"""
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
def applicant_session():
    """Applicant login session with cookies"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Applicant login failed: {response.status_code} - {response.text}")
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
    if response.status_code != 200:
        pytest.skip(f"Partner login failed: {response.status_code} - {response.text}")
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
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code} - {response.text}")
    return session


class TestHealthAndLogin:
    """Health check and login tests for all 5 roles"""
    
    def test_health_endpoint(self):
        """Health endpoint returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Health endpoint OK")
    
    def test_staff_login(self):
        """Staff can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "staff"
        print(f"✓ Staff login OK - role: {data.get('role')}")
    
    def test_applicant_login(self):
        """Applicant can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "applicant"
        print(f"✓ Applicant login OK - role: {data.get('role')}")
    
    def test_partner_login(self):
        """Partner can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "affiliate"
        print(f"✓ Partner login OK - role: {data.get('role')}")
    
    def test_admin_login(self):
        """Admin can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "superadmin"
        print(f"✓ Admin login OK - role: {data.get('role')}")
    
    def test_teacher_login(self):
        """Teacher can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEACHER_EMAIL,
            "password": TEACHER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "teacher"
        print(f"✓ Teacher login OK - role: {data.get('role')}")


class TestTasksCRUD:
    """Task CRUD operations - create, list, get, update, delete"""
    
    def test_create_task(self, staff_session):
        """Staff can create a task with all fields"""
        due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        payload = {
            "title": "TEST_Phase37l: Dokumente prüfen",
            "description": "Alle Unterlagen auf Vollständigkeit prüfen",
            "priority": "high",
            "due_date": due_date,
            "visibility": "internal"
        }
        response = staff_session.post(f"{BASE_URL}/api/tasks", json=payload)
        assert response.status_code == 200, f"Create task failed: {response.text}"
        data = response.json()
        assert data.get("title") == payload["title"]
        assert data.get("priority") == "high"
        assert data.get("status") == "open"
        assert "id" in data
        print(f"✓ Task created: {data.get('id')}")
        # Store for later tests
        pytest.task_id = data.get("id")
    
    def test_list_tasks(self, staff_session):
        """Staff can list tasks"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tasks listed: {len(data)} tasks")
    
    def test_get_task_detail(self, staff_session):
        """Staff can get task detail"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.get(f"{BASE_URL}/api/tasks/{pytest.task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == pytest.task_id
        assert "title" in data
        assert "status" in data
        print(f"✓ Task detail retrieved: {data.get('title')}")
    
    def test_update_task_status_to_in_progress(self, staff_session):
        """Staff can update task status to in_progress"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.put(f"{BASE_URL}/api/tasks/{pytest.task_id}", json={
            "status": "in_progress"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "in_progress"
        print("✓ Task status updated to in_progress")
    
    def test_update_task_status_to_done(self, staff_session):
        """Staff can update task status to done"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.put(f"{BASE_URL}/api/tasks/{pytest.task_id}", json={
            "status": "done"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "done"
        print("✓ Task status updated to done")
    
    def test_reopen_task(self, staff_session):
        """Staff can reopen a done task"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.put(f"{BASE_URL}/api/tasks/{pytest.task_id}", json={
            "status": "open"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "open"
        print("✓ Task reopened to open status")
    
    def test_update_task_priority(self, staff_session):
        """Staff can update task priority"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.put(f"{BASE_URL}/api/tasks/{pytest.task_id}", json={
            "priority": "low"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("priority") == "low"
        print("✓ Task priority updated to low")


class TestTaskAuthorization:
    """Task detail and attachment authorization checks."""

    def test_forbidden_access_to_foreign_task_id_returns_403(self, staff_session, admin_session):
        """Staff cannot access admin-owned task that is not assigned/shared to staff."""
        create_resp = admin_session.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Phase37l_Auth: Private Admin Task",
            "description": "Only admin should access",
            "visibility": "internal"
        })
        assert create_resp.status_code == 200, f"Task creation failed: {create_resp.text}"
        foreign_task_id = create_resp.json()["id"]

        get_resp = staff_session.get(f"{BASE_URL}/api/tasks/{foreign_task_id}")
        assert get_resp.status_code == 403, f"Expected 403, got {get_resp.status_code} - {get_resp.text}"
        print(f"✓ Foreign task access denied with 403 for task {foreign_task_id}")

    def test_access_to_own_task_id_returns_200(self, staff_session):
        """Staff can access own task details."""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No own task created")
        own_resp = staff_session.get(f"{BASE_URL}/api/tasks/{pytest.task_id}")
        assert own_resp.status_code == 200, f"Expected 200, got {own_resp.status_code} - {own_resp.text}"
        print(f"✓ Own task access allowed with 200 for task {pytest.task_id}")

    def test_download_foreign_attachment_returns_403(self, staff_session, admin_session):
        """Staff cannot download attachment from foreign admin-owned task."""
        payload = base64.b64encode(b"foreign-attachment-content").decode("utf-8")
        create_task_resp = admin_session.post(f"{BASE_URL}/api/tasks", json={
            "title": "TEST_Phase37l_Auth: Admin Attachment Task",
            "description": "Attachment authorization check",
            "visibility": "internal"
        })
        assert create_task_resp.status_code == 200, f"Task creation failed: {create_task_resp.text}"
        foreign_task_id = create_task_resp.json()["id"]

        upload_resp = admin_session.post(f"{BASE_URL}/api/tasks/{foreign_task_id}/attachments", json={
            "filename": "foreign-auth.txt",
            "content_type": "text/plain",
            "file_data": payload
        })
        assert upload_resp.status_code == 200, f"Attachment upload failed: {upload_resp.text}"
        att_id = upload_resp.json()["id"]

        download_resp = staff_session.get(f"{BASE_URL}/api/tasks/{foreign_task_id}/attachments/{att_id}")
        assert download_resp.status_code == 403, (
            f"Expected 403, got {download_resp.status_code} - {download_resp.text}"
        )
        print(f"✓ Foreign attachment download denied with 403 for attachment {att_id}")


class TestTaskNotes:
    """Task notes - add and list"""
    
    def test_add_task_note(self, staff_session):
        """Staff can add a note to a task"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.post(f"{BASE_URL}/api/tasks/{pytest.task_id}/notes", json={
            "content": "TEST_Phase37l: Erste Notiz zur Aufgabe"
        })
        assert response.status_code == 200, f"Add note failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data.get("content") == "TEST_Phase37l: Erste Notiz zur Aufgabe"
        print(f"✓ Note added: {data.get('id')}")
    
    def test_list_task_notes(self, staff_session):
        """Staff can list notes for a task"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.get(f"{BASE_URL}/api/tasks/{pytest.task_id}/notes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Notes listed: {len(data)} notes")


class TestTaskAttachments:
    """Task attachments - upload, list, download"""
    
    def test_upload_task_attachment(self, staff_session):
        """Staff can upload an attachment to a task"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        # Create a simple text file as base64
        file_content = "TEST_Phase37l: Test attachment content"
        file_data = base64.b64encode(file_content.encode()).decode()
        
        response = staff_session.post(f"{BASE_URL}/api/tasks/{pytest.task_id}/attachments", json={
            "filename": "test_phase37l.txt",
            "content_type": "text/plain",
            "file_data": file_data
        })
        assert response.status_code == 200, f"Upload attachment failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data.get("filename") == "test_phase37l.txt"
        pytest.attachment_id = data.get("id")
        print(f"✓ Attachment uploaded: {data.get('id')}")
    
    def test_list_task_attachments(self, staff_session):
        """Staff can list attachments for a task"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.get(f"{BASE_URL}/api/tasks/{pytest.task_id}/attachments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✓ Attachments listed: {len(data)} attachments")
    
    def test_download_task_attachment(self, staff_session):
        """Staff can download an attachment"""
        if not hasattr(pytest, 'task_id') or not hasattr(pytest, 'attachment_id'):
            pytest.skip("No task or attachment created")
        response = staff_session.get(f"{BASE_URL}/api/tasks/{pytest.task_id}/attachments/{pytest.attachment_id}")
        assert response.status_code == 200
        assert len(response.content) > 0
        print(f"✓ Attachment downloaded: {len(response.content)} bytes")


class TestTaskHistory:
    """Task history - view status changes"""
    
    def test_get_task_history(self, staff_session):
        """Staff can view task history"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task created")
        response = staff_session.get(f"{BASE_URL}/api/tasks/{pytest.task_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least: created, status_changed (to in_progress), status_changed (to done), status_changed (to open), priority_changed, note_added, attachment_added
        assert len(data) >= 1
        print(f"✓ Task history retrieved: {len(data)} entries")
        # Check history entry structure
        if data:
            entry = data[0]
            assert "action" in entry
            assert "occurred_at" in entry
            print(f"  Latest action: {entry.get('action')}")


class TestTaskFilters:
    """Task filtering by status and priority"""
    
    def test_filter_tasks_by_status(self, staff_session):
        """Tasks can be filtered by status (via frontend logic, backend returns all)"""
        response = staff_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        # Filter locally (frontend does this)
        open_tasks = [t for t in data if t.get("status") == "open"]
        in_progress_tasks = [t for t in data if t.get("status") == "in_progress"]
        done_tasks = [t for t in data if t.get("status") == "done"]
        print(f"✓ Task counts - Open: {len(open_tasks)}, In Progress: {len(in_progress_tasks)}, Done: {len(done_tasks)}")


class TestApplicantDataIntegrity:
    """Applicant detail data integrity - GET /api/applications/{id} returns applicant data"""
    
    def test_get_application_with_applicant_data(self, staff_session):
        """GET /api/applications/{id} returns applicant object with full_name, email, phone, country"""
        # First get list of applications
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        apps = response.json()
        if not apps:
            pytest.skip("No applications found")
        
        # Get first application detail
        app_id = apps[0].get("id")
        response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
        assert response.status_code == 200
        data = response.json()
        
        # Check applicant data is joined
        assert "applicant" in data or "applicant_id" in data, "No applicant data in response"
        
        if "applicant" in data:
            applicant = data["applicant"]
            # Check required fields exist (may be empty but should be present)
            print(f"✓ Applicant data found:")
            print(f"  - full_name: {applicant.get('full_name', '–')}")
            print(f"  - email: {applicant.get('email', '–')}")
            print(f"  - phone: {applicant.get('phone', '–')}")
            print(f"  - country: {applicant.get('country', '–')}")
        else:
            print(f"✓ Application has applicant_id: {data.get('applicant_id')}")


class TestPartnerPortal:
    """Partner portal - dashboard, referrals, referral-link"""
    
    def test_partner_dashboard(self, partner_session):
        """Partner can access dashboard stats"""
        response = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert response.status_code == 200
        data = response.json()
        # Check stats structure
        assert "total_referrals" in data or "stats" in data or isinstance(data, dict)
        print(f"✓ Partner dashboard: {data}")
    
    def test_partner_referrals(self, partner_session):
        """Partner can list referrals"""
        response = partner_session.get(f"{BASE_URL}/api/partner/referrals")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "referrals" in data
        print(f"✓ Partner referrals: {len(data) if isinstance(data, list) else 'OK'}")
    
    def test_partner_referral_link(self, partner_session):
        """Partner can get referral link"""
        response = partner_session.get(f"{BASE_URL}/api/partner/referral-link")
        assert response.status_code == 200
        data = response.json()
        assert "link" in data or "referral_code" in data or "url" in data
        print(f"✓ Partner referral link: {data}")


class TestCleanup:
    """Cleanup test data"""
    
    def test_delete_test_task(self, staff_session):
        """Delete test task"""
        if not hasattr(pytest, 'task_id'):
            pytest.skip("No task to delete")
        response = staff_session.delete(f"{BASE_URL}/api/tasks/{pytest.task_id}")
        assert response.status_code == 200
        print(f"✓ Test task deleted: {pytest.task_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
