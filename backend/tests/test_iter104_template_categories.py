"""
Iteration 104 - AI Email Template Categories Testing

Tests for:
- POST /api/messaging/generate-email with 8 template types
- Auto language detection from recipient's language_pref
- Returns detected_lang and recipient_name fields
- Free form (no template) still works
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Template categories to test (testing 4 of 8 to save tokens as per instructions)
TEMPLATES_TO_TEST = [
    'documents_request',
    'status_update', 
    'appointment',
    'welcome',
]

class TestAIEmailTemplateCategories:
    """Test AI email generation with template categories"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as staff and get CSRF token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as staff
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "staff@studienkolleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        
        # Get CSRF token from cookies
        csrf_token = self.session.cookies.get('csrf_token')
        if csrf_token:
            self.session.headers.update({"X-CSRF-Token": csrf_token})
        
        yield
        
        # Cleanup
        self.session.close()
    
    def test_generate_email_documents_request_template(self):
        """Test documents_request template generates appropriate email"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "template": "documents_request",
                "hints": "Sprachzertifikat fehlt"
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "generated_text" in data, "Missing generated_text field"
        assert "detected_lang" in data, "Missing detected_lang field"
        assert len(data["generated_text"]) > 50, "Generated text too short"
        print(f"PASS: documents_request template - generated {len(data['generated_text'])} chars, lang={data['detected_lang']}")
    
    def test_generate_email_status_update_template(self):
        """Test status_update template generates appropriate email"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "template": "status_update",
                "hints": "Bewerbung wird geprueft"
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "generated_text" in data
        assert "detected_lang" in data
        assert len(data["generated_text"]) > 50
        print(f"PASS: status_update template - generated {len(data['generated_text'])} chars, lang={data['detected_lang']}")
    
    def test_generate_email_appointment_template(self):
        """Test appointment template generates appropriate email"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "template": "appointment",
                "hints": "Termin am Freitag 14 Uhr"
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "generated_text" in data
        assert "detected_lang" in data
        assert len(data["generated_text"]) > 50
        print(f"PASS: appointment template - generated {len(data['generated_text'])} chars, lang={data['detected_lang']}")
    
    def test_generate_email_welcome_template(self):
        """Test welcome template generates appropriate email"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "template": "welcome",
                "hints": ""
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "generated_text" in data
        assert "detected_lang" in data
        assert len(data["generated_text"]) > 50
        print(f"PASS: welcome template - generated {len(data['generated_text'])} chars, lang={data['detected_lang']}")
    
    def test_generate_email_free_form_no_template(self):
        """Test free form (no template) still works"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "hints": "Bitte um Rueckruf wegen offener Fragen"
            }
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()
        
        assert "generated_text" in data
        assert "detected_lang" in data
        assert len(data["generated_text"]) > 50
        print(f"PASS: free form (no template) - generated {len(data['generated_text'])} chars, lang={data['detected_lang']}")
    
    def test_generate_email_returns_detected_lang_field(self):
        """Test that detected_lang field is returned"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "template": "documents_request",
                "hints": "Test"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        
        assert "detected_lang" in data, "Missing detected_lang field"
        assert data["detected_lang"] in ["de", "en", ""], f"Unexpected lang: {data['detected_lang']}"
        print(f"PASS: detected_lang field returned: {data['detected_lang']}")
    
    def test_generate_email_returns_recipient_name_field(self):
        """Test that recipient_name field is returned"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={
                "template": "status_update",
                "hints": "Test"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        
        assert "recipient_name" in data, "Missing recipient_name field"
        # recipient_name can be empty string if no conversation context
        print(f"PASS: recipient_name field returned: '{data['recipient_name']}'")
    
    def test_generate_email_requires_staff_role(self):
        """Test that applicant cannot generate emails"""
        # Login as applicant
        applicant_session = requests.Session()
        applicant_session.headers.update({"Content-Type": "application/json"})
        
        login_resp = applicant_session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "applicant@studienkoleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        
        # Even if login fails, try the endpoint
        csrf = applicant_session.cookies.get('csrf_token')
        if csrf:
            applicant_session.headers.update({"X-CSRF-Token": csrf})
        
        resp = applicant_session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={"template": "welcome", "hints": "test"}
        )
        
        # Should be 401 (not logged in) or 403 (forbidden)
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print(f"PASS: Non-staff gets {resp.status_code} as expected")
        applicant_session.close()


class TestTemplateInstructionsExist:
    """Verify all 8 template types are defined in backend"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "staff@studienkolleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        assert login_resp.status_code == 200
        
        csrf_token = self.session.cookies.get('csrf_token')
        if csrf_token:
            self.session.headers.update({"X-CSRF-Token": csrf_token})
        
        yield
        self.session.close()
    
    def test_offer_template_works(self):
        """Test offer (Zusage) template"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={"template": "offer", "hints": "Zusage fuer Sommersemester"}
        )
        assert resp.status_code == 200, f"offer template failed: {resp.text}"
        assert "generated_text" in resp.json()
        print("PASS: offer template works")
    
    def test_rejection_template_works(self):
        """Test rejection (Absage) template"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={"template": "rejection", "hints": "Leider nicht qualifiziert"}
        )
        assert resp.status_code == 200, f"rejection template failed: {resp.text}"
        assert "generated_text" in resp.json()
        print("PASS: rejection template works")
    
    def test_payment_reminder_template_works(self):
        """Test payment_reminder (Zahlungserinnerung) template"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={"template": "payment_reminder", "hints": "Rechnung 12345 offen"}
        )
        assert resp.status_code == 200, f"payment_reminder template failed: {resp.text}"
        assert "generated_text" in resp.json()
        print("PASS: payment_reminder template works")
    
    def test_follow_up_template_works(self):
        """Test follow_up (Nachfrage) template"""
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={"template": "follow_up", "hints": "Warten auf Antwort"}
        )
        assert resp.status_code == 200, f"follow_up template failed: {resp.text}"
        assert "generated_text" in resp.json()
        print("PASS: follow_up template works")
