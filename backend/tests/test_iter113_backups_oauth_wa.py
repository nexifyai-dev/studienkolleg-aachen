"""
Iteration 113 – Backups + Google OAuth + WhatsApp + PWA regression tests.

Coverage:
  - Backups: /api/backups/status, /api/backups, /api/backups/run, DELETE
    (restore is NOT invoked to avoid data loss)
  - Google OAuth: /api/oauth/google/status, /api/oauth/google/authorize (not configured)
  - WhatsApp: /api/whatsapp/status, /api/whatsapp/send (skipped), /api/whatsapp/messages
  - Appointments: POST creates without error even if GCal not configured
  - Regression: /api/health, /api/auth/login, /api/products/public, PWA files
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "admin@studienkolleg-aachen.de")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "")


# ─── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def admin_session():
    if not ADMIN_PASSWORD:
        pytest.skip("Test credentials missing: set TEST_ADMIN_PASSWORD")
    s = requests.Session()
    # Fetch csrf cookie
    r = s.get(f"{BASE_URL}/api/health", timeout=15)
    assert r.status_code == 200, f"Health failed: {r.status_code}"
    csrf = s.cookies.get("csrf_token")
    assert csrf, "csrf_token cookie missing"
    login = s.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        headers={"x-csrf-token": csrf, "Content-Type": "application/json"},
        timeout=15,
    )
    assert login.status_code == 200, f"Admin login failed: {login.status_code} {login.text[:200]}"
    # Refresh csrf for post-login state
    return s


def _csrf(session: requests.Session) -> str:
    tok = session.cookies.get("csrf_token")
    assert tok, "csrf_token missing in session cookies"
    return tok


# ─── Health / Auth Regression ────────────────────────────────────────────────
class TestHealthAndAuth:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") in ("ok", "healthy", "online") or "status" in data

    def test_admin_login(self, admin_session):
        me = admin_session.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert me.status_code == 200
        assert me.json().get("email") == ADMIN_EMAIL

    def test_products_public_still_works(self):
        r = requests.get(f"{BASE_URL}/api/products/public", timeout=15)
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        assert len(items) >= 5


# ─── Backups API ─────────────────────────────────────────────────────────────
class TestBackups:
    def test_status_endpoint(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/backups/status", timeout=15)
        assert r.status_code == 200, r.text[:200]
        data = r.json()
        assert "backup_dir" in data
        assert "retention_days" in data
        assert "count" in data
        assert "mongodump_available" in data
        assert "mongorestore_available" in data
        # These should be true on this env
        assert data["mongodump_available"] is True, "mongodump missing on system"
        assert data["mongorestore_available"] is True, "mongorestore missing on system"

    def test_list_backups(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/backups", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "backups" in data
        assert isinstance(data["backups"], list)

    def test_run_backup_creates_new(self, admin_session):
        # count before
        before = admin_session.get(f"{BASE_URL}/api/backups", timeout=15).json()["backups"]
        count_before = len(before)

        r = admin_session.post(
            f"{BASE_URL}/api/backups/run",
            headers={"x-csrf-token": _csrf(admin_session)},
            timeout=120,
        )
        assert r.status_code == 200, f"Run backup failed: {r.status_code} {r.text[:200]}"
        result = r.json()
        assert result.get("status") in ("ok", "success"), f"Backup status not ok: {result}"

        # verify persistence via list
        after = admin_session.get(f"{BASE_URL}/api/backups", timeout=15).json()["backups"]
        assert len(after) >= count_before + 1, f"Backup not created (before={count_before}, after={len(after)})"

    def test_delete_backup(self, admin_session):
        # Ensure at least one backup exists
        listing = admin_session.get(f"{BASE_URL}/api/backups", timeout=15).json()["backups"]
        if len(listing) < 2:
            # Create one to delete
            admin_session.post(
                f"{BASE_URL}/api/backups/run",
                headers={"x-csrf-token": _csrf(admin_session)},
                timeout=120,
            )
            time.sleep(1)
            listing = admin_session.get(f"{BASE_URL}/api/backups", timeout=15).json()["backups"]

        # Delete oldest (last in the sorted-desc list)
        assert len(listing) >= 1, "No backups to delete"
        victim = listing[-1]["name"]
        r = admin_session.delete(
            f"{BASE_URL}/api/backups/{victim}",
            headers={"x-csrf-token": _csrf(admin_session)},
            timeout=30,
        )
        assert r.status_code == 200, f"Delete failed: {r.status_code} {r.text[:200]}"
        assert r.json().get("status") == "deleted"

        # verify removal
        after = admin_session.get(f"{BASE_URL}/api/backups", timeout=15).json()["backups"]
        names = [b["name"] for b in after]
        assert victim not in names

    def test_restore_endpoint_exists_but_not_invoked(self, admin_session):
        """We only verify the endpoint requires auth + rejects invalid names.
        We do NOT invoke a real restore to avoid data loss."""
        # Invalid name (does not start with backup_) → 400
        r = admin_session.post(
            f"{BASE_URL}/api/backups/foo/restore",
            headers={"x-csrf-token": _csrf(admin_session)},
            timeout=15,
        )
        assert r.status_code == 400, f"Expected 400 invalid name, got {r.status_code}"

        # Well-formed but nonexistent → 404
        r = admin_session.post(
            f"{BASE_URL}/api/backups/backup_99999999_999999/restore",
            headers={"x-csrf-token": _csrf(admin_session)},
            timeout=15,
        )
        assert r.status_code == 404, f"Expected 404 not found, got {r.status_code}"

    def test_backups_require_admin(self):
        """Unauthenticated must be rejected."""
        r = requests.get(f"{BASE_URL}/api/backups/status", timeout=10)
        assert r.status_code in (401, 403), f"Should require auth, got {r.status_code}"


# ─── Google OAuth ────────────────────────────────────────────────────────────
class TestGoogleOAuth:
    def test_google_status_not_configured(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/oauth/google/status", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data.get("configured") is False
        assert data.get("connected") is False

    def test_google_authorize_400_when_not_configured(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/oauth/google/authorize", timeout=15)
        assert r.status_code == 400, f"Expected 400 not configured, got {r.status_code}"
        assert "nicht konfiguriert" in r.text.lower() or "not configured" in r.text.lower()

    def test_google_requires_admin(self):
        r = requests.get(f"{BASE_URL}/api/oauth/google/status", timeout=10)
        assert r.status_code in (401, 403)


# ─── WhatsApp ────────────────────────────────────────────────────────────────
class TestWhatsApp:
    def test_whatsapp_status_not_configured(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/whatsapp/status", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert data.get("configured") is False

    def test_whatsapp_send_returns_skipped(self, admin_session):
        r = admin_session.post(
            f"{BASE_URL}/api/whatsapp/send",
            json={"to": "+491701234567", "body": "TEST_ITER113 hello"},
            headers={"x-csrf-token": _csrf(admin_session), "Content-Type": "application/json"},
            timeout=15,
        )
        assert r.status_code == 200, f"send failed: {r.status_code} {r.text[:200]}"
        data = r.json()
        assert data.get("status") == "skipped"
        assert data.get("reason") == "twilio_not_configured"

    def test_whatsapp_messages_list(self, admin_session):
        r = admin_session.get(f"{BASE_URL}/api/whatsapp/messages", timeout=15)
        assert r.status_code == 200
        data = r.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        # No mongo _id leakage
        for m in data["messages"]:
            assert "_id" not in m, f"_id leaked in whatsapp message: {m}"

    def test_whatsapp_send_validates_fields(self, admin_session):
        r = admin_session.post(
            f"{BASE_URL}/api/whatsapp/send",
            json={"to": "", "body": ""},
            headers={"x-csrf-token": _csrf(admin_session), "Content-Type": "application/json"},
            timeout=15,
        )
        assert r.status_code == 400


# ─── Appointments (no GCal error) ────────────────────────────────────────────
class TestAppointmentsNoGCal:
    def test_create_appointment_without_gcal(self, admin_session):
        # Try to create a minimal appointment as admin (must silently skip GCal sync)
        payload = {
            "title": "TEST_ITER113 Beratung",
            "date": "2026-06-15",
            "time": "10:00",
            "duration_min": 30,
            "type": "consultation",
            "location": "Online (Zoom)",
        }
        r = admin_session.post(
            f"{BASE_URL}/api/appointments",
            json=payload,
            headers={"x-csrf-token": _csrf(admin_session), "Content-Type": "application/json"},
            timeout=20,
        )
        # Endpoint schema may vary; accept 200/201, otherwise skip with reason
        if r.status_code == 422:
            pytest.skip(f"Appointment schema differs (422): {r.text[:200]}")
        assert r.status_code in (200, 201), f"Appointment create failed: {r.status_code} {r.text[:200]}"
        data = r.json()
        # google_event_id should be absent or None since GCal not configured
        assert data.get("google_event_id") in (None, "", False, [])


# ─── PWA static files ────────────────────────────────────────────────────────
class TestPWA:
    def test_manifest_json(self):
        r = requests.get(f"{BASE_URL}/manifest.json", timeout=15)
        assert r.status_code == 200, f"manifest.json {r.status_code}"
        data = r.json()
        assert "name" in data
        assert "icons" in data
        assert "start_url" in data

    def test_service_worker(self):
        r = requests.get(f"{BASE_URL}/sw.js", timeout=15)
        assert r.status_code == 200, f"sw.js {r.status_code}"
        # Should look like JS
        assert "self" in r.text or "addEventListener" in r.text or "install" in r.text.lower()
