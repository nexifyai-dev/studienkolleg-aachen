"""
Test Appointments API - Iteration 91
Tests for FullCalendar integration and appointment booking flow.

Endpoints tested:
- GET /api/appointments - List appointments for logged-in user
- POST /api/appointments - Create new appointment
- GET /api/appointments/available-slots - Get available time slots
- DELETE /api/appointments/{id} - Cancel appointment
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

# Credentials from environment
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = os.environ.get("SEED_DEV_PASSWORD", "DevSeed@2026!")
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = os.environ.get("SEED_DEV_PASSWORD", "DevSeed@2026!")

BASE_URL = os.environ.get("APP_URL", "https://invoice-fix-31.preview.emergentagent.com").rstrip('/')


class TestAppointmentsAPI:
    """Test appointments CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login as applicant"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as applicant
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.applicant_token = login_resp.cookies.get("access_token")
        yield
        # Cleanup handled per test
    
    def test_list_appointments(self):
        """GET /api/appointments - should return list of appointments"""
        resp = self.session.get(f"{BASE_URL}/api/appointments")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ GET /api/appointments returned {len(data)} appointments")
    
    def test_available_slots_with_date(self):
        """GET /api/appointments/available-slots?date=YYYY-MM-DD - should return slots"""
        # Use tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        resp = self.session.get(f"{BASE_URL}/api/appointments/available-slots?date={tomorrow}")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "date" in data, "Response should have 'date' field"
        assert "slots" in data, "Response should have 'slots' field"
        assert isinstance(data["slots"], list), "'slots' should be a list"
        assert data["date"] == tomorrow, f"Date should match: expected {tomorrow}, got {data['date']}"
        
        # Slots should be time strings like "09:00", "09:30", etc.
        if data["slots"]:
            assert all(":" in s for s in data["slots"]), "Slots should be time strings"
        
        print(f"✓ GET /api/appointments/available-slots returned {len(data['slots'])} slots for {tomorrow}")
    
    def test_available_slots_without_date(self):
        """GET /api/appointments/available-slots - should default to tomorrow"""
        resp = self.session.get(f"{BASE_URL}/api/appointments/available-slots")
        
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "date" in data, "Response should have 'date' field"
        assert "slots" in data, "Response should have 'slots' field"
        
        print(f"✓ GET /api/appointments/available-slots (no date) returned slots for {data['date']}")
    
    def test_create_appointment(self):
        """POST /api/appointments - should create new appointment"""
        # Use a date 7 days from now to avoid conflicts
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        payload = {
            "title": "TEST_Beratung - Terminanfrage",
            "type": "consultation",
            "date": future_date,
            "time": "14:00",
            "description": "Test appointment from pytest",
            "location": "Online (Zoom)"
        }
        
        resp = self.session.post(f"{BASE_URL}/api/appointments", json=payload)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "id" in data, "Response should have 'id' field"
        assert data["title"] == payload["title"], "Title should match"
        assert data["type"] == payload["type"], "Type should match"
        assert data["date"] == payload["date"], "Date should match"
        assert data["time"] == payload["time"], "Time should match"
        assert data["status"] == "confirmed", "Status should be 'confirmed'"
        
        # Store for cleanup
        self.created_apt_id = data["id"]
        
        print(f"✓ POST /api/appointments created appointment {data['id']}")
        
        # Verify by GET
        list_resp = self.session.get(f"{BASE_URL}/api/appointments")
        assert list_resp.status_code == 200
        appointments = list_resp.json()
        found = any(a["id"] == data["id"] for a in appointments)
        assert found, "Created appointment should appear in list"
        
        print(f"✓ Created appointment verified in GET /api/appointments")
        
        # Cleanup - cancel the appointment
        del_resp = self.session.delete(f"{BASE_URL}/api/appointments/{data['id']}")
        assert del_resp.status_code == 200, f"Cleanup failed: {del_resp.text}"
        print(f"✓ Cleanup: appointment {data['id']} cancelled")
    
    def test_cancel_appointment(self):
        """DELETE /api/appointments/{id} - should cancel appointment"""
        # First create an appointment
        future_date = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")
        
        create_resp = self.session.post(f"{BASE_URL}/api/appointments", json={
            "title": "TEST_Cancel Test",
            "type": "consultation",
            "date": future_date,
            "time": "15:00"
        })
        assert create_resp.status_code == 200
        apt_id = create_resp.json()["id"]
        
        # Cancel it
        del_resp = self.session.delete(f"{BASE_URL}/api/appointments/{apt_id}")
        assert del_resp.status_code == 200, f"Expected 200, got {del_resp.status_code}: {del_resp.text}"
        
        data = del_resp.json()
        assert data["status"] == "cancelled", "Status should be 'cancelled'"
        
        print(f"✓ DELETE /api/appointments/{apt_id} cancelled appointment")
    
    def test_appointment_types(self):
        """Test creating appointments with different types"""
        types = ["consultation", "course", "exam", "interview", "other"]
        future_date = (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d")
        
        for apt_type in types:
            resp = self.session.post(f"{BASE_URL}/api/appointments", json={
                "title": f"TEST_{apt_type}",
                "type": apt_type,
                "date": future_date,
                "time": "10:00"
            })
            assert resp.status_code == 200, f"Failed for type '{apt_type}': {resp.text}"
            
            data = resp.json()
            assert data["type"] == apt_type
            
            # Cleanup
            self.session.delete(f"{BASE_URL}/api/appointments/{data['id']}")
        
        print(f"✓ All appointment types work: {types}")


class TestOpenRouterProvider:
    """Test OpenRouter provider configuration (no actual API calls)"""
    
    def test_openrouter_env_configured(self):
        """Verify OPENROUTER_API_KEY is set in environment"""
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        assert api_key, "OPENROUTER_API_KEY should be set"
        assert api_key.startswith("sk-or-"), "OPENROUTER_API_KEY should start with 'sk-or-'"
        print(f"✓ OPENROUTER_API_KEY is configured (starts with sk-or-...)")
    
    def test_openrouter_model_configured(self):
        """Verify OPENROUTER_MODEL is set"""
        model = os.environ.get("OPENROUTER_MODEL", "")
        assert model, "OPENROUTER_MODEL should be set"
        assert "minimax" in model.lower(), "Model should be minimax variant"
        print(f"✓ OPENROUTER_MODEL is configured: {model}")


class TestStaffAppointments:
    """Test appointments from staff perspective"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and login as staff"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        yield
    
    def test_staff_list_appointments(self):
        """Staff should see all appointments"""
        resp = self.session.get(f"{BASE_URL}/api/appointments")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"✓ Staff GET /api/appointments returned {len(data)} appointments")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
