"""
Phase 3.7j Backend Tests
- Leads ingest with password (account creation + auto-login)
- Followups (Wiedervorlage) CRUD
- Export CSV endpoint
- Messaging attachments upload/download
"""
import pytest
import requests
import os
import base64
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def session():
    """Shared requests session"""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def staff_session(session):
    """Staff authenticated session"""
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "staff@studienkolleg-aachen.de",
        "password": os.environ["TEST_DEFAULT_PASSWORD"]
    })
    assert resp.status_code == 200, f"Staff login failed: {resp.text}"
    # Copy cookies to a new session
    staff = requests.Session()
    staff.cookies.update(session.cookies)
    staff.headers.update({"Content-Type": "application/json"})
    return staff


@pytest.fixture(scope="module")
def applicant_session(session):
    """Applicant authenticated session"""
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": "applicant@studienkolleg-aachen.de",
        "password": os.environ["TEST_DEFAULT_PASSWORD"]
    })
    assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
    applicant = requests.Session()
    applicant.cookies.update(session.cookies)
    applicant.headers.update({"Content-Type": "application/json"})
    return applicant


class TestHealthCheck:
    """Basic health check"""
    
    def test_health_endpoint(self, session):
        resp = session.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "ok"
        print("✓ Health endpoint OK")


class TestLeadsIngestWithPassword:
    """Test leads/ingest endpoint with password field for account creation"""
    
    def test_ingest_with_password_creates_account(self, session):
        """POST /api/leads/ingest with password should create account and return auth cookies"""
        unique_email = f"test_phase37j_{int(time.time())}@example.com"
        payload = {
            "full_name": "Test Phase37j",
            "first_name": "Test",
            "last_name": "Phase37j",
            "email": unique_email,
            "phone": "+49123456789",
            "date_of_birth": "2000-01-15",
            "country": "Germany",
            "area_interest": "studienkolleg",
            "course_type": "T-Course",
            "desired_start": "Winter Semester 2025/26",
            "language_level": "B1",
            "degree_country": "Germany",
            "source": "website_form",
            "password": os.environ["TEST_REGISTER_PASSWORD"]  # Password provided
        }
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200, f"Ingest failed: {resp.text}"
        data = resp.json()
        
        # Verify account_created flag
        assert data.get("account_created") == True, "account_created should be True"
        assert data.get("success") == True
        assert data.get("user_id") is not None
        
        # Verify auth cookies are set
        cookies = resp.cookies
        assert "access_token" in cookies or "access_token" in session.cookies, "access_token cookie should be set"
        print(f"✓ Ingest with password creates account: {unique_email}")
    
    def test_ingest_without_password_backwards_compatible(self, session):
        """POST /api/leads/ingest without password should still work (backwards compatible)"""
        unique_email = f"test_nopass_{int(time.time())}@example.com"
        payload = {
            "full_name": "NoPass User",
            "first_name": "NoPass",
            "last_name": "User",
            "email": unique_email,
            "phone": "+49123456789",
            "date_of_birth": "2000-01-15",
            "country": "Germany",
            "area_interest": "studienkolleg",
            "course_type": "M-Course",
            "desired_start": "Summer Semester 2026",
            "language_level": "A2",
            "degree_country": "Germany",
            "source": "website_form"
            # No password field
        }
        resp = session.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200, f"Ingest without password failed: {resp.text}"
        data = resp.json()
        
        assert data.get("success") == True
        assert data.get("user_id") is not None
        # account_created should not be True when no password
        assert data.get("account_created") != True, "account_created should not be True without password"
        print(f"✓ Ingest without password works (backwards compatible): {unique_email}")


class TestFollowupsAPI:
    """Test Wiedervorlage (Followups) CRUD endpoints"""
    
    @pytest.fixture(scope="class")
    def test_application_id(self, staff_session):
        """Get an existing application ID for testing"""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200
        apps = resp.json()
        if apps and len(apps) > 0:
            return apps[0]["id"]
        pytest.skip("No applications available for followup testing")
    
    def test_list_followups(self, staff_session):
        """GET /api/followups returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/followups")
        assert resp.status_code == 200, f"List followups failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ List followups: {len(data)} items")
    
    def test_list_due_followups(self, staff_session):
        """GET /api/followups/due returns due followups"""
        resp = staff_session.get(f"{BASE_URL}/api/followups/due")
        assert resp.status_code == 200, f"List due followups failed: {resp.text}"
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ List due followups: {len(data)} items")
    
    def test_create_followup(self, staff_session, test_application_id):
        """POST /api/followups creates a followup"""
        payload = {
            "application_id": test_application_id,
            "due_date": "2026-02-15",
            "reason": "TEST_Phase37j: Dokumente nachfragen"
        }
        resp = staff_session.post(f"{BASE_URL}/api/followups", json=payload)
        assert resp.status_code == 200, f"Create followup failed: {resp.text}"
        data = resp.json()
        
        assert data.get("id") is not None
        assert data.get("application_id") == test_application_id
        assert data.get("reason") == payload["reason"]
        assert data.get("status") == "pending"
        print(f"✓ Create followup: {data.get('id')}")
        return data.get("id")
    
    def test_update_followup(self, staff_session, test_application_id):
        """PUT /api/followups/{id} updates a followup"""
        # First create a followup
        create_payload = {
            "application_id": test_application_id,
            "due_date": "2026-02-20",
            "reason": "TEST_Phase37j: Update test"
        }
        create_resp = staff_session.post(f"{BASE_URL}/api/followups", json=create_payload)
        assert create_resp.status_code == 200
        followup_id = create_resp.json().get("id")
        
        # Update it
        update_payload = {
            "status": "completed",
            "reason": "TEST_Phase37j: Updated reason"
        }
        resp = staff_session.put(f"{BASE_URL}/api/followups/{followup_id}", json=update_payload)
        assert resp.status_code == 200, f"Update followup failed: {resp.text}"
        print(f"✓ Update followup: {followup_id}")
    
    def test_dismiss_followup(self, staff_session, test_application_id):
        """DELETE /api/followups/{id} dismisses a followup"""
        # First create a followup
        create_payload = {
            "application_id": test_application_id,
            "due_date": "2026-02-25",
            "reason": "TEST_Phase37j: Dismiss test"
        }
        create_resp = staff_session.post(f"{BASE_URL}/api/followups", json=create_payload)
        assert create_resp.status_code == 200
        followup_id = create_resp.json().get("id")
        
        # Dismiss it
        resp = staff_session.delete(f"{BASE_URL}/api/followups/{followup_id}")
        assert resp.status_code == 200, f"Dismiss followup failed: {resp.text}"
        print(f"✓ Dismiss followup: {followup_id}")


class TestExportAPI:
    """Test CSV export endpoint"""
    
    def test_export_applications_csv(self, staff_session):
        """GET /api/export/applications returns CSV"""
        resp = staff_session.get(f"{BASE_URL}/api/export/applications")
        assert resp.status_code == 200, f"Export failed: {resp.text}"
        
        # Check content type
        content_type = resp.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected CSV content type, got: {content_type}"
        
        # Check content disposition
        content_disp = resp.headers.get("Content-Disposition", "")
        assert "attachment" in content_disp, "Should have attachment disposition"
        assert "bewerbungen_export" in content_disp, "Filename should contain 'bewerbungen_export'"
        
        # Check CSV content has headers
        content = resp.text
        assert "Name" in content or "E-Mail" in content, "CSV should have headers"
        print(f"✓ Export CSV: {len(content)} bytes")
    
    def test_export_applications_with_stage_filter(self, staff_session):
        """GET /api/export/applications?stage=lead_new filters by stage"""
        resp = staff_session.get(f"{BASE_URL}/api/export/applications?stage=lead_new")
        assert resp.status_code == 200, f"Export with filter failed: {resp.text}"
        
        content_type = resp.headers.get("Content-Type", "")
        assert "text/csv" in content_type
        print("✓ Export CSV with stage filter works")


class TestMessagingAttachments:
    """Test messaging file attachment upload/download"""
    
    @pytest.fixture(scope="class")
    def conversation_id(self, applicant_session):
        """Get or create a support conversation"""
        resp = applicant_session.get(f"{BASE_URL}/api/conversations/support")
        assert resp.status_code == 200, f"Get support conversation failed: {resp.text}"
        data = resp.json()
        return data.get("id")
    
    def test_upload_attachment(self, applicant_session, conversation_id):
        """POST /api/conversations/{conv_id}/attachments uploads file"""
        # Create a simple PDF-like file as base64 (use allowed content type)
        file_content = b"%PDF-1.4 Test file content for Phase 3.7j attachment testing"
        file_b64 = base64.b64encode(file_content).decode()
        
        payload = {
            "filename": "test_phase37j.pdf",
            "content_type": "application/pdf",
            "file_data": file_b64,
            "content": "Test message with attachment"
        }
        resp = applicant_session.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/attachments",
            json=payload
        )
        assert resp.status_code == 200, f"Upload attachment failed: {resp.text}"
        data = resp.json()
        
        assert data.get("id") is not None
        assert data.get("attachment") is not None
        assert data["attachment"].get("filename") == "test_phase37j.pdf"
        assert data["attachment"].get("file_size") == len(file_content)
        # storage_key should NOT be exposed
        assert "storage_key" not in data.get("attachment", {}), "storage_key should not be exposed"
        
        print(f"✓ Upload attachment: message_id={data.get('id')}")
        return data.get("id")
    
    def test_download_attachment(self, applicant_session, conversation_id):
        """GET /api/messages/{msg_id}/attachment downloads file"""
        # First upload an attachment (use allowed content type)
        file_content = b"%PDF-1.4 Download test content for Phase 3.7j"
        file_b64 = base64.b64encode(file_content).decode()
        
        upload_resp = applicant_session.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/attachments",
            json={
                "filename": "download_test.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64,
                "content": ""
            }
        )
        assert upload_resp.status_code == 200, f"Upload for download test failed: {upload_resp.text}"
        msg_id = upload_resp.json().get("id")
        
        # Now download it
        resp = applicant_session.get(f"{BASE_URL}/api/messages/{msg_id}/attachment")
        assert resp.status_code == 200, f"Download attachment failed: {resp.text}"
        
        # Verify content
        assert resp.content == file_content, "Downloaded content should match uploaded"
        
        # Check headers
        content_disp = resp.headers.get("Content-Disposition", "")
        assert "download_test.pdf" in content_disp
        print(f"✓ Download attachment: {len(resp.content)} bytes")
    
    def test_staff_can_see_applicant_attachment(self, staff_session, applicant_session, conversation_id):
        """Staff should be able to download attachments from applicant messages"""
        # Applicant uploads (use allowed content type)
        file_content = b"%PDF-1.4 Staff visibility test"
        file_b64 = base64.b64encode(file_content).decode()
        
        upload_resp = applicant_session.post(
            f"{BASE_URL}/api/conversations/{conversation_id}/attachments",
            json={
                "filename": "staff_test.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64,
                "content": "For staff"
            }
        )
        assert upload_resp.status_code == 200
        msg_id = upload_resp.json().get("id")
        
        # Staff downloads
        resp = staff_session.get(f"{BASE_URL}/api/messages/{msg_id}/attachment")
        assert resp.status_code == 200, f"Staff download failed: {resp.text}"
        assert resp.content == file_content
        print("✓ Staff can download applicant attachments")


class TestAuthCookiesOnIngest:
    """Verify auth cookies are properly set on ingest with password"""
    
    def test_cookies_allow_portal_access(self):
        """After ingest with password, user should be able to access portal endpoints"""
        # Create a fresh session
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        
        unique_email = f"test_portal_access_{int(time.time())}@example.com"
        payload = {
            "full_name": "Portal Access",
            "first_name": "Portal",
            "last_name": "Access",
            "email": unique_email,
            "phone": "+49123456789",
            "date_of_birth": "2000-01-15",
            "country": "Germany",
            "area_interest": "studienkolleg",
            "course_type": "T-Course",
            "desired_start": "Winter Semester 2025/26",
            "language_level": "B1",
            "degree_country": "Germany",
            "source": "website_form",
            "password": os.environ["TEST_PORTAL_PASSWORD"]
        }
        
        # Ingest with password
        resp = s.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200
        assert resp.json().get("account_created") == True
        
        # Now try to access a protected endpoint
        me_resp = s.get(f"{BASE_URL}/api/auth/me")
        assert me_resp.status_code == 200, f"Auth/me failed after ingest: {me_resp.text}"
        me_data = me_resp.json()
        assert me_data.get("email") == unique_email
        assert me_data.get("role") == "applicant"
        print(f"✓ Auth cookies work after ingest: {unique_email}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
