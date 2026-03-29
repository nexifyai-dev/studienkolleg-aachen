# Test Credentials

## Admin
- **Email:** admin@studienkolleg-aachen.de
- **Password:** DevSeed@2026!
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

## Admin Password (Backend Seed)
- **ADMIN_PASSWORD:** Admin@2026!

## Quick Login Test Commands
```bash
API_URL="https://ai-screening-staff.preview.emergentagent.com"

# Staff login
curl -s -c /tmp/staff.cookies -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d '{"email":"staff@studienkolleg-aachen.de","password":"DevSeed@2026!"}'

# Applicant login
curl -s -c /tmp/applicant.cookies -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d '{"email":"applicant@studienkolleg-aachen.de","password":"DevSeed@2026!"}'

# Partner login
curl -s -c /tmp/partner.cookies -X POST "$API_URL/api/auth/login" -H "Content-Type: application/json" -d '{"email":"partner@studienkolleg-aachen.de","password":"DevSeed@2026!"}'

# Use cookies: curl -s -b /tmp/staff.cookies "$API_URL/api/auth/me"
```
