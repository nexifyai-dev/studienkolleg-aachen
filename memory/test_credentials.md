# W2G Platform – Test Credentials

## Admin Account
- Email: admin@studienkolleg-aachen.de
- Password: Admin@2026!
- Role: superadmin
- Portal: /staff (nach Login) oder /admin

## Test Applicant (erstellt durch Testing Agent)
- Testbewerber können über /auth/register erstellt werden
- Oder über /apply (lead ingest) und danach /auth/register mit derselben Email (Account-Claiming-Flow)

## Notes
- Admin ist in der Seed-Funktion verankert und wird beim Serverstart automatisch angelegt
- Passwortreset-Links erscheinen im Backend-Log (RESEND_API_KEY noch nicht konfiguriert)
- Invite-Links erscheinen ebenfalls im Backend-Log
