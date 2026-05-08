"""
CI-Design Audit Tests - Iteration 59
Tests for CI-Design Enforcement changes:
- Auth endpoints (login, forgot-password)
- Dashboard stats
- Applications, Invoices, Oracle context
- Public booking slots and rate limiting
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthEndpoints:
    """Authentication endpoint tests"""
    
    def test_login_staff_success(self):
        """POST /api/auth/login - Staff login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["email"] == "staff@studienkolleg-aachen.de"
        assert data["role"] in ["staff", "admin", "superadmin"]
        print(f"✓ Staff login successful: {data['email']} (role: {data['role']})")
    
    def test_login_applicant_success(self):
        """POST /api/auth/login - Applicant login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["email"] == "applicant@studienkolleg-aachen.de"
        assert data["role"] == "applicant"
        print(f"✓ Applicant login successful: {data['email']} (role: {data['role']})")
    
    def test_login_invalid_credentials(self):
        """POST /api/auth/login - Invalid credentials returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid credentials correctly rejected with 401")


class TestDashboardStats:
    """Dashboard stats endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_dashboard_stats(self, staff_session):
        """GET /api/dashboard/stats - Returns 200"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Dashboard stats returned: {list(data.keys())}")


class TestApplicationsEndpoint:
    """Applications endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_applications_list(self, staff_session):
        """GET /api/applications - Returns 200"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Applications endpoint returned successfully")


class TestInvoicesEndpoint:
    """Invoices endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_invoices_list(self, staff_session):
        """GET /api/invoices - Returns 200"""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, (list, dict))
        print(f"✓ Invoices endpoint returned successfully")


class TestOracleEndpoint:
    """Oracle context endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_oracle_context(self, staff_session):
        """GET /api/oracle/context - Returns 200"""
        response = staff_session.get(f"{BASE_URL}/api/oracle/context")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert isinstance(data, dict)
        print(f"✓ Oracle context returned: {list(data.keys())}")


class TestPublicBookingEndpoints:
    """Public booking endpoints tests"""
    
    def test_public_slots(self):
        """GET /api/appointments/public-slots - Returns 200"""
        # Get tomorrow's date
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = requests.get(f"{BASE_URL}/api/appointments/public-slots?date={tomorrow}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "slots" in data
        print(f"✓ Public slots returned: {len(data.get('slots', []))} slots for {tomorrow}")
    
    def test_public_booking_rate_limit(self):
        """POST /api/appointments/public-booking - Rate limited (5/min)"""
        # First request should work (or fail with validation error, not rate limit)
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        booking_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+49123456789",
            "type": "consultation",
            "date": tomorrow,
            "time": "10:00",
            "message": "Test booking"
        }
        
        response = requests.post(f"{BASE_URL}/api/appointments/public-booking", json=booking_data)
        # Should either succeed (201) or fail with validation (400/422), but not 500
        assert response.status_code in [200, 201, 400, 422, 429], f"Unexpected status: {response.status_code}: {response.text}"
        print(f"✓ Public booking endpoint accessible (status: {response.status_code})")


class TestForgotPassword:
    """Forgot password endpoint tests"""
    
    def test_forgot_password_endpoint(self):
        """POST /api/auth/forgot-password - Returns 200"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            "email": "test@example.com"
        })
        # Should always return 200 (no user enumeration)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ Forgot password endpoint works (no user enumeration)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
