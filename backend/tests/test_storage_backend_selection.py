import importlib
import sys
import types
from pathlib import Path

import pytest

class _DummyAiofilesModule:
    @staticmethod
    def open(*args, **kwargs):
        raise RuntimeError("aiofiles.open should not be used in backend selection tests")


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def storage_module(monkeypatch):
    def _load_config(**values):
        cfg = types.ModuleType("config")
        cfg.STORAGE_BACKEND = values.get("STORAGE_BACKEND", "local")
        cfg.LOCAL_STORAGE_PATH = values.get("LOCAL_STORAGE_PATH", "/tmp/storage")
        cfg.S3_ENDPOINT = values.get("S3_ENDPOINT", "")
        cfg.S3_ACCESS_KEY = values.get("S3_ACCESS_KEY", "")
        cfg.S3_SECRET_KEY = values.get("S3_SECRET_KEY", "")
        cfg.S3_BUCKET = values.get("S3_BUCKET", "")
        cfg.S3_REGION = values.get("S3_REGION", "eu-central-1")
        monkeypatch.setitem(sys.modules, "config", cfg)

    _load_config()
    monkeypatch.setitem(sys.modules, "aiofiles", _DummyAiofilesModule())

    if "services.storage" in sys.modules:
        module = importlib.reload(sys.modules["services.storage"])
    else:
        module = importlib.import_module("services.storage")

    module._storage = None
    return module, _load_config


def test_s3_backend_selected_without_endpoint(storage_module):
    storage, set_config = storage_module
    set_config(
        STORAGE_BACKEND="s3",
        S3_ACCESS_KEY="key",
        S3_SECRET_KEY="secret",
        S3_BUCKET="bucket",
        S3_ENDPOINT="",
    )

    backend = storage.get_storage_backend()

    assert isinstance(backend, storage.S3StorageBackend)


def test_minio_requires_endpoint(storage_module):
    storage, set_config = storage_module
    set_config(
        STORAGE_BACKEND="minio",
        S3_ACCESS_KEY="key",
        S3_SECRET_KEY="secret",
        S3_BUCKET="bucket",
        S3_ENDPOINT="",
    )

    with pytest.raises(RuntimeError, match="S3_ENDPOINT"):
        storage.get_storage_backend()


def test_s3_requires_credentials(storage_module):
    storage, set_config = storage_module
    set_config(
        STORAGE_BACKEND="s3",
        S3_ACCESS_KEY="",
        S3_SECRET_KEY="secret",
        S3_BUCKET="bucket",
    )

    with pytest.raises(RuntimeError, match="S3_ACCESS_KEY"):
        storage.get_storage_backend()


def test_minio_requires_bucket_even_with_endpoint(storage_module):
    storage, set_config = storage_module
    set_config(
        STORAGE_BACKEND="minio",
        S3_ENDPOINT="https://minio.example.local",
        S3_ACCESS_KEY="key",
        S3_SECRET_KEY="secret",
        S3_BUCKET="",
    )

    with pytest.raises(RuntimeError, match="S3_BUCKET"):
        storage.get_storage_backend()


def test_unknown_backend_uses_metadata_only(storage_module):
    storage, set_config = storage_module
    set_config(STORAGE_BACKEND="none")

    backend = storage.get_storage_backend()

    assert isinstance(backend, storage.MetadataOnlyBackend)


def test_storage_singleton_uses_factory(storage_module):
    storage, set_config = storage_module
    set_config(
        STORAGE_BACKEND="s3",
        S3_ACCESS_KEY="key",
        S3_SECRET_KEY="secret",
        S3_BUCKET="bucket",
    )
    storage._storage = None

    first = storage.storage()
    second = storage.storage()

    assert isinstance(first, storage.S3StorageBackend)
    assert first is second
