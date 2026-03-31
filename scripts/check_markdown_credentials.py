#!/usr/bin/env python3
"""Block obvious credential leaks in tracked documentation/report files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ALLOWED_PLACEHOLDER_TOKENS = {
    "<from_internal_secret_manager>",
    "<environment_specific_api_url>",
    "<superadmin_login_identifier>",
    "<staff_login_identifier>",
    "<teacher_login_identifier>",
    "<applicant_login_identifier>",
    "<affiliate_login_identifier>",
    "<redacted>",
    "<placeholder>",
    "YOUR_API_KEY",
    "REPLACE_ME",
    "CHANGEME",
}

EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PASSWORD_ASSIGN_RE = re.compile(
    r'(?i)\b(password|passwort|pwd)\b\s*[:=]\s*["\'`]?([^\s"\'`|]{6,})'
)
JSON_PASSWORD_RE = re.compile(r'"password"\s*:\s*"([^"]{6,})"', re.IGNORECASE)
AUTH_HEADER_RE = re.compile(r"Authorization\s*:\s*Token\s+([^\s]+)", re.IGNORECASE)


SCAN_GLOBS = ("*.md", "*.json", "*.yaml", "*.yml", "*.txt")


def git_tracked_text_files() -> list[Path]:
    cmd = ["git", "ls-files", *SCAN_GLOBS]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    files = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    return files


def is_placeholder(value: str) -> bool:
    cleaned = value.strip().strip('"\'`')
    if not cleaned:
        return True
    if cleaned in ALLOWED_PLACEHOLDER_TOKENS:
        return True
    if cleaned.startswith("<"):
        return True
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return True
    if "secret" in cleaned.lower() or "vault" in cleaned.lower():
        return True
    return False


def looks_like_secret(value: str) -> bool:
    candidate = value.strip().strip('"\'`')
    if len(candidate) < 8:
        return False
    if candidate.lower() in {"password", "passwort"}:
        return False
    has_digit = any(ch.isdigit() for ch in candidate)
    has_special = any(not ch.isalnum() for ch in candidate)
    return has_digit or has_special


def scan_file(path: Path) -> list[str]:
    issues: list[str] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for match in PASSWORD_ASSIGN_RE.finditer(line):
            candidate = match.group(2)
            if not is_placeholder(candidate) and looks_like_secret(candidate):
                issues.append(f"{path}:{idx}: potential password assignment '{candidate}'")

        for match in JSON_PASSWORD_RE.finditer(line):
            candidate = match.group(1)
            if not is_placeholder(candidate) and looks_like_secret(candidate):
                issues.append(f"{path}:{idx}: potential JSON password value '{candidate}'")

        auth_match = AUTH_HEADER_RE.search(line)
        if auth_match and not is_placeholder(auth_match.group(1)):
            issues.append(f"{path}:{idx}: potential API token in Authorization header")

        if EMAIL_RE.search(line) and ("|" in line or "password" in line.lower()):
            if "<" not in line and "placeholder" not in line.lower():
                issues.append(f"{path}:{idx}: potential real email credential entry")

    return issues


def main() -> int:
    files = git_tracked_text_files()
    findings: list[str] = []
    for path in files:
        findings.extend(scan_file(path))

    if findings:
        print("Credential scan failed. Potential secrets found in Markdown:")
        for finding in findings:
            print(f"- {finding}")
        print("\nUse placeholders and store real values in internal secret management.")
        return 1

    print(f"Credential scan passed ({len(files)} tracked text files checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
