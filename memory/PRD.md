# Hinweis

Dieses Dokument bleibt vorerst als historisches / Übergangsartefakt im Repository.

Die kanonische, weiter gepflegte Dokumentation liegt jetzt unter `docs/`, insbesondere:

- `docs/00-overview/product-overview.md`
- `docs/01-architecture/system-architecture.md`
- `docs/02-product/user-roles.md`
- `docs/03-backend/`
- `docs/06-operations/go-live-checklist.md`

Der Inhalt unten bleibt erhalten, sollte aber perspektivisch nicht mehr als alleinige Source of Truth verwendet werden.

---

# W2G Platform – PRD (Product Requirements Document)

## Projektübersicht
**Plattform:** Studienkolleg Aachen / Way2Germany
**Betreiber:** W2G Academy GmbH, Theaterstraße 30–32, 52062 Aachen
**Typ:** Multi-Tenant Applicant Management Platform
**Stack:** React + FastAPI + MongoDB
**Sprachen:** Deutsch (Standard), Englisch (vollständig)
**CI-Farbe:** #113655 (primary)

---

## Implementierte Features

### Öffentliche Website
- Homepage, Kurse, Services, Kontakt, Bewerbungsformular
- SEO: Meta-Titel, Descriptions, OG-Tags, hreflang DE/EN (react-helmet-async)
- Favicon: W2G-Markenicon (favicon.ico, logo192, logo512, apple-touch-icon)
- Cookie-Banner mit Consent-Logik
- Impressum, Datenschutzerklärung, AGB (Legal Pages)

### Authentifizierung
- Cookie-basierte JWT (httponly, Secure=true, SameSite=none)
- Rollen: superadmin, admin, staff, teacher, applicant, affiliate
- Relative API-URLs (REACT_APP_BACKEND_URL=leer) für Same-Origin-Betrieb
- Sprach-Synchronisation bei Login (i18n ← language_pref)

### Bewerberportal (/portal)
- Dashboard: Willkommen, Status-Karte, Quick-Stats, Quick-Actions, Nächste Schritte
- Journey: Bewerbungsfortschritt-Timeline
- Dokumente: Upload, Statusanzeige (Hochgeladen/In Prüfung/Akzeptiert/Abgelehnt)
- Nachrichten: Echtzeit-Chat mit Anhängen, bündig oben/unten, Input verankert
- Finanzen: "Zahlungsmodul in Vorbereitung" (Platzhalter)
- Einstellungen: Name, Sprache, Speichern
- Einwilligungen: DSGVO-Consent-Verwaltung
- Vollständig DE/EN (i18n über t()-Aufrufe)
- Onboarding-Tour (5 Schritte, DE/EN)

### Staff-Portal (/staff)
- Dashboard: KPIs, Schnellzugriff, Wiedervorlagen
- Kanban: Pipeline-Board nach Bewerbungsstatus
- Bewerberdetail: Alle Daten (Name, E-Mail, Telefon, Land, Geb.-Datum), Stage-Selector, Follow-ups, Notizen, Audit-Log, KI-Screening
- Aufgaben: Volloperativ (CRUD, Detail-Modal, Notizen, Anhänge, Download, Historie, Filter, Zuweisung, Priorität, Toast-Feedback)
- Nachrichten: Staff-Messaging mit Konversationsliste + Chat
- KI-Prüfung: Prominenter Button, "Vorschlag übernehmen" → Statuswechsel + Audit (NSCall/nscale)
- Export: CSV-Export der Bewerbungen

### Teacher-Portal (/staff als teacher-Rolle)
- Dashboard: Zugewiesene Fälle, Consent-gated Zugriff
- CI-Blau-Design durchgehend

### Partner-Portal (/partner)
- Dashboard: Statistiken (Gesamt/Aktiv/Eingeschrieben)
- Vermittlungen: Tabelle mit Name, Kurs, Status, Datum
- Empfehlungslink: Kopierbarer Link mit ?ref=-Parameter
- Einstellungen: Organisationsname, Sprache

### Admin-Portal (/admin)
- Dashboard, Benutzerverwaltung, Audit-Logs

### Systemweit
- CI-Blau (#113655) als einzige Primärfarbe für Buttons/Actions
- Sekundär: Outline/Neutral nur bei Primär-/Sekundär-Paaren
- Toast-Benachrichtigungen (sonner) für Aktions-Feedback
- Keine generischen Platzhalter (kein "React App")
- Responsive Design

---

## Architektur
```
/app/
├── backend/ (FastAPI)
│   ├── routers/ (auth, users, applications, documents, tasks, messaging, ai_screening, partner, export, followups, leads, teacher)
│   ├── services/ (audit, email, storage, ai, nscale_provider, automation)
│   ├── models/schemas.py
│   ├── config.py, database.py, deps.py, seed.py, server.py
│   └── tests/
├── frontend/ (React + Tailwind + Shadcn)
│   ├── src/
│   │   ├── App.js (HelmetProvider + Toaster + Routes)
│   │   ├── contexts/AuthContext.js (syncLanguage)
│   │   ├── lib/apiClient.js (relative URLs)
│   │   ├── locales/ (de + en translation.json)
│   │   ├── components/ (layout, shared, ui, OnboardingTour)
│   │   └── pages/ (public, portal, staff, partner, admin, auth)
│   └── public/ (favicon.ico, logo192, logo512, manifest.json)
```

---

## Seed-Zugänge

Entwicklungs- und Seed-Accounts werden über `backend/seed.py` und die Umgebungsvariablen gesteuert.

Wichtig:
- keine Passwörter in Dokumentation oder Repo festhalten
- Seed-Accounts nur über lokale / sichere Env-Konfiguration erzeugen
- produktive Zugangsdaten niemals versionieren

---

## Mocked / Feature-Flagged
- Zahlungsmodul: "in Vorbereitung"
- Preiskalkulator: feature-flagged
- AI-Screening: abhängig von NSCALE_API_KEY

## Offene Punkte (P2/P3 Backlog)
- Payment-Modul Anbindung (P2)
- Erweiterte Suchfilter im Staff-Portal (P2)
- Partner-Provisionsabrechnung (P2)
- PWA-Fähigkeit (P3)
- E-Mail-Benachrichtigungen erweitern (P2)
