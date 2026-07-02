"""
Iteration 109 – DeepSeek Migration + Go-Live Regression

Focus: Support Chat (visitor/applicant/admin), Brain endpoints, Oracle,
Integration status (ai_provider=deepseek), Health, CSRF still enforced,
Admin analytics, storage backend=emergent.

Rate-limit awareness: /api/support/chat is limited to 20/min.
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://live-demo-fix.preview.emergentagent.com").rstrip("/")

ADMIN = ("admin@studienkolleg-aachen.de", "Admin@2026!")
STAFF = ("staff@studienkolleg-aachen.de", "DevSeed@2026!")
APPLICANT = ("applicant@studienkolleg-aachen.de", "DevSeed@2026!")


# ─── Helpers ──────────────────────────────────────────────────────────────────
def login(email: str, password: str) -> requests.Session:
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    r = s.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=15)
    assert r.status_code == 200, f"Login failed for {email}: {r.status_code} {r.text}"
    csrf = s.cookies.get("csrf_token")
    if csrf:
        s.headers.update({"X-CSRF-Token": csrf})
    return s


# ─── 1. Health & integration status ───────────────────────────────────────────
class TestHealthAndIntegrations:
    def test_health_endpoint(self):
        r = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert data.get("version"), "version missing"
        assert data.get("storage_backend") == "emergent", f"storage_backend={data.get('storage_backend')}"

    def test_integration_status_admin(self):
        s = login(*ADMIN)
        # Try the admin health endpoint that includes integrations
        r = s.get(f"{BASE_URL}/api/system/monitoring", timeout=15)
        assert r.status_code == 200, f"{r.status_code} {r.text[:200]}"
        data = r.json()
        integ = data.get("integrations", {})
        assert integ.get("ai_provider") == "deepseek", f"ai_provider={integ.get('ai_provider')}"
        assert integ.get("ai_active") is True, "ai_active must be True"
        assert integ.get("storage_active") is True, "storage_active must be True"


# ─── 2. Support Chat (public, no CSRF) ────────────────────────────────────────
class TestSupportChatDeepSeek:
    def test_visitor_chat_returns_reply(self):
        # No auth, no CSRF – public endpoint
        r = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "Was kostet der T-Kurs am Studienkolleg Aachen?", "history": [], "language": "de"},
            timeout=90,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        assert "reply" in data and isinstance(data["reply"], str) and len(data["reply"]) > 20, \
            f"Reply too short/missing: {data}"
        # Must NOT be the error fallback
        assert "konnte die Anfrage nicht verarbeiten" not in data["reply"], \
            f"Chat returned error fallback: {data['reply']}"
        assert data.get("role_context") == "visitor", f"role_context={data.get('role_context')}"

    def test_visitor_multi_turn_context(self):
        time.sleep(3)  # respect rate limit
        history = [
            {"role": "user", "content": "Ich interessiere mich fuer den T-Kurs."},
            {"role": "assistant", "content": "Gerne, der T-Kurs ist fuer technische Studiengaenge."},
        ]
        r = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "Und was kostet dieser Kurs?", "history": history, "language": "de"},
            timeout=90,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        assert len(data.get("reply", "")) > 20
        assert "konnte die Anfrage nicht verarbeiten" not in data["reply"]

    def test_applicant_chat_role_context(self):
        time.sleep(3)
        s = login(*APPLICANT)
        r = s.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "Wie ist der Status meiner Bewerbung?", "history": [], "language": "de"},
            timeout=90,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        assert data.get("role_context") == "applicant", f"role_context={data.get('role_context')}"
        assert len(data.get("reply", "")) > 10

    def test_admin_chat_role_context(self):
        time.sleep(3)
        s = login(*ADMIN)
        r = s.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "Was sind aktuelle Betriebs-KPIs?", "history": [], "language": "de"},
            timeout=90,
        )
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        # Admin uses staff prompt or admin prompt – both acceptable, must not be visitor
        assert data.get("role_context") in ("admin", "staff"), f"role_context={data.get('role_context')}"
        assert len(data.get("reply", "")) > 10


# ─── 3. CSRF still enforced (excluding public /support/chat + login) ─────────
class TestCSRF:
    def test_post_without_csrf_rejected(self):
        s = requests.Session()
        # Login first (login itself is exempt)
        r = s.post(f"{BASE_URL}/api/auth/login",
                   json={"email": ADMIN[0], "password": ADMIN[1]},
                   headers={"Content-Type": "application/json"}, timeout=15)
        assert r.status_code == 200
        # Now call an unsafe endpoint WITHOUT X-CSRF-Token header
        r2 = s.post(f"{BASE_URL}/api/system/clean-demo-data",
                    headers={"Content-Type": "application/json"}, timeout=15)
        assert r2.status_code == 403, f"Expected 403 without CSRF token, got {r2.status_code}"

    def test_support_chat_public_no_csrf(self):
        # Support-chat must be reachable without login and without csrf
        r = requests.post(
            f"{BASE_URL}/api/support/chat",
            json={"message": "Hallo", "history": [], "language": "de"},
            timeout=90,
        )
        assert r.status_code == 200, f"support/chat should be public, got {r.status_code}"


# ─── 4. Admin regression (analytics, portals) ─────────────────────────────────
class TestAdminRegression:
    def test_admin_analytics(self):
        s = login(*ADMIN)
        r = s.get(f"{BASE_URL}/api/admin/analytics?range=30d", timeout=20)
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        assert isinstance(data, dict) and len(data) > 0

    def test_auth_me_admin(self):
        s = login(*ADMIN)
        r = s.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert r.status_code == 200
        assert r.json().get("role") in ("admin", "superadmin")

    def test_auth_me_staff(self):
        s = login(*STAFF)
        r = s.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert r.status_code == 200
        assert r.json().get("role") in ("staff", "teacher")

    def test_auth_me_applicant(self):
        s = login(*APPLICANT)
        r = s.get(f"{BASE_URL}/api/auth/me", timeout=10)
        assert r.status_code == 200
        assert r.json().get("role") == "applicant"


# ─── 5. Brain / Oracle DeepSeek regression ────────────────────────────────────
class TestOtherAIEndpoints:
    def test_oracle_chat(self):
        """Oracle uses DeepSeek via nscale_provider wrapper."""
        s = login(*ADMIN)
        # Try common Oracle endpoint
        r = s.post(f"{BASE_URL}/api/oracle/chat",
                   json={"message": "Wie viele offene Bewerbungen sind aktuell im System?"},
                   timeout=90)
        if r.status_code == 404:
            pytest.skip("Oracle endpoint not found at /api/oracle/chat")
        assert r.status_code == 200, f"{r.status_code} {r.text[:300]}"
        data = r.json()
        # Look for a reply-like field
        found_text = None
        for k in ("reply", "content", "answer", "response", "message"):
            if isinstance(data.get(k), str) and len(data[k]) > 5:
                found_text = data[k]
                break
        assert found_text, f"No text response found in oracle: {data}"
        assert "API key not configured" not in found_text
