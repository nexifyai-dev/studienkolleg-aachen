# W2G Platform – PRD
# 26.04.2026 | v4.7.0 (Pre-Live)

## Kernprodukt
Voll funktionsfaehiges Full-Stack-CRM fuer das Studienkolleg Aachen (React, FastAPI, MongoDB).
Bewerber-Verwaltung, Kommunikation (Portal/E-Mail/WhatsApp), Dokumenten-Management, Rechnungsstellung, KI-Assistent (Brain).

## Sicherheit
- CSRF Double-Submit Cookie Pattern (e2e aktiv)
- DSGVO-konformer Support-Chat (isolierte Sessions)
- Auth/RBAC auf allen 28 Routern geprueft

## Abgeschlossen
- [x] Frontend CSRF-Token Integration
- [x] Brain Memory System (mem0 + IMAP)
- [x] Premium Design System Upgrade
- [x] Migration S3 -> Local Storage
- [x] Frontend Lazy-Loading
- [x] DSGVO Chat-Isolation
- [x] SMTP-only E-Mail-Versand (Resend deaktiviert)
- [x] Dashboard Reporting Fix
- [x] Invoice Creation Bug Fix (amount auto-calc, due_date default +30d)
- [x] KI-Mail-Text-Generierung mit Template-Kategorien
- [x] Einklappbare Signatur im Messaging
- [x] Pro-Mitarbeiter-Signaturen (DB-basiert)
- [x] E-Mail Vorlagen perfektioniert (8 Kategorien, Auto-Sprache, Bewerber-Kontext)
- [x] LLM-Konsolidierung: alle KI-Flows auf deepseek/deepseek-v4-flash via OpenRouter (26.04.2026)
- [x] Vercel-Deployment Vorbereitung: api/index.py + vercel.json (26.04.2026)
- [x] Custom-Domain Setup: studienkolleg.nexifyai.de (Cloudflare Proxy)
- [x] PDF-Vorschau-Fix (26.04.2026): Security-Headers-Middleware in backend/server.py
      verwendet `Content-Security-Policy: frame-ancestors *` fuer
      /documents/, /invoices/, /applications/, /messages/ Pfade statt
      X-Frame-Options: DENY. Andere Endpoints behalten DENY.
- [x] Pre-Live Cleanup (26.04.2026): backend/scripts/clean_demo_data.py
      Entfernte 18 Mock-Bewerber, 20 Apps, 16 Demo-Invoices,
      183 Messages, 153 Notifications, 99 Activities, 40 Tasks,
      61 AI-Screenings, 17 Termine, 12 Documents, audit_logs (3139),
      background_jobs (59), counters reset.
      Behalten: 5 Dev-Accounts, workspaces, settings, anabin_knowledge (82),
      brain_emails (146 echte IMAP), brain_memories (4).

## E-Mail Template-Kategorien
- documents_request: Unterlagen anfordern
- status_update: Status-Update
- appointment: Termin
- offer: Zusage
- rejection: Absage
- payment_reminder: Zahlungserinnerung
- welcome: Willkommen
- follow_up: Nachfrage
- (frei formulieren): Ohne Vorlage

## Verbleibend
- [ ] Google Kalender Integration (P1)
- [ ] Erweiterte Reports (P2)
- [ ] PWA Integration (P3)
- [ ] WhatsApp API Integration (P3)
- [ ] SSR/SEO Optimierung (P3)
- [ ] Kanban-Ansicht zusammenfuehren (P3)
- [ ] Dokumentation (README, CHANGELOG, ADRs)
- [ ] Backend-Tests (pytest)

## Technischer Stack
- Frontend: React + Shadcn/UI + Tailwind
- Backend: FastAPI + MongoDB
- KI: OpenRouter (deepseek/deepseek-v4-flash fuer ALLE Aufgaben)
- Vision: nscale Llama-4-Scout (Dokument-Bildanalyse, separat)
- Payments: Stripe (Live)
- Storage: Lokal (/app/storage)
- E-Mail: SMTP (Strato)

## Datenbank-Collections
- users, applications, conversations, messages
- invoices, user_signatures
- brain_memories, brain_emails
- documents, tasks, followups, settings
