"""
Shared test configuration – centralizes credential loading.

Credentials are loaded from environment variables to prevent
plaintext secrets in versioned test files.

Required env vars (set in backend/.env or CI):
  ADMIN_EMAIL, ADMIN_PASSWORD, SEED_DEV_PASSWORD
"""
import os

# ─── Test Credentials (from env, never hardcoded) ────────────────────────────
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@studienkolleg-aachen.de")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = os.environ.get("SEED_DEV_PASSWORD", "")
TEACHER_EMAIL = "teacher@studienkolleg-aachen.de"
TEACHER_PASSWORD = os.environ.get("SEED_DEV_PASSWORD", "")
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = os.environ.get("SEED_DEV_PASSWORD", "")
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = os.environ.get("SEED_DEV_PASSWORD", "")

# ─── API URL ──────────────────────────────────────────────────────────────────
API_URL = os.environ.get(
    "TEST_API_URL",
    os.environ.get("APP_URL", "http://localhost:8001"),
)
