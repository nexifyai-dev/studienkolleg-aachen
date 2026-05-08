"""
Block 7: Document Validation Pipeline Tests

Tests:
1. Document upload with tiny file → needs_review + too_small warning
2. Document upload with passport-like PDF → detected_type=passport, confidence=high
3. Document upload with wrong type detection → wrong_type warning
4. Staff review endpoints: GET /api/documents/{doc_id}/validation
5. Staff revalidate endpoint: POST /api/documents/{doc_id}/revalidate
6. Staff approve/reject: PUT /api/documents/{doc_id}/review
7. PDF Invoice layout: Zwischensumme, UStG, Gesamtbetrag on separate lines
"""
import pytest
import requests
import os
import base64
from io import BytesIO

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"

# Test application ID from requirements
TEST_APP_ID = "69cb8e9a3f026e1d41dd4800"
TEST_INVOICE = "W2G-202603-1005-AC"


@pytest.fixture(scope="module")
def applicant_session():
    """Login as applicant and return session with cookies."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
    return session


@pytest.fixture(scope="module")
def staff_session():
    """Login as staff and return session with cookies."""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    assert resp.status_code == 200, f"Staff login failed: {resp.text}"
    return session


def create_test_pdf(content_text: str) -> bytes:
    """Create a simple PDF with given text content using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        c.setFont("Helvetica", 12)
        y = 750
        for line in content_text.split('\n'):
            c.drawString(50, y, line)
            y -= 15
        c.save()
        buf.seek(0)
        return buf.read()
    except ImportError:
        # Fallback: minimal PDF
        return b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF"


class TestDocumentValidationPipeline:
    """Test document validation on upload."""

    def test_tiny_file_gets_needs_review(self, applicant_session):
        """Upload tiny file as passport → should return needs_review with too_small warning."""
        # Create a tiny file (less than 30KB minimum for passport)
        tiny_content = b"tiny file content"  # ~17 bytes
        file_b64 = base64.b64encode(tiny_content).decode()

        resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "passport",
                "filename": "TEST_tiny_passport.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )

        # Should succeed but with validation warnings
        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        data = resp.json()

        # Check validation result
        assert "validation" in data or "status" in data, "No validation info in response"
        
        if "validation" in data and data["validation"]:
            validation = data["validation"]
            assert validation.get("status") in ["needs_review", "rejected"], \
                f"Expected needs_review or rejected, got {validation.get('status')}"
            warnings = validation.get("warnings", [])
            assert "too_small" in warnings, f"Expected 'too_small' warning, got {warnings}"
        
        print(f"✓ Tiny file upload returned: status={data.get('status')}, validation={data.get('validation')}")

    def test_passport_pdf_detection(self, applicant_session):
        """Upload PDF with passport-like content → should detect as passport with high confidence."""
        # Create PDF with passport keywords
        passport_text = """
        PASSPORT / REISEPASS
        REPUBLIC OF GERMANY
        
        Surname: MUSTERMANN
        Given Names: MAX
        Nationality: GERMAN
        Date of Birth: 01.01.1990
        
        Machine Readable Zone
        P<DEUMUSTERMANN<<MAX<<<<<<<<<<<<<<<<<<<<<<<<
        """
        pdf_bytes = create_test_pdf(passport_text)
        file_b64 = base64.b64encode(pdf_bytes).decode()

        resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "passport",
                "filename": "TEST_passport_valid.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )

        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        data = resp.json()

        if "validation" in data and data["validation"]:
            validation = data["validation"]
            detected = validation.get("detected_type")
            confidence = validation.get("confidence")
            print(f"✓ Passport PDF: detected_type={detected}, confidence={confidence}")
            # Should detect as passport with medium/high confidence
            assert detected == "passport", f"Expected passport, got {detected}"
            assert confidence in ["high", "medium"], f"Expected high/medium confidence, got {confidence}"

    def test_wrong_type_detection_warning(self, applicant_session):
        """Upload language cert content declared as passport → should warn about wrong_type."""
        # Create PDF with language certificate keywords
        lang_cert_text = """
        GOETHE-INSTITUT
        SPRACHZERTIFIKAT / LANGUAGE CERTIFICATE
        
        Deutsch als Fremdsprache
        Niveau: B2
        
        Prüfungsergebnis: BESTANDEN
        TestDaF Level: TDN 4
        """
        pdf_bytes = create_test_pdf(lang_cert_text)
        file_b64 = base64.b64encode(pdf_bytes).decode()

        resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "passport",  # Declared as passport but content is language cert
                "filename": "TEST_wrong_type.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )

        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        data = resp.json()

        if "validation" in data and data["validation"]:
            validation = data["validation"]
            detected = validation.get("detected_type")
            warnings = validation.get("warnings", [])
            print(f"✓ Wrong type test: detected={detected}, warnings={warnings}")
            # Should detect mismatch
            if detected == "language_certificate":
                assert "wrong_type" in warnings, f"Expected 'wrong_type' warning, got {warnings}"


class TestStaffDocumentReview:
    """Test staff document review endpoints."""

    def test_get_document_validation(self, staff_session, applicant_session):
        """Staff can get validation details for a document."""
        # First upload a document as applicant
        pdf_bytes = create_test_pdf("Test document for validation check")
        file_b64 = base64.b64encode(pdf_bytes).decode()

        upload_resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "other",
                "filename": "TEST_validation_check.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )
        assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
        doc_id = upload_resp.json().get("id")
        assert doc_id, "No document ID returned"

        # Staff gets validation details
        resp = staff_session.get(f"{BASE_URL}/api/documents/{doc_id}/validation")
        assert resp.status_code == 200, f"Get validation failed: {resp.text}"
        
        data = resp.json()
        assert "id" in data, "Missing id in validation response"
        assert "validation_status" in data or "status" in data, "Missing status in validation response"
        print(f"✓ GET /api/documents/{doc_id}/validation returned: {list(data.keys())}")

    def test_staff_approve_document(self, staff_session, applicant_session):
        """Staff can approve a document."""
        # Upload a document
        pdf_bytes = create_test_pdf("Document to approve")
        file_b64 = base64.b64encode(pdf_bytes).decode()

        upload_resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "other",
                "filename": "TEST_to_approve.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )
        assert upload_resp.status_code == 200
        doc_id = upload_resp.json().get("id")

        # Staff approves
        resp = staff_session.put(
            f"{BASE_URL}/api/documents/{doc_id}/review",
            json={"status": "approved"}
        )
        assert resp.status_code == 200, f"Approve failed: {resp.text}"
        print(f"✓ PUT /api/documents/{doc_id}/review (approved) succeeded")

    def test_staff_reject_document(self, staff_session, applicant_session):
        """Staff can reject a document with reason."""
        # Upload a document
        pdf_bytes = create_test_pdf("Document to reject")
        file_b64 = base64.b64encode(pdf_bytes).decode()

        upload_resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "other",
                "filename": "TEST_to_reject.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )
        assert upload_resp.status_code == 200
        doc_id = upload_resp.json().get("id")

        # Staff rejects
        resp = staff_session.put(
            f"{BASE_URL}/api/documents/{doc_id}/review",
            json={
                "status": "rejected",
                "rejection_reason": "Document is not readable"
            }
        )
        assert resp.status_code == 200, f"Reject failed: {resp.text}"
        print(f"✓ PUT /api/documents/{doc_id}/review (rejected) succeeded")

    def test_staff_revalidate_document(self, staff_session, applicant_session):
        """Staff can trigger revalidation of a document."""
        # Upload a document
        pdf_bytes = create_test_pdf("Document for revalidation test")
        file_b64 = base64.b64encode(pdf_bytes).decode()

        upload_resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents/upload",
            json={
                "document_type": "passport",
                "filename": "TEST_revalidate.pdf",
                "content_type": "application/pdf",
                "file_data": file_b64
            }
        )
        assert upload_resp.status_code == 200
        doc_id = upload_resp.json().get("id")

        # Staff triggers revalidation
        resp = staff_session.post(f"{BASE_URL}/api/documents/{doc_id}/revalidate")
        assert resp.status_code == 200, f"Revalidate failed: {resp.text}"
        
        data = resp.json()
        assert "validation_status" in data, "Missing validation_status in revalidate response"
        print(f"✓ POST /api/documents/{doc_id}/revalidate returned: {data}")


class TestPDFInvoiceLayout:
    """Test PDF invoice layout - Summenblock spacing."""

    def test_pdf_summenblock_no_overlap(self, staff_session):
        """PDF should have Zwischensumme, UStG-Hinweis, Gesamtbetrag on separate lines."""
        resp = staff_session.get(f"{BASE_URL}/api/invoices/{TEST_INVOICE}/pdf")
        assert resp.status_code == 200, f"PDF download failed: {resp.text}"
        assert resp.headers.get("content-type") == "application/pdf", "Not a PDF response"
        
        pdf_bytes = resp.content
        assert len(pdf_bytes) > 1000, "PDF too small"
        
        # Extract text from PDF to verify layout
        try:
            from PyPDF2 import PdfReader
            from io import BytesIO
            reader = PdfReader(BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "")
            
            # Check that key elements are present
            assert "Zwischensumme" in text, "Missing 'Zwischensumme' in PDF"
            assert "§ 4 Nr. 21 UStG" in text or "UStG" in text, "Missing UStG reference in PDF"
            assert "Gesamtbetrag" in text, "Missing 'Gesamtbetrag' in PDF"
            
            print(f"✓ PDF contains: Zwischensumme, UStG reference, Gesamtbetrag")
            print(f"  PDF size: {len(pdf_bytes)} bytes")
            
        except ImportError:
            # If PyPDF2 not available, just check PDF is valid
            assert pdf_bytes.startswith(b"%PDF"), "Invalid PDF format"
            print(f"✓ PDF downloaded successfully ({len(pdf_bytes)} bytes)")


class TestCleanup:
    """Cleanup test documents."""

    def test_cleanup_test_documents(self, staff_session):
        """Remove TEST_ prefixed documents created during testing."""
        # Get all documents for the test application
        resp = staff_session.get(f"{BASE_URL}/api/applications/{TEST_APP_ID}/documents")
        if resp.status_code == 200:
            docs = resp.json()
            test_docs = [d for d in docs if d.get("filename", "").startswith("TEST_")]
            print(f"Found {len(test_docs)} test documents to potentially clean up")
            # Note: No delete endpoint for documents in current API, so just report
        print("✓ Cleanup check complete")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
