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
backend/services/ → nscale_provider, ai_screening, email (7 DE/EN templates), notifications (8 types), automation (triggers), audit
frontend/components/shared/ → CookieBanner, NotificationBell
frontend/components/layout/ → PublicNav, PublicFooter, StaffLayout, ApplicantLayout
frontend/pages/staff/ → StaffDashboard, ApplicantDetailPage, KanbanBoard, TeacherDashboard
frontend/pages/portal/ → Dashboard, Documents, Journey, Settings, Consent, Financials
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
- **Staff Dashboard**: 4 KPI-Cards (Neue Anfragen, In Bearbeitung, Docs ausstehend, Gesamt) mit klickbaren Links, "Zuletzt bearbeitet" mit klickbaren Bewerber-Zeilen, "Handlungsbedarf"-Sidebar, Schnellzugriff, Systemstatus
- **Bewerberdetail – Manuelle Bearbeitung**: EditableField-Komponente für Persönliche Daten (Name, E-Mail, Telefon, Land, Geb.-Datum) und Bewerbungsdaten (Kurstyp, Semester, Deutsch, Abschlussland, Kombination, Quelle) mit Hover-Edit-Icon und Audit-Trail
- **WhatsApp im Fallkontext**: Deep-Link mit vorausgefüllter Nachricht + Fallreferenz direkt aus Quick Actions Bar
- **E-Mail als Arbeitskanal**: CaseEmailComposer – Betreff + Text + Senden direkt aus dem Fall, geloggt in email_events Collection mit Versandstatus in Activity History
- **Interne Notizen**: CRUD für case_notes mit Autor, Rolle, Zeitstempel, Sichtbarkeit (intern/geteilt)
- **Bearbeitungsverlauf**: Unified Activity History – Statuswechsel, Profilbearbeitungen, Notizen, E-Mails, Dokumentereignisse mit Zeitstempeln und Akteuren
- **Backend-Endpunkte**: POST/GET notes, GET activities, PUT profile, POST send-email
- **100% Tests**: 20/20 Backend + alle Frontend (iteration_11.json)

## Drive-Gegenprüfung (Phase 3.7h)
- 22+ Dokumente geprüft
- Verifiziert: Anlegen ✅, Bearbeiten ✅, Suchen/Filtern ✅, Zuweisen ✅, Statuslogik ✅, Historie ✅, Dokumentenbezug ✅, Kommunikation ✅, Rollen ✅
- Offen: Wiedervorlage-System (P2), Erweiterte Suchfilter (P2)

## Go-Live-Blocker (intern)
- E-Mail: info@stk-aachen.de vs info@cd-stk.com klären
- DSB-Kontaktdaten final bestätigen
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
