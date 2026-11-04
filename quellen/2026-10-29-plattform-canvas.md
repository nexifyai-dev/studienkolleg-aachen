# Master-Canvas & Soll-Konzept: Digitale Campus-, Healthcare- und SaaS-Plattform

**Projekt:** Studienkolleg Aachen (`studienkolleg-aachen.de` / `studienkollage-aachen.de`) – basierend auf und migriert von `https://deinstudienkolleg.de`
**Trägergesellschaft & Sitz:** W2G Academy GmbH (Way2Germany / Stay in Aachen), Theaterstr. 30–32, 52062 Aachen (Amtsgericht Aachen HRB 23610)
**Betreibermodell:** Eigenstandort Aachen, kooperative Partnerstandorte (Franchise/Lizenz) sowie externes B2B-White-Label-SaaS (für fremde Pflegeschulen und Arbeitgeber im Gesundheitswesen).
**Umfang:** Vollintegriertes Core-ERP (40+ Module), Designsystem-Adaption von `deinstudienkolleg.de`, Hybride Domain- & Koexistenz-Architektur (`prev.studienkolleg-aachen.de` -> `studienkolleg-aachen.de`), Twenty CRM als Single-Source-of-Truth, BigBlueButton (BBB) OSS-Videokonferenz-Cluster, integrierte Cloud-Drive-Speicherlösung, KI-Admissions & Anabin-Engine, Sprachschule, Wohnungsportal, Affiliate-Ökosystem, Digitale Pflegeschule (PflBG/AZAV), Reverse-Recruiting Job-Portal sowie Voll-SEO, AI-SEO (GEO/LLMO), Google-Stack & First-Party-Besuchertracking.
**Version:** 13.0 (Vollständige, ungekürzte Gesamtspezifikation)

---

## 1. Systemarchitektur, Plattform-Ökosystem, Domain-Koexistenz & Designsystem

Das System vereint acht vernetzte Plattformen sowie eine eigene Videokonferenz- (BigBlueButton) und Cloud-Drive-Infrastruktur auf Basis einer einzigen Codebasis und einer zentralen API-Steuerung. Es ist von Grund auf als echtes Multi-Tenant-System (Mandantenfähigkeit mit strikter Datenbank-Isolierung) konzipiert.

### 1.1 Referenz-Basis `https://deinstudienkolleg.de`, Domain-Strategie & Ablösung des Vertriebsportals

Als verbindliche visuelle, strukturelle und inhaltliche Ausgangsbasis für den Auf- und Ausbau der gesamten Plattform dient der bestehende Webauftritt unter **`https://deinstudienkolleg.de`** (W2G Academy GmbH, Theaterstr. 30–32, 52062 Aachen). Für die Migration, Koexistenz und den Rollout gilt folgende strikte Architektur-Vorgabe:

1. **Erhalt des bestehenden Bestandsportals (`deinstudienkolleg.de` ab Login):**
   * Das bisherige Portal auf der Domain `https://deinstudienkolleg.de`, welches **ab dem Login-Bereich ("Sign In")** beginnt, bleibt für bestehende Prozesse und Bestandsnutzer unangetastet erhalten.
   * Im Header der neuen Plattform kann bei Bedarf eine intelligente Login-Weiche (Legacy-Auth-Bridge) integriert werden, die Bestandsnutzer nahtlos auf das bestehende Portal unter `deinstudienkolleg.de` routet, während alle neuen Jahrgänge, Bewerber und Standorte im neuen System arbeiten.
2. **Vollständige Ablösung des bisherigen Vertriebsportals (ab Bewerberformular):**
   * Das bisher an `deinstudienkolleg.de` angeschlossene **Vertriebsportal**, welches ab dem Online-Bewerbungsformular (*"Apply Now" / "Bewerbung starten"* und *"Book Free Consultation" / "Beratung buchen"*) greift, wird **vollständig durch die neue Lösung (Next.js-Bewerber-Funnel + KI-OCR-Anabin-Pipeline + Twenty CRM) ersetzt**.
   * Sämtliche neuen Leads, Beratungsbuchungen und Dokumenten-Uploads fließen ab Tag 1 ausschließlich in die neue Systemarchitektur.
3. **Zweistufige Domain- & Staging-Strategie (`prev.` -> Produktion):**
   * **Phase 1 (Aufbau, Integration & Abnahme – Staging):** Die gesamte neue Webseite sowie alle neuen Portale, Dashboards, KI-Pipelines, BigBlueButton- und Drive-Integrationen werden zunächst vollständig unter der Preview-Subdomain **`https://prev.studienkolleg-aachen.de`** (sowie analog gespiegelt auf `https://prev.studienkollage-aachen.de`) aufgebaut, mit Echtdaten-Szenarien getestet und durch die Geschäftsführung abgenommen. Auf der Preview-Umgebung verhindert ein `X-Robots-Tag: noindex, nofollow`-Header eine vorzeitige Indexierung während der Testphase.
   * **Phase 2 (Produktiver Go-Live / Cut-over):** Nach finaler Abnahme erfolgt der Zero-Downtime-Umzug der neuen Seiten und Portale auf die Hauptdomain **`https://studienkolleg-aachen.de`** (mit permanenter `301`-Weiterleitung der Tippfehler-Domain `https://studienkollage-aachen.de` auf die kanonische Hauptdomain).

### 1.2 Verbindliches UI/UX-Designsystem (abgeleitet aus `deinstudienkolleg.de` & DIN EN ISO 9241)

Das Designsystem von `https://deinstudienkolleg.de` wird extrahiert, in ein zentrales **Figma- & Tailwind-CSS-Design-Token-System** überführt und verbindlich auf alle 8 Plattformen (Webseiten, Studierenden-Portal, B2B-Arbeitgeber-Portal, Admin-Dashboards und Flutter-Apps) ausgerollt:

* **Marken- & Content-Architektur von `deinstudienkolleg.de`:**
  * Übernahme und Ausbau der klaren, vertrauensbildenden Struktur der bestehenden Seite: Hero-Sektion (*"Your Path to Germany – clear, digitally guided"*), Kennzahlen-Trust-Bar ($4,9 / 5$ Bewertung, $2.800+$ Absolventen, $45+$ Länder, $94\%$ Bestehensquote), Leadership-Sektion (Laura Saboor – Managing Director, Way2Germany), authentische Campus-Life-Einblicke, vertikale **Short-Video-Reels** (*"Studienkolleg Up Close"*: W-Kurs, M-Kurs, Student Stories, Dormitory Tour Aachen, FSP Explained), der 4-Schritte-Prozess (*01 Apply Online -> 02 AI Document Review -> 03 Start Your Course -> 04 Begin Your Studies*), verifizierte Google-Bewertungen und interaktive FAQs.
  * **Nativ integrierte 8-Sprachigkeit im Header-Switcher:** Analog zu `deinstudienkolleg.de` unterstützen alle öffentlichen Seiten und Portale ab Werk die acht Kernsprachen **Deutsch (DE), Englisch (EN), Arabisch (AR – inkl. vollwertigem RTL-Layout), Russisch (RU), Ukrainisch (UK), Spanisch (ES), Französisch (FR) und Italienisch (IT)**, ergänzt um Chinesisch (ZH) und Türkisch (TR).
* **Einheitliche, normgerechte Dashboard-Gestaltung (DIN EN ISO 9241-110 & -210):**
  * Sämtliche Dashboards (Master Admin, School Admin, Studierenden-Portal, Dozenten-Portal, B2B-Arbeitgeber-Dashboard, integriertem Drive- und BigBlueButton-UI) folgen denselben visuellen und ergonomischen Prinzipien der **DIN EN ISO 9241-110 (Grundsätze der Dialoggestaltung)**: *Aufgabenangemessenheit, Selbstbeschreibungsfähigkeit, Erwartungskonformität, Fehlertoleranz, Steuerbarkeit und Individualisierbarkeit*.
  * **Visuelle Hierarchie & Layout-Raster:** 12-Spalten-CSS-Grid mit konsistentem 8px-Spacing-System, ruhiger Bento-Grid-Kartenoptik für KPIs, klarer Farbcodierung für Status-Ampeln (Grün = Erledigt/Anabin-Match, Gelb = In Prüfung/Fristwarnung, Rot = Handlungsbedarf/Fehlzeitenkritisch), einheitlicher Typografie-Skala, schattenarmen High-Contrast-Oberflächen sowie durchgängigem Light- und Dark-Mode.
  * **Barrierefreiheit nach DIN EN 301 549 & BFSG:** Alle Formulare, Tabellen, Drive-Ordnerbäume und Video-Räume erfüllen das Kontrastverhältnis von mindestens $4,5:1$ (WCAG 2.1 AA), besitzen vollständige `aria-*`-Attribute und sind komplett per Tastatur bedienbar.

### 1.3 Die 8 vernetzten Plattformen des Ökosystems

1. **Master Admin Panel (SaaS- & Träger-Steuerung - Laravel):**
   * Zentrale Konsole für die Geschäftsführung der W2G Academy GmbH / Studienkolleg Aachen.
   * Globale Steuerung aller Standorte (Eigenstandort Aachen, Partnerstandorte, externe White-Label-Pflegeschulen).
   * Verwaltung von Abonnement-Plänen (Prepaid/Postpaid, Abrechnung pro Schüler/Personal), kostenpflichtigen Add-ons, Custom Domains, globalen Umsatzberichten, BigBlueButton-Cluster-Auslastung, Cloud-Drive-Speicherquoten und System-Health-Metriken.
   * Vollautomatisches Tenant-Onboarding: Ein Provisionierungs-Skript generiert bei Registrierung einer neuen Partnerschule vollautomatisch ein isoliertes PostgreSQL-Datenbank-Schema, dedizierte S3/R2-Storage-Buckets, eine isolierte Cloud-Drive-Instanz (Groupfolder/Tenant), einen eigenen Twenty CRM Workspace sowie die Subdomain-Routings.

2. **Campus / School Admin Panel (Standort-ERP - Laravel):**
   * Isoliertes ERP-Backend für die operative Leitung eines einzelnen Standorts (Aachen, Partnerstandort oder fremde Pflegeschule).
   * Beinhaltet den Setup-Wizard, granulare Rollen- und Berechtigungssteuerung (RBAC), Massen-Import/Export (CSV/Excel) und Zugriff auf alle 40+ Verwaltungsmodule.

3. **Studierenden-, Schüler- & Angehörigen-App (Flutter - iOS & Android):**
   * Zwei Rollen-Ansichten in einer App (Studierende/Schüler sowie optional Eltern/Bürgen bei Minderjährigen mit Multi-Child-Switcher).
   * Funktionen: Echtzeit-Stundenplan (inkl. 1-Klick-Beitritt zu BigBlueButton-Live-Klassen), integrierter **persönlicher Cloud-Drive-Dateimanager**, Hausaufgaben-Upload, Online-Prüfungen, Noten & Zeugnisse, digitales Schülertagebuch, Urlaubsanträge, Online-Gebührenzahlung via Revolut, Visa-Tracker, Live-Bus-/Shuttle-Tracking und Job-Portal-Matching-Anfragen (für Pflegeschüler).

4. **Dozenten- & Personal-App (Flutter - iOS & Android):**
   * Mobile Arbeitsumgebung für festangestellte Lehrkräfte, Honorardozenten und Verwaltungsmitarbeiter.
   * Funktionen: QR-Code-basierte Zeiterfassung am Campus, Starten/Steuern von BigBlueButton-Unterrichtsräumen, digitale Klassenbuchführung (Anwesenheiten), Hausaufgabenvergabe und -benotung, Noteneintragung (Marks Register), Direkt-Synchronisation von Unterrichtsmaterialien über das **Cloud-Drive**, Einreichen von Urlaubsanträgen, Abruf von Gehalts-/Honorar-Abrechnungen (Payslips) und 1-zu-1-Chat.

5. **Praxisanleiter-App (Flutter - iOS & Android - Spezial-App für Krankenhäuser):**
   * Extrem schlanke Mobile-App für externe Praxisanleiter in kooperierenden Krankenhäusern und Pflegeheimen.
   * Ermöglicht das sekundenschnelle Scannen eines QR-Codes auf dem Smartphone des Pflegeschülers, um absolvierte Praxisstunden, Pflicht-Anleitungsstunden und Kompetenznachweise im digitalen Ausbildungsnachweis (E-Logbook) rechtskonform (eIDAS) gegenzuzeichnen.

6. **Studierenden- & Kandidaten-Web-Portal (Next.js):**
   * Vollwertige Desktop-Oberfläche im einheitlichen Designsystem von `deinstudienkolleg.de` für Studierende, Sprachschüler, Mieter und externe Jobsuchende.
   * Umfasst das neue digitale Bewerbungs-Dashboard (welches das alte Vertriebsportal ablöst), die eingebettete **BigBlueButton-Lernumgebung**, das persönliche **Cloud-Drive ("Meine Dokumente & Kursmaterialien")**, Online-Klausuren, Gebührenhistorie, Mietvertragsverwaltung und das Kandidaten-Profil für das Healthcare Job-Portal.

7. **B2B Arbeitgeber- & Agentur-Portal (Next.js):**
   * Dediziertes Web-Dashboard für Krankenhäuser, Pflegeheime und medizinische Einrichtungen (sowie ein separates B2B-Subportal für internationale Bildungsagenturen zur Einreichung von Bewerbern).
   * Ermöglicht Krankenhäusern das Schalten von Stellenanzeigen, das Filtern in anonymisierten Bewerber-Pools (Active Sourcing / Reverse Recruiting), das Auslösen von Match-Anfragen, die Durchführung von **BigBlueButton-Video-Interviews** direkt im Browser und die Verwaltung der B2B-Abonnements.

8. **Multi-Site CMS & SaaS-Landingpages (Next.js / Laravel):**
   * Öffentliche, 8+ sprachige Website für `studienkolleg-aachen.de` (zuvor Staging auf `prev.studienkolleg-aachen.de`) im weiterentwickelten Design von `deinstudienkolleg.de` inkl. Direktbuchungsstrecken für die Sprachschule, dem öffentlichen Wohnungsportal, der Service-/Affiliate-Unterseite, dem Knowledge-Center (Blog/Wiki für SEO & AI-SEO), dem Beratungs-Buchungstool (*"Book Free Consultation"* mit automatischem BigBlueButton-Raumlink) und dem neuen Online-Bewerbungsfunnel (*"Apply Now"*).
   * Jeder Partnerstandort und jede White-Label-Pflegeschule erhält auf Wunsch eine eigene, SEO-optimierte Website unter eigener Custom Domain.
   * Separate B2B-SaaS-Landingpage zur Vermarktung der Plattform an externe Pflegeschulen und Arbeitgeber inkl. Self-Service-Registrierung und Preisrechner.

### 1.4 Dedicated School Apps Add-on (White-Label App-Generator)

* Für Partnerstandorte und externe Pflegeschulen bietet das System im Master Admin Panel einen automatisierten Build-Service (CI/CD via Fastlane/Codemagic).
* Aus einer einzigen Flutter-Codebasis werden vollautomatisch komplett eigenständige Apps (APK/AAB für Google Play Store, IPA für Apple App Store) für den jeweiligen Mandanten kompiliert.
* Individualisierbar pro Mandant: Eigener App-Name, eigene Package-ID (z. B. `de.pflegeschule-muster.app`), eigenes App-Icon, Splash-Screen, eigene CI-Theme-Farben und eigenes Firebase-Projekt.
* Fest einprogrammierter School-Code (kein manuelles Eingeben eines Schul-Codes beim Login nötig).
* Build-Tracking im Master Admin von "Pending" über "In Review" bis "Published" inkl. automatischem Lizenz-Killswitch (App sperrt den Zugriff automatisch, falls das SaaS-Abonnement der externen Schule nicht bezahlt wird).

### 1.5 Twenty CRM als zentrale "Single-Source-of-Truth"

* Vollständige Integration von **Twenty CRM** (Self-Hosted, Open-Source, Node.js/TypeScript/PostgreSQL) über dessen native GraphQL-API und bidirektionale Webhooks.
* Alle externen und internen Kontakte werden primär in Twenty CRM als Custom Objects geführt:
  * **B2C-Objekte:** Interessenten (Leads inklusive vollständiger Besuchertracking-Historie, UTM-Parametern und GCLID), Beratungs-Termine, Sprachschüler, Studienkolleg-Bewerber, immatrikulierte Kollegiaten, Pflegeschüler, Wohnungsmieter, Alumni und externe Pflege-Jobsuchende.
  * **B2B-Objekte:** Internationale Bildungsagenturen (mit Provisions-Tracking), Partnerstandorte, Kooperationskrankenhäuser (Praxisträger), B2B-Arbeitgeber (Job-Portal-Kunden) und White-Label-Pflegeschulen.
* **Event-Driven Automation:** Jede Statusänderung einer Pipeline-Stage in Twenty CRM (z. B. Wechsel von *"Dokumente in Prüfung"* auf *"Zugelassen"* oder von *"Sprachkurs B2"* auf *"C1 Bestanden"*) feuert einen Webhook an das Laravel Core-ERP und löst dort deterministische Geschäftsprozesse aus (Account-Erstellung, automatische Provisionierung der persönlichen Cloud-Drive-Ordnerstruktur, Rechnungsstellung via Revolut, Freischaltung der Wohnungsbuchung, Versand des Welcome-PDFs).

---

## 2. Die 40+ Core-ERP-Module im Detail (Basis-Substanz)

Alle Grundfunktionen sind nativ im Laravel-ERP und den angeschlossenen Portalen verankert und lassen sich im Master Admin pro Standort oder Abo-Plan granular aktivieren oder als kostenpflichtiges Add-on freischalten:

### 2.1 Akademisches Management & Kursbetrieb

* **Spezifische Kursstrukturen:** Native Abbildung der Studienkolleg-Schwerpunktkurse (T-Kurs für Technik/Naturwissenschaften, W-Kurs für Wirtschaft, M-Kurs für Medizin/Biologie, G-Kurs für Geisteswissenschaften), der Sprachschul-Stufen (A1, A2, B1, B2, C1, DSH/TestDaF) sowie der Klassenverbände der generalistischen Pflegeausbildung.
* **Fächer- & Lehrplan-Engine (Syllabus):** Verwaltung von Pflicht- und Wahlfächern, Unterrichtseinheiten (Lessons), Lernthemen (Topics) und strukturierten Lehrplänen pro Semester oder Ausbildungsjahr.
* **Intelligenter Stundenplan-Generator (Timetable Builder):** Drag-and-Drop- sowie algorithmische Erstellung von Stundenplänen mit automatischer Konflikterkennung bei Raum-, Dozenten- oder Klassenüberschneidungen. Jede Unterrichtseinheit kann als *"Präsenz (Campus Aachen)"*, *"Online-Live (BigBlueButton)"* oder *"Hybrid (Smartboard + BigBlueButton)"* klassifiziert werden. Echtzeit-Push-Benachrichtigung bei kurzfristigen Raum- oder Zeitenwechseln.
* **Lernmaterial-Management (Drive-gekoppelt):** Zentraler Upload und versionierte Bereitstellung von Skripten, PDFs, Videos und Vorlesungsfolien pro Kurs und Unterrichtseinheit, direkt synchronisiert mit dem integrierten Cloud-Drive-Speicher der jeweiligen Klasse.
* **Versetzungs- & Transfer-Logik (Promotion & Transfer):** Automatisierte Workflows für den Aufstieg in das nächste Semester (z. B. vom 1. ins 2. Semester Studienkolleg, von B2 nach C1 oder zwischen Ausbildungsjahren) sowie standortübergreifende Transfers inkl. automatischer Anpassung der Cloud-Drive-Gruppenberechtigungen.

### 2.2 Prüfungswesen, Benotung & Zertifizierung

* **Online-Prüfungssystem (Online Exams):** Durchführung von digitalen Einstufungstests und Klausuren (Multiple-Choice und Freitext) im Browser oder in der App. Inklusive umfangreicher Fragendatenbank (Question Bank), CSV-Massen-Upload von Fragen, Festlegung von Schwierigkeitsgraden, Zeitlimits, zufälliger Fragen- und Antwortreihenfolge (Anti-Cheating), optionalem **Live-Proctoring via BigBlueButton-Webcams** sowie Screen-Recording-/Screenshot-Sperre in den Apps.
* **Offline-Prüfungen & Klausurverwaltung:** Planung von Präsenzklausuren, Vorprüfungen (Mock-Exams), der staatlichen Feststellungsprüfung (FSP) und des Pflege-Staatsexamens inkl. Raum- und Aufsichtsplanung sowie Massen-Notenimport via CSV.
* **KI-gestützte Vorkorrektur:** Bei digitalen Aufsätzen (z. B. im Fach Deutsch oder bei FSP-Übungsaufsätzen) führt ein LLM-Modul eine automatische Vorab-Analyse hinsichtlich Grammatik, Orthografie, Ausdruck, Struktur und Wortanzahl durch und schlägt dem Dozenten eine Bewertung nach dem hinterlegten Erwartungshorizont vor.
* **Dynamische Zeugnis- & Zertifikats-Engine:** Automatische Berechnung von Gewichtungen, Durchschnittsnoten und Bestehensregeln. Generierung von druckfertigen PDF-Leistungsnachweisen, Teilnahmezertifikaten, Sprachdiplomen und FSP-Zeugnissen, die automatisch im persönlichen Cloud-Drive-Tresor des Studierenden abgelegt werden.
* **Kryptographische Echtheitsprüfung:** Jedes generierte Zertifikat und jeder Studentenausweis erhält einen individuellen, kryptographisch signierten QR-Code. Behörden, Universitäten und Botschaften können das Dokument durch Scannen des Codes direkt unter `verify.studienkolleg-aachen.de` auf Echtheit und Unversehrtheit prüfen.

### 2.3 Finanzen, Gebühren & Buchhaltung (ERP-Seite)

* **Gebühren-Matrix (Fee Structures):** Flexible Anlage beliebiger Gebührenarten (Bewerbungsgebühr, Semestergebühren ab $3.500\text{ EUR}$, Sprachkurs-Pakete ab $1.200\text{ EUR}$, Prüfungsgebühren, Kaution, Warmmiete, Lehrmaterialpauschalen) zuweisbar nach Kurs, Standort oder individuellem Studierenden.
* **Ratenzahlungs-Engine (Installments & Partial Payments):** Individuelle oder standardisierte Ratenpläne (z. B. 3 oder 6 Raten pro Semester) inkl. automatischer Mahnläufe, Verzugszinsen-Berechnung und Teilzahlungsverfolgung.
* **Rabatte & Stipendien (Fee Relief / Concessions):** Hinterlegung von prozentualen oder absoluten Gebührenermäßigungen (z. B. Geschwisterrabatt, Frühbucherrabatt, Stipendien oder Agentur-Sonderkonditionen).
* **Automatisierte Portal-Restriktionen bei Zahlungsverzug:** Ist eine fällige Rate trotz Mahnung um mehr als $X\text{ Tage}$ überfällig, sperrt das System automatisch definierte Funktionen im Studierenden-Portal und Cloud-Drive (z. B. den Download von Immatrikulationsbescheinigungen für die Ausländerbehörde, die Einsicht in Klausurergebnisse oder die Anmeldung zur FSP), bis der Zahlungseingang verbucht ist.
* **Einnahmen- & Ausgaben-Ledger:** Vollständiges Kassenbuch zur Erfassung sämtlicher operativer Standort-Ausgaben, Kassenbelege, manueller Bar-/Scheckzahlungen und Banktransaktionen.

### 2.4 Personalwesen (HR), Dozenten & Abrechnung (Payroll)

* **Digitale Personalakte:** Verwaltung von festangestellten Lehrkräften, freien Honorardozenten, Praxisanleitern und Verwaltungspersonal inkl. Hinterlegung von Verträgen, akademischen Abschlüssen, BAMF-/AZAV-Zulassungen und Lehrbefähigungen im geschützten HR-Drive.
* **QR-Code- & BigBlueButton-Zeiterfassung:** Dozenten scannen bei Präsenz-Unterrichtsbeginn und -ende über die Staff-App einen dynamischen QR-Code am Campus-Terminal. Bei Online-Unterricht über BigBlueButton erfasst das System die exakte Moderator-Session-Zeit vollautomatisch per Webhook. Die erfassten Nettostunden werden automatisch mit dem Stundenplan abgeglichen.
* **Gehalts- & Honorarabrechnung (Payroll):** Abbildung fester Gehaltsstrukturen (inkl. Zulagen/Allowances und Abzügen/Deductions) für Angestellte sowie stundengenauer Honorarabrechnungen für Freiberufler. Automatische Generierung monatlicher Gehaltsabrechnungen / Honorargutschriften (Payslips) in der Dozenten-App und im persönlichen Mitarbeiter-Drive-Ordner.
* **Urlaubs- & Vertretungsmanagement:** Digitaler Workflow für Urlaubsanträge und Krankmeldungen von Dozenten. Bei Genehmigung markiert das System betroffene Unterrichtsstunden sofort als "Vertretung erforderlich" und schlägt verfügbare Fachkollegen vor.
* **DATEV-Schnittstelle:** Direkter Export aller Lohn-, Gehalts-, Honorar- und Ausbildungsvergütungsdaten sowie aller Debitoren-/Kreditorenbuchungen im zertifizierten DATEV-Format (DATEV XML / Buchungsstapel) an den Steuerberater.

### 2.5 Transport, Shuttle-Service & Ankunfts-Logistik

* **Flughafen-Pick-up-Management (Arrival Service):** Internationale Studierende können vor ihrer Einreise im Portal einen Abholservice (z. B. ab Flughafen Frankfurt, Düsseldorf oder Köln/Bonn nach Aachen) buchen und via Revolut bezahlen. Dispositions-Modul für Fahrer, Fahrzeuge und Sammeltransporte bei Gruppenankünften.
* **Campus-Shuttle & Bus-Tracking:** Verwaltung von festen Busrouten, Haltestellen, Fahrzeugen und Fahrern (z. B. Pendelbusse zwischen Wohnheimen, Campus Theaterstr. 30–32 und Kooperationskrankenhäusern).
* **Live-GPS-Timeline:** Studierende sehen in der App die exakte Live-Position des Shuttles auf einer Fahrt-Timeline und erhalten Push-Benachrichtigungen, sobald das Fahrzeug $5\text{ Minuten}$ von ihrer Haltestelle entfernt ist. Inklusive digitaler Transport-Anwesenheitsberichte.

### 2.6 Kommunikation & Studierenden-Betreuung

* **Echtzeit-Chat (1-zu-1 & Gruppen):** Integriertes Messaging-System (Web & Mobile auf Basis von Laravel Reverb WebSockets) für die direkte, DSGVO-konforme Kommunikation zwischen Studierenden, Dozenten, Wohnheimverwaltung und Sekretariat (inkl. direktem Teilen von Dateien aus dem Cloud-Drive und Starten spontaner BigBlueButton-Calls).
* **Multi-Channel-Alerts:** Orchestrierung von Nachrichten über Push-Benachrichtigungen (Firebase FCM), E-Mail-Templates und die **WhatsApp Business API** (z. B. automatische WhatsApp-Warnung bei unentschuldigtem Fehlen im Unterricht oder fälliger Miet-/Gebührenrate).
* **Digitales Schwarzes Brett (Notice Board) & Event-Kalender:** Standort- oder kursspezifische Ankündigungen für Exkursionen, Workshops (z. B. *"Wichtige Dokumente für dein Studium"*, *"Das deutsche Gesundheitssystem"*), Prüfungstermine, Feiertage und Fristen der Ausländerbehörde.
* **Digitales Studierendentagebuch (Student Diary):** Dokumentation von individuellen Betreuungsgesprächen, Lernfortschritten und disziplinarischen Vermerken.

### 2.7 Dokumenten-Engine & System-Administration

* **Dynamischer ID-Card-Generator:** Automatische Erstellung von druckfertigen und digitalen Studierenden- und Mitarbeiterausweisen mit Foto, Matrikelnummer, Gültigkeitsdauer und Verifikations-QR-Code (inkl. Bulk-Image-Upload).
* **Sicherheit & Lokalisierung:** Rollenbasierte Zugriffskontrolle (RBAC) bis auf Feldebene, verpflichtende Zwei-Faktor-Authentifizierung (2FA) für Admins und Dozenten, Cloudflare Turnstile / reCAPTCHA Schutz, vollständige Mehrsprachigkeit (DE, EN, AR, RU, UK, ES, FR, IT, ZH, TR) inklusive nativer RTL-Unterstützung (Right-to-Left) und Dark Mode im Admin-Panel.

---

## 3. Vollintegrierte BigBlueButton (BBB) OSS-Videokonferenz- & Drive-Onlinespeicher-Architektur

Um den Präsenz-, Hybrid- und Online-Unterricht, die Studienberatung sowie die gesamte Dokumenten- und Medienverwaltung ohne Abhängigkeit von US-Cloud-Konzernen (wie Zoom oder Google Drive) zu $100\%$ DSGVO-konform auf eigenen Servern abzubilden, sind **BigBlueButton (Open-Source Web Conferencing)** und eine **Enterprise Cloud-Drive-Lösung (Self-Hosted Nextcloud / OwnCloud Storage Core)** tief in die Geschäftslogik aller Plattformbereiche eingewoben.

### 3.1 BigBlueButton (BBB) Open-Source Integration & Dedizierte Server-Architektur

Auf den dafür vorgesehenen dedizierten Streaming- und Medienservern wird ein hochverfügbares **BigBlueButton-Cluster** betrieben, das über einen zentralen Load-Balancer (**Scalelite**) mit dem Laravel Core-ERP und Twenty CRM gekoppelt ist. Kein Nutzer sieht jemals eine externe BBB-URL; der Beitritt erfolgt nahtlos eingebettet (oder per Custom-Domain `live.studienkolleg-aachen.de`) im Corporate Design von `deinstudienkolleg.de`.

#### A. Vollmigration in alle relevanten Geschäftsprozesse & Bereiche
1. **Virtuelle Klassenzimmer & Hybrid-Unterricht (Studienkolleg, Sprachschule & Pflegeschule):**
   * Jede im Stundenplan-Generator angelegte Unterrichtseinheit besitzt automatisch einen zugeordneten BigBlueButton-Raum.
   * **Dozenten-Flow:** Der Dozent klickt im Dozenten-Portal oder am digitalen Smartboard im Aachener Klassenzimmer (Theaterstr. 30–32) auf *"Unterricht starten"*. Das ERP ruft per BBB-API `/api/create` auf, lädt vollautomatisch die für diese Stunde im **Cloud-Drive** hinterlegte Präsentation/PDF als Standard-Foliensatz (`preUploadPresentation`) in die Tafel des BBB-Raums und loggt den Dozenten mit Moderator-Rechten ein.
   * **Studierenden-Flow:** Erst sobald der Dozent im Raum ist, wechselt der Button im Studierenden-Portal und in der Flutter-App in Echtzeit (via WebSocket) auf Grün (*"Jetzt Live-Unterricht beitreten"*).
   * **Didaktische Features:** Mehrbenutzer-Whiteboard (für mathematische Formeln im T-/W-Kurs), Breakout-Räume für Gruppenarbeiten im Sprachkurs, geteilte Notizen, Live-Umfragen (Polls) zur Wissensabfrage und Bildschirmfreigabe.
2. **Automatisierte Anwesenheits- & AZAV-/Visa-Compliance-Logik (Webhook-getrieben):**
   * Für Sprachkursvisa und AZAV-geförderte Pflegeschüler (Bildungsgutschein) verlangen Behörden einen sekundengenauen Anwesenheitsnachweis bei Online- und Hybrid-Unterricht.
   * Der BigBlueButton-Server sendet sämtliche Raum-Events (`user-joined`, `user-left`, `meeting-ended`) in Echtzeit per HMAC-signiertem Webhook an das Laravel-ERP.
   * **Berechnungs-Logik:** Das ERP summiert die Netto-Anwesenheitsdauer jedes Schülers pro Unterrichtseinheit. Ist ein Schüler mindestens $85\%$ der Unterrichtszeit aktiv verbunden (inkl. optionalem Zufalls-Anwesenheits-Ping bei Kamerapflicht), wird er im digitalen Klassenbuch automatisch als *"Anwesend (Online verifiziert)"* markiert. Bei Unterschreitung wird automatisch eine Teil- oder Fehlzeit verbucht, die direkt in das **PflBG-/AZAV-Fehlzeiten-Frühwarnsystem** und den **Visa-Tracker** einfließt.
3. **Vertriebs- & Studienberatung ("Book Free Consultation" auf der Webseite):**
   * Bucht ein Interessent auf `studienkolleg-aachen.de` über den Button *"Book Free Consultation / Beratung buchen"* einen Termin (z. B. mit der Studienberatung der W2G Academy GmbH), legt **Twenty CRM** automatisch einen Kalendereintrag an, generiert einen dedizierten 1-zu-1-BigBlueButton-Beratungsraum und versendet den Einladungslink per E-Mail und WhatsApp-Erinnerung ($24\text{ Std.}$ und $15\text{ Min.}$ vor Beginn).
   * Während des Gesprächs sieht der Studienberater im Split-Screen daneben direkt die Twenty-CRM-Akte und die KI-Anabin-Auswertung des Bewerbers.
4. **Mündliche KI-/Live-Sprachprüfungen & B2B-Vorstellungsgespräche (Job-Portal):**
   * **Sprachschule:** Mündliche GER-Prüfungen (B1/B2/C1) finden in speziellen, revisionssicher aufgezeichneten BBB-Prüfungsräumen statt.
   * **Healthcare Job-Portal:** Sobald zwischen einem Krankenhaus und einem Pflege-Kandidaten ein *"Match"* entsteht, können beide Parteien im B2B-/Kandidaten-Portal mit einem Klick ein **Video-Vorstellungsgespräch** terminieren. Das System schaltet zum gewählten Zeitpunkt automatisch einen geschützten BBB-Interview-Raum frei – ohne dass private Telefonnummern oder externe Tools (Teams/Zoom) ausgetauscht werden müssen.

---

### 3.2 Vollintegrierte Cloud-Drive-Onlinespeicher-Lösung (Enterprise Document & Media Core)

Als zentrale Dateidrehscheibe wird eine selbstgehostete, S3/R2-gestützte **Cloud-Drive-Onlinespeicher-Lösung** (Nextcloud / OwnCloud Enterprise File-Sync & Share Core mit WebDAV-, OCS-REST-API und Collabora/OnlyOffice-Integration) nahtlos in alle Portale und Apps integriert. Nutzer müssen sich niemals separat im Drive einloggen (Single Sign-On via OIDC/JWT); das Drive ist sowohl als natives UI-Modul (*"Mein Drive"*) im Portal eingebettet als auch über Desktop-/Mobile-Sync-Clients nutzbar.

#### A. Automatisierte Ordner-Topologie & Berechtigungs-Matrix (Zero-Touch Provisioning)
Jede Statusänderung in **Twenty CRM** oder im **Laravel-ERP** steuert vollautomatisch die Ordnerstrukturen und Zugriffsrechte (ACLs) im Cloud-Drive:

1. **Persönlicher Bewerber- & Studierenden-Tresor (`/Users/{matrikel_nr}_{name}/`):**
   * Wird automatisch bei Registrierung im neuen Bewerbungsportal angelegt:
     * `01_Bewerbung_&_Anabin/` (Hier landen automatisch Reisepass, Originalzeugnisse, Übersetzungen und das KI-Prüfprotokoll).
     * `02_Vertraege_&_Bescheide/` (Hier legt das ERP vollautomatisch den Zulassungsbescheid, das dynamische Welcome-PDF, aktuelle Immatrikulationsbescheinigungen und FSP-/Sprach-Zertifikate ab).
     * `03_Visum_&_Behoerden/` (Synchronisiert mit dem Visa-Tracker: Sperrkontonachweis Fintiba/Expatrio, Krankenversicherungsnachweis Care Concept/Feather, eAT-Aufenthaltstitel).
     * `04_Wohnen_&_Mietvertrag/` (Enthält den eIDAS-signierten Mietvertrag, das Übergabeprotokoll mit Fotos, den GEG-Energieausweis, die Kautionsbürgschaftsurkunde und die Haftpflichtpolice).
     * `05_Rechnungen_&_Quittungen/` (Alle Revolut-Zahlungsbelege, SWIFT-MT103-Uploads und ZUGFeRD-Rechnungen).
     * `06_Persoenlicher_Speicher/` (Freier Cloud-Speicherplatz des Studierenden, z. B. $10\text{ GB}$ Quota, für eigene Zusammenfassungen und Mitschriften).
2. **Automatisierte Kurs-, Klassen- & Lehrmaterial-Laufwerke (`/Courses/{semester}/{kurs_code}/`):**
   * Sobald ein Studierender im ERP z. B. dem `T-Kurs WS 2026/27` oder dem `Deutsch B2-Intensivkurs` zugewiesen wird, erhält er automatisch Zugriff auf das Gruppenlaufwerk seiner Klasse:
     * `01_Skripte_&_Vorlesungsfolien/` (*Read-Only* für Studierende, *Read-Write* für Dozenten des Kurses).
     * `02_BigBlueButton_Aufzeichnungen/` (*Automatischer Zielordner für alle Video-Aufzeichnungen der Live-Unterrichtsstunden dieser Klasse*).
     * `03_Hausaufgaben_Abgabe/` (*File-Drop / Write-Only-Logik*: Jeder Schüler sieht hier nur seinen eigenen Unterordner für Abgaben; der Dozent sieht alle Abgaben der Klasse gesammelt zur Korrektur).
     * `04_Kollaborative_Arbeitsmappe/` (Gemeinsames Bearbeiten von Dokumenten, Tabellen und Präsentationen in Echtzeit direkt im Browser).
3. **Pflegeschul-, AZAV- & Krankenhaus-Laufwerke (`/Nursing/`):**
   * Isolierte Drive-Bereiche für Ausbildungsnachweise (E-Logbook-PDF-Exporte), Praxis-Rotationspläne für kooperierende Krankenhäuser sowie der revisionssichere **`/AZAV_Audit_Safe/`**, in dem alle für TÜV/DEKRA relevanten Dozenten-Urkunden, Fortbildungsnachweise der Praxisanleiter und Maßnahmenbögen stets aktuell synchronisiert liegen.

#### B. Vollautomatischer Workflow: BigBlueButton -> Transcoding -> Cloud-Drive -> ERP
Ein Paradebeispiel für das Zusammenspiel der Komponenten ist der **Vorlesungs-Aufzeichnungs-Flow**:
1. Eine Online- oder Hybrid-Vorlesung in BigBlueButton endet.
2. Der BBB-Server rendert die Aufzeichnung (Folien + Whiteboard + Audio/Video des Dozenten) als hochauflösende `MP4`-Videodatei und triggert den Webhook `recording-ready` an das Laravel-ERP.
3. Ein Hintergrund-Worker überträgt die Videodatei vollautomatisch über die Drive-WebDAV/S3-Schnittstelle in den exakt passenden Kursordner (`/Courses/WS26_27/T-Kurs_Mathematik/02_BigBlueButton_Aufzeichnungen/2026-10-19_Differentialrechnung.mp4`).
4. Optional erstellt ein Whisper-KI-Microservice ein voll durchsuchbares **Transkript & Kapitelmarken** der Vorlesung und legt es als PDF neben das Video in das Drive.
5. Alle Studierenden des Kurses erhalten eine Push-Benachrichtigung (*"Die Aufzeichnung und das Skript der heutigen Mathematik-Vorlesung stehen ab sofort in deinem Drive bereit"*).

---

## 4. Studienkolleg Aachen: KI-Zulassung, OCR-Pipeline & Anabin-Architektur (Ablösung des Alt-Vertriebsportals)

Das bisherige Vertriebsportal auf `deinstudienkolleg.de` (ab dem Bewerbungsformular) wird vollständig durch diese neue, KI-gestützte Bewerbungs- und Zulassungsstrecke auf `prev.studienkolleg-aachen.de` bzw. `studienkolleg-aachen.de` ersetzt. Dadurch wird das Markenversprechen der Webseite (*"Apply now with your documents and receive a response within 24 hours"*) technisch in wenigen Sekunden eingelöst.

### 4.1 Digitaler Bewerbungs-Funnel & KI-OCR-Dokumentenprüfung

1. **Dynamisches Bewerbungsformular (Next.js Funnel):** Bewerber (oder angeschlossene Bildungsagenturen über ihr B2B-Portal) klicken auf der Webseite auf *"Apply Now / Bewerbung starten"* und durchlaufen einen mehrstufigen, mehrsprachigen Funnel. Alle dort hochgeladenen Pflichtdokumente (Reisepass, Sekundarschulabschlusszeugnis im Original und in beglaubigter Übersetzung, Fächer- und Notenübersicht, ggf. APS-Zertifikat für China/Indien/Vietnam, Sprachzertifikat B1/B2) werden sofort im persönlichen **Cloud-Drive-Tresor** des Bewerbers gespeichert.
2. **Vision-LLM & OCR-Extraktions-Pipeline:**
   * Unmittelbar nach dem Upload analysiert ein isolierter Python-Microservice (FastAPI + Vision LLM / OCR) die Dokumente aus dem Drive.
   * **Authentizitäts- & Vollständigkeitscheck:** Die KI prüft, ob es sich tatsächlich um das geforderte Dokument handelt, führt eine digitale Forensik-Prüfung (EXIF/Error-Level-Analysis gegen Bildmanipulation) durch, prüft die Lesbarkeit und liest das Ablaufdatum des Reisepasses aus.
   * **Strukturierte Datenextraktion (JSON):** Die KI extrahiert vollautomatisch: Vorname, Nachname, Geburtsdatum, Staatsangehörigkeit, Passnummer, exakter Name der ausländischen Schule, Ausstellungsland, exakte Bezeichnung des Schulabschlusses, Abschlussjahr, Einzelnoten relevanter Kernfächer (Mathematik, Physik, Chemie, Biologie, Sprachen) sowie die Gesamtnote und schreibt diese Daten per GraphQL direkt in die Felder des Bewerber-Datensatzes in **Twenty CRM**.

### 4.2 Gescrapte Anabin-Datenbank & Echtzeit-Matching-Engine

Da die offizielle Datenbank der Kultusministerkonferenz (`anabin.kmk.org`) langsam ist und keine öffentliche API für Echtzeit-Abfragen bietet, betreibt die Plattform eine eigene, hochperformante Spiegel- und Matching-Architektur:

1. **Der Anabin-Scraper (Python / Playwright Microservice):**
   * Ein containerisierter Headless-Browser-Service (Playwright) durchläuft zeitgesteuert (monatlicher Delta-Sync via Cronjob) die Bereiche *"Schulabschlüsse mit Hochschulzugang"* und *"Institutionen"* der Anabin-Datenbank für alle relevanten Herkunftsländer.
   * Der Scraper umgeht Session-Timeouts durch intelligentes Request-Throttling, parst die komplexen HTML-Tabellen und Entscheidungsbäume (inkl. spezifischer Bedingungen wie Mindestnoten, Fächerkombinationen oder erforderlicher Hochschulaufnahmeprüfungen im Heimatland) und überführt diese in ein normalisiertes **PostgreSQL-Anabin-Schema** auf dem eigenen Server.
   * Bei strukturellen Änderungen am DOM der offiziellen Anabin-Seite schlägt ein Monitoring-Skript sofort im Master Admin Alarm.
2. **Fuzzy-Matching & Semantischer Abgleich:**
   * Sobald die KI-OCR-Pipeline den Abschluss und das Land aus dem hochgeladenen Zeugnis extrahiert hat, gleicht der Matching-Service diese Daten mittels PostgreSQL Trigram-Matching (`pg_trgm`) und Vektor-Embeddings (zur Überbrückung unterschiedlicher Übersetzungen von Abschlusstiteln) in unter $200\text{ Millisekunden}$ mit dem lokalen Anabin-Cache ab.
   * Gleichzeitig rechnet ein integrierter **Bayerische-Formel-Rechner** die ausländische Gesamtnote anhand der in Anabin hinterlegten Maximal- und Bestehensnoten des jeweiligen Landes exakt in das deutsche Notensystem ($1,0$ bis $4,0$) um:
     $$\text{Deutsche Note} = 1 + 3 \cdot \frac{N_{\max} - N_{\text{Bewerber}}}{N_{\max} - N_{\min}}$$
3. **Automatisiertes Ampel-Scoring in Twenty CRM:**
   * **Status GRÜN (Fast-Track Zulassung):** Der ausländische Abschluss ist in Anabin eindeutig für den gewählten Schwerpunktkurs (T/W/M/G) für den Zugang zum Studienkolleg qualifiziert (Feststellungsprüfung erforderlich), alle Fächer- und Notenbedingungen sind erfüllt, Pass und Sprachnachweis sind gültig. Twenty CRM bereitet den Zulassungsbescheid (Conditional / Unconditional Offer Letter) mit 1-Klick-Freigabe für den Sachbearbeiter vor.
   * **Status GELB (Manuelle Prüfung / Review Queue):** Unklare Dokumentenqualität, fehlendes Einzelfach, Grenzfall bei der Note oder eine Schule, die via Fuzzy-Search nur zu $75\%$ gematcht werden konnte. Das System markiert dem Sachbearbeiter im Split-Screen exakt die zu prüfende Textstelle im Originaldokument.
   * **Status ROT (Automatische Ablehnung / Alternativangebot):** Der Abschluss berechtigt laut Anabin selbst mit Studienkolleg nicht zum Studium in Deutschland (H- Status) oder die Mindestnote wird deutlich verfehlt. Das System schlägt automatisch eine Umleitung in ein vorbereitendes Programm oder eine Ausbildung an der hauseigenen Pflegeschule vor.

### 4.3 Visa-Tracker & Behörden-Compliance

* Für zugelassene internationale Studierende führt das System ein dediziertes **Visa- & Aufenthaltstitel-Tracking**.
* Nach Erhalt des Zulassungsbescheids verfolgt Twenty CRM den Status des Visumverfahrens an der deutschen Botschaft im Heimatland.
* Nach Einreise erfasst das System das Ablaufdatum des Visums bzw. der Fiktionsbescheinigung oder des elektronischen Aufenthaltstitels (eAT).
* **Fristen-Eskalation:** $90\text{ Tage}$, $60\text{ Tage}$ und $30\text{ Tage}$ vor Ablauf des Aufenthaltstitels erhält der Studierende (und das International Office des Studienkollegs) automatische Push- und E-Mail-Erinnerungen inklusive der direkt im persönlichen **Cloud-Drive** bereitgestellten, aktuellen Studienbescheinigung und Anwesenheitsstatistik zur Vorlage bei der Ausländerbehörde der Städteregion Aachen.

---

## 5. Integrierte Sprachschule: E-Commerce, KI-Assessment, BigBlueButton & Upselling

Die hauseigene Sprachschule des Studienkollegs Aachen ist als vollwertiges E-Commerce- und Akademisches Modul nahtlos in die Webseite und die Plattform-Architektur integriert.

### 5.1 Öffentlicher Kurskatalog & Direktbuchung

* Auf `studienkolleg-aachen.de/sprachschule` werden alle Kurse (Deutsch Intensiv A1, A2, B1, B2, C1 in $8\text{–}12\text{ Wochen}$-Modulen ab $1.200\text{ EUR}$ sowie DSH-, TestDaF-, telc-Vorbereitungskurse und Fachsprachenkurse Pflege B2) mit Live-Verfügbarkeiten (freie Plätze, Starttermine, Präsenz in Aachen vs. **Online-Live via BigBlueButton**) dargestellt.
* Interessenten können einzelne Kursmodule oder komplette Lernpakete (z. B. *"Zero to C1 + Studienkolleg-Garantieplatz"*) direkt in den Warenkorb legen und über die Revolut Checkout-Engine bezahlen.
* Nach Zahlungseingang wird automatisch die offizielle Anmeldebestätigung zur Vorlage für das Sprachkursvisum generiert, im persönlichen **Cloud-Drive** abgelegt und der Zugang zum BigBlueButton-Klassenraum freigeschaltet.

### 5.2 Adaptiver KI-Sprach-Einstufungstest (GER / CEFR)

* Jeder neue Sprachschüler (oder Bewerber ohne offizielles Zertifikat) absolviert direkt im Web-Portal einen KI-gestützten Einstufungstest nach dem **Gemeinsamen Europäischen Referenzrahmen für Sprachen (GER / CEFR)**:
  1. **Adaptiver Multiple-Choice-Teil (Hör- & Leseverstehen, Grammatik):** Ein Algorithmus passt den Schwierigkeitsgrad der nächsten Frage nach dem Prinzip des *Computerized Adaptive Testing (CAT)* in Echtzeit an die vorherige Antwort des Schülers an. Beantwortet der Schüler A2-Fragen fehlerfrei, schaltet das System sofort auf B1/B2-Fragen hoch.
  2. **KI-Freitext- & Sprachanalyse (Schreiben & Sprechen):** Der Bewerber verfasst einen kurzen Text zu einem dynamisch generierten Thema und spricht eine 60-sekündige Audio-Antwort über das Mikrofon ein. Ein angebundenes Audio-/Text-LLM transkribiert und bewertet Wortschatzbreite, Satzbaukomplexität, Flüssigkeit und grammatikalische Korrektheit exakt nach den GER-Deskriptoren (A1.1 bis C1.2).
* Das Ergebnis weist den Schüler ohne manuellen Korrekturaufwand der exakt passenden Kursstufe und Klasse im ERP zu.

### 5.3 Automatisierte "Student Journey" & CRM-Upselling

* Sprachschüler werden in Twenty CRM in einer dedizierten Pipeline geführt.
* **Automatischer Übergang ins Studienkolleg:** Sobald ein Sprachschüler mit Studienwunsch in Deutschland im ERP die interne B1- oder B2-Abschlussprüfung besteht, feuert das ERP einen Webhook an Twenty CRM. Das CRM sendet dem Schüler vollautomatisch ein personalisiertes Angebot zur Reservierung seines Platzes im kommenden T-, W-, M- oder G-Kurs des Studienkollegs Aachen und startet den Dokumenten-Check (Anabin).
* **Automatischer Übergang in die Pflegeschule:** Sprachschüler aus dem Ausland, die das Niveau B1/B2 erreichen und kein Hochschulstudium anstreben (oder deren Schulabschluss laut Anabin nicht für die Universität ausreicht), erhalten über Twenty CRM proaktiv das Angebot für einen direkten Ausbildungsplatz in der hauseigenen Pflegeschule inklusive Ausbildungsvergütung.

---

## 6. Wohnungsportal & Digitale Immobilienverwaltung ("Stay in Aachen" nach DIN-Norm)

Das Studienkolleg Aachen (bzw. die verbundene Marke *Stay in Aachen*) bewirtschaftet eigene Zimmer, Apartments und Wohngemeinschaften und vermittelt Kontingente kooperierender Wohnheime. Das Wohnungsportal ist als vollständiges Property-Management-System (PMS) in das ERP und die Website eingebettet.

### 6.1 Normgerechte Objekt- & Bestandsverwaltung

* Im ERP werden Liegenschaften hierarchisch angelegt: Gebäude -> Etage -> Wohneinheit (Apartment / WG) -> Einzelzimmer / Bettplatz -> Inventarliste.
* **Strikte Berechnung nach DIN 277 & WoFlV:** Bei der Anlage eines Zimmers oder einer Wohnung im Backend müssen die Grundflächen zwingend nach **DIN 277** (Nettoraumfläche, Nutzfläche, Verkehrsfläche, Technikfläche) sowie der **Wohnflächenverordnung (WoFlV)** (inkl. automatischer Abzugslogik von $50\%$ bei Dachschrägen zwischen $1,00\text{ m}$ und $2,00\text{ m}$ lichte Höhe und $100\%$ Abzug unter $1,00\text{ m}$ sowie anteiliger Berechnung von Balkonen mit $25\%$) eingegeben werden. Das System berechnet daraus rechtssicher die exakte anrechenbare Wohnfläche und den Umlageschlüssel für die Nebenkostenabrechnung.
* **Pflichtangaben nach GEG:** Erzwingung der Hinterlegung des Energieausweises (Energiebedarfs- oder Energieverbrauchsausweis, Endenergiekennwert in $\text{kWh}/(\text{m}^2\cdot\text{a})$, wesentlicher Energieträger, Baujahr, Energieeffizienzklasse A+ bis H) vor Freischaltung eines Inserats auf der Website, um Abmahnrisiken zu $100\%$ auszuschließen.

### 6.2 KI-Virtual-Staging & Automatischer Exposé-Generator

* **KI-Bildaufbereitung (Virtual Staging):** Verwalter laden einfache Smartphone-Fotos von leeren, unrenovierten oder noch im Bau befindlichen Zimmern in das Backend hoch. Eine integrierte Image-to-Image-KI-Pipeline korrigiert automatisch Belichtung und Perspektive und möbliert die Räume fotorealistisch im modernen Studierenden-Stil (Bett, Schreibtisch, Kleiderschrank, Beleuchtung). Zur Wahrung der rechtlichen Transparenz wird jedes Bild automatisch mit einem dezenten Wasserzeichen (*"Visualisierungsbeispiel / Virtuell möbliert"*) neben dem Originalfoto und dem maßstabsgetreuen 2D/3D-Grundriss ausgespielt.
* **KI-Exposé-Texterstellung:** Auf Basis der eingegebenen Eckdaten (Fläche nach DIN 277, Lage in Aachen, Distanz zum Campus Theaterstr. 30–32 / RWTH / Uniklinik, Ausstattung, Mietpreis) generiert ein LLM auf Knopfdruck verkaufsstarke, zielgruppengerechte Objektbeschreibungen simultan in allen 8+ Portalsprachen (DE, EN, AR, RU, UK, ES, FR, IT, ZH).

### 6.3 Zulassungs-gekoppelter Buchungs-, Mietvertrags- & Kautionsprozess

1. **Gated Booking (Bewerber-Schranke):** Auf `studienkolleg-aachen.de/wohnen` sind sämtliche Immobilienangebote öffentlich einsehbar (inkl. Verfügbarkeitsampel, Video-Room-Tour und Einzugsdatum). Ein Interessent kann sich auf ein Zimmer vormerken lassen. Der verbindliche Buchungs- und Abschlussprozess im Portal wird jedoch erst dann technisch freigeschaltet, wenn in **Twenty CRM** der Status des Bewerbers auf *"Zugelassen (Studienkolleg / Sprachschule / Pflegeschule)"* steht.
2. **Automatisierte Mietvertragsgenerierung, eIDAS-Signatur & Cloud-Drive-Ablage:**
   * Wählt der zugelassene Bewerber ein Zimmer aus, generiert das ERP in Echtzeit einen zweisprachigen (Deutsch/Englisch), rechtssicheren Mietvertrag inkl. Hausordnung, Widerrufsbelehrung und Energieausweis-Anhang.
   * Der Vertrag wird direkt im Browser über eine integrierte **qualifizierte elektronische Signatur (QES nach eIDAS-Verordnung)** von Mieter und Vermieter rechtsgültig online gezeichnet und anschließend vollautomatisch im Ordner `04_Wohnen_&_Mietvertrag/` des persönlichen **Cloud-Drives** archiviert.
3. **Revolut-Mietzahlung & Clevere Kautionslogik im Check-out:**
   * Für die erste Monatsmiete und das Einrichten des Dauerauftrags (SEPA-Mandat oder wiederkehrende Kreditkartenbelastung) wird der Mieter direkt durch den Revolut-Payment-Flow geführt.
   * **Wahlrecht bei der Mietkaution (3 Kaltmieten nach § 551 BGB):** Da internationale Studierende bei Einreise oft unter Liquiditätsengpässen leiden (da ihr Geld auf dem Sperrkonto gebunden ist), bietet der Check-out zwei vollintegrierte Wege:
     * *Option A (Klassische Barkaution auf Treuhandkonto):* Direkte Überweisung der Kaution via Revolut. Die Revolut-API legt hierfür vollautomatisch ein insolvenzfestes, virtuelles Unterkonto (Escrow / Mietkautionskonto) auf den Namen des Mieters an.
     * *Option B (Mietkautionsbürgschaft ohne Liquiditätsverlust):* Der Mieter wählt im Check-out mit einem Klick die integrierte Kautionskasse (z. B. *kautionsfrei.de*). Er zahlt lediglich einen geringen jährlichen Beitrag (ca. $4,7\%$ bis $5,2\%$ der Kautionssumme), das Studienkolleg Aachen erhält sofort die digitale Bürgschaftsurkunde als 100%ige Sicherheit ins Cloud-Drive und generiert zusätzlich eine Affiliate-Provision.
4. **Digitale Schlüsselübergabe & Übergabeprotokoll:**
   * Die Freigabe des digitalen Türzugangscodes (Smart-Lock-Integration) bzw. der Termin zur physischen Schlüsselübergabe erfolgt im System erst, wenn: a) der Mietvertrag eIDAS-signiert ist, b) die 1. Miete + Kaution/Bürgschaft verbucht sind und c) der Pflichtnachweis einer **deutschen Privathaftpflichtversicherung** im Portal/Drive hochgeladen wurde.
   * Beim Einzug und Auszug wird über die Mobile-App ein digitales Wohnungsübergabeprotokoll (inkl. Zählerständen, Inventar-Checkliste und Pflichtfotos etwaiger Mängel) erstellt, von beiden Parteien auf dem Smartphone-Display unterschrieben und automatisch im Cloud-Drive abgelegt.

---

## 7. Value-Added Services (VAS), Affiliate-Ökosystem & Dynamisches Welcome-PDF

Um internationale Studierende und Auszubildende bei sämtlichen bürokratischen Hürden in Deutschland proaktiv zu unterstützen und gleichzeitig hochmargige Zusatzeinnahmen (Affiliate-Provisionen) ohne eigenen Betriebsaufwand zu realisieren, ist ein komplettes Partner-Ökosystem fest in die Plattform und die Kommunikationsprozesse eingebaut.

### 7.1 Dedizierte Service-Unterseite (`studienkolleg-aachen.de/services`)

Auf einer eigenen, in allen 8+ Sprachen aufbereiteten Unterseite sowie in einem permanenten Reiter *"Mein Start in Deutschland (Checklist)"* im Studierenden-Portal sind alle relevanten Partnerlösungen mit direkter API-Vorausfüllung (Pre-Fill der Bewerberdaten aus Twenty CRM) oder direktem Partner-Tracking-Link eingebunden:

1. **Sperrkonto (Blocked Account) & Kombi-Pakete (Pflicht für das Visum):**
   * **Fintiba (Fintiba Basic & Fintiba Plus inkl. Krankenversicherung):** Direkte API-/Partner-Integration. Zielseite & Partner-Anbindung: <https://www.fintiba.com> bzw. Partnerprogramm unter <https://www.fintiba.com/partner/>.
   * **Expatrio (Blocked Account & Value Package):** Vollintegrierte Alternative für internationale Studierende. Zielseite & Partner-Anbindung: <https://www.expatrio.com> bzw. Partnerprogramm unter <https://www.expatrio.com/partners>.
   * *System-Workflow:* Sobald der Studierende über den Link eröffnet und die Sperrbestätigung (Blocking Confirmation) erhält, wird das Dokument automatisch im Cloud-Drive unter `03_Visum_&_Behoerden/` gespeichert und der Status im Twenty CRM Visa-Tracker auf *"Sperrkonto aktiv"* gesetzt.
2. **Gesetzliche & Private Krankenversicherung (GKV / PKV für Sprachschüler & Studienkollegiaten):**
   * Da Studierende am Studienkolleg und in Sprachkursen oft noch nicht in die reguläre studentische GKV aufgenommen werden können, bis sie an der Universität immatrikuliert sind, werden spezialisierte Incoming-/Tarife sowie GKV-Partner für Pflegeschüler direkt vermittelt:
   * **Care Concept (Care College / Care Economy):** Spezialtarife exakt für Studienkollegiaten und Sprachschüler. Zielseite & Partner-Anbindung: <https://www.care-concept.de> bzw. Vermittlerportal unter <https://www.care-concept.de/vermittler.php>.
   * **MAWISTA (Mawista Student):** Private Krankenversicherung für internationale Bildungszwecke. Zielseite: <https://www.mawista.com>.
   * **Feather Insurance (Digitale Expat-Versicherungen auf Englisch):** Bietet sowohl Expat Health Insurance als auch gesetzliche Kassen (TK, Barmer, DAK) volldigital an. Zielseite & Partnerprogramm: <https://feather-insurance.com> bzw. <https://feather-insurance.com/partners>.
3. **Mietkautionsbürgschaft (Kautionskasse für das Wohnungsportal):**
   * **kautionsfrei.de (R+V Versicherung Gruppe):** Direkte Einbettung im Wohnungs-Checkout und auf der Serviceseite. Zielseite & Partnerprogramm: <https://www.kautionsfrei.de> bzw. <https://www.kautionsfrei.de/partnerprogramm>.
   * **SWK Bank Mietkautionsbürgschaft:** Bankbürgschaft als zweite Option. Zielseite: <https://www.swkbank.de>.
4. **Privathaftpflicht-, Hausrat- & Mietschadenversicherung (Pflichtbaustein für Mieter):**
   * **Getsafe (App-basierte Versicherung auf Englisch/Deutsch):** Abschluss einer Privathaftpflichtversicherung (inkl. Abdeckung von Mietsachschäden und Schlüsselverlust für die Wohnheime des Studienkollegs Aachen) in unter $3\text{ Minuten}$ per App. Zielseite & Partnerprogramm: <https://www.hellogetsafe.com> bzw. <https://www.hellogetsafe.com/de-de/affiliate>.
5. **Girokonto, Finanzen & Internationale Überweisungen:**
   * **Revolut:** Kontoeröffnung für Studierende im Heimatland oder direkt nach Ankunft für gebührenfreie Währungsumrechnung und sofortige Zahlung am Campus. Zielseite: <https://www.revolut.com>.
6. **Mobilität & Telekommunikation in Aachen:**
   * Direkte Buchungsmöglichkeit für das **Deutschlandticket / Semesterticket (ASEAG Aachen)** sowie eSIM-Soforttarife für die Einreise (z. B. **fraenk** unter <https://fraenk.de> oder **Congstar** unter <https://www.congstar.de>).

### 7.2 Automatisierte Einbettung in die Bewerberprozesse (Das dynamische Welcome-PDF)

Die Vermarktung dieser Zusatzleistungen erfolgt nicht passiv, sondern wird durch **Twenty CRM** exakt in dem Moment getriggert, in dem der Bewerber den höchsten Bedarf hat:

* **Trigger "Zulassung erteilt":** Sobald ein Bewerber für das Studienkolleg, die Sprachschule oder die Pflegeschule zugelassen wird, generiert das Laravel-ERP neben dem formellen Zulassungsbescheid vollautomatisch ein personalisiertes, mehrseitiges **"Welcome & Onboarding Guide PDF"** (im Corporate Design von `deinstudienkolleg.de` / Studienkolleg Aachen, adressiert mit dem Namen und der Matrikelnummer des Bewerbers) und legt es direkt im persönlichen **Cloud-Drive** ab.
* **Inhalt des dynamischen PDFs:**
  * Schritt-für-Schritt-Checkliste für das Visum und die Einreise nach Aachen.
  * Direkte, klickbare Buttons und individuelle **QR-Codes** (mit eingebetteter Affiliate-Sub-ID des Bewerbers, damit jede Provision eindeutig dem Studierenden und ggf. dem Standort zugeordnet werden kann) zu:
    1. *Eröffnung des Sperrkontos (Fintiba / Expatrio).*
    2. *Abschluss der verpflichtenden Krankenversicherung (Care Concept / Feather).*
    3. *Direkt-Bewerbung auf die aktuell noch freien Zimmer im eigenen Wohnungsportal des Studienkollegs Aachen.*
    4. *Abschluss der Kautionsbürgschaft (kautionsfrei.de) und der Privathaftpflicht (Getsafe).*
    5. *Buchung des Flughafen-Shuttle-Services nach Aachen.*
* **Portal-Gamification (Onboarding-Fortschrittsbalken):** Im Studierenden-Portal sieht der Bewerber vor seiner Anreise einen Fortschrittsbalken (*"Dein Start in Aachen: 3 von 6 Schritten erledigt"*). Offene Punkte (wie fehlende Krankenversicherung oder fehlende Wohnung) verlinken direkt auf die integrierten Partner-Strecken.

---

## 8. Digitale Pflegeschule: PflBG, PflAPrV & AZAV-Compliance

Das Studienkolleg Aachen betreibt (aufbauend auf der Säule *"Healthcare & Medicine"* von `deinstudienkolleg.de`) eine eigene Pflegeschule zur Ausbildung von Pflegefachfrauen und Pflegefachmännern sowie Anerkennungskurse für internationale Pflegekräfte. Da die generalistische Pflegeausbildung in Deutschland strengsten gesetzlichen Vorgaben unterliegt, bildet das ERP sämtliche regulatorischen Anforderungen nach dem **Pflegeberufegesetz (PflBG)**, der **Ausbildungs- und Prüfungsverordnung (PflAPrV)** und der **AZAV** vollständig ab.

### 8.1 Algorithmischer Theorie- & Praxis-Rotationsplaner

Die generalistische Pflegeausbildung umfasst zwingend mindestens $2.100\text{ Stunden}$ theoretischen und praktischen Unterricht an der Pflegeschule sowie mindestens $2.500\text{ Stunden}$ praktische Ausbildung bei den Trägern der praktischen Ausbildung (Krankenhäuser, stationäre Pflegeheime, ambulante Pflegedienste).

* **Pflichteinsatz-Matrix nach PflAPrV:** Der integrierte Rotationsplaner-Algorithmus überwacht und plant für jeden einzelnen Auszubildenden über die 3 Ausbildungsjahre hinweg die gesetzlich vorgeschriebenen Mindeststunden in den 7 Pflichtbereichen:
  1. Orientierungseinsatz ($400\text{ Std.}$ beim eigenen Träger).
  2. Pflichteinsatz stationäre Akutpflege / Krankenhaus ($400\text{ Std.}$).
  3. Pflichteinsatz stationäre Langzeitpflege / Pflegeheim ($400\text{ Std.}$).
  4. Pflichteinsatz ambulante Akut- und Langzeitpflege ($400\text{ Std.}$).
  5. Pflichteinsatz pädiatrische Versorgung / Kinderheilkunde ($120\text{ Std.}$).
  6. Pflichteinsatz psychiatrische Versorgung ($120\text{ Std.}$).
  7. Vertiefungseinsatz ($500\text{ Std.}$) sowie weitere zur freien Verteilung stehende Stunden.
* **Kapazitäts- & Kooperationsmanagement:** Im System sind alle kooperierenden Kliniken und Heime (der Ausbildungsverbund) mit ihren maximalen Stationskapazitäten pro Zeitraum hinterlegt. Der Algorithmus weist die Schüler unter Berücksichtigung von Wohnortnähe (Aachen/NRW), Kapazitätsgrenzen und Theorieblöcken automatisch den Praxisstellen zu und meldet den Einsatzplan per Schnittstelle (oder über einen geteilten Kooperations-Ordner im **Cloud-Drive**) direkt an die Pflegedienstleitungen der Krankenhäuser.

### 8.2 Digitaler Ausbildungsnachweis (E-Logbook) & Die "Praxisanleiter-App"

* **Das Problem im Krankenhausalltag:** Während der Praxiseinsätze müssen Auszubildende ihre Tätigkeiten und Kompetenzen nach Anlage 2 PflAPrV dokumentieren. Zudem schreibt das Gesetz zwingend vor, dass mindestens **$10\%$ der praktischen Ausbildungszeit** eines jeden Einsatzes als geplante und strukturierte **Praxisanleitung** durch examinierte Praxisanleiter vor Ort durchgeführt und nachgewiesen werden müssen. Pflegekräfte auf Station haben jedoch keine Zeit, sich an stationären PCs in komplexe Schulportale einzuloggen.
* **Unsere Schlüssel-Lösung (Mobile QR-Abzeichnung):**
  1. Der Pflegeschüler führt seinen Ausbildungsnachweis (E-Logbook) digital in seiner **Studierenden-App**.
  2. Am Ende einer Schicht oder einer Praxisanleitungs-Sequenz wählt der Schüler in seiner App die absolvierten Stunden und Kompetenzbereiche aus und klickt auf *"Jetzt vom Praxisanleiter gegenzeichnen lassen"*. Auf dem Display des Schülers erscheint ein zeitlich begrenzter, dynamischer QR-Code.
  3. Der Praxisanleiter im Krankenhaus öffnet auf seinem Smartphone die extrem schlanke **Praxisanleiter-App** (oder nutzt einen installationsfreien Web-Scanner), scannt den QR-Code des Schülers, sieht sofort die Zusammenfassung (*"8 Std. Akutpflege / 1,5 Std. gezielte Praxisanleitung Wundmanagement"*), vergibt per Slider eine Kurzbewertung und unterschreibt mit dem Finger auf dem Display (fortgeschrittene/qualifizierte elektronische Signatur nach **eIDAS**).
  4. Die Daten sind in derselben Sekunde manipulationssicher im ERP der Pflegeschule verbucht und als signiertes PDF im **Cloud-Drive** des Schülers aktualisiert. Fehlt die 10%-Quote der Praxisanleitung gegen Ende eines Einsatzblocks, warnt das System automatisch die Schule und den Praxisträger.

### 8.3 Gesetzliches Fehlzeiten-Frühwarnsystem (PflBG & AZAV)

* **Überwachung der gesetzlichen Höchstgrenzen (§ 13 PflBG):** Auf die Dauer der Ausbildung werden Urlaub und Ferien sowie bis zu $10\%$ Fehlzeiten (durch Krankheit oder andere vom Schüler nicht zu vertretende Gründe) angerechnet, wobei weder im Theorie- noch im Praxisteil mehr als $10\%$ der Stunden versäumt werden dürfen, ohne dass die Zulassung zum Staatsexamen gefährdet ist (bzw. eine Ausbildungsverlängerung beantragt werden muss).
* **Mehrstufige Eskalationslogik in Twenty CRM (inkl. BigBlueButton-Live-Zeiten):**
  * Das ERP summiert tägliche Fehlzeiten aus dem digitalen Klassenbuch der Schule, den automatischen **BigBlueButton-Anwesenheitslogs** (bei Online-Theorieunterricht) und dem E-Logbook der Krankenhäuser in Echtzeit.
  * **Stufe 1 ($5\%$ Fehlzeiten erreicht):** Automatische Info-Nachricht an den Klassenlehrer und den Schüler in der App mit genauer Anzeige des verbleibenden Stundenpuffers.
  * **Stufe 2 ($7,5\%$ Fehlzeiten erreicht):** Automatische Generierung einer Einladung zum verpflichtenden Fürsorge-/Beratungsgespräch (vor Ort oder via BigBlueButton) durch die Schulleitung und Benachrichtigung des Praxisträgers (Krankenhaus).
  * **Stufe 3 ($9\%$ Fehlzeiten erreicht / AZAV-Kritisch):** Sofortige rote Eskalation im Master/School Admin. Bei geförderten Umschülern (Bildungsgutschein) generiert das System automatisch die vorgeschriebene **Veränderungsmeldung für die Agentur für Arbeit / das Jobcenter**, um Regressforderungen gegen die Schule zu verhindern.

### 8.4 1-Klick AZAV-Audit-Report & Staatsexamen-Meldung

* **Der "Audit-Knopf" für TÜV / DEKRA (AZAV-Zertifizierung):** Bildungsträger müssen für die Zulassung nach AZAV regelmäßige Überwachungsaudits bestehen. Im ERP existiert ein dediziertes Reporting-Modul, das auf einen einzigen Klick ein vollständig normiertes, pseudonymisiertes **AZAV-Audit-Dossier** im Cloud-Drive-Ordner `/AZAV_Audit_Safe/` generiert. Dieses enthält:
  * Lückenlose Stunden- und Curriculums-Nachweise pro Klasse (inkl. BigBlueButton-Teilnahmeprotokollen).
  * Qualifikationsmatrix aller eingesetzten Dozenten und Praxisanleiter (inkl. direkter Drive-Verknüpfung zu deren hinterlegten Hochschulabschlüssen und 24-Stunden-Pflichtfortbildungen pro Jahr für Praxisanleiter nach § 4 Abs. 3 PflAPrV).
  * Statistiken über Fehlzeiten, Abbrecherquoten (Drop-out), Bestehensquoten und Ergebnisse der Teilnehmerbefragungen (Qualitätsmanagement nach ISO 9001 / AZAV).
* **Behörden-Export für das Staatsexamen:** Automatisierte Zusammenstellung aller Zulassungsvoraussetzungen (Fehlzeitenprüfung, Notenbescheinigungen der Vornoten, Nachweis aller Pflichteinsätze und Praxisanleitungsstunden) zur digitalen Einreichung bei der zuständigen Prüfungsbehörde (Bezirksregierung Köln / NRW).

---

## 9. Healthcare Job-Portal, Reverse Recruiting & White-Label-SaaS

Direkt an die Pflegeschule (und die Säule *"Work & Career"* von `deinstudienkolleg.de`) ist ein hochmodernes **Healthcare Job-Portal nach dem Reverse-Recruiting-Prinzip ("Tinder für Pflegekräfte")** gekoppelt. Gleichzeitig wird die gesamte Pflegeschul- und Job-Portal-Infrastruktur als **White-Label-SaaS** an andere Pflegeschulen in ganz Deutschland vertrieben.

### 9.1 Die 3 Kandidaten-Pools des Job-Portals

Das System bündelt drei kontinuierlich wachsende Quellen an qualifizierten Pflegekräften in einer zentralen, strukturierten Matching-Datenbank:

1. **Pool 1 – Eigene Absolventen (Pflegeschule & Sprachschule Aachen):**
   * Auszubildende der eigenen Pflegeschule sowie internationale Pflegekräfte aus den B2-Fachsprachenkursen (im Anerkennungsverfahren).
   * *Automatisierter Onboarding-Trigger:* Exakt $6\text{ Monate}$ vor dem geplanten Staatsexamen (oder der Kenntnisprüfung) erhält der Schüler in seiner App eine Push-Einladung: *"Aktiviere jetzt mit einem Klick dein anonymes Karriere-Profil und lass dir Top-Jobangebote von Kliniken in deiner Wunschregion zusenden."*
2. **Pool 2 – Netzwerk-Pool (Schüler externer White-Label-Pflegeschulen):**
   * Auszubildende von fremden Pflegeschulen in Deutschland, die unsere Software als White-Label-ERP nutzen und ihre Abschlussklassen für den bundesweiten Recruiting-Pool freigeschaltet haben.
3. **Pool 3 – Externe, freie Jobsuchende (Examiniertes Personal):**
   * Examinierte Pflegefachkräfte, Intensivpfleger, OP-Personal und Pflegehelfer aus dem gesamten Bundesgebiet und dem Ausland, die sich kostenlos über die öffentliche Plattform registrieren.
   * *KI-CV-Parser & Drive-Sync:* Externe Bewerber laden lediglich ihren Lebenslauf und ihre Examensurkunde/Berufserlaubnis in ihren Bewerber-Drive-Ordner hoch. Unsere KI-OCR-Pipeline (aus Modul 4) liest alle Qualifikationen, Fachweiterbildungen und Berufsjahre automatisch aus und generiert sofort ein verifiziertes Kandidatenprofil.

### 9.2 Das B2B Arbeitgeber-Dashboard, Anonymes Matching & BigBlueButton-Interviews

Klassische Stellenanzeigen funktionieren im Pflegemarkt kaum noch. Auf unserer Plattform drehen wir den Prozess um – **das Krankenhaus bewirbt sich beim Kandidaten**:

1. **Arbeitgeber-Registrierung & Verifizierung:** Krankenhäuser, Universitätskliniken, Altenheime und ambulante Dienste registrieren sich im B2B-Portal (Verifizierung durch Twenty CRM). Sie hinterlegen ein attraktives Arbeitgeber-Profil (Tarifvertrag/AVR, Einstiegsgehalt, Willkommensprämie, Dienstplansicherheit, Kinderbetreuung, Bilder der Stationen).
2. **Suche im Anonymisierten Kandidaten-Pool:**
   * Arbeitgeber filtern in Echtzeit durch die Kandidaten-Pools nach harten Kriterien: *Abschlussdatum (z. B. Examen Herbst 2026), Qualifikation (Generalistik, Altenpflege, Kinderkrankenpflege, Anerkennungspraktikant), Wunschregion + Umkreis in km, Schichtbereitschaft (3-Schicht, nur Tagdienst, Dauernachtwache), Wunschart der Station (z. B. Notaufnahme, Pädiatrie, Langzeitpflege) und verifiziertes Sprachniveau.*
   * **100%ige Anonymität in Phase 1:** Der Arbeitgeber sieht im Dashboard **keine Klardaten** (kein Name, kein Foto, kein Geburtsdatum, kein aktueller Arbeitgeber/Schule), sondern standardisierte Talent-Cards (z. B. *"Kandidat #A8492 | Pflegefachkraft (Examen 09/2026) | Praxisnote: 1,7 | Praxiserfahrung Pädiatrie & Akutpflege | Sucht in: Raum Aachen/Köln | Verfügbar ab: 01.10.2026"*).
3. **Der "Match-Request" (1-Klick-Anfrage):**
   * Gefällt einer Klinik ein Profil, klickt der Personaler auf *"Kandidat anfragen (Pitch senden)"* und fügt ein kurzes, konkretes Angebot hinzu (z. B. *"Wir bieten dir auf unserer Kardiologie $4.100\text{ EUR}$ Einstiegsgehalt + $3.000\text{ EUR}$ Startprämie + 38,5h Woche"*).
4. **Entscheidung durch den Kandidaten, Drive-Freigabe & BigBlueButton-Interview:**
   * Der Kandidat erhält sofort eine Push-Benachrichtigung in seiner Flutter-App und per WhatsApp.
   * Er sieht das vollständige Profil des Krankenhauses und das konkrete Gehaltsangebot.
   * **Lehnt der Kandidat ab:** Das Krankenhaus erhält eine höfliche Absage; die Identität des Kandidaten bleibt für immer geheim.
   * **Nimmt der Kandidat an ("It's a Match!"):** Erst durch diesen aktiven Klick des Kandidaten werden sein vollständiger Lebenslauf, seine im **Cloud-Drive** hinterlegten Zeugnisse/Urkunden (über zeitlich befristete Read-Only-Share-Links) und seine Kontaktdaten im Dashboard des Krankenhauses freigeschaltet. Gleichzeitig öffnet sich der integrierte 1-zu-1-Chat und das Terminbuchungstool für ein direktes **BigBlueButton-Video-Vorstellungsgespräch** im Browser.

### 9.3 White-Label-SaaS-Lösung für externe Pflegeschulen

Externe Pflegeschulen in Deutschland können die gesamte Plattform in zwei Ausprägungen nutzen:

* **Variante A (Direkte Pool-Anbindung):** Die externe Pflegeschule nutzt kostenlos oder sehr günstig unser Kooperations-Modul, um ihren Schülern im letzten Ausbildungsjahr Zugang zu unserem Job-Portal zu bieten.
* **Variante B (Vollwertiges White-Label-ERP & Eigenes Portal):**
  * Die externe Pflegeschule mietet unsere komplette Software (Schulverwaltung, BigBlueButton-Klassenzimmer, Cloud-Drive, PflBG-Rotationsplaner, E-Logbook, Praxisanleiter-App, AZAV-Reporting und Job-Portal) als eigene **White-Label-Instanz**.
  * Über den automatisierten Onboarding-Prozess im Master Admin generiert das System aus den Stammdaten der Schule binnen Minuten deren eigenes System unter eigener Domain (z. B. `campus.pflegeschule-bayern.de`), im eigenen Corporate Design (eigenes Logo, eigene Primär-/Sekundärfarben auf Basis unseres Design-Token-Systems, eigenes Impressum, eigene Dedicated Mobile Apps im App Store) und mit **physisch/logisch strikt getrennter Datenbank und Drive-Instanz**.
  * Die externe Schule tritt gegenüber ihren Schülern und ihren regionalen Kooperationskrankenhäusern komplett als eigener Betreiber auf. Optional kann sie gegen einen Rabatt auf ihre monatliche SaaS-Gebühr aktivieren, dass nicht vermittelte Absolventen zusätzlich in den globalen Bewerber-Pool des Gesamtsystems eingespeist werden.

### 9.4 Strikte DSGVO- & AGG-Compliance im Recruiting-Prozess

Da im Gesundheits- und Bewerberbereich besonders schützenswerte Daten verarbeitet werden, setzt die Architektur folgende juristische Schutzmechanismen technisch zwingend durch:

1. **Strikte Trennung & Koppelungsverbot (Art. 7 Abs. 4 DSGVO):** Die Nutzung des Schul-ERPs (Stundenplan, Noten, E-Logbook, Drive) durch einen Pflegeschüler ist rechtlich und technisch komplett getrennt vom Job-Portal. Ein Schüler ist im Job-Portal standardmäßig **unsichtbar**. Erst durch einen expliziten, freiwilligen **Double-Opt-In** (mit detaillierter Einwilligungserklärung und jederzeitiger 1-Klick-Widerrufsmöglichkeit in der App) wird sein anonymisiertes Profil für den Matching-Pool generiert. Der eigene Ausbildungsbetrieb (Träger der praktischen Ausbildung) kann durch den Schüler auf eine Blacklist gesetzt werden, sodass der eigene Chef nicht sieht, dass sich der Azubi anderweitig orientiert.
2. **Automatisierter AVV-Generator (Art. 28 DSGVO):** Beim digitalen Onboarding einer externen White-Label-Pflegeschule oder eines B2B-Arbeitgebers generiert das System automatisch einen individualisierten **Auftragsverarbeitungsvertrag (AVV nach Art. 28 DSGVO)** inkl. Dokumentation der Technischen und Organisatorischen Maßnahmen (TOMs), der vor Systemfreischaltung digital (eIDAS) gezeichnet werden muss und automatisch im B2B-Drive archiviert wird.
3. **Automatisiertes Löschkonzept nach AGG-Fristen (Cronjob):**
   * Wird ein Kandidat nach erfolgtem Match (Freigabe der Klardaten) von einem Arbeitgeber abgelehnt oder kommt es nach $6\text{ Monaten}$ zu keiner Einstellung, greift das gesetzliche Löschgebot unter Berücksichtigung der Klagefristen des **Allgemeinen Gleichbehandlungsgesetzes (§ 15 Abs. 4 AGG – 2 Monate Geltendmachung + Puffer)**.
   * Ein täglicher Server-Cronjob entzieht dem Arbeitgeber nach exakt **$180\text{ Tagen}$ (6 Monaten)** vollautomatisch die Zugriffsrechte auf die Klardaten und die Cloud-Drive-Freigaben des abgelehnten Bewerbers, löscht lokal gespeicherte Gesprächsnotizen des Arbeitgebers und protokolliert den Löschvorgang revisionssicher im Datenschutz-Audit-Log.

---

## 10. Finanzen, Revolut Payment-Engine, Fördermittel & Preis-/Abo-Kalkulation

Das Finanz-Modul vereint alle internationalen B2C-Zahlungsströme, die komplexe Abrechnung staatlicher deutscher Bildungsträger-Gelder sowie die wiederkehrende B2B-SaaS- und Recruiting-Monetarisierung.

### 10.1 Revolut Business Payment-Engine & KI-Belegprüfung

* **Zentrale Abwicklung über Revolut:** Die gesamte Plattform nutzt die **Revolut Business & Merchant API** als primäres Zahlungs- und Konten-Backend:
  * *B2C-Checkout:* Zahlung von Bewerbungsgebühren, Sprachkursen, Studienkolleg-Raten und Wohnungsmieten per Kreditkarte (Visa/Mastercard), Apple Pay, Google Pay, Revolut Pay und SEPA-Überweisung.
  * *Virtuelle IBANs (vIBANs) pro Student/Mieter:* Über die Revolut API kann jedem internationalen Studierenden oder Mieter eine eigene virtuelle IBAN zugewiesen werden. Jede eingehende Auslandsüberweisung (SWIFT/SEPA) wird dadurch ohne Tippfehler im Verwendungszweck zu $100\%$ automatisch dem richtigen offenen Posten im ERP zugeordnet.
  * *B2B-Recurring-Billing:* Automatischer monatlicher Einzug der SaaS-Gebühren (von White-Label-Schulen) und der Job-Portal-Abos (von Krankenhäusern) via SEPA-Firmenlastschrift oder hinterlegter Firmenkreditkarte.
* **KI-Vision-Belegprüfung für internationale SWIFT-Überweisungen:**
  * Da Banküberweisungen aus Drittstaaten (z. B. Iran, China, Indien, Marokko, Lateinamerika) oft mehrere Tage dauern oder über Mittelsmänner/Wechselstuben laufen, laden Studierende den Zahlungsbeleg (SWIFT MT103 / Bankquittung) in der App hoch (wird automatisch in `05_Rechnungen_&_Quittungen/` im Cloud-Drive gespeichert).
  * Ein Vision-LLM liest den Beleg in Sekundenschnelle aus, extrahiert Überweisungsbetrag, Währung, Datum, Absendername und Referenznummer, prüft das Dokument auf Bildmanipulationen (Photoshop-Detektion) und setzt die Rechnung im ERP auf *"Zahlung angekündigt (Verifiziert)"*, bis der tatsächliche Geldeingang auf dem Revolut-Konto per Webhook bestätigt wird.

### 10.2 Staatliche Fördermittel & B2B-Abrechnung (Pflegeschule)

In der deutschen Pflegeausbildung zahlen nicht die Schüler das Schulgeld, sondern staatliche Stellen und Krankenhausträger. Das ERP bildet diese drei Abrechnungswege nativ ab:

1. **Abrechnung mit dem staatlichen Ausgleichsfonds (§§ 26 ff. PflBG):**
   * Pflegeschulen finanzieren sich über Pauschalen bzw. vereinbarte Ausbildungsbudgets aus dem Landes-Ausgleichsfonds (in NRW verwaltet durch die Bezirksregierungen).
   * Das ERP erstellt auf Basis der immatrikulierten Schülerzahlen zum Stichtag automatisch die elektronischen Meldungen, die Budgetkalkulation sowie die monatlichen Festsetzungs- und Auszahlungsabrufe.
2. **Abrechnung mit der Agentur für Arbeit / Jobcenter (Bildungsgutscheine nach AZAV / SGB III):**
   * Für geförderte Umschüler hinterlegt die Verwaltung die Nummer des Bildungsgutscheins und den Maßnahmebogen im ERP.
   * Das System berechnet die monatlichen Maßnahmekosten pro Teilnehmer (unter automatischer Berücksichtigung von Abbrüchen oder Fehlzeiten) und generiert die fertigen Abrechnungslisten für den Träger-Service der Bundesagentur für Arbeit.
3. **B2B-Kooperationsabrechnung mit Krankenhäusern:**
   * Schicken externe Krankenhäuser oder Pflegeheime ihre Auszubildenden für den Theorieunterricht an die Pflegeschule Aachen, rechnet das ERP die vereinbarten Schulplatzpauschalen oder anteiligen Verwaltungskosten monatlich vollautomatisch mit den Trägern ab.
4. **Verpflichtender E-Rechnungs-Standard (XRechnung & ZUGFeRD):**
   * Da öffentliche Auftraggeber (Behörden, Ausgleichsfonds, Jobcenter, kommunale Kliniken) und alle deutschen B2B-Unternehmen gesetzlich auf elektronische Rechnungen nach der europäischen Norm **EN 16931** angewiesen sind, generiert das ERP jede Rechnung nativ im XML-Format **XRechnung (Version 3.0+)** sowie als hybrides **ZUGFeRD 2.2 PDF/A-3** (inkl. Leitweg-ID-Unterstützung für Behörden) und legt eine Kopie revisionssicher im Cloud-Drive ab.

### 10.3 Wettbewerbsanalyse & Verbindliche Preis-/Abo-Kalkulation

Die Preisstruktur der Plattform ist gezielt so kalkuliert, dass sie etablierte Marktbegleiter massiv unterbietet und gleichzeitig für das Studienkolleg Aachen extrem hohe, wiederkehrende Margen (ARR – Annual Recurring Revenue) erwirtschaftet:

#### A. Preismodell: White-Label-SaaS für externe Pflegeschulen
* **Marktreferenz (Mitbewerber):** Etablierte Pflegeschul-Softwareanbieter (wie *easySoft*, *CareCenter* oder *MSc*) verlangen für Einrichtung, Schulung und Lizenzierung oft $10.000\text{ EUR}$ bis $25.000\text{ EUR}$ Initialkosten sowie laufende Lizenz- und Wartungsgebühren von $1.000\text{ EUR}$ bis $2.500\text{ EUR}$ pro Monat – ohne integriertes Recruiting-Portal, ohne BigBlueButton-Cluster und ohne eigenes Cloud-Drive.
* **Unsere SaaS-Kalkulation (für angeschlossene Fremdschulen):**
  * **Einmalige Onboarding- & Setup-Pauschale:** $1.500\text{ EUR}$ (beinhaltet automatisches Datenbank- & Drive-Provisioning, Custom Domain, CI-Branding, AVV-Abschluss und CSV-Altdatenimport).
  * **Tarif 1 – "Campus Basic" (bis 100 aktive Schüler):** $499\text{ EUR} / \text{Monat}$ (beinhaltet komplettes Schul-ERP, Cloud-Drive, BigBlueButton-Klassenräume, PflBG-Rotationsplaner, E-Logbook, Praxisanleiter-App und AZAV-Audit-Modul).
  * **Tarif 2 – "Campus Pro" (bis 300 aktive Schüler + Job-Portal):** $899\text{ EUR} / \text{Monat}$ (beinhaltet alles aus Basic + eigenes White-Label-Jobportal für die Kooperationskliniken der Schule). *Strategischer Hebel:* Schulen, die zustimmen, dass ihre Absolventen (nach Opt-In) auch im globalen Bewerber-Pool unserer Hauptplattform sichtbar sind, erhalten **$200\text{ EUR} / \text{Monat}$ Pool-Rabatt** (zahlen also nur $699\text{ EUR}$) oder erhalten $20\%$ Revenue-Share bei einer erfolgreichen Vermittlung ihres Schülers an Dritte.
  * **Tarif 3 – "Campus Enterprise" (Unlimitierte Schüler / Schulverbünde):** $1.499\text{ EUR} / \text{Monat}$ (inkl. Dedicated Store Apps im eigenen Apple/Google-Account, HL7/FHIR-KIS-Schnittstellen und DATEV-Direktanbindung).

#### B. Preismodell: Healthcare Job-Portal für B2B-Arbeitgeber (Kliniken & Heime)
* **Marktreferenz (Mitbewerber):** Klassische Stellenbörsen (*StepStone*, *praktischArzt*, *Medi-Karriere*) berechnen ca. $800\text{ EUR}$ bis $1.600\text{ EUR}$ für eine einzige passive Anzeige ($30\text{ Tage}$) ohne Bewerbergarantie. Spezialisierte Pflege-Headhunter und Recruiting-Plattformen (*Medwing*, Personalvermittler) verlangen bei Einstellung $15\%$ bis $25\%$ eines Jahresbruttogehalts – also **$6.000\text{ EUR}$ bis $15.000\text{ EUR}$ pro vermittelter Pflegekraft**.
* **Unsere Disruptive Abo- & Pay-Per-Hire-Kalkulation (für Arbeitgeber):**
  * **Arbeitgeber-Abo "Starter" (Passive Sichtbarkeit):** $399\text{ EUR} / \text{Monat}$ (Verifiziertes Arbeitgeberprofil, Schaltung von bis zu 3 klassischen Stellenanzeigen im Portal und in der Schüler-App).
  * **Arbeitgeber-Abo "Pro Active Sourcing" (Der Standard-Bestseller):** $999\text{ EUR} / \text{Monat}$ (Vollzugriff auf die anonymisierten Bewerber-Pools der freien Jobsuchenden und Absolventen, unlimitierte Suchfilter, bis zu 25 direkte Match-Anfragen inkl. BigBlueButton-Video-Interviews pro Monat).
  * **Arbeitgeber-Abo "Enterprise Pipeline" (Für Großkliniken & Trägerketten):** $1.899\text{ EUR} / \text{Monat}$ (Unlimitierte Match-Anfragen, bis zu 10 Personaler-Zugänge sowie **exklusiver Early-Bird-Zugriff** auf die neuen Abschlussklassen der angeschlossenen Pflegeschulen bereits $6\text{ Monate}$ vor dem Examen, noch bevor Starter/Pro-Kunden diese sehen).
  * **Erfolgsprämie (Pay-Per-Hire Fee bei Einstellung):** **$2.500\text{ EUR}$ pauschal pro erfolgreicher Einstellung** (bzw. $1.500\text{ EUR}$ im Enterprise-Tarif). Sobald ein Match in Twenty CRM zum Status *"Arbeitsvertrag unterschrieben"* führt, generiert das ERP automatisch die Erfolgsrechnung (XRechnung/ZUGFeRD). Für ein Krankenhaus ist dies bis zu $80\%$ günstiger als ein Headhunter; für das Studienkolleg Aachen ist es reiner Gewinn, da die Kandidaten organisch über das eigene Schul- und SaaS-Ökosystem generiert werden.

---

## 11. Technisches High-End-SEO, AI-SEO (GEO / LLMO), Google-Ökosystem & Vollwertiges Besuchertracking

Damit `studienkolleg-aachen.de` (und jeder angeschlossene Partnerstandort) international bei Google, Bing sowie in KI-Antwortsystemen (ChatGPT Search, Perplexity, Google AI Overviews, Claude) auf Platz 1 für Suchbegriffe wie *"Studienkolleg Deutschland"*, *"T-Kurs Aachen"*, *"Medizin studieren Deutschland Studienkolleg"* oder *"Pflegeausbildung Deutschland Visum"* rankt und jeder Website-Besucher lückenlos bis zum Vertragsabschluss in **Twenty CRM** gemessen wird, setzt die Plattform folgende Architektur um:

### 11.1 Technisches High-End-SEO (Next.js SSR/ISR & Mehrsprachiges Programm-SEO)

* **Server-Side Rendering (SSR) & Incremental Static Regeneration (ISR):** Sämtliche öffentlichen Seiten (Kursseiten, Sprachschule, Wohnungs-Exposés, Job-Portal-Stellenanzeigen, Knowledge-Base-Artikel) werden durch Next.js serverseitig vorgerendert und mit einer Time-to-First-Byte ($\text{TTFB} < 80\text{ ms}$) ausgeliefert.
* **Core Web Vitals Optimierung:** Automatische Bildkonvertierung in `AVIF`/`WebP`, kritisches Inline-CSS, lokales Font-Hosting (DSGVO-konform ohne Google-Fonts-Request) und Lazy-Loading für die Short-Video-Reels garantieren einen Google PageSpeed Score von $> 95/100$ auf Mobile und Desktop.
* **Internationale `hreflang`- & Subfolder-Architektur:** Automatische Ausspielung sprachspezifischer URLs (`/de/`, `/en/`, `/ar/`, `/ru/`, `/uk/`, `/es/`, `/fr/`, `/it/`, `/zh/`, `/tr/`) mit bidirektionalen `rel="alternate" hreflang="x"`-Tags und `x-default`-Fallback sowie vollautomatisch generierten, mehrsprachigen XML-Sitemaps (`sitemap-index.xml`, `sitemap-courses.xml`, `sitemap-housing.xml`, `sitemap-jobs.xml`, `sitemap-knowledge.xml`).
* **Programmatic SEO für Länder- & Anabin-Landingpages:** Aus der gescrapten Anabin-Datenbank generiert das CMS vollautomatisch hunderte hochrelevante, mehrsprachige Landingpages nach dem Muster *"Studienkolleg in Deutschland mit [Abschlussname] aus [Herkunftsland] – Voraussetzungen, Notenumrechnung & Visum"* (z. B. für Marokko Baccalauréat, Brasilien Ensino Médio, Türkei Lise Diplomasi, Indien CBSE, China Gaokao).
* **Vollständiges Schema.org JSON-LD Markup:** Jede Unterseite bettet automatisch valides, verschachteltes JSON-LD ein:
  * `EducationalOrganization` & `LocalBusiness` (W2G Academy GmbH, Theaterstr. 30–32, 52062 Aachen, Geo-Koordinaten, AggregateRating $4,9/5$).
  * `Course` & `CourseInstance` (für T-Kurs, M-Kurs, W-Kurs, G-Kurs und alle Deutsch-Intensivkurse inkl. Preis und Startdatum).
  * `Apartment` / `Accommodation` & `Offer` (für jedes verfügbare Zimmer im Wohnungsportal inkl. Fläche nach DIN 277 / WoFlV und Mietpreis).
  * `JobPosting` (für alle öffentlichen Pflege-Stellenanzeigen zur direkten Indexierung in **Google for Jobs**).
  * `FAQPage`, `VideoObject` (für die Campus-Reels) und `BreadcrumbList`.

### 11.2 Vollwertige AI-SEO-Optimierung (GEO – Generative Engine Optimization / LLMO)

Moderne internationale Bewerber fragen zunehmend KI-Systeme (*"Welches Studienkolleg in Deutschland hilft bei Visum und Wohnung in Aachen?"*). Damit LLMs das Studienkolleg Aachen als primäre, autoritative Quelle zitieren und empfehlen, implementiert die Plattform eine dedizierte **AI-SEO-Schicht**:

1. **Dynamische `/llms.txt` & `/llms-full.txt` Bereitstellung:**
   * Unter `https://studienkolleg-aachen.de/llms.txt` und `/llms-full.txt` stellt das System eine täglich aktualisierte, streng strukturierte Markdown-Wissensdatenbank speziell für KI-Crawler (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`) bereit.
   * Diese Datei enthält alle Fakten, Kursstrukturen, Gebühren ($1.200\text{ EUR}$ Sprachkurs, $3.500\text{ EUR}$ Studienkolleg), die $94\%$ Bestehensquote, die $2.800+$ Absolventen, Adresse, Zulassungsvoraussetzungen pro Land, Wohnheim-Garantien und direkte Bewerbungs-Links in einem für Sprachmodelle sofort konsumierbaren Format.
2. **Answer-First Content-Struktur & Entitäts-Optimierung (Knowledge Hub):**
   * Der Bereich *"Knowledge"* von `deinstudienkolleg.de` wird zu einem semantisch vernetzten **AI-Knowledge-Graph** ausgebaut. Jeder Artikel beginnt mit einer präzisen 40-bis-60-Wörter-Direktantwort (Summary-Box), gefolgt von strukturierten Vergleichstabellen, Berechnungsformeln (Bayerische Formel) und verifizierten Fakten, die von RAG-Systemen (Retrieval-Augmented Generation) bevorzugt als direktes Zitat extrahiert werden.
3. **Gezielte `robots.txt`-Steuerung für KI-Agenten:** Explizites Whitelisting aller relevanten Such- und Antwort-KI-Bots auf den öffentlichen Content- und Kursseiten bei gleichzeitigem Schutz der privaten Portal-, Drive- und Admin-Pfade.

### 11.3 Vollintegration des Google-Ökosystems (Analytics, Ads, Indexing & Business)

1. **Google Tag Manager (GTM Web + Server-Side Container):**
   * Betrieb eines eigenen **Server-Side Google Tag Managers (sGTM)** auf einer Subdomain (`metrics.studienkolleg-aachen.de` auf den eigenen deutschen Servern). Dadurch werden AdBlocker/ITP legal umgangen, Ladezeiten im Browser minimiert und IP-Adressen vor einer Weiterleitung an Google datenschutzkonform nach DSGVO/TTDSG anonymisiert.
2. **Google Analytics 4 (GA4) mit Enhanced Conversions & E-Commerce-Events:**
   * Lückenloses Event-Tracking über die gesamte Funnel-Kette: `view_course`, `start_application`, `upload_anabin_docs`, `ai_precheck_green`, `book_consultation`, `add_to_cart_language_course`, `purchase_revolut_completed`, `initiate_housing_lease`, `job_portal_match_accepted`.
3. **Google Consent Mode v2 (Advanced) & CMP:**
   * Weiterentwicklung des bestehenden Cookie-Banners von `deinstudienkolleg.de` zu einer zertifizierten Consent-Management-Plattform mit nativer Unterstützung für **Google Consent Mode v2** (`ad_storage`, `analytics_storage`, `ad_user_data`, `ad_personalization`).
4. **Google Ads Offline-Conversion-Import (aus Twenty CRM):**
   * Klickt ein Bewerber auf eine Google-Anzeige, wird die `GCLID` (Google Click ID) beim Absenden des Bewerbungsformulars in **Twenty CRM** gespeichert. Zahlt der Bewerber $3\text{ Wochen}$ später seine erste Semestergebühr via Revolut, meldet Twenty CRM diese echte Umsatz-Conversion automatisch über die **Google Ads API** zurück, sodass der Google-Bidding-Algorithmus auf zahlende Studierende statt nur auf bloße Formular-Leads optimiert.
5. **Google Search Console API & Google Indexing API:**
   * Neue Kurse, freie Wohnungen im Wohnungsportal und neue Pflege-Stellenanzeigen werden im Moment ihrer Veröffentlichung automatisch über die **Google Indexing API** an Google gemeldet und sind binnen Minuten im Index und in *Google for Jobs* sichtbar.
   * Live-Integration der Google-Bewertungen (Google Places API für W2G Academy GmbH / Studienkolleg Aachen) mit automatischer Synchronisation auf der Website.

### 11.4 Vollwertiges First-Party-Besuchertracking, Behavioral Analytics & Lead-Attribution

Zusätzlich zu Google Analytics betreibt die Plattform auf den eigenen Servern eine **100% DSGVO-konforme First-Party-Besuchertracking- & Customer-Journey-Engine** (ohne Datenweitergabe an Dritte), die direkt in das Master Admin Panel und **Twenty CRM** integriert ist:

* **Lückenlose Multi-Touch-Attribution & Session-Stitching:**
  * Jeder Besucher auf `prev.studienkolleg-aachen.de` bzw. `studienkolleg-aachen.de` erhält eine kryptographische First-Party-Visitor-ID.
  * Das System protokolliert in Echtzeit: Herkunftsland (Geo-IP), Spracheinstellung, Einstiegsseite, Referrer, UTM-Kampagnenparameter (`utm_source`, `utm_medium`, `utm_campaign`, `utm_content`), Affiliate-/Agentur-Sub-IDs, angesehene Kurse, Verweildauer auf Wohnungs-Exposés, Wiedergabedauer der Campus-Short-Videos und Abbruchpunkte im Bewerbungsformular (Funnel-Drop-off-Analyse).
* **Vom anonymen Besucher zur vollständigen Twenty-CRM-Timeline (Identity Resolution):**
  * Sobald der Besucher sich für ein Beratungsgespräch einträgt, den KI-Sprachtest startet oder das neue Bewerbungsformular absendet, verknüpft das System seine gesamte bisherige anonyme Besuchshistorie rückwirkend mit seinem neuen Kontakt-Datensatz in **Twenty CRM**.
  * Der Studienberater sieht in Twenty CRM auf einen Blick: *"Bewerber kam vor 4 Tagen über Instagram-Reel (M-Kurs), hat sich 3x die Wohnungen in Aachen angesehen, den Artikel zur Bayerischen Formel gelesen und heute sein Zeugnis hochgeladen."*
* **Heatmaps, Scrollmaps & Formular-Feld-Analyse:**
  * Integrierte Aufzeichnung von anonymisierten Klick-Heatmaps und Formular-Interaktionen, um sofort zu erkennen, bei welchem Schritt oder Dokumenten-Upload internationale Bewerber zögern, inklusive automatischer Auslösung eines kontextsensitiven KI-Chat-Popups oder WhatsApp-Hilfsangebots bei drohendem Formularabbruch (Exit-Intent-Trigger).

---

## 12. Technische Infrastruktur, Microservices & Schnittstellen-Spezifikation

Um höchste Ausfallsicherheit, Skalierbarkeit und strikte Einhaltung deutscher Datenschutzgesetze zu gewährleisten, wird die gesamte Systemlandschaft auf folgendem modernen Tech-Stack implementiert:

* **Core-ERP & SaaS-Orchestrator:** **Laravel 13 (PHP 8.3+)** als API-zentrierter Kern für Geschäftslogik, Multi-Tenancy, Rechnungsstellung, Berechtigungssystem, BigBlueButton-/Drive-Orchestrierung und Modulsteuerung.
* **CRM & Workflow-Engine:** **Twenty CRM** (Node.js, TypeScript, GraphQL, Webhooks) als selbstgehosteter Container-Cluster. Synchronisation über asynchrone Message-Queues (Redis / RabbitMQ).
* **Open-Source Videokonferenz-Cluster:** **BigBlueButton (BBB 3.0+)** auf dedizierten Bare-Metal-Servern mit **Scalelite** Load-Balancer, eigenem TURN/STUN-Server (`coturn`) und automatisierter MP4-Recording-Pipeline ins Cloud-Drive.
* **Cloud-Drive-Onlinespeicher-Core:** **Self-Hosted Nextcloud / OwnCloud Enterprise Storage Core** (angebunden über WebDAV / OCS REST API an S3/R2 Object Storage) inkl. **Collabora Online / OnlyOffice** für gemeinsames Bearbeiten von Dokumenten im Browser.
* **KI- & Scraping-Microservices:** **Python 3.11+ mit FastAPI**.
  * *Service 1 (Anabin-Bot):* Playwright Headless Chromium + BeautifulSoup4 + SQLAlchemy.
  * *Service 2 (Vision & OCR):* Dokumenten-Vorverarbeitung (OpenCV/PDF2Image) + multimodales Vision-LLM (selbstgehostet oder über DSGVO-konforme EU-Endpunkte mit Zero-Data-Retention) für Zeugnisse, Pässe, Lebensläufe und SWIFT-Überweisungsbelege.
  * *Service 3 (RAG-Support-Bot, Whisper-Transkription & Sprachtest):* Vektordatenbank (**pgvector** in PostgreSQL) für den 24/7 First-Level-Support-Chatbot (beantwortet Fragen zu Visum, Anabin, Miete und Kursen in 20+ Sprachen), für die GER-Sprachbewertung sowie für die automatische Transkription von BigBlueButton-Vorlesungen.
* **Web-Frontends:** **Next.js (React, TypeScript, Tailwind CSS)** im Designsystem von `deinstudienkolleg.de` mit Server-Side Rendering (SSR) für maximale SEO-/AI-SEO-Performance (Sprachschule, Wohnungsportal, Job-Portal, Schul-CMS) und schnellen App-Router-Dashboards (Studierenden-Portal, B2B-Arbeitgeber-Portal).
* **Mobile Applikationen:** **Flutter (Dart)** für iOS und Android (Student/Parent App, Teacher/Staff App, Praxisanleiter-App) mit nativer Kamera-/QR-Integration, Biometrie-Login (FaceID/TouchID), integriertem Drive-Viewer, BigBlueButton-WebRTC-Ansicht, Offline-Caching für Stundenpläne/E-Logbooks und Screenshot-Blocker bei Prüfungen.
* **Echtzeit-Kommunikation:** **Laravel Reverb** (WebSockets) für den Echtzeit-Chat, Live-Stundenplan-Updates und BigBlueButton-Raumstatus, **Firebase Cloud Messaging (FCM)** für mobile Push-Notifications sowie Anbindung der offiziellen **WhatsApp Business Cloud API**.
* **Datenbank-Architektur & Mandanten-Isolierung:** **PostgreSQL 16+**. Jeder Mandant (Eigenstandort Aachen, Partnerstandort, externe White-Label-Pflegeschule) erhält ein physisch/logisch isoliertes Datenbank-Schema (`tenant_aachen`, `tenant_school_xyz`), sodass Cross-Tenant-Data-Leaks auf SQL-Ebene architektonisch ausgeschlossen sind.
* **Dateispeicher (Object Storage):** S3-kompatibler Cloud-Speicher (**Cloudflare R2** mit EU-Jurisdiction oder **Hetzner Object Storage** in Deutschland) als primäres Backend für das Cloud-Drive und alle BBB-Aufzeichnungen. Sämtliche sensiblen Dokumente werden Server-Side verschlüsselt (AES-256) abgelegt und sind ausschließlich über kryptographisch signierte, kurzlebige **Pre-Signed URLs** oder authentifizierte Drive-Streams abrufbar.
* **Medizinische & Kaufmännische Interoperabilität:**
  * **HL7 FHIR R4 Schnittstelle:** Standardisierte RESTful-API zum Austausch von Auszubildenden-Stammdaten, Einsatzplänen und Abwesenheiten mit den Krankenhausinformationssystemen (KIS wie *SAP IS-H*, *Dedalus ORBIS*, *CGM Medico*) und Dienstplanprogrammen (*ATOSS*, *TimeOffice*) der Kooperationskliniken.
  * **DATEV-Schnittstelle:** Export-Engine für Finanzbuchhaltung (EXTF/XML) und Lohnbuchhaltung (LODAS / Lohn und Gehalt).
* **Hosting, Staging & Deployment:** Vollständig containerisiert via **Docker / Docker Swarm (oder Kubernetes)** auf dedizierten Servern in deutschen, nach ISO/IEC 27001 zertifizierten Rechenzentren (z. B. Hetzner Falkenstein/Nürnberg) mit automatischer CI/CD-Pipeline auf die Staging-Umgebung `prev.studienkolleg-aachen.de` und Zero-Downtime-Promotion auf `studienkolleg-aachen.de`.

---

## 13. Verbindliche Deutsche DIN-Normen, ISO-Standards & Rechtsgrundlagen

Da der Hauptsitz des Betreibers (W2G Academy GmbH, Theaterstr. 30–32, 52062 Aachen) in Deutschland liegt und sowohl Bildungs-, Immobilien- als auch Gesundheitsdaten verarbeitet werden, ist die gesamte Plattform-Architektur zwingend nach den folgenden deutschen und internationalen Normen in ihrer jeweils aktuellen, vollwertigen Fassung auszulegen und zu betreiben:

### 13.1 Deutsche DIN-Normen, Ergonomie- & Immobilienrechtliche Vorschriften

1. **DIN EN ISO 9241 (insb. Teil 110: Grundsätze der Dialoggestaltung & Teil 210: Prozess zur Gestaltung gebrauchstauglicher interaktiver Systeme):**
   * *Anwendung im System:* Verbindliche Grundlage für das aus `deinstudienkolleg.de` abgeleitete UI/UX-Designsystem und sämtliche Dashboards (Studierenden-Portal, Dozenten-Portal, B2B-Arbeitgeber-Portal, Admin-Konsole, Drive- und BigBlueButton-Ansichten) hinsichtlich Aufgabenangemessenheit, Erwartungskonformität, visueller Klarheit und Fehlertoleranz.
2. **DIN 277 (Grundflächen und Rauminhalte im Hochbau – aktuelle Fassung DIN 277:2021-08):**
   * *Anwendung im System:* Verbindliche Grundlage im Wohnungsportal-Backend zur exakten Ermittlung und Trennung von Brutto-Grundfläche (BGF), Konstruktions-Grundfläche (KGF) und Netto-Raumfläche (NRF), unterteilt in Nutzfläche (NUF), Technikfläche (TF) und Verkehrsfläche (VF). Dient als unanfechtbare Basis für die Kalkulation der Gewerbemieten (Schulräume) und die rechtssichere Umlage der Betriebskosten.
3. **Wohnflächenverordnung – WoFlV (Verordnung zur Berechnung der Wohnfläche vom 25. November 2003):**
   * *Anwendung im System:* Zwingende Berechnungslogik für alle im Wohnungsportal an Studierende und Pflegeschüler vermieteten Wohnräume. Das System erzwingt die korrekte Anrechnung von Grundflächen nach lichten Höhen ($100\%$ ab $2,00\text{ m}$, $50\%$ zwischen $1,00\text{ m}$ und $2,00\text{ m}$, $0\%$ unter $1,00\text{ m}$) sowie von Balkonen, Loggien und Terrassen (in der Regel $25\%$), um Mietminderungsansprüche wegen Flächenabweichungen auszuschließen.
4. **Gebäudeenergiegesetz – GEG (Gesetz zur Einsparung von Energie und zur Nutzung erneuerbarer Energien zur Wärme- und Kälteerzeugung in Gebäuden):**
   * *Anwendung im System:* Pflichtfelder nach § 87 GEG für alle Immobilieninserate im Wohnungsportal (Art des Energieausweises, Endenergiebedarf/-verbrauch, wesentlicher Energieträger für die Heizung, Baujahr und Energieeffizienzklasse) sowie automatische Beifügung des Energieausweises im Cloud-Drive bei digitaler Mietvertragsunterzeichnung (§ 80 GEG).
5. **DIN 5008 (Schreib- und Gestaltungsregeln für die Text- und Informationsverarbeitung – aktuelle Fassung DIN 5008:2020-03):**
   * *Anwendung im System:* Verbindlicher Formatierungsstandard für sämtliche vom System automatisch generierten PDF-Dokumente, Zulassungsbescheide, Rechnungen, Mahnungen, Mietverträge, Behördenanschreiben und Bescheinigungen (insb. korrekte Datumsformate nach ISO/DIN `JJJJ-MM-TT` bzw. `TT.MM.JJJJ`, Währungsformatierungen, Anschriftenfelder für Fensterbriefumschläge nach DIN 676 sowie Gliederungs- und Tabellenstrukturen).
6. **DIN EN 301 549 & BITV 2.0 / Barrierefreiheitsstärkungsgesetz (BFSG):**
   * *Anwendung im System:* Europäische und deutsche Norm für digitale Barrierefreiheit von IKT-Produkten und Webseiten (WCAG 2.1 Level AA Konformität). Da Dienstleistungen im elektronischen Geschäftsverkehr für Verbraucher (Sprachschulbuchung, Wohnungsportal, Bewerbung) angeboten werden, sind sämtliche Next.js-Frontends, Dashboards und Flutter-Apps nach den Vorgaben des **Barrierefreiheitsstärkungsgesetzes (BFSG)** barrierefrei (Screenreader-Kompatibilität, Tastaturbedienbarkeit, Kontrastverhältnisse) gestaltet.

### 13.2 Internationale & Europäische ISO-Normen (in deutscher Übernahme als DIN EN ISO)

1. **DIN EN ISO/IEC 27001 (Informationssicherheit, Cybersicherheit und Schutz der Privatsphäre – Informationssicherheitsmanagementsysteme - ISMS):**
   * *Anwendung im System:* Maßgeblicher Architekturstandard für die gesamte Server-Infrastruktur (inkl. BigBlueButton- und Cloud-Drive-Servern), Verschlüsselung (Data-at-Rest via AES-256 und Data-in-Transit via TLS 1.3), das Rollen- und Berechtigungskonzept (Need-to-know-Prinzip), das Patch-Management, die Protokollierung sicherheitsrelevanter Events (SIEM/Audit-Logs) und das Hosting in ISO-27001-zertifizierten deutschen Rechenzentren.
2. **DIN EN ISO/IEC 27701 (Erweiterung zu ISO/IEC 27001 und ISO/IEC 27002 für das Datenschutzmanagement – PIMS):**
   * *Anwendung im System:* Spezifische Norm für das Privacy Information Management System. Regelt die technische Umsetzung von "Privacy by Design" und "Privacy by Default", die Trennung zwischen Verantwortlichem (Controller – z. B. externe Pflegeschule) und Auftragsverarbeiter (Processor – SaaS-Betreiber), das Einwilligungsmanagement (Consent Mode v2, Double-Opt-In im Job-Portal) und die automatisierten Löschroutinen.
3. **ISO/IEC 27017 & ISO/IEC 27018 (Informationssheitskontrollen für Cloud-Dienste und Schutz personenbezogener Daten in Public Clouds):**
   * *Anwendung im System:* Verbindliche Vorgabe für die Multi-Tenant-Isolierung (PostgreSQL Schema-per-Tenant, isolierte Cloud-Drive-Instanzen und S3-Buckets mit Pre-Signed URLs) zur Verhinderung von Mandanten-Überschneidungen im SaaS-Betrieb.
4. **DIN EN ISO 9001 (Qualitätsmanagementsysteme – Anforderungen) & ISO 21001 (Managementsysteme für Bildungsorganisationen – EOMS):**
   * *Anwendung im System:* Grundlage für das integrierte Qualitätsmanagement- und Evaluationsmodul (digitale Kursevaluationen, Dozentenbewertungen, Beschwerdemanagement in Twenty CRM und kontinuierliche Prozessverbesserung), welches zugleich die Basis für die deutsche AZAV-Trägerzulassung bildet.

### 13.3 Fachspezifische Gesetze, Verordnungen & Technische Standards (Gesundheit, Bildung, Finanzen, Telemedien)

1. **DSGVO (Verordnung (EU) 2016/679), BDSG & TDDDG (ehem. TTDSG):**
   * *Anwendung im System:* Vollständige Umsetzung der Betroffenenrechte (Datenexport auf Knopfdruck nach Art. 15/20 DSGVO direkt aus dem Cloud-Drive, Recht auf Löschung nach Art. 17 DSGVO), rechtskonforme Cookie- und Tracking-Einwilligung nach § 25 TDDDG (inkl. Google Consent Mode v2), automatischer AVV-Generator nach Art. 28 DSGVO für White-Label-Schulen und Arbeitgeber sowie ausschließliche Datenverarbeitung (inkl. Video-Streaming via BigBlueButton und Dateispeicherung im Drive) auf eigenen Servern innerhalb Deutschlands / der EU.
2. **Allgemeines Gleichbehandlungsgesetz (AGG):**
   * *Anwendung im System:* Diskriminierungsfreies, anonymisiertes Erst-Matching im Healthcare Job-Portal sowie der automatisierte **180-Tage-Lösch-Cronjob** für abgelehnte Bewerberprofile (inkl. Widerruf der Drive-Freigaben) zur rechtssicheren Abwehr und Dokumentation im Rahmen der Fristen nach § 15 Abs. 4 AGG.
3. **Pflegeberufegesetz (PflBG) & Ausbildungs- und Prüfungsverordnung für die Pflegeberufe (PflAPrV):**
   * *Anwendung im System:* Zwingende gesetzliche Logik für den Theorie- ($2.100\text{ Std.}$) und Praxis-Rotationsplaner ($2.500\text{ Std.}$ inkl. aller Pflichteinsätze nach Anlage 7 PflAPrV), den Kompetenznachweis nach Anlage 2 PflAPrV, die 10%-Praxisanleitungsquote (§ 4 PflAPrV), die 24-Stunden-Fortbildungspflicht der Praxisanleiter sowie die 10%-Fehlzeitengrenze (§ 13 PflBG) und die Abrechnung über den Ausgleichsfonds (§§ 26–36 PflBG).
4. **AZAV (Akkreditierungs- und Zulassungsverordnung Arbeitsförderung) & SGB III:**
   * *Anwendung im System:* Gesetzliche Voraussetzung für die Annahme und Abrechnung von Bildungsgutscheinen der Agentur für Arbeit und der Jobcenter. Abgesichert durch die Echtzeit-Fehlzeitenüberwachung (inkl. BigBlueButton-Präsenztracking), das Maßnahmen-Tracking und den 1-Klick-AZAV-Audit-Report für fachkundige Stellen (TÜV/DEKRA).
5. **eIDAS-Verordnung (Verordnung (EU) Nr. 910/2014 über elektronische Identifizierung und Vertrauensdienste):**
   * *Anwendung im System:* Rechtsgrundlage für die elektronischen Signaturen im System – insbesondere für den digitalen Abschluss von Wohnungsmietverträgen, Schul-/Ausbildungsverträgen, Auftragsverarbeitungsverträgen (AVV) sowie die digitale Gegenzeichnung der Praxisstunden durch Praxisanleiter in der Krankenhaus-App.
6. **EN 16931, XRechnung & ZUGFeRD (E-Rechnungsverordnung / Wachstumschancengesetz) sowie GoBD:**
   * *Anwendung im System:* Gesetzlicher Pflichtstandard für die Ausstellung und den Empfang strukturierter elektronischer Rechnungen im B2G-Verkehr (Ausgleichsfonds, Jobcenter) und B2B-Verkehr (Krankenhäuser, Partnerschulen). Sämtliche Buchungs-, Rechnungs- und Belegprozesse im ERP und Cloud-Drive sind unveränderbar, nachvollziehbar und revisionssicher nach den **Grundsätzen zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form (GoBD)** ausgelegt.
7. **Gemeinsamer Europäischer Referenzrahmen für Sprachen (GER / CEFR):**
   * *Anwendung im System:* Verbindlicher Bewertungsmaßstab des Europarats für den adaptiven KI-Einstufungstest, die Kursstruktur (A1 bis C1) der Sprachschule und die Vorkorrektur von Texten.
8. **HL7 FHIR R4 (Fast Healthcare Interoperability Resources):**
   * *Anwendung im System:* Internationaler und deutscher Standard (auch im Rahmen der Telematikinfrastruktur / ISiK) für den strukturierten, sicheren Datenaustausch zwischen unserem Pflegeschul-ERP und den Softwaresystemen der kooperierenden Krankenhäuser.