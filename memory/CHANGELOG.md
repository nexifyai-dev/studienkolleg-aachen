# CHANGELOG

## 2026-07-02 – v1.4.3: KI-Migration auf DeepSeek Direct API + Chat-Fix
- Support-Chat ("W2G Assistent / Studienberatung") repariert: OpenRouter-Aufrufe schlugen fehl → komplette KI auf DeepSeek Direct API (https://api.deepseek.com, model `deepseek-chat`, AsyncOpenAI-Client) migriert
- Neuer `DEEPSEEK_API_KEY` in backend/.env hinterlegt (vom User bereitgestellt)
- Betroffen: `services/openrouter_provider.py` (komplett neu), `services/brain_memory.py`, `routers/system.py` (ai_provider=deepseek, storage_active inkl. emergent), `services/email_brain.py`
- Vision-KI (Dokumentenanalyse) bleibt auf NSCALE (DeepSeek hat keine Vision)
- E2E getestet: iteration_109.json — 13/13 Backend PASS, Chat-Widget liefert echte Antworten, Admin-Regression grün

## 2026-05-12 – v1.4.2: Demo-Daten-Restore-Endpunkt
- Neuer Admin-Endpunkt `POST /api/system/seed-demo-data`: legt 12 realistische Demo-Bewerber (Libanon, Türkei, Marokko, China, Vietnam, Iran, Indien, Kolumbien, Russland, Nigeria, Irak, Ägypten) verteilt über 7 Pipeline-Stadien + 5 Staff-Tasks an
- Idempotent: bestehende Demo-E-Mails werden aktualisiert statt dupliziert
- UI-Buttons in `/admin/settings` ("Demo-Daten wiederherstellen" + "Alle operativen Daten löschen")
- Lokal getestet: 11 neue Bewerber + 1 Update + 5 Tasks in einem Klick

## 2026-05-12 – v1.4.1: Storage-Default auf Emergent (Production-Hotfix)
- `STORAGE_BACKEND` Default in `/app/backend/config.py` von `local` auf `emergent` umgestellt
- Damit funktioniert persistenter Object-Storage in Production OHNE manuelle Env-Var
- `get_storage_backend()` mit Schutz-Fallback: warnt + loggt Fehler bei fehlendem `EMERGENT_LLM_KEY`
- Behebt finalen Live-Bug: "Datei im Speicher nicht gefunden" für neu hochgeladene PDFs

## 2026-04-06 – v1.4.0: Production-Readiness Sprint

### Security Headers Middleware
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy: camera=(), microphone=(), geolocation=()
- Strict-Transport-Security: max-age=31536000 (bei HTTPS)
- Testing: iteration_83, alle 6 Headers verifiziert

### DSGVO-Endpunkte
- GET /api/system/gdpr/user-data/{id}: Vollstaendiger Datenexport (7 Kategorien)
- POST /api/system/gdpr/anonymize/{id}: Nutzer-Anonymisierung mit Admin-Schutz
- Rechnungsdaten bleiben (Aufbewahrungspflicht), Namen werden anonymisiert

### Admin-Settings & Screening-Regeln
- GET/PUT /api/system/settings: Systemweite Einstellungen
- Admin-Rules-Seite: 8 konfigurierbare Screening-Regeln + Custom Rules
- Audit-Logging bei jeder Settings-Aenderung

### Frontend: Alle Stubs zu funktionalen Seiten
- TeacherStudentsPage: Studenten-Liste mit Suche, Status, Navigation (99 LOC)
- TeacherStudentDetailPage: Vollstaendiges Studentenprofil (111 LOC)
- AdminRulesPage: Screening-Regeln mit Toggles, Selects, Custom Rules (166 LOC)
- StaffReportingPage: KPI-Cards, Pipeline-Chart, CSV-Export (132 LOC)
- PartnerTrackingPage: Performance-Dashboard mit Monatsuebersicht (104 LOC)
- PartnerSettingsPage: Profil + Passwort-Aenderung (107 LOC)
- PartnerLinkPage: Empfehlungslink mit Copy-Button (62 LOC)
- PartnerMessagesPage: 3-Spalten-Messaging (118 LOC)

### Business Logic
- Stage-Effects-Engine (Auto-Tasks, Auto-Close)
- Payment → Stage-Advance
- Document-Rejection → Applicant-Notification
- Duplicate-Merge Endpoint
- 3-stufiges Mahnwesen (Scheduler)
- State Machine (10 Stages)
- Rate-Limiting pro Endpunkt

### Testing: 92 Tests, 100% Pass Rate
- iteration_81: 11/11 (State Machine + Rate-Limiting)
- iteration_82: 11/11 (Stage Effects + Merge)
- iteration_83: 21/21 (Security + GDPR + alle Pages)

## 2026-04-05 – Systemanalyse A-L
- 739-Zeilen-Report, 27 Gaps identifiziert

## 2026-04-04 – v1.3.0: RustFS S3 + Stripe + Batch-Screening

## 2026-04-02 – Visual Root-Cause-Rebuild


## 2026-07-02 — DeepSeek-Migration, Frontend-CSS-Fixes, Kundenfall-Tests
- KI komplett von OpenRouter auf direkte DeepSeek-API migriert (services/openrouter_provider.py = DeepSeek-Gateway via AsyncOpenAI, base_url https://api.deepseek.com, Modell deepseek-chat, Key DEEPSEEK_API_KEY in backend/.env). brain_memory.py, system.py (Integrations-Status ai_provider=deepseek, storage_active inkl. emergent) angepasst.
- Support-Chat (W2G Assistent) Bug behoben: lieferte vorher Fehler, jetzt DeepSeek-Antworten (public, applicant, staff, multi-turn getestet).
- Frontend: 36 Dateien gefixt — ungültige Tailwind-Klassen (bg-white/8, border-white/6 und ALLE [var(--color-X)]/N Opacity-Modifier erzeugten kein CSS) ersetzt durch gültige Stufen bzw. [rgba(...)]-Arbitrary-Values. Weißer Suchbalken auf /knowledge behoben.
- Tests: iteration_109 (DeepSeek-Migration 13/13 PASS), iteration_110 (Finale Abnahme: 30/30 Backend, 24 Seiten frontend fehlerfrei, Apply/Booking/Docs/Analytics/Email/Stripe/CSRF grün).
- 5 echte Kundenfälle (Google Drive) als Testdaten nach /app/testdata geladen und E2E durchgespielt: Lead-Ingest -> 18/18 Dokument-Uploads (Emergent Storage) -> 5/5 KI-Screenings via DeepSeek. KI erkannte korrekt fehlende HZB, Dokumenttyp-Abweichungen und sogar ein APS-Zertifikat einer falschen Person (Fall 3). Testbewerbungen fall1-5.test@stk-aachen.de in DB (source=e2e_case_test).


## 2026-07-02 (2) — P0-Bugfixes + Admin-Portal Paket 2
- BUG: Admin-Fälle nicht öffenbar → /admin/cases Zeilen klickbar, neue Route /admin/cases/:id (ApplicantDetailPage, kontextabhängiger Back-Link).
- BUG: Partner-Verwaltung read-only → komplettes Management: GET /api/admin/partners/overview (Referral-/Provisions-Stats), Edit (PUT /users/{id}), Aktiv-Toggle, Passwort-Reset (jetzt auch für affiliate), Partner-Einladung (invite role=affiliate).
- BUG: Messaging langsam/unzuverlässig → Root Cause: synchrone SMTP/IMAP-Calls blockierten die Event-Loop. 9 Stellen mit asyncio.to_thread entblockt (messaging send/sync-imap/send-email, auth invite/forgot-password, applications send-email, automation, dunning, job_handlers). Portal-Send jetzt <2s, IMAP-Sync non-blocking.
- NEU Paket 2: Bulk-Aktionen (POST /api/applications/bulk-update: set_stage/assign_staff/set_priority/archive, max 100 IDs, Activity-Log), Stage-Filter + CSV-Export auf /admin/cases, Nachrichten-Audit /admin/messages (read-only, Kanal-Filter), Dokumenten-Compliance /admin/documents (GET /api/admin/documents/compliance mit fehlenden Pflicht-Docs je Fall), AdminLayout-Nav erweitert (Nachrichten, Dokumente, Staff-Ansicht-Link).
- Tests: iteration_111.json — Backend 17/17 PASS, Frontend alle Flows PASS (inkl. RBAC 403-Checks, Regression Staff-Kanban/Messaging/Auth).
