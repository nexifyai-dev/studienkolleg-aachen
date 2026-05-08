"""
AI Provider – Alle KI-Funktionen via OpenRouter (deepseek/deepseek-v4-flash).

Wrapper um openrouter_provider fuer Abwaertskompatibilitaet.
Alle alten Imports (from services.nscale_provider import ...) funktionieren weiter.
"""
import logging
from typing import Optional
from services.openrouter_provider import (
    chat_completion as _or_chat_completion,
    is_enabled,
    TASK_MODELS,
    DEFAULT_MODEL,
)

logger = logging.getLogger(__name__)

MODEL_REGISTRY = {
    "screening": {
        "model": DEFAULT_MODEL,
        "purpose": "Komplexe Bewerberanalyse, strukturierte Berichte, Kursempfehlung",
        "fallback": DEFAULT_MODEL,
        "max_tokens": 2048,
        "temperature": 0.3,
    },
    "classification": {
        "model": DEFAULT_MODEL,
        "purpose": "Schnelle Klassifikation, Dokumentenkategorisierung, Statusvorschlag",
        "fallback": DEFAULT_MODEL,
        "max_tokens": 512,
        "temperature": 0.1,
    },
    "summary": {
        "model": DEFAULT_MODEL,
        "purpose": "Kommunikationszusammenfassungen, Staff-Hinweise, Kurzbewertungen",
        "fallback": DEFAULT_MODEL,
        "max_tokens": 1024,
        "temperature": 0.4,
    },
    "suggestion": {
        "model": DEFAULT_MODEL,
        "purpose": "KI-Entscheidungshilfe, Empfehlungen, Workflow-Optimierung",
        "fallback": DEFAULT_MODEL,
        "max_tokens": 1024,
        "temperature": 0.3,
    },
    "oracle": {
        "model": DEFAULT_MODEL,
        "purpose": "Oracle Command Center – Live-Daten-Analyse, Betriebssteuerung",
        "fallback": DEFAULT_MODEL,
        "max_tokens": 2048,
        "temperature": 0.4,
    },
}


async def chat_completion(
    task: str,
    system_message: str,
    user_message: str,
    override_model: Optional[str] = None,
    override_temperature: Optional[float] = None,
    override_max_tokens: Optional[int] = None,
) -> dict:
    """Run chat completion via OpenRouter. Drop-in replacement for old nscale/DeepSeek provider."""
    config = MODEL_REGISTRY.get(task, MODEL_REGISTRY["summary"])
    temperature = override_temperature if override_temperature is not None else config["temperature"]
    max_tokens = override_max_tokens or config["max_tokens"]

    result = await _or_chat_completion(
        system_message=system_message,
        user_message=user_message,
        task=task,
        override_max_tokens=max_tokens,
        temperature=temperature,
        model_override=override_model,
    )

    return {
        "content": result.get("content"),
        "model": result.get("model", DEFAULT_MODEL),
        "task": task,
        "tokens_used": result.get("tokens_used", 0),
        "error": result.get("error"),
    }


def get_model_registry() -> dict:
    """Return current model registry for documentation/audit."""
    return {k: {
        "model": v["model"],
        "purpose": v["purpose"],
        "fallback": v["fallback"],
    } for k, v in MODEL_REGISTRY.items()}
