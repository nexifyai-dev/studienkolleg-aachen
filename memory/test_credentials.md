# Test Credentials

## Admin
- **Email:** admin@studienkolleg-aachen.de
- **Password:** ${TEST_ADMIN_PASSWORD}
- **Role:** superadmin

## Staff
- **Email:** staff@studienkolleg-aachen.de
- **Password:** ${TEST_DEFAULT_PASSWORD}
- **Role:** staff

## Teacher
- **Email:** teacher@studienkolleg-aachen.de
- **Password:** ${TEST_DEFAULT_PASSWORD}
- **Role:** teacher

## Applicant
- **Email:** applicant@studienkolleg-aachen.de
- **Password:** ${TEST_DEFAULT_PASSWORD}
- **Role:** applicant

## Partner / Affiliate
- **Email:** partner@studienkolleg-aachen.de
- **Password:** ${TEST_DEFAULT_PASSWORD}
- **Role:** affiliate

## Quick Login Test
```bash
API_URL="https://aachen-checkout.preview.emergentagent.com"
curl -s -c /tmp/staff.cookies -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d '{"email":"staff@studienkolleg-aachen.de","password":"${TEST_DEFAULT_PASSWORD}"}'
curl -s -b /tmp/staff.cookies "$API_URL/api/auth/me"
```
