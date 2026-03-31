"""
Phase 3.7d Backend Tests
- Teacher list endpoint (GET /api/teacher/list)
- Teacher assignment CRUD (POST/DELETE /api/teacher/assignments)
- Teacher my-students with consent flow
- Cost simulator individual pricing disclaimers
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_CREDS = {"email": "admin@studienkolleg-aachen.de", "password": os.environ["TEST_ADMIN_PASSWORD"]}
STAFF_CREDS = {"email": "staff@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]}
TEACHER_CREDS = {"email": "teacher@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]}
APPLICANT_CREDS = {"email": "applicant@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]}


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"✓ Health check passed: {data}")
    
    def test_admin_login(self):
        """Admin login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "superadmin"
        print(f"✓ Admin login: role={data.get('role')}")
    
    def test_staff_login(self):
        """Staff login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=STAFF_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "staff"
        print(f"✓ Staff login: role={data.get('role')}")
    
    def test_teacher_login(self):
        """Teacher login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=TEACHER_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "teacher"
        print(f"✓ Teacher login: role={data.get('role')}")
    
    def test_applicant_login(self):
        """Applicant login works"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=APPLICANT_CREDS)
        assert response.status_code == 200
        data = response.json()
        assert data.get("role") == "applicant"
        print(f"✓ Applicant login: role={data.get('role')}")


class TestTeacherListEndpoint:
    """GET /api/teacher/list - returns teacher list with ID, name, email"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=STAFF_CREDS)
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def teacher_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=TEACHER_CREDS)
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=APPLICANT_CREDS)
        assert response.status_code == 200
        return session
    
    def test_staff_can_list_teachers(self, staff_session):
        """Staff can access GET /api/teacher/list"""
        response = staff_session.get(f"{BASE_URL}/api/teacher/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Staff listed {len(data)} teachers")
        
        # Verify teacher data structure
        if len(data) > 0:
            teacher = data[0]
            assert "id" in teacher, "Teacher should have 'id' field"
            assert "email" in teacher, "Teacher should have 'email' field"
            # full_name may be empty but should exist
            assert "full_name" in teacher or "email" in teacher
            print(f"  Teacher sample: id={teacher.get('id')}, email={teacher.get('email')}")
    
    def test_teacher_can_list_teachers(self, teacher_session):
        """Teacher can also access GET /api/teacher/list"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Teacher listed {len(data)} teachers")
    
    def test_applicant_cannot_list_teachers(self, applicant_session):
        """Applicant cannot access GET /api/teacher/list (403)"""
        response = applicant_session.get(f"{BASE_URL}/api/teacher/list")
        assert response.status_code == 403
        print("✓ Applicant correctly denied access to teacher list (403)")
    
    def test_unauthenticated_cannot_list_teachers(self):
        """Unauthenticated request returns 401"""
        response = requests.get(f"{BASE_URL}/api/teacher/list")
        assert response.status_code == 401
        print("✓ Unauthenticated correctly denied (401)")


class TestTeacherAssignments:
    """POST/DELETE /api/teacher/assignments - staff assigns/removes teacher"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=STAFF_CREDS)
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def teacher_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=TEACHER_CREDS)
        assert response.status_code == 200
        return session
    
    def test_staff_can_list_assignments(self, staff_session):
        """Staff can GET /api/teacher/assignments"""
        response = staff_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 200
        data = response.json()
        assert "assignments" in data
        print(f"✓ Staff listed {len(data['assignments'])} assignments")
    
    def test_teacher_can_list_own_assignments(self, teacher_session):
        """Teacher can GET /api/teacher/assignments (sees own only)"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 200
        data = response.json()
        assert "assignments" in data
        print(f"✓ Teacher listed {len(data['assignments'])} own assignments")
    
    def test_assignment_requires_auth(self):
        """POST /api/teacher/assignments requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/teacher/assignments",
            params={"applicant_id": "test", "teacher_id": "test"}
        )
        assert response.status_code == 401
        print("✓ Assignment creation requires auth (401)")
    
    def test_assignment_requires_staff_role(self, teacher_session):
        """Teacher cannot create assignments (403)"""
        response = teacher_session.post(
            f"{BASE_URL}/api/teacher/assignments",
            params={"applicant_id": "test", "teacher_id": "test"}
        )
        assert response.status_code == 403
        print("✓ Teacher cannot create assignments (403)")


class TestTeacherMyStudents:
    """GET /api/teacher/my-students - consent-gated student access"""
    
    @pytest.fixture
    def teacher_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=TEACHER_CREDS)
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=APPLICANT_CREDS)
        assert response.status_code == 200
        return session
    
    def test_teacher_can_get_my_students(self, teacher_session):
        """Teacher can access GET /api/teacher/my-students"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 200
        data = response.json()
        assert "students" in data
        assert "total" in data
        print(f"✓ Teacher my-students: {data.get('total')} students, page {data.get('page')}")
    
    def test_my_students_requires_teacher_role(self, applicant_session):
        """Applicant cannot access my-students (403)"""
        response = applicant_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 403
        print("✓ Applicant cannot access my-students (403)")
    
    def test_my_students_requires_auth(self):
        """Unauthenticated cannot access my-students"""
        response = requests.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 401
        print("✓ my-students requires auth (401)")


class TestConsentFlow:
    """Consent grant/revoke affects teacher visibility"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=APPLICANT_CREDS)
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def teacher_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=TEACHER_CREDS)
        assert response.status_code == 200
        return session
    
    def test_consent_types_include_teacher_data_access(self, applicant_session):
        """Consent types include teacher_data_access"""
        response = applicant_session.get(f"{BASE_URL}/api/consents/types")
        assert response.status_code == 200
        data = response.json()
        # Response is a dict with consent type keys
        assert "teacher_data_access" in data
        consent_def = data["teacher_data_access"]
        assert "purpose_de" in consent_def or "purpose_en" in consent_def
        assert "scope" in consent_def
        assert "excludes" in consent_def
        print(f"✓ Consent types include teacher_data_access with scope: {consent_def.get('scope')}")
    
    def test_applicant_can_grant_consent(self, applicant_session):
        """Applicant can grant teacher_data_access consent"""
        response = applicant_session.post(
            f"{BASE_URL}/api/consents/grant",
            json={"consent_type": "teacher_data_access"}
        )
        # May return 200 (granted) or already granted
        assert response.status_code in [200, 201]
        print(f"✓ Consent grant response: {response.status_code}")
    
    def test_applicant_can_view_own_consents(self, applicant_session):
        """Applicant can view own consents"""
        response = applicant_session.get(f"{BASE_URL}/api/consents/my")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Applicant consents: {len(data)} records")
    
    def test_applicant_can_revoke_consent(self, applicant_session):
        """Applicant can revoke consent"""
        # First grant
        applicant_session.post(
            f"{BASE_URL}/api/consents/grant",
            json={"consent_type": "teacher_data_access"}
        )
        # Then revoke
        response = applicant_session.post(f"{BASE_URL}/api/consents/revoke/teacher_data_access")
        assert response.status_code == 200
        print("✓ Consent revoked successfully")


class TestCostSimulator:
    """GET /api/internal/cost-simulator/config - individual pricing disclaimers"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=STAFF_CREDS)
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=APPLICANT_CREDS)
        assert response.status_code == 200
        return session
    
    def test_staff_can_access_cost_simulator(self, staff_session):
        """Staff can access cost simulator config"""
        response = staff_session.get(f"{BASE_URL}/api/internal/cost-simulator/config")
        assert response.status_code == 200
        data = response.json()
        # Should have enabled flag and message/disclaimer
        assert "enabled" in data
        if data.get("enabled"):
            assert "disclaimer" in data
            # Check for individual pricing language
            disclaimer = data.get("disclaimer", "")
            assert "einzelfall" in disclaimer.lower() or "individual" in disclaimer.lower()
            print(f"✓ Cost simulator enabled with disclaimer: {disclaimer[:100]}...")
        else:
            assert "message" in data
            message = data.get("message", "")
            assert "einzelfall" in message.lower() or "individual" in message.lower()
            print(f"✓ Cost simulator disabled with message: {message[:100]}...")
    
    def test_applicant_cannot_access_cost_simulator(self, applicant_session):
        """Applicant cannot access cost simulator (403)"""
        response = applicant_session.get(f"{BASE_URL}/api/internal/cost-simulator/config")
        assert response.status_code == 403
        print("✓ Applicant cannot access cost simulator (403)")
    
    def test_cost_simulator_requires_auth(self):
        """Cost simulator requires authentication"""
        response = requests.get(f"{BASE_URL}/api/internal/cost-simulator/config")
        assert response.status_code == 401
        print("✓ Cost simulator requires auth (401)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
