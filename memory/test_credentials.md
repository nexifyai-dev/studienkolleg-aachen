# W2G Platform – Test Credentials

## Admin Account (Seeded)
- Email: admin@studienkolleg-aachen.de
- Password: Admin@2026!
- Role: superadmin
- Redirect after login: /staff (dann /admin für Admin-Bereich)

## Test Applicant (erstellt durch Testing Agent iteration_1)
- Email: TEST_portal_ui@example.com
- Password: Portal@2026!
- Role: applicant
- Redirect after login: /portal

## Invite Flow
- Admin kann Invite-Links generieren via POST /api/auth/invite (authenticated)
- Invite-Link-URL: /auth/register?token=<TOKEN>
- Invite TTL: 7 Tage

## Lead-Claiming Flow
- User füllt /apply aus → Lead in DB ohne Passwort
- User registriert sich mit derselben Email unter /auth/register
- System erkennt Lead-Account, setzt Passwort (kein 409)

## Notes
- Passwort-Reset-Links werden bei fehlender RESEND_API_KEY ins Backend-Log geschrieben
- Invite-Links werden bei fehlender RESEND_API_KEY ins Backend-Log geschrieben
- Brute-Force-Lockout: 5 Fehlversuche → 15 min gesperrt (IP-basiert via X-Forwarded-For)
