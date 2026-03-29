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

## Tech Stack
React 18, Tailwind, Shadcn/UI, react-i18next, FastAPI, Motor (async MongoDB), bcrypt, PyJWT, nscale (NSCall), Resend (send.nexify-automate.com)

## Architecture
```
backend/routers/  → auth, leads, applications (CRUD + notes + activities + profile + email), documents, tasks, messaging, consents, teacher, notifications, ai_screening, cost_simulator
backend/services/ → nscale_provider, ai_screening, email (7+1 DE/EN templates + case_email), notifications (8 types), automation (triggers), audit
frontend/components/shared/ → CookieBanner, NotificationBell
frontend/components/layout/ → PublicNav, PublicFooter, StaffLayout (TOP HEADER), ApplicantLayout
frontend/pages/staff/ → StaffDashboard, StaffTasksPage, StaffMessagingPage, ApplicantDetailPage, KanbanBoard, TeacherDashboard
frontend/pages/portal/ → Dashboard, Documents, Journey, Settings, Consent, Financials, MessagesPage
frontend/pages/public/ → Home, Courses, Services, Contact, Apply, FAQ, Legal
```

## Implemented Features

### Phase 1–3.6: Core + Public (DONE)
Multi-Workspace, JWT Auth, Lead-Ingest, Pipeline, Kanban, Docs, Tasks, Messaging, 8 Public Pages, Impressum/AGB/Datenschutz

### Phase 3.7b–d: i18n + AI + Teacher + Preise (DONE)
DE/EN systemweit, NSCall-AI, Teacher-Dashboard, Consent-UI, Individuelle Preisregel, TeacherAssignmentPanel

### Phase 3.7e: E-Mail + Notifications (DONE)
7 DE/EN-Templates, In-App Notification (8 Typen), Trigger: Status→E-Mail+Notif, Teacher→E-Mail+Notif, Consent→Notif, DocUpload→Notif

### Phase 3.7f: Cookie + Staging-Bereinigung (DONE)
Cookie-Banner DE/EN, 2 Kategorien, Staging-Hinweise entfernt, Mobile-Header optimiert

### Phase 3.7g: Cookie-Manage + Fehlerregister (DONE)
Footer-Link für Cookie-Einstellungen, Manage-Modus, Fehlerregister angelegt

### Phase 3.7h: Operative Portal-Reife (DONE - 2026-03-29)
- Staff Dashboard: 4 KPI-Cards mit klickbaren Links, Zuletzt bearbeitet, Handlungsbedarf-Sidebar, Schnellzugriff, Systemstatus
- Bewerberdetail – Manuelle Bearbeitung: EditableField für Persönliche/Bewerbungsdaten mit Audit-Trail
- WhatsApp im Fallkontext, E-Mail als Arbeitskanal, Interne Notizen, Bearbeitungsverlauf
- 100% Tests (iteration_11.json)

### Phase 3.7i: Operative Staff-Portal-Reife (DONE - 2026-03-29)
- **Dashboard-Links gefixt**: /staff/tasks → StaffTasksPage, /staff/messaging → StaffMessagingPage (keine Redirect mehr zur Home-Seite)
- **Kanban-Filter**: URL-Parameter ?stage=xxx werden ausgewertet, Filter-Banner mit "Filter entfernen", KPI-Links (Docs ausstehend, Neue Anfragen) öffnen direkt die gefilterte Kanban-Ansicht
- **Messaging-System komplett repariert**: 
  - Backend: Support-Konversation auto-erstellt (GET /api/conversations/support), enriched participants (Namen, Rollen), sender_name in Messages, mark-as-read Endpoint
  - Applicant: Auto-Support-Conversation beim Laden von /portal/messages, Polling für neue Nachrichten
  - Staff: Eigene Messaging-Seite (/staff/messaging) mit Konversationsliste, Suche, Nachrichtenansicht, Antwortfunktion
  - E2E verifiziert: Applicant sendet → Staff empfängt → Staff antwortet → Applicant sieht Antwort
- **Staff-Navigation → Top-Header**: Sidebar komplett entfernt, responsives Top-Header-Menü (Desktop: horizontal, Mobile: Hamburger), User-Dropdown, NotificationBell
- **StaffTasksPage**: Aufgaben erstellen/bearbeiten/filtern (Offen/In Bearbeitung/Erledigt), Prioritäten, Status-Wechsel
- **StaffDashboard verbessert**: Klarere Informationshierarchie, offene Aufgaben-Panel, korrekte Schnellzugriff-Links
- **E-Mail-Templates finalisiert**: CI-konformes Layout (HTML5 DOCTYPE), strukturierter Footer (GmbH, Registergericht, Adresse, Kontakt), Divider, konsistente Typografie, DE/EN, keine Festpreise, send_case_email-Funktion für Staff-Mails
- **Tasks-Router fix**: ObjectId-Serialisierung korrigiert (kein 500er bei POST /api/tasks)
- 100% Tests (iteration_12.json: 18/18 Backend + alle Frontend)

## Drive-Gegenprüfung (Phase 3.7i)
- 22+ Dokumente geprüft (gleicher Stand wie 3.7h)
- Verifiziert: Routing ✅, Navigation ✅, Messaging ✅, Filtern ✅, Aufgaben ✅, E-Mail-Templates ✅
- Offen: Wiedervorlage-System (P2), Erweiterte Suchfilter (P2)

## Go-Live-Blocker (intern)
- E-Mail: info@stk-aachen.de vs info@cd-stk.com klären
- DSB-Kontaktdaten final bestätigen
- Geschäftsführer-Name im E-Mail-Footer ergänzen
- Drittanbieter-Liste prüfen
- Juristische Endprüfung Rechtstexte

## Backlog
### P1
- Erweiterte Bewerber-Detail-Ansicht für Lehrer
- Staff-Dashboard KPIs / Reporting Ausbau

### P2
- Payment-Freischaltung, Partner-Portal, Exportfunktionen, PWA
- Wiedervorlage-System, Erweiterte Suchfilter

## MOCKED
- Preiskalkulator: feature-flagged
- Zahlungsmodul: "in Vorbereitung"
