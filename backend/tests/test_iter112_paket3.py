"""
Iter112 Regression: Products/Tariffs CRUD, Auto-Lead via Staff-Chat, notify_new_message,
Apply optional docs, KI Regression, IMAP-Sync non-blocking, Public pages.
"""
import os
import time
import pytest
import requests

BASE_URL = (os.environ.get("REACT_APP_BACKEND_URL") or "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

ADMIN = (os.environ.get("TEST_ADMIN_EMAIL", "admin@studienkolleg-aachen.de"), os.environ.get("TEST_ADMIN_PASSWORD", ""))
STAFF = (os.environ.get("TEST_STAFF_EMAIL", "staff@studienkolleg-aachen.de"), os.environ.get("TEST_STAFF_PASSWORD", ""))
APPLICANT = (os.environ.get("TEST_APPLICANT_EMAIL", "applicant@studienkolleg-aachen.de"), os.environ.get("TEST_APPLICANT_PASSWORD", ""))


def _login(email, password):
    if not password:
        pytest.skip("Test credentials missing: set TEST_ADMIN_PASSWORD, TEST_STAFF_PASSWORD and TEST_APPLICANT_PASSWORD")
    s = requests.Session()
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, f"Login failed for {email}: {r.status_code} {r.text[:200]}"
    csrf = s.cookies.get("csrf_token") or ""
    s.headers.update({"X-CSRF-Token": csrf, "Content-Type": "application/json"})
    return s


@pytest.fixture(scope="module")
def admin_session():
    return _login(*ADMIN)


@pytest.fixture(scope="module")
def staff_session():
    return _login(*STAFF)


@pytest.fixture(scope="module")
def applicant_session():
    return _login(*APPLICANT)


# ─── Sanity ─────────────────────────────────────────────────────────────────
def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert r.status_code == 200


# ─── P0: Products/Tariffs public + CRUD ─────────────────────────────────────
class TestProductsPublic:
    def test_public_no_auth(self):
        r = requests.get(f"{BASE_URL}/api/products/public", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) >= 17, f"Expected >=17 seed items, got {len(items)}"
        # Alle Items müssen active sein
        assert all(i.get("is_active") is not False for i in items)
        # Structure
        first = items[0]
        for k in ("id", "code", "name", "price", "currency", "category"):
            assert k in first, f"Missing key: {k}"
        # ObjectId must not appear as _id
        assert "_id" not in first
        codes = {i["code"] for i in items}
        assert "SK-TKURS" in codes
        assert "DSH-PREP" in codes
        assert "VISUM-SERVICE" in codes
        assert "UNTERKUNFT-M" in codes
        assert "KOMBI-BASIC" in codes


class TestProductsCRUD:
    def test_staff_forbidden_create(self, staff_session):
        r = staff_session.post(f"{BASE_URL}/api/products", json={
            "code": "TEST_STAFF_FORBID", "name": "Staff Forbidden", "price": 100, "category": "sonstig"
        }, timeout=15)
        assert r.status_code == 403, f"Staff must NOT create: {r.status_code} {r.text[:200]}"

    def test_admin_full_crud_cycle(self, admin_session):
        code = f"TEST-ITER112-{int(time.time())}"
        # CREATE
        r = admin_session.post(f"{BASE_URL}/api/products", json={
            "code": code, "name": "Iter112 Test-Tarif", "description": "test",
            "price": 999, "currency": "EUR", "category": "sonstig"
        }, timeout=15)
        assert r.status_code in (200, 201), r.text[:200]
        created = r.json()
        pid = created["id"]
        assert created["code"] == code.upper()
        assert created["price"] == 999
        # DUPLICATE -> 409
        r = admin_session.post(f"{BASE_URL}/api/products", json={
            "code": code, "name": "dup", "price": 1, "category": "sonstig"
        }, timeout=15)
        assert r.status_code == 409, f"Dup must be 409: {r.status_code}"
        # UPDATE price
        r = admin_session.put(f"{BASE_URL}/api/products/{pid}", json={"price": 1234}, timeout=15)
        assert r.status_code == 200
        assert r.json()["price"] == 1234
        # ARCHIVE (soft-delete)
        r = admin_session.delete(f"{BASE_URL}/api/products/{pid}", timeout=15)
        assert r.status_code == 200
        # Verify not in public list
        pub = requests.get(f"{BASE_URL}/api/products/public", timeout=15).json()
        codes = {p["code"] for p in pub}
        assert code.upper() not in codes, "Archived product must not appear in public list"
        # REACTIVATE
        r = admin_session.put(f"{BASE_URL}/api/products/{pid}", json={"is_active": True}, timeout=15)
        assert r.status_code == 200
        assert r.json()["is_active"] is True
        # Cleanup: archive again
        admin_session.delete(f"{BASE_URL}/api/products/{pid}", timeout=15)

    def test_applicant_forbidden(self, applicant_session):
        r = applicant_session.post(f"{BASE_URL}/api/products", json={
            "code": "TEST_APP_FORBID", "name": "x", "price": 1, "category": "sonstig"
        }, timeout=15)
        assert r.status_code == 403


class TestProductsPriceSync:
    def test_admin_price_update_reflects_public(self, admin_session):
        # Get T-Kurs
        r = requests.get(f"{BASE_URL}/api/products/public", timeout=15)
        items = r.json()
        tkurs = next((p for p in items if p["code"] == "SK-TKURS"), None)
        assert tkurs, "SK-TKURS not found"
        original = tkurs["price"]
        pid = tkurs["id"]
        try:
            # Update to a distinct value
            new_price = 4321
            r = admin_session.put(f"{BASE_URL}/api/products/{pid}", json={"price": new_price}, timeout=15)
            assert r.status_code == 200
            # Verify public reflects change
            time.sleep(0.5)
            pub = requests.get(f"{BASE_URL}/api/products/public", timeout=15).json()
            updated = next((p for p in pub if p["code"] == "SK-TKURS"), None)
            assert updated and updated["price"] == new_price
        finally:
            # Reset
            admin_session.put(f"{BASE_URL}/api/products/{pid}", json={"price": original}, timeout=15)


# ─── P0: Staff-Chat Auto-Lead ───────────────────────────────────────────────
class TestStartByEmail:
    def test_new_lead_creation(self, staff_session):
        email = f"autolead.test.{int(time.time())}@example.com"
        r = staff_session.post(f"{BASE_URL}/api/conversations/start-by-email",
                               json={"email": email}, timeout=15)
        assert r.status_code == 200, r.text[:300]
        body = r.json()
        assert body.get("conversation_id")
        assert body.get("user_id")
        assert body.get("application_id")
        assert body.get("lead_created") is True

        # Second call idempotent
        r2 = staff_session.post(f"{BASE_URL}/api/conversations/start-by-email",
                                json={"email": email}, timeout=15)
        assert r2.status_code == 200
        b2 = r2.json()
        assert b2.get("lead_created") is False, "Second call must not recreate lead"
        assert b2["conversation_id"] == body["conversation_id"]

    def test_invalid_email(self, staff_session):
        r = staff_session.post(f"{BASE_URL}/api/conversations/start-by-email",
                               json={"email": "not-an-email"}, timeout=15)
        assert r.status_code == 400

    def test_applicant_forbidden(self, applicant_session):
        r = applicant_session.post(f"{BASE_URL}/api/conversations/start-by-email",
                                   json={"email": "x@example.com"}, timeout=15)
        assert r.status_code == 403


# ─── P0: Apply optional docs (via API) ──────────────────────────────────────
class TestApplyOptionalDocs:
    def test_apply_no_documents_ok(self):
        """Public /api/leads/ingest with NO documents must succeed (docs are now optional)."""
        ts = int(time.time())
        payload = {
            "full_name": f"Iter112 Optional {ts}",
            "first_name": "Iter112",
            "last_name": f"Optional{ts}",
            "email": f"iter112_optional_{ts}@example.com",
            "date_of_birth": "2000-01-01",
            "phone": "+491701234567",
            "country": "Marokko",
            "area_interest": "studienkolleg",
            "course_type": "T-Course",
            "desired_start": "Winter Semester 2026/27",
            "language_level": "B1",
            "degree_country": "Türkei",
            "source": "website_form",
            "language_pref": "de",
            # documents intentionally omitted
        }
        r = requests.post(f"{BASE_URL}/api/leads/ingest", json=payload, timeout=25)
        assert r.status_code in (200, 201), f"Ingest w/o docs must succeed: {r.status_code} {r.text[:400]}"
        body = r.json()
        # application_id should be present
        app_id = body.get("application_id") or body.get("id")
        if app_id:
            # Verify stage lead_new via admin
            admin = _login(*ADMIN)
            r2 = admin.get(f"{BASE_URL}/api/applications/{app_id}", timeout=15)
            if r2.status_code == 200:
                det = r2.json()
                stage = det.get("current_stage") or det.get("stage")
                assert stage == "lead_new", f"Stage should be lead_new, got {stage}"


# ─── P1: notify_new_message ─────────────────────────────────────────────────
class TestNotifyNewMessage:
    def test_portal_message_creates_notif_for_applicant(self, staff_session, applicant_session):
        # Get applicant user id
        r = applicant_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        assert r.status_code == 200
        applicant_id = r.json().get("id") or r.json().get("_id")
        assert applicant_id

        # Get applicant's application id
        r = applicant_session.get(f"{BASE_URL}/api/applications", timeout=15)
        data = r.json()
        items = data.get("items") if isinstance(data, dict) else data
        if not items:
            pytest.skip("Applicant has no application")
        app_id = items[0].get("id") or items[0].get("_id")

        marker = f"iter112_notify_{int(time.time())}"
        # Staff sends portal message directly to applicant via recipient_id
        payload = {
            "application_id": app_id,
            "recipient_id": applicant_id,
            "channel": "portal",
            "subject": "Iter112 Notify",
            "content": marker,
            "visibility": "public",
        }
        r = staff_session.post(f"{BASE_URL}/api/messages", json=payload, timeout=15)
        assert r.status_code in (200, 201), r.text[:300]
        time.sleep(2)  # notification is async
        # Applicant polls notifications
        r = applicant_session.get(f"{BASE_URL}/api/notifications", timeout=15)
        assert r.status_code == 200
        notif_data = r.json()
        notif_list = notif_data if isinstance(notif_data, list) else (notif_data.get("items") or [])
        assert any(
            (n.get("type") == "new_message" or n.get("notification_type") == "new_message")
            for n in notif_list
        ), f"No new_message notification found. Sample: {[n.get('type') or n.get('notification_type') for n in notif_list[:5]]}"

    def test_internal_note_does_not_notify_applicant(self, staff_session, applicant_session):
        """Internal-visibility notes must NOT create applicant notifications."""
        r = applicant_session.get(f"{BASE_URL}/api/auth/me", timeout=15)
        applicant_id = r.json().get("id")
        r = applicant_session.get(f"{BASE_URL}/api/applications", timeout=15)
        data = r.json()
        items = data.get("items") if isinstance(data, dict) else data
        if not items:
            pytest.skip("no app")
        app_id = items[0].get("id") or items[0].get("_id")

        # Snapshot current notification count
        r0 = applicant_session.get(f"{BASE_URL}/api/notifications", timeout=15)
        before = len(r0.json() if isinstance(r0.json(), list) else [])

        marker = f"iter112_internal_{int(time.time())}"
        payload = {
            "application_id": app_id,
            "recipient_id": applicant_id,
            "channel": "portal",
            "content": marker,
            "visibility": "internal",
        }
        r = staff_session.post(f"{BASE_URL}/api/messages", json=payload, timeout=15)
        assert r.status_code in (200, 201)
        time.sleep(2)
        r = applicant_session.get(f"{BASE_URL}/api/notifications", timeout=15)
        after = len(r.json() if isinstance(r.json(), list) else [])
        # No new notification for applicant on internal note
        assert after <= before, f"Internal notes must not notify applicant. before={before} after={after}"


# ─── P1: KI Support Chat regression ─────────────────────────────────────────
class TestSupportChat:
    def test_deepseek_fallback_returns_german(self):
        r = requests.post(f"{BASE_URL}/api/support/chat",
                          json={"message": "Was ist das Studienkolleg?", "session_id": f"iter112_{int(time.time())}"},
                          timeout=45)
        assert r.status_code == 200, r.text[:300]
        body = r.json()
        reply = body.get("reply") or body.get("answer") or body.get("message") or ""
        assert isinstance(reply, str) and len(reply) > 10, f"Reply too short: {reply}"


# ─── P1: Regression - IMAP non-blocking & products with staff ───────────────
class TestRegression:
    def test_products_staff_list(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/products", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list) and len(items) > 0
        assert "code" in items[0] and "name" in items[0] and "price" in items[0]

    def test_imap_sync_non_blocking(self, staff_session):
        import threading
        health_dur = {}

        def hit_health():
            t0 = time.time()
            requests.get(f"{BASE_URL}/api/health", timeout=10)
            health_dur["dur"] = time.time() - t0

        def run_sync():
            try:
                staff_session.post(f"{BASE_URL}/api/messaging/sync-imap", timeout=60)
            except Exception:
                pass

        sync_thread = threading.Thread(target=run_sync)
        sync_thread.start()
        time.sleep(0.3)
        hit_health()
        sync_thread.join(timeout=90)
        assert health_dur.get("dur", 99) < 3.0

    def test_all_role_logins(self):
        for email, pw in (ADMIN, STAFF, APPLICANT):
            if not pw:
                pytest.skip("Test credentials missing: set TEST_ADMIN_PASSWORD, TEST_STAFF_PASSWORD and TEST_APPLICANT_PASSWORD")
            s = requests.Session()
            r = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": pw}, timeout=15)
            assert r.status_code == 200, f"Login failed for {email}"
