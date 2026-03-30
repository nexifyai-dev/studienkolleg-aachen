# Test- und QA-Dokumentation

Stand: 2026-03-30

## Teststrategie
- Stabilitätsorientiert: zuerst Build-/Syntax-/Import-Sicherheit, dann Flow-spezifische Checks.
- Rollen- und Portalregressionen explizit prüfen.

## Automatisiert geprüft
- Backend: `python -m compileall backend`, Pytest-Suites.
- Frontend: `npm run build`, `npm test -- --watchAll=false`.

## Manuell zu prüfen
- Rollenrouting zwischen `/portal`, `/staff`, `/admin`, `/partner`.
- Consent-Auswirkung auf Teacher-Sicht.
- Aufgaben/Messaging UX-Flows inkl. Anhänge/Historie.
- AI-Screening-Ausgabe und Stage-Übernahmefluss.

## Quality Gates
1. Build/Syntax erfolgreich.
2. Keine offensichtlichen RBAC-Regressions.
3. Doku aktualisiert (README + Fachdoku + ggf. ADR + Changelog).
4. Offene Risiken explizit dokumentiert.

## Offene Lücken
- E2E-Testabdeckung für alle Portale noch nicht vollständig zentralisiert.
- Externe Integrationen (Resend, S3/MinIO, TLS) benötigen produktionsnahe Verifikation.

## Rollen-/Portal-spezifische Prüfbereiche
- Applicant: Upload, Consent, Messaging.
- Staff: Kanban, Detail, Tasks, AI-Vorprüfung.
- Teacher: assignment/consent-gated Zugriff.
- Admin: User/Audit.
- Partner: Referral-Dashboard und Link-Logik.

## Definition of Done
Eine Änderung gilt nur dann als done, wenn:
- Code konsistent ist,
- relevante Tests/Checks liefen,
- Dokumentation aktualisiert ist,
- Auswirkungen auf Rollen, Daten und Betrieb nachvollziehbar dokumentiert wurden.
