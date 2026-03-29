# W2G Platform – PRD (Product Requirements Document)

## Projektübersicht
**Plattform:** Studienkolleg Aachen / Way2Germany
**Betreiber:** W2G Academy GmbH, Theaterstraße 30–32, 52062 Aachen
**Typ:** Multi-Tenant Applicant Management Platform
**Stack:** React (Frontend) + FastAPI (Backend) + MongoDB
**Sprachen:** Deutsch (Standard), Englisch (vollständig)

---

## Implementierte Features (Stand 29.03.2026)

### Phase 1–3.7j (Abgeschlossen)
- Öffentliche Website: Homepage, Kurse, Services, Kontakt, Bewerbungsformular
- Cookie-basierte JWT-Authentifizierung (httponly, Secure, SameSite)
- Rollenbasiertes System: superadmin, admin, staff, teacher, applicant, affiliate
- Bewerberportal: Dashboard, Journey/Status, Dokumente, Nachrichten, Finanzen, Einstellungen, Einwilligungen
- Staff-Portal: Dashboard, Kanban, Aufgaben, Nachrichten, Bewerber-Detailseite
- Admin-Portal: Dashboard, Benutzerverwaltung, Audit-Logs
- KI-Screening über NSCall (nscale)
- E-Mail-Versand via Resend
- Datei-Uploads in Nachrichten
- Onboarding-Tour für Bewerber
- Top-Navigation portal-weit
- Bewerbungs-/Registrierungs-Kopplung

### Phase 3.7k (Abgeschlossen – 29.03.2026)
- **i18n Bewerberportal komplett:** Alle Portal-Seiten (Dashboard, Journey, Documents, Messages, Financials, Settings) vollständig DE/EN über t()-Aufrufe
- **Messaging-UI Fix:** Chat bündig oben/unten, Input am Boden verankert, keine toten Flächen (Bewerber + Staff)
- **KI-Prüfung operativ:** Prominenter "KI-Prüfung starten"-Button, "Vorschlag übernehmen" mit echtem Statuswechsel + Audit-Trail
- **SEO:** Alle öffentlichen Seiten mit korrekten Meta-Titeln, Descriptions, OG-Tags, hreflang DE/EN via react-helmet-async
- **Partner-Portal:** Eigenes Portal für Affiliates mit Dashboard, Referrals-Tabelle, Empfehlungslink, Einstellungen
- **Login-Bug Fix:** CORS/Cookie-Problem für Deployment gelöst (relative URLs, Secure=true, SameSite=none)
- **index.html:** "Studienkolleg Aachen – Way2Germany" statt "React App"

---

## Architektur

```
/app/
├── backend/
│   ├── config.py (Env-Config)
│   ├── database.py (MongoDB)
│   ├── deps.py (Auth Dependencies)
│   ├── seed.py (Idempotent Seeding)
│   ├── server.py (FastAPI App)
│   ├── routers/ (auth, users, applications, documents, tasks, messaging, ai_screening, partner, export, followups, etc.)
│   ├── services/ (audit, email, storage, ai, nscale_provider, automation)
│   ├── models/ (schemas.py)
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.js (Routing inkl. HelmetProvider)
│   │   ├── contexts/AuthContext.js
│   │   ├── lib/apiClient.js (relative URLs)
│   │   ├── locales/ (de/translation.json, en/translation.json)
│   │   ├── components/shared/SEOHead.js
│   │   ├── components/layout/ (ApplicantLayout, StaffLayout, AdminLayout, PartnerLayout, PublicNav, PublicFooter)
│   │   ├── pages/public/ (Home, Courses, Services, Contact, Apply, Legal)
│   │   ├── pages/portal/ (Dashboard, Journey, Documents, Messages, Financials, Settings, Consent)
│   │   ├── pages/staff/ (Dashboard, Kanban, Tasks, Messaging, ApplicantDetail)
│   │   ├── pages/admin/ (Dashboard, Users, Audit)
│   │   └── pages/partner/ (Dashboard, Referrals, Link, Settings)
```

---

## Zugangsdaten (Test)

| Rolle      | E-Mail                                | Passwort        |
|------------|---------------------------------------|-----------------|
| superadmin | admin@studienkolleg-aachen.de         | Admin@2026!     |
| staff      | staff@studienkolleg-aachen.de         | DevSeed@2026!   |
| teacher    | teacher@studienkolleg-aachen.de       | DevSeed@2026!   |
| applicant  | applicant@studienkolleg-aachen.de     | DevSeed@2026!   |
| affiliate  | partner@studienkolleg-aachen.de       | DevSeed@2026!   |

---

## Offene Punkte / Backlog

### P2
- Payment-Freischaltung (Zahlungsmodul – aktuell "in Vorbereitung")
- Erweiterte Suchfilter im Staff-Portal
- Preiskalkulator (feature-flagged)

### P3
- PWA-Fähigkeit
- Erweiterte Partner-Statistiken / Provisionsabrechnung

---

## Mocked / Feature-Flagged
- Zahlungsmodul: "in Vorbereitung"
- Preiskalkulator: feature-flagged
- AI-Screening: abhängig von NSCALE_API_KEY
