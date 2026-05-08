"""
Iteration 70 - Dashboard Redesign with shadcn/ui Components Testing
Tests for:
- Dashboard APIs (stats, applications, tasks, invoices)
- Staff login functionality
- Dashboard data integrity
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestStaffLogin:
    """Staff authentication tests"""
    
    def test_staff_login_success(self):
        """Test staff login with correct credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["email"] == "staff@studienkolleg-aachen.de"
        assert data["role"] == "staff"
        print(f"PASS: Staff login successful - User: {data['full_name']}")
    
    def test_staff_login_invalid_password(self):
        """Test staff login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401
        print("PASS: Invalid password rejected with 401")


class TestDashboardStats:
    """Dashboard statistics API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookies"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert login_resp.status_code == 200
    
    def test_dashboard_stats_endpoint(self):
        """Test GET /api/dashboard/stats returns valid data"""
        response = self.session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "total_leads" in data
        assert "open_leads" in data
        assert "open_tasks" in data
        assert "pending_documents" in data
        assert "pipeline" in data
        assert "recent_activity" in data
        
        # Verify pipeline stages
        pipeline = data["pipeline"]
        expected_stages = ["lead_new", "in_review", "pending_docs", "interview_scheduled", 
                          "conditional_offer", "offer_sent", "enrolled"]
        for stage in expected_stages:
            assert stage in pipeline, f"Missing pipeline stage: {stage}"
        
        print(f"PASS: Dashboard stats - Total leads: {data['total_leads']}, Open tasks: {data['open_tasks']}")
    
    def test_dashboard_stats_unauthorized(self):
        """Test dashboard stats requires authentication"""
        response = requests.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 401
        print("PASS: Dashboard stats requires authentication")


class TestApplicationsAPI:
    """Applications API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookies"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert login_resp.status_code == 200
    
    def test_get_applications(self):
        """Test GET /api/applications returns list of applications"""
        response = self.session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0, "Expected at least one application"
        
        # Verify application structure
        app = data[0]
        assert "id" in app
        assert "applicant_id" in app
        assert "current_stage" in app
        assert "applicant" in app
        
        # Verify applicant data
        applicant = app["applicant"]
        assert "full_name" in applicant
        assert "email" in applicant
        
        print(f"PASS: Applications API - Found {len(data)} applications")
    
    def test_applications_unauthorized(self):
        """Test applications requires authentication"""
        response = requests.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 401
        print("PASS: Applications API requires authentication")


class TestTasksAPI:
    """Tasks API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookies"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert login_resp.status_code == 200
    
    def test_get_tasks(self):
        """Test GET /api/tasks returns list of tasks"""
        response = self.session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if len(data) > 0:
            task = data[0]
            assert "id" in task
            assert "title" in task
            assert "status" in task
            assert "priority" in task
            print(f"PASS: Tasks API - Found {len(data)} tasks")
        else:
            print("PASS: Tasks API - No tasks found (empty list)")
    
    def test_tasks_unauthorized(self):
        """Test tasks requires authentication"""
        response = requests.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 401
        print("PASS: Tasks API requires authentication")


class TestInvoicesAPI:
    """Invoices API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get session cookies"""
        self.session = requests.Session()
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert login_resp.status_code == 200
    
    def test_get_invoices(self):
        """Test GET /api/invoices returns list of invoices"""
        response = self.session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if len(data) > 0:
            invoice = data[0]
            assert "invoice_number" in invoice or "id" in invoice
            assert "amount" in invoice
            assert "status" in invoice
            print(f"PASS: Invoices API - Found {len(data)} invoices")
        else:
            print("PASS: Invoices API - No invoices found (empty list)")
    
    def test_invoices_unauthorized(self):
        """Test invoices requires authentication"""
        response = requests.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 401
        print("PASS: Invoices API requires authentication")


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_check(self):
        """Test /api/health returns OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print(f"PASS: Health check - Service: {data.get('service', 'N/A')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
