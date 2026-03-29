"""
NSCall (nscale) AI Provider – Zentrale Inferenzschicht für alle KI-Funktionen.

Alle produktiven KI-Funktionen der Plattform laufen über die nscale API.
Kein anderer Modellprovider wird für Produktiv-KI genutzt.

Architektur:
- OpenAI-kompatible API (https://inference.api.nscale.com/v1)
- Task-basierte Modellauswahl (Screening, Klassifikation, Zusammenfassung)
- Fallback-Strategie bei Modellfehlern
- Dokumentierte, austauschbare, auditierbare Modellzuweisung

Modellstrategie:
- SCREENING (komplex): Qwen/Qwen3-235B-A22B-Instruct-2507 (stärkstes verfügbares Modell)
- CLASSIFICATION (schnell): meta-llama/Llama-3.3-70B-Instruct (gutes Preis-Leistungs-Verhältnis)
- SUMMARY (mittel): Qwen/Qwen3-32B (solider Mittelweg)
- FALLBACK: deepseek-ai/DeepSeek-R1-Distill-Llama-70B (Reasoning-optimiert)
"""
import os
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

NSCALE_BASE_URL = "https://inference.api.nscale.com/v1"

# Task-basierte Modellzuweisung (dokumentiert + austauschbar)
MODEL_REGISTRY = {
    "screening": {
        "model": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "purpose": "Komplexe Bewerberanalyse, strukturierte Berichte, Kursempfehlung",
        "fallback": "meta-llama/Llama-3.3-70B-Instruct",
        "max_tokens": 2048,
        "temperature": 0.3,
    },
    "classification": {
        "model": "meta-llama/Llama-3.3-70B-Instruct",
        "purpose": "Schnelle Klassifikation, Dokumentenkategorisierung, Statusvorschlag",
        "fallback": "Qwen/Qwen3-32B",
        "max_tokens": 512,
        "temperature": 0.1,
    },
    "summary": {
        "model": "Qwen/Qwen3-32B",
        "purpose": "Kommunikationszusammenfassungen, Staff-Hinweise, Kurzbewertungen",
        "fallback": "meta-llama/Llama-3.1-8B-Instruct",
        "max_tokens": 1024,
        "temperature": 0.4,
    },
    "suggestion": {
        "model": "Qwen/Qwen3-235B-A22B-Instruct-2507",
        "purpose": "KI-Entscheidungshilfe, Empfehlungen, Workflow-Optimierung",
        "fallback": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "max_tokens": 1024,
        "temperature": 0.3,
    },
}


def _get_client() -> Optional[OpenAI]:
    """Initialize nscale OpenAI client."""
    api_key = os.environ.get("NSCALE_API_KEY", "")
    if not api_key:
        logger.warning("[NSCALE] NSCALE_API_KEY not set – AI features disabled")
        return None
    return OpenAI(base_url=NSCALE_BASE_URL, api_key=api_key)


def is_enabled() -> bool:
    """Check if nscale AI is available."""
    return bool(os.environ.get("NSCALE_API_KEY", ""))


async def chat_completion(
    task: str,
    system_message: str,
    user_message: str,
    override_model: Optional[str] = None,
    override_temperature: Optional[float] = None,
    override_max_tokens: Optional[int] = None,
) -> dict:
    """
    Run a chat completion via nscale.

    Args:
        task: Task type key from MODEL_REGISTRY (screening, classification, summary, suggestion)
        system_message: System prompt
        user_message: User prompt
        override_model: Optional model override
        override_temperature: Optional temperature override
        override_max_tokens: Optional max_tokens override

    Returns:
        dict with 'content', 'model', 'task', 'tokens_used', 'error'
    """
    config = MODEL_REGISTRY.get(task, MODEL_REGISTRY["summary"])
    model = override_model or config["model"]
    temperature = override_temperature if override_temperature is not None else config["temperature"]
    max_tokens = override_max_tokens or config["max_tokens"]

    client = _get_client()
    if not client:
        return {
            "content": None,
            "model": model,
            "task": task,
            "tokens_used": 0,
            "error": "NSCALE_API_KEY not configured",
        }

    # Try primary model, then fallback
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
            # Strip thinking tags if present (some models like Qwen3 use <think> tags)
            if content and "<think>" in content:
                import re
                content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

            tokens = getattr(response.usage, 'total_tokens', 0) if response.usage else 0

            logger.info(f"[NSCALE] Task={task} Model={attempt_model} Tokens={tokens}")
            return {
                "content": content,
                "model": attempt_model,
                "task": task,
                "tokens_used": tokens,
                "error": None,
            }
        except Exception as e:
            logger.warning(f"[NSCALE] Model {attempt_model} failed: {e}")
            if attempt_model == config.get("fallback", model):
                return {
                    "content": None,
                    "model": attempt_model,
                    "task": task,
                    "tokens_used": 0,
                    "error": str(e),
                }
            continue

    return {"content": None, "model": model, "task": task, "tokens_used": 0, "error": "All models failed"}


def get_model_registry() -> dict:
    """Return current model registry for documentation/audit."""
    return {k: {
        "model": v["model"],
        "purpose": v["purpose"],
        "fallback": v["fallback"],
    } for k, v in MODEL_REGISTRY.items()}
