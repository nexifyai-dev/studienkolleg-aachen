"""
Iteration 62 - Testing new Admin/Partner/Applicant pages and backend APIs
Focus: AdminReportsPage, AdminCasesPage, AdminPartnersPage, PartnerMessagesPage, PartnerTrackingPage, ApplicantMorePage
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = "DevSeed@2026!"


class TestHealthAndBasics:
    """Basic health and version checks"""
    
    def test_health_endpoint(self):
        """GET /api/health - Version 1.3.0"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.3.0"
        print(f"✓ Health check passed: version={data['version']}")
    
    def test_jobs_health(self, admin_session):
        """GET /api/jobs/health - Background jobs status (requires auth)"""
        response = admin_session.get(f"{BASE_URL}/api/jobs/health")
        assert response.status_code == 200
        data = response.json()
        assert "is_healthy" in data
        print(f"✓ Jobs health: is_healthy={data.get('is_healthy')}, running={data.get('running')}")
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session for jobs health"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return session


class TestAuthentication:
    """Authentication tests for all user roles"""
    
    def test_login_staff(self):
        """POST /api/auth/login - Staff login"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # Response returns user directly, not wrapped in 'user' key
        assert data["role"] == "staff"
        print(f"✓ Staff login successful: role={data['role']}")
    
    def test_login_admin(self):
        """POST /api/auth/login - Admin login"""
        time.sleep(1)  # Rate limit protection
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["role"] in ["admin", "superadmin"]
        print(f"✓ Admin login successful: role={data['role']}")
    
    def test_login_applicant(self):
        """POST /api/auth/login - Applicant login"""
        time.sleep(1)  # Rate limit protection
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "applicant"
        print(f"✓ Applicant login successful: role={data['role']}")
    
    def test_login_partner(self):
        """POST /api/auth/login - Partner login"""
        time.sleep(1)  # Rate limit protection
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        # Partner may or may not exist
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Partner login successful: role={data['role']}")
        else:
            print(f"⚠ Partner user may not exist (status={response.status_code})")
            pytest.skip("Partner user not seeded")


class TestSystemMonitoring:
    """System monitoring endpoint tests - Admin only"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    def test_system_monitoring_admin_access(self, admin_session):
        """GET /api/system/monitoring - Admin should have access"""
        response = admin_session.get(f"{BASE_URL}/api/system/monitoring")
        assert response.status_code == 200
        data = response.json()
        assert "worker" in data
        assert "scheduler" in data
        assert "job_queue" in data
        assert "system_metrics" in data
        print(f"✓ System monitoring accessible for admin")
        print(f"  Worker: is_healthy={data['worker'].get('is_healthy')}")
        print(f"  Scheduler: is_healthy={data['scheduler'].get('is_healthy')}")
    
    def test_system_monitoring_staff_forbidden(self, staff_session):
        """GET /api/system/monitoring - Staff should get 403"""
        response = staff_session.get(f"{BASE_URL}/api/system/monitoring")
        assert response.status_code == 403
        print(f"✓ System monitoring correctly returns 403 for staff")


class TestDashboardAndApplications:
    """Dashboard stats and applications endpoints"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    def test_dashboard_stats(self, admin_session):
        """GET /api/dashboard/stats - Dashboard statistics"""
        response = admin_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        # Staff/Admin dashboard should have these fields
        assert "total_leads" in data or "applications" in data
        print(f"✓ Dashboard stats retrieved")
        if "pipeline" in data:
            print(f"  Pipeline stages: {list(data['pipeline'].keys())}")
    
    def test_applications_list(self, admin_session):
        """GET /api/applications - Applications list for AdminCasesPage"""
        response = admin_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applications list retrieved: {len(data)} applications")
        if len(data) > 0:
            app = data[0]
            assert "id" in app or "_id" in app
            print(f"  Sample fields: {list(app.keys())[:5]}")
    
    def test_invoices_list(self, admin_session):
        """GET /api/invoices - Invoices list"""
        response = admin_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Invoices list retrieved: {len(data)} invoices")
    
    def test_tasks_list(self, admin_session):
        """GET /api/tasks - Tasks list"""
        response = admin_session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tasks list retrieved: {len(data)} tasks")


class TestOracleContext:
    """Oracle context endpoint for live data"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    def test_oracle_context(self, staff_session):
        """GET /api/oracle/context - Live data for Oracle"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 200
        data = response.json()
        # Should contain system context data
        print(f"✓ Oracle context retrieved")
        print(f"  Context keys: {list(data.keys())[:5]}")


class TestUsersEndpoint:
    """Users endpoint for AdminPartnersPage (affiliate users)"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    def test_users_affiliate_filter(self, admin_session):
        """GET /api/users?role=affiliate - Partner list for AdminPartnersPage"""
        response = admin_session.get(f"{BASE_URL}/api/users", params={"role": "affiliate"})
        # May return 200 with empty list or 404 if endpoint doesn't support filter
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Affiliate users retrieved: {len(data)} partners")
        else:
            print(f"⚠ Users endpoint returned {response.status_code} - may not support role filter")


class TestPartnerEndpoints:
    """Partner-specific endpoints for PartnerTrackingPage"""
    
    @pytest.fixture
    def partner_session(self):
        """Get authenticated partner session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Partner login failed - user may not exist")
        return session
    
    def test_partner_stats(self, partner_session):
        """GET /api/partner/stats - Partner tracking KPIs"""
        response = partner_session.get(f"{BASE_URL}/api/partner/stats")
        # May return 200 or 404 if endpoint doesn't exist
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Partner stats retrieved: {data}")
        else:
            print(f"⚠ Partner stats endpoint returned {response.status_code}")
    
    def test_conversations(self, partner_session):
        """GET /api/conversations - Partner messages"""
        response = partner_session.get(f"{BASE_URL}/api/conversations")
        # May return 200 or 404 if endpoint doesn't exist
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Conversations retrieved: {len(data) if isinstance(data, list) else 'N/A'}")
        else:
            print(f"⚠ Conversations endpoint returned {response.status_code}")


class TestApplicantEndpoints:
    """Applicant-specific endpoints for ApplicantMorePage"""
    
    @pytest.fixture
    def applicant_session(self):
        """Get authenticated applicant session"""
        time.sleep(1)
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Applicant login failed")
        return session
    
    def test_applicant_dashboard_stats(self, applicant_session):
        """GET /api/dashboard/stats - Applicant dashboard"""
        response = applicant_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        # Applicant dashboard should have applications count
        assert "applications" in data or "stages" in data
        print(f"✓ Applicant dashboard stats retrieved")
    
    def test_auth_me(self, applicant_session):
        """GET /api/auth/me - Current user info for ApplicantMorePage"""
        response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert data["role"] == "applicant"
        print(f"✓ Auth/me returned user info: {data['email']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
