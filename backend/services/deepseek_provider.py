"""
DeepSeek AI Provider – zentrale Inferenzschicht für alle KI-Funktionen.

Alle produktiven KI-Funktionen der Plattform laufen über DeepSeek.
"""
import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

MODEL_REGISTRY = {
    "screening": {
        "model": "deepseek-chat",
        "purpose": "Komplexe Bewerberanalyse, strukturierte Berichte, Kursempfehlung",
        "fallback": "deepseek-reasoner",
        "max_tokens": 2048,
        "temperature": 0.2,
    },
    "classification": {
        "model": "deepseek-chat",
        "purpose": "Schnelle Klassifikation, Dokumentenkategorisierung, Statusvorschlag",
        "fallback": "deepseek-reasoner",
        "max_tokens": 700,
        "temperature": 0.1,
    },
    "summary": {
        "model": "deepseek-chat",
        "purpose": "Kommunikationszusammenfassungen, Staff-Hinweise, Kurzbewertungen",
        "fallback": "deepseek-reasoner",
        "max_tokens": 1100,
        "temperature": 0.3,
    },
    "suggestion": {
        "model": "deepseek-reasoner",
        "purpose": "KI-Entscheidungshilfe, Empfehlungen, Workflow-Optimierung",
        "fallback": "deepseek-chat",
        "max_tokens": 1200,
        "temperature": 0.2,
    },
}


def _get_client() -> Optional[OpenAI]:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        logger.warning("[DEEPSEEK] DEEPSEEK_API_KEY not set – AI features disabled")
        return None
    return OpenAI(base_url=DEEPSEEK_BASE_URL, api_key=api_key)


def is_enabled() -> bool:
    return bool(os.environ.get("DEEPSEEK_API_KEY", ""))


async def chat_completion(task: str, system_message: str, user_message: str,
                          override_model: Optional[str] = None,
                          override_temperature: Optional[float] = None,
                          override_max_tokens: Optional[int] = None) -> dict:
    config = MODEL_REGISTRY.get(task, MODEL_REGISTRY["summary"])
    model = override_model or config["model"]
    temperature = override_temperature if override_temperature is not None else config["temperature"]
    max_tokens = override_max_tokens or config["max_tokens"]

    client = _get_client()
    if not client:
        return {"content": None, "model": model, "task": task, "tokens_used": 0, "error": "DEEPSEEK_API_KEY not configured"}

    for attempt_model in [model, config.get("fallback", model)]:
        try:
            response = client.chat.completions.create(
                model=attempt_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            tokens = getattr(response.usage, 'total_tokens', 0) if response.usage else 0
            logger.info(f"[DEEPSEEK] Task={task} Model={attempt_model} Tokens={tokens}")
            return {"content": content, "model": attempt_model, "task": task, "tokens_used": tokens, "error": None}
        except Exception as e:
            logger.warning(f"[DEEPSEEK] Model {attempt_model} failed: {e}")
            if attempt_model == config.get("fallback", model):
                return {"content": None, "model": attempt_model, "task": task, "tokens_used": 0, "error": str(e)}
    return {"content": None, "model": model, "task": task, "tokens_used": 0, "error": "All models failed"}


def get_model_registry() -> dict:
    return {k: {"model": v["model"], "purpose": v["purpose"], "fallback": v["fallback"]} for k, v in MODEL_REGISTRY.items()}
