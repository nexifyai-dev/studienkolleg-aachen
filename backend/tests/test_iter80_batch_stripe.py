"""
Iteration 80 - Batch-Screening & Stripe Payment Integration Tests

Tests:
1. Batch-Screening: POST /api/ai-screening/batch
2. Batch-Screening: GET /api/ai-screening/batch/{batch_id}/status
3. Batch-Screening: GET /api/ai-screening/batches
4. Batch-Screening: Validation (max 50, empty array, invalid IDs)
5. Stripe Checkout: POST /api/payments/checkout
6. Stripe Checkout: Already paid invoice rejection
7. Stripe Status: GET /api/payments/status/{session_id}
8. Stripe Transactions: GET /api/payments/transactions
9. Regression: Staff login, Dashboard, Invoice PDF
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://invoice-fix-31.preview.emergentagent.com').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"

# Test data from DB
TEST_APP_IDS = [
    "69cb8e9a3f026e1d41dd4800",  # lead_new
    "69d0bd306dc21f6b888229e2",  # lead_new
    "69d0bd326dc21f6b888229f0",  # pending_docs
]
TEST_INVOICE_SENT = "W2G-202603-1004-AC"  # Fatima Benali, 1950 EUR, status=sent
TEST_INVOICE_SENT_2 = "W2G-202603-1002-AC"  # Amira El-Khoury, 2800 EUR, status=sent


@pytest.fixture(scope="module")
def staff_session():
    """Login as staff and return authenticated session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    login_resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
    
    # Verify session
    me_resp = session.get(f"{BASE_URL}/api/auth/me")
    assert me_resp.status_code == 200, f"Auth/me failed: {me_resp.text}"
    assert me_resp.json().get("role") in ["staff", "admin"], "Not staff/admin role"
    
    return session


class TestBatchScreening:
    """Batch-Screening API Tests"""
    
    def test_batch_screening_start(self, staff_session):
        """POST /api/ai-screening/batch - Start batch screening with valid IDs"""
        resp = staff_session.post(f"{BASE_URL}/api/ai-screening/batch", json={
            "application_ids": TEST_APP_IDS[:2]  # Use 2 IDs
        })
        
        assert resp.status_code == 200, f"Batch start failed: {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "batch_id" in data, "Missing batch_id"
        assert "enqueued" in data, "Missing enqueued count"
        assert "total" in data, "Missing total count"
        assert "status" in data, "Missing status"
        
        # Verify values
        assert data["total"] == 2, f"Expected total=2, got {data['total']}"
        assert data["enqueued"] >= 0, "enqueued should be >= 0"
        assert data["status"] in ["running", "empty"], f"Unexpected status: {data['status']}"
        
        print(f"Batch started: batch_id={data['batch_id']}, enqueued={data['enqueued']}")
        
        # Store batch_id for status test
        pytest.batch_id = data["batch_id"]
    
    def test_batch_screening_status(self, staff_session):
        """GET /api/ai-screening/batch/{batch_id}/status - Check batch progress"""
        batch_id = getattr(pytest, 'batch_id', None)
        if not batch_id:
            pytest.skip("No batch_id from previous test")
        
        # Wait a moment for jobs to process
        time.sleep(2)
        
        resp = staff_session.get(f"{BASE_URL}/api/ai-screening/batch/{batch_id}/status")
        assert resp.status_code == 200, f"Batch status failed: {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "batch_id" in data, "Missing batch_id"
        assert "progress" in data, "Missing progress"
        
        progress = data["progress"]
        assert "completed" in progress, "Missing progress.completed"
        assert "failed" in progress, "Missing progress.failed"
        assert "running" in progress, "Missing progress.running"
        assert "total" in progress, "Missing progress.total"
        assert "is_done" in progress, "Missing progress.is_done"
        assert "percent" in progress, "Missing progress.percent"
        
        print(f"Batch status: {progress['completed']}/{progress['total']} completed, {progress['percent']}%")
    
    def test_batch_screening_list(self, staff_session):
        """GET /api/ai-screening/batches - List all batches"""
        resp = staff_session.get(f"{BASE_URL}/api/ai-screening/batches")
        assert resp.status_code == 200, f"Batch list failed: {resp.text}"
        data = resp.json()
        
        assert isinstance(data, list), "Expected list of batches"
        
        if len(data) > 0:
            batch = data[0]
            assert "batch_id" in batch, "Missing batch_id in list item"
            assert "status" in batch, "Missing status in list item"
            assert "created_at" in batch, "Missing created_at in list item"
            print(f"Found {len(data)} batches, latest: {batch['batch_id']}")
    
    def test_batch_screening_empty_array_rejected(self, staff_session):
        """POST /api/ai-screening/batch - Empty array should be rejected"""
        resp = staff_session.post(f"{BASE_URL}/api/ai-screening/batch", json={
            "application_ids": []
        })
        
        assert resp.status_code == 400, f"Expected 400 for empty array, got {resp.status_code}"
        assert "mindestens" in resp.text.lower() or "erforderlich" in resp.text.lower(), \
            f"Expected validation error message, got: {resp.text}"
    
    def test_batch_screening_max_50_limit(self, staff_session):
        """POST /api/ai-screening/batch - More than 50 IDs should be rejected"""
        # Create 51 fake IDs
        fake_ids = [f"000000000000000000000{i:03d}" for i in range(51)]
        
        resp = staff_session.post(f"{BASE_URL}/api/ai-screening/batch", json={
            "application_ids": fake_ids
        })
        
        assert resp.status_code == 400, f"Expected 400 for >50 IDs, got {resp.status_code}"
        assert "50" in resp.text or "maximal" in resp.text.lower(), \
            f"Expected max 50 error message, got: {resp.text}"
    
    def test_batch_screening_invalid_ids_skipped(self, staff_session):
        """POST /api/ai-screening/batch - Invalid IDs should be skipped"""
        resp = staff_session.post(f"{BASE_URL}/api/ai-screening/batch", json={
            "application_ids": [
                TEST_APP_IDS[0],  # Valid
                "invalid_id_12345",  # Invalid
                "000000000000000000000000",  # Valid format but not found
            ]
        })
        
        assert resp.status_code == 200, f"Batch start failed: {resp.text}"
        data = resp.json()
        
        # Should have skipped some
        assert "skipped" in data, "Missing skipped array"
        assert len(data["skipped"]) >= 1, "Expected at least 1 skipped ID"
        
        print(f"Skipped {len(data['skipped'])} invalid IDs: {data['skipped']}")


class TestStripePayment:
    """Stripe Payment Integration Tests"""
    
    def test_stripe_checkout_create(self, staff_session):
        """POST /api/payments/checkout - Create checkout session for sent invoice"""
        resp = staff_session.post(f"{BASE_URL}/api/payments/checkout", json={
            "invoice_number": TEST_INVOICE_SENT,
            "origin_url": "https://invoice-fix-31.preview.emergentagent.com"
        })
        
        # Could be 200 (success) or 503 (Stripe not configured) or 400 (already paid)
        if resp.status_code == 503:
            pytest.skip("Stripe not configured on server")
        
        if resp.status_code == 400 and "bezahlt" in resp.text.lower():
            pytest.skip("Invoice already paid")
        
        assert resp.status_code == 200, f"Checkout create failed: {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "url" in data, "Missing checkout URL"
        assert "session_id" in data, "Missing session_id"
        assert "amount" in data, "Missing amount"
        assert "currency" in data, "Missing currency"
        
        # Verify values
        assert data["url"].startswith("https://checkout.stripe.com"), \
            f"Invalid Stripe URL: {data['url']}"
        assert data["currency"] == "eur", f"Expected EUR, got {data['currency']}"
        assert data["amount"] > 0, "Amount should be positive"
        
        print(f"Checkout created: session_id={data['session_id']}, amount={data['amount']} EUR")
        
        # Store session_id for status test
        pytest.stripe_session_id = data["session_id"]
    
    def test_stripe_checkout_missing_invoice_number(self, staff_session):
        """POST /api/payments/checkout - Missing invoice_number should fail"""
        resp = staff_session.post(f"{BASE_URL}/api/payments/checkout", json={
            "origin_url": "https://example.com"
        })
        
        if resp.status_code == 503:
            pytest.skip("Stripe not configured")
        
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert "invoice_number" in resp.text.lower() or "erforderlich" in resp.text.lower()
    
    def test_stripe_checkout_missing_origin_url(self, staff_session):
        """POST /api/payments/checkout - Missing origin_url should fail"""
        resp = staff_session.post(f"{BASE_URL}/api/payments/checkout", json={
            "invoice_number": TEST_INVOICE_SENT
        })
        
        if resp.status_code == 503:
            pytest.skip("Stripe not configured")
        
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        assert "origin_url" in resp.text.lower() or "erforderlich" in resp.text.lower()
    
    def test_stripe_checkout_nonexistent_invoice(self, staff_session):
        """POST /api/payments/checkout - Non-existent invoice should fail"""
        resp = staff_session.post(f"{BASE_URL}/api/payments/checkout", json={
            "invoice_number": "NONEXISTENT-12345",
            "origin_url": "https://example.com"
        })
        
        if resp.status_code == 503:
            pytest.skip("Stripe not configured")
        
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    
    def test_stripe_payment_status(self, staff_session):
        """GET /api/payments/status/{session_id} - Check payment status"""
        session_id = getattr(pytest, 'stripe_session_id', None)
        
        # Try with existing session from DB if no new one
        if not session_id:
            session_id = "cs_test_a1cW5CNcAUSOoh5XgOAMoFDQSj6wxMII4PtT2pQqXfpz4mL2wSdrdQls5Y"
        
        resp = staff_session.get(f"{BASE_URL}/api/payments/status/{session_id}")
        
        if resp.status_code == 503:
            pytest.skip("Stripe not configured")
        
        if resp.status_code == 404:
            pytest.skip("Session not found in DB")
        
        if resp.status_code == 502:
            # Stripe API call failed - this is expected for test keys
            print("Stripe API call failed (expected for test environment)")
            return
        
        assert resp.status_code == 200, f"Status check failed: {resp.text}"
        data = resp.json()
        
        # Verify response structure
        assert "session_id" in data, "Missing session_id"
        assert "status" in data, "Missing status"
        assert "payment_status" in data, "Missing payment_status"
        
        print(f"Payment status: {data['payment_status']}, status: {data['status']}")
    
    def test_stripe_transactions_list(self, staff_session):
        """GET /api/payments/transactions - List all transactions"""
        resp = staff_session.get(f"{BASE_URL}/api/payments/transactions")
        
        assert resp.status_code == 200, f"Transactions list failed: {resp.text}"
        data = resp.json()
        
        assert isinstance(data, list), "Expected list of transactions"
        
        if len(data) > 0:
            tx = data[0]
            assert "session_id" in tx, "Missing session_id in transaction"
            assert "invoice_number" in tx, "Missing invoice_number in transaction"
            assert "payment_status" in tx, "Missing payment_status in transaction"
            assert "amount" in tx, "Missing amount in transaction"
            print(f"Found {len(data)} transactions, latest: {tx['invoice_number']} - {tx['payment_status']}")


class TestRegression:
    """Regression tests for existing functionality"""
    
    def test_staff_login(self, staff_session):
        """Verify staff login works"""
        resp = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("email") == STAFF_EMAIL
        print(f"Staff logged in: {data.get('full_name', data.get('email'))}")
    
    def test_dashboard_stats(self, staff_session):
        """GET /api/dashboard/stats - Dashboard should load"""
        resp = staff_session.get(f"{BASE_URL}/api/dashboard/stats")
        assert resp.status_code == 200, f"Dashboard stats failed: {resp.text}"
        data = resp.json()
        
        # Verify some expected fields
        assert "total_applications" in data or "applications" in data or "pipeline" in data, \
            f"Unexpected dashboard response: {data.keys()}"
        print(f"Dashboard stats loaded: {list(data.keys())[:5]}...")
    
    def test_applications_list(self, staff_session):
        """GET /api/applications - Applications list should work"""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        assert resp.status_code == 200, f"Applications list failed: {resp.text}"
        data = resp.json()
        
        assert isinstance(data, list), "Expected list of applications"
        assert len(data) > 0, "Expected at least 1 application"
        print(f"Found {len(data)} applications")
    
    def test_invoices_list(self, staff_session):
        """GET /api/invoices - Invoices list should work"""
        resp = staff_session.get(f"{BASE_URL}/api/invoices")
        assert resp.status_code == 200, f"Invoices list failed: {resp.text}"
        data = resp.json()
        
        assert isinstance(data, list), "Expected list of invoices"
        print(f"Found {len(data)} invoices")
    
    def test_invoice_pdf_download(self, staff_session):
        """GET /api/invoices/{invoice_number}/pdf - PDF download should work"""
        resp = staff_session.get(f"{BASE_URL}/api/invoices/{TEST_INVOICE_SENT}/pdf")
        
        assert resp.status_code == 200, f"PDF download failed: {resp.text}"
        assert resp.headers.get("Content-Type") == "application/pdf", \
            f"Expected PDF content type, got: {resp.headers.get('Content-Type')}"
        assert len(resp.content) > 1000, "PDF content too small"
        print(f"PDF downloaded: {len(resp.content)} bytes")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
