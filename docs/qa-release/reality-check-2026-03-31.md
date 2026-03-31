# Reality Check – Auditbefunde vs. Repo-Stand (31.03.2026)

## Scope und Methode

- Gelesen/abgeglichen: `README.md`, `docs/`, `memory/`, `release/golive_checklist.yaml`, `docs/adr/`, `docs/history/`, `CHANGELOG.md`.
- Audit-kritische Pfade direkt geprüft: `backend/routers/invoices.py`, `backend/services/audit.py`, `backend/config.py`, `storage/messages/`, `test_reports/`.
- Einstufung strikt in:
  1. **verifiziert**
  2. **plausibel abgeleitet**
  3. **offen / nicht verifizierbar**

## Reality-Check-Liste

### Bestätigt (verifiziert)

- **Credentials in `test_reports/` vorhanden:** bestätigt (mehrere Klartext-Passwörter in Iterationsreports).
- **Versionierte Storage-Artefakte unter `storage/messages/`:** bestätigt (binäre Anhänge im Repo).
- **`invoices.py` Audit-Bug:** bestätigt. `write_audit_log(...)` wurde in `invoices.py` mit `db` als erstem Parameter aufgerufen, obwohl Signatur in `services/audit.py` kein `db`-Argument annimmt.
- **Queue-Layer fehlt:** bestätigt (kein Worker-/Queue-Stack oder dokumentierter Async-Job-Layer im Repo).
- **Architekturdrift (Plan vs. Implementierung) nicht als ADR dokumentiert:** bestätigt (nur ADR-0001 vorhanden, keine ADR zur Next/Supabase-vs-FastAPI/Mongo-Abweichung).

### Teilweise behoben (verifiziert)

- **`COOKIE_SECURE` / HTTPS-Härtung:** teilweise. Cookie-Flags werden gesetzt, aber `COOKIE_SECURE` defaultet weiterhin auf `false`; produktive HTTPS-Erzwingung liegt aktuell außerhalb Repo-Defaults.
- **DeepSeek-Produktivkonfiguration:** teilweise. DeepSeek ist als Provider im Code vorhanden, produktive Key-/Betriebsnachweise fehlen.

### Bereits behoben (verifiziert)

- **Master-Credentials in `memory/test_credentials.md`:** aktuell sanitisiert (Platzhalter statt nutzbarer Secrets).

### Offen / nicht verifizierbar

- **Resend Sender-Domain-Verifizierung:** offen (keine externe Provider-Evidenz im Repo).
- **MongoDB-Backup + Restore Drill:** offen (kein ausführbares Backup/Restore-Artefakt im Repo).
- **S3/MinIO produktiver End-to-End-Nachweis:** offen (Codepfade vorhanden, kein belastbarer Betriebsnachweis im Repo).
- **Rechtliche Freigaben (Impressum/Datenschutz/AGB/Preislogik):** offen laut Checkliste, keine juristische Signoff-Evidenz im Repo.

## Definierte P0-Fix-Reihenfolge

1. **P0 Block 1 – Credential-Leaks & Repo-Hygiene**
   - Klartext-Zugangsdaten aus Reports entfernen.
   - Versionierte Storage-Artefakte entfernen + `.gitignore` härten.
   - Leak-Detection von nur Markdown auf alle relevanten textuellen, versionierten Artefakte erweitern.
2. **P0 Block 2 – Audit/Compliance-Kernfix**
   - `write_audit_log`-Bug in Invoice-Write-Pfaden korrigieren.
   - Zieltests ergänzen/aktualisieren.
3. **P0 Block 3 – Security-Hardening**
   - Sichere Cookie-/HTTPS-Defaults und produktive Guardrails repo-seitig härten.
4. **P0 Block 4 – Backup-Minimum**
   - Minimale Backup-/Restore-Strategie als Repo-Artefakt (Script/Runbook/Verifikation).
