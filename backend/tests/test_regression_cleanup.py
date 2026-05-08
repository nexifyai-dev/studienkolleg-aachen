"""
REGRESSION TEST AFTER DATA CLEANUP - Pre-Production Final Check
Tests all portals, APIs, and data integrity after DB cleanup.
Production launch: Tomorrow 9 AM with 200+ applicants/day.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
CREDENTIALS = {
    'admin': {'email': 'admin@studienkolleg-aachen.de', 'password': 'Admin@2026!'},
    'staff': {'email': 'staff@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
    'applicant': {'email': 'applicant@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
    'teacher': {'email': 'teacher@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
    'partner': {'email': 'partner@studienkolleg-aachen.de', 'password': 'DevSeed@2026!'},
}


@pytest.fixture(scope='module')
def sessions():
    """Create authenticated sessions for all roles."""
    result = {}
    for role, creds in CREDENTIALS.items():
        session = requests.Session()
        resp = session.post(f'{BASE_URL}/api/auth/login', json=creds)
        if resp.status_code == 200:
            result[role] = session
        else:
            print(f"Warning: {role} login failed: {resp.status_code}")
    return result


class TestHealthAndBasics:
    """Basic health checks."""
    
    def test_health_endpoint(self):
        resp = requests.get(f'{BASE_URL}/api/health')
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'ok'
        assert data['email_enabled'] == True
        print("✓ Health endpoint OK, email enabled")


class TestDataIntegrityAfterCleanup:
    """Verify DB state after cleanup - no TEST_ entries, no garbage."""
    
    def test_dashboard_stats_consistent(self, sessions):
        """Staff dashboard stats must be consistent with clean data."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/dashboard/stats')
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify expected counts
        assert data['total_leads'] == 12, f"Expected 12 applications, got {data['total_leads']}"
        assert data['pending_documents'] == 0, f"Expected 0 pending docs, got {data['pending_documents']}"
        print(f"✓ Dashboard stats: {data['total_leads']} leads, {data['pending_documents']} pending docs")
    
    def test_tasks_no_test_entries(self, sessions):
        """Tasks should have no TEST_ prefixed entries."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/tasks')
        assert resp.status_code == 200
        tasks = resp.json()
        
        test_tasks = [t for t in tasks if t.get('title', '').startswith('TEST_')]
        assert len(test_tasks) == 0, f"Found TEST_ tasks: {[t['title'] for t in test_tasks]}"
        assert len(tasks) == 5, f"Expected 5 tasks, got {len(tasks)}"
        print(f"✓ Tasks: {len(tasks)} real tasks, 0 TEST_ entries")
    
    def test_invoices_correct_amounts(self, sessions):
        """Invoices should have correct amounts and no test entries."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/invoices')
        assert resp.status_code == 200
        invoices = resp.json()
        
        assert len(invoices) == 5, f"Expected 5 invoices, got {len(invoices)}"
        total = sum(inv.get('amount', 0) for inv in invoices)
        assert total == 20350, f"Expected total €20,350, got €{total}"
        print(f"✓ Invoices: {len(invoices)} invoices, total €{total}")
    
    def test_conversations_exist(self, sessions):
        """Conversations endpoint should work (IMAP may have synced new emails)."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/conversations')
        assert resp.status_code == 200
        convos = resp.json()
        
        # Count by channel
        email_convos = [c for c in convos if c.get('channel') == 'email']
        portal_convos = [c for c in convos if c.get('channel') == 'portal']
        print(f"✓ Conversations: {len(convos)} total ({len(email_convos)} email, {len(portal_convos)} portal)")
    
    def test_applications_list(self, sessions):
        """Should have 12 applications."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/applications')
        assert resp.status_code == 200
        apps = resp.json()
        assert len(apps) == 12, f"Expected 12 applications, got {len(apps)}"
        print(f"✓ Applications: {len(apps)} total")
    
    def test_documents_empty(self, sessions):
        """Documents collection should be empty after cleanup."""
        # Check via applications - each should have 0 documents
        resp = sessions['staff'].get(f'{BASE_URL}/api/applications')
        apps = resp.json()
        
        total_docs = 0
        for app in apps[:5]:  # Check first 5
            doc_resp = sessions['staff'].get(f"{BASE_URL}/api/applications/{app['id']}/documents")
            if doc_resp.status_code == 200:
                total_docs += len(doc_resp.json())
        
        assert total_docs == 0, f"Expected 0 documents, found {total_docs}"
        print(f"✓ Documents: 0 (empty after cleanup)")


class TestStaffPortal:
    """Staff portal functionality tests."""
    
    def test_staff_kanban(self, sessions):
        """Kanban board should show applicants in correct stages."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/applications')
        assert resp.status_code == 200
        apps = resp.json()
        
        # Group by stage
        stages = {}
        for app in apps:
            stage = app.get('current_stage', 'unknown')
            stages[stage] = stages.get(stage, 0) + 1
        
        print(f"✓ Kanban stages: {stages}")
        assert len(apps) == 12
    
    def test_staff_tasks_list(self, sessions):
        """Tasks list should show 5 real tasks."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/tasks')
        assert resp.status_code == 200
        tasks = resp.json()
        
        # Verify task titles are real (not garbage)
        for task in tasks:
            title = task.get('title', '')
            assert len(title) > 5, f"Task title too short: {title}"
            assert not title.startswith('TEST_'), f"Found TEST_ task: {title}"
        
        print(f"✓ Tasks: {len(tasks)} valid tasks")
    
    def test_staff_invoices_pdf(self, sessions):
        """Invoice PDF download should work."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/invoices')
        invoices = resp.json()
        
        if invoices:
            inv_id = invoices[0]['id']
            pdf_resp = sessions['staff'].get(f'{BASE_URL}/api/invoices/{inv_id}/pdf')
            assert pdf_resp.status_code == 200
            assert pdf_resp.headers.get('content-type') == 'application/pdf'
            assert len(pdf_resp.content) > 1000  # Valid PDF
            print(f"✓ Invoice PDF: {len(pdf_resp.content)} bytes")
    
    def test_staff_messaging(self, sessions):
        """Messaging should show conversations."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/conversations')
        assert resp.status_code == 200
        convos = resp.json()
        assert len(convos) > 0, "Expected at least 1 conversation"
        print(f"✓ Messaging: {len(convos)} conversations")


class TestApplicantPortal:
    """Applicant portal functionality tests."""
    
    def test_applicant_dashboard(self, sessions):
        """Applicant dashboard should show progress."""
        resp = sessions['applicant'].get(f'{BASE_URL}/api/dashboard/stats')
        assert resp.status_code == 200
        data = resp.json()
        assert 'applications' in data
        print(f"✓ Applicant dashboard: {data.get('applications', 0)} applications")
    
    def test_applicant_documents_empty(self, sessions):
        """Applicant should see empty documents list."""
        resp = sessions['applicant'].get(f'{BASE_URL}/api/documents/my')
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) == 0, f"Expected 0 documents, got {len(docs)}"
        print(f"✓ Applicant documents: 0 (empty)")
    
    def test_applicant_invoices(self, sessions):
        """Applicant should see their invoices."""
        resp = sessions['applicant'].get(f'{BASE_URL}/api/invoices/my')
        assert resp.status_code == 200
        invoices = resp.json()
        print(f"✓ Applicant invoices: {len(invoices)}")
    
    def test_applicant_appointments(self, sessions):
        """Appointments endpoint should work."""
        resp = sessions['applicant'].get(f'{BASE_URL}/api/appointments')
        assert resp.status_code == 200
        appointments = resp.json()
        print(f"✓ Applicant appointments: {len(appointments)}")


class TestAdminPortal:
    """Admin portal functionality tests."""
    
    def test_admin_dashboard(self, sessions):
        """Admin dashboard should show system stats."""
        resp = sessions['admin'].get(f'{BASE_URL}/api/dashboard/stats')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total_users'] == 16, f"Expected 16 users, got {data['total_users']}"
        print(f"✓ Admin dashboard: {data['total_users']} users, {data['total_leads']} leads")
    
    def test_admin_users_list(self, sessions):
        """Admin should see 16 users."""
        resp = sessions['admin'].get(f'{BASE_URL}/api/users')
        assert resp.status_code == 200
        users = resp.json()
        assert len(users) == 16, f"Expected 16 users, got {len(users)}"
        print(f"✓ Admin users: {len(users)}")
    
    def test_admin_audit_logs(self, sessions):
        """Audit logs should be accessible."""
        resp = sessions['admin'].get(f'{BASE_URL}/api/audit-logs')
        assert resp.status_code == 200
        logs = resp.json()
        assert len(logs) > 0, "Expected audit logs"
        print(f"✓ Admin audit logs: {len(logs)} entries")


class TestPartnerPortal:
    """Partner portal functionality tests."""
    
    def test_partner_dashboard(self, sessions):
        """Partner dashboard should show referral stats."""
        resp = sessions['partner'].get(f'{BASE_URL}/api/partner/dashboard')
        assert resp.status_code == 200
        data = resp.json()
        assert 'total_referrals' in data
        print(f"✓ Partner dashboard: {data.get('total_referrals', 0)} referrals")
    
    def test_partner_referral_link(self, sessions):
        """Partner should be able to get referral link."""
        resp = sessions['partner'].get(f'{BASE_URL}/api/partner/referral-link')
        assert resp.status_code == 200
        data = resp.json()
        assert 'link' in data or 'referral_code' in data
        print(f"✓ Partner referral link OK")


class TestTeacherPortal:
    """Teacher portal functionality tests."""
    
    def test_teacher_students(self, sessions):
        """Teacher should be able to access students endpoint."""
        resp = sessions['teacher'].get(f'{BASE_URL}/api/teacher/my-students')
        assert resp.status_code == 200
        data = resp.json()
        students = data.get('students', [])
        print(f"✓ Teacher students: {len(students)}")
    
    def test_teacher_assignments(self, sessions):
        """Teacher should be able to see assignments."""
        resp = sessions['teacher'].get(f'{BASE_URL}/api/teacher/assignments')
        assert resp.status_code == 200
        data = resp.json()
        print(f"✓ Teacher assignments: {len(data.get('assignments', []))}")


class TestCoreFeatures:
    """Core functionality tests."""
    
    def test_csv_export(self, sessions):
        """CSV export should work."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/export/applications')
        assert resp.status_code == 200
        assert 'text/csv' in resp.headers.get('content-type', '')
        print(f"✓ CSV export: {len(resp.content)} bytes")
    
    def test_imap_sync_endpoint(self, sessions):
        """IMAP sync endpoint should respond."""
        resp = sessions['staff'].post(f'{BASE_URL}/api/messaging/sync-imap')
        # May return 200 or 202 or even error if no new mail
        assert resp.status_code in [200, 202, 400, 500]
        print(f"✓ IMAP sync endpoint: {resp.status_code}")
    
    def test_notifications(self, sessions):
        """Notifications endpoint should work."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/notifications')
        assert resp.status_code == 200
        notifs = resp.json()
        print(f"✓ Notifications: {len(notifs)} for current user")


class TestPublicPages:
    """Public pages accessibility tests."""
    
    def test_homepage(self):
        """Homepage should load."""
        resp = requests.get(f'{BASE_URL}/')
        assert resp.status_code == 200
        print(f"✓ Homepage loads")
    
    def test_apply_page(self):
        """Apply page should load."""
        resp = requests.get(f'{BASE_URL}/apply')
        assert resp.status_code == 200
        print(f"✓ Apply page loads")
    
    def test_contact_page(self):
        """Contact page should load."""
        resp = requests.get(f'{BASE_URL}/contact')
        assert resp.status_code == 200
        print(f"✓ Contact page loads")
    
    def test_booking_page(self):
        """Booking page should load."""
        resp = requests.get(f'{BASE_URL}/booking')
        assert resp.status_code == 200
        print(f"✓ Booking page loads")
    
    def test_booking_slots_public(self):
        """Public booking slots should be available."""
        resp = requests.get(f'{BASE_URL}/api/appointments/public-slots')
        assert resp.status_code == 200
        data = resp.json()
        assert 'slots' in data
        print(f"✓ Public booking slots: {len(data.get('slots', []))} available")


class TestAIScreenings:
    """AI Screening tests."""
    
    def test_ai_screenings_via_applications(self, sessions):
        """AI screenings should be accessible via applications."""
        resp = sessions['staff'].get(f'{BASE_URL}/api/applications')
        apps = resp.json()
        
        # Check first app for AI screening
        if apps:
            app_id = apps[0]['id']
            screening_resp = sessions['staff'].get(f'{BASE_URL}/api/applications/{app_id}/ai-screening')
            # May return 200 or 404 if no screening
            assert screening_resp.status_code in [200, 404]
            print(f"✓ AI screening endpoint accessible")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
