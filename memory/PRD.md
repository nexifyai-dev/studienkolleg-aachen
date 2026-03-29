# W2G Platform – PRD / Memory

**Stand:** 29. März 2026 (Update: Phase 3 – AI Screening, Legal, Formular)
**Version:** 1.2.0
**Projekt:** Studienkolleg Aachen / Way2Germany – Mehrmandantenfähige Plattform

---

## Original Problemstellung
Produktionsreife, skalierbare, mehrmandantenfähige Plattform für Studienkolleg Aachen / Way2Germany.
Saubere Trennung: Public Website, Applicant Portal, Staff/Admin-Bereich, Datenmodell, Rollen/Rechte,
Dokumentenlogik, Automationen, Auditfähigkeit, i18n-fähig.

---

## Verbindliche User-Entscheidungen
- **Auth:** JWT Custom Auth (Email + Passwort), kein Google OAuth
- **Sprachen:** Mehrsprachig, Deutsch primär, i18n-Struktur von Beginn an
- **E-Mail:** Resend (RESEND_API_KEY konfiguriert – Domain muss in Resend verifiziert werden)
- **DB:** MongoDB (projektspezifische Abweichung von Supabase-Empfehlung)
- **Design:** #113655 primär, #B3CDE1 akzent, Inter/Arboria, live-site-abgeleitet
- **AI-Screening:** Emergent LLM Key (Claude Sonnet), Ausgabe auf Deutsch
- **Kosten-Simulator:** Nur intern, feature-flagged (COST_SIMULATOR_ENABLED=false)

---

## Neue Kontaktbasis (Feb 2026 – W2G Academy GmbH)
W2G Academy GmbH
Theaterstraße 24
52062 Aachen

Vertreten durch: Geschäftsführerin Laura Saboor
Telefon: +49 (0) 241 990 322 92
E-Mail: info@stk-aachen.de
Handelsregister: Amtsgericht Aachen, HRB 23610

**OFFEN:** Adress-Widerspruch (Theaterstr. 24 vs 30-32 im AGB-Alttext) – vor Go-Live klären
**OFFEN:** E-Mail-Widerspruch (info@stk-aachen.de vs info@cd-stk.com) – vor Go-Live klären

Datenschutzbeauftragter:
Hardtstraße 3, 53474 Bad Neuenahr-Ahrweiler
datenschutzbeauftragter@privatschule-carpediem.de

---

## Architektur (v1.2.0)

### Backend-Struktur
```
/app/backend/
├── server.py           # App Factory only
├── config.py           # All env vars – EMERGENT_LLM_KEY, COST_SIMULATOR_ENABLED neu
├── database.py         # MongoDB client + all indexes
├── deps.py             # get_current_user, require_roles, role groups
├── seed.py             # Idempotent workspace + admin seeding
├── models/
│   └── schemas.py      # Alle Pydantic-Schemas inkl. erweitertem LeadIngest
├── routers/
│   ├── auth.py         # Login, Register (+ Lead-Claiming), Invite, Reset
│   ├── users.py        # User CRUD (field-level access control)
│   ├── workspaces.py   # Workspace management
│   ├── leads.py        # Public lead ingest (PHASE 3: new fields + inline file upload)
│   ├── applications.py # Application CRUD + stage pipeline + automation triggers
│   ├── documents.py    # Upload/Download/Review (storage abstraction)
│   ├── tasks.py        # Task management (ownership-checked updates)
│   ├── messaging.py    # Conversations + Messages (participant-scoped)
│   ├── ai_screening.py # PHASE 3: KI-Prüfung (POST {appId}/ai-screen, GET {appId}/ai-screenings)
│   ├── cost_simulator.py # PHASE 3: Interner Staff-Simulator (feature-flagged, nicht öffentlich)
│   └── system.py       # Audit logs, Dashboard stats, Notifications, Health
├── services/
│   ├── audit.py        # Append-only audit logging (never raises)
│   ├── email.py        # Resend with feature flag (no-op without API key)
│   ├── storage.py      # LocalStorage / S3 / MinIO abstraction
│   ├── ai_screening.py # PHASE 3: run_ai_screening() + lokale Anabin-Checks
│   └── automation.py   # PHASE 3: Workflow-Automationen (received, missing_docs, status_change, reminder)
```

### Frontend-Struktur
```
/app/frontend/src/
├── pages/
│   ├── public/
│   │   ├── HomePage.js      # PHASE 3: echte Assets von studienkollegaachen.de + YouTube
│   │   ├── ApplyPage.js     # PHASE 3: vollständiges Formular + Datei-Upload (3 Pflichtdoks)
│   │   └── LegalPage.js     # PHASE 3: Impressum, AGB (16 §§), Datenschutz – accordion-basiert
│   ├── staff/
│   │   └── ApplicantDetailPage.js  # PHASE 3: AI Screening Panel + erweiterte Bewerberdaten
│   └── ...
├── lib/
│   └── utils.js             # PHASE 3: erweiterte STAGE_LABELS + STAGE_COLORS
```

---

## Datenmodelle (v1.2.0)

### `users` Collection
```json
{id, email, password_hash, full_name, first_name, last_name, phone, country,
 date_of_birth, role, workspace_id, language_pref, active, created_at}
```

### `applications` Collection (erweitert in Phase 3)
```json
{id, applicant_id, workspace_id, current_stage, source,
 course_type, desired_start, combo_option, language_level,
 degree_country, date_of_birth, notes, priority, duplicate_flag,
 referral_code, created_at, last_activity_at}
```

Neue Felder in Phase 3: course_type, desired_start, combo_option, language_level, degree_country, date_of_birth

### `ai_screenings` Collection (NEU in Phase 3)
```json
{screening_id, application_id, screened_at, screened_by, triggered_by,
 local_checks: {completeness, anabin_assessment, language_level_check},
 ai_report, ai_error, suggested_stage, is_complete, missing_documents,
 anabin_category, language_level_ok, decision_note, created_at}
```

### Andere Collections
```
login_attempts, workspaces, documents, tasks, messages, conversations,
audit_logs, notifications, application_activities, password_resets
```

---

## Formular-Pflichtfelder (Phase 3)
- first_name, last_name, email, phone, date_of_birth, country
- course_type: M-Course | T-Course | W-Course | M/T-Course | Language Course
- desired_start: Winter/Summer Semester (5 Optionen)
- combo_option: optional
- language_level: A1 | A2 | B1 | B2 | C1 | C2
- degree_country: Freitextfeld
- notes: optional

Pflicht-Uploads:
- language_certificate (Sprachzertifikat)
- highschool_diploma (Zeugnis)
- passport (Reisepass)

---

## AI-Screening-Logik

### Lokale Checks (immer verfügbar)
1. Vollständigkeitsprüfung: Alle 3 Pflichtdokumente vorhanden?
2. Anabin-Einschätzung: Herkunftsland des Abschlusses → H+, H, D, prüfen
3. Sprachniveau-Check: Ausreichend für gewünschten Kurs?

### Anabin-Kategorien (vereinfacht)
- H+: USA, DE, AT, CH, GB, JP, KR... → volle Anerkennung wahrscheinlich
- H: India, China, Egypt, Turkey... → mit Auflagen
- D: Afghanistan, Syrien, Libyen... → intensive Einzelfallprüfung
- prüfen: Land nicht in Referenzliste → manuell in Anabin-DB prüfen

### LLM-Prüfung (Claude Sonnet via Emergent LLM Key)
- Vollständiger Vorprüfungsbericht auf Deutsch
- 7 Abschnitte: Vollständigkeit, Formale Eignung, Anabin, Kursempfehlung, Risiken, Statusvorschlag, Nächste Aktion
- Fallback: ai_report null bei Budget-Limit (lokale Checks bleiben aktiv)

---

## Workflow-Automationen (Phase 3)

1. **application_received**: Bei neuer Bewerbung → E-Mail an Bewerber + Audit-Log
2. **trigger_missing_documents**: Fehlende Pflichtdoks → Nachforderungs-Mail
3. **trigger_status_change**: Statuswechsel → Bewerber-Mail mit neuem Status
4. **trigger_inactivity_reminder**: Keine Aktivität → Erinnerungs-Mail

Hinweis: Resend-Domain `studienkolleg-aachen.de` muss in Resend-Dashboard verifiziert werden.

---

## Umgebungsvariablen (v1.2.0)

### Backend (.env)
```
MONGO_URL, DB_NAME
JWT_SECRET, COOKIE_SECURE
RESEND_API_KEY=re_XDMFMkFp_... (gesetzt, Domain-Verifikation nötig)
EMERGENT_LLM_KEY=sk-emergent-5500c5dF1Bb9e47958 (gesetzt)
STORAGE_MODE=local|s3|minio|metadata (default: local)
S3_BUCKET, S3_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (wenn S3)
COST_SIMULATOR_ENABLED=false (intern, nicht öffentlich)
```

---

## Was steht noch aus (Backlog)

### P0 – Go-Live-Blocker
- Resend-Domain `studienkolleg-aachen.de` in Resend verifizieren (Emails gehen nicht raus)
- S3/MinIO für Produktions-Dateiablage konfigurieren
- COOKIE_SECURE=true auf HTTPS
- MongoDB-Backup-Routine einrichten
- JWT_SECRET 64+ Zeichen Rotation
- Finale rechtliche Prüfung und Freigabe aller Legal-Texte

### P1 – Offen
- Preislogik / Refund-Regeln final klären und implementieren [OFFEN]
- Payment-Integration (Stripe/Razorpay) nach Preisklärung
- Staff-Kosten-Simulator ausbauen (COST_SIMULATOR_ENABLED=true + echte Preise)
- Agency-Portal (agency_admin / agency_agent Views)
- E-Mail-Domainwiderspruch klären (stk-aachen.de vs cd-stk.com)
- Adresswiderspruch klären (Theaterstr. 24 vs 30-32)

### P2 – Zukünftig
- PWA-Manifest + Mobile-App
- Vollständiges Rechnungsmodul
- CRM-Integration
- Hochschulbewerbungs-Tracking
- SCORM/Lernmodul-Integration

---

## Go-Live-Checkliste
- [ ] Resend-Domain verifiziert
- [ ] S3/MinIO konfiguriert
- [ ] COOKIE_SECURE=true
- [ ] MongoDB-Backup
- [ ] JWT_SECRET rotiert (64+ Zeichen)
- [ ] Alle Legal-Texte rechtlich geprüft und freigegeben
- [ ] Adresse und E-Mail-Kontakt final abgestimmt
- [ ] Preislogik geklärt
- [ ] DSGVO-Cookie-Consent eingebaut

---

## Implementierte Features (Chronologie)

### v1.0.0 – Foundation
- FastAPI Backend + MongoDB + JWT Auth
- React Frontend + Tailwind + React Router + i18next
- App-Shells: Public, Applicant Portal, Staff, Admin
- RBAC-System, Audit Logging, Lead Ingest
- Account-Claiming-Flow, Brute-Force-Schutz

### v1.1.0 – Hardening
- 10 Security-Bugs behoben
- Backend modularisiert (routers/ + services/)
- JWT Refresh Logic im Frontend (Axios-Interceptor)
- Storage-Abstraktion (Local/S3/MinIO/Metadata)
- Resend-Integration mit Feature-Flag
- E-Mail-Templates (Willkommen, Bewerbung, Dokument, Reset, Invite)
- Go-Live-Blocker-Dokumentation

### v1.2.0 – Phase 3 (29. März 2026)
- RESEND_API_KEY und EMERGENT_LLM_KEY in .env konfiguriert
- Legal-Seiten: Impressum, AGB (16 §§), Datenschutz mit W2G-Daten
- Bewerbungsformular vollständig: 12 Felder + 3 Pflicht-Uploads (base64)
- Homepage: echte Assets von studienkollegaachen.de + YouTube-Videos
- KI-Screening: Anabin-Checks, Sprachniveau-Check, Vollständigkeitsprüfung, LLM-Bericht
- Workflow-Automationen: 4 Trigger (received, missing_docs, status_change, reminder)
- Interner Staff-Kosten-Simulator (feature-flagged, nicht öffentlich)
- Erweiterte Stage-Labels + neue STAGE_COLORS in utils.js
- ApplicantDetailPage: AI-Screening-Panel + neue Felder (course, semester, degree_country)
