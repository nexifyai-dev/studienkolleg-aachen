"""
Iteration 106 - Final pre-presentation smoke test.
Focus: Security headers for PDF/iframe preview, plus regression check on
critical flows (auth, applications, documents, invoices, support chat,
brain assistant, email generation, dashboard, notifications).
"""
import os
import io
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://invoice-fix-31.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN = ("admin@studienkolleg-aachen.de", "Admin@2026!")
STAFF = ("staff@studienkolleg-aachen.de", "DevSeed@2026!")
APPLICANT = ("applicant@studienkolleg-aachen.de", "DevSeed@2026!")


def _login(email: str, password: str) -> requests.Session:
    s = requests.Session()
    # First touch a GET endpoint to receive a csrf_token cookie
    s.get(f"{API}/health", timeout=10)
    csrf = s.cookies.get("csrf_token", "")
    headers = {"x-csrf-token": csrf} if csrf else {}
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password},
               headers=headers, timeout=15)
    assert r.status_code == 200, f"Login failed for {email}: {r.status_code} {r.text[:200]}"
    # Refresh CSRF token from cookie jar and attach to default headers
    csrf = s.cookies.get("csrf_token", "")
    if csrf:
        s.headers.update({"x-csrf-token": csrf})
    return s


@pytest.fixture(scope="session")
def staff_session():
    return _login(*STAFF)


@pytest.fixture(scope="session")
def admin_session():
    return _login(*ADMIN)


@pytest.fixture(scope="session")
def applicant_session():
    return _login(*APPLICANT)


# ─── 1. Auth ──────────────────────────────────────────────────────────────────
class TestAuth:
    def test_admin_login_and_me(self):
        s = _login(*ADMIN)
        me = s.get(f"{API}/auth/me", timeout=10)
        assert me.status_code == 200
        data = me.json()
        assert data["email"] == ADMIN[0]
        assert data["role"] in ("admin", "superadmin")

    def test_staff_login_and_me(self):
        s = _login(*STAFF)
        me = s.get(f"{API}/auth/me", timeout=10).json()
        assert me["role"] == "staff"

    def test_applicant_login_and_me(self):
        s = _login(*APPLICANT)
        me = s.get(f"{API}/auth/me", timeout=10).json()
        assert me["role"] == "applicant"

    def test_logout(self):
        s = _login(*STAFF)
        r = s.post(f"{API}/auth/logout", timeout=10)
        assert r.status_code in (200, 204)
        # After logout, /auth/me should be unauthorized
        me = s.get(f"{API}/auth/me", timeout=10)
        assert me.status_code in (401, 403)


# ─── 2. Security Headers (PRIMARY FOCUS) ─────────────────────────────────────
class TestSecurityHeaders:
    """Middleware change: frameable paths get CSP frame-ancestors *, others X-Frame-Options DENY."""

    def test_health_has_xfo_deny(self):
        r = requests.get(f"{API}/health", timeout=10)
        assert r.headers.get("X-Frame-Options") == "DENY"
        # Should NOT have frame-ancestors override
        csp = r.headers.get("Content-Security-Policy", "")
        assert "frame-ancestors *" not in csp
        assert r.headers.get("X-Content-Type-Options") == "nosniff"

    def test_dashboard_has_xfo_deny(self, staff_session):
        r = staff_session.get(f"{API}/dashboard/stats", timeout=10)
        assert r.status_code == 200
        assert r.headers.get("X-Frame-Options") == "DENY"

    def test_document_download_is_frameable(self, staff_session):
        # Find any document
        apps = staff_session.get(f"{API}/applications", timeout=10).json()
        assert isinstance(apps, list) and len(apps) > 0
        doc_id = None
        for app in apps:
            docs = staff_session.get(f"{API}/applications/{app['id']}/documents", timeout=10)
            if docs.status_code == 200 and docs.json():
                doc_id = docs.json()[0]["id"]
                break
        if not doc_id:
            pytest.skip("No documents available")
        r = staff_session.get(f"{API}/documents/{doc_id}/download", timeout=15, allow_redirects=False)
        assert r.status_code in (200, 302, 307)
        # Verify security headers
        csp = r.headers.get("Content-Security-Policy", "")
        xfo = r.headers.get("X-Frame-Options")
        assert "frame-ancestors *" in csp, f"Expected frame-ancestors *, got CSP={csp}, XFO={xfo}"
        assert xfo != "DENY", f"Document download must NOT have X-Frame-Options: DENY (got: {xfo})"

    def test_invoice_pdf_is_frameable(self, staff_session):
        invoices = staff_session.get(f"{API}/invoices", timeout=10).json()
        if not invoices:
            pytest.skip("No invoices to test")
        inv = invoices[0]
        number = inv.get("invoice_number") or inv.get("number")
        if not number:
            pytest.skip("Invoice has no number")
        r = staff_session.get(f"{API}/invoices/{number}/pdf", timeout=20, allow_redirects=False)
        assert r.status_code in (200, 302, 307), f"Invoice PDF returned {r.status_code}"
        csp = r.headers.get("Content-Security-Policy", "")
        xfo = r.headers.get("X-Frame-Options")
        assert "frame-ancestors *" in csp, f"Invoice PDF must have frame-ancestors *. CSP={csp}"
        assert xfo != "DENY", f"Invoice PDF must NOT have X-Frame-Options: DENY (got: {xfo})"


# ─── 3. Applications CRUD ─────────────────────────────────────────────────────
class TestApplications:
    def test_list_applications(self, staff_session):
        r = staff_session.get(f"{API}/applications", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_application_detail(self, staff_session):
        apps = staff_session.get(f"{API}/applications", timeout=10).json()
        app_id = apps[0]["id"]
        r = staff_session.get(f"{API}/applications/{app_id}", timeout=10)
        assert r.status_code == 200
        detail = r.json()
        assert detail["id"] == app_id


# ─── 4. Documents ─────────────────────────────────────────────────────────────
class TestDocuments:
    def test_upload_document(self, staff_session):
        apps = staff_session.get(f"{API}/applications", timeout=10).json()
        app_id = apps[0]["id"]
        # tiny PDF header
        pdf_bytes = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
        files = {"file": ("TEST_iter106.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        data = {"document_type": "passport", "category": "identity"}
        r = staff_session.post(
            f"{API}/applications/{app_id}/documents/upload",
            files=files,
            data=data,
            timeout=60,
        )
        assert r.status_code in (200, 201), f"Upload failed: {r.status_code} {r.text[:200]}"
        body = r.json()
        assert "id" in body or "document_id" in body


# ─── 5. Invoices ──────────────────────────────────────────────────────────────
class TestInvoices:
    def test_list_invoices(self, staff_session):
        r = staff_session.get(f"{API}/invoices", timeout=10)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_create_invoice_auto_calc(self, staff_session):
        apps = staff_session.get(f"{API}/applications", timeout=10).json()
        app_id = apps[0]["id"]
        applicant_id = apps[0].get("applicant_id") or apps[0].get("user_id")
        payload = {
            "application_id": app_id,
            "applicant_id": applicant_id,
            "items": [
                {"description": "TEST_iter106 Tuition", "quantity": 1, "unit_price": 5000.0},
                {"description": "TEST_iter106 Fee", "quantity": 1, "unit_price": 200.0},
            ],
            "currency": "EUR",
            "notes": "TEST_iter106 invoice",
        }
        r = staff_session.post(f"{API}/invoices", json=payload, timeout=15)
        assert r.status_code in (200, 201), f"Invoice create failed: {r.status_code} {r.text[:300]}"
        inv = r.json()
        assert float(inv.get("amount", 0)) == 5200.0, f"Auto-calc failed: {inv.get('amount')}"
        assert inv.get("due_date"), "due_date should be auto-set"


# ─── 6. Messaging & Email Generation ─────────────────────────────────────────
class TestMessaging:
    def test_messages_list(self, staff_session):
        r = staff_session.get(f"{API}/conversations", timeout=10)
        assert r.status_code == 200

    def test_generate_email_template(self, staff_session):
        # Find a conversation to use as context
        convs = staff_session.get(f"{API}/conversations", timeout=10).json()
        conv_id = None
        if isinstance(convs, list) and convs:
            conv_id = convs[0].get("id") or convs[0].get("_id") or convs[0].get("conversation_id")
        payload = {
            "template": "documents_request",
            "hints": "Bitte um Reisepass und Sprachnachweis B2.",
            "lang": "de",
        }
        if conv_id:
            payload["conversation_id"] = conv_id
        r = staff_session.post(f"{API}/messaging/generate-email", json=payload, timeout=60)
        assert r.status_code == 200, f"Email gen failed: {r.status_code} {r.text[:300]}"
        body = r.json()
        text = body.get("generated_text") or body.get("body") or body.get("text") or body.get("content") or ""
        assert len(text) > 30, f"Generated email too short: {text!r}"


# ─── 7. Support Chat (Public, OpenRouter DeepSeek) ───────────────────────────
class TestSupportChat:
    def test_support_chat_normal(self):
        r = requests.post(
            f"{API}/support/chat",
            json={"message": "Wie kann ich mich bewerben?", "history": [], "language": "de"},
            timeout=45,
        )
        assert r.status_code == 200, f"Support chat failed: {r.text[:300]}"
        body = r.json()
        reply = body.get("reply") or body.get("response") or body.get("message") or ""
        assert len(reply) > 20, f"Support chat reply too short: {reply!r}"

    def test_support_chat_nonsense_input(self):
        r = requests.post(
            f"{API}/support/chat",
            json={"message": "asdfghjkl 12345 zzz???", "history": [], "language": "de"},
            timeout=45,
        )
        assert r.status_code == 200
        reply = (r.json().get("reply") or r.json().get("response") or "")
        assert len(reply) > 10, f"Should give a sensible fallback reply, got: {reply!r}"


# ─── 8. Brain Assistant ───────────────────────────────────────────────────────
class TestBrain:
    def test_brain_chat(self, staff_session):
        # Real endpoint is /brain/ask with field "query"
        payload = {"query": "Wie viele Bewerbungen haben wir aktuell?", "lang": "de"}
        r = staff_session.post(f"{API}/brain/ask", json=payload, timeout=60)
        assert r.status_code == 200, f"Brain ask failed: {r.status_code} {r.text[:300]}"
        body = r.json()
        reply = body.get("reply") or body.get("response") or body.get("answer") or body.get("content") or ""
        assert len(reply) > 20


# ─── 9. Calendar / Appointments ──────────────────────────────────────────────
class TestAppointments:
    def test_list_appointments(self, staff_session):
        r = staff_session.get(f"{API}/appointments", timeout=10)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# ─── 10. Reporting / Notifications ───────────────────────────────────────────
class TestReporting:
    def test_dashboard(self, staff_session):
        r = staff_session.get(f"{API}/dashboard/stats", timeout=10)
        assert r.status_code == 200

    def test_notifications(self, applicant_session):
        r = applicant_session.get(f"{API}/notifications", timeout=10)
        assert r.status_code == 200


# ─── 11. Stripe Payment ──────────────────────────────────────────────────────
class TestPayments:
    def test_create_checkout(self, applicant_session):
        # Find an invoice to pay
        invoices = applicant_session.get(f"{API}/invoices", timeout=10).json()
        if not invoices:
            pytest.skip("No invoices for applicant")
        inv = invoices[0]
        payload = {
            "invoice_id": inv["id"],
            "success_url": f"{BASE_URL}/portal/financials?success=true",
            "cancel_url": f"{BASE_URL}/portal/financials?canceled=true",
        }
        r = applicant_session.post(f"{API}/payments/create-checkout", json=payload, timeout=20)
        # Stripe returns 200 with checkout_url, or 400/404 if invoice already paid
        assert r.status_code in (200, 400, 404, 409), f"Stripe checkout {r.status_code}: {r.text[:200]}"
        if r.status_code == 200:
            body = r.json()
            assert body.get("url") or body.get("checkout_url") or body.get("session_id")
