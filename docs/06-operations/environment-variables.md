# Environment Variables

## Zweck

Diese Seite dokumentiert die zentralen Umgebungsvariablen des Backends und ihre betriebliche Bedeutung. Sie ersetzt keine Secret-Verwaltung, sondern erklärt Zweck, Wirkung und Risiken.

## Grundprinzipien

- Secrets und produktive Credentials gehören nicht in das Repository.
- Fehlende Pflichtvariablen stoppen den Backend-Start bewusst.
- Feature-Verhalten wird teilweise über Keys und Flags aktiviert.
- Env-Änderungen können direkte Auswirkungen auf Auth, Storage, E-Mail und KI-Verhalten haben.

## Pflichtvariablen

Diese Variablen sind für den Start zwingend erforderlich:

- `MONGO_URL`
- `DB_NAME`
- `JWT_SECRET`
- `ADMIN_PASSWORD`

### Hinweise
- `JWT_SECRET` wird zusätzlich validiert und darf nicht zu kurz sein.
- `ADMIN_EMAIL` hat einen sicheren Default, ist aber kein Secret.

## App- und URL-Konfiguration

### `FRONTEND_URL`
Primäre Frontend-URL, relevant für lokale Entwicklung und Fallback-CORS.

### `APP_URL`
Basis-URL der Anwendung / Backend-Seite, relevant für Links und Systembezüge.

## Security- und Session-Variablen

### `COOKIE_SECURE`
Muss in echter Produktion mit HTTPS auf `true` gesetzt werden.

### `COOKIE_SAMESITE`
Beeinflusst, wie Browser Cookies in Cross-Site-Kontexten behandeln.

### `ACCESS_TOKEN_TTL_MINUTES`
Lebensdauer des Access Tokens.

### `REFRESH_TOKEN_TTL_DAYS`
Lebensdauer des Refresh Tokens.

## Seed- und Bootstrap-Variablen

### `ADMIN_EMAIL`
Seed-Adresse für den initialen Admin.

### `ADMIN_PASSWORD`
Pflichtwert für initialen Admin-Zugang.

### `SEED_DEV_PASSWORD`
Optional. Wenn gesetzt, werden Dev-/Testkonten mit definierter Seed-Logik erzeugt bzw. synchronisiert.

## E-Mail-Konfiguration

### `RESEND_API_KEY`
Aktiviert produktive E-Mail-Funktionalität.

### `EMAIL_FROM`
Absenderadresse.

### `REPLY_TO`
Antwortadresse für E-Mail-Kommunikation.

### `EMAIL_ENABLED`
Abgeleiteter Schalter basierend auf vorhandenem API-Key.

## Storage-Konfiguration

### `STORAGE_BACKEND`
Mögliche Werte:
- `local`
- `s3`
- `minio`

### `LOCAL_STORAGE_PATH`
Dateispeicherort für lokalen Storage.

### `S3_ENDPOINT`
Endpoint für S3- oder MinIO-kompatiblen Objektspeicher.

### `S3_ACCESS_KEY`
Credential für Storage-Zugriff.

### `S3_SECRET_KEY`
Credential für Storage-Zugriff.

### `S3_BUCKET`
Bucket-Name für Dokumente.

### `S3_REGION`
Region für S3-Zugriffe.

### `STORAGE_ENABLED`
Abgeleiteter Schalter, der das verfügbare Storage-Modell widerspiegelt.

## KI- und Feature-Konfiguration

### `NSCALE_API_KEY`
Aktiviert nscale-basierte KI-Funktionalität.

### `AI_SCREENING_ENABLED`
Abgeleiteter Schalter für KI-Screening.

### `EMERGENT_LLM_KEY`
Legacy-Variable aus Übergangscode.

### `COST_SIMULATOR_ENABLED`
Feature Flag für den Cost Simulator.

### `MEM0_API_KEY`
Projektbezogenes Memory-Thema, keine direkte Produktfunktion.

## Betriebsrelevante Folgen von Env-Änderungen

### Security
- Cookie-Verhalten
- HTTPS-Abhängigkeit
- Token-Stabilität
- Auth-Fehler im Browser

### Betrieb
- E-Mail-Delivery
- Dokumenten-Upload
- Storage-Verfügbarkeit
- Seed-Verhalten beim Start

### Produktfunktionalität
- Aktivierung von KI-Screening
- Aktivierung des Cost Simulators
- Sichtbares Verhalten im Portal oder Staff-Bereich

## Änderungsregeln

Diese Seite muss aktualisiert werden, wenn:

- neue Env-Variablen hinzukommen
- Pflichtvariablen sich ändern
- Defaults sich ändern
- neue externe Systeme eingebunden werden
- Feature Flags produktiv relevant werden
- Security- oder Cookie-Verhalten angepasst wird

## Gute Praxis

- Defaults nur für nicht-sensitive Werte
- Secrets nur über sichere Deployment-Mechanismen
- Änderungen an Env immer zusammen mit Ops-/Go-live-Doku prüfen
- neue Variablen zusätzlich im lokalen Setup und in Deploy-Dokumentation vermerken
