# W2G Platform – PRD
# 02.07.2026 | v1.4.3 (Go-Live Ready, KI auf DeepSeek Direct API)

## Finale Production-Domain
https://app.deinstudienkolleg.de — WICHTIG: In den Production-Env-Vars muessen
APP_URL und FRONTEND_URL auf https://app.deinstudienkolleg.de zeigen
(werden fuer Passwort-Reset-/Einladungs-Links in E-Mails verwendet).

## KI-Provider (seit 02.07.2026)
- Text-KI: DeepSeek Direct API (https://api.deepseek.com, model deepseek-chat, DEEPSEEK_API_KEY)
- Vision-KI (Dokumentenanalyse): NSCALE Llama-4-Scout (NSCALE_API_KEY)
- OpenRouter wird NICHT mehr verwendet (Key kann in Prod entfallen)

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
- [ ] **GO-LIVE TODO**: User muss "Save to Github" + "Deploy" ausführen, damit Storage-Fix (emergent default) live ist
- [ ] Google Kalender Integration (P1)
- [ ] Erweiterte Reports (P2)
- [ ] PWA Integration (P3)
- [ ] WhatsApp API Integration (P3)
- [ ] SSR/SEO Optimierung (P3)
- [ ] Kanban-Ansicht zusammenfuehren (P3)

## Go-Live Status (12.05.2026)
- [x] STORAGE_BACKEND Default = 'emergent' (config.py) – Code fertig, Preview verifiziert
- [x] Schutz-Fallback bei fehlendem EMERGENT_LLM_KEY (services/storage.py)
- [x] Admin-Endpoint POST /api/system/seed-demo-data + UI-Buttons in /admin/settings
- [x] Live-DB komplett bereinigt (clean-demo-data ausgeführt 12.05.)
- [x] Preview-DB komplett bereinigt
- [x] Regression-Test bestanden (iteration_107): 25/26 Backend PASS, 100% Frontend PASS, 0 JS-Errors
- [ ] **OFFEN: Live-Deployment ausgeführt** → vom User durchzuführen (`Save to Github` → `Deploy`)
- [ ] **OFFEN: Live-Verifikation** nach Deploy: /api/health soll storage_backend='emergent' zeigen

## Technischer Stack
- Frontend: React + Shadcn/UI + Tailwind
- Backend: FastAPI + MongoDB
- KI: OpenRouter (deepseek/deepseek-v4-flash fuer ALLE Aufgaben)
- Vision: nscale Llama-4-Scout (Dokument-Bildanalyse, separat)
- Payments: Stripe (Live)
- Storage: Emergent Object Storage (persistent, EmergentStorageBackend via integrations.emergentagent.com/objstore)
- E-Mail: SMTP (Strato)

## Datenbank-Collections
- users, applications, conversations, messages
- invoices, user_signatures
- brain_memories, brain_emails
- documents, tasks, followups, settings
