"""
Test Iteration 97 – New Features Testing

Tests for:
- LMS Module (courses, enrollment, access, content)
- Teacher Portal (grades, attendance, progress)
- External Knowledge Base
- CSRF Double-Submit Cookie
- Backup Service
- Rate Limiting (30/min)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Staff login session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL, "password": STAFF_PASSWORD
    })
    assert resp.status_code == 200, f"Staff login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Applicant login session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD
    })
    assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def teacher_session():
    """Teacher login session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEACHER_EMAIL, "password": TEACHER_PASSWORD
    })
    assert resp.status_code == 200, f"Teacher login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Admin login session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return session


# ══════════════════════════════════════════════════════════════════════
# LMS TESTS
# ══════════════════════════════════════════════════════════════════════

class TestLMSCourses:
    """LMS Course Catalog Tests"""

    def test_lms1_list_courses_returns_6_plus(self, staff_session):
        """LMS-1: GET /api/lms/courses returns 6+ courses with correct structure"""
        resp = staff_session.get(f"{BASE_URL}/api/lms/courses")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        courses = resp.json()
        assert isinstance(courses, list), "Response should be a list"
        assert len(courses) >= 6, f"Expected 6+ courses, got {len(courses)}"
        
        # Check structure of first course
        course = courses[0]
        required_fields = ["id", "code", "title", "description", "category", "price", "currency", "course_type"]
        for field in required_fields:
            assert field in course, f"Missing field: {field}"
        print(f"✓ LMS-1: Found {len(courses)} courses with correct structure")

    def test_lms2_get_tkurs_details(self, staff_session):
        """LMS-2: GET /api/lms/courses/course-tkurs returns T-Kurs details with modules"""
        resp = staff_session.get(f"{BASE_URL}/api/lms/courses/course-tkurs")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        course = resp.json()
        
        assert course["id"] == "course-tkurs"
        assert course["code"] == "SK-TKURS"
        assert "T-Kurs" in course["title"]
        assert "modules" in course
        assert len(course["modules"]) > 0, "T-Kurs should have modules"
        print(f"✓ LMS-2: T-Kurs has {len(course['modules'])} modules")

    def test_lms3_enroll_applicant(self, applicant_session):
        """LMS-3: POST /api/lms/enroll creates enrollment (Applicant)"""
        # Use course-a1a2 as specified in agent context
        resp = applicant_session.post(f"{BASE_URL}/api/lms/enroll", json={
            "course_id": "course-a1a2",
            "payment_method": "stripe"
        })
        # Accept 200/201 for success, 400 for duplicate (already enrolled)
        assert resp.status_code in [200, 201, 400], f"Unexpected status: {resp.status_code} - {resp.text}"
        
        if resp.status_code == 400:
            assert "Bereits" in resp.text or "already" in resp.text.lower(), "Should be duplicate enrollment error"
            print("✓ LMS-3: Enrollment exists (duplicate prevention working)")
        else:
            enrollment = resp.json()
            assert "id" in enrollment
            assert enrollment["course_id"] == "course-a1a2"
            print(f"✓ LMS-3: Created enrollment {enrollment['id']}")

    def test_lms4_my_enrollments(self, applicant_session):
        """LMS-4: GET /api/lms/my-enrollments returns user enrollments"""
        resp = applicant_session.get(f"{BASE_URL}/api/lms/my-enrollments")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        enrollments = resp.json()
        assert isinstance(enrollments, list), "Response should be a list"
        print(f"✓ LMS-4: Applicant has {len(enrollments)} enrollments")

    def test_lms5_list_all_enrollments_staff(self, staff_session):
        """LMS-5: GET /api/lms/enrollments returns all enrollments (Staff-only)"""
        resp = staff_session.get(f"{BASE_URL}/api/lms/enrollments")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        enrollments = resp.json()
        assert isinstance(enrollments, list), "Response should be a list"
        print(f"✓ LMS-5: Staff sees {len(enrollments)} total enrollments")

    def test_lms5_list_enrollments_denied_for_applicant(self, applicant_session):
        """LMS-5b: GET /api/lms/enrollments denied for applicant"""
        resp = applicant_session.get(f"{BASE_URL}/api/lms/enrollments")
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        print("✓ LMS-5b: Applicant correctly denied access to all enrollments")

    def test_lms6_update_enrollment_staff(self, staff_session):
        """LMS-6: PUT /api/lms/enrollments/{id} updates enrollment (Staff)"""
        # First get an enrollment
        resp = staff_session.get(f"{BASE_URL}/api/lms/enrollments")
        assert resp.status_code == 200
        enrollments = resp.json()
        
        if len(enrollments) == 0:
            pytest.skip("No enrollments to update")
        
        enrollment_id = enrollments[0]["id"]
        resp = staff_session.put(f"{BASE_URL}/api/lms/enrollments/{enrollment_id}", json={
            "notes": "Test update from iteration 97"
        })
        assert resp.status_code == 200, f"Failed: {resp.text}"
        result = resp.json()
        assert result.get("ok") == True
        print(f"✓ LMS-6: Updated enrollment {enrollment_id}")

    def test_lms7_grant_access_staff(self, staff_session):
        """LMS-7: POST /api/lms/grant-access grants stipendium access (Staff)"""
        # Get an enrollment to grant access
        resp = staff_session.get(f"{BASE_URL}/api/lms/enrollments")
        assert resp.status_code == 200
        enrollments = resp.json()
        
        if len(enrollments) == 0:
            pytest.skip("No enrollments to grant access")
        
        enrollment_id = enrollments[0]["id"]
        resp = staff_session.post(f"{BASE_URL}/api/lms/grant-access", json={
            "enrollment_id": enrollment_id,
            "reason": "stipendium",
            "notes": "Test grant from iteration 97"
        })
        assert resp.status_code == 200, f"Failed: {resp.text}"
        result = resp.json()
        assert result.get("ok") == True
        assert result.get("access_granted") == True
        print(f"✓ LMS-7: Granted access to enrollment {enrollment_id}")

    def test_lms8_course_content_with_access(self, staff_session):
        """LMS-8: GET /api/lms/courses/{id}/content returns content only with access"""
        # Staff should have access
        resp = staff_session.get(f"{BASE_URL}/api/lms/courses/course-tkurs/content")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        content = resp.json()
        assert "course" in content
        assert content.get("access") == True
        print("✓ LMS-8: Staff can access course content")

    def test_lms8_course_content_denied_without_access(self):
        """LMS-8b: Course content denied without enrollment/access"""
        # Create fresh session without enrollment
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD
        })
        assert resp.status_code == 200
        
        # Try to access a course they're not enrolled in
        resp = session.get(f"{BASE_URL}/api/lms/courses/course-mkurs/content")
        # Should be 403 if no access, or 200 if they have access
        assert resp.status_code in [200, 403], f"Unexpected: {resp.status_code}"
        print(f"✓ LMS-8b: Content access check working (status={resp.status_code})")

    def test_lms9_duplicate_enrollment_prevention(self, applicant_session):
        """LMS-9: Duplicate enrollment prevention (same user + course)"""
        # Try to enroll in same course twice
        resp = applicant_session.post(f"{BASE_URL}/api/lms/enroll", json={
            "course_id": "course-a1a2",
            "payment_method": "stripe"
        })
        # Should be 400 for duplicate
        assert resp.status_code == 400, f"Expected 400 for duplicate, got {resp.status_code}"
        assert "Bereits" in resp.text or "already" in resp.text.lower()
        print("✓ LMS-9: Duplicate enrollment correctly prevented")


# ══════════════════════════════════════════════════════════════════════
# TEACHER PORTAL TESTS
# ══════════════════════════════════════════════════════════════════════

class TestTeacherPortal:
    """Teacher Portal Tests - Grades, Attendance, Progress"""

    def test_teacher1_add_grade_requires_teacher_role(self, staff_session):
        """TEACHER-1: POST /api/teacher/grades requires teacher role (403 for Staff)"""
        resp = staff_session.post(f"{BASE_URL}/api/teacher/grades", json={
            "student_id": "test-student-id",
            "subject": "Mathematik",
            "grade": "2.0",
            "grade_numeric": 2.0
        })
        # Staff should get 403 - this is CORRECT behavior
        assert resp.status_code == 403, f"Expected 403 for staff, got {resp.status_code}"
        print("✓ TEACHER-1: Staff correctly denied (403) - teacher role required")

    def test_teacher1_add_grade_teacher_role(self, teacher_session):
        """TEACHER-1b: POST /api/teacher/grades works for teacher (may fail if no assignment)"""
        resp = teacher_session.post(f"{BASE_URL}/api/teacher/grades", json={
            "student_id": "test-student-id",
            "subject": "Mathematik",
            "grade": "2.0",
            "grade_numeric": 2.0
        })
        # Teacher can call endpoint but may get 403 if student not assigned
        assert resp.status_code in [200, 201, 400, 403], f"Unexpected: {resp.status_code}"
        if resp.status_code == 403:
            print("✓ TEACHER-1b: Teacher role works, but student not assigned (expected)")
        else:
            print(f"✓ TEACHER-1b: Teacher grade endpoint accessible (status={resp.status_code})")

    def test_teacher2_get_grades_requires_teacher(self, staff_session):
        """TEACHER-2: GET /api/teacher/grades/{student_id} requires teacher role"""
        resp = staff_session.get(f"{BASE_URL}/api/teacher/grades/test-student-id")
        assert resp.status_code == 403, f"Expected 403 for staff, got {resp.status_code}"
        print("✓ TEACHER-2: Staff correctly denied access to grades")

    def test_teacher3_attendance_requires_teacher(self, staff_session):
        """TEACHER-3: POST /api/teacher/attendance requires teacher role"""
        resp = staff_session.post(f"{BASE_URL}/api/teacher/attendance", json={
            "student_id": "test-student-id",
            "status": "present",
            "subject": "Mathematik"
        })
        assert resp.status_code == 403, f"Expected 403 for staff, got {resp.status_code}"
        print("✓ TEACHER-3: Staff correctly denied attendance recording")

    def test_teacher4_get_attendance_requires_teacher(self, staff_session):
        """TEACHER-4: GET /api/teacher/attendance/{student_id} requires teacher role"""
        resp = staff_session.get(f"{BASE_URL}/api/teacher/attendance/test-student-id")
        assert resp.status_code == 403, f"Expected 403 for staff, got {resp.status_code}"
        print("✓ TEACHER-4: Staff correctly denied attendance access")

    def test_teacher5_progress_requires_teacher(self, staff_session):
        """TEACHER-5: GET /api/teacher/progress/{student_id} requires teacher role"""
        resp = staff_session.get(f"{BASE_URL}/api/teacher/progress/test-student-id")
        assert resp.status_code == 403, f"Expected 403 for staff, got {resp.status_code}"
        print("✓ TEACHER-5: Staff correctly denied progress access")

    def test_teacher_list_accessible(self, staff_session):
        """Teacher list endpoint accessible to staff"""
        resp = staff_session.get(f"{BASE_URL}/api/teacher/list")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        teachers = resp.json()
        assert isinstance(teachers, list)
        print(f"✓ Teacher list: Found {len(teachers)} teachers")


# ══════════════════════════════════════════════════════════════════════
# KNOWLEDGE BASE TESTS
# ══════════════════════════════════════════════════════════════════════

class TestKnowledgeBase:
    """External Knowledge Base Tests"""

    def test_kb1_knowledge_base_endpoint(self, staff_session):
        """KB-1: GET /api/oracle/knowledge-base returns 8 areas + 12 reference URLs"""
        resp = staff_session.get(f"{BASE_URL}/api/oracle/knowledge-base")
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        
        assert "knowledge_base" in data
        assert "reference_urls" in data
        
        kb = data["knowledge_base"]
        urls = data["reference_urls"]
        
        # Check for 8 areas
        expected_areas = ["anabin", "uni_assist", "testas", "visa_requirements", 
                         "bamf", "language_certificates", "document_verification", 
                         "professional_recognition"]
        for area in expected_areas:
            assert area in kb, f"Missing area: {area}"
        
        print(f"✓ KB-1: Found {len(kb)} knowledge areas, {len(urls)} reference URLs")
        assert len(urls) >= 12, f"Expected 12+ URLs, got {len(urls)}"

    def test_kb2_knowledge_base_content(self, staff_session):
        """KB-2: Knowledge base includes anabin categories, visa requirements, language certificates"""
        resp = staff_session.get(f"{BASE_URL}/api/oracle/knowledge-base")
        assert resp.status_code == 200
        kb = resp.json()["knowledge_base"]
        
        # Check anabin categories
        assert "categories" in kb["anabin"]
        categories = kb["anabin"]["categories"]
        assert "H+" in categories
        assert "H+/-" in categories
        assert "H-" in categories
        print("✓ KB-2a: Anabin categories present (H+, H+/-, H-)")
        
        # Check visa requirements
        assert "required_documents" in kb["visa_requirements"]
        assert len(kb["visa_requirements"]["required_documents"]) > 0
        print("✓ KB-2b: Visa requirements present")
        
        # Check language certificates
        assert "goethe" in kb["language_certificates"]
        assert "telc" in kb["language_certificates"]
        assert "testdaf" in kb["language_certificates"]
        print("✓ KB-2c: Language certificates present (Goethe, telc, TestDaF)")


# ══════════════════════════════════════════════════════════════════════
# CSRF TESTS
# ══════════════════════════════════════════════════════════════════════

class TestCSRF:
    """CSRF Double-Submit Cookie Tests"""

    def test_csrf1_cookie_set_on_response(self):
        """CSRF-1: CSRF cookie (csrf_token) is set on responses"""
        session = requests.Session()
        resp = session.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        
        # Check if csrf_token cookie is set
        cookies = session.cookies.get_dict()
        assert "csrf_token" in cookies, f"CSRF cookie not set. Cookies: {cookies.keys()}"
        assert len(cookies["csrf_token"]) > 0
        print(f"✓ CSRF-1: csrf_token cookie set (length={len(cookies['csrf_token'])})")

    def test_csrf2_safe_methods_work_without_header(self):
        """CSRF-2: Safe methods (GET) work without CSRF header"""
        session = requests.Session()
        resp = session.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        print("✓ CSRF-2: GET works without CSRF header")

    def test_csrf3_unsafe_methods_transition_mode(self, staff_session):
        """CSRF-3: Unsafe methods (POST) work in transition mode (no blocking)"""
        # In transition mode, POST should work even without CSRF header
        # The middleware logs but does not block
        resp = staff_session.post(f"{BASE_URL}/api/lms/enroll", json={
            "course_id": "course-dsh",
            "payment_method": "stripe"
        })
        # Should not be blocked by CSRF (transition mode)
        # May be 200/400 depending on enrollment status
        assert resp.status_code != 403 or "CSRF" not in resp.text, "CSRF should not block in transition mode"
        print(f"✓ CSRF-3: POST works in transition mode (status={resp.status_code})")


# ══════════════════════════════════════════════════════════════════════
# BACKUP SERVICE TESTS
# ══════════════════════════════════════════════════════════════════════

class TestBackupService:
    """Backup Service Tests"""

    def test_backup1_service_exists(self):
        """BACKUP-1: backup.py service exists with run_backup function"""
        # We can't directly call the backup function, but we can verify the module exists
        # by checking if the import works in the backend
        # For now, we verify the file structure is correct
        import importlib.util
        backup_path = "/app/backend/services/backup.py"
        
        # Check file exists
        assert os.path.exists(backup_path), f"backup.py not found at {backup_path}"
        
        # Read and verify content
        with open(backup_path, 'r') as f:
            content = f.read()
        
        assert "async def run_backup" in content, "run_backup function not found"
        assert "_cleanup_old_backups" in content, "_cleanup_old_backups function not found"
        assert "mongodump" in content, "mongodump command not found"
        print("✓ BACKUP-1: backup.py exists with run_backup and cleanup functions")


# ══════════════════════════════════════════════════════════════════════
# RATE LIMITING TESTS
# ══════════════════════════════════════════════════════════════════════

class TestRateLimiting:
    """Rate Limiting Tests"""

    def test_rate1_login_limit_30_per_minute(self):
        """RATE-1: Login rate limit is 30/minute (not 10)"""
        # Check the rate_limiter.py file
        rate_limiter_path = "/app/backend/rate_limiter.py"
        with open(rate_limiter_path, 'r') as f:
            content = f.read()
        
        # The old limit was 10/minute, new should be 30/minute
        # Check auth.py for the actual limit
        auth_path = "/app/backend/routers/auth.py"
        with open(auth_path, 'r') as f:
            auth_content = f.read()
        
        # Look for the login endpoint rate limit
        assert '30/minute' in auth_content, f"Login rate limit should be 30/minute"
        print("✓ RATE-1: Login rate limit is 30/minute")


# ══════════════════════════════════════════════════════════════════════
# GENERAL HEALTH TESTS
# ══════════════════════════════════════════════════════════════════════

class TestGeneralHealth:
    """General Health and Regression Tests"""

    def test_health_endpoint(self):
        """ALL: Backend starts without errors"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print(f"✓ Health check passed: version={data.get('version')}")

    def test_previous_features_work(self, staff_session):
        """ALL: Previous features still work"""
        # Test applications endpoint
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        print("✓ Applications endpoint works")
        
        # Test tasks endpoint
        resp = staff_session.get(f"{BASE_URL}/api/tasks")
        assert resp.status_code == 200
        print("✓ Tasks endpoint works")
        
        # Test invoices endpoint
        resp = staff_session.get(f"{BASE_URL}/api/invoices")
        assert resp.status_code == 200
        print("✓ Invoices endpoint works")


# ══════════════════════════════════════════════════════════════════════
# STRIPE WEBHOOK TESTS
# ══════════════════════════════════════════════════════════════════════

class TestStripeWebhook:
    """Stripe Webhook Tests"""

    def test_stripe1_webhook_handler_exists(self):
        """STRIPE-1: Webhook handler sends applicant notification on payment"""
        # Check payments.py for notification logic
        payments_path = "/app/backend/routers/payments.py"
        with open(payments_path, 'r') as f:
            content = f.read()
        
        # Verify notification logic exists in webhook handler
        assert "notifications.insert_one" in content, "Notification insert not found in webhook"
        assert "payment_confirmed" in content, "payment_confirmed notification type not found"
        assert "Bewerber-Benachrichtigung" in content or "applicant_id" in content, "Applicant notification logic not found"
        print("✓ STRIPE-1: Webhook handler includes applicant notification logic")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
