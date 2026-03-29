# Test Credentials – W2G Platform

## Kernrollen (Dev/Preview)

| Rolle | E-Mail | Passwort | Systemrolle |
|-------|--------|----------|-------------|
| Admin | admin@studienkolleg-aachen.de | Admin@2026! | superadmin |
| Staff | staff@studienkolleg-aachen.de | DevSeed@2026! | staff |
| Lehrer | teacher@studienkolleg-aachen.de | DevSeed@2026! | teacher |
| Bewerber | applicant@studienkolleg-aachen.de | DevSeed@2026! | applicant |

## Wie Accounts erzeugt werden

- **Admin**: via `ADMIN_EMAIL` + `ADMIN_PASSWORD` in `backend/.env` (seed.py)
- **Staff/Teacher/Applicant**: via `SEED_DEV_PASSWORD` in `backend/.env` (seed.py)
- Alle Accounts werden idempotent beim Backend-Start geseeded
- Passwort-Rotation: Ändern der ENV-Variable → nächster Start aktualisiert den Hash

## API Testing

```bash
API_URL=https://legal-i18n-verify.preview.emergentagent.com

# Admin Login
curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@studienkolleg-aachen.de","password":"Admin@2026!"}'

# Teacher Login
curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@studienkolleg-aachen.de","password":"DevSeed@2026!"}'
```

## Lead/Application Test (Formular)

Dokument-Uploads: base64-encoded im JSON-Body bei /api/leads/ingest
