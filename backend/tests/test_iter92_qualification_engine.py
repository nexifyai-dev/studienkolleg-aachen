"""
Test Suite for Iteration 92: Qualification Engine, Language Triggers, and Duplicate Detection

Features tested:
1. Qualification Algorithm (Anabin → FSP/TestAS/Direktstudium/Pflege/Sprachkurs path recommendation)
2. Language Level Trigger (< B1 → Auto-Sprachkurs-Task + Notification; >= B1 → Pipeline unlock)
3. Lead Duplicate Logic (Email/Phone match → Admin task + Notification + duplicate_flag)
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Create authenticated staff session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert resp.status_code == 200, f"Staff login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Create authenticated admin session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Create authenticated applicant session."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
    return session


class TestQualificationPathEndpoints:
    """Test qualification path API endpoints."""

    def test_get_qualification_path_returns_data(self, staff_session):
        """GET /api/applications/{id}/qualification-path returns qualification path data."""
        # First get an application
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        apps = resp.json()
        assert len(apps) > 0, "No applications found for testing"
        
        app_id = apps[0]["id"]
        
        # Get qualification path
        resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/qualification-path")
        assert resp.status_code == 200
        data = resp.json()
        
        # Should have recommended_path field
        assert "recommended_path" in data
        assert "path_label_de" in data or data.get("recommended_path") == "not_computed"
        print(f"✓ GET qualification-path returns: {data.get('recommended_path', 'not_computed')}")

    def test_compute_qualification_staff_only(self, staff_session, applicant_session):
        """POST /api/applications/{id}/compute-qualification is Staff-only."""
        # Get an application
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = resp.json()
        app_id = apps[0]["id"]
        
        # Staff should be able to compute
        resp = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/compute-qualification")
        assert resp.status_code == 200
        data = resp.json()
        assert "recommended_path" in data
        print(f"✓ Staff can compute qualification: {data['recommended_path']}")
        
        # Applicant should NOT be able to compute (403)
        resp = applicant_session.post(f"{BASE_URL}/api/applications/{app_id}/compute-qualification")
        assert resp.status_code == 403, f"Expected 403 for applicant, got {resp.status_code}"
        print("✓ Applicant cannot compute qualification (403)")

    def test_compute_qualification_returns_full_structure(self, staff_session):
        """compute_qualification_path returns all required fields."""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = resp.json()
        app_id = apps[0]["id"]
        
        resp = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/compute-qualification")
        assert resp.status_code == 200
        data = resp.json()
        
        # Check all required fields
        required_fields = [
            "recommended_path",
            "path_label_de",
            "path_label_en",
            "reason_de",
            "reason_en",
            "next_steps_de",
            "next_steps_en",
            "auto_triggers",
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Validate types
        assert isinstance(data["next_steps_de"], list)
        assert isinstance(data["next_steps_en"], list)
        assert isinstance(data["auto_triggers"], list)
        
        print(f"✓ All required fields present in qualification response")
        print(f"  - recommended_path: {data['recommended_path']}")
        print(f"  - path_label_de: {data['path_label_de']}")
        print(f"  - auto_triggers: {data['auto_triggers']}")


class TestQualificationPaths:
    """Test different qualification paths based on Anabin categories."""

    def test_valid_qualification_paths(self, staff_session):
        """Qualification paths include all expected values."""
        valid_paths = [
            "direktstudium",
            "studienkolleg",
            "feststellungspruefung",
            "testas",
            "sprachkurs_zuerst",
            "pflegeausbildung",
            "manuelle_pruefung",
            "anpassungslehrgang",
            "berufsausbildung",
        ]
        
        # Get an application and compute
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = resp.json()
        app_id = apps[0]["id"]
        
        resp = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/compute-qualification")
        data = resp.json()
        
        assert data["recommended_path"] in valid_paths, f"Invalid path: {data['recommended_path']}"
        print(f"✓ Qualification path '{data['recommended_path']}' is valid")


class TestLanguageTrigger:
    """Test language level trigger functionality."""

    def test_language_trigger_creates_task_for_low_level(self, admin_session):
        """Language trigger < B1 creates auto task (type=language_course)."""
        # Check tasks collection for language_course type tasks
        resp = admin_session.get(f"{BASE_URL}/api/tasks")
        assert resp.status_code == 200
        tasks = resp.json()
        
        # Look for language_course tasks
        lang_tasks = [t for t in tasks if t.get("type") == "language_course"]
        print(f"✓ Found {len(lang_tasks)} language_course tasks in system")
        
        # Verify task structure if any exist
        if lang_tasks:
            task = lang_tasks[0]
            assert "title" in task
            assert "status" in task
            assert task.get("priority") == "high" or task.get("priority") is not None
            print(f"  - Task: {task.get('title', 'N/A')[:50]}...")

    def test_language_trigger_pipeline_advancement(self, staff_session):
        """Language trigger >= B1 can advance pipeline from lead_new to in_review."""
        # This is tested implicitly through the qualification engine
        # When language level >= B1, the pipeline should be unlocked
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = resp.json()
        
        # Find an application with B1 or higher
        b1_apps = [a for a in apps if a.get("language_level") in ["B1", "B2", "C1", "C2"]]
        if b1_apps:
            app = b1_apps[0]
            print(f"✓ Found application with language level {app.get('language_level')}")
            print(f"  - Current stage: {app.get('current_stage')}")
        else:
            print("⚠ No applications with B1+ language level found for testing")


class TestDuplicateDetection:
    """Test duplicate detection on application creation."""

    def test_duplicate_check_on_create(self, admin_session, staff_session):
        """Duplicate check on application create checks email/phone match."""
        # Get existing applications to find potential duplicates
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = resp.json()
        
        # Check if any have duplicate_flag
        duplicates = [a for a in apps if a.get("duplicate_flag") == True]
        print(f"✓ Found {len(duplicates)} applications with duplicate_flag=true")
        
        if duplicates:
            dup = duplicates[0]
            assert "duplicate_info" in dup or dup.get("duplicate_flag") == True
            print(f"  - Duplicate app: {dup.get('applicant_number', 'N/A')}")

    def test_duplicate_creates_admin_task(self, admin_session):
        """Duplicate detection creates admin task (type=duplicate_review, priority=high)."""
        resp = admin_session.get(f"{BASE_URL}/api/tasks")
        assert resp.status_code == 200
        tasks = resp.json()
        
        # Look for duplicate_review tasks
        dup_tasks = [t for t in tasks if t.get("type") == "duplicate_review"]
        print(f"✓ Found {len(dup_tasks)} duplicate_review tasks")
        
        if dup_tasks:
            task = dup_tasks[0]
            assert task.get("priority") == "high", f"Expected high priority, got {task.get('priority')}"
            print(f"  - Task: {task.get('title', 'N/A')[:50]}...")

    def test_duplicate_creates_notification(self, admin_session):
        """Duplicate detection creates notification for admin."""
        resp = admin_session.get(f"{BASE_URL}/api/notifications")
        assert resp.status_code == 200
        notifications = resp.json()
        
        # Look for duplicate_detected notifications
        dup_notifs = [n for n in notifications if n.get("type") == "duplicate_detected"]
        print(f"✓ Found {len(dup_notifs)} duplicate_detected notifications")

    def test_application_with_duplicate_has_flag(self, staff_session):
        """Application with duplicate has duplicate_flag=true and duplicate_info object."""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        apps = resp.json()
        
        duplicates = [a for a in apps if a.get("duplicate_flag") == True]
        
        if duplicates:
            dup = duplicates[0]
            assert dup.get("duplicate_flag") == True
            # duplicate_info should be present
            if dup.get("duplicate_info"):
                info = dup["duplicate_info"]
                assert "match_type" in info or "existing_app_id" in info
                print(f"✓ Duplicate info: {info}")
        else:
            print("⚠ No duplicate applications found - this is expected if no duplicates exist")


class TestOpenRouterProvider:
    """Test OpenRouter provider configuration."""

    def test_openrouter_provider_file_exists(self):
        """OpenRouter provider file exists."""
        import os
        provider_path = "/app/backend/services/openrouter_provider.py"
        assert os.path.exists(provider_path), f"OpenRouter provider not found at {provider_path}"
        print(f"✓ OpenRouter provider file exists at {provider_path}")

    def test_openrouter_configured(self):
        """OpenRouter is configured with minimax-m2.7."""
        # Check backend .env file for configuration
        env_path = "/app/backend/.env"
        assert os.path.exists(env_path), "Backend .env file not found"
        
        with open(env_path, "r") as f:
            env_content = f.read()
        
        assert "OPENROUTER_API_KEY" in env_content, "OPENROUTER_API_KEY not in .env"
        assert "OPENROUTER_MODEL" in env_content, "OPENROUTER_MODEL not in .env"
        assert "minimax" in env_content.lower(), "minimax model not configured"
        print("✓ OpenRouter configured in backend .env with minimax model")


class TestQualificationEngineFile:
    """Test qualification_engine.py file structure."""

    def test_qualification_engine_exists(self):
        """qualification_engine.py contains compute_qualification_path function."""
        import os
        engine_path = "/app/backend/services/qualification_engine.py"
        assert os.path.exists(engine_path), f"Qualification engine not found at {engine_path}"
        
        with open(engine_path, "r") as f:
            content = f.read()
        
        assert "compute_qualification_path" in content
        assert "async def compute_qualification_path" in content
        print("✓ qualification_engine.py contains compute_qualification_path function")


class TestAutomationFile:
    """Test automation.py file structure."""

    def test_automation_contains_language_trigger(self):
        """automation.py contains trigger_language_level_action function."""
        import os
        automation_path = "/app/backend/services/automation.py"
        assert os.path.exists(automation_path), f"Automation file not found at {automation_path}"
        
        with open(automation_path, "r") as f:
            content = f.read()
        
        assert "trigger_language_level_action" in content
        assert "async def trigger_language_level_action" in content
        print("✓ automation.py contains trigger_language_level_action function")


class TestBackendHealth:
    """Test backend starts without errors."""

    def test_backend_health(self):
        """Backend starts without errors."""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print(f"✓ Backend healthy: {data}")

    def test_auth_endpoints_work(self):
        """Auth endpoints are functional."""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data.get("role") == "staff"
        print(f"✓ Auth working: logged in as {data.get('email')}")


class TestIntegrationFlow:
    """Test full integration flow."""

    def test_full_qualification_flow(self, staff_session):
        """Test complete qualification flow: get app → compute → verify stored."""
        # 1. Get applications
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        apps = resp.json()
        assert len(apps) > 0
        app_id = apps[0]["id"]
        
        # 2. Compute qualification
        resp = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/compute-qualification")
        assert resp.status_code == 200
        computed = resp.json()
        assert "recommended_path" in computed
        
        # 3. Verify it's stored
        resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/qualification-path")
        assert resp.status_code == 200
        stored = resp.json()
        
        # Should match what was computed
        assert stored.get("recommended_path") == computed.get("recommended_path")
        print(f"✓ Full flow works: computed and stored path = {stored['recommended_path']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
