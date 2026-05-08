# W2G Plattform – Detaillierte Nutzerfunktionen pro Portal
## Stand: 03.04.2026

---

## 1. PUBLIC PORTAL (Nicht eingeloggt)

### Seiten & Funktionen
| Seite | Route | Funktionen | Datenquellen | Verlinkung |
|-------|-------|------------|--------------|------------|
| **HomePage** | `/` | Hero + CTA, Team (Laura Saboor), Campus Life (5 Fotos), Reels (5 Videos), Segmente (5 Bereiche), Main Videos (2 MP4), Programme (4 Kurse), Statistik-Counter, Prozess-Schritte (01-04), Trust (4 Features), Testimonials (3 Slider), FAQ (5 Fragen), CTA-Footer | Statisch (i18n DE/EN) | → `/apply`, `/booking`, `/courses`, `/contact` |
| **Kurse** | `/courses` | Kursübersicht (T-Kurs, M-Kurs, W-Kurs, Deutsch), Kursbeschreibungen, Voraussetzungen | Statisch | → `/apply` |
| **Services** | `/services` | Leistungsübersicht, Beratung, Visum, Unterkunft, Versicherung | Statisch | → `/booking` |
| **Knowledge Center** | `/knowledge` | Wissensartikel, Anabin-Universitätssuche (Suchfeld + Ergebnisse) | API: `GET /api/anabin/` | → interne Links |
| **Kontakt** | `/contact` | Kontaktformular (Name, E-Mail, Nachricht, Telefon), Google Maps Karte | API: `POST /api/applications` (als Lead) | → Dankeseite |
| **Bewerbung** | `/apply` | Multi-Step Formular: Persönliche Daten → Bildung → Dokument-Upload → Zusammenfassung → Absenden | API: `POST /api/applications`, `POST /api/documents` | → `/auth/login` (nach Registrierung) |
| **Terminbuchung** | `/booking` | Kalender-Ansicht, Slot-Auswahl, Buchungsformular | API: `GET /api/appointments/public-slots`, `POST /api/appointments/public-booking` | → Bestätigungsseite |
| **Impressum** | `/legal` | Statischer Text (Geschäftsführerin, Adresse, USt-ID) | Statisch | — |
| **Datenschutz** | `/privacy` | DSGVO-Datenschutzerklärung | Statisch | — |
| **AGB** | `/agb` | Allgemeine Geschäftsbedingungen | Statisch | — |
| **Login** | `/auth/login` | E-Mail/Passwort Login, "Passwort vergessen" Link | API: `POST /api/auth/login` | → Portal je nach Rolle |
| **Registrierung** | `/auth/register` | Vorname, Nachname, E-Mail, Passwort | API: `POST /api/auth/register` | → `/auth/login` |
| **Passwort vergessen** | `/auth/forgot-password` | E-Mail eingeben → Reset-Link per E-Mail | API: `POST /api/auth/forgot-password` | → `/auth/login` |
| **Passwort zurücksetzen** | `/auth/reset-password` | Neues Passwort setzen (mit Token) | API: `POST /api/auth/reset-password` | → `/auth/login` |

### Globale Elemente
| Element | Funktionen |
|---------|------------|
| **PublicNav** | Logo, Home, Courses, Services, Knowledge, Booking, Contact, DE/EN Switcher, Sign In, Apply Now (CTA) |
| **PublicFooter** | Links zu allen Seiten, Impressum, Datenschutz, AGB |
| **CookieBanner** | Accept All / Reject Buttons, Basis-Consent-Tracking |
| **SEOHead** | Meta-Title, Meta-Description, OG-Tags pro Seite |

---

## 2. BEWERBER-PORTAL (Rolle: `applicant`)

### Seiten & Funktionen
| Seite | Route | Funktionen | Datenquellen | UI-Elemente |
|-------|-------|------------|--------------|-------------|
| **Dashboard** | `/portal` | Status-Badge (z.B. "In Prüfung"), offene Aufgaben-Counter, letzte Nachrichten, Schnellzugriff auf Upload | API: `GET /api/applications/{id}`, `GET /api/tasks`, `GET /api/notifications` | Karten-Grid, Progress-Ring |
| **Journey** | `/portal/journey` | Timeline/Stepper: Bewerbung → Prüfung → Angebot → Einschreibung, aktiver Step hervorgehoben | API: `GET /api/applications/{id}` (Status) | Vertikale Timeline |
| **Aufgaben** | `/portal/tasks` | Liste offener Tasks (z.B. "Dokument X hochladen"), Status (offen/erledigt), Fälligkeitsdatum | API: `GET /api/tasks` | Task-Liste, Checkboxen |
| **Dokumente** | `/portal/documents` | Upload-Bereich (Drag & Drop), Liste eigener Dokumente, Download, Lösch-Option, Validierungsstatus | API: `GET /api/documents/my`, `POST /api/documents` | Upload-Zone, Dokument-Tabelle |
| **Nachrichten** | `/portal/messages` | Chat-Ansicht mit Staff, Nachricht senden (Text + Anhänge), Lesebestätigungen | API: `GET/POST /api/messaging/conversations/*` | Chat-Bubbles, Input-Field |
| **Finanzen** | `/portal/financials` | Rechnungsübersicht, Status (offen/bezahlt/überfällig), Betrag, PDF-Download-Link | API: `GET /api/invoices/my` | Tabelle, Status-Badges |
| **Termine** | `/portal/appointments` | Eigene Termine anzeigen, Stornierung möglich | API: `GET /api/appointments` | Termin-Karten |
| **Einstellungen** | `/portal/settings` | Profil bearbeiten (Name, Telefon, Adresse), Passwort ändern, Sprache wählen | API: `PUT /api/applications/{id}/profile`, `GET /api/auth/me` | Formular |
| **Einwilligungen** | `/portal/consents` | DSGVO-Einwilligungen verwalten (Datenverarbeitung, Marketing, Drittanbieter), Widerruf möglich | API: `GET /api/consents/my`, `POST /api/consents/grant`, `POST /api/consents/revoke/*` | Toggle-Switches |
| **Mehr** | `/portal/more` | Zusätzliche Links (FAQ, AGB, Abmelden) | — | Link-Liste |

### Navigation (PortalShell)
- Dashboard, Journey, Aufgaben, Dokumente, Nachrichten, Finanzen, Termine, Einstellungen
- Bell-Icon: Ungelesene Benachrichtigungen (API: `GET /api/notifications/unread-count`)
- Logout-Button

---

## 3. STAFF-PORTAL (Rollen: `staff`, `accounting_staff`)

### Seiten & Funktionen
| Seite | Route | Funktionen | Datenquellen | UI-Elemente |
|-------|-------|------------|--------------|-------------|
| **Dashboard** | `/staff` | KPI-Karten (Bewerbungen gesamt, offen, diese Woche), Aufgaben-Feed, Quick-Actions | API: `GET /api/applications`, `GET /api/tasks` | KPI-Cards, Activity-Feed |
| **Kanban-Board** | `/staff/kanban` | Drag-and-Drop Pipeline: Lead → Screening → Interview → Enrolled → Rejected. Karten mit Name, Herkunft, Status-Badge | API: `GET /api/applications`, `PUT /api/applications/{id}` | Spalten, Drag-Cards |
| **Fälle** | `/staff/cases` | Tabelle ALLER Bewerbungen mit Filtern (Status, Datum, Land, Kurs). Suchfeld. Sortierung | API: `GET /api/applications` | Tabelle, Filter-Bar |
| **Aufgaben** | `/staff/tasks` | Task-Übersicht mit Filtern, Task erstellen (Titel, Beschreibung, Zuordnung, Fälligkeit, Priorität), Status-Updates | API: `GET/POST/PUT/DELETE /api/tasks/*` | Task-Tabelle, Modal |
| **Messaging** | `/staff/messaging` | Konversations-Liste (links), Chat (rechts), E-Mail senden via Strato SMTP, IMAP-Sync, Anhänge | API: `GET/POST /api/messaging/*`, `POST /api/messaging/send-email`, `POST /api/messaging/sync-imap` | Split-View, Chat |
| **Dokumente** | `/staff/documents` | Review-Queue: Eingereichte Dokumente prüfen, Genehmigen/Ablehnen, Kommentare, Validierung | API: `GET /api/applications/{id}/documents`, `PUT /api/documents/{id}/review` | Review-Liste |
| **Rechnungen** | `/staff/invoices` | Rechnungen erstellen (Empfänger, Betrag, Positionen), Liste, Status (Entwurf/Gesendet/Bezahlt), PDF-Download (STUB) | API: `GET/POST/PATCH/DELETE /api/invoices/*`, `GET /api/invoices/{id}/pdf` | Tabelle, Modal |
| **Reporting** | `/staff/reporting` | Charts: Bewerbungen pro Monat, nach Herkunftsland, nach Kurswahl, Conversion-Rate | API: `GET /api/applications` (aggregiert) | Bar/Pie Charts |
| **Fallakte** | `/staff/applicants/:id` | KOMPLETTER Bewerberprofil-Viewer: Persönliche Daten, Bildungsweg, Dokumente, KI-Screening (DeepSeek), Notizen, Status-Änderung, E-Mail senden, Follow-Up planen, Rechnungserstellung | API: `GET /api/applications/{id}`, `POST /api/applications/{id}/ai-screen`, `POST /api/applications/{id}/notes`, `POST /api/followups` | Tab-System, Modals |

### Navigation (StaffLayout)
- Dashboard, Kanban, Fälle, Aufgaben, Messaging, Dokumente, Rechnungen, Reporting
- Bell-Icon: Benachrichtigungen
- Profilmenü: Einstellungen, Logout

---

## 4. LEHRER-PORTAL (Rolle: `teacher`)

### Seiten & Funktionen
| Seite | Route | Funktionen | Datenquellen | UI-Elemente |
|-------|-------|------------|--------------|-------------|
| **Dashboard** | `/staff` (teacher-view) | Anzahl zugewiesener Studenten, nächste Unterrichtszeiten, Quick-Links | API: `GET /api/teacher/my-students` | KPI-Cards |
| **Studenten** | `/staff/students` | Liste der zugewiesenen Studenten, Suchfeld, Filter nach Kurs | API: `GET /api/teacher/my-students` | Tabelle |
| **Student Detail** | `/staff/students/:id` | Profildaten des Studenten, Anwesenheit (noch nicht aktiv), Notizen | API: `GET /api/applications/{id}` | Detail-View |
| **Support** | `/staff/teacher/messages` | Support-Chat mit Admin/Staff | API: `GET/POST /api/messaging/conversations/support` | Chat-View |
| **Mehr** | `/staff/more` | Abmelden, Hilfe | — | Link-Liste |

---

## 5. ADMIN-PORTAL (Rollen: `superadmin`, `admin`)

### Seiten & Funktionen
| Seite | Route | Funktionen | Datenquellen | UI-Elemente |
|-------|-------|------------|--------------|-------------|
| **Dashboard** | `/admin` | System-KPIs: Gesamt-Bewerbungen, aktive Nutzer, offene Jobs, Systemstatus. Letzte Aktivitäten | API: diverse Endpoints | KPI-Grid, Activity-Log |
| **Fälle** | `/admin/cases` | ALLE Bewerbungen system-weit (wie Staff, aber ohne Rollen-Beschränkung) | API: `GET /api/applications` | Tabelle |
| **Benutzer** | `/admin/users` | User-Liste: Erstellen, Rollen zuweisen (staff, accounting_staff, teacher, admin), Sperren, Passwort-Reset | API: `GET/PUT /api/users/*`, `POST /api/auth/invite` | Tabelle, Modal |
| **Partner** | `/admin/partners` | Affiliate-Partner verwalten: Erstellen, Provisionssätze, Status, Referral-Statistik | API: `GET /api/partner/dashboard` | Tabelle, Detail-View |
| **Knowledge** | `/admin/knowledge` | Anabin-Wissensbasis: Einträge suchen/bearbeiten/hinzufügen/löschen, Review-Queue für unbekannte Abschlüsse, Wissenslücken identifizieren, Bulk-Update | API: `GET/POST/PUT/DELETE /api/anabin/*` | Tabelle, Modal, Batch-Actions |
| **Jobs** | `/admin/jobs` | Async-Worker-Übersicht: Job-Status (pending/running/done/failed), Retry, Cancel, Health-Check | API: `GET /api/jobs/*`, `POST /api/jobs/{id}/retry` | Tabelle, Status-Badges |
| **Regeln** | `/admin/rules` | KI-Screening-Regeln konfigurieren: Validierungs-Kriterien, Schwellwerte, Automatisierungsgrad | API: Intern | Formular |
| **Audit** | `/admin/audit` | Chronologisches Audit-Log: Wer hat was wann geändert. Filter nach User, Aktion, Zeitraum | API: Intern | Timeline, Filter |
| **Reports** | `/admin/reports` | System-weite Auswertungen: Conversion-Funnel, Umsatz, Herkunftsländer, Kurs-Auslastung | API: aggregiert | Charts, Export |
| **Einstellungen** | `/admin/settings` | System-Konfiguration: E-Mail-SMTP, Benachrichtigungs-Regeln, Rechnungs-Defaults, API-Keys | API: diverse | Formular-Tabs |

---

## 6. PARTNER-PORTAL (Rolle: `affiliate`)

### Seiten & Funktionen
| Seite | Route | Funktionen | Datenquellen | UI-Elemente |
|-------|-------|------------|--------------|-------------|
| **Dashboard** | `/partner` | Provisions-Übersicht: Verdient (gesamt/Monat), Ausgezahlt, Offen. Referral-Counter | API: `GET /api/partner/dashboard` | KPI-Cards |
| **Referrals** | `/partner/referrals` | Liste aller geworbenen Bewerber: Name, Status, Datum, Provision | API: `GET /api/partner/referrals` | Tabelle |
| **Tracking** | `/partner/tracking` | Conversion-Tracking: Klicks, Registrierungen, Abschlüsse, Rate | API: `GET /api/partner/dashboard` | Charts |
| **Affiliate-Link** | `/partner/link` | Persönlicher Referral-Link generieren/kopieren, QR-Code | API: `GET /api/partner/referral-link` | Link-Copy, QR |
| **Nachrichten** | `/partner/messages` | Kommunikation mit Admin | API: `GET/POST /api/messaging/*` | Chat-View |
| **Einstellungen** | `/partner/settings` | Bankdaten, Steuerdaten, Profil bearbeiten | API: `PUT /api/users/{id}` | Formular |

---

## 7. BACKEND-SERVICES (Transversal)

### Aktive Services
| Service | Technologie | Endpunkte | Beschreibung |
|---------|-------------|-----------|--------------|
| **JWT-Auth** | FastAPI + bcrypt + PyJWT | `/api/auth/*` (8 Endpoints) | Login, Register, Refresh, Invite, Password Reset, RBAC |
| **KI-Screening** | DeepSeek API | `/api/applications/{id}/ai-screen*` (7 Endpoints) | Automatische Dokumentenanalyse, Scoring, Delta-Erkennung, Manuelle Nachprüfung |
| **Anabin-Wissensbasis** | MongoDB | `/api/anabin/*` (12 Endpoints) | Universitäts-/Abschluss-Validierung, Review-Queue, Bulk-Update |
| **Async Worker** | Custom Python Worker | `/api/jobs/*` (6 Endpoints) | Background Job Processing, Retry, Health-Check |
| **E-Mail (Strato)** | IMAP/SMTP | `/api/messaging/*` (15+ Endpoints) | Senden (SMTP), Empfangen (IMAP-Sync), Konversationen, Anhänge |
| **Dokumente** | Lokaler Upload | `/api/documents/*` (8 Endpoints) | Upload, Download, Review, Validierung |
| **Rechnungen** | MongoDB + ReportLab (Stub) | `/api/invoices/*` (12 Endpoints) | CRUD, PDF (Stub), Versand, Statistik |
| **Benachrichtigungen** | MongoDB | `/api/notifications/*` (4 Endpoints) | In-App Bell-Icon, Unread-Count, Mark-Read |
| **Aufgaben** | MongoDB | `/api/tasks/*` (11 Endpoints) | CRUD, Notizen, Anhänge, History |
| **Termine** | MongoDB | `/api/appointments/*` (7 Endpoints) | Buchung (öffentlich + intern), Slots, CRUD |
| **DSGVO-Einwilligungen** | MongoDB | `/api/consents/*` (5 Endpoints) | Grant, Revoke, Typen-Katalog |
| **Follow-Ups** | MongoDB | `/api/followups/*` (5 Endpoints) | Erinnerungen planen, fällige Follow-Ups |
| **Cost Simulator** | Konfiguration | `/api/cost-simulator/config` | Kostenberechnung für Bewerber |
| **Export** | CSV | `/api/export/applications` | Daten-Export |
| **Partner** | MongoDB | `/api/partner/*` (3 Endpoints) | Dashboard, Referrals, Link |
| **Nutzer-Verwaltung** | MongoDB | `/api/users/*` (4 Endpoints) | CRUD, Rollen, Kontakte |

---

## ZUSAMMENFASSUNG

| Portal | Seiten | API-Endpoints | Datenhaltung |
|--------|--------|--------------|--------------|
| Public | 14 Seiten | ~15 Endpoints | Statisch + MongoDB |
| Bewerber | 10 Seiten | ~25 Endpoints | MongoDB |
| Staff | 9 Seiten | ~60 Endpoints | MongoDB + DeepSeek + Strato |
| Lehrer | 5 Seiten | ~10 Endpoints | MongoDB |
| Admin | 10 Seiten | ~40 Endpoints | MongoDB |
| Partner | 6 Seiten | ~8 Endpoints | MongoDB |
| **GESAMT** | **54 Seiten** | **~100+ Endpoints** | **MongoDB + 3rd Party** |
