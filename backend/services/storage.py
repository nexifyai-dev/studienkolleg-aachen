"""
Storage service – S3/MinIO-compatible abstraction.

[OFFEN] S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY must be set in .env before
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


def get_storage_backend():
    """Factory: returns the active storage backend based on config."""
    from config import STORAGE_BACKEND, LOCAL_STORAGE_PATH, S3_ENDPOINT
    if STORAGE_BACKEND in ("s3", "minio") and S3_ENDPOINT:
        return S3StorageBackend()
    elif STORAGE_BACKEND == "local":
        return LocalStorageBackend(LOCAL_STORAGE_PATH)
    else:
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
