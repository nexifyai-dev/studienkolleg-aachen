# W2G Frontend-Audit – Vollstaendige Analyse

**Stand:** 2026-04-06 | **Version:** 1.0

---

## A. Seiteninventar & Zustandsbewertung

### Legende
- OK = produktionsreif
- TEILW = teilweise fertig, Maengel
- STUB = Platzhalter / nicht funktional
- FEHLT = nicht implementiert

### A.1 Oeffentliche Seiten (8 Seiten)

| Seite | Zeilen | Zustand | i18n | Responsive | Kritische Probleme |
|-------|--------|---------|------|------------|-------------------|
| HomePage | 1071 | OK | OK (t()) | OK | CTA-Flow koennte klarer sein |
| ApplyPage | 311 | TEILW | TEILW | OK | Fehlerhandling bei Upload unklar |
| CoursesPage | 317 | OK | OK | OK | - |
| ServicesPage | 226 | OK | OK | OK | - |
| ContactPage | 183 | OK | OK | OK | - |
| KnowledgeCenterPage | 223 | OK | OK | OK | - |
| BookingPage | 383 | TEILW | OK | OK | Externe Anbindung fehlt |
| LegalPage | 304 | OK | TEILW | OK | Teile hardcoded DE |

### A.2 Auth (3 Seiten)

| Seite | Zeilen | Zustand | i18n | Probleme |
|-------|--------|---------|------|----------|
| LoginPage | 159 | OK | TEILW | data-testids vorhanden |
| RegisterPage | 20 | STUB | NEIN | Redirect zu /auth/login, kein echtes Register-Form |
| ForgotPasswordPage | 144 | OK | TEILW | Hardcoded DE Strings |

### A.3 Applicant Portal (10 Seiten)

| Seite | Zeilen | Zustand | i18n | Kritische Probleme |
|-------|--------|---------|------|--------------------|
| DashboardPage | 233 | OK | TEILW | Bewerbernummer eingefuegt (Welle 1) |
| JourneyPage | 118 | TEILW | NEIN | Hardcoded DE, kein dynamischer Status |
| ApplicantTasksPage | 70 | TEILW | NEIN | Komplett hardcoded DE, "Jetzt erledigen" ohne Aktion |
| DocumentsPage | 420 | TEILW | TEILW | Delete/Replace UI neu (Welle 2), Status-Grouping vorhanden |
| MessagesPage | 290 | TEILW | TEILW | Mix aus DE/EN Strings |
| FinancialsPage | 242 | OK | OK | Gutes i18n-Pattern mit lang-Variable |
| SettingsPage | 157 | TEILW | TEILW | Sprachspeicherung muss getestet werden |
| ConsentPage | 264 | TEILW | TEILW | Consent-Logik funktioniert, aber UX verbesserbar |
| ApplicantAppointmentsPage | 280 | STUB | NEIN | Kein Backend-Endpunkt, nur Platzhalter-UI |
| ApplicantMorePage | 70 | STUB | NEIN | Link-Liste, keine echte Funktion |

### A.4 Staff Portal (15 Seiten)

| Seite | Zeilen | Zustand | i18n | Kritische Probleme |
|-------|--------|---------|------|--------------------|
| StaffDashboard | 485 | OK | TEILW | Welle 3 i18n begonnen |
| KanbanPage | 458 | TEILW | NEIN | Komplett hardcoded DE |
| StaffCasesPage | 430 | OK | TEILW | Welle 1+3 Updates, Bewerbernr. + Suche |
| ApplicantDetailPage | 938 | OK | NEIN | Groesste Seite, komplett hardcoded DE, aber funktional stark |
| StaffTasksPage | 586 | TEILW | NEIN | Komplett hardcoded DE, kein due_date-Sorting |
| StaffMessagingPage | 772 | TEILW | NEIN | Komplett hardcoded DE |
| StaffInvoicesPage | 692 | TEILW | NEIN | Komplett hardcoded DE |
| StaffDocumentsReviewPage | 396 | TEILW | NEIN | Komplett hardcoded DE |
| StaffReportingPage | 149 | STUB | NEIN | Minimal, keine Diagramme, keine Zeitraeume |
| OraclePage | 496 | OK | NEIN | KI-Chat, funktional, aber hardcoded DE |
| TeacherDashboard | 250 | TEILW | NEIN | Hardcoded DE |
| TeacherStudentsPage | 96 | STUB | NEIN | Funktional |
| TeacherStudentDetailPage | 110 | STUB | NEIN | Funktional |
| TeacherSupportPage | 18 | STUB | NEIN | Platzhalter |
| TeacherMorePage | 15 | STUB | NEIN | Platzhalter |

### A.5 Admin Portal (10 Seiten)

| Seite | Zeilen | Zustand | i18n | Kritische Probleme |
|-------|--------|---------|------|--------------------|
| AdminDashboard | 282 | TEILW | NEIN | Hardcoded DE |
| UsersPage | 273 | TEILW | NEIN | Funktional, hardcoded DE |
| AuditPage | 142 | TEILW | NEIN | Funktional, hardcoded DE |
| AdminCasesPage | 107 | STUB | NEIN | Minimal, verlinkt auf Staff-Cases |
| AdminPartnersPage | 84 | STUB | NEIN | Platzhalter |
| AdminKnowledgePage | 886 | OK | NEIN | Funktional, aber komplett hardcoded DE |
| AdminJobsPage | 428 | TEILW | NEIN | Funktional, hardcoded DE |
| AdminRulesPage | 163 | STUB | NEIN | Platzhalter-UI |
| AdminReportsPage | 100 | STUB | NEIN | Platzhalter |
| AdminSettingsPage | 234 | TEILW | NEIN | Teilw. funktional |

### A.6 Partner Portal (6 Seiten)

| Seite | Zeilen | Zustand | i18n | Kritische Probleme |
|-------|--------|---------|------|--------------------|
| PartnerDashboardPage | 208 | TEILW | NEIN | Hardcoded DE |
| PartnerReferralsPage | 95 | STUB | NEIN | Minimal |
| PartnerTrackingPage | 103 | STUB | NEIN | Funktional, aber duenn |
| PartnerLinkPage | 70 | TEILW | NEIN | Funktional |
| PartnerMessagesPage | 117 | STUB | NEIN | Platzhalter |
| PartnerSettingsPage | 121 | TEILW | NEIN | Funktional |

### A.7 Layouts (5 Komponenten)

| Komponente | Zeilen | Zustand | i18n | Probleme |
|-----------|--------|---------|------|----------|
| PortalShell | 276 | OK | TEILW | Nav-Labels hardcoded DE |
| StaffLayout | 38 | OK | NEIN | Nav-Labels hardcoded DE |
| ApplicantLayout | 38 | OK | NEIN | Nav-Labels hardcoded DE |
| AdminLayout | 22 | OK | NEIN | - |
| PartnerLayout | 15 | OK | NEIN | - |

---

## B. Kritische Frontend-Findings (P0)

### B.1 Navigation-Labels in ALLEN Layouts hardcoded DE
- **Problem:** StaffLayout, ApplicantLayout, AdminLayout, PartnerLayout haben feste deutsche Labels
- **Impact:** Englisch-nutzende Mitarbeiter sehen deutsche Navigation
- **Fix:** t() + i18n Keys fuer alle Nav-Labels
- **Dateien:** `StaffLayout.js`, `ApplicantLayout.js`, `AdminLayout.js`, `PartnerLayout.js`

### B.2 ~30 Seiten komplett ohne i18n
- **Problem:** Fast alle Staff/Admin/Partner-Seiten nutzen KEIN `useTranslation()`
- **Impact:** System ist NICHT auf Englisch nutzbar
- **Fix:** Systematischer i18n-Rollout in Wellen

### B.3 ApplicantTasksPage "Jetzt erledigen" Button ohne Aktion
- **Problem:** CTA-Button hat keinen `onClick` Handler
- **Impact:** Bewerber klickt, nichts passiert
- **Fix:** Verlinken auf relevante Seite (Documents, Messages, etc.)

### B.4 RegisterPage ist nur ein Redirect (20 Zeilen)
- **Problem:** Kein echtes Registrierungsformular
- **Impact:** Bewerber koennen sich nicht selbst registrieren
- **Status:** Registrierung laeuft ueber /apply → Account wird automatisch erstellt

### B.5 ApplicantAppointmentsPage und TeacherSupportPage sind Stubs
- **Problem:** Keine Backend-Anbindung, nur UI-Platzhalter
- **Impact:** Feature existiert visuell, aber nicht funktional
- **Fix:** Als "Coming Soon" markieren oder Backend anbinden

### B.6 StaffReportingPage minimal (149 Zeilen)
- **Problem:** Keine Diagramme, keine Zeitraeume, keine Pro-Mitarbeiter-Auswertung
- **Impact:** Reporting-Anforderung nicht erfuellt
- **Fix:** Recharts-Integration, Zeitraum-Filter, Aggregation

---

## C. Design-/UX-Findings (P1)

### C.1 Inkonsistente Status-Labels
- StaffTasksPage: { open: 'Offen', in_progress: 'In Bearbeitung', done: 'Erledigt' }
- ApplicantTasksPage: Gleiche Keys, gleiche Labels → aber keine i18n
- StaffInvoicesPage: { draft: 'Entwurf', ... } → hardcoded
- **Fix:** Zentrale STATUS_LABELS in `utils.js` mit i18n

### C.2 Fehlende Ueberfaellig-Markierung bei Aufgaben
- **Problem:** Tasks mit abgelaufenem `due_date` werden nicht visuell hervorgehoben
- **Impact:** Staff sieht nicht sofort, welche Aufgaben kritisch sind
- **Fix:** CSS-Klasse + visuelle Markierung wenn `due_date < now`

### C.3 StaffTasksPage: Keine Sortierung nach Faelligkeit
- **Problem:** Tasks werden nur nach created_at sortiert
- **Impact:** Staff muss manuell suchen
- **Fix:** Sortier-Optionen (Faelligkeit, Prioritaet, Status)

### C.4 Fallliste Kanban vs. Cases Redundanz
- **Problem:** Kanban und Fallliste zeigen gleiche Daten, unterschiedliche Ansichten
- **Impact:** Verwirrung, welche Ansicht zu nutzen
- **Fix:** ViewToggle (bereits vorhanden) konsistenter einsetzen

### C.5 Profil-Zentrierung Bewerber-Portal
- **Problem:** Dashboard zeigt Links, aber keine Inline-Aktionen
- **Impact:** Bewerber muss immer navigieren
- **Fix:** Wichtigste Aktionen direkt im Dashboard (Upload, Nachricht, Aufgabe)

### C.6 Messaging-Performance
- **Problem:** Alle Conversations werden gleichzeitig geladen
- **Impact:** Langsam bei vielen Konversationen
- **Fix:** Pagination + virtualisierte Liste

---

## D. Frontend-/Backend-Kopplungsprobleme

### D.1 ApplicantTasksPage: Bereich/Sort-Selects ohne Backend-Anbindung
- **Problem:** Dropdown "Bereich" und "Sortierung" aendern nichts
- **Fix:** Backend-Filter-Parameter nutzen oder clientseitig implementieren

### D.2 FinancialsPage: PDF-Download via direkten URL-Aufruf
- **Problem:** `window.open(API + '/api/invoices/...')` nutzt keine Cookies
- **Impact:** PDF-Download schlaegt evtl. fehl wegen fehlender Auth
- **Fix:** apiClient.get mit responseType: 'blob' nutzen

### D.3 Document-Upload: Grosse Dateien als Base64
- **Problem:** Gesamte Datei wird als Base64 im JSON-Body gesendet
- **Impact:** 10MB Datei → ~13.3MB JSON, Browser-Memory-Druck
- **Status:** Funktioniert fuer uebliche Dokumentengroessen (<5MB)

### D.4 AuthContext: agency_admin/agency_agent Routing fehlt
- **Problem:** PublicRoute redirected 'affiliate' zu /partner
- **Impact:** agency_admin und agency_agent werden zu /portal gesendet
- **Fix:** Rollen in PublicRoute erweitern

---

## E. Priorisierter Frontend-Umsetzungsplan

### P0 – Go-Live-Frontend (SOFORT)

1. **Layout-Navigation i18n** (alle 4 Layouts)
   - t() fuer alle Nav-Labels
   - Aufwand: 1h

2. **ApplicantTasksPage CTA-Fix** (Button ohne Aktion)
   - onClick: Navigation zum relevanten Bereich
   - Aufwand: 15min

3. **PDF-Download Auth-Fix** (FinancialsPage)
   - apiClient.get mit blob statt window.open
   - Aufwand: 30min

4. **Agency-Routing Fix** (PublicRoute)
   - agency_admin/agency_agent → /partner
   - Aufwand: 5min

5. **Stubs als "Coming Soon" markieren**
   - ApplicantAppointmentsPage, AdminRulesPage, AdminReportsPage, TeacherSupportPage
   - Aufwand: 30min

### P1 – Betriebstauglichkeit

6. **StaffTasksPage: Sortierung + Ueberfaellig-Markierung**
7. **Zentrale Status-Labels mit i18n** (utils.js)
8. **StaffInvoicesPage: i18n-Rollout**
9. **StaffMessagingPage: Pagination**
10. **Reporting-Seite: Recharts-Diagramme + Zeitraum**
11. **KanbanPage: i18n**
12. **ApplicantDetailPage: i18n** (groesste Aufgabe, 938 Zeilen)

### P2 – Ausbau

13. **Partner-Portal: Backend-Anbindung haerten**
14. **Kalender-Integration** (FullCalendar)
15. **Admin-Reports echte Daten**
16. **Teacher-Portal erweitern**
