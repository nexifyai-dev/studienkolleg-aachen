"""
OpenRouter Provider – Einheitliche KI-Schnittstelle.

Endpunkt: https://openrouter.ai/api/v1/chat/completions
Auth: Bearer Token (OPENROUTER_API_KEY)

Modell: deepseek/deepseek-v4-flash fuer alle Aufgaben.
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Task-to-model mapping: Ein Modell fuer alles
TASK_MODELS = {
    "email_generation": "deepseek/deepseek-v4-flash",
    "brain_response": "deepseek/deepseek-v4-flash",
    "brain_extraction": "deepseek/deepseek-v4-flash",
    "general": "deepseek/deepseek-v4-flash",
}

# Fallback
DEFAULT_MODEL = "deepseek/deepseek-v4-flash"


def is_enabled() -> bool:
    return bool(OPENROUTER_API_KEY)


def _get_model_for_task(task: str) -> str:
    """Waehlt das passende Modell basierend auf der Aufgabe."""
    return TASK_MODELS.get(task, DEFAULT_MODEL)


async def chat_completion(
    system_message: str,
    user_message: str,
    task: str = "general",
    override_max_tokens: int = 4096,
    temperature: float = 0.3,
    model_override: str = None,
) -> dict:
    if not is_enabled():
        return {"error": "OpenRouter API key not configured", "content": None}

    model = model_override or _get_model_for_task(task)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.environ.get("APP_URL", "https://studienkolleg-aachen.de"),
        "X-Title": "W2G Studienkolleg Platform",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": override_max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(OPENROUTER_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        choice = data.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        usage = data.get("usage", {})
        tokens_used = usage.get("total_tokens", 0)

        logger.info(
            f"[OPENROUTER] task={task} model={model} "
            f"tokens={tokens_used} status=ok"
        )

        return {
            "content": content,
            "model": data.get("model", model),
            "tokens_used": tokens_used,
            "usage": usage,
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"[OPENROUTER] HTTP {e.response.status_code} model={model}: {e.response.text[:300]}")
        return {"error": f"HTTP {e.response.status_code}", "content": None}
    except Exception as e:
        logger.error(f"[OPENROUTER] Fehler model={model}: {e}")
        return {"error": str(e), "content": None}
