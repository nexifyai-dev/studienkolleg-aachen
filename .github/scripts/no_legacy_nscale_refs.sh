#!/usr/bin/env bash
set -euo pipefail

FORBIDDEN_PATTERN='nscale|NSCALE|NSCall|EMERGENT_LLM_KEY'

# Explizit erlaubte Legacy-/Kompatibilitätsstellen.
ALLOWLIST=(
  '^backend/services/nscale_provider\.py:'
  '^backend/config\.py:'
  '^backend/server\.py:'
)

matches="$(rg -n "$FORBIDDEN_PATTERN" backend frontend || true)"

if [[ -z "$matches" ]]; then
  echo "No forbidden legacy references found."
  exit 0
fi

violations="$matches"
for allowed in "${ALLOWLIST[@]}"; do
  violations="$(printf '%s\n' "$violations" | rg -v "$allowed" || true)"
done

if [[ -n "$violations" ]]; then
  echo "Forbidden legacy references found (nscale/NSCall/EMERGENT_LLM_KEY):"
  printf '%s\n' "$violations"
  exit 1
fi

echo "Only allowlisted legacy references found."
