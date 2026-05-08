# W2G Platform – Masterplan: End-to-End System-Audit & Priorisierter Umsetzungsplan

**Erstellt:** 2026-04-06
**Version:** 1.0
**Autor:** AI System Auditor / Lead Architect

---

## A. Architekturueberblick

### Backend (FastAPI + MongoDB)
```
/app/backend/
├── server.py              – App-Factory, CORS, Security Headers, Router-Mount
├── config.py              – Env-Config (fails fast)
├── database.py            – MongoDB Client
├── deps.py                – Auth (JWT Cookie), Rollen-Checks, Workspace-Filter
├── seed.py                – Idempotente Seed-Daten (Admin, Staff, etc.)
├── rate_limiter.py        – slowapi Rate-Limiting
├── routers/               – 23 Router-Module (Domaenen-getrennt)
│   ├── auth.py            – Login/Register/Invite/Reset (Brute-Force-Schutz)
│   ├── applications.py    – CRUD + Stage-Aenderung + Notes + Activity (953 Zeilen)
│   ├── documents.py       – Upload/Download/Validate/Revalidate (573 Zeilen)
│   ├── invoices.py        – CRUD + PDF-Gen + E-Mail-Versand (821 Zeilen)
│   ├── tasks.py           – CRUD + Notes + Attachments + History
│   ├── messaging.py       – Conversations + Messages + IMAP-Sync + Attachments
│   ├── leads.py           – Oeffentliche Bewerbung (2-Phasen-Upload)
│   ├── users.py           – Profil-Update
│   ├── payments.py        – Stripe-Integration
│   ├── ai_screening.py    – KI-Vorpruefung
│   ├── system.py          – Dashboard-Stats, Audit, GDPR-Export
│   └── ... (12 weitere)
├── services/              – Business-Logik (getrennt von Routing)
│   ├── ai_screening.py    – Screening-Pipeline
│   ├── document_validation.py – Dokumentenpruefung (Vision + DeepSeek)
│   ├── nscale_provider.py – DeepSeek Text-API
│   ├── nscale_vision_provider.py – Llama-4-Scout Vision-API (NEU)
│   ├── ai_learning.py     – Institutionelles Lernen (NEU)
│   ├── stage_effects.py   – Automatische Tasks bei Stage-Wechsel
│   ├── dunning.py         – Mahnwesen-Scheduler
│   ├── email_service.py   – SMTP/IMAP (Strato)
│   ├── storage.py         – S3/RustFS Abstraktion
│   └── ...
└── models/schemas.py      – Pydantic Request/Response Schemas
```

### Frontend (React + Tailwind + shadcn/ui)
```
/app/frontend/src/
├── App.js                 – Router (BrowserRouter, 4 Layouts)
├── i18n.js                – i18next Setup (de/en)
├── contexts/AuthContext.js – Auth-State, Cookie-basiert
├── lib/
│   ├── apiClient.js       – Axios mit Credentials
│   ├── api-hooks.js       – React Query Hooks
│   └── utils.js           – Stage-Labels, Formatter
├── pages/
│   ├── public/            – 8 Seiten (Home, Apply, Courses, ...)
│   ├── auth/              – Login, Register, ForgotPassword
│   ├── portal/            – 10 Seiten (Bewerber-Portal)
│   ├── staff/             – 15 Seiten (Mitarbeiter-Bereich)
│   ├── admin/             – 10 Seiten (Admin-Bereich)
│   └── partner/           – 6 Seiten (Partner-Bereich)
├── components/
│   ├── layout/            – StaffLayout, ApplicantLayout, etc.
│   └── ui/                – shadcn/ui Komponenten
└── locales/               – de/en Uebersetzungen (je 905 Zeilen)
```

### Rollen-System
| Rolle | Berechtigung | Layout |
|-------|-------------|--------|
| superadmin | Voller Zugriff | AdminLayout |
| admin | Admin ohne System-Config | AdminLayout |
| staff | Fallbearbeitung, Dokumente, Rechnungen | StaffLayout |
| accounting_staff | Rechnungen + lesender Zugriff | StaffLayout |
| teacher | Studenten-Uebersicht | StaffLayout (Teacher) |
| applicant | Eigenes Portal | ApplicantLayout |
| agency_admin | Partner-Dashboard | PartnerLayout |
| agency_agent | Partner-Vermittlung | PartnerLayout |
| affiliate | Partner-Link | PartnerLayout |

### DB-Collections (34 aktiv)
| Collection | Dokumente | Funktion |
|-----------|-----------|----------|
| users | 18 | Alle Benutzer |
| applications | 14 | Bewerbungsfaelle |
| documents | 7 | Dokument-Metadaten |
| invoices | 5 | Rechnungen |
| tasks | 26 | Aufgaben |
| conversations | 134 | Nachrichtenthreads |
| messages | 137 | Einzelnachrichten |
| ai_screenings | 52 | KI-Pruefungen |
| audit_logs | 2572 | Audit-Trail |
| notifications | 132 | Benachrichtigungen |

---

## B. Gap-Analyse gegen Kundenfeedback

### B.1 Sprache & Internationalisierung (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| L1 | System vollstaendig auf Englisch nutzbar | i18next mit de/en (905 Keys). ABER: ~40% der UI-Texte sind hardcoded deutsch (StaffDashboard, ApplicantDetailPage, StaffTasksPage, StaffInvoicesPage, StaffMessagingPage) | Entwickler haben `t()` nicht konsequent genutzt | Alle Staff-/Admin-Seiten | P0 |
| L2 | Bewerber-Kommunikation an Sprachwahl orientieren | `language_pref` in Users gespeichert. E-Mail-Templates nur DE | Email-Service ignoriert language_pref | `services/email_service.py`, `routers/invoices.py` | P0 |
| L3 | Spracheinstellungen nicht zuverlaessig speicherbar | SettingsPage speichert via `PUT /api/users/:id`. Funktioniert technisch. | Kein Bug gefunden – muss im Kontext getestet werden | `routers/users.py`, `pages/portal/SettingsPage.js` | P1 |
| L4 | Rechnungen auf Englisch (ausser DE-Bewerber) | PDF-Generierung komplett DE-only | Kein i18n im PDF-Generator | `routers/invoices.py` (Zeile 252-582) | P0 |

### B.2 Bewerbungsprozess (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| A1 | Bewerbung ueber Website "fehlgeschlagen" | 2-Phasen-Upload via `/api/leads/upload-temp` + `/api/leads/ingest`. Logik existiert | Muss reproduziert werden: evtl. File-Size-Limit, Timeout, S3-Fehler | `routers/leads.py`, `pages/public/ApplyPage.js` | P0 |
| A2 | Bewerbungsverlauf nicht korrekt aktualisiert | `application_activities` Collection trackt Aenderungen | Pipeline-Tracking fehlerhaft? Status-Transition-Logik pruefen | `routers/applications.py` | P0 |
| A3 | Statusaenderungen nicht sauber weitergefuehrt | Stage-Effects-Engine existiert | Edge Cases: Was passiert bei Skip-Stages? | `services/stage_effects.py` | P1 |

### B.3 Dokumentencenter (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| D1 | Upload durch Bewerber fehlerhaft | Upload-Flow existiert (`/api/applications/:id/documents/upload`). Bewerber braucht application_id | Bewerber muss eigene application_id kennen – Frontend-Flow pruefen | `routers/documents.py`, `pages/portal/DocumentsPage.js` | P0 |
| D2 | Dokumente nicht einsehbar | PreviewModal existiert mit iframe/img. Download-Endpunkt `/api/documents/:id/download` | Moeglich: Fehlende Rechte, Storage-Key leer, Binary nicht gespeichert | `routers/documents.py` | P0 |
| D3 | In-Portal-Vorschau ohne Download | PreviewModal nutzt iframe fuer PDFs, img fuer Bilder | Implementiert – Funktionstest noetig | `pages/portal/DocumentsPage.js` (PreviewModal) | P1 |
| D4 | Nachtraegliche Uploads nicht moeglich | Upload-Endpunkt existiert, kein Check auf "nur einmal pro Typ" | Sollte funktionieren – Frontend-Flow testen | `routers/documents.py` | P1 |

### B.4 Dokumentenstatus (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| DS1 | Automatische Sortierung: akzeptiert/abgelehnt/offen | Status-System existiert (uploaded, in_review, approved, rejected) | Frontend zeigt alle in einer Liste – kein Grouping | `pages/portal/DocumentsPage.js` | P1 |
| DS2 | Erneute Pruefung nach Ablehnung | Revalidate-Endpunkt existiert (`POST /api/documents/:id/revalidate`) | Frontend fehlt "Erneut pruefen" Button im Bewerber-Portal | Portal-Seite | P1 |
| DS3 | Erneute Pruefzyklen funktionieren nicht | Backend unterstuetzt Re-Validierung | Frontend-Anbindung fehlt | `pages/portal/DocumentsPage.js` | P1 |

### B.5 Dokumentenverwaltung (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| DV1 | Dokumente loeschen koennen | Delete-Endpunkt existiert (`DELETE /api/documents/:id`) | Frontend hat keinen Loeschen-Button im Bewerber-Portal | `pages/portal/DocumentsPage.js` | P0 |
| DV2 | Falsch hochgeladene Dokumente ersetzen | Replace-Endpunkt existiert (`PUT /api/documents/:id/replace`) | Frontend fehlt Replace-UI | `pages/portal/DocumentsPage.js` | P0 |
| DV3 | Erneuter Upload derselben Kategorie | Kein Backend-Block fuer gleichen Typ | Funktioniert technisch – UI zeigt es evtl. nicht klar an | `pages/portal/DocumentsPage.js` | P1 |

### B.6 Sicherheit (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| S1 | Upload-Virenscanning | Nicht implementiert | Kein AV-Service integriert | `routers/documents.py`, `services/storage.py` | P1 |
| S2 | Security Headers | Implementiert (X-Content-Type-Options, X-Frame-Options, HSTS) | Vorhanden | `server.py` | DONE |

### B.7 Profil als zentrale Steuerung (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| P1 | Profil als zentrale Arbeitsoberflaeche | ApplicantDetailPage (Staff) ist umfangreich. Bewerber-Portal hat separate Seiten | Bewerber-Dashboard ist zu generisch; Staff-Fallakte ist gut | `pages/portal/DashboardPage.js` | P0 |
| P2 | Aktionen direkt im Profil moeglich | Staff: Fallakte hat Inline-Edit, Docs, Tasks. Bewerber: Nur Links | Bewerber-Portal nicht zentralisiert genug | Portal-Seiten | P1 |

### B.8 Rechnungen (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| R1 | Im Profil erstellen/versenden (Modal) | InvoiceCreateModal existiert in der Fallakte | Funktioniert im Staff-Bereich | `components/staff/InvoiceCreateModal.js` | DONE |
| R2 | Versand per E-Mail + Portal | E-Mail-Versand via Resend, Portal-Anzeige via /my | Implementiert – E-Mail-Funktion abhaengig von Resend-Config | `routers/invoices.py` | P1 |
| R3 | Bewerbernummer auf Rechnungen | FEHLT KOMPLETT: Kein `applicant_number` Feld im System | Nie implementiert | Gesamtes System | P0 |
| R4 | Preise anpassbar | InvoiceUpdate erlaubt amount/items Aenderung | Implementiert | `routers/invoices.py` | DONE |
| R5 | Rechnungen korrekt zugeordnet | `applicant_id` vorhanden, `application_id` optional | Implementiert | `routers/invoices.py` | DONE |

### B.9 Inbox / Nachrichten (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| M1 | Inbox dem Bewerber zugeordnet | Conversation hat `application_id` + `participants` | Implementiert | `routers/messaging.py` | DONE |
| M2 | Nachrichtenbereich langsam | Keine Indizes auf `conversation_id`, `sender_id`, `sent_at` | Fehlende DB-Indizes + N+1 Queries | `database.py` | P1 |

### B.10 Aufgaben (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| T1 | Bewerber kann Aufgaben senden | Applicant hat `visibility: public` Filter. Kein Create | TaskCreate erfordert STAFF_ROLES | `routers/tasks.py` | P1 |
| T2 | Filter nach Name/Kunde/Mitarbeiter | Nur `application_id` und `assigned_to` Filter | Fehlende Query-Parameter | `routers/tasks.py` | P1 |
| T3 | Sortierung Faelligkeit (Tag/Woche/Monat) | Sortierung nur nach `created_at` | `due_date` Sortierung fehlt | `routers/tasks.py` | P1 |
| T4 | Priorisierung (wichtig/dringend/ueberfaellig) | priority-Feld existiert (normal/high/urgent) | Frontend zeigt keine Ueberfaellig-Markierung | `pages/staff/StaffTasksPage.js` | P1 |
| T5 | Listen- und Kalenderansicht | Nur Listenansicht | Kalenderansicht fehlt komplett | `pages/staff/StaffTasksPage.js` | P2 |

### B.11 Dashboard (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| DA1 | Zweite Spalte bei Handlungsbedarf nicht sichtbar | Dashboard hat 3 Spalten. Responsive-Verhalten pruefen | CSS-Breakpoint-Problem? | `pages/staff/StaffDashboard.js` | P1 |

### B.12 Performance (P0)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| PF1 | Portal stellenweise langsam | Keine DB-Indizes auf haeufige Queries | MongoDB-Indizes fehlen | `database.py` | P0 |
| PF2 | Portal bleibt im Ladebildschirm haengen | AuthContext `loading` State bleibt evtl. true | Netzwerk-Timeout bei `/api/auth/me` ohne Cookie | `contexts/AuthContext.js` | P0 |

### B.13 Fallliste / Kanban / Uebersicht (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| K1 | Filter erweitern (Bewerber/Mitarbeiter/Agentur) | StaffCasesPage hat Search + Stage-Filter | Fehlende Filter-Felder | `pages/staff/StaffCasesPage.js` | P1 |
| K2 | Gesamtzahl Bewerber sichtbar | Dashboard zeigt Count. Fallliste nicht | Fehlende Anzeige im Header | `pages/staff/StaffCasesPage.js` | P1 |
| K3 | Bewerbernummer vergeben + anzeigen | FEHLT KOMPLETT | Nie implementiert | System-weit | P0 |

### B.14 Reporting / Statistik (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| RE1 | Umsatz gesamt + pro Mitarbeiter | Dashboard hat Invoice-Stats. StaffReportingPage existiert | StaffReportingPage muss erweitert werden | `pages/staff/StaffReportingPage.js` | P1 |
| RE2 | Offene Rechnungen inkl. Betrag | Invoice-Stats-Endpunkt vorhanden | Frontend muss angepasst werden | `pages/staff/StaffReportingPage.js` | P1 |
| RE3 | Zeitraeume (Tag/Woche/Monat/Jahr/frei) | Nicht implementiert | Backend-Filter fehlt | `routers/system.py` | P2 |
| RE4 | Reports mit Diagrammen | recharts ist installiert. Dashboard nutzt es | StaffReportingPage nutzt es nicht | `pages/staff/StaffReportingPage.js` | P2 |

### B.15 Datenschutz / Einwilligung (P1)

| # | Kundenanforderung | Ist-Stand | Root Cause | Betroffene Dateien | Prioritaet |
|---|------------------|-----------|------------|-------------------|------------|
| DS1 | Dateneinwilligung vereinfachen | ConsentPage existiert, CookieBanner vorhanden | Consent im Bewerbungsformular fehlt evtl. | `pages/public/ApplyPage.js` | P1 |

---

## C. Priorisierung P0 / P1 / P2

### P0 – Go-Live-kritisch (sofort)

1. **Bewerbernummer (applicant_number)** – System-weite Einfuehrung
   - Auto-Generierung bei Application-Erstellung
   - Anzeige: Profil, Fallakte, Rechnungen, Fallliste
   - DB: `applications.applicant_number` Feld
   - Dateien: `routers/applications.py`, `routers/invoices.py`, alle Frontend-Seiten

2. **Bewerbungsprozess-Fehler beheben**
   - /api/leads/ingest Flow End-to-End testen
   - File-Upload-Limits pruefen
   - Error-Handling im Frontend verbessern
   - Dateien: `routers/leads.py`, `pages/public/ApplyPage.js`

3. **Dokumenten-Upload fuer Bewerber reparieren**
   - Portal DocumentsPage: Upload-Flow pruefen
   - Loeschen + Ersetzen UI hinzufuegen
   - In-Portal-Vorschau sicherstellen
   - Dateien: `pages/portal/DocumentsPage.js`, `routers/documents.py`

4. **i18n Komplett-Rollout (Staff-UI auf Englisch)**
   - Alle hardcodierten DE-Strings durch `t()` ersetzen
   - EN Uebersetzungen vervollstaendigen
   - Dateien: Alle Staff-/Admin-Seiten

5. **Rechnungen i18n + Bewerbernummer**
   - PDF-Generator: DE/EN basierend auf Bewerber-Sprache
   - Bewerbernummer auf Rechnung drucken
   - Dateien: `routers/invoices.py`

6. **Performance: DB-Indizes + Auth-Loading**
   - MongoDB Compound-Indizes erstellen
   - AuthContext Loading-Timeout einbauen
   - Dateien: `database.py`, `contexts/AuthContext.js`

### P1 – Betriebsrelevant (nach P0)

7. **Aufgaben-Modul erweitern**
   - Filter: Name, Bewerber, Mitarbeiter
   - Sortierung: due_date, Faelligkeit
   - Ueberfaellig-Markierung
   - Bewerber-Aufgaben-Erstellung
   - Dateien: `routers/tasks.py`, `pages/staff/StaffTasksPage.js`

8. **Messaging-Performance**
   - DB-Indizes fuer messages/conversations
   - Pagination
   - Dateien: `routers/messaging.py`, `database.py`

9. **Fallliste/Kanban Filter erweitern**
   - Mitarbeiter-/Agentur-/Bewerbernummer-Filter
   - Gesamtzahl-Anzeige
   - Dateien: `pages/staff/StaffCasesPage.js`

10. **Dokument-Status-Grouping**
    - Frontend: Dokumente nach Status gruppieren
    - Erneut-Pruefen Button im Bewerber-Portal
    - Dateien: `pages/portal/DocumentsPage.js`

11. **Dashboard zweite Spalte**
    - Responsive Layout pruefen
    - Dateien: `pages/staff/StaffDashboard.js`

12. **E-Mail-Kommunikation Sprache**
    - Templates DE/EN
    - Bewerber-language_pref respektieren
    - Dateien: `services/email_service.py`

### P2 – Ausbau / Komfort (spaeter)

13. **Reporting erweitern** (Diagramme, Zeitraeume, Pro-Mitarbeiter)
14. **Kalender-Integration** (FullCalendar o.ae.)
15. **Virenscanning** (ClamAV Integration)
16. **Upload-Sicherheit** (Content-Type-Validierung, Magic-Bytes)
17. **Profilzentrierung** (Bewerber-Portal Dashboard als Hub)
18. **Partner-Reports** (Agentur-spezifische Auswertungen)

---

## D. Risk-/Dependency-Analyse

### Hohe Risiken
1. **Bewerbernummer-Einfuehrung**: Muss atomar und idempotent sein (Race Conditions bei Parallelbewerbungen)
2. **i18n-Rollout**: ~15 Seiten mit hardcodierten Strings. Risiko: Uebersetzungen unvollstaendig
3. **Document-Upload**: Abhaengig von S3/RustFS-Verfuegbarkeit. Fallback auf MongoDB GridFS pruefen

### Abhaengigkeiten
- P0 Items sind unabhaengig voneinander parallelisierbar
- Bewerbernummer muss VOR Rechnungs-i18n fertig sein
- DB-Indizes koennen sofort ohne Feature-Aenderung erstellt werden
- i18n Keys muessen vor Frontend-Rollout vorhanden sein

### Bekannte technische Schulden
- `StaffReportingPage.js`: Unused imports (FileText, API)
- Document-Samples in DB haben leere `storage_key` und `file_size: null`
- Invoice `list` Endpunkt projiziert `_id: 0` aber gibt kein stabiles `id` zurueck
- Mehrere Router haben redundante Rollen-Checks statt einheitlichem Decorator

---

## E. Teststrategie

### E.1 Pro P0-Feature
| Feature | Backend-Test | Frontend-Test | E2E-Test |
|---------|-------------|--------------|----------|
| Bewerbernummer | pytest: Auto-Gen, Uniqueness | Screenshot: Anzeige | Testing Agent: Full Flow |
| Bewerbungsprozess | curl: /api/leads/ingest | Screenshot: ApplyPage | Testing Agent: Apply + Login |
| Dokumenten-Upload | curl: Upload/Download/Delete | Screenshot: DocumentsPage | Testing Agent: Upload-Flow |
| i18n | - | Screenshot: EN/DE Toggle | Testing Agent: Sprachumschaltung |
| Rechnungs-i18n | curl: PDF Download | Screenshot: PDF-Vorschau | - |
| Performance | Timing: DB Query < 100ms | Lighthouse | - |

### E.2 Regression nach jeder Phase
- Alle Auth-Flows (Login, Register, Refresh)
- Bewerbung anlegen
- Dokument hochladen
- Rechnung erstellen + PDF
- Nachricht senden
- Task erstellen

---

## F. Implementierungsreihenfolge (Wellen)

### Welle 1: Fundament (P0-Kern)
1. DB-Indizes erstellen → sofort, kein Risiko
2. Bewerbernummer einführen → Backend + Frontend
3. AuthContext Loading-Fix → Frontend

### Welle 2: Bewerbung + Dokumente (P0)
4. Bewerbungsprozess E2E testen + fixen
5. Dokument-Upload fuer Bewerber reparieren
6. Dokument-Verwaltung (Loeschen, Ersetzen, Grouping)

### Welle 3: i18n + Rechnungen (P0)
7. i18n Keys vervollstaendigen (EN)
8. Staff-Seiten durchgehen: t() einfuegen
9. Rechnungs-PDF i18n + Bewerbernummer

### Welle 4: Betriebsoptimierung (P1)
10. Aufgaben-Modul erweitern
11. Messaging-Performance
12. Fallliste-Filter
13. Dashboard-Layout

### Welle 5: Ausbau (P2)
14. Reporting-Erweiterung
15. Kalender
16. Sicherheits-Haertung

---

## G. Offene Prüffragen (Ergebnisse)

1. **language_pref**: Gespeichert in `users.language_pref`. Gelesen in AuthContext, sync mit i18n. Ueberschrieben via SettingsPage PUT. ABER: Email-Templates ignorieren es.

2. **Bewerbungsstatus-Pfade**: `routers/applications.py` → Stage-Change → `services/stage_effects.py` → Auto-Tasks. Pipeline: lead_new → in_review → pending_docs → ... → enrolled.

3. **Upload-Kette**: UI (base64) → API (`/api/applications/:id/documents/upload`) → S3 (`services/storage.py`) → Validierung (`document_validation.py`). Moegliche Bruchstellen: S3-Config, File-Size, Content-Type-Check.

4. **Dokument-Versionierung**: Replace-Endpunkt existiert (`superseded`-Status). Loeschen existiert. Erneute Pruefung existiert. Frontend fehlt fuer Bewerber.

5. **Zuordnung Dok ↔ App ↔ Bewerber ↔ Workspace**: `documents.application_id` → `applications.applicant_id` → `users._id`. Workspace nur auf Application-Ebene.

6. **Kommunikation + Sprache**: Conversations haben kein `language`-Feld. E-Mails werden immer auf Deutsch gesendet.

7. **Profil als Einstiegspunkt**: Staff: ApplicantDetailPage ist zentralisiert (Fallakte). Bewerber: DashboardPage ist nur Uebersicht mit Links.

8. **Rechnungslogik**: CRUD komplett. PDF-Gen komplett (nur DE). E-Mail-Versand via Resend. MOCK: Nichts – alles echt. FEHLT: Bewerbernummer.

9. **Bewerbernummer**: FEHLT KOMPLETT. Kein Feld, keine Generierung, keine Anzeige.

10. **Inbox langsam**: Keine Compound-Indizes auf `messages` (conversation_id, sent_at). 137 Messages, 134 Conversations → noch verkraftbar, aber O(n) Queries.

11. **Loading-Screen haengen**: AuthContext hat kein Timeout. Wenn `/api/auth/me` haengt → Endlos-Loading.

12. **Listen/Kanban**: StaffCasesPage + KanbanPage existieren getrennt. Keine Zusammenfuehrung, aber Daten-Quelle ist identisch.

13. **Reporting-Daten**: Invoice-Stats vorhanden. Bewerber-Stats vorhanden. FEHLT: Zeitraum-Filter, Pro-Mitarbeiter-Auswertung.

14. **Security-Luecken**: Kein AV-Scan. Base64-Upload ohne Magic-Byte-Validierung. Aber: File-Size-Limit (10MB), Content-Type-Check, Rate-Limiting, Security-Headers.

15. **Sofort-Fixes vs. Architekturarbeit**: DB-Indizes, AuthContext-Fix, Bewerbernummer → sofort. i18n-Rollout → mittelfristig (15+ Dateien). Kalender → Architekturarbeit.
