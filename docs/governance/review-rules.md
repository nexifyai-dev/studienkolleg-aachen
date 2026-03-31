# Review-Regeln für kritische Bereiche

## Kritische Pfade (CODEOWNERS)

- `backend/services/**` → Backend-Service-Owner
- `backend/routers/auth/**` → Security/Auth-Owner
- `frontend/src/App.js` → Frontend-Architecture-Owner
- `release/**` → Release-Owner

Siehe `.github/CODEOWNERS`.

## Verbindliche Freigaberegeln

1. Mindestens ein CODEOWNER-Review je betroffenem kritischem Pfad.
2. Status-Checks **müssen grün**:
   - `PR Quality Gate`
   - `Node.js CI`
3. Keine offenen Kernmängel (weder im PR-Template noch als Blocking-Label).
4. ADR-Pflicht gemäß `docs/governance/pr-policy.md` einhalten.

## Branch-Protection (GitHub-Einstellung)

Für `main` ist Branch Protection so zu konfigurieren, dass die oben genannten Status-Checks als **required** gesetzt sind und Merges bei fehlendem Review oder rotem Check verhindert werden.
