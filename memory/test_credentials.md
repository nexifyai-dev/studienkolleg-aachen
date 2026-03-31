# Test Credentials (Sanitized)

> Keine Secrets, Passwörter oder nutzbaren Login-Daten in versionierten Dateien ablegen.
> Verwende für lokale Tests ausschließlich das interne Secret-Management (Vault/Password Manager).

## Rollenübersicht (Platzhalter)

## Admin
- **Login Identifier:** `<superadmin_login_identifier>`
- **Password:** `<from_internal_secret_manager>`
- **Role:** superadmin

## Staff
- **Login Identifier:** `<staff_login_identifier>`
- **Password:** `<from_internal_secret_manager>`
- **Role:** staff

## Teacher
- **Login Identifier:** `<teacher_login_identifier>`
- **Password:** `<from_internal_secret_manager>`
- **Role:** teacher

## Applicant
- **Login Identifier:** `<applicant_login_identifier>`
- **Password:** `<from_internal_secret_manager>`
- **Role:** applicant

## Partner / Affiliate
- **Login Identifier:** `<affiliate_login_identifier>`
- **Password:** `<from_internal_secret_manager>`
- **Role:** affiliate

## Login-Test (Template ohne Credentials)
```bash
API_URL="<environment_specific_api_url>"
USER_IDENTIFIER="<from_internal_secret_manager>"
USER_PASSWORD="<from_internal_secret_manager>"

curl -s -c /tmp/session.cookies -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$USER_IDENTIFIER\",\"password\":\"$USER_PASSWORD\"}"

curl -s -b /tmp/session.cookies "$API_URL/api/auth/me"
```

## Betriebsdoku-Referenz (nicht versioniert)
- Zugriffspfad: `Security Operations / Runbooks / Credential Access (W2G Platform)`
- Enthält: Berechtigungsprozess und Retrieval-Workflow
- Enthält **nicht**: Repository-kopierte Secrets
