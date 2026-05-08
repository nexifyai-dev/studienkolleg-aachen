"""
Iteration 103 - Invoice Bug Fix & Messaging Improvements Tests

Tests:
1. POST /api/invoices - amount auto-calculated from items if not provided
2. POST /api/invoices - due_date defaults to +30 days if not provided
3. POST /api/invoices - explicit amount and due_date still work
4. GET /api/email-signature - returns per-user signature or default
5. PUT /api/email-signature - saves custom signature per user
6. GET /api/email-signature?reset=1 - resets to default signature
7. POST /api/messaging/generate-email - AI email text generation
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


def get_csrf_from_cookies(session):
    """Extract CSRF token from session cookies after login"""
    return session.cookies.get('csrf_token', '')


class TestInvoiceAutoCalculation:
    """Tests for invoice amount auto-calculation and due_date default"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as staff and get CSRF token"""
        self.session = requests.Session()
        # Get initial CSRF token
        csrf_resp = self.session.get(f"{BASE_URL}/api/auth/csrf-token")
        initial_csrf = csrf_resp.json().get('csrf_token', '')
        
        # Login as staff
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
            headers={"X-CSRF-Token": initial_csrf}
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        
        # Get CSRF token from cookies after login
        self.csrf_token = get_csrf_from_cookies(self.session)
        
        # Get applicant ID for invoice creation
        applicants_resp = self.session.get(f"{BASE_URL}/api/invoices/applicants")
        assert applicants_resp.status_code == 200
        applicants = applicants_resp.json()
        assert len(applicants) > 0, "No applicants found for invoice testing"
        self.applicant_id = applicants[0]['id']
        self.applicant_name = applicants[0].get('full_name', applicants[0].get('email', ''))
        
    def test_invoice_amount_auto_calculated_from_items(self):
        """POST /api/invoices - amount auto-calculated from items when not provided"""
        # Create invoice with items but NO amount
        items = [
            {"description": "TEST_Kursgebuehr Semester 1", "quantity": 1, "unit_price": 2500.00},
            {"description": "TEST_Anmeldegebuehr", "quantity": 1, "unit_price": 150.00},
        ]
        expected_amount = 2500.00 + 150.00  # 2650.00
        
        payload = {
            "applicant_id": self.applicant_id,
            "description": "TEST_Auto-calculated amount",
            "items": items,
            "due_date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            # NOTE: amount is NOT provided - should be auto-calculated
        }
        
        resp = self.session.post(
            f"{BASE_URL}/api/invoices",
            json=payload,
            headers={"X-CSRF-Token": self.csrf_token}
        )
        
        assert resp.status_code == 200 or resp.status_code == 201, f"Invoice creation failed: {resp.text}"
        invoice = resp.json()
        
        # Verify amount was auto-calculated
        assert 'amount' in invoice, "Invoice response missing 'amount' field"
        assert invoice['amount'] == expected_amount, f"Expected amount {expected_amount}, got {invoice['amount']}"
        assert invoice['invoice_number'] is not None, "Invoice number not generated"
        
        print(f"PASS: Invoice created with auto-calculated amount: {invoice['amount']} EUR")
        print(f"  Invoice number: {invoice['invoice_number']}")
        
    def test_invoice_due_date_defaults_to_30_days(self):
        """POST /api/invoices - due_date defaults to +30 days when not provided"""
        items = [
            {"description": "TEST_Default due_date test", "quantity": 1, "unit_price": 500.00},
        ]
        
        payload = {
            "applicant_id": self.applicant_id,
            "description": "TEST_Default due_date",
            "items": items,
            # NOTE: due_date is NOT provided - should default to +30 days
        }
        
        resp = self.session.post(
            f"{BASE_URL}/api/invoices",
            json=payload,
            headers={"X-CSRF-Token": self.csrf_token}
        )
        
        assert resp.status_code == 200 or resp.status_code == 201, f"Invoice creation failed: {resp.text}"
        invoice = resp.json()
        
        # Verify due_date was set to approximately +30 days
        assert 'due_date' in invoice, "Invoice response missing 'due_date' field"
        due_date = datetime.strptime(invoice['due_date'][:10], "%Y-%m-%d")
        expected_due = datetime.now() + timedelta(days=30)
        
        # Allow 1 day tolerance for timezone differences
        diff_days = abs((due_date - expected_due).days)
        assert diff_days <= 1, f"Due date should be ~30 days from now, got {invoice['due_date']}"
        
        print(f"PASS: Invoice created with default due_date: {invoice['due_date']}")
        print(f"  Invoice number: {invoice['invoice_number']}")
        
    def test_invoice_explicit_amount_and_due_date(self):
        """POST /api/invoices - explicit amount and due_date work correctly"""
        items = [
            {"description": "TEST_Explicit values test", "quantity": 2, "unit_price": 100.00},
        ]
        explicit_amount = 999.99  # Different from calculated (200.00)
        explicit_due_date = (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d")
        
        payload = {
            "applicant_id": self.applicant_id,
            "description": "TEST_Explicit amount and due_date",
            "items": items,
            "amount": explicit_amount,  # Explicit amount
            "due_date": explicit_due_date,  # Explicit due_date
        }
        
        resp = self.session.post(
            f"{BASE_URL}/api/invoices",
            json=payload,
            headers={"X-CSRF-Token": self.csrf_token}
        )
        
        assert resp.status_code == 200 or resp.status_code == 201, f"Invoice creation failed: {resp.text}"
        invoice = resp.json()
        
        # Verify explicit values were used
        assert invoice['amount'] == explicit_amount, f"Expected explicit amount {explicit_amount}, got {invoice['amount']}"
        assert invoice['due_date'][:10] == explicit_due_date, f"Expected due_date {explicit_due_date}, got {invoice['due_date']}"
        
        print(f"PASS: Invoice created with explicit amount: {invoice['amount']} EUR, due_date: {invoice['due_date']}")


class TestEmailSignature:
    """Tests for per-user email signature API"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as staff and get CSRF token"""
        self.session = requests.Session()
        csrf_resp = self.session.get(f"{BASE_URL}/api/auth/csrf-token")
        initial_csrf = csrf_resp.json().get('csrf_token', '')
        
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
            headers={"X-CSRF-Token": initial_csrf}
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        
        self.csrf_token = get_csrf_from_cookies(self.session)
        
    def test_get_email_signature_returns_signature(self):
        """GET /api/email-signature - returns signature (custom or default)"""
        resp = self.session.get(f"{BASE_URL}/api/email-signature")
        
        assert resp.status_code == 200, f"Get signature failed: {resp.text}"
        data = resp.json()
        
        assert 'signature' in data, "Response missing 'signature' field"
        assert 'sender_name' in data, "Response missing 'sender_name' field"
        assert 'sender_role' in data, "Response missing 'sender_role' field"
        assert 'is_custom' in data, "Response missing 'is_custom' field"
        
        print(f"PASS: GET /api/email-signature returns signature")
        print(f"  is_custom: {data['is_custom']}")
        print(f"  sender_name: {data['sender_name']}")
        
    def test_save_custom_email_signature(self):
        """PUT /api/email-signature - saves custom signature per user"""
        custom_sig = """TEST_CUSTOM_SIGNATURE
Mit freundlichen Gruessen,
Test Staff
Studienkolleg Aachen
Tel: +49 241 12345"""
        
        resp = self.session.put(
            f"{BASE_URL}/api/email-signature",
            json={"signature": custom_sig},
            headers={"X-CSRF-Token": self.csrf_token}
        )
        
        assert resp.status_code == 200, f"Save signature failed: {resp.text}"
        data = resp.json()
        
        assert data.get('ok') == True, "Response should have ok=True"
        assert data.get('signature') == custom_sig, "Saved signature doesn't match"
        
        # Verify by fetching again
        get_resp = self.session.get(f"{BASE_URL}/api/email-signature")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        
        assert get_data['signature'] == custom_sig, "Fetched signature doesn't match saved"
        assert get_data['is_custom'] == True, "is_custom should be True after saving"
        
        print(f"PASS: PUT /api/email-signature saves custom signature")
        
    def test_reset_email_signature_to_default(self):
        """GET /api/email-signature?reset=1 - resets to default signature"""
        # First save a custom signature
        custom_sig = "TEST_TO_BE_RESET"
        self.session.put(
            f"{BASE_URL}/api/email-signature",
            json={"signature": custom_sig},
            headers={"X-CSRF-Token": self.csrf_token}
        )
        
        # Now reset
        resp = self.session.get(f"{BASE_URL}/api/email-signature?reset=1")
        
        assert resp.status_code == 200, f"Reset signature failed: {resp.text}"
        data = resp.json()
        
        assert 'signature' in data, "Response missing 'signature' field"
        assert data['is_custom'] == False, "is_custom should be False after reset"
        assert "TEST_TO_BE_RESET" not in data['signature'], "Custom signature should be removed"
        
        # Verify default signature contains expected content
        assert "Studienkolleg Aachen" in data['signature'] or "Way2Germany" in data['signature'], \
            "Default signature should contain organization name"
        
        print(f"PASS: GET /api/email-signature?reset=1 resets to default")


class TestAIEmailGeneration:
    """Tests for AI email text generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as staff and get CSRF token"""
        self.session = requests.Session()
        csrf_resp = self.session.get(f"{BASE_URL}/api/auth/csrf-token")
        initial_csrf = csrf_resp.json().get('csrf_token', '')
        
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
            headers={"X-CSRF-Token": initial_csrf}
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        
        self.csrf_token = get_csrf_from_cookies(self.session)
        
    def test_generate_email_with_hints(self):
        """POST /api/messaging/generate-email - generates AI email text"""
        payload = {
            "hints": "Bewerber nach fehlenden Unterlagen fragen, freundlich bleiben",
            "lang": "de"
        }
        
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json=payload,
            headers={"X-CSRF-Token": self.csrf_token},
            timeout=60  # AI generation can take time
        )
        
        assert resp.status_code == 200, f"Generate email failed: {resp.text}"
        data = resp.json()
        
        assert 'generated_text' in data, "Response missing 'generated_text' field"
        assert len(data['generated_text']) > 50, "Generated text too short"
        assert 'tokens_used' in data, "Response missing 'tokens_used' field"
        
        print(f"PASS: POST /api/messaging/generate-email generates text")
        print(f"  Generated text length: {len(data['generated_text'])} chars")
        print(f"  Tokens used: {data['tokens_used']}")
        
    def test_generate_email_without_hints(self):
        """POST /api/messaging/generate-email - works without hints"""
        payload = {
            "lang": "de"
        }
        
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json=payload,
            headers={"X-CSRF-Token": self.csrf_token},
            timeout=60
        )
        
        assert resp.status_code == 200, f"Generate email failed: {resp.text}"
        data = resp.json()
        
        assert 'generated_text' in data, "Response missing 'generated_text' field"
        
        print(f"PASS: POST /api/messaging/generate-email works without hints")
        
    def test_generate_email_english(self):
        """POST /api/messaging/generate-email - generates English email"""
        payload = {
            "hints": "Ask applicant about missing documents",
            "lang": "en"
        }
        
        resp = self.session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json=payload,
            headers={"X-CSRF-Token": self.csrf_token},
            timeout=60
        )
        
        assert resp.status_code == 200, f"Generate email failed: {resp.text}"
        data = resp.json()
        
        assert 'generated_text' in data, "Response missing 'generated_text' field"
        
        print(f"PASS: POST /api/messaging/generate-email generates English text")
        
    def test_generate_email_requires_staff_role(self):
        """POST /api/messaging/generate-email - requires staff role"""
        # Login as applicant
        applicant_session = requests.Session()
        csrf_resp = applicant_session.get(f"{BASE_URL}/api/auth/csrf-token")
        initial_csrf = csrf_resp.json().get('csrf_token', '')
        
        login_resp = applicant_session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "applicant@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
            headers={"X-CSRF-Token": initial_csrf}
        )
        assert login_resp.status_code == 200, "Applicant login failed"
        
        csrf_token = get_csrf_from_cookies(applicant_session)
        
        # Try to generate email
        resp = applicant_session.post(
            f"{BASE_URL}/api/messaging/generate-email",
            json={"hints": "test", "lang": "de"},
            headers={"X-CSRF-Token": csrf_token}
        )
        
        assert resp.status_code == 403, f"Expected 403 for applicant, got {resp.status_code}"
        
        print(f"PASS: POST /api/messaging/generate-email requires staff role (applicant gets 403)")


class TestMessagingPageLoads:
    """Tests for messaging page and conversations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as staff"""
        self.session = requests.Session()
        csrf_resp = self.session.get(f"{BASE_URL}/api/auth/csrf-token")
        initial_csrf = csrf_resp.json().get('csrf_token', '')
        
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "staff@studienkolleg-aachen.de", "password": "DevSeed@2026!"},
            headers={"X-CSRF-Token": initial_csrf}
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        
        self.csrf_token = get_csrf_from_cookies(self.session)
        
    def test_conversations_list(self):
        """GET /api/conversations - returns conversation list"""
        resp = self.session.get(f"{BASE_URL}/api/conversations")
        
        assert resp.status_code == 200, f"Get conversations failed: {resp.text}"
        data = resp.json()
        
        assert 'conversations' in data, "Response missing 'conversations' field"
        assert 'total' in data, "Response missing 'total' field"
        
        print(f"PASS: GET /api/conversations returns {data['total']} conversations")
        
    def test_conversations_stats(self):
        """GET /api/conversations/stats - returns stats"""
        resp = self.session.get(f"{BASE_URL}/api/conversations/stats")
        
        assert resp.status_code == 200, f"Get stats failed: {resp.text}"
        data = resp.json()
        
        assert 'total' in data, "Response missing 'total' field"
        assert 'portal' in data, "Response missing 'portal' field"
        assert 'email' in data, "Response missing 'email' field"
        
        print(f"PASS: GET /api/conversations/stats returns stats (total: {data['total']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
