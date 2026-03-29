# W2G Platform – Product Requirements Document

## Original Problem Statement
Baue eine produktionsreife, skalierbare, mehrmandantenfähige Plattform für "Studienkolleg Aachen / Way2Germany".

## Verbindliche Regeln (dauerhaft)
1. Preview schlägt Handoff
2. Alle KI nur über NSCall/nscale
3. Preise individuell – keine pauschalen Festpreise
4. Drive + Mem0 als Source of Truth
5. Keine "Potenzielle Verbesserungen" im Abschluss
6. Cookie-Consent nachträglich bearbeitbar
7. Fehlerregister in Mem0 führen
8. Sichtbar reicht nicht – operative Bearbeitbarkeit ist Pflicht
9. Bewerbung = Registrierung + Portal-Onboarding (Portal-first-Funnel)
10. Kommunikation Portal-first (E-Mails führen zurück ins Portal)

## Tech Stack
React 18, Tailwind, Shadcn/UI, react-i18next, FastAPI, Motor (async MongoDB), bcrypt, PyJWT, nscale (NSCall), Resend (send.nexify-automate.com)

## Architecture
```
backend/routers/  → auth, leads (mit Account-Erstellung), applications (CRUD + notes + activities + profile + email), documents, tasks, messaging (mit Attachments), consents, teacher, notifications, ai_screening, cost_simulator, followups (Wiedervorlage), export (CSV)
backend/services/ → nscale_provider, ai_screening, email (7+1 DE/EN templates + case_email), notifications (8 types), automation (triggers), audit, storage (local)
frontend/components/shared/ → CookieBanner, NotificationBell
frontend/components/layout/ → PublicNav, PublicFooter, StaffLayout (TOP HEADER), ApplicantLayout (TOP HEADER)
frontend/pages/staff/ → StaffDashboard (KPI+Export+Wiedervorlage), StaffTasksPage, StaffMessagingPage (mit Datei-Upload), ApplicantDetailPage (mit Wiedervorlage), KanbanBoard, TeacherDashboard
frontend/pages/portal/ → Dashboard, Documents, Journey, Settings, Consent, Financials, MessagesPage (mit Datei-Upload)
frontend/pages/public/ → Home, Courses, Services, Contact, Apply (mit Registrierung), FAQ, Legal
```

## Legal Entity
- W2G Academy GmbH
- Geschäftsführerin: Laura Saboor
- Amtsgericht Aachen, HRB 23610
- Theaterstr. 30–32, 52062 Aachen
- Website: https://www.stk-aachen.de
- E-Mail: info@stk-aachen.de

## Implemented Features

### Phase 1–3.6: Core + Public (DONE)
Multi-Workspace, JWT Auth, Lead-Ingest, Pipeline, Kanban, Docs, Tasks, Messaging, 8 Public Pages, Impressum/AGB/Datenschutz

### Phase 3.7b–d: i18n + AI + Teacher + Preise (DONE)
DE/EN systemweit, NSCall-AI, Teacher-Dashboard, Consent-UI, Individuelle Preisregel, TeacherAssignmentPanel

### Phase 3.7e: E-Mail + Notifications (DONE)
7 DE/EN-Templates, In-App Notification (8 Typen), Trigger-System

### Phase 3.7f–g: Cookie + Staging-Bereinigung (DONE)
Cookie-Banner DE/EN, Manage-Modus, Fehlerregister

### Phase 3.7h: Operative Portal-Reife (DONE)
Staff Dashboard KPIs, Bewerberdetail EditableFields, Audit-Trail, WhatsApp/E-Mail/Notizen

### Phase 3.7i: Staff-Portal-Reife (DONE - 2026-03-29)
- Dashboard-Links gefixt (/staff/tasks, /staff/messaging)
- Kanban-Board URL-Filter (?stage=xxx)
- Messaging-System komplett repariert (E2E)
- Staff-Navigation → Top-Header
- E-Mail-Templates CI-konform finalisiert
- Tasks-Router ObjectId-Fix

### Phase 3.7j: Portal- und Kommunikations-Finallauf (DONE - 2026-03-29)
- **Navigation portalweit vereinheitlicht**: ApplicantLayout von Sidebar auf Top-Header umgebaut. Staff, Applicant und Teacher haben jetzt konsistente obere Navigation.
- **Aufgaben vollständig operativ**: Erstellen, Bearbeiten, Filtern (Offen/In Bearbeitung/Erledigt), Statuswechsel, Prioritäten, Zuweisung
- **Nachrichten mit Datei-Upload**: Paperclip-Button, Base64-Upload via POST /api/conversations/{id}/attachments, Download via GET /api/messages/{id}/attachment, Attachment-Preview, Validierung (max 10 MB, erlaubte Typen)
- **Bewerbung + Registrierung gekoppelt**: ApplyPage hat Passwort-Felder + Datenschutz-Checkbox. Backend (leads.py) erstellt Account mit Passwort-Hash, setzt Auth-Cookies → Auto-Redirect ins Portal. Welcome-E-Mail wird versendet.
- **Portal-first Kommunikation**: Auto-Support-Konversation, alle E-Mails mit Portal-CTA-Button
- **Wiedervorlage-System (P2→DONE)**: Neuer followups-Router (CRUD), Fällige Wiedervorlagen im Dashboard-Panel, Wiedervorlage-Panel in Bewerber-Detailansicht
- **Exportfunktionen (P2→DONE)**: CSV-Export über GET /api/export/applications mit Stage-Filter, Export-Button im Dashboard
- **E-Mail-Footer finalisiert**: Geschäftsführerin Laura Saboor eingetragen
- **i18n ergänzt**: apply.account_title, apply.password_label etc. in DE/EN
- 100% Tests (iteration_13.json: 14/14 Backend + alle Frontend)

## Drive-Gegenprüfung (Phase 3.7j)
- 22+ Dokumente geprüft (Stand unverändert)
- Verifiziert: Navigation ✅, Registrierung ✅, Messaging ✅, Datei-Upload ✅, Export ✅, Wiedervorlage ✅

## Go-Live-Blocker (intern)
- E-Mail: info@stk-aachen.de vs info@cd-stk.com klären
- DSB-Kontaktdaten final bestätigen
- Drittanbieter-Liste prüfen
- Juristische Endprüfung Rechtstexte

## Backlog
### P1
- Erweiterte Bewerber-Detail-Ansicht für Lehrer
- Staff-Dashboard KPIs / Reporting Ausbau
- Partner-/Sub-Agentur-Portal

### P2
- Payment-Freischaltung
- PWA-Fähigkeit
- Erweiterte Suchfilter

## MOCKED
- Preiskalkulator: feature-flagged
- Zahlungsmodul: "in Vorbereitung"
