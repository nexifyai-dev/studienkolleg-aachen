# 15_security_privacy_compliance.md

## Sicherheitsanforderungen

### Basis
1. TLS / HTTPS überall
2. HSTS
3. CSP
4. sichere Session-/Auth-Flows
5. keine Secrets in Git
6. Secret Store / CI-Secrets
7. Dependency-Scanning
8. Secret Scanning
9. serverseitige RBAC-/RLS-Prüfung
10. Upload-Schutz mit Typ-/Größenvalidierung

### Erhöhter Standard für dieses Projekt
1. Audit Logs für kritische Aktionen
2. MFA für Admin-/Cloud-/CI-Zugänge
3. Webhook-Signaturprüfung
4. Idempotenzspeicher
5. Storage Signed URLs
6. Backup-/Restore-Konzept
7. Zugriffsprüfungen je Workspace und Dokument
8. sicherer Umgang mit externen LMS-Credentials
9. Penetration-/Security-Review vor produktiver breiter Freigabe

## Datenschutzanforderungen

### Verifiziert
Das System verarbeitet:
- Identitätsdaten,
- Kontakt- und Kommunikationsdaten,
- sensible Dokumente,
- Zahlungsdaten,
- Consent-Daten,
- ggf. visa- und aufenthaltsbezogene Informationen.

### Daraus folgen
1. Datenminimierung
2. Need-to-know-Zugriff
3. Consent-Nachweise
4. Lösch-/Archivkonzept
5. Zugriffsauskunft / Exportfähigkeit
6. Protokollierung kritischer Änderungen
7. Trennung operativer Logs und Audit Logs

## D/A/CH-relevante Pflichtbereiche

1. Impressum
2. Datenschutz
3. AGB
4. Cookie-/Consent-Hinweise
5. Kommunikations- und Tracking-Hinweise
6. saubere Preis- und Refundkommunikation
7. deutschsprachige Validierungen und Formatierung
8. D/A/CH-konforme Datums-/Preisformate

## Compliance-Matrix

| Bereich | Relevanz | Einstufung | Umsetzungsobjekte | Nachweise |
|---|---|---|---|---|
| DSGVO / Datenschutz | sehr hoch | Muss | Consent, Löschkonzept, Rollen, Exporte, Protokollierung | user_consents, policy docs, exports |
| ISO/IEC 27001-orientiert | hoch | Soll/Muss im Kern | Zugriffskontrolle, Logging, Secrets, Incident-Handling | security concept, audit logs |
| ISO/IEC 27701-orientiert | hoch | Soll | Privacy-Prozesse, Minimierung, Nachweise | privacy architecture |
| WCAG / EN 301 549 | hoch | Muss | barrierearme Frontends | QA-Reports |
| ISO 25010 | hoch | Soll | Qualitätseigenschaften | Test- und Reviewartefakte |
| ISO 22301-orientiert | mittel/hoch | Soll | Backup, Wiederanlauf, Incident Readiness | backup/restore docs |

## Risiko-Register

| Risiko | Eintritt | Wirkung | Gegenmaßnahme |
|---|---|---|---|
| RLS-Fehler | mittel | sehr hoch | RLS-Testmatrix, pgTAP/integration tests, code review |
| öffentliche Dokumente | niedrig bei sauberem Setup | sehr hoch | private buckets, signed URLs, storage tests |
| Preis-/Legal-Widersprüche | hoch | hoch | Legal/Commercial SOT vor Veröffentlichung |
| doppelte Webhooks | hoch | hoch | webhook_events + idempotency |
| Teilzahlungen/Chargebacks ungeklärt | mittel | hoch | ledger model, fachliche Klärung |
| WhatsApp-Kosten eskalieren | mittel | mittel | budget caps, channel policy |
| Scope-Explosion | hoch | hoch | MVP-Gates, Release-Plan |
| personenbezogene Fallbeispiele geraten in Content | mittel | hoch | strikter Freigabeprozess, keine Rohdatenreuse |

## Nachweisdokumente

1. Architekturübersicht
2. ERD / Datenmodell
3. RLS-Matrix
4. Security-Konzept
5. Consent-Modell
6. Audit-Log-Design
7. Backup-/Restore-Konzept
8. Incident-/Rollback-Plan
9. Testberichte
10. Freigabelog

## Offene Rechtsfragen

1. finale Gebühren- und Refundlogik,
2. Steuer- und VAT-Behandlung,
3. Abgrenzung Admission / FSP / Uni-Zulassung in öffentlichen Texten,
4. Rechtslage digitaler Signaturen / Erklärungen für bestimmte Fälle,
5. Speicherdauer und Löschfristen für Archivfälle,
6. Reichweite von WhatsApp-/Messenger-Kommunikation und Opt-ins.

## Pflichtprüfungen vor Go-Live

### Gate Legal
- Impressum, Datenschutz, AGB konsistent
- Kontakt- und Unternehmensangaben konsistent
- Preisangaben konsistent
- Refund-/Cancellation-Texte freigegeben
- Claim-Review abgeschlossen

### Gate Security
- MFA aktiv
- Secrets sauber
- RLS Tests grün
- Storage Policies getestet
- webhook signature validation aktiv
- audit_logs aktiv

### Gate Privacy
- user_consents aktiv
- Exporte/Auskunft möglich
- Lösch-/Archivlogik dokumentiert
- Tracking-Daten pseudonymisiert

### Gate Operations
- Backups laufen
- Restore-Test erfolgreich
- Monitoring/Alerts aktiv
- Incident-Owner benannt

## Sicherheitsentscheidungen

### Verifiziert
- Projekt braucht erhöhten Standard.
- Auditierbarkeit ist Pflicht.
- Dokumente dürfen nie öffentlich sein.

### Plausibel abgeleitet
- Ohne RLS-Tests kein Start.
- Payment-/Finance-Rollout erst nach Commercial/Tax-Freigabe.
- Appendix/WORM-Archiv kann später folgen; MVP braucht aber belastbare Audit Logs.
