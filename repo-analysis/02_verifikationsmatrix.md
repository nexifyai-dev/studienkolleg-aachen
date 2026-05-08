# 02_verifikationsmatrix.md

## Verifikationslogik

- **Verifiziert:** ausdrücklich in mindestens einer analysierten Quelle enthalten.
- **Plausibel abgeleitet:** konsistente Schlussfolgerung aus mehreren Quellen und/oder aus den verbindlichen DOS-/Template-Standards.
- **Offen / nicht verifizierbar:** widersprüchlich, unklar oder nicht abschließend spezifiziert.

## Matrix der wichtigsten Projektaussagen

| Aussage | Einstufung | Begründung / Quellenbasis | Konsequenz für die Umsetzung |
|---|---|---|---|
| Das Projekt ist eine zentrale Plattform, nicht nur eine Website. | verifiziert | PRD, Pflichtenheft, Ist-Stand | Architektur als Plattform mit öffentlicher Web-Ebene + operativer Portal-Ebene planen. |
| Aktuell werden ca. 100 Leads pro Tag weitgehend manuell verarbeitet. | verifiziert | PRD, Ist-Stand | Hoher Automatisierungs- und Skalierungsdruck; keine Excel-/Mailbox-First-Architektur zulässig. |
| Ein Bewerber kann in mehreren Geschäftsbereichen parallel aktiv sein. | verifiziert | PRD, Pflichtenheft, Multi-Workspace-Modell | Datenmodell muss Identity und Kontext trennen; kein 1:1-Prozessmodell pro Person. |
| Geschäftsbereiche sind mindestens Studienkolleg, Sprachschule, Pflegefachschule, Arbeit/Ausbildung. | verifiziert | PRD, Pflichtenheft, Ist-Stand | Workspaces / Bereichspipelines als Kernstruktur. |
| Release 1 muss alle vier Bereiche vollständig operativ enthalten. | offen / nicht verifizierbar | Gesamtziel ist breit, MVP im PRD ist Studienkolleg-fokussiert | Architektur für alle Bereiche offen halten, Release 1 aber klar begrenzen. |
| MVP ist Studienkolleg-first. | verifiziert | PRD, Implementation Guide, Step-by-Step Blueprint | Erstes Go-Live auf Kernprozess fokussieren. |
| Applicant Portal muss mobil priorisiert sein. | verifiziert | UX-Architektur, Pflichtenheft | Mobile-first, 375 px als Pflicht-Breakpoint, PWA-fähig. |
| Native Mobile App ist Teil des MVP. | offen / nicht verifizierbar | PRD verschiebt native App auf Phase 2, Pflichtenheft fordert Mobile Web-App früh | PWA/Mobile-Web-App als MVP; native App später. |
| Interne Oberfläche kann deutschsprachig sein, Bewerberzugang mindestens englisch. | verifiziert | Pflichtenheft | i18n-Architektur ab Start. |
| Weitere Sprachen sollen später ergänzbar sein. | verifiziert | Pflichtenheft, Live-Website | Translation Keys und lokalisierbare Content-Struktur zwingend. |
| Öffentliche Claims zu Zulassung/FSP müssen stark eingegrenzt werden. | verifiziert | Fallbeispiele, FAQ, Website, DOS Claims-Policy | Jede Admission-Aussage mit sauberem Scope; keine implizite FSP-Garantie. |
| FSP-Berechtigung wird nicht durch die Schule final entschieden. | verifiziert | operative E-Mail-Fälle, FAQ | Content- und Vertriebslogik müssen dies konsistent kommunizieren. |
| Öffentliche Preislogik ist widerspruchsfrei geklärt. | offen / nicht verifizierbar | FAQ, Styleguide, Website widersprechen sich | Preis-SOT vor Umsetzung fixieren; bis dahin keine harte Preisautomatisierung im Frontend. |
| Öffentliche Rechts- und Kontaktdaten sind konsistent. | offen / nicht verifizierbar | Live-Seiten widersprechen sich | Legal/Privacy/Footer vor Go-Live harmonisieren. |
| Die richtige Kernarchitektur ist Next.js + Supabase + RLS. | verifiziert | PRD, Implementation Guide, DB-Design, DOS | Dieser Stack ist Primärvorschlag. |
| Dokumente dürfen niemals öffentlich sein. | verifiziert | PRD, Template, Pflichtenheft | Private Buckets, Signed URLs, RLS-basierter Zugriff. |
| CRM-SOT ist die Plattformdatenbank, nicht E-Mail oder Excel. | verifiziert | Ist-Stand, Pflichtenheft, Template-Prinzipien | Mailboxen nur Eingangskanäle; kein Parallel-CRM. |
| Agenturen brauchen isolierte Sicht auf ihre Fälle. | verifiziert | PRD, Pflichtenheft, DB-Design | Tenant-/Workspace-Isolation + RLS + Rollen. |
| Affiliates sollen Status und Provisionen nur für eigene Fälle sehen. | verifiziert | Pflichtenheft, PRD | eingeschränktes Portal mit separatem Rechteprofil. |
| RLS-Tests sind Pflicht vor Entwicklungsstart. | plausibel abgeleitet mit starkem Pflichtcharakter | CTO Review fordert pgTAP/RLS-Tests; DOS/Template verlangen serverseitige Rechteprüfung und Auditfähigkeit | Security Gate ohne RLS-Test nicht bestanden. |
| Queueing für Langläufer ist Pflicht. | plausibel abgeleitet | Scalability-Architektur + CTO Review + Implementation Guide | PDF, Webhooks, Provisioning und Massenkommunikation asynchron ausführen. |
| Zahlungslogik braucht Ledger-Modell statt nur paid/unpaid. | plausibel abgeleitet | DB-Design hat transactions, CTO Review fordert Partial/Chargeback-Logik | invoices + transactions + balance-berechneter Status. |
| Teilzahlungen und Steuerlogik sind final definiert. | offen / nicht verifizierbar | ausdrücklich als Risiko offen | Payment-Modul vor Rollout fachlich klären. |
| Kursmodul ist integraler Teil der Plattform und nicht externer Fremdprozess. | verifiziert | Pflichtenheft Zusatzmodul 27, LMS-Architektur | Course booking, release und access direkt im Portal modellieren. |
| Externe LMS-/Meeting-Anbieter können zusätzlich angebunden werden. | verifiziert | LMS-Architektur | Provider-Schicht und Provisioning-Logik vorsehen. |
| System soll audit-proof sein. | verifiziert | Audit- & Compliance-Dokument, DOS/Template | Append-only Audit Logs, Admin Investigation Tool, Nachweisexporte. |
| Consent-Tracking ist bereits vollständig spezifiziert. | offen / nicht verifizierbar | Gap Analysis benennt dies als fehlend | user_consents ins MVP aufnehmen. |
| Interne Notizen und öffentliche Kommentare sind bereits sauber getrennt. | offen / nicht verifizierbar | Gap Analysis benennt fehlende Trennung | Kommentare mit visibility-Feld ins Datenmodell aufnehmen. |
| Knowledge Base / Wissensdatenbank ist optional. | plausibel abgeleitet | fachlich vorgesehen, aber nicht MVP-kritisch für Kernprozess | in IA und Content-System vorsehen; MVP minimal, aber architekturkonform. |
| White-Label Subdomains sind MVP. | verifiziert negativ | PRD verschiebt Subdomains auf Phase 2 | Branding Level 1 im MVP, Subdomains später. |

## Priorisierte Klärungspunkte vor produktiver Umsetzung

### Gate 1 – Muss vor Payment-/Legal-Rollout geklärt sein
1. Preis- und Gebührenmodell.
2. Rechnungs- und Refund-Logik.
3. Steuer- und VAT-Behandlung.
4. Offizielle Rechts- und Kontaktdaten.

### Gate 2 – Muss vor Partner-/Messaging-Skalierung geklärt sein
1. WhatsApp-Budget und Template-Messaging-Policy.
2. Agenturhierarchien und Provisionsmodell.
3. Calendly-/Terminmodell je Team vs. zentral.

### Gate 3 – Muss vor LMS-/Cross-Sell-Rollout geklärt sein
1. finale Kurs-/Prüfungsobjekte,
2. Freigaberegeln je Bereich,
3. externer vs. interner LMS-Anteil.
