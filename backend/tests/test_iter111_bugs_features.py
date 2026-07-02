"""
Iter111 Regression: 3 P0 bugs + new features (bulk, messages audit, docs compliance,
partners overview/CRUD, messaging performance).
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

ADMIN = ("admin@studienkolleg-aachen.de", "Admin@2026!")
STAFF = ("staff@studienkolleg-aachen.de", "DevSeed@2026!")
APPLICANT = ("applicant@studienkolleg-aachen.de", "DevSeed@2026!")


def _login(email, password):
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


# ─── Sanity ──────────────────────────────────────────────────────────────────
def test_health():
    r = requests.get(f"{BASE_URL}/api/health", timeout=10)
    assert r.status_code == 200


# ─── Bug 1: Fälle öffnen (backend detail endpoint) ───────────────────────────
class TestCasesDetail:
    def test_admin_list_and_open_case(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/applications?limit=50", timeout=15)
        assert r.status_code == 200, r.text[:200]
        data = r.json()
        items = data.get("items") if isinstance(data, dict) else data
        assert isinstance(items, list) and len(items) > 0, "Should have applications for admin"
        first = items[0]
        aid = first.get("id") or first.get("_id")
        assert aid
        # Open detail
        r2 = admin_session.get(f"{BASE_URL}/api/applications/{aid}", timeout=15)
        assert r2.status_code == 200, f"Detail 200 expected: {r2.status_code} {r2.text[:200]}"
        det = r2.json()
        assert det.get("id") == aid or det.get("_id") == aid


# ─── Bug 2: Partner-Verwaltung ───────────────────────────────────────────────
class TestPartners:
    def test_overview_admin_ok(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/partners/overview", timeout=20)
        assert r.status_code == 200, r.text[:300]
        data = r.json()
        assert isinstance(data, list)
        # Validate structure of entries
        if data:
            keys = {"id", "email", "role", "referral_count", "enrolled_count",
                    "commission_confirmed", "commission_pending"}
            assert keys.issubset(set(data[0].keys())), f"Missing keys: {keys - set(data[0].keys())}"

    def test_overview_forbidden_for_staff(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/admin/partners/overview", timeout=15)
        assert r.status_code == 403, f"Staff must NOT access admin partners overview: {r.status_code}"

    def test_reset_password_allows_affiliate(self, admin_session):
        # find a partner
        r = admin_session.get(f"{BASE_URL}/api/admin/partners/overview", timeout=15)
        partners = r.json()
        if not partners:
            pytest.skip("No partner users found")
        pid = partners[0]["id"]
        r2 = admin_session.post(f"{BASE_URL}/api/admin/staff/{pid}/reset-password", timeout=15)
        assert r2.status_code == 200, f"Reset must allow affiliate role: {r2.status_code} {r2.text[:200]}"
        body = r2.json()
        assert "reset_url" in body and body.get("token")

    def test_invite_affiliate(self, admin_session):
        payload = {"email": f"iter111_partner_{int(time.time())}@stk-aachen.de", "role": "affiliate", "full_name": "Iter111 Partner"}
        r = admin_session.post(f"{BASE_URL}/api/auth/invite", json=payload, timeout=15)
        assert r.status_code in (200, 201), f"Invite affiliate: {r.status_code} {r.text[:200]}"
        body = r.json()
        assert body.get("invite_url") or body.get("invite_token")


# ─── Bug 3: Messaging Performance ────────────────────────────────────────────
class TestMessagingPerf:
    def test_portal_message_fast(self, applicant_session):
        # Portal message = channel="portal"; no external SMTP call
        # First get applicant's app
        r = applicant_session.get(f"{BASE_URL}/api/applications", timeout=15)
        data = r.json()
        items = data.get("items") if isinstance(data, dict) else data
        if not items:
            pytest.skip("Applicant has no application")
        app_id = items[0].get("id") or items[0].get("_id")

        payload = {
            "application_id": app_id,
            "channel": "portal",
            "subject": "iter111 perf test",
            "content": "portal message roundtrip",
        }
        t0 = time.time()
        r = applicant_session.post(f"{BASE_URL}/api/messages", json=payload, timeout=10)
        dur = time.time() - t0
        assert r.status_code in (200, 201), f"Message send: {r.status_code} {r.text[:200]}"
        assert dur < 3.0, f"Portal message too slow: {dur:.2f}s"

    def test_imap_sync_non_blocking(self, staff_session):
        """Kick off IMAP sync AND health in parallel; health must stay fast."""
        import threading
        health_dur = {}

        def hit_health():
            t0 = time.time()
            requests.get(f"{BASE_URL}/api/health", timeout=10)
            health_dur["dur"] = time.time() - t0

        # Trigger long-running sync
        def run_sync():
            try:
                staff_session.post(f"{BASE_URL}/api/messaging/sync-imap", timeout=60)
            except Exception:
                pass

        sync_thread = threading.Thread(target=run_sync)
        sync_thread.start()
        time.sleep(0.3)  # ensure sync is in flight
        hit_health()
        sync_thread.join(timeout=90)
        assert health_dur.get("dur", 99) < 3.0, f"health blocked by sync: {health_dur.get('dur')}s"


# ─── Bulk Actions ────────────────────────────────────────────────────────────
class TestBulkActions:
    def _test_ids(self, session, n=2):
        r = session.get(f"{BASE_URL}/api/applications?limit=50", timeout=15)
        data = r.json()
        items = data.get("items") if isinstance(data, dict) else data
        # Prefer test cases "fall*" if available
        ids = []
        for it in items or []:
            aid = it.get("id") or it.get("_id")
            email = ((it.get("applicant") or {}).get("email") or "").lower() if isinstance(it.get("applicant"), dict) else ""
            if "fall" in (email or "") or "test" in (email or ""):
                ids.append(aid)
            if len(ids) >= n:
                break
        if len(ids) < n:
            ids = [(it.get("id") or it.get("_id")) for it in (items or [])[:n]]
        return ids

    def test_bulk_set_stage(self, admin_session):
        ids = self._test_ids(admin_session, 2)
        assert len(ids) >= 1
        r = admin_session.post(f"{BASE_URL}/api/applications/bulk-update",
                               json={"ids": ids, "action": "set_stage", "value": "in_review"}, timeout=20)
        assert r.status_code == 200, r.text[:200]
        body = r.json()
        assert "updated" in body

    def test_bulk_set_priority(self, admin_session):
        ids = self._test_ids(admin_session, 2)
        r = admin_session.post(f"{BASE_URL}/api/applications/bulk-update",
                               json={"ids": ids, "action": "set_priority", "value": "high"}, timeout=20)
        assert r.status_code == 200, r.text[:200]

    def test_bulk_invalid_stage_400(self, admin_session):
        ids = self._test_ids(admin_session, 1)
        r = admin_session.post(f"{BASE_URL}/api/applications/bulk-update",
                               json={"ids": ids, "action": "set_stage", "value": "totally_bogus"}, timeout=15)
        assert r.status_code == 400

    def test_bulk_empty_ids_400(self, admin_session):
        r = admin_session.post(f"{BASE_URL}/api/applications/bulk-update",
                               json={"ids": [], "action": "set_stage", "value": "in_review"}, timeout=15)
        assert r.status_code == 400

    def test_bulk_applicant_forbidden(self, applicant_session):
        r = applicant_session.post(f"{BASE_URL}/api/applications/bulk-update",
                                   json={"ids": ["x"], "action": "set_stage", "value": "in_review"}, timeout=15)
        assert r.status_code == 403


# ─── Documents Compliance ────────────────────────────────────────────────────
class TestDocumentsCompliance:
    def test_admin_ok(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/admin/documents/compliance", timeout=25)
        assert r.status_code == 200, r.text[:300]
        body = r.json()
        assert "items" in body and "stats" in body
        assert isinstance(body["items"], list)

    def test_staff_forbidden(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/admin/documents/compliance", timeout=15)
        assert r.status_code == 403, f"Staff must be blocked: {r.status_code}"


# ─── Regression: forgot-password + invite still work ─────────────────────────
class TestRegression:
    def test_forgot_password(self):
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password",
                          json={"email": "applicant@studienkolleg-aachen.de"}, timeout=15)
        assert r.status_code == 200, r.text[:200]

    def test_conversations_list(self, staff_session):
        r = staff_session.get(f"{BASE_URL}/api/conversations", timeout=15)
        assert r.status_code == 200
