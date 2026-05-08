# 20_ai_agent_handover_master.md

## Auftrag

Setze das Projekt **WaytoGermany Platform / Studienkolleg Portal** als gestuftes, rollenbasiertes Hybrid-System um. Dieses Dokument ist die operative Masteranweisung für einen AI-Agenten oder ein Umsetzungsteam.

## Projektziel

Baue eine zentrale Plattform, die den heutigen, stark manuellen Prozess für Leads, Bewerber, Dokumente, Kommunikation, Rechnungen, Aufgaben und Folgeangebote in ein auditierbares, mandantenfähiges System überführt. Die Plattform muss bereits im Kern auf mehrere Geschäftsbereiche vorbereitet sein, auch wenn Release 1 Studienkolleg-first bleibt.

## Verifikationsstatus des Zielbilds

### Verifiziert
- Plattform statt Einzelsite
- Studienkolleg-first-MVP
- Mehrfachzuordnung je Bewerber
- Applicant Portal + Staff/Admin + Partnerrollen
- sichere Dokumentenverwaltung
- Rechnungs-/Zahlungslogik
- Automationen und Reporting
- Multi-Workspace-Konzept
- Supabase/Next.js/RLS-Fit

### Plausibel abgeleitet
- PWA/Mobile Web-App in Release 1, native App später
- n8n ergänzend, nicht als transaktionaler Kern
- MDX-first Content Layer, später optionales CMS
- Sprachschule als erster Ausbau nach Studienkolleg-Core

### Offen / nicht verifiziert
- finale Preise / Refunds / VAT
- finale Kontakt- und Betreiberdaten
- letzte Dokumentenmatrix
- WhatsApp-Budget / Policy
- Agenturhierarchien
- exaktes Calendly-Modell

## Umsetzungsreihenfolge

1. Governance und offene Blocker klären
2. Monorepo / Infrastruktur / CI / Security-Grundlagen
3. Identity / Organizations / Workspaces / Memberships
4. Applications / Pipelines / Audit / Consent / Webhook Storage
5. Lead-Ingest / Duplicate Flow / Assignment
6. Applicant Portal Core
7. Dokumentenprozess
8. Kommunikationshub
9. Rechnungs- und Zahlungsgrundlage
10. Public Website und Content-SOT
11. Agency/Affiliate Ausbau
12. Kurs-/LMS-Layer
13. Härtung / Reporting / Skalierung

## Architekturregeln

1. **Datenbank first.**
2. **RLS first.**
3. **Queue everything** für Prozesse > 2 Sekunden.
4. **No one-off UI.**
5. **Trigger/Aktion/Log/Audit** für jede kritische Automation.
6. **Source of Truth pro Bereich**; keine Parallelführung in Mail/Excel.
7. **Keine Public Documents.**
8. **Keine Claims ohne Scope.**
9. **Keine Preis- oder Rechtsinhalte aus widersprüchlichen Quellen übernehmen.**
10. **Keine Feature-Entwicklung ohne Funnel- und Rollen-Zuordnung.**

## Artefakte, die der Agent erzeugen oder pflegen muss

1. ERD
2. Migrationsdateien
3. RLS-Matrix
4. Auth-Flow-Diagramm
5. API-Spec
6. Automationsliste
7. Template-Verzeichnis
8. Legal-/Commercial Config
9. Testkonzept
10. Release-Checkliste
11. Audit-/Monitoring-Konzept

## Kernobjekte

- organizations
- profiles
- workspaces
- workspace_members
- pipelines
- applications
- documents / document_requests / comments
- conversations / messages
- invoices / transactions
- tasks
- notifications / preferences / templates / logs
- appointments
- audit_logs
- automation_runs
- webhook_events
- user_consents
- affiliate_links / commissions
- courses / enrollments / provider / release_rules

## Qualitätsmaßstab

Ein Arbeitspaket ist nur dann „done“, wenn:
- Rechte korrekt durchgesetzt sind,
- der Flow real nutzbar ist,
- Audit und Logging vorhanden sind,
- Fehlersituationen behandelt werden,
- mobile Nutzung mitgedacht ist,
- Content und Claims freigegeben sind,
- Rollback und Monitoring existieren.

## Projektweite Regeln für den Agenten

### Daten und Sicherheit
- niemals sensible Dokumente öffentlich exponieren
- niemals Rollenlogik nur im Frontend lösen
- niemals Zahlungsstatus ohne Ledger manipulieren
- niemals Webhooks ohne Idempotenz verarbeiten

### Inhalt und Claims
- Admission ≠ FSP-Berechtigung ≠ Uni-Zulassung
- Preise nur aus finalem Config-Stand
- keine Fallbeispiele mit personenbezogenen Daten reproduzieren
- keine Platzhalter-FAQ produktiv übernehmen

### UX
- jeder Screen braucht Hauptaktion
- Applicant mobil priorisieren
- Staff braucht 360°-Profil statt Tool-Hopping
- Multi-Workspace nur sichtbar machen, wenn wirklich vorhanden

### Betrieb
- Mailboxen sind Eingangskanäle, nicht CRM-SOT
- jede Automation loggen
- every failed run sichtbar machen
- Monitoring und Alerts ab MVP

## No-Go-Punkte

1. Start von Payment ohne Commercial/Tax-Klärung
2. Start von Public Pricing mit widersprüchlichen Preisständen
3. produktiver Go-Live ohne RLS-Tests
4. Dokumentenmodul ohne Signed URLs und Policies
5. Messaging ohne Delivery-Status und Fehlernachweis
6. Multi-Workspace ohne saubere Membership-Tabelle
7. harte Kopplung an einzelne Markenangaben, solange Legal/Brand-Hierarchie ungeklärt ist

## Empfohlene Release-Strategie

### Release 1
- Studienkolleg-Core
- Applicant Portal
- Staff/Admin-Kern
- Dokumente
- Rechnung/Zahlung
- Public Core Pages
- Audit/Consent/Webhook Safety

### Release 2
- Sprachschule
- Kurse / Learning Center
- Agency/Affiliate-Ausbau
- Reporting vertiefen

### Release 3
- Pflege / Arbeit / Ausbildung
- White-Label-Erweiterungen
- OCR
- Native App / weitere Kanäle

## Kritische Risiken

1. Scope-Explosion
2. Rechts-/Preiswidersprüche
3. RLS-Komplexität
4. Payment-/Tax-Unklarheit
5. Messaging-Kosten und Fensterlogik
6. fehlende Governance bei Content und Automationen

## Abschlussanweisung an den Agenten

Arbeite in dieser Reihenfolge:
1. Blocker schließen.
2. Architektur und Datenfundament bauen.
3. Rechte und Audit härten.
4. Kernflows real nutzbar machen.
5. Public und Partnerflächen erst auf dieses Fundament setzen.
6. Jeden Schritt mit Test, Nachweis und Freigabe dokumentieren.

Wenn eine Information in den Quellen fehlt oder widersprüchlich ist:
- markiere sie als **offen / nicht verifiziert**,
- blockiere davon abhängige produktive Claims oder Logiken,
- liefere nur die belastbarste, klar gekennzeichnete Empfehlung.
