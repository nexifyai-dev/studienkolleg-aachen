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

## Portal-Zugänge

- **Admin**: /auth/login → /staff → /admin
- **Staff**: /auth/login → /staff (Dashboard + Kanban)
- **Teacher**: /auth/login → /staff (nur Lehrer-Dashboard, kein Kanban)
- **Applicant**: /auth/login → /portal (Dashboard + Onboarding-Tour + Consent-Management)

## API Testing

```bash
API_URL=https://ai-screening-staff.preview.emergentagent.com

# Admin Login
curl -s -c /tmp/admin.cookies -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@studienkolleg-aachen.de","password":"Admin@2026!"}'

# Teacher Login
curl -s -c /tmp/teacher.cookies -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"teacher@studienkolleg-aachen.de","password":"DevSeed@2026!"}'

# Teacher: My Students
curl -s -b /tmp/teacher.cookies "$API_URL/api/teacher/my-students"

# Applicant: Consent Types
curl -s -b /tmp/applicant.cookies "$API_URL/api/consents/types"

# Staff: AI Model Registry
curl -s -b /tmp/staff.cookies "$API_URL/api/ai/model-registry"
```
