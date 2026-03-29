# Test Credentials – W2G Platform

## Admin-Zugang
- E-Mail: admin@studienkolleg-aachen.de
- Passwort: Admin@2026!
- Rolle: superadmin
- Hinweis: Idempotent durch seed.py erzeugt

## Test-Bewerber
- E-Mail: TEST_portal_ui@example.com
- Passwort: Portal@2026!
- Rolle: applicant
- Hinweis: Wird vom Testing-Agent erwartet

## Test-Bewerberdaten (für Formular-Tests)
- E-Mail: test-phase3-2026@example.com (bereits in DB)
- Application ID: 69c8b08ac3ab59729d52e226

## URLs (aktuell)
- Frontend: https://legal-i18n-verify.preview.emergentagent.com
- Backend: https://legal-i18n-verify.preview.emergentagent.com/api
- Backend (lokal): http://localhost:8001

## Testrouten
- Öffentlich: /, /apply, /legal, /agb, /privacy, /courses, /services, /contact
- Auth: /auth/login, /auth/register, /auth/forgot-password
- Staff: /staff, /staff/kanban, /staff/applications/{id}
- Admin: /admin, /admin/users, /admin/audit
- Portal: /portal, /portal/documents, /portal/journey, /portal/messages

## Test-API-Endpunkte
- POST /api/leads/ingest (öffentlich)
- POST /api/auth/login
- GET /api/applications/{id}/ai-screenings (Staff)
- POST /api/applications/{id}/ai-screen (Staff)
- GET /api/internal/cost-simulator/config (Staff, Feature-Flag)

## Wichtige Hinweise für Testing
- Auth: httpOnly Cookies (nicht Authorization Header für Login)
- AI Screening: LLM kann null sein (Budget), lokale Checks laufen immer
- Email: Resend-Domain nicht verifiziert → Emails loggen, nicht senden (kein Test-Fehler)
- Uploads: base64-encoded im JSON-Body bei /api/leads/ingest
