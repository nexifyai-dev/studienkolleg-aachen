"""Area-specific process profile loading.

Profiles are JSON files in backend/config/process_profiles/*.json and define
required documents, status chain, automations and template keys per area.
"""

import json
from functools import lru_cache
from pathlib import Path

PROFILE_DIR = Path(__file__).resolve().parents[1] / "config" / "process_profiles"
DEFAULT_AREA = "studienkolleg"


@lru_cache(maxsize=1)
def _load_profiles() -> dict:
    profiles = {}
    if not PROFILE_DIR.exists():
        return profiles

    for file in PROFILE_DIR.glob("*.json"):
        with file.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        area = payload.get("area") or file.stem
        profiles[area] = payload

    return profiles


def list_process_profiles() -> list[dict]:
    return list(_load_profiles().values())


def get_process_profile(area: str | None) -> dict:
    profiles = _load_profiles()
    if area and area in profiles:
        return profiles[area]

    if DEFAULT_AREA in profiles:
        return profiles[DEFAULT_AREA]

    return {
        "area": DEFAULT_AREA,
        "label": "Standard",
        "required_documents": ["language_certificate", "highschool_diploma", "passport"],
        "status_chain": ["lead_new", "in_review", "pending_docs", "offer_sent", "enrolled", "declined", "archived"],
        "automations": {},
        "templates": {},
    }


def get_required_documents_for_area(area: str | None) -> list[str]:
    profile = get_process_profile(area)
    return profile.get("required_documents", [])
