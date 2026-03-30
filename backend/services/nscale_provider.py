"""Legacy compatibility shim.
Produktive Aufrufe müssen `services.deepseek_provider` nutzen.
"""
from services.deepseek_provider import chat_completion, get_model_registry, is_enabled

__all__ = ["chat_completion", "get_model_registry", "is_enabled"]
