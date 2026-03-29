"""
Central configuration – all values from environment variables.
NO fallback values for secrets or credentials.
Missing mandatory config fails fast on startup.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Required (fail fast if missing) ─────────────────────────────────────────
MONGO_URL: str = os.environ["MONGO_URL"]
DB_NAME: str = os.environ["DB_NAME"]
JWT_SECRET: str = os.environ["JWT_SECRET"]

# ─── Seed credentials (loaded from env – no code defaults for passwords) ─────
# ADMIN_EMAIL has a safe default (non-secret). ADMIN_PASSWORD has NO default.
ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@studienkolleg-aachen.de")
ADMIN_PASSWORD: str = os.environ["ADMIN_PASSWORD"]   # Must be set explicitly

# ─── App URLs ─────────────────────────────────────────────────────────────────
FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "http://localhost:3000")
APP_URL: str = os.environ.get("APP_URL", "http://localhost:8001")

# ─── Security flags ──────────────────────────────────────────────────────────
# Set COOKIE_SECURE=true in production (HTTPS only).
COOKIE_SECURE: bool = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE: str = os.environ.get("COOKIE_SAMESITE", "lax")

# ─── JWT ──────────────────────────────────────────────────────────────────────
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_TTL_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_TTL_MINUTES", "60"))
REFRESH_TOKEN_TTL_DAYS: int = int(os.environ.get("REFRESH_TOKEN_TTL_DAYS", "7"))

# ─── Email (Resend) ───────────────────────────────────────────────────────────
# [OFFEN] RESEND_API_KEY must be set before email delivery is active.
RESEND_API_KEY: str = os.environ.get("RESEND_API_KEY", "")
EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "noreply@studienkolleg-aachen.de")
EMAIL_ENABLED: bool = bool(RESEND_API_KEY)

# ─── Storage ─────────────────────────────────────────────────────────────────
# [OFFEN] S3/MinIO credentials must be set before binary file uploads are active.
STORAGE_BACKEND: str = os.environ.get("STORAGE_BACKEND", "local")  # local | s3 | minio
S3_ENDPOINT: str = os.environ.get("S3_ENDPOINT", "")
S3_ACCESS_KEY: str = os.environ.get("S3_ACCESS_KEY", "")
S3_SECRET_KEY: str = os.environ.get("S3_SECRET_KEY", "")
S3_BUCKET: str = os.environ.get("S3_BUCKET", "w2g-documents")
S3_REGION: str = os.environ.get("S3_REGION", "eu-central-1")
LOCAL_STORAGE_PATH: str = os.environ.get("LOCAL_STORAGE_PATH", "/app/storage")
STORAGE_ENABLED: bool = bool(S3_ENDPOINT or STORAGE_BACKEND == "local")

# ─── AI Screening (Emergent LLM) ─────────────────────────────────────────────
EMERGENT_LLM_KEY: str = os.environ.get("EMERGENT_LLM_KEY", "")
AI_SCREENING_ENABLED: bool = bool(EMERGENT_LLM_KEY)

# ─── Feature Flags ────────────────────────────────────────────────────────────
COST_SIMULATOR_ENABLED: bool = os.environ.get("COST_SIMULATOR_ENABLED", "false").lower() == "true"

# ─── Env validation on import ─────────────────────────────────────────────────
def _validate():
    if len(JWT_SECRET) < 32:
        raise RuntimeError("JWT_SECRET must be at least 32 characters.")

_validate()
