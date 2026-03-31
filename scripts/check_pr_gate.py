#!/usr/bin/env python3
"""Fail PR quality gate when required governance conditions are not met."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REQUIRED_PHRASES = [
    "### 1) Risikoanalyse (Pflicht)",
    "### 2) ADR-Bedarf (Pflicht)",
    "### 3) Changelog-Update (Pflicht)",
    "### 4) Testevidenz (Pflicht)",
]

BLOCKING_LABELS = {
    "core-defect-open",
    "core-defect",
    "blocker",
    "release-blocker",
}


def fail(message: str) -> int:
    print(f"::error::{message}")
    return 1


def main() -> int:
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if not event_path:
        return fail("GITHUB_EVENT_PATH is not set.")

    event_file = Path(event_path)
    if not event_file.exists():
        return fail(f"Event payload not found: {event_file}")

    payload = json.loads(event_file.read_text(encoding="utf-8"))
    pr = payload.get("pull_request") or {}
    body = pr.get("body") or ""

    missing_sections = [phrase for phrase in REQUIRED_PHRASES if phrase not in body]
    if missing_sections:
        return fail(
            "PR template Pflichtfelder fehlen: " + ", ".join(missing_sections)
        )

    if "- [x] Ja (PR bleibt blockiert)" in body or "- [X] Ja (PR bleibt blockiert)" in body:
        return fail("Offene Kernmängel wurden markiert. PR bleibt blockiert.")

    labels = {
        (label.get("name") or "").strip().lower()
        for label in pr.get("labels", [])
        if isinstance(label, dict)
    }
    matched = sorted(labels.intersection(BLOCKING_LABELS))
    if matched:
        return fail(
            "Blocking Labels gefunden (Kernmangel offen): " + ", ".join(matched)
        )

    print("PR Quality Gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
