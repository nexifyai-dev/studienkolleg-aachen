# 01_quellenregister.md

## Quellenbasis und Verarbeitungsregeln

Dieses Register erfasst alle für das Umsetzungspaket berücksichtigten Quellen. Es trennt zwischen:
- **Verifiziert:** Inhalt liegt in einer analysierten Quelle ausdrücklich vor.
- **Plausibel abgeleitet:** Schlussfolgerung aus mehreren Quellen oder aus den verbindlichen DOS-/Template-Standards.
- **Offen / nicht verifizierbar:** Quelle fehlt, Quellen widersprechen sich oder Detailtiefe reicht nicht aus.

Personenbezogene Fallbeispiele und sensible Betriebsdaten wurden **nur zur Ableitung von Prozesslogik** genutzt und **nicht inhaltlich reproduziert**.

## Vollständige Quellenliste

| Quelle | Typ | Zweck | Relevanz | Status | Enthaltene Anforderungen | Enthaltene Risiken / Konflikte | Betroffene Bereiche |
|---|---|---|---|---|---|---|---|
| Projektprompt.txt | Steuerdokument | definiert Ausgabestruktur, Verifikationslogik und Arbeitspflichten | sehr hoch | verifiziert | 20 Zieldateien, Trennung in verifiziert/abgeleitet/offen, vollständiges Bundle | keine inhaltliche Projektquelle; nur Meta-Vorgabe | gesamtes Paket |
| NeXifyAI_DOS_v1.1_Allgemeine_Agenturvorgaben.pdf | verbindlicher Systemstandard | liefert Guardrails, Funnel-, Copy-, Tech-, QA-, Security-, KPI- und Release-Standard | sehr hoch | verifiziert | Retrieval first, Template first, Tracking first, Quality Gates, Default-Stack, DoD | WCAG im DOS teils 2.1 AA, im Template 2.2 AA; konsolidiert als Mindestziel 2.2-konforme Umsetzung | Strategie, Tech, Content, QA, Security |
| projekt_template_vorlage_nexifyai_standard.md | verbindliche Mastervorlage | liefert Projektprofil, Rollenlogik, Compliance, IA, Datenmodell, Portal-, DMS-, QA- und Release-Template | sehr hoch | verifiziert | Source of Truth, Rollenmatrix, Dokumentlogik, D/A/CH-Standards, Release-Gates | universell formuliert; projektkonkret zu spezifizieren | Governance, IA, Rollen, DMS, QA |
| 01_Product_Requirements_Document.md | PRD | fachliches Zielbild, MVP, Geschäftsbereiche, Zahlungslogik, DMS, Agentur-/Affiliate-Modell | sehr hoch | verifiziert | zentrale Plattform, vier Geschäftsbereiche, RLS, Stripe/PayPal, Signierte URLs, 3-Monats-MVP | offene Punkte bei Migration, Signaturen, WhatsApp-Kosten, Agenturhierarchien | Scope, MVP, Module, Risiken |
| Studienkolleg Ist-Stand und Planung.docx | Ist-Analyse | beschreibt aktuellen Prozess, heutige Tool-Landschaft und Zielbild | sehr hoch | verifiziert | ca. 100 Leads/Tag, manuelle Bearbeitung, kein zentrales CRM, Bewerberportal nötig | bestehende Testlösung ist nicht produktionsintegriert | Discovery, Betriebslogik, Zielbild |
| Neu Pflichtenheft Way.docx | fachliches Pflichtenheft | detailliert Rollen, Prozesse, Bereiche, Dokumente, Kommunikation, Reporting, LMS, White-Label | sehr hoch | verifiziert | Webplattform + Mobile Web-App, Mehrfachzuordnung pro Bewerber, Agenturen, Affiliates, Aufgaben, Reporting, Kursmodul | sehr breiter Sollumfang; nicht alles ist MVP | Gesamtarchitektur, Rollen, Prozesse |
| 06_Implementation_Guide.md | Umsetzungsplan | legt Reihenfolge, Stack und Monorepo-Struktur fest | hoch | verifiziert | Datenbank-first, Supabase, Next.js, Expo, Resend, Twilio, pg_mq | Mobile-App wird später eingeplant; Spannungsfeld zur Mobile-Web-App-Anforderung | Umsetzung, Roadmap, Stack |
| 07_Step_by_Step_Blueprint.md | technischer Blueprint | zerlegt Implementierung in Phasen und Abhängigkeiten | hoch | verifiziert | Tabellenreihenfolge, RLS, Buckets, Edge Functions, Kanban, Stripe-Webhook | Automation Logs noch knapp spezifiziert | Build Order, Kernpfad |
| 03_Database_Entity_Design.md | Datenbankspezifikation | definiert Kernobjekte und RLS-Prinzipien | sehr hoch | verifiziert | organizations, profiles, pipelines, applications, conversations, invoices, transactions, affiliate_clicks | JSONB-Flexibilität kann spätere Filterung erschweren | Datenmodell, Source of Truth, Rechte |
| 08_SQL_Migration_Plan.md | Migrationsplan | definiert technische Reihenfolge der DB-Migrationen | hoch | verifiziert | Enums, Extensions, Tabellenreihenfolge, Indizes, Soft Delete | kein vollständiger RLS-Testplan enthalten | Datenbank, DevOps |
| 10_Critical_Architecture_Review.md | Risiko-Audit | benennt Architektur-, RLS-, Payment-, Automation- und App/Web-Risiken | sehr hoch | verifiziert | RLS-Tests, Queue-Pflicht für Langläufer, Partials/Chargebacks, Steuerlogik, State Machines | explizite Blocker vor Entwicklungsstart | Risiken, Abnahmekriterien |
| 11_Gap_Analysis_Missing_Entities.md | Lückenanalyse | benennt fehlende Entitäten und Subsysteme | hoch | verifiziert | audit_logs, automation_runs, webhook_events, user_consents, internal/public comments | ohne diese Entitäten Black-Box-Risiken und Rechtslücken | Datenmodell, Compliance, Debugging |
| 12_Pre_Development_Checklist.md | Freigabe-Checkliste | definiert Mindestliefergegenstände vor Coding | hoch | verifiziert | ERD, RLS-Matrix, Security-Konzept, API-Spec, Backup-/Deployment-Konzept, Testkonzept | Start ohne diese Artefakte ist nicht freigabefähig | Governance, Projektsteuerung |
| 05_Automation_and_Communication_DeepDive.md | Automations-Pflichtenheft | detailliert Lead-, Dokument-, Status-, Zahlungs- und Reminder-Automation | sehr hoch | verifiziert | Duplicate Check, Welcome Flow, Reminder-Logik, Mahnwesen, Calendly-Sync, Inaktivitätslogik | offene Punkte bei Mahnwesen, WhatsApp-Kosten, Dokumentenmatrix, Storno, Calendly-Modell | Automationen, CRM, Communication |
| 22_Notification_System_Architecture.md | Notification-Architektur | beschreibt Präferenzlogik, Template-Modell und Omnichannel-Router | hoch | verifiziert | notification_preferences, templates, logs, Kanal-Priorisierung, Override für Security/Invoice | Kanal- und Kostensteuerung noch offen zu finalisieren | Kommunikation, UX, Datenmodell |
| 25_Applicant_Portal_UX_Architecture.md | UX/UI-Konzept | definiert Portal-Sitemap, Flows und mobile Prioritäten | hoch | verifiziert | Dashboard, Journey, Learning, Inbox, Settings, Help; Mobile first; Self-Service | LMS teils Phase 2; Applicant-Portal muss trotz Komplexität einfach bleiben | IA, UX, Design |
| 28_Multi-Workspace_Access_Model.md | Access-Control-Architektur | definiert One Identity / Many Contexts | sehr hoch | verifiziert | globale Identity, Workspace-Mitgliedschaften, Kontextwechsel, RLS-Beispiele | höhere Komplexität in RLS und UX | Rollen, RLS, Datenmodell |
| 30_Course_Delivery_Architecture.md | LMS-Zugriffslogik | definiert interne/externe Kursbereitstellung | hoch | verifiziert | interne Videokurse, externe LMS/Zoom-Modelle, Provisioning, Zugangsentzug | Credential-Handling und Provider-Fehler sind sicherheitskritisch | LMS, Automationen, Portal |
| 24_Scalability_Architecture.md | Skalierungsstrategie | beschreibt Serverless-First, Queueing, Storage Tiering, Monitoring | hoch | verifiziert | Supavisor, Read Replicas, Partitionierung, Queue Layer, Caching | bei wachsender Last ohne Partitionierung und Queueing drohen Bottlenecks | Performance, Ops |
| Webseiten.docx / Webseite mit Inhaltsvorgaben inkl..txt | Web-Referenzen | nennen die relevanten Websites | mittel | verifiziert | öffentliche Referenzseiten für Marke und Landingpages | staging/live können voneinander abweichen | Public Web, Content |
| FAQ 2.docx | FAQ- und Vertriebsinhalt | liefert Produkt-, Preis-, Fristen-, Visa- und Refund-Statements | hoch | verifiziert | T/M/W-Kurse, B1-Anforderung, Gebührenmodelle, Unterkunft, Refund-Logik | in sich und gegen andere Quellen teils widersprüchlich; enthält Platzhalter-Fragen | Content, Pricing, Legal Claims |
| Bewerber Fälle_Plattform_2026.docx | operative Falllogik | zeigt reale Entscheidungsbäume ohne Produktarchitektur | hoch | verifiziert | frühe Schulabschlussprüfung, FSP unklar/nicht möglich, Kursreservierung, Statuslogik | personenbezogen; nur abstrahiert nutzbar | CRM, Kommunikation |
| Bewerbung über Kontaktformular / Anfrage Bewerbung (Fallbeispiele) | operative Kommunikationsbeispiele | zeigen reale Antwortlogiken, Claim-Scopes und Zulassungs-/Zahlungsabläufe | hoch | verifiziert | FSP-Entscheidung durch Bezirksregierung, Zahlung vor Admission Letter, Online-Teilnahme im 1. Semester, Unterkunfts-Cross-Sell | personenbezogen; nicht wiederzugeben | CRM, Copy, Legal Claims |
| way_2_germany_styleguide_002_studienkolleg_v1.0.pdf | Styleguide | visuelle Markenbasis | hoch | verifiziert | Farben, Typografie, Logoeinsatz, Beispiele | Preis- und Kontaktangaben widersprechen teils anderen Quellen | Designsystem, Brand |
| Logo-/Asset-Dateien (PDF/PNG/EPS/AI) | Design-Assets | Referenz für Markenarchitektur und Subbrands | mittel | verifiziert | Subbrand-Hinweise zu Studienkolleg, Sprachkurse, Stay in Aachen, Jobs, Uni | keine Textquelle für Geschäftslogik | Branding |
| E-Mail-Adressen um die Logik der Abläufe zu verstehen.txt | sensible Betriebsquelle | zeigt, dass reale Mailprozesse über konkrete Mailboxen laufen | mittel | verifiziert | operative E-Mail-Abhängigkeit | enthält sensible Zugangsinfrastruktur; nicht reproduzieren | Betrieb, Inbox-Integration |
| Öffentliche Website studienkollegaachen.de | Live-Web | validiert öffentliche Kommunikation, Navigation, Kontakt- und Legal-Angaben | hoch | verifiziert | Mehrsprachigkeit, Kursangebote, öffentliche Claims, Footer/Legal/AGB | Widersprüche bei Adresse, Telefon, E-Mail, Preis, Rechtsangaben | Public Web, Legal, Content |
| Öffentliche Staging-Seite way2germany.designschaefer.com | Staging-Web | zeigt Design-/Marken- und Seitencluster-Richtung | mittel | verifiziert | Ökosystem-Navigation (Studienkolleg, Sprachkurse, Stay in Aachen, Jobs, Uni), Calendly CTA | teils repetitive/unstabile Inhalte; nicht als finale Wahrheit nutzbar | IA, Brand, Funnel |

## Zentrale Doppelungen, Lücken und Konflikte

### Verifiziert
1. Das Projektziel ist **nicht** nur eine Website, sondern eine zentrale Plattform mit CRM, Bewerberportal, Agentur-/Affiliate-Bereich, Kommunikationshub, Dokumentenmanagement, Zahlungslogik und Reporting.
2. Das strategische Zielbild ist **multi-domain**; die operative Einführungslogik ist jedoch **Studienkolleg-first / MVP-first**.
3. Rollen, Rechte, RLS, Dokumentensicherheit und Automationen sind keine Zusatzfeatures, sondern Kernanforderungen.

### Plausibel abgeleitet
1. Das Gesamtprojekt braucht **zwei Ebenen**:
   - öffentliche Conversion-Websites / Funnel-Seiten,
   - operative Plattform mit Mandanten-, Workspace- und Rollenlogik.
2. Für den Start ist ein **MVP mit Studienkolleg-Kernprozess** sinnvoll, aber die Daten- und Rechtearchitektur muss ab Tag 1 für weitere Bereiche offen sein.
3. Eine **PWA / Mobile Web-App zuerst, native App später** löst den Widerspruch zwischen „Mobile Web-App sofort“ und „native App später“.

### Offen / nicht verifizierbar
1. **Preislogik:** 5.500 € + 500 € vs. 6.000 € Gesamtpreis vs. 3.500 € + 3.000 € Ratenmodell.
2. **Rechts- und Kontaktdaten:** Theaterstraße 24 vs. Theaterstraße 30–32; unterschiedliche Telefonnummern und E-Mail-Adressen.
3. **FSP-Formulierungen:** öffentliche/operative Kommunikation muss sauber trennen zwischen „registrationsfähig“ und „FSP-berechtigt“.
4. **Steuer-/VAT-Logik, Teilzahlungen, Chargebacks, Stornos** sind für produktive Implementierung nicht abschließend geklärt.
5. **Master-Agentur-Hierarchien**, **Kalenderkonten**, **WhatsApp-Budgetgrenzen** und **finale Dokumentenmatrix pro Pipeline-Stufe** sind offen.

## Reales Projektziel aus allen Quellen

**Verifiziert:** Das WaytoGermany Portal soll die heutige, stark manuelle Lead-, Bewerber-, Dokumenten-, Kommunikations- und Zahlungsbearbeitung in ein zentrales, mandantenfähiges, rollenbasiertes System überführen.

**Plausibel abgeleitet:** Das wirtschaftlich sinnvolle Ziel ist ein skalierbares Plattformfundament, das zuerst den Studienkolleg-Prozess stabilisiert und danach Sprachschule, Pflege, Arbeit/Ausbildung, White-Label-Partner und Kursbereitstellung ohne Neubau erweitert.

**Offen / nicht verifizierbar:** Ob das Gesamtprojekt bereits in Release 1 alle Bereiche vollständig produktiv abdecken soll, ist nicht belastbar bestätigt. Belastbar bestätigt ist nur, dass die Architektur dafür vorbereitet sein muss.
