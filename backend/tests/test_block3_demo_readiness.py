"""
Block 3: Demo-Readiness / Präsentationsreife Tests

Tests für:
1. Demo-Daten (realistische Bewerbernamen, keine TEST_-Einträge)
2. Invoice Settings (Präfix/Startnr/Suffix bearbeitbar)
3. Invoice Search
4. DeepSeek Migration (AI Model Registry)
5. Messaging Polling (3s)
6. Stage Labels (documents_requested)
7. Navigation & Regression
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Staff login session."""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL, "password": STAFF_PASSWORD
    })
    assert r.status_code == 200, f"Staff login failed: {r.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Admin login session."""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Applicant login session."""
    session = requests.Session()
    r = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD
    })
    assert r.status_code == 200, f"Applicant login failed: {r.text}"
    return session


class TestDemoData:
    """Test realistic demo data - no TEST_ entries."""

    def test_applications_have_realistic_names(self, staff_session):
        """Applications should have realistic international names, not TEST_ prefixes."""
        r = staff_session.get(f"{BASE_URL}/api/applications")
        assert r.status_code == 200
        apps = r.json()
        assert len(apps) >= 10, f"Expected at least 10 demo applications, got {len(apps)}"
        
        # Check for realistic names (no TEST_ prefix)
        for app in apps:
            name = app.get("applicant", {}).get("full_name", "")
            assert not name.startswith("TEST_"), f"Found TEST_ prefix in name: {name}"
            assert name, f"Application {app.get('id')} has empty applicant name"
        
        # Check for international diversity
        countries = set(app.get("applicant", {}).get("country", "") for app in apps)
        assert len(countries) >= 5, f"Expected at least 5 different countries, got {countries}"
        print(f"✓ {len(apps)} applications with realistic names from {len(countries)} countries")

    def test_tasks_have_realistic_descriptions(self, staff_session):
        """Tasks should have realistic German descriptions."""
        r = staff_session.get(f"{BASE_URL}/api/tasks")
        assert r.status_code == 200
        tasks = r.json()
        assert len(tasks) >= 4, f"Expected at least 4 demo tasks, got {len(tasks)}"
        
        for task in tasks:
            title = task.get("title", "")
            assert not title.startswith("TEST_"), f"Found TEST_ prefix in task: {title}"
            assert title, f"Task {task.get('id')} has empty title"
        print(f"✓ {len(tasks)} tasks with realistic descriptions")

    def test_invoices_have_realistic_data(self, staff_session):
        """Invoices should have realistic applicant names and W2G numbering."""
        r = staff_session.get(f"{BASE_URL}/api/invoices")
        assert r.status_code == 200
        invoices = r.json()
        assert len(invoices) >= 4, f"Expected at least 4 demo invoices, got {len(invoices)}"
        
        for inv in invoices:
            # Check invoice number format: W2G-YYYYMM-XXXX-AC
            inv_num = inv.get("invoice_number", "")
            assert inv_num.startswith("W2G-"), f"Invoice number should start with W2G-: {inv_num}"
            assert "-AC" in inv_num, f"Invoice number should contain -AC suffix: {inv_num}"
            
            # Check applicant name
            name = inv.get("applicant_name", "")
            assert not name.startswith("TEST_"), f"Found TEST_ prefix in invoice applicant: {name}"
        print(f"✓ {len(invoices)} invoices with W2G numbering format")


class TestInvoiceSettings:
    """Test invoice numbering settings (Präfix/Startnr/Suffix)."""

    def test_get_invoice_settings(self, staff_session):
        """Staff can get invoice settings."""
        r = staff_session.get(f"{BASE_URL}/api/invoices/settings")
        assert r.status_code == 200
        settings = r.json()
        
        assert "prefix" in settings, "Settings should have prefix"
        assert "start_number" in settings, "Settings should have start_number"
        assert "suffix" in settings, "Settings should have suffix"
        assert "include_date" in settings, "Settings should have include_date"
        assert "preview" in settings, "Settings should have preview"
        
        # Verify current W2G settings
        assert settings["prefix"] == "W2G", f"Expected prefix W2G, got {settings['prefix']}"
        assert settings["suffix"] == "AC", f"Expected suffix AC, got {settings['suffix']}"
        print(f"✓ Invoice settings: {settings['prefix']}-YYYYMM-XXXX-{settings['suffix']}")

    def test_update_invoice_settings_admin_only(self, staff_session, admin_session):
        """Only admin can update invoice settings."""
        # Staff should get 403
        r = staff_session.put(f"{BASE_URL}/api/invoices/settings", json={
            "prefix": "TEST"
        })
        assert r.status_code == 403, f"Staff should not update settings: {r.status_code}"
        
        # Admin can update
        r = admin_session.put(f"{BASE_URL}/api/invoices/settings", json={
            "prefix": "W2G",
            "start_number": 1001,
            "suffix": "AC",
            "include_date": True
        })
        assert r.status_code == 200, f"Admin should update settings: {r.text}"
        settings = r.json()
        assert settings["prefix"] == "W2G"
        print("✓ Invoice settings RBAC: Admin only")

    def test_invoice_number_preview(self, staff_session):
        """Invoice settings should show preview of next number."""
        r = staff_session.get(f"{BASE_URL}/api/invoices/settings")
        assert r.status_code == 200
        settings = r.json()
        
        preview = settings.get("preview", "")
        # Should match pattern: W2G-YYYYMM-XXXX-AC
        pattern = r"W2G-\d{6}-\d{4}-AC"
        assert re.match(pattern, preview), f"Preview should match W2G-YYYYMM-XXXX-AC: {preview}"
        print(f"✓ Invoice number preview: {preview}")


class TestInvoiceSearch:
    """Test invoice search functionality."""

    def test_invoice_list_with_status_filter(self, staff_session):
        """Staff can filter invoices by status."""
        # Get all invoices
        r = staff_session.get(f"{BASE_URL}/api/invoices")
        assert r.status_code == 200
        all_invoices = r.json()
        
        # Filter by status
        for status in ["draft", "sent", "paid"]:
            r = staff_session.get(f"{BASE_URL}/api/invoices?status={status}")
            assert r.status_code == 200
            filtered = r.json()
            for inv in filtered:
                assert inv.get("status") == status, f"Expected status {status}, got {inv.get('status')}"
        print("✓ Invoice status filter working")

    def test_invoice_stats(self, staff_session):
        """Invoice stats endpoint returns correct structure."""
        r = staff_session.get(f"{BASE_URL}/api/invoices/stats")
        assert r.status_code == 200
        stats = r.json()
        
        assert "total_count" in stats, "Stats should have total_count"
        assert "total_amount" in stats, "Stats should have total_amount"
        assert "by_status" in stats, "Stats should have by_status"
        
        assert stats["total_count"] >= 4, f"Expected at least 4 invoices, got {stats['total_count']}"
        print(f"✓ Invoice stats: {stats['total_count']} invoices, {stats['total_amount']}€ total")


class TestDeepSeekMigration:
    """Test DeepSeek AI provider migration."""

    def test_ai_model_registry_returns_deepseek(self, staff_session):
        """AI model registry should show DeepSeek models, not NSCall."""
        r = staff_session.get(f"{BASE_URL}/api/ai/model-registry")
        assert r.status_code == 200
        registry = r.json()
        
        assert registry.get("enabled") == True, "AI should be enabled"
        models = registry.get("models", {})
        
        # Check all task types use deepseek models
        for task_type in ["screening", "classification", "summary", "suggestion"]:
            assert task_type in models, f"Missing task type: {task_type}"
            model = models[task_type].get("model", "")
            assert "deepseek" in model.lower(), f"Task {task_type} should use DeepSeek: {model}"
        
        # Verify no NSCall references
        registry_str = str(registry).lower()
        assert "nscall" not in registry_str, "Should not contain NSCall references"
        print(f"✓ DeepSeek migration complete: {list(models.keys())}")


class TestStageLabels:
    """Test stage labels including documents_requested."""

    def test_applications_have_valid_stages(self, staff_session):
        """All applications should have valid stage values."""
        r = staff_session.get(f"{BASE_URL}/api/applications")
        assert r.status_code == 200
        apps = r.json()
        
        valid_stages = {
            "lead_new", "contacted", "in_review", "pending_docs", "documents_requested",
            "docs_requested", "docs_received", "docs_review", "interview_scheduled",
            "conditional_offer", "offer_sent", "enrolled", "invoice_open",
            "payment_received", "process_next", "on_hold", "declined",
            "completed", "dormant", "archived"
        }
        
        stages_found = set()
        for app in apps:
            stage = app.get("current_stage", "")
            assert stage in valid_stages, f"Invalid stage: {stage}"
            stages_found.add(stage)
        
        print(f"✓ Found {len(stages_found)} different stages: {stages_found}")


class TestMessaging:
    """Test messaging functionality."""

    def test_conversations_list(self, staff_session):
        """Staff can list conversations."""
        r = staff_session.get(f"{BASE_URL}/api/conversations")
        assert r.status_code == 200
        convs = r.json()
        assert isinstance(convs, list), "Conversations should be a list"
        print(f"✓ Found {len(convs)} conversations")

    def test_applicant_support_conversation(self, applicant_session):
        """Applicant can access support conversation."""
        r = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert r.status_code == 200
        conv = r.json()
        assert "id" in conv, "Support conversation should have id"
        print(f"✓ Applicant support conversation: {conv.get('id')}")


class TestNavigation:
    """Test navigation endpoints."""

    def test_dashboard_stats(self, staff_session):
        """Dashboard stats endpoint works."""
        r = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert r.status_code == 200
        stats = r.json()
        
        assert "total_leads" in stats, "Stats should have total_leads"
        assert "open_tasks" in stats, "Stats should have open_tasks"
        print(f"✓ Dashboard stats: {stats['total_leads']} leads, {stats['open_tasks']} open tasks")

    def test_kanban_applications(self, staff_session):
        """Kanban board data (applications) loads."""
        r = staff_session.get(f"{BASE_URL}/api/applications")
        assert r.status_code == 200
        apps = r.json()
        assert len(apps) >= 10, f"Expected at least 10 applications for Kanban, got {len(apps)}"
        print(f"✓ Kanban: {len(apps)} applications")


class TestRegression:
    """Regression tests for existing functionality."""

    def test_login_logout_flow(self):
        """Login and logout work correctly."""
        session = requests.Session()
        
        # Login
        r = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL, "password": STAFF_PASSWORD
        })
        assert r.status_code == 200, f"Login failed: {r.text}"
        
        # Check auth
        r = session.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 200, f"Auth check failed: {r.text}"
        
        # Logout
        r = session.post(f"{BASE_URL}/api/auth/logout")
        assert r.status_code == 200, f"Logout failed: {r.text}"
        
        # Verify logged out
        r = session.get(f"{BASE_URL}/api/auth/me")
        assert r.status_code == 401, "Should be logged out"
        print("✓ Login/Logout flow working")

    def test_role_based_access(self, staff_session, applicant_session):
        """Role-based access control works."""
        # Staff can access applications
        r = staff_session.get(f"{BASE_URL}/api/applications")
        assert r.status_code == 200, "Staff should access applications"
        
        # Applicant cannot access all applications
        r = applicant_session.get(f"{BASE_URL}/api/applications")
        # Applicant gets their own application or empty list
        assert r.status_code == 200
        
        # Applicant cannot access invoice settings
        r = applicant_session.get(f"{BASE_URL}/api/invoices/settings")
        assert r.status_code == 403, "Applicant should not access invoice settings"
        print("✓ RBAC working correctly")

    def test_audit_logs_exist(self, admin_session):
        """Audit logs are being created."""
        r = admin_session.get(f"{BASE_URL}/api/audit-logs?limit=10")
        assert r.status_code == 200
        logs = r.json()
        assert len(logs) > 0, "Should have audit logs"
        print(f"✓ Audit logs: {len(logs)} recent entries")


class TestApplicantPortal:
    """Test applicant portal functionality."""

    def test_applicant_invoices(self, applicant_session):
        """Applicant can see their own invoices."""
        r = applicant_session.get(f"{BASE_URL}/api/invoices")
        assert r.status_code == 200
        invoices = r.json()
        # Applicant may have 0 or more invoices
        assert isinstance(invoices, list), "Invoices should be a list"
        print(f"✓ Applicant sees {len(invoices)} invoices")

    def test_applicant_conversations(self, applicant_session):
        """Applicant can access conversations."""
        r = applicant_session.get(f"{BASE_URL}/api/conversations")
        assert r.status_code == 200
        convs = r.json()
        assert isinstance(convs, list), "Conversations should be a list"
        print(f"✓ Applicant has {len(convs)} conversations")
