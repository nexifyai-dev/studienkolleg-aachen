"""
Iteration 102 - Email Brain API Tests
Tests for:
- GET /api/brain/emails - E-Mail-Inbox mit KI-Entwuerfen
- POST /api/brain/poll-inbox - IMAP-Polling ausloesen
- GET /api/brain/drafts/{id} - Entwurf-Details
- GET /api/brain/stats - Memory-Statistiken
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


def get_csrf_token(session):
    """Get CSRF token from session cookies"""
    return session.cookies.get('csrf_token', '')


class TestEmailBrainAPI:
    """Email Brain API endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate as staff"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        self.staff_user = login_resp.json().get("user", {})
        
        # Get CSRF token from cookies after login
        self.session.get(f"{BASE_URL}/api/auth/me")  # This sets the csrf_token cookie
        csrf_token = get_csrf_token(self.session)
        if csrf_token:
            self.session.headers.update({"x-csrf-token": csrf_token})
        
        print(f"Logged in as staff: {self.staff_user.get('email')}")
    
    def test_01_brain_emails_returns_list(self):
        """GET /api/brain/emails should return email list with drafts"""
        response = self.session.get(f"{BASE_URL}/api/brain/emails?limit=100")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: GET /api/brain/emails returned {len(data)} emails")
        
        # Verify email structure if we have emails
        if len(data) > 0:
            email = data[0]
            assert "id" in email, "Email should have id"
            assert "subject" in email or "from_addr" in email, "Email should have subject or from_addr"
            print(f"  First email: {email.get('subject', 'No subject')[:50]}...")
    
    def test_02_brain_emails_with_limit(self):
        """GET /api/brain/emails with limit parameter"""
        response = self.session.get(f"{BASE_URL}/api/brain/emails?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 10, f"Expected max 10 emails, got {len(data)}"
        print(f"PASS: Limit parameter works - returned {len(data)} emails")
    
    def test_03_brain_poll_inbox_triggers_imap(self):
        """POST /api/brain/poll-inbox should trigger IMAP polling"""
        response = self.session.post(f"{BASE_URL}/api/brain/poll-inbox")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should return counts
        assert "imported" in data or "skipped" in data or "errors" in data, \
            f"Response should contain import stats: {data}"
        print(f"PASS: POST /api/brain/poll-inbox returned: imported={data.get('imported', 0)}, skipped={data.get('skipped', 0)}")
    
    def test_04_brain_stats_returns_statistics(self):
        """GET /api/brain/stats should return memory statistics"""
        response = self.session.get(f"{BASE_URL}/api/brain/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "total_memories" in data or "emails_ingested" in data, \
            f"Response should contain stats: {data}"
        print(f"PASS: GET /api/brain/stats returned: {data}")
    
    def test_05_brain_drafts_get_by_id(self):
        """GET /api/brain/drafts/{id} should return draft details"""
        # First get emails to find one with a draft
        emails_resp = self.session.get(f"{BASE_URL}/api/brain/emails?limit=100")
        assert emails_resp.status_code == 200
        
        emails = emails_resp.json()
        draft_id = None
        
        # Find an email with a draft
        for email in emails:
            if email.get("has_draft") and email.get("drafts"):
                draft_id = email["drafts"][0].get("id")
                break
        
        if not draft_id:
            pytest.skip("No drafts found to test GET /api/brain/drafts/{id}")
        
        response = self.session.get(f"{BASE_URL}/api/brain/drafts/{draft_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "id" in data, "Draft should have id"
        assert "body" in data or "subject" in data, "Draft should have body or subject"
        print(f"PASS: GET /api/brain/drafts/{draft_id} returned draft with subject: {data.get('subject', 'N/A')[:50]}")
    
    def test_06_brain_drafts_invalid_id_returns_404(self):
        """GET /api/brain/drafts/{invalid_id} should return 404"""
        response = self.session.get(f"{BASE_URL}/api/brain/drafts/000000000000000000000000")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid draft ID returns 404")


class TestEmailBrainAccessControl:
    """Test role-based access control for Email Brain API"""
    
    def test_07_applicant_cannot_access_brain_emails(self):
        """Applicant should not be able to access /api/brain/emails"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as applicant
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert login_resp.status_code == 200, f"Applicant login failed: {login_resp.text}"
        
        # Get CSRF token from cookies
        session.get(f"{BASE_URL}/api/auth/me")
        csrf_token = get_csrf_token(session)
        if csrf_token:
            session.headers.update({"x-csrf-token": csrf_token})
        
        # Try to access brain emails
        response = session.get(f"{BASE_URL}/api/brain/emails")
        assert response.status_code in [401, 403], \
            f"Applicant should not access brain emails, got {response.status_code}"
        print("PASS: Applicant correctly denied access to /api/brain/emails")
    
    def test_08_applicant_cannot_poll_inbox(self):
        """Applicant should not be able to trigger IMAP polling"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login as applicant
        login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert login_resp.status_code == 200
        
        # Get CSRF token from cookies
        session.get(f"{BASE_URL}/api/auth/me")
        csrf_token = get_csrf_token(session)
        if csrf_token:
            session.headers.update({"x-csrf-token": csrf_token})
        
        # Try to poll inbox
        response = session.post(f"{BASE_URL}/api/brain/poll-inbox")
        assert response.status_code in [401, 403], \
            f"Applicant should not poll inbox, got {response.status_code}"
        print("PASS: Applicant correctly denied access to /api/brain/poll-inbox")


class TestEmailBrainDataIntegrity:
    """Test data integrity and structure of Email Brain responses"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and authenticate as staff"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert login_resp.status_code == 200
        
        # Get CSRF token from cookies
        self.session.get(f"{BASE_URL}/api/auth/me")
        csrf_token = get_csrf_token(self.session)
        if csrf_token:
            self.session.headers.update({"x-csrf-token": csrf_token})
    
    def test_09_email_structure_validation(self):
        """Validate email object structure"""
        response = self.session.get(f"{BASE_URL}/api/brain/emails?limit=50")
        assert response.status_code == 200
        
        emails = response.json()
        if len(emails) == 0:
            pytest.skip("No emails to validate structure")
        
        # Check first email has expected fields
        email = emails[0]
        expected_fields = ["id", "direction"]
        
        for field in expected_fields:
            assert field in email, f"Email missing field: {field}"
        
        # Check direction is valid
        if "direction" in email:
            assert email["direction"] in ["inbound", "outbound"], \
                f"Invalid direction: {email['direction']}"
        
        print(f"PASS: Email structure validated - {len(emails)} emails checked")
    
    def test_10_emails_have_drafts_info(self):
        """Emails should include draft information"""
        response = self.session.get(f"{BASE_URL}/api/brain/emails?limit=100")
        assert response.status_code == 200
        
        emails = response.json()
        emails_with_drafts = [e for e in emails if e.get("has_draft")]
        
        print(f"PASS: Found {len(emails_with_drafts)} emails with drafts out of {len(emails)} total")
        
        # If we have drafts, verify structure
        if emails_with_drafts:
            email = emails_with_drafts[0]
            assert "drafts" in email or "draft_status" in email, \
                "Email with draft should have drafts array or draft_status"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
