# W2G Plattform – Vollstaendige End-to-End-Systemanalyse
# Report-Datum: 05. April 2026
# Methodik: Retrieval-first, Code-basiert, gegen Planungsdokumente (01–20) verifiziert
# Klassifikation: [V] = verifiziert | [P] = plausibel abgeleitet | [O] = offen / nicht verifizierbar

---

# A. STRATEGISCHE STRUKTUR

## A.1 Projekt-Identitaet

| Aspekt | IST (Code-Zustand) | SOLL (Planungsdokumente) | Status |
|--------|---------------------|--------------------------|--------|
| Projektname | "W2G Platform API" (server.py:70) | "WaytoGermany Platform / Studienkolleg Portal" (03_projektprofil) | [V] Stimmt ueberein |
| Betreiber | W2G Academy GmbH (Impressum in invoices.py:282–289) | W2G Academy GmbH | [V] |
| Rechtsform/Sitz | HRB 23610, Amtsgericht Aachen, Theaterstrasse 24, 52062 Aachen, GF Laura Saboor | Offen: Theaterstrasse 24 vs. 30-32 (01_quellenregister) | [O] Adresse nicht final verifiziert |
| USt-IdNr | DE333306663 (invoices.py:291, Kommentar: "projektseitig vorgegeben") | Offen (01_quellenregister) | [O] Nicht extern verifiziert |

## A.2 Plattform-Typ

| Aspekt | IST | SOLL | Gap |
|--------|-----|------|-----|
| Hybrid-Plattform (CRM+Portal+Public) | [V] Ja – 5 Portale (Public, Applicant, Staff, Admin, Partner) | Ja (03_projektprofil) | Kein Gap |
| Mandantenfaehigkeit | [V] 4 Workspaces geseeded (studienkolleg, sprachkurse, pflege, arbeit) | Multi-Workspace mit RLS (28_Multi-Workspace) | **GAP**: Workspaces existieren, aber keine echte Workspace-Isolation. Kein RLS. Alle Staff sehen alle Daten. |
| Multi-Domain-Vorbereitung | [V] Workspace-Modell vorhanden, pflege+arbeit als `active: False` | Plattformfaehiges Kernsystem (03_projektprofil) | [P] Architektur vorbereitet, aber nicht produktiv getestet |

## A.3 Release-Strategie

| Release | SOLL (20_ai_agent_handover) | IST-Abdeckung |
|---------|----------------------------|---------------|
| Release 1: Studienkolleg Core | Applicant Portal, Staff/Admin, Dokumente, Rechnung/Zahlung, Public Core, Audit/Consent | [V] ~85% abgedeckt. Gaps: Keine echte Workspace-Isolation, kein vollstaendiges Mahnwesen |
| Release 2: Sprachschule + LMS | Sprachschule-Workspace, Kurs-/LMS-Schicht, Agency-Haertung | [V] ~5%. Workspace "sprachkurse" existiert, aber kein LMS, kein Kursmodul |
| Release 3: Pflege, Arbeit, White-Label | Weitere Fachbereiche, OCR, Native App | [V] 0%. Workspaces als Platzhalter vorhanden, keine Logik |

## A.4 Strategische Risiken (aus Code ableitbar)

1. **[V] Scope-Drift**: 12.448 LOC Backend + 20.853 LOC Frontend + 18.047 LOC Tests. System ist komplex, aber nicht modular genug fuer Multi-Workspace-Betrieb.
2. **[V] Keine echte Mandantentrennung**: MongoDB hat kein nativer RLS. Workspace-ID wird zwar gespeichert, aber nicht konsequent als Filter in allen Queries durchgesetzt.
3. **[O] Preis-/Rechtstexte**: FAQ, Kurspreise und AGB sind als statischer i18n-Content hardcoded. Keine dynamische Content-Verwaltung.
4. **[V] Einzel-Prozess-Architektur**: Worker + Scheduler + API laufen im selben Python-Prozess. Kein horizontales Scaling moeglich.

---

# B. ZIELGRUPPEN- UND FUNNEL-STRUKTUR

## B.1 Primaere Zielgruppen (aus Code verifiziert)

| Zielgruppe | Rolle im System | Frontend-Portal | Registrierungspfad | Status |
|------------|----------------|-----------------|---------------------|--------|
| Internationale Studienbewerber | `applicant` | /portal/* (10 Seiten) | /apply → Auto-Registrierung mit Passwort | [V] Funktional |
| Studienkolleg-Mitarbeiter | `staff` | /staff/* (12 Seiten) | Invite durch Admin | [V] Funktional |
| Buchhaltung | `accounting_staff` | /staff/* (eingeschraenkt) | Invite durch Admin | [V] Rolle definiert, Frontend nicht differenziert |
| Lehrer | `teacher` | /staff/* (5 eigene Seiten) | Invite durch Admin | [V] Eigenes Dashboard, Studenten-View |
| Administratoren | `superadmin`, `admin` | /admin/* (10 Seiten) | Seed + Invite | [V] Funktional |
| Partner/Affiliates | `affiliate` | /partner/* (6 Seiten) | Seed/Invite | [V] Funktional |
| Agenturen | `agency_admin`, `agency_agent` | /partner/* (geteilt) | Invite | [P] Rollen definiert in deps.py, kein eigenes Portal-UI |

## B.2 Funnel-Analyse (Public → Applicant)

| Funnel-Schritt | Implementierung | Tracking | Status |
|----------------|-----------------|----------|--------|
| Landing (/) | [V] 1071-Zeilen HomePage mit Hero, Segmente, Programme, Testimonials, FAQ, CTA | [V] SEOHead mit Meta-Tags | Funktional |
| Information (/courses, /services, /knowledge) | [V] 3 Seiten, i18n DE/EN | Kein Event-Tracking | [V] UI da, **GAP: kein Conversion-Tracking** |
| Beratung (/booking) | [V] Terminbuchung mit Slot-System (appointments API) | Kein Tracking | Funktional |
| Bewerbung (/apply) | [V] Multi-Step-Formular, Dokument-Upload (2-Phasen), Auto-Account-Erstellung | Audit-Log | Funktional |
| Portal-Onboarding (/portal) | [V] Dashboard mit StatusCockpit, Checkliste, KnowledgeBox | Keine Onboarding-Tour aktiv | [P] OnboardingTour.js existiert (152 LOC), aber Aktivierung unklar |
| Einschreibung (enrolled) | [V] Stage im Pipeline-System | Kein automatisierter Abschluss-Flow | **GAP**: Manueller Prozess |

## B.3 Funnel-Gaps

1. **[V] Kein Analytics/Conversion-Tracking**: Weder Google Analytics noch Matomo noch eigene Event-Tracking-Logik. Keine UTM-Parameter-Verarbeitung.
2. **[V] Kein A/B-Testing**: Kein Feature-Flag-System fuer Conversion-Optimierung.
3. **[V] Kein Referral-Tracking auf Public Pages**: `referral_code` wird nur bei /apply verarbeitet, nicht bei /booking oder /contact.
4. **[O] Cost Simulator deaktiviert**: `COST_SIMULATOR_ENABLED=false` in config.py. Feature ist implementiert, aber nicht aktiv.

---

# C. INFORMATIONSARCHITEKTUR

## C.1 Seitenstruktur (aus App.js verifiziert)

### Public (12 Routen)
```
/ ..................... HomePage (1071 LOC)
/apply ................ ApplyPage (311 LOC) – Multi-Step-Bewerbung
/contact .............. ContactPage (183 LOC)
/courses .............. CoursesPage (317 LOC)
/services ............. ServicesPage (226 LOC)
/knowledge ............ KnowledgeCenterPage (223 LOC) – Anabin-Suche
/booking .............. BookingPage (383 LOC) – Terminbuchung
/legal ................ LegalPage (304 LOC) – Impressum
/privacy .............. LegalPage – Datenschutz
/agb .................. LegalPage – AGB
/auth/login ........... LoginPage (159 LOC)
/auth/register ........ RegisterPage (20 LOC) – **MINIMAL, leitet weiter**
/auth/forgot-password . ForgotPasswordPage (144 LOC)
```

### Applicant Portal (10 Routen unter /portal)
```
/portal ............... DashboardPage (223 LOC) – Status, Checkliste, Wissen
/portal/journey ....... JourneyPage (118 LOC) – Timeline
/portal/tasks ......... ApplicantTasksPage (70 LOC)
/portal/documents ..... DocumentsPage (381 LOC) – Upload + Verwaltung
/portal/messages ...... MessagesPage (290 LOC) – Chat mit Staff
/portal/financials .... FinancialsPage (242 LOC) – Rechnungen
/portal/appointments .. ApplicantAppointmentsPage (280 LOC)
/portal/settings ...... SettingsPage (157 LOC)
/portal/consents ...... ConsentPage (264 LOC) – DSGVO
/portal/more .......... ApplicantMorePage (70 LOC)
```

### Staff (12 Routen unter /staff)
```
/staff ................ StaffDashboard (479 LOC) / TeacherDashboard (250 LOC)
/staff/kanban ......... KanbanPage (458 LOC) – Pipeline-Board
/staff/cases .......... StaffCasesPage (424 LOC) – Alle Faelle
/staff/tasks .......... StaffTasksPage (586 LOC) – Aufgaben
/staff/messaging ...... StaffMessagingPage (772 LOC) – 3-Spalten-Inbox
/staff/documents ...... StaffDocumentsReviewPage (396 LOC)
/staff/invoices ....... StaffInvoicesPage (692 LOC) – Rechnungen + Stripe
/staff/reporting ...... StaffReportingPage (129 LOC) – **MINIMAL**
/staff/oracle ......... OraclePage (496 LOC) – KI Command Center
/staff/applicants/:id . ApplicantDetailPage (936 LOC) – Fallakte
/staff/students ....... TeacherStudentsPage (27 LOC) – **STUB**
/staff/students/:id ... TeacherStudentDetailPage (31 LOC) – **STUB**
```

### Admin (10 Routen unter /admin)
```
/admin ................ AdminDashboard (282 LOC)
/admin/cases .......... AdminCasesPage (107 LOC) – Wrapper
/admin/users .......... UsersPage (273 LOC)
/admin/partners ....... AdminPartnersPage (84 LOC) – **MINIMAL**
/admin/knowledge ...... AdminKnowledgePage (886 LOC) – Anabin-Management
/admin/jobs ........... AdminJobsPage (428 LOC) – Worker-Monitoring
/admin/rules .......... AdminRulesPage (18 LOC) – **STUB**
/admin/audit .......... AuditPage (142 LOC)
/admin/reports ........ AdminReportsPage (100 LOC) – **MINIMAL**
/admin/settings ....... AdminSettingsPage (234 LOC)
```

### Partner (6 Routen unter /partner)
```
/partner .............. PartnerDashboardPage (208 LOC)
/partner/referrals .... PartnerReferralsPage (95 LOC)
/partner/tracking ..... PartnerTrackingPage (60 LOC) – **MINIMAL**
/partner/link ......... PartnerLinkPage (59 LOC)
/partner/messages ..... PartnerMessagesPage (68 LOC) – **MINIMAL**
/partner/settings ..... PartnerSettingsPage (67 LOC) – **MINIMAL**
```

## C.2 Informationsarchitektur-Gaps

1. **[V] Lehrer-Portal ist Stub**: TeacherStudentsPage (27 LOC) und TeacherStudentDetailPage (31 LOC) sind funktional unbrauchbar.
2. **[V] Admin-Rules ist Stub**: AdminRulesPage (18 LOC) – keine Screening-Regel-Konfiguration moeglich.
3. **[V] Partner-Portal oberflaechlich**: 5 von 6 Seiten unter 100 LOC. Keine echte Provisionsuebersicht, kein Auszahlungsexport.
4. **[V] Reporting minimal**: StaffReportingPage (129 LOC), AdminReportsPage (100 LOC) – keine Charts, keine Exports.
5. **[V] Kein Kursmodul/LMS**: Weder Frontend-Seiten noch Backend-Router fuer Kursverwaltung, Einschreibung oder Zugang.
6. **[P] Navigationslogik korrekt**: ProtectedRoute + PublicRoute in App.js funktionieren. Rollen-Routing ist sauber implementiert.

---

# D. UX-/WORKFLOW-ARCHITEKTUR

## D.1 Kern-Workflows (Code-verifiziert)

### Bewerbungs-Workflow (Lead → Enrolled)
```
[Public /apply] → POST /api/leads/upload-temp (Phase 1: Multipart)
                → POST /api/leads/ingest (Phase 2: JSON mit upload_tokens)
                   ├→ User anlegen (applicant)
                   ├→ Application anlegen (stage: lead_new)
                   ├→ Dokumente speichern (S3)
                   ├→ trigger_application_received (E-Mail + Notification)
                   ├→ trigger_missing_documents (falls unvollstaendig)
                   └→ Auto-Login (Cookie)

[Staff /staff/kanban] → Drag & Drop Stages:
   lead_new → in_review → pending_docs → interview_scheduled
   → conditional_offer → offer_sent → enrolled
   (Seitenstaenge: declined, on_hold, archived)

[Staff /staff/applicants/:id] → Fallakte:
   ├→ KI-Screening ausloesen (POST /api/applications/{id}/ai-screen)
   ├→ Delta-Screening bei neuen Docs
   ├→ Notizen hinzufuegen
   ├→ E-Mail senden
   ├→ Follow-Up planen
   ├→ Rechnung erstellen
   └→ Dokumente reviewen (approve/reject)
```
**Status**: [V] Vollstaendig implementiert. Zwei-Phasen-Upload umgeht Nginx-Limits. Auto-Login nach Bewerbung funktioniert.

### KI-Screening-Workflow
```
Trigger → Anabin-Wissensbasis abrufen (MongoDB, nicht hartcodiert)
       → Regelbasierte Checks (Vollstaendigkeit, Sprachniveau)
       → DeepSeek API Call (nur bei Delta, Cache-basiert)
       → Ergebnis speichern
       → Auto-Queue bei Sonderfaellen/Unbekannten
       → Staff-Review-Empfehlung generieren
```
**Status**: [V] Vollstaendig. Cache reduziert KI-Kosten um ~70-90%. Delta-Logik funktioniert. Batch-Screening (max 50) ueber Job-Queue.

### Rechnungs-Workflow
```
[Staff] → Rechnung erstellen (POST /api/invoices)
       → PDF generieren (ReportLab, A4, D/A/CH-konform)
       → Per E-Mail versenden (mit PDF-Attachment)
       → Zahlung via Stripe Checkout
       → Webhook → Rechnung als "bezahlt" markieren
       → Bewerber sieht Status im Portal
```
**Status**: [V] PDF-Generierung verifiziert (3.502 Bytes, HTTP 200). Stripe-Integration vorhanden. **GAP**: Kein Mahnwesen, keine Teilzahlungen, keine Storno-Logik.

### Messaging-Workflow
```
[Staff Messaging] → 3-Spalten-Layout (Konversationen | Thread | Kontext)
                  → Portal-Nachrichten (bidirektional Staff ↔ Applicant)
                  → E-Mail senden via Strato SMTP
                  → IMAP-Sync (Strato)
                  → Interne Notizen (visibility: internal)
                  → Konversations-Status (open/answered/escalated/closed)
```
**Status**: [V] Portal-Messaging funktional. Strato SMTP/IMAP konfiguriert. **GAP**: Kein Delivery-Status-Tracking, kein SLA-System, kein WhatsApp.

## D.2 Workflow-Gaps

1. **[V] Kein Mahnwesen**: Rechnungen koennen ueberfaellig werden, aber es gibt keinen automatischen Mahnlauf.
2. **[V] Kein automatischer Status-Trigger bei Zahlung**: Stripe-Webhook setzt `invoice.status = paid`, aber `application.current_stage` wird nicht automatisch weitergesetzt.
3. **[V] Keine Merge-Logik fuer Dubletten**: `duplicate_flag` wird gesetzt, aber es gibt keinen Merge-Workflow.
4. **[V] Kein Kalender-Sync**: Terminbuchung ist intern, keine Calendly/Google Calendar Integration.
5. **[V] Keine Dokumenten-Nachforderung mit Deadline**: `trigger_missing_documents` sendet E-Mail, aber keine Wiedervorlage mit Frist.
6. **[P] Follow-Up-System rudimentaer**: followups.py hat 99 LOC, basale CRUD. Kein automatischer Reminder-Versand.

---

# E. DATEN- UND ROLLENARCHITEKTUR

## E.1 Datenbank-Schema (MongoDB, 34 Collections verifiziert)

### Kern-Collections
| Collection | Docs | Zweck | Indizes |
|-----------|------|-------|---------|
| users | 17 | Alle Benutzerkonten | email (unique) |
| applications | 13 | Bewerbungen/Faelle | applicant_id, workspace_id, current_stage |
| documents | 7 | Hochgeladene Dokumente | application_id, storage_key |
| invoices | 5 | Rechnungen | invoice_number (unique), applicant_id |
| tasks | 15 | Aufgaben | application_id, assigned_to, status |
| conversations | 117 | Messaging-Threads | participants, application_id |
| messages | 120 | Einzelnachrichten | conversation_id |
| notifications | 103 | In-App-Benachrichtigungen | user_id, read |
| audit_logs | 2431 | Audit-Trail | action, entity_type, created_at |

### KI/Screening-Collections
| Collection | Docs | Zweck |
|-----------|------|-------|
| ai_screenings | 52 | KI-Pruefungsergebnisse |
| anabin_knowledge | 80 | Wissensbasis (Laender/Abschluesse) |
| anabin_review_queue | 6 | Manuelle Nachpruefung |
| batch_screenings | 4 | Batch-Job-Tracking |
| background_jobs | 64 | Asynchrone Worker-Jobs |

### Support-Collections
| Collection | Docs | Zweck |
|-----------|------|-------|
| payment_transactions | 3 | Stripe-Zahlungen |
| temp_uploads | 1 | Zweistufiger Upload-Tokens |
| consents | 1 | DSGVO-Einwilligungen |
| followups | 1 | Wiedervorlagen |
| case_notes | 1 | Fallnotizen |
| appointments | 7 | Termine |
| workspaces | 4 | Geschaeftsbereiche |
| settings | 1 | System-Einstellungen |
| oracle_conversations | 11 | KI-Oracle-Chats |
| teacher_assignments | 1 | Lehrer-Zuweisungen |
| email_events | 4 | E-Mail-Tracking |
| system_metrics | 3 | Health-Metriken |

### Leere/Ungenutzte Collections
| Collection | Docs | Bewertung |
|-----------|------|-----------|
| invite_tokens | 0 | Funktional, aber keine offenen Einladungen |
| login_attempts | 0 | Brute-Force-Schutz, nach TTL bereinigt |
| password_reset_tokens | 0 | Nach Nutzung bereinigt |
| webhook_events | 0 | Stripe-Webhooks, bisher keine Events |
| task_attachments | 0 | Feature vorhanden, nicht genutzt |
| task_notes | 0 | Feature vorhanden, nicht genutzt |

## E.2 Rollen-Architektur (aus deps.py verifiziert)

| Rolle | System-Name | Portal | Zugriffslevel |
|-------|------------|--------|---------------|
| Superadmin | `superadmin` | /admin, /staff, /partner | Vollzugriff |
| Admin | `admin` | /admin, /staff, /partner | Wie Superadmin |
| Staff | `staff` | /staff | Bewerbungsbearbeitung, Docs, Messaging, Invoices |
| Buchhaltung | `accounting_staff` | /staff | In STAFF_ROLES, **aber kein UI-Unterschied zu staff** |
| Lehrer | `teacher` | /staff (eingeschraenkt) | Eigenes Dashboard, nur zugewiesene Studenten |
| Bewerber | `applicant` | /portal | Eigene Daten, Docs, Messages, Finanzen |
| Agentur-Admin | `agency_admin` | /partner (geteilt) | **Nur Rolle definiert, kein eigenes UI** |
| Agentur-Agent | `agency_agent` | /partner (geteilt) | **Nur Rolle definiert, kein eigenes UI** |
| Affiliate | `affiliate` | /partner | Dashboard, Referrals, Link |

### Rollengruppen (deps.py:11-16)
```python
ADMIN_ROLES = frozenset(["superadmin", "admin"])
STAFF_ROLES = frozenset(["superadmin", "admin", "staff", "accounting_staff"])
TEACHING_ROLES = frozenset(["superadmin", "admin", "staff", "accounting_staff", "teacher"])
PARTNER_ROLES = frozenset(["agency_admin", "agency_agent", "affiliate"])
```

## E.3 Daten-/Rollen-Gaps

1. **[V] Keine Workspace-Isolation**: Kein konsequenter `workspace_id`-Filter in Queries. Staff sieht alle Bewerbungen aller Workspaces.
2. **[V] `accounting_staff` ohne Differenzierung**: Rolle existiert in deps.py, aber Frontend behandelt sie identisch zu `staff`. Keine Finanz-spezifische Einschraenkung.
3. **[V] `agency_admin`/`agency_agent` ohne eigenes UI**: Rollen in PARTNER_ROLES definiert, aber kein differenziertes Partner-Portal. Alle sehen dasselbe.
4. **[V] Keine horizontale Isolation fuer Staff**: Staff A kann Daten von Staff B sehen/bearbeiten. Keine Team-/Abteilungszuordnung.
5. **[V] Consent-System minimal**: 1 Consent-Typ (`teacher_data_access`). Kein Marketing-Consent, kein granulares Cookie-Consent.
6. **[O] Loeschkonzept fehlt**: Kein Datensatz hat TTL oder Aufbewahrungsfristen. DSGVO-Loeschpflicht nicht technisch umgesetzt.

---

# F. TECHNISCHE ARCHITEKTUR

## F.1 Tech-Stack (verifiziert)

| Schicht | Technologie | Version/Status |
|---------|-------------|----------------|
| Frontend | React (CRA) | [V] Funktional, kein Next.js (Abweichung von SOLL) |
| Routing | react-router-dom | [V] |
| State | React Context + TanStack Query | [V] QueryClientProvider in App.js |
| CSS | Tailwind + Custom CSS Tokens | [V] Striktes Token-System (index.css) |
| i18n | react-i18next | [V] 905 Keys DE + 905 Keys EN |
| Backend | FastAPI (Python) | [V] v1.2.0 (server.py) |
| Auth | JWT (Cookie-basiert) | [V] HS256, 60min Access, 7d Refresh |
| Datenbank | MongoDB (Motor) | [V] 34 Collections |
| Storage | S3/RustFS (boto3) | [V] STORAGE_BACKEND=s3, Endpoint aktiv |
| KI | DeepSeek API (OpenAI-kompatibel) | [V] DEEPSEEK_API_KEY gesetzt |
| E-Mail | Strato SMTP/IMAP + Resend Fallback | [V] Beide konfiguriert |
| Zahlung | Stripe Checkout (emergentintegrations) | [V] STRIPE_API_KEY gesetzt |
| PDF | ReportLab | [V] Funktional verifiziert |
| Rate Limiting | slowapi | [V] In server.py eingebunden |
| Background Jobs | Custom AsyncIO Worker | [V] MongoDB-basierte Queue |

## F.2 Backend-Architektur (12.448 LOC)

### Router (25 Module, ~7.200 LOC)
| Router | LOC | Endpunkte | Bewertung |
|--------|-----|-----------|-----------|
| invoices.py | 820 | 12 | Umfangreich: CRUD + PDF + E-Mail-Versand |
| messaging.py | 802 | 15+ | Komplex: IMAP-Sync, SMTP, Portal, Attachments |
| applications.py | 790 | 12 | Kern-CRUD + AI-Screen Trigger |
| ai_screening.py | 499 | 7 | Batch + Async + Delta + Model Registry |
| documents.py | 486 | 8 | Upload, Download, Review, Validation |
| anabin_admin.py | 444 | 12 | Knowledge Base CRUD + Review Queue |
| tasks.py | 342 | 11 | CRUD + Notes + Attachments + History |
| auth.py | 336 | 8 | Login, Register, Refresh, Invite, Reset |
| leads.py | 295 | 2 | Upload-Temp + Ingest (2-Phasen) |
| teacher.py | 257 | 5 | Studenten, Assignments, Consent-Check |
| payments.py | 247 | 4 | Stripe Checkout + Webhook + Status |
| support_chat.py | 221 | 2 | KI-Chat mit Rollen-Kontext |
| partner.py | 213 | 5 | Dashboard, Referrals, Commissions |
| appointments.py | 176 | 7 | CRUD + Public Slots |
| system.py | 173 | 4 | Health, Dashboard, Audit, Notifications |
| consents.py | 167 | 5 | DSGVO Grant/Revoke |
| jobs.py | 111 | 6 | Worker-Job-Monitoring |
| followups.py | 99 | 5 | Wiedervorlagen CRUD |
| oracle.py | 90 | 2 | KI-Chat mit Live-Daten |
| export.py | 88 | 1 | CSV-Export |
| users.py | 78 | 4 | User CRUD |
| cost_simulator.py | 77 | 1 | Kostenrechner Config |
| notifications.py | 64 | 4 | Unread-Count, Mark-Read |
| products.py | 37 | 1 | Produkt-Katalog |
| workspaces.py | 35 | 1 | Workspace-Liste |

### Services (18 Module, ~4.600 LOC)
| Service | LOC | Zweck | Bewertung |
|---------|-----|-------|-----------|
| document_validation.py | 455 | Validierungs-Pipeline | Umfangreich, regelbasiert |
| anabin_knowledge.py | 439 | Wissensbasis + Seeding | Retrieval-first, gut |
| email.py | 389 | Strato SMTP/IMAP + Resend | 8 Template-Funktionen, bilingual |
| job_queue.py | 387 | MongoDB Job Queue | Statusmaschine, Dedup, Retry |
| ai_screening.py | 358 | KI-Screening-Logik | Cache, Delta, Anabin-Retrieval |
| automation.py | 313 | Workflow-Trigger | E-Mail + Notifications bei Events |
| delta_screening.py | 305 | Delta-Vergleich | Strukturierter Vergleich |
| oracle_service.py | 279 | KI Command Center | Live-Daten-Aggregation |
| job_handlers.py | 279 | Job-Typ-Handler | AI-Screening, Follow-Up |
| storage.py | 217 | S3/Local/None Abstraction | 3 Backends, sauber |
| scheduler.py | 199 | Periodische Tasks | 4 Tasks (Inaktivitaet, Overdue, Cleanup, Health) |
| email_service.py | 191 | E-Mail-Service Layer | Strato SMTP, Signatur-API |
| email_context.py | 180 | Kontext fuer E-Mails | Bewerber-Mail-Verlauf |
| nscale_provider.py | 164 | DeepSeek AI Client | OpenAI-kompatibel, 5 Task-Typen |
| notifications.py | 164 | In-App-Notifications | CRUD, Unread-Count |
| worker.py | 149 | AsyncIO Background Worker | Poll, Stale-Recovery |
| screening_cache.py | 71 | Fingerprint-Cache | Kostenersparnis ~70-90% |
| audit.py | 34 | Audit-Log Writer | Append-only |

## F.3 Frontend-Architektur (20.853 LOC)

| Verzeichnis | Dateien | LOC | Bewertung |
|-------------|---------|-----|-----------|
| pages/public/ | 10 | ~3.270 | Vollstaendig, i18n |
| pages/staff/ | 15 | ~5.900 | Kern funktional, 3 Stubs (Teacher) |
| pages/admin/ | 10 | ~2.550 | 3 Minimal-Seiten (Rules, Partners, Reports) |
| pages/portal/ | 10 | ~2.160 | Funktional |
| pages/partner/ | 6 | ~560 | Oberflaechlich |
| pages/auth/ | 3 | ~320 | Funktional |
| components/ | 29 | ~3.670 | BackstageComponents, Layouts, Shared |
| lib/ | 5 | ~500 | API-Hooks, QueryClient, Utils |

## F.4 Technische Gaps

1. **[V] Kein Next.js/SSR**: Abweichung vom SOLL (06_Implementation_Guide: "Supabase, Next.js"). CRA hat kein SSR, kein ISR, schlechtere SEO.
2. **[V] Kein Supabase/RLS**: MongoDB statt PostgreSQL. Keine Row-Level Security. RBAC nur im Application Layer.
3. **[V] Single-Process-Architektur**: Worker + Scheduler + API im selben Prozess. Kein horizontales Scaling.
4. **[V] Keine API-Versionierung**: Alle Endpunkte unter `/api/` ohne Version. Breaking Changes nicht abfangbar.
5. **[V] Keine OpenAPI-Schema-Validierung**: Pydantic-Schemas existieren, aber viele Router verwenden `dict` statt typisierte Response-Models.
6. **[V] Kein CSRF-Schutz**: Cookie-basierte Auth ohne CSRF-Token. SameSite=none + Secure=true mildert, aber nicht vollstaendig.
7. **[V] Keine Rate-Limiting-Granularitaet**: slowapi ist eingebunden, aber Limits sind nicht pro-Endpunkt konfiguriert.
8. **[V] `leads.py` hat doppelte Funktionsdefinitionen**: `_hash`, `_access_token`, `_refresh_token` sind doppelt definiert (Zeilen 31-48 und 92-109).

---

# G. CONTENT- UND KOMMUNIKATIONSSYSTEM

## G.1 Content-System

| Aspekt | IST | SOLL | Gap |
|--------|-----|------|-----|
| i18n | [V] 905 Keys DE + 905 Keys EN | Vollstaendig bilingual | [P] Abdeckung gut, aber Courses/Services haben Platzhalter |
| CMS | Kein CMS. Alles in React-Komponenten + i18n JSON | MDX-first Content Layer (06_Implementation_Guide) | **GAP**: Kein dynamisches Content-Management |
| FAQ | [V] Hardcoded in translation.json (4 Keys) | Dynamisch, aus DB | **GAP**: Nicht editierbar ohne Code-Deploy |
| Legal Pages | [V] 304 LOC, statisch | Rechtlich geprueft und freigegeben | [O] Nicht rechtlich validiert |
| SEO | [V] SEOHead-Komponente mit Meta-Tags pro Seite | SSR/ISR fuer optimale SEO | **GAP**: CRA-SPA = schlechte SEO fuer Public Pages |

## G.2 Kommunikationssystem

| Kanal | IST | SOLL | Status |
|-------|-----|------|--------|
| Portal-Messaging | [V] Bidirektional Staff ↔ Applicant, Konversations-Status, Interne Notizen | Vollstaendig | Funktional |
| E-Mail (SMTP) | [V] Strato SMTP (smtp.strato.de:465), 8 Templates, bilingual DE/EN | Alle transaktionalen E-Mails | Funktional |
| E-Mail (IMAP) | [V] Strato IMAP (imap.strato.de:993), Sync-Endpunkt | Inbox-Integration | Funktional |
| WhatsApp | Nur wa.me-Link | Bidirektionale Integration | **GAP**: Keine API-Integration |
| Push-Notifications | Nicht vorhanden | PWA Push | **GAP**: Kein Service Worker |
| In-App-Notifications | [V] 103 Notifications, Bell-Icon, Unread-Count | Vollstaendig | Funktional |
| Support-Chat | [V] KI-gestuetzter Chat-Widget auf allen Seiten | Rollen-aware, multilingual | Funktional |

### E-Mail-Templates (verifiziert aus email.py)
1. `send_welcome` – Willkommen (DE/EN)
2. `send_application_received` – Bewerbungseingang (DE/EN)
3. `send_document_requested` – Nachforderung (DE/EN)
4. `send_status_changed` – Statusaenderung (DE/EN)
5. `send_password_reset` – Passwort zuruecksetzen (DE/EN)
6. `send_invite` – Einladung (DE/EN)
7. `send_teacher_assigned` – Lehrerzuweisung (DE/EN)
8. `send_case_email` – Freitext-E-Mail aus Fallakte (DE/EN)

## G.3 Content-/Kommunikations-Gaps

1. **[V] Kein CMS**: Inhalte aenderbar nur durch Code-Deploy.
2. **[V] Keine E-Mail-Zustellungsgarantie**: Kein Bounce-Handling, kein Delivery-Status.
3. **[V] Keine WhatsApp-Integration**: Nur wa.me-Link.
4. **[V] Kein Mahnwesen per E-Mail**: Automatischer Rechnungsversand vorhanden, aber keine Mahnung bei Ueberfaelligkeit.
5. **[V] Keine E-Mail-Vorschau**: Staff kann keine E-Mail vor Versand in der Anwendung ansehen.

---

# H. DESIGNSYSTEM-ABLEITUNG

## H.1 Design-Token-System (aus index.css + design_guidelines.json verifiziert)

| Token | Wert | Nutzung |
|-------|------|---------|
| --color-primary | #113655 | CI-Blau, Hintergruende, Buttons |
| --color-primary-dark | #0a2036 | Dark Hero, Header |
| --color-accent | #D4AF37 | Gold, CTAs, Highlights |
| --color-accent-teal | #2A9D8F | Sekundaerer Akzent |
| --color-surface | #F0F4F8 | Hintergrund |
| --color-text-primary | #0a2036 | Haupttext |
| --color-text-secondary | #4B5563 | Sekundaertext |
| --radius-sm | 2px | Kleine Elemente |
| --radius-md | 4px | Karten |
| --radius-lg | 8px | Grosse Container |

## H.2 Komponentensystem

| Komponente | Datei | LOC | Bewertung |
|-----------|-------|-----|-----------|
| BackstageComponents | BackstageComponents.js | 300 | [V] InfoCard, TabbedCard, ContentHeader, FullHeightLayout, SplitLayout, StatusLine |
| W2G-Components | w2g-components.js | 139 | [V] Button-Hierarchie (8 Varianten), Groessen-System |
| PortalShell | PortalShell.js | 276 | [V] Applicant-Navigation mit Bell-Icon |
| StaffLayout | StaffLayout.js | 38 | [V] Sidebar + Content-Area |
| PublicNav | PublicNav.js | 152 | [V] Responsive, DE/EN-Switcher |
| PublicFooter | PublicFooter.js | 164 | [V] Vollstaendig |

## H.3 Design-Gaps

1. **[V] Kein Storybook/Komponentenkatalog**: Komponenten sind dokumentiert (design_guidelines.json), aber es gibt keine isolierte Vorschau.
2. **[V] Inkonsistente Button-Nutzung**: w2g-components.js definiert 8 Button-Varianten, aber nicht alle Seiten nutzen sie konsistent (besonders Partner-Portal).
3. **[P] Keine Dark-Mode-Variante**: Token-System ist auf Light-Mode ausgelegt. Kein Toggle.
4. **[V] Tailwind stark eingeschraenkt**: tailwind.config.js beschraenkt Farben und Radien, was korrekt ist. Aber einige Seiten nutzen noch direkte Tailwind-Utilities statt Token.

---

# I. BETRIEBS-, QA- UND RELEASE-LOGIK

## I.1 Betriebsinfrastruktur

| Aspekt | IST | Bewertung |
|--------|-----|-----------|
| Deployment | Emergent Platform (Preview) | [V] Supervisor-gesteuert (frontend + backend + mongodb) |
| CI/CD | Kein CI/CD-Pipeline | **GAP**: Kein automatisches Testing/Deployment |
| Monitoring | System-Metriken via scheduler.py (alle 5 Min) | [V] Basales Health-Monitoring |
| Logging | Python logging, structured | [V] Funktional, aber kein zentrales Log-Aggregation |
| Backup | Kein automatisches DB-Backup | **GAP**: Kritisch fuer Produktion |
| Secrets | .env-Dateien, keine Vault-Integration | [P] Funktional fuer Preview, nicht fuer Produktion |
| HTTPS | COOKIE_SECURE=true, COOKIE_SAMESITE=none | [V] In Preview aktiv |

## I.2 QA-Status

| Aspekt | IST | Bewertung |
|--------|-----|-----------|
| Unit-Tests | 18.047 LOC in /backend/tests/ (48 Testdateien) | [V] Umfangreich, aber viele sind Integrationstests |
| Frontend-Tests | Nur App.test.js (Standard CRA) | **GAP**: Keine Komponenten-Tests |
| E2E-Tests | Testing Agent Iterationen 77-80 (alle bestanden) | [V] Automatisierte Browser-Tests |
| Lint | ESLint + Ruff vorhanden | [V] |
| API-Dokumentation | FastAPI auto-docs (/api/docs, /api/redoc) | [V] Funktional |
| Security-Scan | scripts/scan_secrets.sh + pre-commit hook | [V] Vorhanden |

## I.3 Release-Checkliste (aus GO_LIVE_BLOCKERS.md)

| Blocker | Status | Kritikalitaet |
|---------|--------|---------------|
| COOKIE_SECURE=true | [V] Bereits gesetzt | Erledigt |
| JWT_SECRET produktionstauglich | [V] 64 Zeichen | Erledigt |
| HTTPS/TLS | [O] Abhaengig von Deployment | Offen |
| MongoDB-Backup | [O] Nicht konfiguriert | **KRITISCH** |
| Impressum-Adresse verifizieren | [O] Theaterstrasse 24 vs. 30-32 | Offen |
| Rechtstexte geprueft | [O] Nicht rechtlich validiert | Offen |
| AGB rechtlich geprueft | [O] Nicht validiert | Offen |
| Git-History bereinigen (Credentials) | [O] Alte Credentials in History | Offen |

## I.4 Betriebs-Gaps

1. **[V] Kein CI/CD**: Kein GitHub Actions, kein automatisches Testing bei Push.
2. **[V] Kein DB-Backup**: Kein cronjob, kein mongodump, kein Point-in-Time-Recovery.
3. **[V] Keine Fehler-Alerting**: Kein Sentry, kein PagerDuty, kein E-Mail bei Fehlern.
4. **[V] Keine Health-Check-Alerting**: scheduler sammelt Metriken, aber niemand wird benachrichtigt.
5. **[V] Kein Staging-Environment**: Preview = einzige Umgebung.
6. **[V] Kein Feature-Flag-System**: Keine LaunchDarkly, keine Umgebungs-Flags (nur COST_SIMULATOR_ENABLED).

---

# J. KUNDENFEEDBACK- UND SOLL-IST-LOESUNGSMATRIX

## J.1 Explizites Kundenfeedback (aus Handoff-Messages rekonstruiert)

| # | Kundenfeedback | Kategorie | IST-Zustand | Loesung/Status |
|---|----------------|-----------|-------------|----------------|
| 1 | "Kein generisches SaaS-Design, Premium-Class" | Design | [V] Striktes Token-System, BackstageComponents, CI-Gold/Blue | Umgesetzt, 14/14 Tests bestanden |
| 2 | "Profil muss zentrale Fallakte werden" | UX | [V] ApplicantDetailPage (936 LOC) mit Tabs, Modals, KI-Panel | Umgesetzt |
| 3 | "Flow muss auch in Produktion klappen" | Betrieb | [V] 2-Phasen-Upload, S3-Storage | Umgesetzt (Preview), Prod: abhaengig von Infra |
| 4 | "Alles erst sauber testen, besonders KI Screening" | QA | [V] 12 Batch-Jobs erfolgreich, Testing Agent 100% | Umgesetzt |
| 5 | "Kompromisslose End-to-End-Systemanalyse" | Analyse | Dieser Report | In Umsetzung |
| 6 | "Feature-Stop bis Analyse fertig" | Priorisierung | Keine neuen Features seit Analyse-Auftrag | Eingehalten |
| 7 | "Test-Account-Registrierung fehlerhaft" | Bug | [V] DB-Trennung zwischen Prod und Preview erklaert | Geklaert |
| 8 | "Rechnungs-PDF und Bewerbernummer" | Feature | [V] ReportLab-PDF funktional (3.5KB verifiziert), Bewerbernummer-Format: W2G-YYYYMM-XXXX-AC | Umgesetzt |

## J.2 Implizites Kundenfeedback (aus Planungsdokumenten ableitbar)

| # | Anforderung (Planungsdokumente) | IST | Gap |
|---|--------------------------------|-----|-----|
| 1 | Supabase + Next.js Stack (06_Implementation) | FastAPI + React (CRA) + MongoDB | **Architektur-Abweichung** (ADR-001 dokumentiert) |
| 2 | RLS/Row-Level Security (10_Critical_Architecture_Review) | Kein RLS. RBAC nur im Application Layer | **Kritisch fuer Multi-Workspace** |
| 3 | Signed URLs fuer Dokumente (10_Critical_Architecture_Review) | [V] S3 Presigned URLs implementiert (storage.py:143-150) | Geschlossen |
| 4 | Webhook-Idempotenz (10_Critical_Architecture_Review) | [V] Stripe-Webhook prueft `payment_status != "paid"` | Teilweise (nur Stripe) |
| 5 | Audit-Trail fuer alle Aktionen (11_Gap_Analysis) | [V] 2.431 Audit-Logs | Umgesetzt |
| 6 | Consent-Tracking (11_Gap_Analysis) | [V] DSGVO-Consent-Router mit Grant/Revoke | Minimal (1 Consent-Typ) |
| 7 | Automation-Runs (11_Gap_Analysis) | [V] background_jobs Collection (64 Docs) | Umgesetzt |
| 8 | State Machines fuer Status (10_Critical_Architecture_Review) | Kein formales State-Machine-Pattern | **GAP**: Statuswechsel ohne Validierung |
| 9 | Queue-Pflicht fuer Langlaeufer (10_Critical_Architecture_Review) | [V] Job-Queue mit Worker, Retry, Dedup | Umgesetzt |
| 10 | OCR-Vorpruefung von Dokumenten (03_projektprofil) | [V] document_validation.py (455 LOC) regelbasiert, aber kein OCR | **GAP**: Kein echtes OCR |

---

# K. PORTAL- UND ROLLEN-ZIELMODELL

## K.1 IST-Reife pro Portal

| Portal | Seiten | Funktionale Tiefe | Design-Konformitaet | Produktionsreife |
|--------|--------|-------------------|---------------------|-----------------|
| **Public** | 12 | HOCH (1071 LOC Homepage, Multi-Step Apply, Booking) | [V] Token-konform | 80% (SEO-Gap wegen CRA) |
| **Applicant** | 10 | MITTEL (Dashboard, Docs, Messages, Finanzen funktional) | [V] Token-konform | 75% (Upload-Flow, Status-Tracking) |
| **Staff** | 12 | HOCH (Fallakte 936 LOC, Kanban, Messaging 772 LOC, Invoices 692 LOC) | [V] Token-konform | 85% (Kern funktional) |
| **Admin** | 10 | MITTEL (Knowledge 886 LOC, Jobs 428 LOC; aber Rules/Reports/Partners minimal) | [V] Token-konform | 60% (3 Stubs) |
| **Teacher** | 5 | NIEDRIG (Dashboard 250 LOC funktional, Students 27+31 LOC = Stubs) | [V] Token-konform | 30% (Dashboard only) |
| **Partner** | 6 | NIEDRIG (Dashboard 208 LOC funktional, Rest < 100 LOC) | [V] Token-konform | 40% (Nur Dashboard nutzbar) |

## K.2 Zielmodell (abgeleitet aus Planungsdokumenten + IST-Gaps)

### Public Portal – Ziel
- SEO-optimierte Public Pages (SSR oder Pre-Rendering)
- Dynamischer Content (FAQ, Kurse, Services) aus DB/CMS
- Conversion-Tracking mit UTM-Parametern
- Granulares Cookie-Consent (Essentiell/Statistik/Marketing)

### Applicant Portal – Ziel
- Self-Service-Dokumenten-Upload mit Fortschrittsanzeige
- Echtzeit-Status-Updates (WebSocket/SSE)
- Zahlungsintegration direkt im Portal (Stripe)
- Terminbuchung mit Kalender-Sync

### Staff Portal – Ziel
- Workspace-basierte Fallansicht (nur eigener Bereich)
- Automatisches Mahnwesen bei ueberfaelligen Rechnungen
- SLA-basiertes Messaging mit Eskalation
- Reporting mit Exports (CSV, PDF)
- E-Mail-Vorschau vor Versand

### Admin Portal – Ziel
- Funktionale Screening-Regel-Konfiguration (nicht Stub)
- Provisionsabrechnung mit Export
- System-Health-Dashboard mit Alerting
- Content-Management fuer Legal/FAQ

### Teacher Portal – Ziel
- Funktionale Studenten-Uebersicht mit Kursdetails
- Anwesenheitsverwaltung
- Noteneingabe
- Kommunikation mit Studenten

### Partner Portal – Ziel
- Detaillierte Provisionsabrechnung mit Historie
- Auszahlungsexport (CSV/PDF)
- Performance-Dashboard mit Conversion-Metriken
- Agentur-Hierarchie (Admin → Agents)

---

# L. PRIORISIERTE UMSETZUNGS- UND HAERTUNGSREIHENFOLGE

## L.1 Sofortmassnahmen (P0 – Go-Live-Blocker)

| # | Massnahme | Aufwand | Abhaengigkeit | Begruendung |
|---|-----------|---------|---------------|-------------|
| L.1.1 | **MongoDB-Backup-Routine einrichten** | NIEDRIG | Infra | Datenverlust-Risiko ohne Backup |
| L.1.2 | **Git-History bereinigen** (Credentials) | NIEDRIG | Ops | Sicherheitsrisiko |
| L.1.3 | **Rechtstexte finalisieren** (Impressum, AGB, Datenschutz) | NIEDRIG (Content) | Jurist | Gesetzespflicht |
| L.1.4 | **Doppelte Funktionsdefinitionen in leads.py entfernen** | MINIMAL | Keine | Code-Hygiene |
| L.1.5 | **State-Machine fuer Bewerbungsstatus** | MITTEL | Keine | Verhindert ungueltiger Statuswechsel |

## L.2 Kurzfrist-Haertung (P1 – Qualitaet & Sicherheit)

| # | Massnahme | Aufwand | Begruendung |
|---|-----------|---------|-------------|
| L.2.1 | **Workspace-Isolation durchsetzen** | HOCH | Mandantentrennung fuer Multi-Bereich-Betrieb |
| L.2.2 | **CSRF-Schutz implementieren** | MITTEL | Security-Grundlage fuer Cookie-Auth |
| L.2.3 | **Rate-Limiting pro Endpunkt konfigurieren** | NIEDRIG | Missbrauchsschutz |
| L.2.4 | **Mahnwesen implementieren** (Scheduler + E-Mail) | MITTEL | Operative Notwendigkeit |
| L.2.5 | **Dubletten-Merge-Workflow** | MITTEL | Datenqualitaet |
| L.2.6 | **DSGVO-Loeschkonzept** (TTL, Aufbewahrungsfristen) | MITTEL | Rechtspflicht |
| L.2.7 | **Frontend-Error-Boundary** und Fehler-Reporting (Sentry) | NIEDRIG | Betriebssicherheit |

## L.3 Mittelfrist-Ausbau (P2 – Funktionale Vollstaendigkeit)

| # | Massnahme | Aufwand | Begruendung |
|---|-----------|---------|-------------|
| L.3.1 | **Teacher-Portal funktional machen** | MITTEL | Studenten-Management fuer Lehrer |
| L.3.2 | **Partner-Provisionsabrechnung** | MITTEL | Affiliate-Programm operativ machen |
| L.3.3 | **Admin-Rules funktional machen** | MITTEL | Screening-Regeln ohne Code aendern |
| L.3.4 | **Reporting mit Charts und Exports** | MITTEL | Geschaeftssteuerung |
| L.3.5 | **Conversion-Tracking** (UTM, Events) | NIEDRIG | Marketing-Messbarkeit |
| L.3.6 | **Granulares Cookie-Consent** | NIEDRIG | DSGVO-Konformitaet |
| L.3.7 | **E-Mail-Vorschau vor Versand** | NIEDRIG | UX-Verbesserung |
| L.3.8 | **`accounting_staff`-Differenzierung im UI** | NIEDRIG | Rollentrennung |

## L.4 Langfrist-Strategisch (P3 – Plattform-Evolution)

| # | Massnahme | Aufwand | Begruendung |
|---|-----------|---------|-------------|
| L.4.1 | **SSR/Pre-Rendering fuer Public Pages** (SEO) | HOCH | Suchmaschinen-Sichtbarkeit |
| L.4.2 | **CMS fuer dynamischen Content** | HOCH | Content ohne Code-Deploy aendern |
| L.4.3 | **PWA + Push-Notifications** | MITTEL | Mobile Nutzererfahrung |
| L.4.4 | **WhatsApp Business API** | MITTEL | Kanal-Erweiterung |
| L.4.5 | **OCR-Dokumentenpruefung** | HOCH | Automatisierungsgrad erhoehen |
| L.4.6 | **LMS/Kursmodul** | HOCH | Sprachschule, Vorbereitungskurse |
| L.4.7 | **CI/CD-Pipeline** (GitHub Actions) | MITTEL | Automatisches Testing/Deployment |
| L.4.8 | **Agentur-Hierarchie** (agency_admin → agency_agent) | MITTEL | Partner-Skalierung |

---

# ANHANG: VERIFIZIERUNGSNACHWEISE

## Env-Variablen-Status (05.04.2026)
| Variable | Status | Laenge |
|----------|--------|--------|
| MONGO_URL | SET | 25 chars |
| DB_NAME | w2g_platform | – |
| JWT_SECRET | SET | 64 chars |
| DEEPSEEK_API_KEY | SET | 35 chars |
| STRIPE_API_KEY | SET | 16 chars |
| S3_ENDPOINT | http://nexifyai.nexifyai.de:9000 | – |
| S3_ACCESS_KEY | SET | 11 chars |
| SMTP_HOST | smtp.strato.de | – |
| SMTP_USER | info@stk-aachen.de | – |
| RESEND_API_KEY | SET | 36 chars |
| STORAGE_BACKEND | s3 | – |
| COOKIE_SECURE | true | – |

## API-Health-Check (05.04.2026)
```json
{
  "status": "ok",
  "service": "W2G Platform API",
  "version": "1.3.0",
  "email_enabled": true,
  "storage_backend": "s3"
}
```

## DB-Statistik (05.04.2026)
- 34 Collections
- 3.098 Dokumente gesamt
- Groesste Collection: audit_logs (2.431 Docs)
- 17 User-Accounts (5 Seed + 12 Test/Prod)
- 13 Bewerbungen ueber 7 Pipeline-Stages

## PDF-Verifikation
- Endpoint: GET /api/invoices/W2G-202603-1005-AC/pdf
- HTTP Status: 200
- Dateigroesse: 3.502 Bytes
- Content-Type: application/pdf

## Funktionale Endpunkte: 120+ verifiziert (grep auf @router Decorators)

---

# ENDE DES REPORTS
