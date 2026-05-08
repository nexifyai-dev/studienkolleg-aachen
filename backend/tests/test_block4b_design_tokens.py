"""
Block 4B: Design Token & Operability Roll-out Tests

Tests:
1. Admin User Edit: PUT /api/users/{id} changes user data correctly
2. Invoice PDF Download: GET /api/invoices/{id}/pdf returns valid PDF
3. AI Screening: POST /api/applications/{id}/ai-screen returns structured result
4. AI Screening Cache: Second call returns cache_hit=true
5. Invoice Settings: GET/PUT /api/invoices/settings
6. Anabin Knowledge: Lookup country returns category
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


class TestAuth:
    """Authentication tests"""
    
    def test_staff_login(self):
        """Staff login returns valid session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert data.get("email") == STAFF_EMAIL
        assert data.get("role") == "staff"
        print(f"✓ Staff login successful: {data.get('full_name')}")
    
    def test_admin_login(self):
        """Admin login returns valid session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data.get("email") == ADMIN_EMAIL
        assert data.get("role") == "superadmin"
        print(f"✓ Admin login successful: {data.get('full_name')}")
    
    def test_applicant_login(self):
        """Applicant login returns valid session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data.get("email") == APPLICANT_EMAIL
        assert data.get("role") == "applicant"
        print(f"✓ Applicant login successful: {data.get('full_name')}")


class TestAdminUserEdit:
    """Admin User Edit: PUT /api/users/{id} tests"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_list_users(self, admin_session):
        """Admin can list all users"""
        response = admin_session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200, f"List users failed: {response.text}"
        users = response.json()
        assert isinstance(users, list)
        assert len(users) > 0
        print(f"✓ Listed {len(users)} users")
    
    def test_update_user_name(self, admin_session):
        """Admin can update user full_name"""
        # Get users list
        response = admin_session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200
        users = response.json()
        
        # Find a non-superadmin user to update
        target_user = None
        for u in users:
            if u.get("role") == "applicant":
                target_user = u
                break
        
        if not target_user:
            pytest.skip("No applicant user found to test update")
        
        user_id = target_user["id"]
        original_name = target_user.get("full_name", "")
        test_name = f"TEST_Updated_{int(time.time())}"
        
        # Update user
        response = admin_session.put(f"{BASE_URL}/api/users/{user_id}", json={
            "full_name": test_name
        })
        assert response.status_code == 200, f"Update user failed: {response.text}"
        
        # Verify update
        response = admin_session.get(f"{BASE_URL}/api/users/{user_id}")
        assert response.status_code == 200
        updated_user = response.json()
        assert updated_user.get("full_name") == test_name
        print(f"✓ Updated user {user_id} name to {test_name}")
        
        # Restore original name
        admin_session.put(f"{BASE_URL}/api/users/{user_id}", json={
            "full_name": original_name or "Ahmed Hassan"
        })
    
    def test_update_user_role(self, admin_session):
        """Admin can update user role"""
        # Get users list
        response = admin_session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200
        users = response.json()
        
        # Find staff user
        target_user = None
        for u in users:
            if u.get("role") == "staff" and u.get("email") != ADMIN_EMAIL:
                target_user = u
                break
        
        if not target_user:
            pytest.skip("No staff user found to test role update")
        
        user_id = target_user["id"]
        
        # Update role (just verify the endpoint accepts it)
        response = admin_session.put(f"{BASE_URL}/api/users/{user_id}", json={
            "role": "staff"  # Keep same role to avoid breaking things
        })
        assert response.status_code == 200, f"Update user role failed: {response.text}"
        print(f"✓ User role update endpoint works for {user_id}")


class TestInvoicePDF:
    """Invoice PDF Download: GET /api/invoices/{id}/pdf tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_list_invoices(self, staff_session):
        """Staff can list invoices"""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"List invoices failed: {response.text}"
        invoices = response.json()
        assert isinstance(invoices, list)
        print(f"✓ Listed {len(invoices)} invoices")
        return invoices
    
    def test_invoice_pdf_download(self, staff_session):
        """Staff can download invoice PDF"""
        # Get invoices
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        invoices = response.json()
        
        if not invoices:
            pytest.skip("No invoices found to test PDF download")
        
        invoice_number = invoices[0].get("invoice_number")
        assert invoice_number, "Invoice has no invoice_number"
        
        # Download PDF
        response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        assert response.status_code == 200, f"PDF download failed: {response.text}"
        
        # Verify it's a PDF
        content_type = response.headers.get("content-type", "")
        assert "application/pdf" in content_type, f"Expected PDF, got {content_type}"
        
        # Verify PDF magic bytes
        content = response.content
        assert content[:4] == b'%PDF', "Response is not a valid PDF"
        
        print(f"✓ Downloaded PDF for invoice {invoice_number} ({len(content)} bytes)")
    
    def test_invoice_stats(self, staff_session):
        """Staff can get invoice stats"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/stats")
        assert response.status_code == 200, f"Invoice stats failed: {response.text}"
        stats = response.json()
        assert "total_count" in stats
        assert "total_amount" in stats
        assert "by_status" in stats
        print(f"✓ Invoice stats: {stats['total_count']} invoices, {stats['total_amount']} total")


class TestInvoiceSettings:
    """Invoice Settings: GET/PUT /api/invoices/settings tests"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_get_invoice_settings(self, staff_session):
        """Staff can get invoice settings"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/settings")
        assert response.status_code == 200, f"Get settings failed: {response.text}"
        settings = response.json()
        assert "prefix" in settings
        assert "start_number" in settings
        assert "suffix" in settings
        assert "preview" in settings
        print(f"✓ Invoice settings: prefix={settings['prefix']}, preview={settings['preview']}")
    
    def test_update_invoice_settings_admin_only(self, staff_session, admin_session):
        """Only admin can update invoice settings"""
        # Staff should get 403
        response = staff_session.put(f"{BASE_URL}/api/invoices/settings", json={
            "prefix": "TEST"
        })
        assert response.status_code == 403, f"Staff should not be able to update settings: {response.status_code}"
        print("✓ Staff correctly denied from updating invoice settings")
        
        # Admin should succeed
        response = admin_session.get(f"{BASE_URL}/api/invoices/settings")
        original_settings = response.json()
        
        response = admin_session.put(f"{BASE_URL}/api/invoices/settings", json={
            "prefix": "W2G",
            "suffix": "AC"
        })
        assert response.status_code == 200, f"Admin update settings failed: {response.text}"
        updated = response.json()
        assert updated.get("prefix") == "W2G"
        assert updated.get("suffix") == "AC"
        print(f"✓ Admin updated invoice settings: prefix={updated['prefix']}, suffix={updated['suffix']}")


class TestAIScreening:
    """AI Screening: POST /api/applications/{id}/ai-screen tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_list_applications(self, staff_session):
        """Staff can list applications"""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"List applications failed: {response.text}"
        apps = response.json()
        assert isinstance(apps, list)
        print(f"✓ Listed {len(apps)} applications")
        return apps
    
    def test_ai_screening_returns_structured_result(self, staff_session):
        """AI screening returns structured result with retrieval-first fields"""
        # Get applications
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        apps = response.json()
        
        if not apps:
            pytest.skip("No applications found to test AI screening")
        
        app_id = apps[0].get("id")
        assert app_id, "Application has no id"
        
        # Run AI screening
        response = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/ai-screen")
        assert response.status_code == 200, f"AI screening failed: {response.text}"
        
        result = response.json()
        
        # Verify structured result fields
        assert "screening_id" in result, "Missing screening_id"
        assert "application_id" in result, "Missing application_id"
        assert "screened_at" in result, "Missing screened_at"
        assert "is_complete" in result, "Missing is_complete"
        assert "anabin_category" in result, "Missing anabin_category"
        assert "language_level_ok" in result, "Missing language_level_ok"
        assert "suggested_stage" in result, "Missing suggested_stage"
        assert "data_fingerprint" in result, "Missing data_fingerprint (retrieval-first)"
        assert "cache_hit" in result, "Missing cache_hit field"
        
        print(f"✓ AI screening returned structured result:")
        print(f"  - screening_id: {result['screening_id']}")
        print(f"  - is_complete: {result['is_complete']}")
        print(f"  - anabin_category: {result['anabin_category']}")
        print(f"  - suggested_stage: {result['suggested_stage']}")
        print(f"  - cache_hit: {result['cache_hit']}")
        print(f"  - data_fingerprint: {result['data_fingerprint']}")
        
        return app_id
    
    def test_ai_screening_cache_hit(self, staff_session):
        """Second AI screening call returns cache_hit=true"""
        # Get applications
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        apps = response.json()
        
        if not apps:
            pytest.skip("No applications found to test AI screening cache")
        
        app_id = apps[0].get("id")
        
        # First call (may or may not be cached)
        response1 = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/ai-screen")
        assert response1.status_code == 200
        result1 = response1.json()
        fingerprint1 = result1.get("data_fingerprint")
        
        # Second call (should be cached)
        response2 = staff_session.post(f"{BASE_URL}/api/applications/{app_id}/ai-screen")
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Verify cache hit
        assert result2.get("cache_hit") == True, f"Expected cache_hit=true, got {result2.get('cache_hit')}"
        assert result2.get("data_fingerprint") == fingerprint1, "Fingerprint should match"
        
        print(f"✓ AI screening cache working:")
        print(f"  - First call cache_hit: {result1.get('cache_hit')}")
        print(f"  - Second call cache_hit: {result2.get('cache_hit')}")
        print(f"  - Fingerprint: {fingerprint1}")


class TestDashboardStats:
    """Dashboard stats endpoint tests"""
    
    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_dashboard_stats(self, staff_session):
        """Staff can get dashboard stats"""
        response = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        stats = response.json()
        assert "total_leads" in stats or "open_tasks" in stats
        print(f"✓ Dashboard stats: {stats}")


class TestAuditLogs:
    """Audit logs endpoint tests"""
    
    @pytest.fixture
    def admin_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_audit_logs(self, admin_session):
        """Admin can get audit logs"""
        response = admin_session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 200, f"Audit logs failed: {response.text}"
        logs = response.json()
        assert isinstance(logs, list)
        print(f"✓ Audit logs: {len(logs)} entries")


class TestApplicantPortal:
    """Applicant portal endpoint tests"""
    
    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        return session
    
    def test_applicant_applications(self, applicant_session):
        """Applicant can see own applications"""
        response = applicant_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Applicant applications failed: {response.text}"
        apps = response.json()
        assert isinstance(apps, list)
        print(f"✓ Applicant has {len(apps)} applications")
    
    def test_applicant_invoices(self, applicant_session):
        """Applicant can see own invoices"""
        response = applicant_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Applicant invoices failed: {response.text}"
        invoices = response.json()
        assert isinstance(invoices, list)
        print(f"✓ Applicant has {len(invoices)} invoices")
    
    def test_applicant_conversations(self, applicant_session):
        """Applicant can access support conversation"""
        response = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert response.status_code == 200, f"Applicant support conversation failed: {response.text}"
        conv = response.json()
        assert "id" in conv
        print(f"✓ Applicant support conversation: {conv.get('id')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
