# API Base URL Regression Checks

Ziel: sicherstellen, dass alle Auth-/Lead-Flows sowohl mit leerer als auch gesetzter `REACT_APP_BACKEND_URL` funktionieren.

## Test-Matrix

- **Variante A (leer):** `REACT_APP_BACKEND_URL` nicht gesetzt (oder `''`).
- **Variante B (gesetzt):** `REACT_APP_BACKEND_URL=https://<backend-host>`.

Für beide Varianten dieselben Checks ausführen:

## Setup

```bash
# Variante A
unset REACT_APP_BACKEND_URL
npm run build

# Variante B
REACT_APP_BACKEND_URL=https://example-backend.test npm run build
```

## Regression-Checks (manuell oder per E2E)

1. **Login**
   - Login über `/auth/login` mit gültigen Credentials.
   - Erwartung: POST geht an `/api/auth/login` (A) bzw. `https://<backend-host>/api/auth/login` (B), User landet im passenden Portal.

2. **Token-Refresh nach 401**
   - API-Request provozieren, der `401` liefert (abgelaufene Session).
   - Erwartung: Interceptor ruft `/api/auth/refresh` auf und wiederholt Original-Request einmal.
   - Bei fehlgeschlagenem Refresh: Logout-Call an `/api/auth/logout`, Redirect zu `/auth/login`.

3. **Logout**
   - Logout im UI ausführen.
   - Erwartung: Session wird serverseitig beendet (`/api/auth/logout`), User-Context wird geleert.

4. **Register**
   - Registrierung über `/auth/register` absenden.
   - Erwartung: POST an `/api/auth/register`, anschließend Navigation entsprechend Rolle.

5. **Forgot Password**
   - Formular unter `/auth/forgot-password` absenden.
   - Erwartung: POST an `/api/auth/forgot-password`, Success-State im UI.

6. **Apply Submit**
   - Formular unter `/apply` mit Pflichtfeldern + Pflichtdokumenten absenden.
   - Erwartung: POST an `/api/leads/ingest`, Erfolgsmeldung oder Auto-Login/Weiterleitung bei Account-Erstellung.

## Hinweis zu Download-/Export-Links

Zusätzlich prüfen:
- Portal-Nachrichten: Attachment-Download-Link (`/api/messages/:id/attachment`)
- Staff-Nachrichten: Attachment-Download-Link (`/api/messages/:id/attachment`)
- Staff-Dashboard: CSV-Export (`/api/export/applications`)

Alle Links müssen in Variante A relativ (`/api/...`) und in Variante B absolut (`https://<backend-host>/api/...`) aufgelöst werden.
