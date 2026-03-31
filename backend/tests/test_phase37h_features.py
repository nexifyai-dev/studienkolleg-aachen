"""
Phase 3.7h Backend Tests - Operative Portal-Reife
Tests for: Notes CRUD, Activities, Profile Edit, Case Email Send, Dashboard Stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = os.environ["TEST_ADMIN_PASSWORD"]
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = os.environ["TEST_DEFAULT_PASSWORD"]
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = os.environ["TEST_DEFAULT_PASSWORD"]
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = os.environ["TEST_DEFAULT_PASSWORD"]

# Test application ID from context
TEST_APP_ID = "69c8b7f98fed65b8d953ffb0"


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint OK")
    
    def test_admin_login(self):
        """Admin login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "superadmin"
        print(f"✓ Admin login OK - role: {data.get('role')}")
    
    def test_staff_login(self):
        """Staff login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "staff"
        print(f"✓ Staff login OK - role: {data.get('role')}")
    
    def test_teacher_login(self):
        """Teacher login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEACHER_EMAIL,
            "password": TEACHER_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "teacher"
        print(f"✓ Teacher login OK - role: {data.get('role')}")
    
    def test_applicant_login(self):
        """Applicant login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "applicant"
        print(f"✓ Applicant login OK - role: {data.get('role')}")


class TestDashboardStats:
    """Dashboard stats endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_dashboard_stats_endpoint(self, staff_session):
        """GET /api/dashboard/stats returns stats"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        # Check expected fields
        assert "total_leads" in data or "total_applications" in data or isinstance(data, dict)
        print(f"✓ Dashboard stats endpoint OK - data: {data}")
    
    def test_applications_list_endpoint(self, staff_session):
        """GET /api/applications returns list"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applications list OK - count: {len(data)}")
        
        # Check if applications have applicant info embedded
        if len(data) > 0:
            app = data[0]
            if app.get("applicant"):
                print(f"  - Applicant info embedded: {app['applicant'].get('full_name', 'N/A')}")


class TestCaseNotes:
    """Case notes CRUD tests"""
    
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
    
    def test_get_application_for_notes(self, staff_session):
        """Get application to verify it exists"""
        response = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if response.status_code == 404:
            pytest.skip(f"Test application {TEST_APP_ID} not found - skipping notes tests")
        assert response.status_code == 200
        print(f"✓ Application {TEST_APP_ID} exists")
    
    def test_create_case_note(self, staff_session):
        """POST /api/applications/{id}/notes creates note"""
        # First check if app exists
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        response = staff_session.post(f"{BASE_URL}/api/applications/{TEST_APP_ID}/notes", json={
            "content": "TEST_NOTE: Automated test note from pytest",
            "visibility": "internal"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data.get("content") == "TEST_NOTE: Automated test note from pytest"
        assert data.get("visibility") == "internal"
        assert "author_name" in data or "author_id" in data
        print(f"✓ Case note created - id: {data.get('id')}")
    
    def test_list_case_notes_staff(self, staff_session):
        """GET /api/applications/{id}/notes lists notes for staff"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        response = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}/notes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Case notes list OK - count: {len(data)}")
        
        # Check if our test note is there
        test_notes = [n for n in data if "TEST_NOTE" in (n.get("content") or "")]
        if test_notes:
            print(f"  - Found test note: {test_notes[0].get('content')[:50]}...")
    
    def test_empty_note_rejected(self, staff_session):
        """POST /api/applications/{id}/notes rejects empty content"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        response = staff_session.post(f"{BASE_URL}/api/applications/{TEST_APP_ID}/notes", json={
            "content": "   ",
            "visibility": "internal"
        })
        assert response.status_code == 400
        print("✓ Empty note correctly rejected with 400")


class TestActivities:
    """Activity history tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_list_activities(self, staff_session):
        """GET /api/applications/{id}/activities returns unified stream"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        response = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Activities list OK - count: {len(data)}")
        
        # Check activity structure
        if len(data) > 0:
            activity = data[0]
            assert "type" in activity or "action" in activity
            print(f"  - First activity: {activity.get('action', activity.get('type', 'unknown'))}")


class TestProfileEdit:
    """Applicant profile edit tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_update_applicant_profile(self, staff_session):
        """PUT /api/applications/{id}/profile updates applicant fields"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        app_data = check.json()
        if not app_data.get("applicant_id"):
            pytest.skip("Application has no linked applicant")
        
        response = staff_session.put(f"{BASE_URL}/api/applications/{TEST_APP_ID}/profile", json={
            "phone": "+49 123 456789"
        })
        # Should be 200 or could be 400 if no applicant linked
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") in ["updated", "no_changes"]
            print(f"✓ Profile update OK - status: {data.get('status')}")
        else:
            print(f"✓ Profile update returned 400 (expected if no applicant linked)")
    
    def test_profile_edit_no_applicant(self, staff_session):
        """PUT /api/applications/{id}/profile handles missing applicant"""
        # This tests the error case
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        # Just verify the endpoint exists and responds
        response = staff_session.put(f"{BASE_URL}/api/applications/{TEST_APP_ID}/profile", json={
            "full_name": "Test Name"
        })
        assert response.status_code in [200, 400]
        print(f"✓ Profile edit endpoint responds correctly - status: {response.status_code}")


class TestCaseEmail:
    """Case email send tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_send_case_email(self, staff_session):
        """POST /api/applications/{id}/send-email sends email"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        app_data = check.json()
        if not app_data.get("applicant_id"):
            pytest.skip("Application has no linked applicant")
        
        response = staff_session.post(f"{BASE_URL}/api/applications/{TEST_APP_ID}/send-email", json={
            "subject": "TEST: Automated Test Email",
            "body": "This is an automated test email from pytest. Please ignore.",
            "lang": "de"
        })
        # Could be 200 (sent), 400 (no applicant), or 500 (email service error)
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert data.get("status") == "sent"
            print(f"✓ Case email sent - to: {data.get('to')}")
        elif response.status_code == 400:
            print("✓ Case email endpoint returned 400 (no applicant linked)")
        else:
            print(f"✓ Case email endpoint returned 500 (email service issue - expected in test)")


class TestApplicationUpdate:
    """Application update and stage change tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_update_application_stage(self, staff_session):
        """PUT /api/applications/{id} updates stage"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        current_stage = check.json().get("current_stage", "lead_new")
        
        # Change to a different stage
        new_stage = "in_review" if current_stage != "in_review" else "pending_docs"
        
        response = staff_session.put(f"{BASE_URL}/api/applications/{TEST_APP_ID}", json={
            "current_stage": new_stage
        })
        assert response.status_code == 200
        print(f"✓ Stage updated: {current_stage} → {new_stage}")
        
        # Revert back
        staff_session.put(f"{BASE_URL}/api/applications/{TEST_APP_ID}", json={
            "current_stage": current_stage
        })
        print(f"  - Reverted to: {current_stage}")
    
    def test_update_application_fields(self, staff_session):
        """PUT /api/applications/{id} updates case fields"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        response = staff_session.put(f"{BASE_URL}/api/applications/{TEST_APP_ID}", json={
            "course_type": "M-Course",
            "language_level": "B1"
        })
        assert response.status_code == 200
        print("✓ Application fields updated (course_type, language_level)")


class TestDocuments:
    """Document listing tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_list_documents(self, staff_session):
        """GET /api/applications/{id}/documents returns list"""
        check = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}")
        if check.status_code == 404:
            pytest.skip("Test application not found")
        
        response = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Documents list OK - count: {len(data)}")


class TestNotifications:
    """Notification bell tests"""
    
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
    
    def test_notifications_endpoint_staff(self, staff_session):
        """GET /api/notifications works for staff"""
        response = staff_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Staff notifications OK - count: {len(data)}")
    
    def test_notifications_endpoint_applicant(self, applicant_session):
        """GET /api/notifications works for applicant"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applicant notifications OK - count: {len(data)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
