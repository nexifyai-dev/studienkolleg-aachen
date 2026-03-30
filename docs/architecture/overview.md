# Architekturübersicht

Stand: 2026-03-30

## Architekturprinzipien
- Modulare Domänenrouter im Backend.
- Rollen- und consent-basierte Datenzugriffe.
- Source-of-Truth je fachlichem Bereich.
- Auditierbarkeit durch Logs, ADRs und Changelog.

## Frontend
- React SPA mit zentralem Routing in `frontend/src/App.js`.
- Portale: Public, Applicant, Staff/Teacher, Admin, Partner.
- i18n über `react-i18next` (DE/EN).
- Shared Layout-Komponenten pro Portal.

## Backend
- FastAPI als API-Gateway, Router nach Domänen getrennt (`routers/*`).
- Domain Services (`services/*`) für Audit, Email, Storage, AI.
- Zentrale Abhängigkeits-/RBAC-Prüfung über `deps.py`.

## Datenbank
- MongoDB als primäre Datenhaltung.
- Collections u. a.: users, applications, documents, tasks, task_notes, task_history, messages, ai_screenings, teacher_assignments, audit_logs.

## Auth
- JWT (Access/Refresh) mit Cookie-Transport.
- Rollenprüfung serverseitig via Dependencies.

## Storage
- Abstraktion über Storage-Service.
- Betriebsarten: `local`, `s3`, `minio`.

## Messaging & Notifications
- In-App Messaging pro Bewerbung.
- Notification-Service für Bell/Inbox und E-Mail-Erweiterung.

## Aufgaben
- Task CRUD + Zuweisung + Priorität + Historie + Anhänge + Notizen.
- Rolle und Besitz steuern Bearbeitungsrechte.

## Screening
- Local Rulebook + DeepSeek-Bericht.
- Trennung: completeness, formal_precheck, ai_recommendation, staff_decision.

## Portal-/Rollenstruktur
- Applicant: nur eigene Daten.
- Staff/Admin: operative Bearbeitung.
- Teacher: assignment- und consent-gated Teilmenge.
- Partner: referralspezifische Sicht.

## Hauptdatenflüsse
1. Public Apply → Application + Applicant + initiale Aufgaben/Nachrichten.
2. Applicant Uploads → Document Metadata → Staff Review.
3. Staff Trigger AI → ai_screenings + audit_log.
4. Task-/Message-Aktionen → Historie/Audit.
5. Consent-Update → Teacher-Zugriffsfähigkeit dynamisch.

## Integrationen
- DeepSeek (AI), Resend (Mail), optionale S3/MinIO-Objektspeicherung.

## API-/Modulgrenzen
- Router dürfen Domänenverantwortung nicht überdehnen.
- Providerwechsel nur über Service-Schicht.
- Frontend konsumiert API ausschließlich über zentralen API-Client.

## Source-of-Truth-Prinzipien
- Betriebsparameter: `.env` + `backend/config.py`.
- Rollenlogik: `deps.py` + Rollen-Doku.
- Workflowlogik: Router/Services + `docs/workflows/core-workflows.md`.
