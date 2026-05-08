"""
nscale Vision Provider – Llama-4-Scout fuer Bild-/Dokumentenanalyse.

Modell: meta-llama/Llama-4-Scout-17B-16E-Instruct
API: OpenAI-kompatibel via https://inference.api.nscale.com/v1
Faehigkeiten: Multimodal (Text + Bilder), 10M Context Window

Einsatzgebiete:
- Dokumentenklassifikation (Ausweis vs. Zeugnis vs. irrelevant)
- OCR / Textextraktion aus Scans und Fotos
- Echtheitsbewertung (strukturelle Muster)
- Ausstellungsland-Erkennung
- Strukturierte Datenextraktion (Name, Datum, Noten, etc.)
"""
import os
import base64
import logging
from typing import Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

NSCALE_BASE_URL = "https://inference.api.nscale.com/v1"
VISION_MODEL = "meta-llama/Llama-4-Scout-17B-16E-Instruct"


def _get_client() -> Optional[OpenAI]:
    api_key = os.environ.get("NSCALE_API_KEY", "")
    if not api_key:
        logger.warning("[NSCALE_VISION] NSCALE_API_KEY nicht gesetzt – Vision deaktiviert")
        return None
    return OpenAI(base_url=NSCALE_BASE_URL, api_key=api_key)


def is_vision_enabled() -> bool:
    return bool(os.environ.get("NSCALE_API_KEY", ""))


def _encode_image_bytes(data: bytes, content_type: str = "image/jpeg") -> str:
    """Konvertiert Bild-Bytes zu base64 Data-URL."""
    b64 = base64.b64encode(data).decode("utf-8")
    mime = content_type if content_type.startswith("image/") else "image/jpeg"
    return f"data:{mime};base64,{b64}"


async def analyze_image(
    image_data: bytes,
    content_type: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> dict:
    """
    Analysiert ein Bild mit Llama-4-Scout Vision.

    Args:
        image_data: Bild als Bytes
        content_type: MIME-Typ (image/jpeg, image/png, etc.)
        system_prompt: System-Anweisung
        user_prompt: Benutzer-Anfrage
        max_tokens: Max Antwort-Tokens
        temperature: Kreativitaet

    Returns:
        dict mit content, model, tokens_used, error
    """
    client = _get_client()
    if not client:
        return {"content": None, "model": VISION_MODEL, "tokens_used": 0,
                "error": "NSCALE_API_KEY nicht konfiguriert"}

    image_url = _encode_image_bytes(image_data, content_type)

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        logger.info(f"[NSCALE_VISION] Analyse OK – {tokens} Tokens")
        return {"content": content, "model": VISION_MODEL, "tokens_used": tokens, "error": None}
    except Exception as e:
        logger.error(f"[NSCALE_VISION] Fehler: {e}")
        return {"content": None, "model": VISION_MODEL, "tokens_used": 0, "error": str(e)}


async def analyze_multiple_images(
    images: list,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 3000,
    temperature: float = 0.1,
) -> dict:
    """
    Analysiert mehrere Bilder gleichzeitig (z.B. mehrseitige PDFs).

    Args:
        images: Liste von (bytes, content_type) Tupeln
        system_prompt: System-Anweisung
        user_prompt: Benutzer-Anfrage

    Returns:
        dict mit content, model, tokens_used, error
    """
    client = _get_client()
    if not client:
        return {"content": None, "model": VISION_MODEL, "tokens_used": 0,
                "error": "NSCALE_API_KEY nicht konfiguriert"}

    content_parts = [{"type": "text", "text": user_prompt}]
    for img_bytes, img_type in images[:5]:
        url = _encode_image_bytes(img_bytes, img_type)
        content_parts.append({"type": "image_url", "image_url": {"url": url}})

    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_parts},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0
        logger.info(f"[NSCALE_VISION] Multi-Image Analyse OK – {tokens} Tokens, {len(images)} Bilder")
        return {"content": content, "model": VISION_MODEL, "tokens_used": tokens, "error": None}
    except Exception as e:
        logger.error(f"[NSCALE_VISION] Multi-Image Fehler: {e}")
        return {"content": None, "model": VISION_MODEL, "tokens_used": 0, "error": str(e)}


def pdf_to_images(pdf_bytes: bytes, max_pages: int = 5, dpi: int = 200) -> list:
    """
    Konvertiert PDF-Seiten zu JPEG-Bildern fuer Vision-Analyse.

    Returns:
        Liste von (jpeg_bytes, 'image/jpeg') Tupeln
    """
    try:
        from pdf2image import convert_from_bytes
        from io import BytesIO
        pages = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=max_pages)
        result = []
        for page in pages:
            buf = BytesIO()
            page.save(buf, format="JPEG", quality=85)
            result.append((buf.getvalue(), "image/jpeg"))
        logger.info(f"[PDF_TO_IMG] {len(result)} Seiten konvertiert (DPI={dpi})")
        return result
    except Exception as e:
        logger.error(f"[PDF_TO_IMG] Konvertierung fehlgeschlagen: {e}")
        return []
