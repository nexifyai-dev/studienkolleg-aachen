# Go-live Checklist

## Zweck

Diese Seite bündelt den aktuellen Go-live-Reifegrad der Plattform und übersetzt bestehende Blocker in eine wartbare Operations-Checkliste.

## Aktueller Status

Die Plattform ist funktional weit fortgeschritten, aber noch nicht vollständig produktionsreif. Mehrere technische, rechtliche und betriebliche Punkte müssen vor einem echten Go-live abgeschlossen werden.

## Technische Go-live-Punkte

### Sicherheit & Session

- [ ] `COOKIE_SECURE=true` in Produktion setzen
- [ ] HTTPS/TLS für Produktionsumgebung verbindlich sicherstellen
- [ ] produktionsfähigen `JWT_SECRET` verwenden
- [ ] initialen Admin-Zugang nach Erstbetrieb rotieren oder absichern

### E-Mail

- [ ] `RESEND_API_KEY` setzen
- [ ] verifizierte Absender-Domain konfigurieren
- [ ] Willkommens- und Bewerbungs-E-Mails end-to-end testen
- [ ] Reply-To und Absenderadressen fachlich verifizieren

### Storage / Dokumente

- [ ] Storage-Strategie für Produktion festlegen (`local`, `s3`, `minio`)
- [ ] falls S3/MinIO: Credentials und Bucket konfigurieren
- [ ] Datei-Uploads mit echten Binärdateien testen
- [ ] Download-/Presign-Flows validieren
- [ ] Aufbewahrung und Recovery-Konzept für Dokumente definieren

### Datenbank & Betrieb

- [ ] MongoDB-Backup-Routine einrichten
- [ ] Restore-Prozess dokumentieren und testen
- [ ] Monitoring-/Logging-Mindeststandard definieren
- [ ] Seed-/Bootstrap-Verhalten für Produktionsbetrieb prüfen

## Recht / Compliance

- [ ] Impressumsdaten final verifizieren
- [ ] vollständiges Impressum einpflegen
- [ ] Datenschutzerklärung juristisch finalisieren
- [ ] AGB juristisch finalisieren
- [ ] Preisangaben konsistent und verifiziert machen

## Operativer Go-live

- [ ] mindestens einen produktionsnahen Staff-Account anlegen und testen
- [ ] externe Testbewerbung vollständig durchlaufen
- [ ] Bewerberkommunikation inkl. E-Mail testen
- [ ] Portal-, Staff- und Admin-Grundflüsse smoke-testen
- [ ] Rollen- und Sichtbarkeitsgrenzen mit Testnutzern validieren

## Produktionsreif vs. vorbereitet

### Bereits tragfähig

Folgende Bereiche sind grundsätzlich vorhanden und bilden das funktionale Fundament:

- Authentifizierung mit Login / Logout / Refresh / Register / Reset
- RBAC-Grundstruktur
- Applicant Isolation
- Audit Logging
- Lead Ingest
- Application Pipeline
- Document Metadata
- Task Management
- Messaging
- i18n
- modularer Backend-Zuschnitt

### Vorhanden, aber konfigurationsabhängig

- E-Mail-Delivery
- binäre Datei-Uploads
- S3/MinIO Storage
- AI-Screening
- Secure Cookies in echter Produktionsumgebung

### Vor echtem Go-live nicht ignorierbar

- Rechtstexte
- Preislogik / Preiswahrheit
- Backup- und Restore-Prozess
- produktive Infrastrukturhärtung

## Empfohlene Reihenfolge

### Phase 1 – Infrastruktur und Sicherheit
1. HTTPS / TLS
2. `COOKIE_SECURE`
3. `JWT_SECRET`
4. Admin-Rotation
5. Backup-Routine

### Phase 2 – Kommunikation und Dokumente
1. Resend / Domain
2. E-Mail-End-to-End-Test
3. Storage-Backend
4. Upload-/Download-Test

### Phase 3 – Recht und Betriebsfreigabe
1. Impressum
2. Datenschutz
3. AGB
4. Preisprüfung
5. finaler Prozess-Test

## Definition of Done für echten Go-live

Ein echter Go-live ist erst dann erreicht, wenn:

- Produktion über HTTPS läuft
- Secure Cookies aktiv sind
- Secrets produktionsreif gesetzt sind
- E-Mail- und Dokumentenprozesse getestet sind
- rechtliche Pflichtseiten final sind
- Backup und Restore nachweislich funktionieren
- ein kompletter Bewerbungsdurchlauf erfolgreich getestet wurde

## Pflegehinweis

Diese Seite ist eine operative Checkliste. Sie sollte bei jeder Änderung an Infrastruktur, Security, E-Mail, Storage, Preislogik oder Rechtstexten überprüft werden.
