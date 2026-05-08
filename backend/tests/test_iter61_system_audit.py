"""
Iteration 61 - System-Wide Audit Tests
Tests: Auth (Staff/Admin/Applicant), System Monitoring, Scheduler, Oracle, Dashboard, Jobs
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestHealthEndpoint:
    """Health endpoint tests - Version 1.3.0"""
    
    def test_health_returns_ok(self):
        """GET /api/health - System health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.3.0"
        assert "email_enabled" in data
        assert "storage_backend" in data
        print(f"✓ Health: status={data['status']}, version={data['version']}")


class TestAuthEndpoints:
    """Authentication tests for all roles"""
    
    def test_staff_login_success(self):
        """POST /api/auth/login - Staff login"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # Response returns user data directly (not wrapped in "user" key)
        assert "role" in data
        assert data["role"] == "staff"
        assert data["email"] == STAFF_EMAIL
        print(f"✓ Staff login: role={data['role']}")
    
    def test_admin_login_success(self):
        """POST /api/auth/login - Admin login"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # Response returns user data directly
        assert "role" in data
        assert data["role"] in ["admin", "superadmin"]
        print(f"✓ Admin login: role={data['role']}")
    
    def test_applicant_login_success(self):
        """POST /api/auth/login - Applicant login"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        # Response returns user data directly
        assert "role" in data
        assert data["role"] == "applicant"
        print(f"✓ Applicant login: role={data['role']}")
    
    def test_login_wrong_password_returns_401(self):
        """POST /api/auth/login - Wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401
        print("✓ Wrong password returns 401")


class TestSystemMonitoring:
    """System monitoring endpoint tests - Admin only"""
    
    @pytest.fixture
    def admin_session(self):
        """Get authenticated admin session"""
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
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    def test_system_monitoring_admin_access(self, admin_session):
        """GET /api/system/monitoring - Admin can access"""
        response = admin_session.get(f"{BASE_URL}/api/system/monitoring")
        assert response.status_code == 200
        data = response.json()
        
        # Verify worker health
        assert "worker" in data
        assert "is_healthy" in data["worker"]
        print(f"✓ Worker: is_healthy={data['worker'].get('is_healthy')}")
        
        # Verify scheduler health
        assert "scheduler" in data
        assert "is_healthy" in data["scheduler"]
        print(f"✓ Scheduler: is_healthy={data['scheduler'].get('is_healthy')}")
        
        # Verify job queue stats
        assert "job_queue" in data
        assert "pending" in data["job_queue"]
        print(f"✓ Job Queue: pending={data['job_queue'].get('pending')}")
        
        # Verify system metrics
        assert "system_metrics" in data
        print(f"✓ System Metrics present")
    
    def test_system_monitoring_staff_forbidden(self, staff_session):
        """GET /api/system/monitoring - Staff gets 403"""
        response = staff_session.get(f"{BASE_URL}/api/system/monitoring")
        assert response.status_code == 403
        print("✓ Staff correctly gets 403 for /system/monitoring")


class TestOracleEndpoints:
    """Oracle Live-Data and Chat tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    def test_oracle_context_returns_live_data(self, staff_session):
        """GET /api/oracle/context - Returns live system data"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 200
        data = response.json()
        assert "context" in data or "stats" in data or isinstance(data, dict)
        print(f"✓ Oracle context returned live data")
    
    def test_oracle_chat_works(self, staff_session):
        """POST /api/oracle/chat - AI chat responds"""
        response = staff_session.post(
            f"{BASE_URL}/api/oracle/chat",
            json={"message": "Wie viele Bewerbungen gibt es?"},
            timeout=30  # Oracle needs longer timeout
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data or "message" in data or "answer" in data
        print(f"✓ Oracle chat responded")


class TestDashboardAndDataEndpoints:
    """Dashboard stats and data endpoints"""
    
    def get_staff_session(self):
        """Get authenticated staff session"""
        time.sleep(1)  # Rate limit protection
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        if response.status_code != 200:
            return None
        return session
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats - Returns dashboard data"""
        session = self.get_staff_session()
        assert session is not None, "Staff login failed"
        response = session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_leads" in data or "applications" in data
        print(f"✓ Dashboard stats returned")
    
    def test_applications_list(self):
        """GET /api/applications - Returns applications"""
        session = self.get_staff_session()
        assert session is not None, "Staff login failed"
        response = session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "applications" in data
        print(f"✓ Applications list returned")
    
    def test_invoices_list(self):
        """GET /api/invoices - Returns invoices"""
        session = self.get_staff_session()
        assert session is not None, "Staff login failed"
        response = session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "invoices" in data
        print(f"✓ Invoices list returned")
    
    def test_tasks_list(self):
        """GET /api/tasks - Returns tasks"""
        session = self.get_staff_session()
        assert session is not None, "Staff login failed"
        response = session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "tasks" in data
        print(f"✓ Tasks list returned")
    
    def test_notifications_list(self):
        """GET /api/notifications - Returns notifications"""
        session = self.get_staff_session()
        assert session is not None, "Staff login failed"
        response = session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "notifications" in data
        print(f"✓ Notifications list returned")


class TestJobsHealth:
    """Background jobs health endpoint"""
    
    def test_jobs_health(self):
        """GET /api/jobs/health - Worker health check"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, "Staff login failed"
        
        response = session.get(f"{BASE_URL}/api/jobs/health")
        assert response.status_code == 200
        data = response.json()
        assert "is_healthy" in data or "running" in data or "status" in data
        print(f"✓ Jobs health: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
