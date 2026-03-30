# Test Credentials

## Admin
- **Email:** admin@studienkolleg-aachen.de
- **Password:** Admin@2026!
- **Role:** superadmin

## Staff
- **Email:** staff@studienkolleg-aachen.de
- **Password:** DevSeed@2026!
- **Role:** staff

## Teacher
- **Email:** teacher@studienkolleg-aachen.de
- **Password:** DevSeed@2026!
- **Role:** teacher

## Applicant
- **Email:** applicant@studienkolleg-aachen.de
- **Password:** DevSeed@2026!
- **Role:** applicant

## Partner / Affiliate
- **Email:** partner@studienkolleg-aachen.de
- **Password:** DevSeed@2026!
- **Role:** affiliate

## Quick Login Test
```bash
API_URL="https://aachen-checkout.preview.emergentagent.com"
curl -s -c /tmp/staff.cookies -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d '{"email":"staff@studienkolleg-aachen.de","password":"DevSeed@2026!"}'
curl -s -b /tmp/staff.cookies "$API_URL/api/auth/me"
```
