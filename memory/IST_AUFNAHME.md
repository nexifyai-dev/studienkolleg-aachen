# W2G Plattform – Vollstaendige IST-Aufnahme
## Datum: 04.04.2026 | Version: 1.0

---

## 1. SYSTEM-GESUNDHEIT

| Komponente | Status | Details |
|------------|--------|---------|
| Frontend (React) | OK | Kompiliert ohne Fehler/Warnungen |
| Backend (FastAPI) | OK | v1.2.0, Startup clean |
| MongoDB | OK | 20 Collections, 128 Docs gesamt |
| Auth (Cookie-basiert) | OK | Alle 5 Rollen loginbar |
| Worker (Background) | OK | Laeuft als Hintergrundprozess |
| SMTP/IMAP (Strato) | KONFIGURIERT | info@stk-aachen.de |

---

## 2. FRONTEND-ROUTEN (28 Routen)

### Public Pages (12) – ALLE 200 OK
| Route | Seite | Elite-Design | i18n DE/EN | Mobile |
|-------|-------|-------------|-----------|--------|
| / | HomePage | JA | JA | JA |
| /courses | CoursesPage | JA | JA | JA |
| /services | ServicesPage | JA | JA | JA |
| /contact | ContactPage | JA | JA | JA |
| /knowledge | KnowledgeCenterPage | JA | JA | JA |
| /booking | BookingPage | JA | JA | JA |
| /legal | LegalPage (Impressum) | JA | JA | JA |
| /agb | LegalPage (AGB) | JA | JA | JA |
| /privacy | LegalPage (Datenschutz) | JA | JA | JA |
| /apply | ApplicantOnboarding | STANDARD | TEILS | TEILS |
| /auth/login | LoginPage | JA | JA | JA |
| /auth/forgot-password | ForgotPasswordPage | JA | JA | JA |

### Portal Pages (16+)
| Portal | Routen | Design | Status |
|--------|--------|--------|--------|
| Staff (/staff/*) | Dashboard, Applicants, Detail, Reports, Invoices, Knowledge, Tasks | Token-System | FUNKTIONAL |
| Admin (/admin/*) | Knowledge, Users | Token-System | FUNKTIONAL |
| Portal (/portal/*) | Dashboard, Application, Docs, Messages, Invoices, Schedule | Token-System | FUNKTIONAL |
| Teacher (/teacher/*) | Dashboard, Courses, Students, Grades, Attendance, Reports | Token-System | FUNKTIONAL |
| Partner (/partner/*) | Dashboard, Tracking, Billing | Token-System | FUNKTIONAL |

---

## 3. API-ENDPUNKTE (E2E-Pruefung)

### Auth (Cookie-basiert, NICHT Bearer-Token)
| Endpunkt | Status | Anmerkung |
|----------|--------|-----------|
| POST /api/auth/login | 200 | Setzt Session-Cookie |
| POST /api/auth/register | 200 | Fuer Bewerber-Onboarding |
| POST /api/auth/forgot-password | - | Strato SMTP |
| GET /api/auth/me | 200 | Cookie-auth |

### Kern-APIs (alle 200 OK)
| Endpunkt | Response | Anmerkung |
|----------|----------|-----------|
| GET /api/applications | list(12) | Bewerbungen |
| GET /api/invoices | list(5) | Rechnungen |
| GET /api/invoices/{id}/pdf | application/pdf | PDF existiert, aber GEMOCKT |
| GET /api/tasks | list(5) | Aufgaben |
| GET /api/notifications | list(4) | Benachrichtigungen |
| GET /api/conversations | 200 | Messaging |
| GET /api/conversations/support | 200 | Support-Tickets |
| GET /api/audit-logs | 200 | Audit-Trail |
| GET /api/dashboard/stats | 200 | Dashboard-Statistiken |
| GET /api/documents/my | 200 | Benutzer-Dokumente |
| GET /api/anabin/entries | 200 | Anabin-Wissensbasis |
| GET /api/workspaces | 200 | Arbeitsbereiche |
| GET /api/health | 200 | Systemstatus |
| GET /api/appointments/public-slots | 200 | Oeffentliche Termine |
| GET /api/cost-simulator/config | 200 | Kostenrechner-Config |

### Bekannte 404s
| Endpunkt | Grund |
|----------|-------|
| /api/dashboard | Route heisst /api/dashboard/stats |
| /api/users/list | Braucht query-params |

---

## 4. DATENBANK (MongoDB)

| Collection | Docs | Beschreibung |
|------------|------|-------------|
| users | 16 | Alle Benutzerkonten |
| applications | 12 | Bewerbungen |
| invoices | 5 | Rechnungen |
| tasks | 5 | Aufgaben |
| notifications | 4 | Benachrichtigungen |
| conversations | 2 | Messaging-Threads |
| anabin_entries | 80 | Anabin-Wissensbasis |
| appointments | 3 | Termine |
| documents | 0 | Hochgeladene Dokumente |
| workspaces | 4 | Arbeitsbereiche |
| worker_jobs | 0 | Background-Jobs |
| webhook_events | 0 | Webhook-Events |

---

## 5. RESTLUECKEN-ANALYSE

### P0 – Kritische Luecken
| Luecke | Impact | Aufwand |
|--------|--------|---------|
| PDF-Rechnungen sind GEMOCKT (kein echtes ReportLab) | Kein Rechnungsversand moeglich | MITTEL |
| Storage ist lokal (kein S3/Presigned URLs) | Dokumente nicht persistent | HOCH |
| Kein echtes Upload-System (Tus/Uppy) | Keine robusten Datei-Uploads | HOCH |
| /api/dashboard fehlt (nur /stats) | Admin-Dashboard unvollstaendig | NIEDRIG |

### P1 – Funktionale Luecken
| Luecke | Impact | Aufwand |
|--------|--------|---------|
| Messaging-System rudimentaer | Keine SLA, kein Fallbezug | HOCH |
| Rechnungserstellung nur manuell | Kein Workflow aus Fallakte | MITTEL |
| Dokumente haben keinen Review-Workflow | Keine Statusmaschine | HOCH |
| i18n-Mail-Templates fehlen | Bewerber erhalten DE-Mails | MITTEL |
| Bewerbernummern-Logik unvollstaendig | Keine eindeutige Zuordnung | NIEDRIG |

### P2 – Qualitaets-Luecken
| Luecke | Impact | Aufwand |
|--------|--------|---------|
| Keine E2E-Tests vorhanden | Regression-Risiko | MITTEL |
| Keine Input-Validierung (Zod/RHF) | Fehleranfaelligkeit | MITTEL |
| Kein TanStack Table (Listen) | Keine Sortierung/Filterung | MITTEL |
| Kein TanStack Query (Caching) | Unnoetige API-Calls | MITTEL |
| Test-Artefakte in DB (TEST_*) | Unsaubere Daten | NIEDRIG |

### P3 – Nicht gestartet
| Feature | Phase |
|---------|-------|
| Stripe/Payment-Integration | Phase 0 |
| Case Shell (zentrale Fallakte) | Phase 1 |
| Kalender/Teacher-Modul | Phase 5 |
| Reporting & Partner-Provisionen | Phase 6 |
| PWA-Faehigkeit | Backlog |

---

## 6. DESIGN-SYSTEM STATUS

| Aspekt | Status |
|--------|--------|
| CSS-Token-System (index.css) | KOMPLETT |
| Buttons: rounded-full, Gold CTA | UMGESETZT |
| Cards: rounded-[8px], border 8% | UMGESETZT |
| Dark Hero Gradient | UMGESETZT |
| Section Labels (Gold Line + Uppercase) | UMGESETZT |
| Social Icons (Inline SVGs) | UMGESETZT |
| W2G Component Library | NEU ERSTELLT |
| Mobile (375px) Overflow-frei | GETESTET |
| Tablet (768px) korrekt | GETESTET |

---

## 7. ACCOUNTS

| Rolle | E-Mail | Status |
|-------|--------|--------|
| Admin/Superadmin | admin@studienkolleg-aachen.de | OK |
| Staff | staff@studienkolleg-aachen.de | OK |
| Teacher | teacher@studienkolleg-aachen.de | OK |
| Applicant | applicant@studienkolleg-aachen.de | OK |
| Partner | partner@studienkolleg-aachen.de | OK |
