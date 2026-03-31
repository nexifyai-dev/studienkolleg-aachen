"""W2G Platform - Backend API Tests"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealth:
    """Health check"""
    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get('status') == 'ok'
        print(f"Health: {data}")

class TestAuth:
    """Auth endpoints"""
    def test_admin_login_success(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": os.environ["TEST_ADMIN_PASSWORD"]
        })
        assert r.status_code == 200
        data = r.json()
        assert data.get('role') == 'superadmin'
        assert data.get('email') == 'admin@studienkolleg-aachen.de'
        print(f"Admin login: {data}")

    def test_login_invalid_credentials(self):
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": os.environ["TEST_INVALID_PASSWORD"]
        })
        assert r.status_code == 401
        print("Invalid creds rejected correctly")

    def test_register_applicant(self):
        import time
        email = f"test_applicant_{int(time.time())}@example.com"
        r = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": email,
            "password": os.environ["TEST_REGISTER_PASSWORD"],
            "full_name": "Test Applicant",
            "role": "applicant"
        })
        assert r.status_code == 200
        data = r.json()
        assert data.get('role') == 'applicant'
        assert data.get('email') == email
        print(f"Applicant registered: {data}")

    def test_me_unauthenticated(self):
        r = requests.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401
        print("Unauthenticated /me correctly returns 401")

class TestLeadIngest:
    """Lead ingestion"""
    def test_ingest_lead(self):
        import time
        r = requests.post(f"{BASE_URL}/api/leads/ingest", json={
            "full_name": "TEST_Lead User",
            "email": f"test_lead_{int(time.time())}@example.com",
            "phone": "+49123456789",
            "country": "Nigeria",
            "area_interest": "studienkolleg",
            "source": "website_form"
        })
        assert r.status_code == 200
        data = r.json()
        assert data.get('success') == True
        assert 'user_id' in data
        print(f"Lead ingested: {data}")

class TestWorkspaces:
    """Workspace endpoints (auth required)"""
    @pytest.fixture(autouse=True)
    def get_session(self):
        self.session = requests.Session()
        r = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": os.environ["TEST_ADMIN_PASSWORD"]
        })
        assert r.status_code == 200
        # Cookies are saved in session

    def test_list_workspaces(self):
        r = self.session.get(f"{BASE_URL}/api/workspaces")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        slugs = [w.get('slug') for w in data]
        assert 'studienkolleg' in slugs
        print(f"Workspaces: {slugs}")

class TestDashboardStats:
    """Dashboard stats (auth required)"""
    @pytest.fixture(autouse=True)
    def get_session(self):
        self.session = requests.Session()
        self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": os.environ["TEST_ADMIN_PASSWORD"]
        })

    def test_dashboard_stats(self):
        r = self.session.get(f"{BASE_URL}/api/dashboard/stats")
        assert r.status_code == 200
        data = r.json()
        assert 'total_leads' in data
        print(f"Stats: {data}")

class TestUsers:
    """Users admin endpoint"""
    @pytest.fixture(autouse=True)
    def get_session(self):
        self.session = requests.Session()
        self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": os.environ["TEST_ADMIN_PASSWORD"]
        })

    def test_list_users(self):
        r = self.session.get(f"{BASE_URL}/api/users")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify no password_hash in response
        for u in data:
            assert 'password_hash' not in u
        print(f"Users count: {len(data)}")

class TestApplications:
    """Applications endpoint"""
    @pytest.fixture(autouse=True)
    def get_session(self):
        self.session = requests.Session()
        self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": os.environ["TEST_ADMIN_PASSWORD"]
        })

    def test_list_applications(self):
        r = self.session.get(f"{BASE_URL}/api/applications")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        print(f"Applications count: {len(data)}")

class TestLogout:
    """Logout"""
    def test_logout(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": os.environ["TEST_ADMIN_PASSWORD"]
        })
        r = session.post(f"{BASE_URL}/api/auth/logout")
        assert r.status_code == 200
        data = r.json()
        assert 'message' in data
        print(f"Logout: {data}")
        # After logout, /me should return 401
        r2 = session.get(f"{BASE_URL}/api/auth/me")
        assert r2.status_code == 401
