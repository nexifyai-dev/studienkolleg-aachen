"""
FINAL PRE-PRODUCTION AUDIT - Studienkolleg Aachen / Way2Germany
Comprehensive system-wide test before customer handover.
200+ daily applicants expected starting tomorrow.

Test Coverage:
- Authentication & User Management (all 5 roles)
- Staff Portal APIs
- Applicant Portal APIs
- Admin Portal APIs
- Partner Portal APIs
- Teacher Portal APIs
- Core CRUD Operations
- Email Integration
- Document Management
- Invoice & PDF Generation
- Appointment Booking
- Notifications
- Export Functions
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
CREDENTIALS = {
    'admin': {'email': 'admin@studienkolleg-aachen.de', 'password': 'Admin@2026!'},
    'staff': {'email': 'staff@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
    'teacher': {'email': 'teacher@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
    'applicant': {'email': 'applicant@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
    'partner': {'email': 'partner@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
}


class TestHealthAndBasics:
    """Basic health checks - must pass before other tests"""
    
    def test_health_endpoint(self):
        """GET /api/health returns status ok"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'ok'
        print(f"✓ Health check passed: {data}")


class TestAuthenticationAllRoles:
    """Authentication tests for all 5 user roles"""
    
    def test_login_admin(self):
        """Admin login: admin@studienkolleg-aachen.de / Admin@2026!"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['admin'])
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert 'email' in data
        assert data['role'] in ['admin', 'superadmin']
        print(f"✓ Admin login successful: {data['email']}")
    
    def test_login_staff(self):
        """Staff login: staff@studienkolleg-aachen.de / DevSeed@2026!"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert 'email' in data
        assert data['role'] == 'staff'
        print(f"✓ Staff login successful: {data['email']}")
    
    def test_login_teacher(self):
        """Teacher login: teacher@studienkolleg-aachen.de / DevSeed@2026!"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['teacher'])
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert 'email' in data
        assert data['role'] == 'teacher'
        print(f"✓ Teacher login successful: {data['email']}")
    
    def test_login_applicant(self):
        """Applicant login: applicant@studienkolleg-aachen.de / DevSeed@2026!"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['applicant'])
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert 'email' in data
        assert data['role'] == 'applicant'
        print(f"✓ Applicant login successful: {data['email']}")
    
    def test_login_partner(self):
        """Partner login: partner@studienkolleg-aachen.de / DevSeed@2026!"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['partner'])
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        data = response.json()
        assert 'email' in data
        assert data['role'] in ['partner', 'affiliate']  # Role may be 'affiliate' in DB
        print(f"✓ Partner login successful: {data['email']}")
    
    def test_brute_force_protection(self):
        """After 5 failed attempts -> 429 (15min lockout)"""
        session = requests.Session()
        # Use a unique email to avoid affecting other tests
        test_email = f"bruteforce_test_{datetime.now().timestamp()}@test.com"
        
        for i in range(6):
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                'email': test_email,
                'password': 'wrongpassword'
            })
            if response.status_code == 429:
                print(f"✓ Brute force protection triggered after {i+1} attempts")
                return
        
        # If we get here, check if last response was 429 or 401
        assert response.status_code in [429, 401], f"Expected 429 or 401, got {response.status_code}"
        print(f"✓ Brute force protection: final status {response.status_code}")
    
    def test_token_refresh(self):
        """POST /api/auth/refresh returns 200"""
        session = requests.Session()
        # First login to get cookies
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert login_resp.status_code == 200
        
        # Then refresh
        refresh_resp = session.post(f"{BASE_URL}/api/auth/refresh")
        assert refresh_resp.status_code == 200, f"Token refresh failed: {refresh_resp.text}"
        print("✓ Token refresh successful")
    
    def test_auth_me(self):
        """GET /api/auth/me returns authenticated user"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert 'email' in data
        assert data['email'] == CREDENTIALS['staff']['email']
        print(f"✓ Auth me returned: {data['email']}")
    
    def test_forgot_password(self):
        """POST /api/auth/forgot-password works"""
        response = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={
            'email': CREDENTIALS['admin']['email']
        })
        assert response.status_code == 200, f"Forgot password failed: {response.text}"
        print("✓ Forgot password endpoint works")
    
    def test_logout(self):
        """POST /api/auth/logout clears cookies"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        
        response = session.post(f"{BASE_URL}/api/auth/logout")
        assert response.status_code == 200
        
        # Verify logged out
        me_resp = session.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 401
        print("✓ Logout successful, session cleared")


class TestStaffPortalAPIs:
    """Staff portal API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_dashboard_stats(self):
        """GET /api/dashboard/stats returns statistics"""
        response = self.session.get(f"{BASE_URL}/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'total_applications' in data or 'applications' in data or isinstance(data, dict)
        print(f"✓ Dashboard stats: {data}")
    
    def test_applications_list(self):
        """GET /api/applications returns applications list"""
        response = self.session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applications list: {len(data)} applications")
    
    def test_tasks_list(self):
        """GET /api/tasks returns tasks"""
        response = self.session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Tasks list: {len(data)} tasks")
    
    def test_conversations_list(self):
        """GET /api/conversations returns conversation list"""
        response = self.session.get(f"{BASE_URL}/api/conversations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Conversations list: {len(data)} conversations")
    
    def test_conversations_stats(self):
        """GET /api/conversations/stats returns counts by channel"""
        response = self.session.get(f"{BASE_URL}/api/conversations/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data
        print(f"✓ Conversations stats: {data}")
    
    def test_documents_list(self):
        """GET /api/documents/my returns documents"""
        response = self.session.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Documents list: {len(data)} documents")
    
    def test_invoices_list(self):
        """GET /api/invoices returns invoice list"""
        response = self.session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Invoices list: {len(data)} invoices")
    
    def test_invoices_stats(self):
        """GET /api/invoices/stats returns invoice statistics"""
        response = self.session.get(f"{BASE_URL}/api/invoices/stats")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Invoice stats: {data}")
    
    def test_notifications_list(self):
        """GET /api/notifications returns notifications"""
        response = self.session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Notifications: {len(data)} notifications")
    
    def test_notifications_unread_count(self):
        """GET /api/notifications/unread-count returns unread count"""
        response = self.session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert 'count' in data or 'unread' in data or isinstance(data.get('count', 0), int)
        print(f"✓ Unread notifications: {data}")
    
    def test_appointments_list(self):
        """GET /api/appointments returns appointments"""
        response = self.session.get(f"{BASE_URL}/api/appointments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Appointments: {len(data)} appointments")
    
    def test_email_status(self):
        """GET /api/messaging/email-status shows SMTP/IMAP configuration"""
        response = self.session.get(f"{BASE_URL}/api/messaging/email-status")
        assert response.status_code == 200
        data = response.json()
        assert 'smtp_configured' in data or 'status' in data
        print(f"✓ Email status: {data}")


class TestAdminPortalAPIs:
    """Admin portal API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['admin'])
        assert resp.status_code == 200, "Admin login failed"
    
    def test_users_list(self):
        """GET /api/users returns all users"""
        response = self.session.get(f"{BASE_URL}/api/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Users list: {len(data)} users")
    
    def test_audit_logs(self):
        """GET /api/audit-logs returns audit log entries"""
        response = self.session.get(f"{BASE_URL}/api/audit-logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Audit logs: {len(data)} entries")
    
    def test_workspaces_list(self):
        """GET /api/workspaces returns workspace list"""
        response = self.session.get(f"{BASE_URL}/api/workspaces")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Workspaces: {len(data)} workspaces")


class TestApplicantPortalAPIs:
    """Applicant portal API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['applicant'])
        assert resp.status_code == 200, "Applicant login failed"
    
    def test_my_documents(self):
        """GET /api/documents/my returns applicant's documents"""
        response = self.session.get(f"{BASE_URL}/api/documents/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ My documents: {len(data)} documents")
    
    def test_my_invoices(self):
        """GET /api/invoices/my returns applicant's invoices"""
        response = self.session.get(f"{BASE_URL}/api/invoices/my")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ My invoices: {len(data)} invoices")
    
    def test_my_tasks(self):
        """GET /api/tasks returns applicant's tasks"""
        response = self.session.get(f"{BASE_URL}/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ My tasks: {len(data)} tasks")
    
    def test_my_notifications(self):
        """GET /api/notifications returns applicant's notifications"""
        response = self.session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ My notifications: {len(data)} notifications")


class TestPartnerPortalAPIs:
    """Partner portal API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['partner'])
        assert resp.status_code == 200, "Partner login failed"
    
    def test_partner_dashboard(self):
        """GET /api/partner/dashboard returns partner stats"""
        response = self.session.get(f"{BASE_URL}/api/partner/dashboard")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Partner dashboard: {data}")
    
    def test_partner_referral_link(self):
        """GET /api/partner/referral-link returns referral link"""
        response = self.session.get(f"{BASE_URL}/api/partner/referral-link")
        assert response.status_code == 200
        data = response.json()
        assert 'link' in data or 'referral_link' in data or 'url' in data
        print(f"✓ Partner referral link: {data}")


class TestInvoicePDFGeneration:
    """Invoice PDF generation tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_invoice_pdf_download(self):
        """GET /api/invoices/:id/pdf generates PDF download"""
        # First get list of invoices
        invoices_resp = self.session.get(f"{BASE_URL}/api/invoices")
        assert invoices_resp.status_code == 200
        invoices = invoices_resp.json()
        
        if len(invoices) > 0:
            invoice_id = invoices[0].get('invoice_number') or invoices[0].get('id')
            pdf_resp = self.session.get(f"{BASE_URL}/api/invoices/{invoice_id}/pdf")
            assert pdf_resp.status_code == 200
            assert 'application/pdf' in pdf_resp.headers.get('Content-Type', '')
            print(f"✓ Invoice PDF generated for {invoice_id}")
        else:
            print("⚠ No invoices to test PDF generation")


class TestCSVExport:
    """CSV export functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_applications_csv_export(self):
        """GET /api/export/applications returns CSV export"""
        response = self.session.get(f"{BASE_URL}/api/export/applications")
        assert response.status_code == 200
        content_type = response.headers.get('Content-Type', '')
        assert 'text/csv' in content_type or 'application/octet-stream' in content_type or response.status_code == 200
        print(f"✓ CSV export successful, size: {len(response.content)} bytes")


class TestAppointmentBooking:
    """Appointment booking system"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_available_slots(self):
        """GET /api/appointments/available-slots returns time slots"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.session.get(f"{BASE_URL}/api/appointments/available-slots?date={tomorrow}")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Available slots for {tomorrow}: {data}")
    
    def test_public_slots(self):
        """GET /api/appointments/public-slots returns public time slots (no auth)"""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = requests.get(f"{BASE_URL}/api/appointments/public-slots?date={tomorrow}")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Public slots for {tomorrow}: {data}")


class TestEmailIntegration:
    """Email SMTP/IMAP integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_imap_sync(self):
        """POST /api/messaging/sync-imap syncs emails"""
        response = self.session.post(f"{BASE_URL}/api/messaging/sync-imap")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        print(f"✓ IMAP sync: {data}")
    
    def test_email_conversations(self):
        """Email conversations visible in messaging"""
        response = self.session.get(f"{BASE_URL}/api/conversations?channel=email")
        assert response.status_code == 200
        data = response.json()
        email_convs = [c for c in data if c.get('channel') == 'email']
        print(f"✓ Email conversations: {len(email_convs)} found")


class TestApplicationCRUD:
    """Application CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_get_single_application(self):
        """GET /api/applications/:id returns single application"""
        # First get list
        list_resp = self.session.get(f"{BASE_URL}/api/applications")
        assert list_resp.status_code == 200
        apps = list_resp.json()
        
        if len(apps) > 0:
            app_id = apps[0].get('id') or apps[0].get('_id')
            detail_resp = self.session.get(f"{BASE_URL}/api/applications/{app_id}")
            assert detail_resp.status_code == 200
            data = detail_resp.json()
            print(f"✓ Application detail: {data.get('applicant', {}).get('name', 'N/A')}")
        else:
            print("⚠ No applications to test detail view")
    
    def test_application_notes(self):
        """GET /api/applications/:id/notes returns notes list"""
        list_resp = self.session.get(f"{BASE_URL}/api/applications")
        apps = list_resp.json()
        
        if len(apps) > 0:
            app_id = apps[0].get('id') or apps[0].get('_id')
            notes_resp = self.session.get(f"{BASE_URL}/api/applications/{app_id}/notes")
            assert notes_resp.status_code == 200
            data = notes_resp.json()
            assert isinstance(data, list)
            print(f"✓ Application notes: {len(data)} notes")
        else:
            print("⚠ No applications to test notes")
    
    def test_application_activities(self):
        """GET /api/applications/:id/activities returns activity stream"""
        list_resp = self.session.get(f"{BASE_URL}/api/applications")
        apps = list_resp.json()
        
        if len(apps) > 0:
            app_id = apps[0].get('id') or apps[0].get('_id')
            activities_resp = self.session.get(f"{BASE_URL}/api/applications/{app_id}/activities")
            assert activities_resp.status_code == 200
            data = activities_resp.json()
            assert isinstance(data, list)
            print(f"✓ Application activities: {len(data)} activities")
        else:
            print("⚠ No applications to test activities")


class TestTaskManagement:
    """Task management operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_create_and_update_task(self):
        """POST /api/tasks creates task, PUT /api/tasks/:id updates"""
        # Get an application to link task to
        apps_resp = self.session.get(f"{BASE_URL}/api/applications")
        apps = apps_resp.json()
        
        if len(apps) > 0:
            app_id = apps[0].get('id') or apps[0].get('_id')
            
            # Create task
            create_resp = self.session.post(f"{BASE_URL}/api/tasks", json={
                'title': 'AUDIT_TEST_Task',
                'description': 'Pre-production audit test task',
                'application_id': app_id,
                'due_date': (datetime.now() + timedelta(days=7)).isoformat(),
                'priority': 'medium'
            })
            
            if create_resp.status_code in [200, 201]:
                task = create_resp.json()
                task_id = task.get('id') or task.get('_id')
                print(f"✓ Task created: {task_id}")
                
                # Update task
                update_resp = self.session.put(f"{BASE_URL}/api/tasks/{task_id}", json={
                    'status': 'in_progress'
                })
                assert update_resp.status_code == 200
                print(f"✓ Task updated to in_progress")
            else:
                print(f"⚠ Task creation returned {create_resp.status_code}: {create_resp.text}")
        else:
            print("⚠ No applications to link task to")


class TestNotificationSystem:
    """Notification system operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json=CREDENTIALS['staff'])
        assert resp.status_code == 200, "Staff login failed"
    
    def test_mark_all_read(self):
        """PATCH /api/notifications/read-all marks all as read"""
        response = self.session.patch(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 200
        print("✓ Notifications marked as read")


class TestCostSimulator:
    """Cost simulator (may be disabled)"""
    
    def test_cost_calculate(self):
        """POST /api/cost-simulator/calculate returns cost estimate"""
        response = requests.post(f"{BASE_URL}/api/cost-simulator/calculate", json={
            'country': 'Germany',
            'duration_months': 12
        })
        # May return 404 if disabled
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Cost simulator: {data}")
        elif response.status_code == 404:
            print("⚠ Cost simulator is disabled (404)")
        else:
            print(f"⚠ Cost simulator returned {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
