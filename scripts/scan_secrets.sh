#!/usr/bin/env bash
# ──────────────────────────────────────────────
# W2G Secret Scanner – pre-commit / CI guard
#
# Prüft staged files auf bekannte Secret-Patterns.
# Aufruf: bash scripts/scan_secrets.sh [--all]
#   --all  → scannt alle tracked files statt nur staged
# ──────────────────────────────────────────────
set -euo pipefail

# ── ÄNDERUNGEN (Zeitstempel Europe/Berlin) ──────────────────────────────────
# 2026-08-13 09:15 CEST — Fix: hartkodiertes /app entfernt (Repo liegt hier unter
#   /workspace/customers/studienkolleg-aachen, nicht /app) → REPO_ROOT dynamisch
#   via git rev-parse. Vorher: Hook/Scanner wirkungslos (exit 128, kein Scan).
REPO_ROOT="$(git rev-parse --show-toplevel)"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Patterns that should never appear in committed code
PATTERNS=(
  'Admin@2026'
  'DevSeed@2026'
  'sk-emergent-'
  're_XDMFMkFp'
  'NSCALE_API_KEY=eyJ'
  'JWT_SECRET=d4f8a3b1'
  'RESEND_API_KEY=re_'
  'MEM0_API_KEY=m0-'
  'password.*Admin@'
  'password.*DevSeed@'
)

# Allowed files (documentation that intentionally contains credential references)
ALLOWED_FILES=(
  "memory/test_credentials.md"
  "scripts/scan_secrets.sh"
)

is_allowed() {
  local file="$1"
  for allowed in "${ALLOWED_FILES[@]}"; do
    if [[ "$file" == *"$allowed" ]]; then
      return 0
    fi
  done
  return 1
}

if [[ "${1:-}" == "--all" ]]; then
  FILES=$(git -C "$REPO_ROOT" ls-files)
else
  FILES=$(git -C "$REPO_ROOT" diff --cached --name-only 2>/dev/null || git -C "$REPO_ROOT" ls-files)
fi

FOUND=0

# ── ÄNDERUNG 2026-08-13 09:25 CEST — Perf-Fix: Ein-Grep-Pass mit kombiniertem
#   Pattern statt Pattern-äußerer Schleife (vorher O(Patterns×Dateien) mit je
#   einem file-/grep-Prozess je Datei → --all-Lauf >180 s Timeout). Treffer-
#   Detail je Pattern nur noch im seltenen Trefferfall (2. Pass je Treffer-Datei).
COMBINED=$(IFS='|'; echo "${PATTERNS[*]}")

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  [[ ! -f "$REPO_ROOT/$file" ]] && continue

  # Skip binary files
  file_type=$(file --mime-type -b "$REPO_ROOT/$file" 2>/dev/null || echo "unknown")
  [[ "$file_type" == application/octet-stream ]] && continue
  [[ "$file_type" == application/pdf ]] && continue
  [[ "$file_type" == image/* ]] && continue

  # Skip allowed files
  is_allowed "$file" && continue

  # Skip .env files (they SHOULD contain secrets)
  [[ "$file" == *.env ]] && continue
  [[ "$file" == *.env.* ]] && continue

  if grep -qnE "$COMBINED" "$REPO_ROOT/$file" 2>/dev/null; then
    for pattern in "${PATTERNS[@]}"; do
      if grep -q "$pattern" "$REPO_ROOT/$file" 2>/dev/null; then
        echo -e "${RED}SECRET FOUND${NC} in $file: pattern '$pattern'"
        FOUND=$((FOUND + 1))
      fi
    done
  fi
done <<< "$FILES"

if [[ $FOUND -gt 0 ]]; then
  echo ""
  echo -e "${RED}BLOCKED: $FOUND secret(s) found in tracked files.${NC}"
  echo "Fix: Remove secrets, use env vars, or add file to ALLOWED_FILES."
  exit 1
else
  echo -e "${GREEN}OK: No secrets found in tracked files.${NC}"
  exit 0
fi
