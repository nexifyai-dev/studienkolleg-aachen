"""Deprecated compatibility shim for historical imports.

Produktive KI-Aufrufe müssen `services.deepseek_provider` nutzen.
Neue Nutzung dieses Moduls ist per CI-Guard untersagt.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "services.nscale_provider is deprecated. Use services.deepseek_provider instead.",
    DeprecationWarning,
    stacklevel=2,
)

from services.deepseek_provider import chat_completion, get_model_registry, is_enabled

__all__ = ["chat_completion", "get_model_registry", "is_enabled"]
