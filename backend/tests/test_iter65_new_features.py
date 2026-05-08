"""
Iteration 65 - New Features Testing
Tests for:
1. Support Chat API (POST /api/support/chat)
2. Products API (GET /api/products)
3. Invoice Create API (POST /api/invoices)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"


@pytest.fixture(scope="module")
def staff_session():
    """Login as staff and return session with cookies."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert response.status_code == 200, f"Staff login failed: {response.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Login as admin and return session with cookies."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert response.status_code == 200, f"Admin login failed: {response.text}"
    return session


class TestSupportChatAPI:
    """Tests for Support Chat API - POST /api/support/chat"""
    
    def test_support_chat_public_access(self):
        """Test support chat works without authentication (visitor mode)."""
        response = requests.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Was ist das Studienkolleg?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Support chat failed: {response.text}"
        
        data = response.json()
        assert "reply" in data, "Response should contain 'reply'"
        assert "role_context" in data, "Response should contain 'role_context'"
        assert data["role_context"] == "visitor", "Unauthenticated user should be 'visitor'"
        assert len(data["reply"]) > 0, "Reply should not be empty"
    
    def test_support_chat_authenticated_staff(self, staff_session):
        """Test support chat with staff authentication."""
        response = staff_session.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Wie erstelle ich eine Rechnung?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Support chat failed: {response.text}"
        
        data = response.json()
        assert data["role_context"] == "staff", "Staff user should have 'staff' context"
        assert len(data["reply"]) > 0, "Reply should not be empty"
    
    def test_support_chat_authenticated_admin(self, admin_session):
        """Test support chat with admin authentication."""
        response = admin_session.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Wie verwalte ich Benutzer?",
            "history": [],
            "language": "de"
        })
        assert response.status_code == 200, f"Support chat failed: {response.text}"
        
        data = response.json()
        assert data["role_context"] == "admin", "Admin user should have 'admin' context"
        assert len(data["reply"]) > 0, "Reply should not be empty"
    
    def test_support_chat_with_history(self):
        """Test support chat with conversation history."""
        history = [
            {"role": "user", "content": "Hallo"},
            {"role": "assistant", "content": "Hallo! Wie kann ich Ihnen helfen?"}
        ]
        response = requests.post(f"{BASE_URL}/api/support/chat", json={
            "message": "Was sind die Kurstypen?",
            "history": history,
            "language": "de"
        })
        assert response.status_code == 200, f"Support chat with history failed: {response.text}"
        
        data = response.json()
        assert "reply" in data
    
    def test_support_chat_english_language(self):
        """Test support chat responds in English when requested."""
        response = requests.post(f"{BASE_URL}/api/support/chat", json={
            "message": "What is Studienkolleg?",
            "history": [],
            "language": "en"
        })
        assert response.status_code == 200, f"Support chat English failed: {response.text}"
        
        data = response.json()
        assert "reply" in data
    
    def test_support_chat_empty_message_rejected(self):
        """Test that empty messages are rejected."""
        response = requests.post(f"{BASE_URL}/api/support/chat", json={
            "message": "",
            "history": [],
            "language": "de"
        })
        # Should return 422 validation error
        assert response.status_code == 422, "Empty message should be rejected"


class TestProductsAPI:
    """Tests for Products API - GET /api/products"""
    
    def test_products_requires_auth(self):
        """Test that products API requires authentication."""
        response = requests.get(f"{BASE_URL}/api/products")
        assert response.status_code == 401, "Products API should require authentication"
    
    def test_products_list_authenticated(self, staff_session):
        """Test products list returns expected products."""
        response = staff_session.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200, f"Products list failed: {response.text}"
        
        products = response.json()
        assert isinstance(products, list), "Products should be a list"
        assert len(products) == 17, f"Expected 17 products, got {len(products)}"
    
    def test_products_structure(self, staff_session):
        """Test product structure has required fields."""
        response = staff_session.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        required_fields = ["code", "name", "description", "price", "currency", "category"]
        
        for product in products:
            for field in required_fields:
                assert field in product, f"Product missing field: {field}"
    
    def test_products_categories(self, staff_session):
        """Test products have valid categories."""
        response = staff_session.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        valid_categories = ["kurs", "sprache", "pruefung", "gebuehr", "service", "unterkunft", "kombi", "sonstig"]
        
        for product in products:
            assert product["category"] in valid_categories, f"Invalid category: {product['category']}"
    
    def test_products_contains_kurse(self, staff_session):
        """Test products contain expected course types."""
        response = staff_session.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        codes = [p["code"] for p in products]
        
        expected_courses = ["SK-TKURS", "SK-MKURS", "SK-WKURS", "SK-GKURS", "SK-SKURS"]
        for course in expected_courses:
            assert course in codes, f"Missing course: {course}"
    
    def test_products_contains_kombi_pakete(self, staff_session):
        """Test products contain combo packages."""
        response = staff_session.get(f"{BASE_URL}/api/products")
        assert response.status_code == 200
        
        products = response.json()
        codes = [p["code"] for p in products]
        
        expected_combos = ["KOMBI-BASIC", "KOMBI-PREMIUM", "KOMBI-ALL-IN"]
        for combo in expected_combos:
            assert combo in codes, f"Missing combo package: {combo}"


class TestInvoiceCreateAPI:
    """Tests for Invoice Create API - POST /api/invoices"""
    
    def test_invoice_create_requires_auth(self):
        """Test that invoice creation requires authentication."""
        response = requests.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": "test",
            "description": "Test",
            "amount": 100,
            "due_date": "2026-05-01"
        })
        assert response.status_code == 401, "Invoice create should require authentication"
    
    def test_invoice_create_with_items(self, staff_session):
        """Test creating invoice with line items."""
        # First get an application to use
        apps_response = staff_session.get(f"{BASE_URL}/api/applications?limit=1")
        assert apps_response.status_code == 200
        
        apps = apps_response.json()
        if isinstance(apps, dict):
            apps = apps.get("applications", [])
        
        if len(apps) == 0:
            pytest.skip("No applications available for testing")
        
        app = apps[0]
        
        # Create invoice
        invoice_data = {
            "applicant_id": app.get("applicant_id") or app.get("id"),
            "application_id": app.get("id"),
            "description": "TEST_Invoice - T-Kurs WS 2026/27",
            "amount": 4500,
            "due_date": "2026-05-01",
            "currency": "EUR",
            "items": [
                {
                    "description": "T-Kurs (Technik)",
                    "quantity": 1,
                    "unit_price": 4500
                }
            ]
        }
        
        response = staff_session.post(f"{BASE_URL}/api/invoices", json=invoice_data)
        assert response.status_code in [200, 201], f"Invoice create failed: {response.text}"
        
        data = response.json()
        assert "id" in data or "invoice_number" in data, "Response should contain invoice ID or number"
    
    def test_invoice_list(self, staff_session):
        """Test listing invoices."""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Invoice list failed: {response.text}"
        
        data = response.json()
        # Can be list or dict with invoices key
        invoices = data if isinstance(data, list) else data.get("invoices", [])
        assert isinstance(invoices, list), "Invoices should be a list"


class TestApplicationsAPI:
    """Tests for Applications API - used by Invoice Modal"""
    
    def test_applications_list(self, staff_session):
        """Test applications list for invoice modal."""
        response = staff_session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Applications list failed: {response.text}"
        
        data = response.json()
        apps = data if isinstance(data, list) else data.get("applications", [])
        assert len(apps) > 0, "Should have at least one application"
    
    def test_application_detail(self, staff_session):
        """Test application detail page data."""
        # Get first application
        response = staff_session.get(f"{BASE_URL}/api/applications?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        apps = data if isinstance(data, list) else data.get("applications", [])
        
        if len(apps) == 0:
            pytest.skip("No applications available")
        
        app_id = apps[0]["id"]
        
        # Get detail
        detail_response = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
        assert detail_response.status_code == 200, f"Application detail failed: {detail_response.text}"
        
        detail = detail_response.json()
        assert "id" in detail
        assert "applicant" in detail or "applicant_id" in detail


class TestHealthAndAuth:
    """Basic health and auth tests."""
    
    def test_health_endpoint(self):
        """Test health endpoint."""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
    
    def test_staff_login(self):
        """Test staff login."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["role"] == "staff"
    
    def test_admin_login(self):
        """Test admin login."""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["role"] in ["admin", "superadmin"]
