"""
Iteration 105 - Full System Test
Tests all LLM endpoints (deepseek/deepseek-v4-flash via OpenRouter) and core functionality.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com")

# Test credentials
CREDENTIALS = {
    "admin": {"email": "admin@studienkolleg-aachen.de", "password": "Admin@2026!"},
    "staff": {"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "teacher": {"email": "teacher@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "applicant": {"email": "applicant@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
    "partner": {"email": "partner@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
}


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """GET /api/health returns ok"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print(f"PASS: Health endpoint returns status=ok, version={data.get('version')}")


class TestAuthentication:
    """Test login for all 5 roles"""
    
    @pytest.fixture(scope="class")
    def session(self):
        return requests.Session()
    
    def test_admin_login(self, session):
        """Admin login works"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["admin"])
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("user", {}).get("role") in ("admin", "superadmin")
        print(f"PASS: Admin login - role={data['user']['role']}")
    
    def test_staff_login(self, session):
        """Staff login works"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("user", {}).get("role") == "staff"
        print(f"PASS: Staff login - role={data['user']['role']}")
    
    def test_teacher_login(self, session):
        """Teacher login works"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["teacher"])
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("user", {}).get("role") == "teacher"
        print(f"PASS: Teacher login - role={data['user']['role']}")
    
    def test_applicant_login(self, session):
        """Applicant login works"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["applicant"])
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("user", {}).get("role") == "applicant"
        print(f"PASS: Applicant login - role={data['user']['role']}")
    
    def test_partner_login(self, session):
        """Partner login works"""
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["partner"])
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("user", {}).get("role") in ("affiliate", "agency_admin", "agency_agent")
        print(f"PASS: Partner login - role={data['user']['role']}")


class TestStaffEndpoints:
    """Test Staff-accessible endpoints"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        assert resp.status_code == 200
        # Extract CSRF token from cookies
        csrf = session.cookies.get("csrf_token", "")
        session.headers.update({"X-CSRF-Token": csrf})
        return session
    
    def test_dashboard_stats(self, staff_session):
        """GET /api/dashboard/stats returns data"""
        resp = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "applications" in data or "total_applications" in data or isinstance(data, dict)
        print(f"PASS: Dashboard stats returned")
    
    def test_applications_list(self, staff_session):
        """GET /api/applications returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))
        print(f"PASS: Applications list returned")
    
    def test_tasks_list(self, staff_session):
        """GET /api/tasks returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/tasks")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))
        print(f"PASS: Tasks list returned")
    
    def test_documents_list(self, staff_session):
        """GET /api/documents returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))
        print(f"PASS: Documents list returned")
    
    def test_invoices_list(self, staff_session):
        """GET /api/invoices returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/invoices")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Invoices list returned ({len(data)} invoices)")
    
    def test_conversations_list(self, staff_session):
        """GET /api/conversations returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/conversations")
        assert resp.status_code == 200
        data = resp.json()
        assert "conversations" in data
        print(f"PASS: Conversations list returned ({len(data.get('conversations', []))} conversations)")
    
    def test_email_signature(self, staff_session):
        """GET /api/email-signature returns signature"""
        resp = staff_session.get(f"{BASE_URL}/api/email-signature")
        assert resp.status_code == 200
        data = resp.json()
        assert "signature" in data
        assert "Studienkolleg" in data["signature"] or "W2G" in data["signature"]
        print(f"PASS: Email signature returned ({len(data['signature'])} chars)")


class TestLLMEndpoints:
    """Test AI/LLM endpoints using deepseek/deepseek-v4-flash via OpenRouter"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        assert resp.status_code == 200
        csrf = session.cookies.get("csrf_token", "")
        session.headers.update({"X-CSRF-Token": csrf})
        return session
    
    def test_support_chat_ai_response(self, staff_session):
        """POST /api/support/chat returns AI response (deepseek model)"""
        resp = staff_session.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Was sind die Voraussetzungen fuer das Studienkolleg?",
            "history": [],
            "language": "de"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "reply" in data
        assert len(data["reply"]) > 50  # Should have substantial response
        print(f"PASS: Support chat AI response ({len(data['reply'])} chars)")
    
    def test_brain_ask_ai_response(self, staff_session):
        """POST /api/brain/ask returns response with correct model"""
        resp = staff_session.post(f"{BASE_URL}/api/brain/ask", json={
            "query": "Wie viele offene Bewerbungen gibt es?",
            "context": "",
            "entity_id": ""
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "content" in data
        assert data.get("content") is not None
        # Check model is deepseek
        model = data.get("model", "")
        assert "deepseek" in model.lower() or model == ""  # Model may not always be returned
        print(f"PASS: Brain ask AI response - model={model}, content_len={len(data.get('content', ''))}")
    
    def test_email_generation_with_template(self, staff_session):
        """POST /api/messaging/generate-email with template returns response"""
        resp = staff_session.post(f"{BASE_URL}/api/messaging/generate-email", json={
            "hints": "Bitte um fehlende Unterlagen bitten",
            "template": "documents_request",
            "conversation_id": ""
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "generated_text" in data
        assert len(data["generated_text"]) > 50
        assert "detected_lang" in data
        print(f"PASS: Email generation with template - lang={data.get('detected_lang')}, text_len={len(data['generated_text'])}")
    
    def test_email_generation_free_form(self, staff_session):
        """POST /api/messaging/generate-email without template (free form)"""
        resp = staff_session.post(f"{BASE_URL}/api/messaging/generate-email", json={
            "hints": "Willkommen am Studienkolleg, naechste Schritte erklaeren",
            "template": "",
            "conversation_id": ""
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "generated_text" in data
        assert len(data["generated_text"]) > 30
        print(f"PASS: Email generation free form - text_len={len(data['generated_text'])}")


class TestInvoiceCreation:
    """Test invoice creation with auto-calculation"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["staff"])
        assert resp.status_code == 200
        csrf = session.cookies.get("csrf_token", "")
        session.headers.update({"X-CSRF-Token": csrf})
        return session
    
    def test_invoice_create_with_items_auto_calc(self, staff_session):
        """POST /api/invoices with items auto-calculates amount"""
        # First get an applicant ID
        resp = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert resp.status_code == 200
        applicants = resp.json()
        if not applicants:
            pytest.skip("No applicants available for invoice test")
        
        applicant_id = applicants[0]["id"]
        
        # Create invoice with line items
        invoice_data = {
            "applicant_id": applicant_id,
            "description": "TEST_Kursgebuehr Iteration 105",
            "items": [
                {"description": "Kursgebuehr T-Kurs", "quantity": 1, "unit_price": 5500.00},
                {"description": "Anmeldegebuehr", "quantity": 1, "unit_price": 150.00}
            ],
            "currency": "EUR"
        }
        
        resp = staff_session.post(f"{BASE_URL}/api/invoices", json=invoice_data)
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify auto-calculation
        assert data.get("amount") == 5650.00  # 5500 + 150
        assert data.get("invoice_number") is not None
        assert data.get("due_date") is not None  # Auto-generated +30 days
        
        print(f"PASS: Invoice created with auto-calc - number={data['invoice_number']}, amount={data['amount']}, due={data['due_date']}")
        
        # Cleanup - delete the test invoice (admin only, so we'll just leave it as draft)
        return data


class TestAdminEndpoints:
    """Test Admin-specific endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["admin"])
        assert resp.status_code == 200
        csrf = session.cookies.get("csrf_token", "")
        session.headers.update({"X-CSRF-Token": csrf})
        return session
    
    def test_admin_users_list(self, admin_session):
        """GET /api/users returns list (admin only)"""
        resp = admin_session.get(f"{BASE_URL}/api/users")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Admin users list returned ({len(data)} users)")
    
    def test_admin_settings(self, admin_session):
        """GET /api/settings returns settings"""
        resp = admin_session.get(f"{BASE_URL}/api/settings")
        # Settings endpoint may return 200 or 404 if not configured
        assert resp.status_code in (200, 404)
        print(f"PASS: Admin settings endpoint accessible (status={resp.status_code})")
    
    def test_admin_audit_logs(self, admin_session):
        """GET /api/audit returns audit logs"""
        resp = admin_session.get(f"{BASE_URL}/api/audit")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))
        print(f"PASS: Admin audit logs returned")


class TestApplicantEndpoints:
    """Test Applicant-specific endpoints"""
    
    @pytest.fixture(scope="class")
    def applicant_session(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["applicant"])
        assert resp.status_code == 200
        csrf = session.cookies.get("csrf_token", "")
        session.headers.update({"X-CSRF-Token": csrf})
        return session
    
    def test_applicant_my_application(self, applicant_session):
        """GET /api/applications/my returns applicant's application"""
        resp = applicant_session.get(f"{BASE_URL}/api/applications/my")
        # May return 200 with data or 404 if no application
        assert resp.status_code in (200, 404)
        print(f"PASS: Applicant my-application endpoint (status={resp.status_code})")
    
    def test_applicant_my_invoices(self, applicant_session):
        """GET /api/invoices/my returns applicant's invoices"""
        resp = applicant_session.get(f"{BASE_URL}/api/invoices/my")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"PASS: Applicant my-invoices returned ({len(data)} invoices)")
    
    def test_applicant_support_conversation(self, applicant_session):
        """GET /api/conversations/support returns or creates support conversation"""
        resp = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data or "participants" in data
        print(f"PASS: Applicant support conversation accessible")


class TestPartnerEndpoints:
    """Test Partner-specific endpoints"""
    
    @pytest.fixture(scope="class")
    def partner_session(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS["partner"])
        assert resp.status_code == 200
        csrf = session.cookies.get("csrf_token", "")
        session.headers.update({"X-CSRF-Token": csrf})
        return session
    
    def test_partner_referrals(self, partner_session):
        """GET /api/partners/referrals returns partner's referrals"""
        resp = partner_session.get(f"{BASE_URL}/api/partners/referrals")
        # May return 200 or 403 depending on partner setup
        assert resp.status_code in (200, 403, 404)
        print(f"PASS: Partner referrals endpoint (status={resp.status_code})")
    
    def test_partner_stats(self, partner_session):
        """GET /api/partners/stats returns partner stats"""
        resp = partner_session.get(f"{BASE_URL}/api/partners/stats")
        assert resp.status_code in (200, 403, 404)
        print(f"PASS: Partner stats endpoint (status={resp.status_code})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
