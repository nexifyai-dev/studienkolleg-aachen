"""
Storage service – S3/MinIO-compatible abstraction.

[OFFEN] S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET must be set in .env before
binary file uploads are active in production.

When STORAGE_BACKEND=local, files are saved to LOCAL_STORAGE_PATH.
This is acceptable for development but NOT for production (no redundancy, no CDN).

Architecture:
  upload(path, data, content_type) -> storage_key
  download(storage_key) -> bytes
  get_presigned_url(storage_key, expires_in) -> str (S3 only)
  delete(storage_key) -> None

Access control: storage keys are internal only.
No URL is ever returned directly to the browser without authentication.
"""
import os
import re
import uuid
import logging
import aiofiles
import zipfile
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """Remove path traversal characters and limit length."""
    name = os.path.basename(filename)
    name = re.sub(r"[^\w.\-]", "_", name)
    name = name[:100]
    return name or "document"


def build_storage_key(app_id: str, doc_type: str, filename: str) -> str:
    """Build deterministic, collision-resistant storage key."""
    safe = sanitize_filename(filename)
    uid = uuid.uuid4().hex[:8]
    return f"documents/{app_id}/{doc_type}/{uid}_{safe}"


class LocalStorageBackend:
    """
    Dev/staging fallback: stores files on local filesystem.
    NOT suitable for production (no replication, no signed URLs).
    """

    def __init__(self, base_path: str):
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        target = self.base / key
        target.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(target, "wb") as f:
            await f.write(data)
        logger.info(f"[STORAGE:local] Stored key={key} size={len(data)}")
        return key

    async def download(self, key: str) -> bytes:
        target = self.base / key
        if not target.exists():
            raise FileNotFoundError(f"Storage key not found: {key}")
        async with aiofiles.open(target, "rb") as f:
            return await f.read()

    async def delete(self, key: str) -> None:
        target = self.base / key
        if target.exists():
            target.unlink()

    def get_presigned_url(self, key: str, expires_in: int = 300) -> str:
        # Local backend has no presigned URLs; caller must use /api/documents/{id}/download
        raise NotImplementedError("Presigned URLs not supported in local storage backend.")


class S3StorageBackend:
    """
    [OFFEN] S3/MinIO backend – requires boto3 + configured credentials.
    Activate by setting STORAGE_BACKEND=s3 or STORAGE_BACKEND=minio in .env.
    """

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                from config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_REGION
                kwargs = dict(
                    aws_access_key_id=S3_ACCESS_KEY,
                    aws_secret_access_key=S3_SECRET_KEY,
                    region_name=S3_REGION,
                )
                if S3_ENDPOINT:
                    kwargs["endpoint_url"] = S3_ENDPOINT
                self._client = boto3.client("s3", **kwargs)
            except ImportError:
                raise RuntimeError("[STORAGE:s3] boto3 not installed. Run: pip install boto3")
        return self._client

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        from config import S3_BUCKET
        import asyncio
        client = self._get_client()
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.put_object(
                Bucket=S3_BUCKET, Key=key, Body=data,
                ContentType=content_type,
                ServerSideEncryption="AES256",
            )
        )
        logger.info(f"[STORAGE:s3] Uploaded key={key}")
        return key

    async def download(self, key: str) -> bytes:
        from config import S3_BUCKET
        import asyncio
        client = self._get_client()
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.get_object(Bucket=S3_BUCKET, Key=key)
        )
        return response["Body"].read()

    async def delete(self, key: str) -> None:
        from config import S3_BUCKET
        import asyncio
        client = self._get_client()
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.delete_object(Bucket=S3_BUCKET, Key=key)
        )

    def get_presigned_url(self, key: str, expires_in: int = 300) -> str:
        from config import S3_BUCKET
        client = self._get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": key},
            ExpiresIn=expires_in,
        )


class MetadataOnlyBackend:
    """
    Fallback when no storage is configured.
    Records metadata but does not store actual files.
    NOT acceptable for production – only for MVP demo / testing without file keys.
    """

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        logger.warning(f"[STORAGE:none] File not stored (no backend configured). key={key}")
        return key

    async def download(self, key: str) -> bytes:
        raise NotImplementedError("No storage backend configured.")

    async def delete(self, key: str) -> None:
        pass

    def get_presigned_url(self, key: str, expires_in: int = 300) -> str:
        raise NotImplementedError("No storage backend configured.")


def _validate_s3_configuration(storage_backend: str, require_endpoint: bool) -> None:
    from config import S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET

    missing = []
    if require_endpoint and not S3_ENDPOINT:
        missing.append("S3_ENDPOINT")
    if not S3_ACCESS_KEY:
        missing.append("S3_ACCESS_KEY")
    if not S3_SECRET_KEY:
        missing.append("S3_SECRET_KEY")
    if not S3_BUCKET:
        missing.append("S3_BUCKET")

    if missing:
        required_for = "minio" if require_endpoint else "s3"
        raise RuntimeError(
            f"[STORAGE:{storage_backend}] Missing required configuration for {required_for}: {', '.join(missing)}"
        )


def get_storage_backend():
    """Factory: returns the active storage backend based on config."""
    from config import STORAGE_BACKEND, LOCAL_STORAGE_PATH

    if STORAGE_BACKEND in ("s3", "minio"):
        _validate_s3_configuration(
            STORAGE_BACKEND,
            require_endpoint=STORAGE_BACKEND == "minio",
        )
        return S3StorageBackend()
    if STORAGE_BACKEND == "local":
        return LocalStorageBackend(LOCAL_STORAGE_PATH)

    logger.warning("[STORAGE] No storage backend configured – using metadata-only mode.")
    return MetadataOnlyBackend()


# Singleton instance
_storage = None


def storage():
    global _storage
    if _storage is None:
        _storage = get_storage_backend()
    return _storage


# ─── Allowed file types ───────────────────────────────────────────────────────
ALLOWED_MIME_TYPES = frozenset([
    "application/pdf",
    "image/jpeg", "image/jpg", "image/png", "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def validate_upload(filename: str, size: int, content_type: str) -> None:
    """Raises ValueError with a user-facing message if upload is invalid."""
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"Datei zu groß (max. {MAX_FILE_SIZE_BYTES // 1024 // 1024} MB)")
    if content_type not in ALLOWED_MIME_TYPES:
        allowed = ", ".join(sorted(ALLOWED_MIME_TYPES))
        raise ValueError(f"Dateityp nicht erlaubt. Erlaubt: {allowed}")
    safe = sanitize_filename(filename)
    if not safe or safe.startswith("."):
        raise ValueError("Ungültiger Dateiname")


def _normalize_mime(mime: str) -> str:
    return {
        "image/jpg": "image/jpeg",
    }.get((mime or "").lower(), (mime or "").lower())


def _detect_mime_from_magic(file_bytes: bytes) -> str | None:
    if file_bytes.startswith(b"%PDF-"):
        return "application/pdf"
    if file_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(file_bytes) >= 12 and file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP":
        return "image/webp"
    if file_bytes.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return "application/msword"
    if file_bytes.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(BytesIO(file_bytes), "r") as zf:
                names = set(zf.namelist())
                if "[Content_Types].xml" in names and "word/document.xml" in names:
                    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        except Exception:
            return "application/zip"
    return None


def _is_blank_file(file_bytes: bytes) -> bool:
    if not file_bytes:
        return True
    blank_bytes = {0, 9, 10, 11, 12, 13, 32}
    return all(b in blank_bytes for b in file_bytes)


def _check_pdf_integrity(file_bytes: bytes) -> tuple[bool, bool]:
    if not file_bytes.startswith(b"%PDF-"):
        return False, True
    trailer = file_bytes[-2048:] if len(file_bytes) > 2048 else file_bytes
    has_eof = b"%%EOF" in trailer
    has_structural_markers = b" obj" in file_bytes and (b"xref" in file_bytes or b"trailer" in file_bytes)
    readable = has_eof and has_structural_markers
    return readable, not readable


def _check_png_integrity(file_bytes: bytes) -> tuple[bool, bool]:
    if not file_bytes.startswith(b"\x89PNG\r\n\x1a\n") or len(file_bytes) < 33:
        return False, True
    ihdr_len = int.from_bytes(file_bytes[8:12], "big")
    ihdr_type = file_bytes[12:16]
    readable = ihdr_len == 13 and ihdr_type == b"IHDR"
    return readable, not readable


def _check_jpeg_integrity(file_bytes: bytes) -> tuple[bool, bool]:
    readable = file_bytes.startswith(b"\xff\xd8") and file_bytes.endswith(b"\xff\xd9") and b"\xff\xda" in file_bytes
    return readable, not readable


def _check_webp_integrity(file_bytes: bytes) -> tuple[bool, bool]:
    if len(file_bytes) < 12:
        return False, True
    readable = file_bytes[:4] == b"RIFF" and file_bytes[8:12] == b"WEBP"
    return readable, not readable


def _check_doc_integrity(file_bytes: bytes) -> tuple[bool, bool]:
    readable = file_bytes.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1") and len(file_bytes) > 512
    return readable, not readable


def _check_docx_integrity(file_bytes: bytes) -> tuple[bool, bool]:
    try:
        with zipfile.ZipFile(BytesIO(file_bytes), "r") as zf:
            names = set(zf.namelist())
            readable = "[Content_Types].xml" in names and "word/document.xml" in names
            return readable, not readable
    except Exception:
        return False, True


def preflight_validate_upload(filename: str, content_type: str, file_bytes: bytes) -> dict:
    """Structured technical validation for document uploads."""
    result = {
        "mime_declared": content_type,
        "mime_detected": None,
        "magic_match": False,
        "is_corrupted": False,
        "is_blank": False,
        "readable": False,
        "errors": [],
    }

    safe = sanitize_filename(filename)
    if not safe or safe.startswith("."):
        result["errors"].append("invalid_filename")
        return result
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        result["errors"].append("file_too_large")
        return result

    normalized_declared = _normalize_mime(content_type)
    if normalized_declared not in ALLOWED_MIME_TYPES:
        result["errors"].append("mime_not_allowed")
        return result

    if _is_blank_file(file_bytes):
        result["is_blank"] = True
        result["errors"].append("blank_file")
        return result

    detected = _detect_mime_from_magic(file_bytes)
    result["mime_detected"] = detected
    normalized_detected = _normalize_mime(detected) if detected else None
    result["magic_match"] = normalized_detected == normalized_declared

    readable = False
    is_corrupted = True
    if normalized_declared == "application/pdf":
        readable, is_corrupted = _check_pdf_integrity(file_bytes)
    elif normalized_declared == "image/png":
        readable, is_corrupted = _check_png_integrity(file_bytes)
    elif normalized_declared == "image/jpeg":
        readable, is_corrupted = _check_jpeg_integrity(file_bytes)
    elif normalized_declared == "image/webp":
        readable, is_corrupted = _check_webp_integrity(file_bytes)
    elif normalized_declared == "application/msword":
        readable, is_corrupted = _check_doc_integrity(file_bytes)
    elif normalized_declared == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        readable, is_corrupted = _check_docx_integrity(file_bytes)

    result["readable"] = readable
    result["is_corrupted"] = is_corrupted

    if not result["magic_match"]:
        result["errors"].append("magic_mismatch")
    if result["is_corrupted"]:
        result["errors"].append("corrupted_or_unreadable")

    return result


def derive_document_status(has_binary: bool, technical_validation: dict | None) -> str:
    if not has_binary:
        return "uploaded"
    if not technical_validation:
        return "invalid_technical"
    if technical_validation.get("errors"):
        return "invalid_technical"
    if technical_validation.get("is_blank"):
        return "invalid_technical"
    if technical_validation.get("is_corrupted"):
        return "invalid_technical"
    if not technical_validation.get("readable"):
        return "invalid_technical"
    if not technical_validation.get("magic_match"):
        return "invalid_technical"
    return "uploaded"
