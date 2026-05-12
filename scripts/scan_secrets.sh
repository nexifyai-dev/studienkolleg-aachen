#!/usr/bin/env bash
# ──────────────────────────────────────────────
# W2G Secret Scanner – pre-commit / CI guard
#
# Prüft staged files auf bekannte Secret-Patterns.
# Aufruf: bash scripts/scan_secrets.sh [--all]
#   --all  → scannt alle tracked files statt nur staged
# ──────────────────────────────────────────────
set -euo pipefail

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
  FILES=$(cd /app && git ls-files)
else
  FILES=$(cd /app && git diff --cached --name-only 2>/dev/null || git ls-files)
fi

FOUND=0

for pattern in "${PATTERNS[@]}"; do
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ ! -f "/app/$file" ]] && continue

    # Skip binary files
    file_type=$(file --mime-type -b "/app/$file" 2>/dev/null || echo "unknown")
    [[ "$file_type" == application/octet-stream ]] && continue
    [[ "$file_type" == application/pdf ]] && continue
    [[ "$file_type" == image/* ]] && continue

    # Skip allowed files
    is_allowed "$file" && continue

    # Skip .env files (they SHOULD contain secrets)
    [[ "$file" == *.env ]] && continue
    [[ "$file" == *.env.* ]] && continue

    if grep -q "$pattern" "/app/$file" 2>/dev/null; then
      echo -e "${RED}SECRET FOUND${NC} in $file: pattern '$pattern'"
      FOUND=$((FOUND + 1))
    fi
  done <<< "$FILES"
done

if [[ $FOUND -gt 0 ]]; then
  echo ""
  echo -e "${RED}BLOCKED: $FOUND secret(s) found in tracked files.${NC}"
  echo "Fix: Remove secrets, use env vars, or add file to ALLOWED_FILES."
  exit 1
else
  echo -e "${GREEN}OK: No secrets found in tracked files.${NC}"
  exit 0
fi
