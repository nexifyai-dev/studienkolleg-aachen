# W2G Plattform – IST/SOLL Funktionsreport
## Stand: 03.04.2026

---

## 1. PUBLIC PORTAL (Nicht eingeloggt)

### IST (Implementiert)
| Seite | Status | Details |
|-------|--------|---------|
| **Homepage** (`/`) | LIVE | Editorial Layout, Hero, Team (Laura Saboor), Campus Life (5 Fotos), Reels (5 Videos), Main Videos (2 MP4), Segmente, Programme, Statistik, Prozess-Steps, Trust, Testimonials, FAQ, CTA |
| **Kurse** (`/courses`) | LIVE | Kursübersicht (T/M/W/Deutsch) |
| **Services** (`/services`) | LIVE | Leistungsübersicht |
| **Knowledge Center** (`/knowledge`) | LIVE | Wissensartikel, Anabin-Suche |
| **Kontakt** (`/contact`) | LIVE | Kontaktformular |
| **Bewerbung** (`/apply`) | LIVE | Multi-Step Bewerbungsformular |
| **Terminbuchung** (`/booking`) | LIVE | Beratungstermin buchen |
| **Impressum** (`/legal`) | LIVE | Rechtliche Infos |
| **Datenschutz** (`/privacy`) | LIVE | Datenschutzerklärung |
| **AGB** (`/agb`) | LIVE | Allgemeine Geschäftsbedingungen |
| **Login** (`/auth/login`) | LIVE | JWT-Auth |
| **Registrierung** (`/auth/register`) | LIVE | Bewerber-Registrierung |
| **Passwort vergessen** (`/auth/forgot-password`) | LIVE | E-Mail-Reset |
| **PublicNav** | LIVE | Responsive Navigation, DE/EN Switcher |
| **PublicFooter** | LIVE | Footer mit Links |
| **CookieBanner** | LIVE | Basis-Cookie-Banner (Accept/Reject) |
| **SEOHead** | LIVE | Meta-Tags pro Seite |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| DSGVO-Cookie-Einstellungen (granular) | P0 | Cookie-Präferenzen (Essentiell/Statistik/Marketing) mit Speicherung |
| Echte Texte auf Courses/Services | P1 | Platzhalter durch Google Drive-Inhalte ersetzen |
| Design-Token-System auf alle Public Pages | P1 | Courses, Services, Contact, Knowledge noch nicht im neuen Editorial-Stil |

---

## 2. BEWERBER-PORTAL (Rolle: applicant)

### IST (Implementiert)
| Seite | Status | Details |
|-------|--------|---------|
| **Dashboard** (`/portal`) | LIVE | Status-Cockpit, Checkliste, Wissensbox |
| **Journey** (`/portal/journey`) | LIVE | Bewerbungsfortschritt visualisiert |
| **Aufgaben** (`/portal/tasks`) | LIVE | Zugewiesene Aufgaben abarbeiten |
| **Dokumente** (`/portal/documents`) | LIVE | Upload & Verwaltung eigener Dokumente |
| **Nachrichten** (`/portal/messages`) | LIVE | Kommunikation mit Staff |
| **Finanzen** (`/portal/financials`) | LIVE | Rechnungsübersicht & Zahlungsstatus |
| **Termine** (`/portal/appointments`) | LIVE | Terminübersicht |
| **Einstellungen** (`/portal/settings`) | LIVE | Profil bearbeiten |
| **Einwilligungen** (`/portal/consents`) | LIVE | DSGVO-Einwilligungsverwaltung |
| **Mehr** (`/portal/more`) | LIVE | Zusätzliche Optionen |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| Dokument-Upload mit S3/Presigned URLs | P1 | Aktuell lokaler Upload, muss auf Object Storage migriert werden |
| Echtzeit-Benachrichtigungen | P2 | WebSocket/SSE für sofortige Status-Updates |

---

## 3. STAFF-PORTAL (Rollen: staff, accounting_staff)

### IST (Implementiert)
| Seite | Status | Details |
|-------|--------|---------|
| **Dashboard** (`/staff`) | LIVE | KPIs, aktuelle Bewerbungen, Aufgaben-Feed |
| **Kanban-Board** (`/staff/kanban`) | LIVE | Drag-and-Drop Pipeline (Lead → Enrolled) |
| **Fälle** (`/staff/cases`) | LIVE | Alle Bewerbungen filtern & durchsuchen |
| **Aufgaben** (`/staff/tasks`) | LIVE | Task-Management für Staff |
| **Messaging** (`/staff/messaging`) | LIVE | E-Mail-Integration (Strato IMAP/SMTP), Direktnachrichten |
| **Dokumente** (`/staff/documents`) | LIVE | Dokument-Review & Freigabe |
| **Rechnungen** (`/staff/invoices`) | LIVE (UI) | Rechnungsliste, Status-Management, **PDF-Generierung nur als Stub** |
| **Reporting** (`/staff/reporting`) | LIVE | Auswertungen & Statistiken |
| **Fallakte** (`/staff/applicants/:id`) | LIVE | Detailansicht, KI-Screening, Dokumente, Notizen, Modals |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| PDF-Rechnungsgenerierung (ReportLab) | P1 | Echte PDF-Erstellung mit Bewerbernummer, Logo, Rechnungsdetails |
| Automatisches Re-Screening (Delta-Logik) | P1 | Bei neuem Dokument-Upload: nur die Delta-Änderungen neu screenen |
| Batch-Screening | P2 | Mehrere Bewerber gleichzeitig screenen |
| Export KI-Berichte als PDF | P3 | AI-Screening-Ergebnisse als PDF herunterladen |

---

## 4. LEHRER-PORTAL (Rolle: teacher)

### IST (Implementiert)
| Seite | Status | Details |
|-------|--------|---------|
| **Dashboard** (`/staff` als teacher) | LIVE | Lehrer-spezifische Ansicht mit Klassen-KPIs |
| **Studenten** (`/staff/students`) | LIVE | Eigene Studenten verwalten |
| **Student Detail** (`/staff/students/:id`) | LIVE | Detailansicht einzelner Student |
| **Support** (`/staff/teacher/messages`) | LIVE | Support-Nachrichten |
| **Mehr** (`/staff/more`) | LIVE | Erweiterte Optionen |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| Noten-/Prüfungsverwaltung | P2 | Noten eintragen, Prüfungsergebnisse verwalten |
| Anwesenheitskontrolle | P3 | Digitale Anwesenheitsliste |

---

## 5. ADMIN-PORTAL (Rollen: superadmin, admin)

### IST (Implementiert)
| Seite | Status | Details |
|-------|--------|---------|
| **Dashboard** (`/admin`) | LIVE | System-Übersicht, KPIs, letzte Aktivitäten |
| **Fälle** (`/admin/cases`) | LIVE | Alle Bewerbungen system-weit |
| **Benutzer** (`/admin/users`) | LIVE | User-Management (Erstellen, Rollen, Sperren) |
| **Partner** (`/admin/partners`) | LIVE | Affiliate-Partner verwalten |
| **Knowledge** (`/admin/knowledge`) | LIVE | Anabin-Wissensbasis pflegen |
| **Jobs** (`/admin/jobs`) | LIVE | Async-Worker-Jobs überwachen |
| **Regeln** (`/admin/rules`) | LIVE | Screening-Regeln konfigurieren |
| **Audit** (`/admin/audit`) | LIVE | Audit-Log aller System-Aktionen |
| **Reports** (`/admin/reports`) | LIVE | System-weite Auswertungen |
| **Einstellungen** (`/admin/settings`) | LIVE | System-Konfiguration |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| Stripe/Payment-Integration | P2 | Online-Zahlungen verarbeiten |
| Partner-Provisionsabrechnung | P2 | Automatische Abrechnung für Affiliates |

---

## 6. PARTNER-PORTAL (Rolle: affiliate)

### IST (Implementiert)
| Seite | Status | Details |
|-------|--------|---------|
| **Dashboard** (`/partner`) | LIVE | Partner-Übersicht, Provisionen |
| **Referrals** (`/partner/referrals`) | LIVE | Empfehlungen verwalten |
| **Tracking** (`/partner/tracking`) | LIVE | Conversion-Tracking |
| **Link** (`/partner/link`) | LIVE | Affiliate-Link generieren |
| **Nachrichten** (`/partner/messages`) | LIVE | Kommunikation mit Admin |
| **Einstellungen** (`/partner/settings`) | LIVE | Profil & Auszahlungsdaten |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| Automatische Provisionsabrechnung | P2 | Monatliche Abrechnung & Export |

---

## 7. BACKEND-SERVICES (Transversal)

### IST (Implementiert)
| Service | Status | Details |
|---------|--------|---------|
| JWT-Auth + Rollen | LIVE | Login, Register, Passwort-Reset, RBAC |
| KI-Screening (DeepSeek) | LIVE | Automatische Dokumentenanalyse |
| Anabin-Wissensbasis | LIVE | Universitäts-/Abschluss-Validierung |
| Async Worker | LIVE | Background Job Processing |
| E-Mail (Strato SMTP/IMAP) | LIVE | Senden & Empfangen |
| Dokument-Upload (lokal) | LIVE | Lokaler Datei-Upload |
| Benachrichtigungen (in-app) | LIVE | Bell-Icon mit Notifications |
| Audit-Logging | LIVE | Alle Aktionen protokolliert |
| Cost Simulator | LIVE | Kostenberechnung für Bewerber |
| Follow-Up System | LIVE | Automatische Erinnerungen |

### SOLL (Noch nicht umgesetzt)
| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| S3/Presigned URLs (Storage) | P1 | Persistenter Object Storage statt lokalem Upload |
| PDF-Generierung (ReportLab) | P1 | Rechnungs-PDFs mit Logo, Bewerbernummer |
| Delta-Screening | P1 | Nur geänderte Dokumente neu screenen |
| i18n E-Mail-Templates | P2 | Mehrsprachige E-Mails (DE/EN/AR etc.) |
| Stripe Payment Webhooks | P2 | Zahlungseingang automatisch verbuchen |
| PWA-Fähigkeit | P3 | Service Worker, Offline-Modus, Push |
| Test-Artefakte bereinigen | P2 | "TEST_" Einträge aus DB entfernen |

---

## ZUSAMMENFASSUNG

| Portal | IST-Seiten | IST-Features | SOLL-Features |
|--------|-----------|--------------|---------------|
| Public | 13 Seiten | 16 Features | 3 Features |
| Bewerber | 10 Seiten | 10 Features | 2 Features |
| Staff | 9 Seiten | 9 Features | 4 Features |
| Lehrer | 5 Seiten | 5 Features | 2 Features |
| Admin | 10 Seiten | 10 Features | 2 Features |
| Partner | 6 Seiten | 6 Features | 1 Feature |
| Backend | - | 10 Services | 7 Features |
| **GESAMT** | **53 Seiten** | **66 Features** | **21 Features** |
