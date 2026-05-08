"""
Iteration 57 - Rate Limiting Tests
Tests for slowapi rate limits on auth endpoints:
- Login: 10/minute
- Register: 5/minute  
- Forgot-Password: 3/minute
- Reset-Password: 5/minute
- Public-Booking: 5/minute

IMPORTANT: Use DIFFERENT email addresses to avoid brute-force protection (5 attempts per IP:email)
"""
import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def session():
    """Fresh session for each test"""
    s = requests.Session()
    s.headers.update({'Content-Type': 'application/json'})
    return s


class TestRateLimiting:
    """Rate limiting tests - use unique emails to avoid brute-force lockout"""
    
    def test_login_rate_limit_triggers_after_10_attempts(self, session):
        """Login endpoint should return 429 after 10 requests/minute"""
        # Use unique emails for each request to avoid brute-force protection
        responses = []
        for i in range(12):
            unique_email = f"ratelimit_test_{uuid.uuid4().hex[:8]}@test.de"
            resp = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": unique_email,
                "password": "wrongpassword123"
            })
            responses.append(resp.status_code)
            print(f"Login attempt {i+1}: {resp.status_code}")
        
        # First 10 should be 401 (invalid credentials), after that 429 (rate limited)
        assert 429 in responses, f"Expected 429 in responses after 10 attempts, got: {responses}"
        # Count how many 429s we got
        rate_limited = responses.count(429)
        print(f"Rate limited responses: {rate_limited}")
        assert rate_limited >= 1, "Should have at least 1 rate-limited response"
    
    def test_register_rate_limit_triggers_after_5_attempts(self, session):
        """Register endpoint should return 429 after 5 requests/minute"""
        responses = []
        for i in range(7):
            unique_email = f"register_test_{uuid.uuid4().hex[:8]}@test.de"
            resp = session.post(f"{BASE_URL}/api/auth/register", json={
                "email": unique_email,
                "password": "TestPassword123!",
                "full_name": f"Test User {i}"
            })
            responses.append(resp.status_code)
            print(f"Register attempt {i+1}: {resp.status_code}")
        
        # After 5 attempts, should get 429
        assert 429 in responses, f"Expected 429 in responses after 5 attempts, got: {responses}"
    
    def test_forgot_password_rate_limit_triggers_after_3_attempts(self, session):
        """Forgot-password endpoint should return 429 after 3 requests/minute"""
        responses = []
        for i in range(5):
            unique_email = f"forgot_test_{uuid.uuid4().hex[:8]}@test.de"
            resp = session.post(f"{BASE_URL}/api/auth/forgot-password", json={
                "email": unique_email
            })
            responses.append(resp.status_code)
            print(f"Forgot-password attempt {i+1}: {resp.status_code}")
        
        # After 3 attempts, should get 429
        assert 429 in responses, f"Expected 429 in responses after 3 attempts, got: {responses}"
    
    def test_reset_password_rate_limit_triggers_after_5_attempts(self, session):
        """Reset-password endpoint should return 429 after 5 requests/minute"""
        responses = []
        for i in range(7):
            resp = session.post(f"{BASE_URL}/api/auth/reset-password", json={
                "token": f"invalid_token_{uuid.uuid4().hex}",
                "new_password": "NewPassword123!"
            })
            responses.append(resp.status_code)
            print(f"Reset-password attempt {i+1}: {resp.status_code}")
        
        # After 5 attempts, should get 429
        assert 429 in responses, f"Expected 429 in responses after 5 attempts, got: {responses}"
    
    def test_public_booking_rate_limit_triggers_after_5_attempts(self, session):
        """Public-booking endpoint should return 429 after 5 requests/minute"""
        responses = []
        for i in range(7):
            unique_email = f"booking_test_{uuid.uuid4().hex[:8]}@test.de"
            resp = session.post(f"{BASE_URL}/api/appointments/public-booking", json={
                "name": f"Test User {i}",
                "email": unique_email,
                "date": "2026-02-15",
                "time": "10:00",
                "type": "consultation"
            })
            responses.append(resp.status_code)
            print(f"Public-booking attempt {i+1}: {resp.status_code}")
        
        # After 5 attempts, should get 429
        assert 429 in responses, f"Expected 429 in responses after 5 attempts, got: {responses}"


class TestAuthEndpointsBasic:
    """Basic auth endpoint tests"""
    
    def test_login_valid_credentials_staff(self, session):
        """Staff login should work with correct credentials"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert resp.status_code == 200, f"Staff login failed: {resp.text}"
        data = resp.json()
        assert data.get("role") == "staff"
        assert "id" in data
    
    def test_login_valid_credentials_admin(self, session):
        """Admin login should work with correct credentials"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": "Admin@2026!"
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        data = resp.json()
        assert data.get("role") == "admin"
    
    def test_login_invalid_credentials(self, session):
        """Invalid credentials should return 401"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.de",
            "password": "wrongpassword"
        })
        assert resp.status_code == 401


class TestPortalAPIs:
    """Test portal-specific APIs for different roles"""
    
    @pytest.fixture
    def staff_session(self, session):
        """Authenticated staff session"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        if resp.status_code != 200:
            pytest.skip("Staff login failed")
        return session
    
    @pytest.fixture
    def admin_session(self, session):
        """Authenticated admin session"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": "Admin@2026!"
        })
        if resp.status_code != 200:
            pytest.skip("Admin login failed")
        return session
    
    @pytest.fixture
    def partner_session(self, session):
        """Authenticated partner session"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "partner@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        if resp.status_code != 200:
            pytest.skip("Partner login failed")
        return session
    
    @pytest.fixture
    def teacher_session(self, session):
        """Authenticated teacher session"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teacher@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        if resp.status_code != 200:
            pytest.skip("Teacher login failed")
        return session
    
    @pytest.fixture
    def applicant_session(self, session):
        """Authenticated applicant session"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        if resp.status_code != 200:
            pytest.skip("Applicant login failed")
        return session
    
    def test_staff_dashboard_api(self, staff_session):
        """Staff dashboard API should return KPIs"""
        resp = staff_session.get(f"{BASE_URL}/api/dashboard/staff")
        assert resp.status_code == 200, f"Staff dashboard failed: {resp.text}"
        data = resp.json()
        # Should have KPI data
        assert isinstance(data, dict)
    
    def test_admin_jobs_stats_api(self, admin_session):
        """Admin jobs stats API should return job statistics"""
        resp = admin_session.get(f"{BASE_URL}/api/jobs/stats")
        assert resp.status_code == 200, f"Jobs stats failed: {resp.text}"
        data = resp.json()
        # Should have stats fields
        assert "queued" in data or "running" in data or "succeeded" in data
    
    def test_admin_jobs_health_api(self, admin_session):
        """Admin jobs health API should return worker health"""
        resp = admin_session.get(f"{BASE_URL}/api/jobs/health")
        assert resp.status_code == 200, f"Jobs health failed: {resp.text}"
        data = resp.json()
        assert "is_healthy" in data
    
    def test_partner_dashboard_api(self, partner_session):
        """Partner dashboard API should return data"""
        resp = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert resp.status_code == 200, f"Partner dashboard failed: {resp.text}"
    
    def test_teacher_students_api(self, teacher_session):
        """Teacher students API should return student list"""
        resp = teacher_session.get(f"{BASE_URL}/api/teacher/my-students")
        assert resp.status_code == 200, f"Teacher students failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)
    
    def test_applicant_invoices_api(self, applicant_session):
        """Applicant invoices API should return invoice list"""
        resp = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert resp.status_code == 200, f"Applicant invoices failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)
    
    def test_applicant_documents_api(self, applicant_session):
        """Applicant documents API should return document list"""
        resp = applicant_session.get(f"{BASE_URL}/api/documents/my")
        assert resp.status_code == 200, f"Applicant documents failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)


class TestPublicEndpoints:
    """Test public endpoints (no auth required)"""
    
    def test_public_slots_api(self, session):
        """Public slots API should return available time slots"""
        resp = session.get(f"{BASE_URL}/api/appointments/public-slots")
        assert resp.status_code == 200, f"Public slots failed: {resp.text}"
        data = resp.json()
        assert "slots" in data
        assert "date" in data
