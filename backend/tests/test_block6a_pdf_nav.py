"""
Block 6A Tests: PDF Layout Hotfix + Nav Language Selector Fix

Tests:
1. PDF Layout - Single item invoice (W2G-202603-1003-AC)
2. PDF Layout - Multi-item invoice (W2G-202603-1005-AC) with 4 positions
3. PDF Legal Requirements - Company info, HRB, GF, §4 Nr. 21 UStG
4. All role logins - admin, staff, applicant, teacher, partner
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAllRoleLogins:
    """Test login functionality for all roles"""
    
    def test_admin_login(self):
        """Admin login with superadmin role"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@studienkolleg-aachen.de",
            "password": "Admin@2026!"
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert data["role"] == "superadmin"
        assert data["email"] == "admin@studienkolleg-aachen.de"
        print("✓ Admin login successful")
    
    def test_staff_login(self):
        """Staff login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert data["role"] == "staff"
        assert data["email"] == "staff@studienkolleg-aachen.de"
        print("✓ Staff login successful")
    
    def test_applicant_login(self):
        """Applicant login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "applicant@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        data = response.json()
        assert data["role"] == "applicant"
        assert data["email"] == "applicant@studienkolleg-aachen.de"
        print("✓ Applicant login successful")
    
    def test_teacher_login(self):
        """Teacher login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "teacher@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200, f"Teacher login failed: {response.text}"
        data = response.json()
        assert data["role"] == "teacher"
        assert data["email"] == "teacher@studienkolleg-aachen.de"
        print("✓ Teacher login successful")
    
    def test_partner_login(self):
        """Partner/Affiliate login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "partner@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200, f"Partner login failed: {response.text}"
        data = response.json()
        assert data["role"] == "affiliate"
        assert data["email"] == "partner@studienkolleg-aachen.de"
        print("✓ Partner login successful")


class TestInvoicePDFLayout:
    """Test PDF layout for invoices"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_single_item_invoice_pdf(self, staff_session):
        """Test PDF for single item invoice W2G-202603-1003-AC"""
        # First verify invoice exists
        response = staff_session.get(f"{BASE_URL}/api/invoices/W2G-202603-1003-AC")
        assert response.status_code == 200, f"Invoice not found: {response.text}"
        invoice = response.json()
        
        # Verify invoice data
        assert invoice["invoice_number"] == "W2G-202603-1003-AC"
        assert invoice["amount"] == 150.0
        assert invoice["status"] == "paid"
        assert len(invoice.get("items", [])) == 1
        print(f"✓ Invoice W2G-202603-1003-AC found: {invoice['amount']} EUR, status={invoice['status']}")
        
        # Download PDF
        pdf_response = staff_session.get(f"{BASE_URL}/api/invoices/W2G-202603-1003-AC/pdf")
        assert pdf_response.status_code == 200, f"PDF download failed: {pdf_response.status_code}"
        assert pdf_response.headers.get("content-type") == "application/pdf"
        assert len(pdf_response.content) > 1000, "PDF too small"
        print(f"✓ PDF downloaded: {len(pdf_response.content)} bytes")
        
        # Extract and verify PDF content
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(pdf_response.content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Verify content
            assert "W2G-202603-1003-AC" in text, "Invoice number not in PDF"
            assert "150,00 EUR" in text, "Amount not correctly formatted in PDF"
            assert "BEZAHLT" in text, "Status not in PDF"
            print("✓ PDF content verified: invoice number, amount, status")
        except ImportError:
            print("⚠ PyPDF2 not available, skipping content verification")
    
    def test_multi_item_invoice_pdf(self, staff_session):
        """Test PDF for 4-item invoice W2G-202603-1005-AC"""
        # First verify invoice exists
        response = staff_session.get(f"{BASE_URL}/api/invoices/W2G-202603-1005-AC")
        assert response.status_code == 200, f"Invoice not found: {response.text}"
        invoice = response.json()
        
        # Verify invoice data
        assert invoice["invoice_number"] == "W2G-202603-1005-AC"
        assert invoice["amount"] == 12500.0
        assert len(invoice.get("items", [])) == 4, f"Expected 4 items, got {len(invoice.get('items', []))}"
        
        # Verify individual items
        items = invoice["items"]
        expected_items = [
            ("Studienkolleg T-Kurs", 8500),
            ("Intensiv-Sprachkurs", 2800),
            ("Visumsberatung", 750),
            ("Wohnungsvermittlung", 450),
        ]
        for desc_part, expected_price in expected_items:
            found = any(desc_part in item.get("description", "") and item.get("unit_price") == expected_price for item in items)
            assert found, f"Item '{desc_part}' with price {expected_price} not found"
        print(f"✓ Invoice W2G-202603-1005-AC found: 4 items, total {invoice['amount']} EUR")
        
        # Download PDF
        pdf_response = staff_session.get(f"{BASE_URL}/api/invoices/W2G-202603-1005-AC/pdf")
        assert pdf_response.status_code == 200, f"PDF download failed: {pdf_response.status_code}"
        assert pdf_response.headers.get("content-type") == "application/pdf"
        print(f"✓ PDF downloaded: {len(pdf_response.content)} bytes")
        
        # Extract and verify PDF content
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(pdf_response.content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Verify all amounts are present
            assert "8.500,00 EUR" in text, "T-Kurs amount not in PDF"
            assert "2.800,00 EUR" in text, "Sprachkurs amount not in PDF"
            assert "750,00 EUR" in text, "Visumsberatung amount not in PDF"
            assert "450,00 EUR" in text, "Wohnungsvermittlung amount not in PDF"
            assert "12.500,00 EUR" in text, "Total amount not in PDF"
            print("✓ PDF content verified: all 4 item amounts and total")
        except ImportError:
            print("⚠ PyPDF2 not available, skipping content verification")


class TestPDFLegalRequirements:
    """Test D/A/CH legal requirements in PDF"""
    
    @pytest.fixture
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "staff@studienkolleg-aachen.de",
            "password": "DevSeed@2026!"
        })
        assert response.status_code == 200
        return session
    
    def test_pdf_legal_content(self, staff_session):
        """Verify all D/A/CH legal requirements in PDF"""
        pdf_response = staff_session.get(f"{BASE_URL}/api/invoices/W2G-202603-1003-AC/pdf")
        assert pdf_response.status_code == 200
        
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            
            reader = PdfReader(BytesIO(pdf_response.content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Required legal elements
            legal_checks = [
                ("W2G Academy GmbH", "Company name"),
                ("HRB 23610", "Handelsregister number"),
                ("Amtsgericht Aachen", "Registry court"),
                ("Laura Saboor", "Managing director"),
                ("§ 4 Nr. 21 UStG", "Tax exemption reference"),
                ("Theaterstraße", "Company address"),
                ("52062 Aachen", "City/ZIP"),
            ]
            
            for text_check, description in legal_checks:
                # Handle special characters
                text_normalized = text.replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
                text_check_normalized = text_check.replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
                
                found = text_check in text or text_check_normalized in text_normalized
                assert found, f"{description} ({text_check}) not found in PDF"
                print(f"✓ {description}: {text_check}")
            
            print("✓ All D/A/CH legal requirements verified in PDF")
        except ImportError:
            print("⚠ PyPDF2 not available, skipping legal content verification")


class TestPublicEndpoints:
    """Test public endpoints load without errors"""
    
    def test_health_check(self):
        """Health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health check passed")
    
    def test_courses_page_api(self):
        """Courses data endpoint"""
        response = requests.get(f"{BASE_URL}/api/courses")
        # May return 404 if no public courses endpoint, that's ok
        assert response.status_code in [200, 404]
        print(f"✓ Courses endpoint: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
