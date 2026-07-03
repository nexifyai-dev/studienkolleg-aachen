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

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
EMERGENT_BASE_URL = "https://integrations.emergentagent.com/llm"
FALLBACK_MODEL = "gpt-4o-mini"

DEFAULT_MODEL = "deepseek-chat"

# Task-to-model mapping: Ein Modell fuer alles
TASK_MODELS = {
    "email_generation": DEFAULT_MODEL,
    "brain_response": DEFAULT_MODEL,
    "brain_extraction": DEFAULT_MODEL,
    "general": DEFAULT_MODEL,
}

_client = None
_fallback_client = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None and DEEPSEEK_API_KEY:
        _client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


def _get_fallback_client() -> AsyncOpenAI:
    global _fallback_client
    if _fallback_client is None and EMERGENT_LLM_KEY:
        _fallback_client = AsyncOpenAI(api_key=EMERGENT_LLM_KEY, base_url=EMERGENT_BASE_URL)
    return _fallback_client


def is_enabled() -> bool:
    return bool(DEEPSEEK_API_KEY or EMERGENT_LLM_KEY)


def _get_model_for_task(task: str) -> str:
    return TASK_MODELS.get(task, DEFAULT_MODEL)


async def _do_completion(client, model, system_message, user_message, temperature, max_tokens, task, provider_label):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=90.0,
    )
    content = response.choices[0].message.content or ""
    usage = response.usage.model_dump() if response.usage else {}
    tokens_used = usage.get("total_tokens", 0)
    logger.info(f"[{provider_label}] task={task} model={model} tokens={tokens_used} status=ok")
    return {
        "content": content,
        "model": response.model or model,
        "tokens_used": tokens_used,
        "usage": usage,
    }


async def chat_completion(
    system_message: str,
    user_message: str,
    task: str = "general",
    override_max_tokens: int = 4096,
    temperature: float = 0.3,
    model_override: str = None,
) -> dict:
    """Primaer DeepSeek, automatischer Fallback auf Emergent LLM (gpt-4o-mini)."""
    model = model_override or _get_model_for_task(task)
    if not model or "/" in model:
        model = DEFAULT_MODEL

    client = _get_client()
    primary_error = None
    if client:
        try:
            return await _do_completion(client, model, system_message, user_message,
                                        temperature, override_max_tokens, task, "DEEPSEEK")
        except Exception as e:
            primary_error = str(e)
            logger.warning(f"[DEEPSEEK] Fehler model={model}: {e} – versuche Fallback")

    fallback = _get_fallback_client()
    if fallback:
        try:
            return await _do_completion(fallback, FALLBACK_MODEL, system_message, user_message,
                                        temperature, override_max_tokens, task, "EMERGENT_FALLBACK")
        except Exception as e:
            logger.error(f"[EMERGENT_FALLBACK] Fehler: {e}")
            return {"error": f"primary={primary_error}; fallback={e}", "content": None}

    return {"error": primary_error or "Kein KI-Provider konfiguriert", "content": None}
