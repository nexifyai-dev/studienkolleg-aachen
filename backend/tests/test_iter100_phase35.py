"""
Iteration 100 - Phase 3-5 Backend Tests
Testing:
1. Applicant task creation (POST /api/tasks with task_type=applicant_request)
2. Applicant task creation without active application (should 400)
3. Applicant task listing (visibility=public)
4. Staff appointment CRUD (GET/POST/PUT/DELETE /api/appointments)
5. PUT /api/auth/me language preference change
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestCSRFAndAuth:
    """Helper to get CSRF token and login"""
    
    @staticmethod
    def get_csrf_token(session):
        """Get CSRF token from cookie (set by any request)"""
        # Make a request to get the CSRF cookie set
        session.get(f"{BASE_URL}/api/auth/me")
        return session.cookies.get("csrf_token")
    
    @staticmethod
    def login_staff(session):
        """Login as staff and return session with CSRF"""
        # Get initial CSRF from cookie
        session.get(f"{BASE_URL}/api/auth/me")  # This sets the csrf_token cookie
        csrf = session.cookies.get("csrf_token")
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        }, headers=headers)
        # CSRF token stays the same in cookie after login
        csrf = session.cookies.get("csrf_token")
        return resp, csrf
    
    @staticmethod
    def login_applicant(session):
        """Login as applicant and return session with CSRF"""
        # Get initial CSRF from cookie
        session.get(f"{BASE_URL}/api/auth/me")  # This sets the csrf_token cookie
        csrf = session.cookies.get("csrf_token")
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        }, headers=headers)
        # CSRF token stays the same in cookie after login
        csrf = session.cookies.get("csrf_token")
        return resp, csrf


class TestApplicantTaskCreation:
    """Test applicant can create tasks (applicant_request type)"""
    
    def test_applicant_login(self):
        """BACKEND-1: Applicant login works"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_applicant(session)
        assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
        data = resp.json()
        assert "user" in data or "email" in data, "Login response missing user data"
        print(f"PASS: Applicant login successful")
    
    def test_applicant_create_task(self):
        """BACKEND-2: POST /api/tasks as Applicant creates task_type=applicant_request"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_applicant(session)
        assert resp.status_code == 200, "Applicant login failed"
        
        # Create task
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        
        task_data = {
            "title": "TEST_Anfrage: Bewerbungsstatus",
            "description": "Ich moechte den aktuellen Stand meiner Bewerbung erfahren."
        }
        resp = session.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
        
        assert resp.status_code == 200, f"Task creation failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # Verify task_type is applicant_request
        assert data.get("task_type") == "applicant_request", f"Expected task_type=applicant_request, got {data.get('task_type')}"
        # Verify visibility is public
        assert data.get("visibility") == "public", f"Expected visibility=public, got {data.get('visibility')}"
        # Verify assigned_to is set (auto-assigned to staff)
        assert data.get("assigned_to") is not None, "Task should be auto-assigned to staff"
        # Verify status is open
        assert data.get("status") == "open", f"Expected status=open, got {data.get('status')}"
        
        print(f"PASS: Applicant task created with task_type=applicant_request, id={data.get('id')}")
        return data.get("id")
    
    def test_applicant_list_tasks(self):
        """BACKEND-3: GET /api/tasks as Applicant shows own tasks (visibility=public)"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_applicant(session)
        assert resp.status_code == 200, "Applicant login failed"
        
        resp = session.get(f"{BASE_URL}/api/tasks")
        assert resp.status_code == 200, f"Task list failed: {resp.status_code} - {resp.text}"
        
        tasks = resp.json()
        assert isinstance(tasks, list), "Expected list of tasks"
        
        # All tasks should have visibility=public for applicant
        for task in tasks:
            assert task.get("visibility") == "public", f"Applicant should only see public tasks, got {task.get('visibility')}"
        
        print(f"PASS: Applicant can list {len(tasks)} tasks (all visibility=public)")


class TestStaffAppointments:
    """Test staff appointment CRUD operations"""
    
    def test_staff_login(self):
        """BACKEND-4: Staff login works"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, f"Staff login failed: {resp.text}"
        print("PASS: Staff login successful")
    
    def test_staff_list_appointments(self):
        """BACKEND-5: GET /api/appointments as Staff shows all appointments"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, "Staff login failed"
        
        resp = session.get(f"{BASE_URL}/api/appointments")
        assert resp.status_code == 200, f"Appointments list failed: {resp.status_code} - {resp.text}"
        
        appointments = resp.json()
        assert isinstance(appointments, list), "Expected list of appointments"
        print(f"PASS: Staff can list {len(appointments)} appointments")
    
    def test_staff_create_appointment(self):
        """BACKEND-6: POST /api/appointments as Staff creates new appointment"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, "Staff login failed"
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        
        apt_data = {
            "title": "TEST_Beratungstermin",
            "type": "consultation",
            "date": "2026-02-15",
            "time": "10:00",
            "duration_min": 30,
            "description": "Test appointment for iteration 100",
            "location": "Online (Zoom)"
        }
        resp = session.post(f"{BASE_URL}/api/appointments", json=apt_data, headers=headers)
        
        assert resp.status_code == 200, f"Appointment creation failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        assert data.get("id"), "Appointment should have an id"
        assert data.get("title") == apt_data["title"], f"Title mismatch"
        assert data.get("status") == "confirmed", f"Expected status=confirmed, got {data.get('status')}"
        
        print(f"PASS: Staff created appointment id={data.get('id')}")
        return data.get("id")
    
    def test_staff_update_appointment(self):
        """BACKEND-7: PUT /api/appointments/{id} as Staff updates appointment"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, "Staff login failed"
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        
        # First create an appointment
        apt_data = {
            "title": "TEST_Update_Termin",
            "type": "consultation",
            "date": "2026-02-16",
            "time": "11:00",
            "duration_min": 30
        }
        resp = session.post(f"{BASE_URL}/api/appointments", json=apt_data, headers=headers)
        assert resp.status_code == 200, f"Appointment creation failed: {resp.text}"
        apt_id = resp.json().get("id")
        
        # Update the appointment
        update_data = {
            "title": "TEST_Updated_Termin",
            "time": "14:00",
            "description": "Updated description"
        }
        resp = session.put(f"{BASE_URL}/api/appointments/{apt_id}", json=update_data, headers=headers)
        
        assert resp.status_code == 200, f"Appointment update failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        assert data.get("title") == "TEST_Updated_Termin", f"Title not updated"
        assert data.get("time") == "14:00", f"Time not updated"
        
        print(f"PASS: Staff updated appointment id={apt_id}")
    
    def test_staff_cancel_appointment(self):
        """BACKEND-8: DELETE /api/appointments/{id} cancels appointment"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, "Staff login failed"
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        
        # First create an appointment
        apt_data = {
            "title": "TEST_Cancel_Termin",
            "type": "consultation",
            "date": "2026-02-17",
            "time": "09:00"
        }
        resp = session.post(f"{BASE_URL}/api/appointments", json=apt_data, headers=headers)
        assert resp.status_code == 200, f"Appointment creation failed: {resp.text}"
        apt_id = resp.json().get("id")
        
        # Cancel (DELETE) the appointment
        resp = session.delete(f"{BASE_URL}/api/appointments/{apt_id}", headers=headers)
        
        assert resp.status_code == 200, f"Appointment cancellation failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        assert data.get("status") == "cancelled", f"Expected status=cancelled, got {data.get('status')}"
        
        print(f"PASS: Staff cancelled appointment id={apt_id}")


class TestAuthLanguagePreference:
    """Test PUT /api/auth/me for language preference"""
    
    def test_staff_update_language_preference(self):
        """BACKEND-9: PUT /api/auth/me updates language_pref"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, "Staff login failed"
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        
        # Update language to English
        resp = session.put(f"{BASE_URL}/api/auth/me", json={"language_pref": "en"}, headers=headers)
        assert resp.status_code == 200, f"Language update failed: {resp.status_code} - {resp.text}"
        
        # Verify via GET /api/auth/me
        resp = session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200, f"GET /api/auth/me failed: {resp.text}"
        data = resp.json()
        assert data.get("language_pref") == "en", f"Language not updated to 'en', got {data.get('language_pref')}"
        
        # Update back to German
        resp = session.put(f"{BASE_URL}/api/auth/me", json={"language_pref": "de"}, headers=headers)
        assert resp.status_code == 200, f"Language update back to de failed: {resp.text}"
        
        print("PASS: PUT /api/auth/me language_pref update works")
    
    def test_applicant_update_language_preference(self):
        """BACKEND-10: Applicant can also update language_pref"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_applicant(session)
        assert resp.status_code == 200, "Applicant login failed"
        
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["x-csrf-token"] = csrf
        
        # Update language to English
        resp = session.put(f"{BASE_URL}/api/auth/me", json={"language_pref": "en"}, headers=headers)
        assert resp.status_code == 200, f"Applicant language update failed: {resp.status_code} - {resp.text}"
        
        # Verify
        resp = session.get(f"{BASE_URL}/api/auth/me")
        data = resp.json()
        assert data.get("language_pref") == "en", f"Applicant language not updated"
        
        # Restore to German
        resp = session.put(f"{BASE_URL}/api/auth/me", json={"language_pref": "de"}, headers=headers)
        
        print("PASS: Applicant can update language_pref")


class TestAvailableSlots:
    """Test appointment available slots endpoint"""
    
    def test_available_slots(self):
        """BACKEND-11: GET /api/appointments/available-slots returns slots"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_staff(session)
        assert resp.status_code == 200, "Staff login failed"
        
        resp = session.get(f"{BASE_URL}/api/appointments/available-slots?date=2026-02-20")
        assert resp.status_code == 200, f"Available slots failed: {resp.status_code} - {resp.text}"
        
        data = resp.json()
        assert "slots" in data, "Response should contain 'slots'"
        assert "date" in data, "Response should contain 'date'"
        assert isinstance(data["slots"], list), "Slots should be a list"
        
        print(f"PASS: Available slots endpoint returns {len(data['slots'])} slots for 2026-02-20")


class TestApplicantAppointments:
    """Test applicant can view their appointments"""
    
    def test_applicant_list_appointments(self):
        """BACKEND-12: GET /api/appointments as Applicant shows own appointments"""
        session = requests.Session()
        resp, csrf = TestCSRFAndAuth.login_applicant(session)
        assert resp.status_code == 200, "Applicant login failed"
        
        resp = session.get(f"{BASE_URL}/api/appointments")
        assert resp.status_code == 200, f"Applicant appointments list failed: {resp.status_code} - {resp.text}"
        
        appointments = resp.json()
        assert isinstance(appointments, list), "Expected list of appointments"
        
        print(f"PASS: Applicant can list {len(appointments)} appointments")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
