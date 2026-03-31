"""
Phase 3.7c Backend Tests - Teacher Dashboard, Consent UI, AI Model Registry, 4 Role Logins

Tests:
- All 4 role logins (admin, staff, teacher, applicant)
- Teacher API: GET /api/teacher/my-students
- Consent API: POST /api/consents/grant, GET /api/consents/my
- AI Model Registry: GET /api/ai/model-registry (deepseek provider)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
CREDENTIALS = {
    "admin": {"email": "admin@studienkolleg-aachen.de", "password": os.environ["TEST_ADMIN_PASSWORD"]},
    "staff": {"email": "staff@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]},
    "teacher": {"email": "teacher@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]},
    "applicant": {"email": "applicant@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]},
}


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "email_enabled" in data
        print(f"✓ Health check passed: {data}")


class TestAllRoleLogins:
    """Test all 4 seeded role accounts can login"""
    
    def test_admin_login(self):
        """Admin login (superadmin role)"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["admin"])
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data.get("role") == "superadmin", f"Expected superadmin role, got {data.get('role')}"
        assert data.get("email") == CREDENTIALS["admin"]["email"]
        print(f"✓ Admin login successful: role={data.get('role')}")
    
    def test_staff_login(self):
        """Staff login (staff role)"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert data.get("role") == "staff", f"Expected staff role, got {data.get('role')}"
        assert data.get("email") == CREDENTIALS["staff"]["email"]
        print(f"✓ Staff login successful: role={data.get('role')}")
    
    def test_teacher_login(self):
        """Teacher login (teacher role)"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["teacher"])
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert data.get("role") == "teacher", f"Expected teacher role, got {data.get('role')}"
        assert data.get("email") == CREDENTIALS["teacher"]["email"]
        print(f"✓ Teacher login successful: role={data.get('role')}")
    
    def test_applicant_login(self):
        """Applicant login (applicant role)"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["applicant"])
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data.get("role") == "applicant", f"Expected applicant role, got {data.get('role')}"
        assert data.get("email") == CREDENTIALS["applicant"]["email"]
        print(f"✓ Applicant login successful: role={data.get('role')}")
    
    def test_invalid_login_returns_401(self):
        """Invalid credentials return 401"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@example.com",
            "password": os.environ["TEST_INVALID_PASSWORD"]
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid login correctly returns 401")


class TestTeacherAPI:
    """Teacher-specific API tests"""
    
    @pytest.fixture
    def teacher_session(self):
        """Get authenticated teacher session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["teacher"])
        if response.status_code != 200:
            pytest.skip("Teacher login failed")
        return session
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    @pytest.fixture
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["applicant"])
        if response.status_code != 200:
            pytest.skip("Applicant login failed")
        return session
    
    def test_teacher_my_students_endpoint(self, teacher_session):
        """Teacher can access /api/teacher/my-students"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "students" in data, "Response should contain 'students' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "page" in data, "Response should contain 'page' key"
        print(f"✓ Teacher my-students endpoint works: {len(data['students'])} students, total={data['total']}")
    
    def test_teacher_my_students_requires_auth(self):
        """Teacher endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ Teacher endpoint correctly requires authentication")
    
    def test_applicant_cannot_access_teacher_endpoint(self, applicant_session):
        """Applicant cannot access teacher endpoints (403)"""
        response = applicant_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 403, f"Expected 403 for applicant, got {response.status_code}"
        print("✓ Applicant correctly denied access to teacher endpoint")
    
    def test_teacher_assignments_endpoint(self, teacher_session):
        """Teacher can list own assignments"""
        response = teacher_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "assignments" in data, "Response should contain 'assignments' key"
        print(f"✓ Teacher assignments endpoint works: {len(data['assignments'])} assignments")
    
    def test_staff_can_list_all_assignments(self, staff_session):
        """Staff can list all assignments"""
        response = staff_session.get(f"{BASE_URL}/api/teacher/assignments")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "assignments" in data
        print(f"✓ Staff can list all assignments: {len(data['assignments'])} assignments")


class TestConsentAPI:
    """Consent management API tests"""
    
    @pytest.fixture
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["applicant"])
        if response.status_code != 200:
            pytest.skip("Applicant login failed")
        return session
    
    @pytest.fixture
    def teacher_session(self):
        """Get authenticated teacher session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["teacher"])
        if response.status_code != 200:
            pytest.skip("Teacher login failed")
        return session
    
    def test_consent_types_endpoint(self):
        """GET /api/consents/types returns consent definitions"""
        response = requests.get(f"{BASE_URL}/api/consents/types")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "teacher_data_access" in data, "Should contain teacher_data_access consent type"
        consent_def = data["teacher_data_access"]
        assert "purpose_de" in consent_def, "Should have German purpose"
        assert "purpose_en" in consent_def, "Should have English purpose"
        assert "scope" in consent_def, "Should have scope"
        assert "excludes" in consent_def, "Should have excludes"
        print(f"✓ Consent types endpoint works: {list(data.keys())}")
    
    def test_applicant_grant_consent(self, applicant_session):
        """Applicant can grant consent"""
        response = applicant_session.post(f"{BASE_URL}/api/consents/grant", json={
            "consent_type": "teacher_data_access",
            "version": "1.0",
            "granted": True
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "ok", f"Expected status ok, got {data}"
        assert data.get("consent_type") == "teacher_data_access"
        assert data.get("granted") == True
        print(f"✓ Applicant granted consent successfully: {data}")
    
    def test_applicant_get_my_consents(self, applicant_session):
        """Applicant can view own consents"""
        response = applicant_session.get(f"{BASE_URL}/api/consents/my")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Applicant can view consents: {len(data)} consent records")
        # Verify consent structure if any exist
        if data:
            consent = data[0]
            assert "consent_type" in consent
            assert "granted" in consent
            print(f"  Latest consent: type={consent.get('consent_type')}, granted={consent.get('granted')}")
    
    def test_applicant_revoke_consent(self, applicant_session):
        """Applicant can revoke consent"""
        # First grant consent
        applicant_session.post(f"{BASE_URL}/api/consents/grant", json={
            "consent_type": "teacher_data_access",
            "version": "1.0",
            "granted": True
        })
        # Then revoke
        response = applicant_session.post(f"{BASE_URL}/api/consents/revoke/teacher_data_access")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "revoked"
        print(f"✓ Applicant revoked consent successfully: {data}")
    
    def test_consent_my_requires_auth(self):
        """GET /api/consents/my requires authentication"""
        response = requests.get(f"{BASE_URL}/api/consents/my")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ Consent my endpoint correctly requires authentication")


class TestAIModelRegistry:
    """AI Model Registry tests (deepseek provider)"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    @pytest.fixture
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["applicant"])
        if response.status_code != 200:
            pytest.skip("Applicant login failed")
        return session
    
    def test_ai_model_registry_staff_access(self, staff_session):
        """Staff can access AI model registry"""
        response = staff_session.get(f"{BASE_URL}/api/ai/model-registry")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify deepseek provider
        assert data.get("provider") == "deepseek", f"Expected deepseek provider, got {data.get('provider')}"
        assert "enabled" in data, "Should have enabled field"
        assert "models" in data, "Should have models field"
        
        # Verify 4 task-based models
        models = data.get("models", {})
        expected_tasks = ["screening", "classification", "summary", "suggestion"]
        for task in expected_tasks:
            assert task in models, f"Missing task model: {task}"
            assert "model" in models[task], f"Task {task} should have model field"
            assert "purpose" in models[task], f"Task {task} should have purpose field"
            assert "fallback" in models[task], f"Task {task} should have fallback field"
        
        print(f"✓ AI Model Registry works: provider={data['provider']}, enabled={data['enabled']}")
        print(f"  Models: {list(models.keys())}")
        for task, config in models.items():
            print(f"    {task}: {config['model']}")
    
    def test_ai_model_registry_requires_staff_role(self, applicant_session):
        """Applicant cannot access AI model registry (403)"""
        response = applicant_session.get(f"{BASE_URL}/api/ai/model-registry")
        assert response.status_code == 403, f"Expected 403 for applicant, got {response.status_code}"
        print("✓ AI Model Registry correctly requires staff role")
    
    def test_ai_model_registry_requires_auth(self):
        """AI model registry requires authentication"""
        response = requests.get(f"{BASE_URL}/api/ai/model-registry")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print("✓ AI Model Registry correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
