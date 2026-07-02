"""
DeepSeek Provider – Einheitliche KI-Schnittstelle.

Endpunkt: https://api.deepseek.com (OpenAI-kompatibel)
Auth: Bearer Token (DEEPSEEK_API_KEY)

Modell: deepseek-chat fuer alle Aufgaben.
"""
import os
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

DEFAULT_MODEL = "deepseek-chat"

# Task-to-model mapping: Ein Modell fuer alles
TASK_MODELS = {
    "email_generation": DEFAULT_MODEL,
    "brain_response": DEFAULT_MODEL,
    "brain_extraction": DEFAULT_MODEL,
    "general": DEFAULT_MODEL,
}

_client = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None and DEEPSEEK_API_KEY:
        _client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


def is_enabled() -> bool:
    return bool(DEEPSEEK_API_KEY)


def _get_model_for_task(task: str) -> str:
    return TASK_MODELS.get(task, DEFAULT_MODEL)


async def chat_completion(
    system_message: str,
    user_message: str,
    task: str = "general",
    override_max_tokens: int = 4096,
    temperature: float = 0.3,
    model_override: str = None,
) -> dict:
    client = _get_client()
    if not client:
        return {"error": "DeepSeek API key not configured", "content": None}

    model = model_override or _get_model_for_task(task)
    if not model or "/" in model:
        model = DEFAULT_MODEL

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=override_max_tokens,
            timeout=90.0,
        )

        content = response.choices[0].message.content or ""
        usage = response.usage.model_dump() if response.usage else {}
        tokens_used = usage.get("total_tokens", 0)

        logger.info(
            f"[DEEPSEEK] task={task} model={model} "
            f"tokens={tokens_used} status=ok"
        )

        return {
            "content": content,
            "model": response.model or model,
            "tokens_used": tokens_used,
            "usage": usage,
        }

    except Exception as e:
        logger.error(f"[DEEPSEEK] Fehler model={model}: {e}")
        return {"error": str(e), "content": None}
