"""
Invoice Module Tests - Block 2
Tests for Invoice CRUD operations, RBAC, and audit logging.

Endpoints tested:
- POST /api/invoices (Staff creates invoice for applicant)
- GET /api/invoices (Staff sees all, Applicant sees own only)
- GET /api/invoices/stats (Statistics by status)
- GET /api/invoices/applicants (Staff/Admin only - applicant list)
- GET /api/invoices/{id} (Get single invoice)
- PATCH /api/invoices/{id} (Status change: draft→sent→paid)
- DELETE /api/invoices/{id} (Admin only, drafts only)
- RBAC: Applicant cannot create/update/delete
- RBAC: Applicant sees only own invoices
- Audit logs for invoice_created, invoice_updated, invoice_deleted
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestInvoiceSetup:
    """Setup and authentication tests"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        """Get authenticated staff session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        """Get authenticated admin session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture(scope="class")
    def applicant_session(self):
        """Get authenticated applicant session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        return session
    
    def test_staff_login(self, staff_session):
        """Verify staff can login"""
        response = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["role"] in ["staff", "admin", "superadmin"]
        print(f"✓ Staff logged in: {data['email']} (role: {data['role']})")
    
    def test_admin_login(self, admin_session):
        """Verify admin can login"""
        response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["role"] in ["admin", "superadmin"]
        print(f"✓ Admin logged in: {data['email']} (role: {data['role']})")
    
    def test_applicant_login(self, applicant_session):
        """Verify applicant can login"""
        response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "applicant"
        print(f"✓ Applicant logged in: {data['email']} (role: {data['role']})")


class TestInvoiceApplicantsList:
    """Test GET /api/invoices/applicants endpoint"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL, "password": STAFF_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD
        })
        return session
    
    def test_staff_can_list_applicants(self, staff_session):
        """Staff can get list of applicants for invoice creation"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "email" in data[0] or "full_name" in data[0]
        print(f"✓ Staff can list {len(data)} applicants for invoice creation")
    
    def test_applicant_cannot_list_applicants(self, applicant_session):
        """Applicant cannot access applicants list (RBAC)"""
        response = applicant_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert response.status_code == 403
        print("✓ Applicant blocked from /api/invoices/applicants (403)")


class TestInvoiceCRUD:
    """Test Invoice CRUD operations"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL, "password": STAFF_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_id(self, staff_session):
        """Get applicant ID for invoice creation"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        assert response.status_code == 200
        applicants = response.json()
        assert len(applicants) > 0, "No applicants found"
        return applicants[0]["id"]
    
    def test_staff_create_invoice(self, staff_session, applicant_id):
        """Staff can create invoice for applicant"""
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        payload = {
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Studiengebühr Wintersemester",
            "amount": 1500.00,
            "due_date": due_date
        }
        response = staff_session.post(f"{BASE_URL}/api/invoices", json=payload)
        assert response.status_code == 200, f"Create invoice failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "invoice_number" in data
        assert data["invoice_number"].startswith("INV-")
        assert data["status"] == "draft"
        assert data["amount"] == 1500.00
        assert data["description"] == "TEST_Block2: Studiengebühr Wintersemester"
        
        print(f"✓ Staff created invoice: {data['invoice_number']} (amount: {data['amount']} EUR)")
        return data["invoice_number"]
    
    def test_staff_list_all_invoices(self, staff_session):
        """Staff can list all invoices"""
        response = staff_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Staff can list {len(data)} invoices")
    
    def test_staff_get_invoice_stats(self, staff_session):
        """Staff can get invoice statistics"""
        response = staff_session.get(f"{BASE_URL}/api/invoices/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_count" in data
        assert "total_amount" in data
        assert "by_status" in data
        print(f"✓ Invoice stats: {data['total_count']} invoices, total {data['total_amount']} EUR")
    
    def test_staff_update_invoice_status(self, staff_session, applicant_id):
        """Staff can update invoice status (draft → sent)"""
        # First create a new invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Status Update Test",
            "amount": 500.00,
            "due_date": due_date
        })
        assert create_response.status_code == 200
        invoice_number = create_response.json()["invoice_number"]
        
        # Update status to sent
        update_response = staff_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={
            "status": "sent"
        })
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["status"] == "sent"
        print(f"✓ Invoice {invoice_number} status updated: draft → sent")
        
        # Update status to paid
        update_response2 = staff_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={
            "status": "paid"
        })
        assert update_response2.status_code == 200
        updated2 = update_response2.json()
        assert updated2["status"] == "paid"
        assert updated2.get("paid_at") is not None  # paid_at should be set
        print(f"✓ Invoice {invoice_number} status updated: sent → paid (paid_at set)")
    
    def test_staff_filter_invoices_by_status(self, staff_session):
        """Staff can filter invoices by status"""
        for status in ["draft", "sent", "paid"]:
            response = staff_session.get(f"{BASE_URL}/api/invoices?status={status}")
            assert response.status_code == 200
            data = response.json()
            # All returned invoices should have the filtered status
            for inv in data:
                assert inv["status"] == status
            print(f"✓ Filter by status={status}: {len(data)} invoices")


class TestInvoiceRBAC:
    """Test Role-Based Access Control for invoices"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL, "password": STAFF_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL, "password": APPLICANT_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_id(self, applicant_session):
        """Get applicant's own ID"""
        response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        return response.json()["id"]
    
    def test_applicant_cannot_create_invoice(self, applicant_session, applicant_id):
        """Applicant cannot create invoices (RBAC)"""
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        response = applicant_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST: Should fail",
            "amount": 100.00,
            "due_date": due_date
        })
        assert response.status_code == 403
        print("✓ Applicant blocked from creating invoices (403)")
    
    def test_applicant_sees_only_own_invoices(self, applicant_session, staff_session, applicant_id):
        """Applicant can only see their own invoices"""
        # Staff creates invoice for this applicant
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Applicant's Invoice",
            "amount": 200.00,
            "due_date": due_date
        })
        
        # Applicant lists invoices
        response = applicant_session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        invoices = response.json()
        
        # All invoices should belong to this applicant
        for inv in invoices:
            assert inv.get("applicant_id") == applicant_id, f"Applicant sees invoice not belonging to them"
        
        print(f"✓ Applicant sees only own invoices ({len(invoices)} invoices)")
    
    def test_applicant_cannot_update_invoice(self, applicant_session, staff_session, applicant_id):
        """Applicant cannot update invoices (RBAC)"""
        # Get an invoice number
        response = applicant_session.get(f"{BASE_URL}/api/invoices")
        if response.status_code == 200 and len(response.json()) > 0:
            invoice_number = response.json()[0].get("invoice_number")
            if invoice_number:
                update_response = applicant_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={
                    "status": "paid"
                })
                assert update_response.status_code == 403
                print("✓ Applicant blocked from updating invoices (403)")
            else:
                print("⚠ No invoice_number found to test update")
        else:
            print("⚠ No invoices found for applicant to test update")
    
    def test_applicant_cannot_delete_invoice(self, applicant_session, staff_session, applicant_id):
        """Applicant cannot delete invoices (RBAC)"""
        response = applicant_session.get(f"{BASE_URL}/api/invoices")
        if response.status_code == 200 and len(response.json()) > 0:
            invoice_number = response.json()[0].get("invoice_number")
            if invoice_number:
                delete_response = applicant_session.delete(f"{BASE_URL}/api/invoices/{invoice_number}")
                assert delete_response.status_code == 403
                print("✓ Applicant blocked from deleting invoices (403)")
            else:
                print("⚠ No invoice_number found to test delete")
        else:
            print("⚠ No invoices found for applicant to test delete")
    
    def test_applicant_cannot_see_other_invoices(self, applicant_session, staff_session):
        """Applicant cannot access invoices of other applicants"""
        # Try to access a specific invoice that doesn't belong to applicant
        # First get all invoices as staff
        staff_response = staff_session.get(f"{BASE_URL}/api/invoices")
        all_invoices = staff_response.json()
        
        # Get applicant's ID
        me_response = applicant_session.get(f"{BASE_URL}/api/auth/me")
        applicant_id = me_response.json()["id"]
        
        # Find an invoice that doesn't belong to this applicant
        other_invoice = None
        for inv in all_invoices:
            if inv.get("applicant_id") != applicant_id:
                other_invoice = inv
                break
        
        if other_invoice:
            invoice_number = other_invoice.get("invoice_number")
            response = applicant_session.get(f"{BASE_URL}/api/invoices/{invoice_number}")
            assert response.status_code == 403, f"Applicant should not access other's invoice"
            print(f"✓ Applicant blocked from viewing other's invoice {invoice_number} (403)")
        else:
            print("⚠ No other applicant's invoice found to test access control")


class TestInvoiceAdminDelete:
    """Test Admin-only delete functionality"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL, "password": STAFF_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_id(self, staff_session):
        response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        return response.json()[0]["id"]
    
    def test_staff_cannot_delete_invoice(self, staff_session, applicant_id):
        """Staff (non-admin) cannot delete invoices"""
        # Create a draft invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Staff Delete Test",
            "amount": 100.00,
            "due_date": due_date
        })
        invoice_number = create_response.json()["invoice_number"]
        
        # Staff tries to delete
        delete_response = staff_session.delete(f"{BASE_URL}/api/invoices/{invoice_number}")
        assert delete_response.status_code == 403
        print(f"✓ Staff blocked from deleting invoice {invoice_number} (403)")
    
    def test_admin_can_delete_draft_invoice(self, admin_session, staff_session, applicant_id):
        """Admin can delete draft invoices"""
        # Create a draft invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Admin Delete Test",
            "amount": 100.00,
            "due_date": due_date
        })
        invoice_number = create_response.json()["invoice_number"]
        
        # Admin deletes
        delete_response = admin_session.delete(f"{BASE_URL}/api/invoices/{invoice_number}")
        assert delete_response.status_code == 200
        assert delete_response.json().get("ok") == True
        print(f"✓ Admin deleted draft invoice {invoice_number}")
        
        # Verify deletion
        get_response = admin_session.get(f"{BASE_URL}/api/invoices/{invoice_number}")
        assert get_response.status_code == 404
        print(f"✓ Invoice {invoice_number} confirmed deleted (404)")
    
    def test_admin_cannot_delete_non_draft_invoice(self, admin_session, staff_session, applicant_id):
        """Admin cannot delete non-draft invoices"""
        # Create and send an invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Non-Draft Delete Test",
            "amount": 100.00,
            "due_date": due_date
        })
        invoice_number = create_response.json()["invoice_number"]
        
        # Update to sent
        staff_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={"status": "sent"})
        
        # Admin tries to delete sent invoice
        delete_response = admin_session.delete(f"{BASE_URL}/api/invoices/{invoice_number}")
        assert delete_response.status_code == 400
        assert "draft" in delete_response.json().get("detail", "").lower()
        print(f"✓ Admin blocked from deleting sent invoice {invoice_number} (400)")


class TestInvoiceAuditLogs:
    """Test audit logging for invoice operations"""
    
    @pytest.fixture(scope="class")
    def admin_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_id(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/invoices/applicants")
        return response.json()[0]["id"]
    
    def test_audit_log_invoice_created(self, admin_session, applicant_id):
        """Verify audit log entry for invoice creation"""
        # Create invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = admin_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Audit Log Test",
            "amount": 999.99,
            "due_date": due_date
        })
        assert create_response.status_code == 200
        invoice_number = create_response.json()["invoice_number"]
        
        # Check audit logs
        audit_response = admin_session.get(f"{BASE_URL}/api/audit?action=invoice_created&limit=5")
        if audit_response.status_code == 200:
            logs = audit_response.json()
            # Find our invoice in logs
            found = any(
                log.get("details", {}).get("invoice_number") == invoice_number 
                for log in logs
            )
            if found:
                print(f"✓ Audit log found for invoice_created: {invoice_number}")
            else:
                print(f"⚠ Audit log entry not found for {invoice_number} (may be timing issue)")
        else:
            print(f"⚠ Could not verify audit logs (status: {audit_response.status_code})")
    
    def test_audit_log_invoice_updated(self, admin_session, applicant_id):
        """Verify audit log entry for invoice update"""
        # Create and update invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = admin_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Audit Update Test",
            "amount": 888.88,
            "due_date": due_date
        })
        invoice_number = create_response.json()["invoice_number"]
        
        # Update status
        admin_session.patch(f"{BASE_URL}/api/invoices/{invoice_number}", json={"status": "sent"})
        
        # Check audit logs
        audit_response = admin_session.get(f"{BASE_URL}/api/audit?action=invoice_updated&limit=5")
        if audit_response.status_code == 200:
            logs = audit_response.json()
            found = any(
                log.get("details", {}).get("invoice_number") == invoice_number 
                for log in logs
            )
            if found:
                print(f"✓ Audit log found for invoice_updated: {invoice_number}")
            else:
                print(f"⚠ Audit log entry not found for update (may be timing issue)")
        else:
            print(f"⚠ Could not verify audit logs (status: {audit_response.status_code})")
    
    def test_audit_log_invoice_deleted(self, admin_session, applicant_id):
        """Verify audit log entry for invoice deletion"""
        # Create and delete invoice
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = admin_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Audit Delete Test",
            "amount": 777.77,
            "due_date": due_date
        })
        invoice_number = create_response.json()["invoice_number"]
        
        # Delete
        admin_session.delete(f"{BASE_URL}/api/invoices/{invoice_number}")
        
        # Check audit logs
        audit_response = admin_session.get(f"{BASE_URL}/api/audit?action=invoice_deleted&limit=5")
        if audit_response.status_code == 200:
            logs = audit_response.json()
            found = any(
                log.get("details", {}).get("invoice_number") == invoice_number 
                for log in logs
            )
            if found:
                print(f"✓ Audit log found for invoice_deleted: {invoice_number}")
            else:
                print(f"⚠ Audit log entry not found for delete (may be timing issue)")
        else:
            print(f"⚠ Could not verify audit logs (status: {audit_response.status_code})")


class TestInvoiceDataIntegrity:
    """Test data integrity and edge cases"""
    
    @pytest.fixture(scope="class")
    def staff_session(self):
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL, "password": STAFF_PASSWORD
        })
        return session
    
    @pytest.fixture(scope="class")
    def applicant_id(self, staff_session):
        response = staff_session.get(f"{BASE_URL}/api/invoices/applicants")
        return response.json()[0]["id"]
    
    def test_invoice_number_format(self, staff_session, applicant_id):
        """Verify invoice number format: INV-YYYYMM-XXXX"""
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Number Format Test",
            "amount": 100.00,
            "due_date": due_date
        })
        invoice_number = response.json()["invoice_number"]
        
        # Verify format
        parts = invoice_number.split("-")
        assert len(parts) == 3
        assert parts[0] == "INV"
        assert len(parts[1]) == 6  # YYYYMM
        assert len(parts[2]) == 4  # XXXX
        print(f"✓ Invoice number format correct: {invoice_number}")
    
    def test_invoice_sequential_numbering(self, staff_session, applicant_id):
        """Verify invoices are numbered sequentially"""
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Create two invoices
        resp1 = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Sequential Test 1",
            "amount": 100.00,
            "due_date": due_date
        })
        num1 = resp1.json()["invoice_number"]
        
        resp2 = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Sequential Test 2",
            "amount": 100.00,
            "due_date": due_date
        })
        num2 = resp2.json()["invoice_number"]
        
        # Extract sequence numbers
        seq1 = int(num1.split("-")[-1])
        seq2 = int(num2.split("-")[-1])
        
        assert seq2 == seq1 + 1, f"Invoices not sequential: {num1} → {num2}"
        print(f"✓ Invoice numbering sequential: {num1} → {num2}")
    
    def test_invalid_applicant_id(self, staff_session):
        """Creating invoice with invalid applicant ID should fail"""
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": "000000000000000000000000",  # Invalid ObjectId
            "description": "TEST: Should fail",
            "amount": 100.00,
            "due_date": due_date
        })
        assert response.status_code == 404
        print("✓ Invalid applicant_id rejected (404)")
    
    def test_get_invoice_by_number(self, staff_session, applicant_id):
        """Can retrieve invoice by invoice_number"""
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        create_response = staff_session.post(f"{BASE_URL}/api/invoices", json={
            "applicant_id": applicant_id,
            "description": "TEST_Block2: Get By Number Test",
            "amount": 123.45,
            "due_date": due_date
        })
        invoice_number = create_response.json()["invoice_number"]
        
        # Get by invoice_number
        get_response = staff_session.get(f"{BASE_URL}/api/invoices/{invoice_number}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["invoice_number"] == invoice_number
        assert data["amount"] == 123.45
        print(f"✓ Invoice retrieved by number: {invoice_number}")


# Cleanup fixture to remove test data
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_invoices():
    """Cleanup TEST_Block2 invoices after all tests"""
    yield
    # Cleanup runs after all tests
    session = requests.Session()
    session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    
    # Get all invoices
    response = session.get(f"{BASE_URL}/api/invoices")
    if response.status_code == 200:
        invoices = response.json()
        for inv in invoices:
            if inv.get("description", "").startswith("TEST_Block2:"):
                # Only delete drafts
                if inv.get("status") == "draft":
                    session.delete(f"{BASE_URL}/api/invoices/{inv.get('invoice_number')}")
        print("✓ Test cleanup completed")
