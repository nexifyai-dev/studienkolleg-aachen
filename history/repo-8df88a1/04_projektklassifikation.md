# 04_projektklassifikation.md

## Projektklassifikation nach DOS

## Projekttyp

### Verifiziert
Hybridprojekt aus:
- Website / Funnel / Landingpages,
- Portal,
- CRM,
- DMS,
- Zahlungs- und Reporting-System,
- Kurs- und Schulungsplattform,
- Agentur-/Affiliate-Modell.

### DOS-Einordnung
- **Primär:** Typ D – Hybrid.
- **Teilweise:** Typ E – Service/Consulting für Beratungs- und Bewerbungsbegleitung.
- **Teilweise:** Typ A – Plattform/SaaS-Logik im operativen System.
- **Teilweise:** Typ F – Plattform/Marketplace-Elemente durch Partner-, Affiliate- und künftig Unternehmens-/Matching-Logik.

## Geschäftsmodell

### Verifiziert
Mehrere Erlös- und Leistungsachsen:
1. Studienkolleg-Programme,
2. Sprachkurse,
3. Prüfungen / Vorbereitung,
4. unterstützende Services (Visa, Unterkunft, Guidance),
5. Partner-/Affiliate-Leadgewinnung,
6. perspektivisch weitere Bildungs- und Vermittlungsleistungen.

### Plausibel abgeleitet
Das Geschäftsmodell ist ein **hybrides Service- und Plattformmodell** mit:
- direkter B2C-Vermarktung an internationale Bewerber,
- indirekter B2B-Akquise über Agenturen/Affiliates,
- späterer B2B2C-Ausweitung über White-Label-Partner.

## B2B / B2C / Hybrid

**Hybrid.**
- **B2C:** Bewerber, Sprachschüler, Kursteilnehmer.
- **B2B:** Agenturen, Affiliates, perspektivisch Unternehmen in Arbeits-/Ausbildungsmodulen.
- **Interner Betrieb:** Staff, Admin, Superadmin.

## Zielmärkte

### Verifiziert
- internationale Bewerber für Deutschland,
- interner Betrieb in Deutschland / D/A/CH-Kontext,
- Partner- und Agenturstrukturen international.

### Plausibel abgeleitet
- primäre Erwerbs- und Kommunikationsmärkte liegen außerhalb Deutschlands,
- rechtlicher und operativer Kern liegt in Deutschland,
- D/A/CH-Konformität betrifft Sprache, Formatierung, Rechts- und Qualitätsmaßstäbe.

## Sprachen

### Verifiziert
- Deutsch intern,
- Englisch mindestens im Bewerberzugang,
- weitere Sprachen erweiterbar,
- Live-Website bereits mehrsprachig.

### Empfehlung
Systemweit i18n-fähig, aber initial in drei Ebenen:
1. **System-Backend / Staff:** Deutsch.
2. **Applicant-Facing Core:** Englisch.
3. **Public Marketing:** vorhandene Sprachen konsolidiert, aber nur mit gepflegtem Inhaltsmodell weiterführen.

## Zielgruppen

### Hauptzielgruppen
1. internationale Studienbewerber,
2. Sprachschüler,
3. Bewerber für Pflege / Arbeit / Ausbildung.

### Nebenzielgruppen
1. Agenturen,
2. Affiliates / Influencer / Vermittler,
3. interne Teams,
4. perspektivisch Unternehmen für Arbeitsvermittlung.

## Rollen / Berechtigungen

### Verifiziert
- superadmin,
- admin,
- staff,
- agency_admin,
- agency_agent,
- applicant,
- affiliate/partner-spezifische Rollen,
- perspektivisch company roles.

### Plausibel abgeleitet
Für Release 1 genügen:
- superadmin,
- admin,
- staff,
- accounting_staff,
- agency_admin,
- agency_agent,
- affiliate,
- applicant.

## Primäre Conversion-Ziele

### Public Web
1. Bewerbungsanfrage,
2. Beratungstermin,
3. Kurs-/Programm-Interesse,
4. qualifizierter Lead,
5. Platzreservierung / Registrierungszahlung.

### Plattform
1. Profilaktivierung,
2. vollständige Datenerfassung,
3. Dokumentenvollständigkeit,
4. Rechnungszahlung,
5. Kursfreischaltung,
6. Statusfortschritt.

## Funnel-Logik

### Public Funnel
Awareness → Vertrauen / Orientierung → Qualifizierung → Kontakt / Bewerbung → Zahlung / Registrierung.

### Operational Funnel
Lead-New → Qualifizierung → Dokumente → Prüfung → Rechnung / Zahlung → Bewerbung / Visum / Kurs → Abschluss / Übergabe / Archiv.

### Cross-Sell-Funnel
Bewerberprofil → Sprachbedarf erkannt → Kursfreigabe / Buchung → Kursnutzung → Prüfung / Nachweis → Rückfluss in Hauptprozess.

## Conversion-Modell

### Verifiziert
- direkte Registrierungs- bzw. Bewerbungsanfragen,
- Rechnung / Payment Request,
- Platzreservierung,
- Beratungs- oder Bewerbungstermine.

### Plausibel abgeleitet
Es gibt **nicht nur eine Conversion**, sondern mehrere kontextspezifische Übergänge:
- Erstkontakt,
- Registrierung,
- Reservierung,
- Kauf / Zahlung,
- Kursbuchung,
- Bewerbungseinreichung.

## Security-/Compliance-Stufe

### Verifiziert
Das Projekt verarbeitet sensible Dokumente, Identitätsdaten, Kommunikations- und Zahlungsdaten.

### Einstufung
**Erhöhter Standard** mit Audit-Ready-Grundlage.

### Begründung
- Mehrmandantenfähigkeit,
- private Dokumente,
- Zahlungsprozesse,
- Rollen-/Freigabelogik,
- personenbezogene Daten,
- rechtlich sensible Kommunikations- und Einreichungsprozesse.

## Review-Tiefe

### Empfohlen
- Standardänderungen: mindestens 1 Reviewer.
- Rechte-, Payment-, Security-, Legal-Änderungen: 2 Reviewer.
- RLS-/Security-Policies: Fachreview + Security Review + Testnachweis.

## KPI-Baseline

### Verifiziert
- Leads/Tag als zentrale Eingangsgröße,
- Status, offene Rechnungen, Zahlungen, Abschlüsse, Mitarbeiterleistung, Agentur-/Affiliate-Performance sind relevante Metriken.

### KPI-Baseline für Start
1. neue Leads pro Quelle / Bereich / Tag,
2. Aktivierungsrate Portalzugang,
3. Dokumentenvollständigkeit,
4. Zeit je Stage,
5. Rechnungs-zu-Zahlungs-Quote,
6. offene Aufgaben je Mitarbeiter,
7. Antwortzeit Kommunikation,
8. Cross-Sell in Sprachkurse,
9. Abschlussquote je Bereich.

## Muss / Soll / Kann

### Muss
- Studienkolleg-Core,
- Applicant Identity + Multi-Workspace-Fähigkeit,
- RLS/RBAC,
- DMS,
- Audit/Logs,
- Rechnungs-/Zahlungsgrundlage,
- Applicant Portal,
- Staff Dashboard,
- rechtssichere Public Pages.

### Soll
- Sprachschule als zweiter Workspace,
- Notification Preferences,
- Affiliate/Agency Dashboards,
- internal/external course release,
- Reporting Exporte,
- PWA-Qualität.

### Kann
- native App,
- OCR,
- White-Label-Subdomains,
- Matching,
- Embassy Monitoring,
- Enterprise-Audit-Archive mit WORM-Storage.

## Klassifikationsfazit

Das Projekt ist **kein klassisches Website-Projekt**, sondern ein **plattformbasiertes Hybrid-System mit mehrstufiger Funnel-, Rollen-, Daten- und Betriebslogik**.  
Die korrekte Struktur ist daher:

- DOS: **Hybrid / Plattform / Service**
- Template: **Öffentlich + Portal + Admin + Mitarbeiter + Dokumente + PDFs + E-Mails + CRM + Bot/Automation**
