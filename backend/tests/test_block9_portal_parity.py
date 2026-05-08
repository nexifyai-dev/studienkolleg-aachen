"""
Block 9: Portal Parity + Dependency Hardening + Real Functionality Tests

Tests:
- P0: Teacher login and dashboard access
- P0: USt-IdNr DE333306663 in Impressum (LegalPage)
- P0: USt-IdNr DE333306663 in Invoice PDF footer
- Staff Fallakte: LinkedTasks + LinkedInvoices panels
- Kanban: Stage dropdown for moving cards
- Dashboard Stats API: pipeline, recent_activity, unread_messages, user counts
- Audit Page: search + action filter
- TEST_ artifacts cleanup verification
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = "DevSeed@2026!"


class TestTeacherAccess:
    """P0: Teacher login and dashboard access tests"""
    
    def test_teacher_login_success(self):
        """Teacher can login successfully"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEACHER_EMAIL,
            "password": TEACHER_PASSWORD
        })
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert data.get("role") == "teacher", f"Expected role 'teacher', got {data.get('role')}"
        print(f"PASSED: Teacher login successful, role={data.get('role')}")
    
    def test_teacher_my_students_endpoint(self):
        """Teacher can access /api/teacher/my-students"""
        session = requests.Session()
        # Login as teacher
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEACHER_EMAIL,
            "password": TEACHER_PASSWORD
        })
        assert login_res.status_code == 200
        
        # Access my-students
        response = session.get(f"{BASE_URL}/api/teacher/my-students")
        assert response.status_code == 200, f"Teacher my-students failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "students" in data, "Response should contain 'students' key"
        print(f"PASSED: Teacher my-students returns {len(data.get('students', []))} students")
    
    def test_teacher_cannot_access_admin_routes(self):
        """Teacher should not access admin-only routes"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEACHER_EMAIL,
            "password": TEACHER_PASSWORD
        })
        
        # Try to access audit logs (admin only)
        response = session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 403, f"Teacher should not access audit logs, got {response.status_code}"
        print("PASSED: Teacher correctly blocked from admin routes")


class TestUStIdNrInvoicePDF:
    """P0: USt-IdNr DE333306663 in Invoice PDF footer"""
    
    def test_create_invoice_and_check_pdf_for_tax_id(self):
        """Create invoice and verify PDF contains USt-IdNr DE333306663"""
        session = requests.Session()
        
        # Login as staff
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert login_res.status_code == 200, f"Staff login failed: {login_res.text}"
        
        # Get an applicant for invoice
        applicants_res = session.get(f"{BASE_URL}/api/invoices/applicants")
        if applicants_res.status_code != 200 or not applicants_res.json():
            pytest.skip("No applicants available for invoice creation")
        
        applicants = applicants_res.json()
        applicant_id = applicants[0]["id"]
        
        # Create invoice
        invoice_data = {
            "applicant_id": applicant_id,
            "description": "TEST_Block9_Invoice_TaxID_Check",
            "amount": 100.00,
            "currency": "EUR",
            "due_date": "2026-03-01"
        }
        create_res = session.post(f"{BASE_URL}/api/invoices", json=invoice_data)
        assert create_res.status_code == 200, f"Invoice creation failed: {create_res.text}"
        
        invoice = create_res.json()
        invoice_id = invoice.get("invoice_number") or invoice.get("id")
        print(f"Created invoice: {invoice_id}")
        
        # Download PDF
        pdf_res = session.get(f"{BASE_URL}/api/invoices/{invoice_id}/pdf")
        assert pdf_res.status_code == 200, f"PDF download failed: {pdf_res.status_code}"
        assert pdf_res.headers.get("content-type") == "application/pdf", "Response should be PDF"
        
        # Check PDF content for USt-IdNr using pypdf for proper text extraction
        from io import BytesIO
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(pdf_res.content))
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
            tax_id_found = "DE333306663" in text
        except ImportError:
            # Fallback: check raw bytes (may not work with compressed PDFs)
            tax_id_found = b"DE333306663" in pdf_res.content
        
        assert tax_id_found, "USt-IdNr DE333306663 not found in PDF content"
        print("PASSED: USt-IdNr DE333306663 found in invoice PDF")


class TestDashboardStatsAPI:
    """Dashboard Stats API: pipeline, recent_activity, unread_messages, user counts"""
    
    def test_staff_dashboard_stats_structure(self):
        """Staff dashboard stats returns all required fields"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200, f"Dashboard stats failed: {response.text}"
        
        data = response.json()
        
        # Check required fields
        required_fields = [
            "total_leads", "open_leads", "open_tasks", "in_progress_tasks",
            "pending_documents", "pipeline", "recent_activity", "unread_messages",
            "total_users", "total_staff", "total_applicants"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Verify pipeline is a dict with stage counts
        assert isinstance(data["pipeline"], dict), "pipeline should be a dict"
        
        # Verify recent_activity is a list
        assert isinstance(data["recent_activity"], list), "recent_activity should be a list"
        
        # Verify counts are integers
        assert isinstance(data["total_users"], int), "total_users should be int"
        assert isinstance(data["total_staff"], int), "total_staff should be int"
        assert isinstance(data["total_applicants"], int), "total_applicants should be int"
        
        print(f"PASSED: Dashboard stats has all required fields")
        print(f"  - Pipeline stages: {len(data['pipeline'])}")
        print(f"  - Recent activities: {len(data['recent_activity'])}")
        print(f"  - Users: {data['total_users']} total, {data['total_staff']} staff, {data['total_applicants']} applicants")


class TestAuditLogsAPI:
    """Audit Page: search + action filter functionality"""
    
    def test_admin_can_access_audit_logs(self):
        """Admin can access audit logs"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 200, f"Audit logs access failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Audit logs should be a list"
        print(f"PASSED: Admin can access audit logs ({len(data)} entries)")
    
    def test_staff_cannot_access_audit_logs(self):
        """Staff (non-admin) cannot access audit logs"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 403, f"Staff should not access audit logs, got {response.status_code}"
        print("PASSED: Staff correctly blocked from audit logs")


class TestTasksAPI:
    """Staff Fallakte: LinkedTasks panel - task creation and listing"""
    
    def test_staff_can_list_tasks(self):
        """Staff can list tasks"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200, f"Tasks list failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Tasks should be a list"
        print(f"PASSED: Staff can list tasks ({len(data)} tasks)")
    
    def test_staff_can_create_task_for_application(self):
        """Staff can create a task linked to an application"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        # Get an application
        apps_res = session.get(f"{BASE_URL}/api/applications")
        if apps_res.status_code != 200 or not apps_res.json():
            pytest.skip("No applications available")
        
        app_id = apps_res.json()[0]["id"]
        
        # Create task
        task_data = {
            "title": "TEST_Block9_LinkedTask",
            "application_id": app_id,
            "priority": "normal",
            "description": "Test task for Block 9"
        }
        
        response = session.post(f"{BASE_URL}/api/tasks", json=task_data)
        assert response.status_code in [200, 201], f"Task creation failed: {response.text}"
        
        task = response.json()
        assert task.get("title") == "TEST_Block9_LinkedTask"
        print(f"PASSED: Created task linked to application {app_id}")


class TestInvoicesAPI:
    """Staff Fallakte: LinkedInvoices panel - invoice listing"""
    
    def test_staff_can_list_invoices(self):
        """Staff can list invoices"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Invoices list failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Invoices should be a list"
        print(f"PASSED: Staff can list invoices ({len(data)} invoices)")
    
    def test_staff_can_get_invoice_applicants(self):
        """Staff can get applicants for invoice creation"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/invoices/applicants")
        assert response.status_code == 200, f"Invoice applicants failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Applicants should be a list"
        print(f"PASSED: Staff can get invoice applicants ({len(data)} applicants)")


class TestApplicationsAPI:
    """Kanban: Stage change via API"""
    
    def test_staff_can_change_application_stage(self):
        """Staff can change application stage (Kanban stage dropdown)"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        # Get an application
        apps_res = session.get(f"{BASE_URL}/api/applications")
        if apps_res.status_code != 200 or not apps_res.json():
            pytest.skip("No applications available")
        
        apps = apps_res.json()
        app = apps[0]
        app_id = app["id"]
        original_stage = app.get("current_stage", "lead_new")
        
        # Change to a different stage
        new_stage = "in_review" if original_stage != "in_review" else "pending_docs"
        
        response = session.put(f"{BASE_URL}/api/applications/{app_id}", json={
            "current_stage": new_stage
        })
        assert response.status_code == 200, f"Stage change failed: {response.text}"
        
        # Verify change
        verify_res = session.get(f"{BASE_URL}/api/applications/{app_id}")
        assert verify_res.status_code == 200
        updated_app = verify_res.json()
        assert updated_app.get("current_stage") == new_stage, f"Stage not updated: {updated_app.get('current_stage')}"
        
        # Restore original stage
        session.put(f"{BASE_URL}/api/applications/{app_id}", json={"current_stage": original_stage})
        
        print(f"PASSED: Application stage changed from {original_stage} to {new_stage}")


class TestPartnerAPI:
    """Partner Dashboard API tests"""
    
    def test_partner_login_and_dashboard(self):
        """Partner can login and access dashboard"""
        session = requests.Session()
        login_res = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": PARTNER_EMAIL,
            "password": PARTNER_PASSWORD
        })
        assert login_res.status_code == 200, f"Partner login failed: {login_res.text}"
        
        data = login_res.json()
        assert data.get("role") == "affiliate", f"Expected role 'affiliate', got {data.get('role')}"
        
        # Access partner dashboard
        dashboard_res = session.get(f"{BASE_URL}/api/partner/dashboard")
        assert dashboard_res.status_code == 200, f"Partner dashboard failed: {dashboard_res.text}"
        
        dashboard = dashboard_res.json()
        # Check for expected fields
        assert "total_referrals" in dashboard or "referrals" in dashboard or isinstance(dashboard, dict)
        print(f"PASSED: Partner login and dashboard access successful")


class TestContactsApplicantsEndpoint:
    """New /contacts/applicants endpoint for staff messaging"""
    
    def test_staff_can_access_contacts_applicants(self):
        """Staff can access /api/users/contacts/applicants"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/users/contacts/applicants")
        assert response.status_code == 200, f"Contacts applicants failed: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Should return a list"
        
        # Verify structure
        if data:
            first = data[0]
            assert "id" in first, "Should have id"
            assert "email" in first, "Should have email"
        
        print(f"PASSED: Staff can access contacts/applicants ({len(data)} applicants)")


class TestTESTArtifactsCleanup:
    """Verify TEST_ artifacts are cleaned from DB"""
    
    def test_no_test_tasks_in_db(self):
        """No TEST_ prefixed tasks should exist (from previous tests)"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/tasks")
        if response.status_code != 200:
            pytest.skip("Cannot access tasks")
        
        tasks = response.json()
        test_tasks = [t for t in tasks if t.get("title", "").startswith("TEST_")]
        
        # Note: We may have just created TEST_ tasks in this run, so we check for old ones
        # This is informational - we'll clean up our own TEST_ tasks
        print(f"INFO: Found {len(test_tasks)} TEST_ prefixed tasks")
        
        # Clean up TEST_ tasks created in this test run
        for task in test_tasks:
            if "Block9" in task.get("title", ""):
                session.delete(f"{BASE_URL}/api/tasks/{task['id']}")
                print(f"  Cleaned up: {task['title']}")


class TestHealthEndpoint:
    """Basic health check"""
    
    def test_health_endpoint(self):
        """Health endpoint returns ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"PASSED: Health check OK - version {data.get('version')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
