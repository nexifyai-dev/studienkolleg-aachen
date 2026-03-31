#!/usr/bin/env python3
"""Validate go-live checklist structure and enforce go-live gate."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


ALLOWED_RESULTS = {"pending", "pass", "fail"}
ALLOWED_UAT = {"pending", "approved", "rejected"}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Checklist root must be a mapping")
    return data


def validate_structure(data: dict) -> tuple[list[str], dict[str, dict], list[str]]:
    errors: list[str] = []
    criteria = data.get("criteria")
    if not isinstance(criteria, list):
        return ["'criteria' must be a list"], {}, []

    by_id: dict[str, dict] = {}
    for item in criteria:
        if not isinstance(item, dict):
            errors.append("Each criterion must be a mapping")
            continue

        criterion_id = item.get("id")
        if not criterion_id:
            errors.append("Criterion missing 'id'")
            continue
        if criterion_id in by_id:
            errors.append(f"Duplicate criterion id: {criterion_id}")
            continue

        for required in ("category", "title", "owner", "deadline", "status", "mandatory"):
            if required not in item:
                errors.append(f"{criterion_id}: missing '{required}'")

        category = item.get("category")
        if category == "TECH":
            verification = item.get("verification")
            if not isinstance(verification, dict):
                errors.append(f"{criterion_id}: TECH criteria require 'verification'")
            else:
                for required in ("type", "description", "evidence_artifact", "verification_command", "result"):
                    if required not in verification:
                        errors.append(f"{criterion_id}: verification missing '{required}'")
                result = verification.get("result")
                if result not in ALLOWED_RESULTS:
                    errors.append(f"{criterion_id}: verification.result must be one of {sorted(ALLOWED_RESULTS)}")

        if category == "LEGAL":
            legal = item.get("legal")
            if not isinstance(legal, dict):
                errors.append(f"{criterion_id}: LEGAL criteria require 'legal'")
            else:
                for required in (
                    "document_name",
                    "version",
                    "signoff_date",
                    "signed_by",
                    "live_url",
                    "page_version",
                    "evidence_artifact",
                ):
                    if required not in legal:
                        errors.append(f"{criterion_id}: legal missing '{required}'")

        if category == "OPERATIONS":
            uat = item.get("uat")
            if not isinstance(uat, dict):
                errors.append(f"{criterion_id}: OPERATIONS criteria require 'uat'")
            else:
                for required in (
                    "case_id",
                    "scenario",
                    "acceptance_owner",
                    "acceptance_status",
                    "acceptance_date",
                    "protocol_artifact",
                ):
                    if required not in uat:
                        errors.append(f"{criterion_id}: uat missing '{required}'")
                if uat.get("acceptance_status") not in ALLOWED_UAT:
                    errors.append(f"{criterion_id}: uat.acceptance_status must be one of {sorted(ALLOWED_UAT)}")

        by_id[criterion_id] = item

    required = data.get("gate", {}).get("required_criteria", [])
    if not isinstance(required, list):
        errors.append("gate.required_criteria must be a list")
        required = []

    for criterion_id in required:
        if criterion_id not in by_id:
            errors.append(f"gate.required_criteria references unknown id '{criterion_id}'")

    return errors, by_id, required


def evaluate_go_live(by_id: dict[str, dict], required: list[str]) -> list[str]:
    blockers: list[str] = []
    for criterion_id in required:
        item = by_id[criterion_id]
        if item.get("status") != "done":
            blockers.append(f"{criterion_id}: status is '{item.get('status')}', expected 'done'")

        category = item.get("category")
        if category == "TECH":
            result = item.get("verification", {}).get("result")
            if result != "pass":
                blockers.append(f"{criterion_id}: verification.result is '{result}', expected 'pass'")

        elif category == "LEGAL":
            legal = item.get("legal", {})
            if not legal.get("signoff_date"):
                blockers.append(f"{criterion_id}: legal.signoff_date is missing")
            if not legal.get("version"):
                blockers.append(f"{criterion_id}: legal.version is missing")
            if not legal.get("live_url") or not legal.get("page_version"):
                blockers.append(f"{criterion_id}: legal live_url/page_version must be set")

        elif category == "OPERATIONS":
            uat = item.get("uat", {})
            if uat.get("acceptance_status") != "approved":
                blockers.append(
                    f"{criterion_id}: uat.acceptance_status is '{uat.get('acceptance_status')}', expected 'approved'"
                )
            if not uat.get("acceptance_date"):
                blockers.append(f"{criterion_id}: uat.acceptance_date is missing")

    return blockers


def main() -> int:
    parser = argparse.ArgumentParser(description="Go-live gate validation")
    parser.add_argument("--file", default="release/golive_checklist.yaml", help="Path to checklist YAML")
    parser.add_argument(
        "--check",
        choices=("structure", "go-live"),
        default="go-live",
        help="Run structure validation only or enforce full go-live criteria",
    )
    args = parser.parse_args()

    data = load_yaml(Path(args.file))
    errors, by_id, required = validate_structure(data)
    if errors:
        print("❌ Checklist structure invalid:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"✅ Checklist structure valid ({len(by_id)} Kriterien).")
    if args.check == "structure":
        return 0

    blockers = evaluate_go_live(by_id, required)
    if blockers:
        print("🚫 GO-LIVE GATE: NO-GO")
        for blocker in blockers:
            print(f"  - {blocker}")
        return 1

    print("✅ GO-LIVE GATE: GO")
    return 0


if __name__ == "__main__":
    sys.exit(main())
