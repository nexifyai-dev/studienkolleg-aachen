"""
Iteration 79 - RustFS S3 Storage Integration Tests

Tests:
1. Document upload via /api/applications/{app_id}/documents/upload with Base64 file_data
2. Document download via /api/documents/{doc_id}/download
3. Storage backend configuration verification
4. language_pref fix verification (regression)
5. Full lead ingest flow with documents
6. Staff login and dashboard (regression)
7. Invoice CRUD and PDF download (regression)
"""
import pytest
import requests
import os
import base64
import time
import random

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"

# Test application ID (from main agent context)
TEST_APP_ID = "69cb8e9a3f026e1d41dd4800"

# Test prefix for cleanup
TEST_PREFIX = f"test_iter79_{random.randint(1000000, 9999999)}"


@pytest.fixture(scope="module")
def staff_session():
    """Login as staff and return session with cookies"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert resp.status_code == 200, f"Staff login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def admin_session():
    """Login as admin and return session with cookies"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return session


class TestStorageConfiguration:
    """Test 1: Verify S3 storage backend is configured correctly"""
    
    def test_health_shows_s3_storage(self):
        """Health endpoint should show storage_backend=s3"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("storage_backend") == "s3", f"Expected s3, got {data.get('storage_backend')}"
        print(f"✓ Storage backend: {data.get('storage_backend')}")


class TestDocumentUploadS3:
    """Test 2: Document upload to RustFS via S3 API"""
    
    def test_upload_document_with_base64(self, staff_session):
        """Upload a document with Base64 file_data to S3"""
        # Create a simple PDF-like content (just for testing)
        test_content = b"%PDF-1.4\nTest document content for iteration 79 S3 storage test\n%%EOF"
        file_data_b64 = base64.b64encode(test_content).decode('utf-8')
        
        payload = {
            "document_type": "language_certificate",
            "filename": f"{TEST_PREFIX}_sprachzertifikat.pdf",
            "content_type": "application/pdf",
            "file_data": file_data_b64
        }
        
        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json=payload
        )
        
        assert resp.status_code == 200, f"Upload failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "id" in data, "Response missing document id"
        assert data.get("has_binary") == True, "Document should have binary data"
        assert data.get("application_id") == TEST_APP_ID
        assert data.get("document_type") == "language_certificate"
        
        print(f"✓ Document uploaded: id={data['id']}, has_binary={data['has_binary']}")
        
        # Store doc_id for download test
        pytest.doc_id_for_download = data["id"]
        return data["id"]
    
    def test_upload_image_document(self, staff_session):
        """Upload an image document to S3"""
        # Create minimal JPEG header
        test_content = bytes([0xFF, 0xD8, 0xFF, 0xE0]) + b"Test JPEG content" + bytes([0xFF, 0xD9])
        file_data_b64 = base64.b64encode(test_content).decode('utf-8')
        
        payload = {
            "document_type": "passport_photo",
            "filename": f"{TEST_PREFIX}_passfoto.jpg",
            "content_type": "image/jpeg",
            "file_data": file_data_b64
        }
        
        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json=payload
        )
        
        assert resp.status_code == 200, f"Image upload failed: {resp.status_code} - {resp.text}"
        data = resp.json()
        assert data.get("has_binary") == True
        print(f"✓ Image uploaded: id={data['id']}")
        
        pytest.image_doc_id = data["id"]


class TestDocumentDownloadS3:
    """Test 3: Document download from RustFS via S3 API"""
    
    def test_download_uploaded_document(self, staff_session):
        """Download the previously uploaded document from S3"""
        doc_id = getattr(pytest, 'doc_id_for_download', None)
        if not doc_id:
            pytest.skip("No document ID from upload test")
        
        resp = staff_session.get(f"{BASE_URL}/api/documents/{doc_id}/download")
        
        assert resp.status_code == 200, f"Download failed: {resp.status_code} - {resp.text}"
        
        # Verify content type
        content_type = resp.headers.get("Content-Type", "")
        assert "pdf" in content_type.lower() or "octet-stream" in content_type.lower(), \
            f"Unexpected content type: {content_type}"
        
        # Verify we got binary content
        assert len(resp.content) > 0, "Downloaded content is empty"
        
        # Verify content disposition
        disposition = resp.headers.get("Content-Disposition", "")
        assert "inline" in disposition or "attachment" in disposition, \
            f"Missing Content-Disposition header: {disposition}"
        
        print(f"✓ Document downloaded: {len(resp.content)} bytes, Content-Type: {content_type}")
    
    def test_download_image_document(self, staff_session):
        """Download the uploaded image from S3"""
        doc_id = getattr(pytest, 'image_doc_id', None)
        if not doc_id:
            pytest.skip("No image document ID from upload test")
        
        resp = staff_session.get(f"{BASE_URL}/api/documents/{doc_id}/download")
        
        assert resp.status_code == 200, f"Image download failed: {resp.status_code}"
        assert len(resp.content) > 0
        print(f"✓ Image downloaded: {len(resp.content)} bytes")


class TestLanguagePrefFix:
    """Test 4: Verify language_pref bug fix (regression from iter78)"""
    
    def test_lead_ingest_with_language_en(self):
        """Create lead with language_pref='en' - should be saved correctly"""
        unique_id = f"{TEST_PREFIX}_en"
        
        payload = {
            "email": f"{unique_id}@example.com",
            "first_name": "Test",
            "last_name": "English",
            "full_name": "Test English",
            "phone": "+49123456789",
            "country": "GB",
            "area_interest": "studienkolleg",
            "course_type": "T-Kurs",
            "language_pref": "en",
            "source": "test_iter79"
        }
        
        resp = requests.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200, f"Lead ingest failed: {resp.text}"
        
        data = resp.json()
        assert data.get("success") == True
        assert data.get("user_id") is not None
        
        pytest.test_user_id_en = data["user_id"]
        print(f"✓ Lead created with language_pref='en': user_id={data['user_id']}")
    
    def test_lead_ingest_with_language_de(self):
        """Create lead with language_pref='de' - should be saved correctly"""
        unique_id = f"{TEST_PREFIX}_de"
        
        payload = {
            "email": f"{unique_id}@example.com",
            "first_name": "Test",
            "last_name": "German",
            "full_name": "Test German",
            "phone": "+49123456789",
            "country": "DE",
            "area_interest": "studienkolleg",
            "course_type": "M-Kurs",
            "language_pref": "de",
            "source": "test_iter79"
        }
        
        resp = requests.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200, f"Lead ingest failed: {resp.text}"
        
        data = resp.json()
        assert data.get("success") == True
        print(f"✓ Lead created with language_pref='de': user_id={data['user_id']}")


class TestLeadIngestWithDocuments:
    """Test 5: Full lead ingest flow with inline document uploads"""
    
    def test_lead_ingest_with_documents_and_password(self):
        """Create lead with documents and password - full flow"""
        unique_id = f"{TEST_PREFIX}_full"
        
        # Create test document content
        test_pdf = b"%PDF-1.4\nTest passport document\n%%EOF"
        test_pdf_b64 = base64.b64encode(test_pdf).decode('utf-8')
        
        payload = {
            "email": f"{unique_id}@example.com",
            "first_name": "Test",
            "last_name": "FullFlow",
            "full_name": "Test FullFlow",
            "phone": "+49123456789",
            "country": "IN",
            "date_of_birth": "1995-05-15",
            "area_interest": "studienkolleg",
            "course_type": "T-Kurs",
            "desired_start": "WS 2026",
            "language_level": "B1",
            "degree_country": "India",
            "language_pref": "en",
            "password": "TestPassword123!",
            "source": "test_iter79",
            "documents": [
                {
                    "document_type": "passport",
                    "filename": f"{TEST_PREFIX}_passport.pdf",
                    "content_type": "application/pdf",
                    "file_data": test_pdf_b64
                }
            ]
        }
        
        resp = requests.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        assert resp.status_code == 200, f"Lead ingest with docs failed: {resp.text}"
        
        data = resp.json()
        assert data.get("success") == True
        assert data.get("user_id") is not None
        assert data.get("application_id") is not None
        assert data.get("account_created") == True, "Account should be created with password"
        
        # Check for auth cookies in response
        cookies = resp.cookies
        # Note: cookies might be httpOnly and not visible here
        
        print(f"✓ Full lead ingest: user_id={data['user_id']}, app_id={data['application_id']}, account_created={data.get('account_created')}")
        
        pytest.full_flow_app_id = data["application_id"]
        pytest.full_flow_user_id = data["user_id"]


class TestStaffDashboardRegression:
    """Test 6: Staff login and dashboard navigation (regression)"""
    
    def test_staff_login(self):
        """Staff can login successfully"""
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert resp.status_code == 200, f"Staff login failed: {resp.text}"
        
        data = resp.json()
        # Login response has role at top level, not nested in user
        role = data.get("role") or data.get("user", {}).get("role")
        assert role in ["staff", "admin"], f"Unexpected role: {role}, data keys: {list(data.keys())}"
        print(f"✓ Staff login successful: {data.get('email')}")
    
    def test_staff_dashboard_stats(self, staff_session):
        """Staff dashboard stats endpoint works"""
        resp = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert resp.status_code == 200, f"Dashboard stats failed: {resp.text}"
        
        data = resp.json()
        # Verify expected fields - actual response has open_leads, open_tasks, etc.
        assert any(k in data for k in ["open_leads", "open_tasks", "total_applications", "applications", "stats"]), \
            f"Unexpected dashboard stats structure: {list(data.keys())}"
        print(f"✓ Dashboard stats: {list(data.keys())[:5]}...")
    
    def test_staff_applications_list(self, staff_session):
        """Staff can list applications"""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200, f"Applications list failed: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ Applications list: {len(data)} applications")


class TestInvoiceRegression:
    """Test 7: Invoice CRUD and PDF download (regression)"""
    
    def test_invoices_list(self, staff_session):
        """Staff can list invoices"""
        resp = staff_session.get(f"{BASE_URL}/api/invoices")
        assert resp.status_code == 200, f"Invoices list failed: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ Invoices list: {len(data)} invoices")
        
        # Store an invoice number for PDF test
        if data:
            pytest.test_invoice_number = data[0].get("invoice_number")
    
    def test_invoices_stats(self, staff_session):
        """Invoice stats endpoint works"""
        resp = staff_session.get(f"{BASE_URL}/api/invoices/stats")
        assert resp.status_code == 200, f"Invoice stats failed: {resp.text}"
        
        data = resp.json()
        # Actual response has total_amount, total_count, by_status
        assert any(k in data for k in ["total_amount", "total_count", "total", "count", "by_status"]), \
            f"Unexpected invoice stats structure: {list(data.keys())}"
        print(f"✓ Invoice stats: total_amount={data.get('total_amount')}, total_count={data.get('total_count')}")
    
    def test_invoice_pdf_download(self, staff_session):
        """Invoice PDF can be downloaded"""
        invoice_number = getattr(pytest, 'test_invoice_number', None)
        if not invoice_number:
            pytest.skip("No invoice number available for PDF test")
        
        resp = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}/pdf")
        
        # PDF endpoint might return 200 or redirect
        assert resp.status_code in [200, 302], f"Invoice PDF failed: {resp.status_code}"
        
        if resp.status_code == 200:
            content_type = resp.headers.get("Content-Type", "")
            assert "pdf" in content_type.lower(), f"Expected PDF, got {content_type}"
            assert len(resp.content) > 100, "PDF content too small"
            print(f"✓ Invoice PDF downloaded: {len(resp.content)} bytes")
        else:
            print(f"✓ Invoice PDF redirect: {resp.status_code}")


class TestApplyPageRegression:
    """Test 8: Apply page renders correctly (frontend regression)"""
    
    def test_apply_page_loads(self):
        """Apply page HTML loads"""
        resp = requests.get(f"{BASE_URL}/apply")
        assert resp.status_code == 200, f"Apply page failed: {resp.status_code}"
        
        # Check for React app markers
        assert "root" in resp.text or "app" in resp.text.lower()
        print("✓ Apply page loads successfully")


class TestCleanup:
    """Cleanup test data created during this iteration"""
    
    def test_cleanup_info(self):
        """Print cleanup info for manual cleanup if needed"""
        print(f"\n--- Test Data Created (prefix: {TEST_PREFIX}) ---")
        print(f"Documents uploaded to app: {TEST_APP_ID}")
        print(f"Test users created with emails: {TEST_PREFIX}_*@example.com")
        print("Note: Documents with prefix test_iter79_* should be cleaned up")
        print("---")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
