# Release- und Operations-Dokumentation

Stand: 2026-03-30

## Lokale Entwicklung
- Backend: `uvicorn server:app --reload --port 8001`.
- Frontend: `npm start` (CRA).

## Umgebungslogik
- Local/Preview/Prod über `.env`-Werte gesteuert.
- Sicherheitskritische Werte ohne Code-Fallback (z. B. `JWT_SECRET`, `ADMIN_PASSWORD`).

## Staging / Preview / Production
- Same-Origin-Strategie für Cookies und API-Aufrufe bevorzugt.
- Produktion benötigt HTTPS + `COOKIE_SECURE=true`.

## Release-Status
- Foundation live, aber Go-Live blockiert durch externe/infra-rechtliche Themen.

## Go-Live-Blocker (komprimiert)
- Resend-Domain/API für Mailversand.
- S3/MinIO-Credentials für produktive Uploadstrategie (falls nicht lokal).
- MongoDB Backup/Restore-Routine.
- Rechtstexte (Impressum/Datenschutz/AGB) final.
- TLS/HTTPS-Härtung validiert.

## CI-/Build-/Test-Logik
- Backend: Syntax + Pytest.
- Frontend: Build + Unit/Smoke Tests.
- Doku-Änderungen: Konsistenzcheck gegen PRD/Memory/Code.

## Rollback-Grundsätze
- Jede fachrelevante Änderung muss in Changelog + ADR nachvollziehbar sein.
- Rollback orientiert sich an versionierter Änderungshistorie (Git + Changelog).
- Kritische Konfigänderungen nur mit rückrollbarem Plan.

## Bekannte externe Abhängigkeiten
- DeepSeek API-Verfügbarkeit.
- Resend-Domain/Provider-Status.
- Infrastruktur (TLS, DNS, Object Storage, MongoDB-Hosting).
