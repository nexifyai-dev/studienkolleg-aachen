# 03_projektprofil_und_scope.md

## Projektprofil

### Projektname
**WaytoGermany Platform / Studienkolleg Portal**

### Kurzbeschreibung
Zentrale, mandantenfähige Plattform zur Verwaltung von Leads, Bewerbern, Dokumenten, Kommunikation, Rechnungen, Aufgaben, Kursen und Partnerbeziehungen für das WaytoGermany-/Studienkolleg-Aachen-Ökosystem.

### Verantwortliche Marke / Struktur
- **Verifiziert:** WaytoGermany ist die übergreifende System- und Projektbezeichnung.
- **Verifiziert:** Studienkolleg Aachen ist ein öffentlicher Angebots- und Markenbaustein.
- **Verifiziert:** W2G Academy GmbH tritt öffentlich als rechtliche Betreiberin auf.
- **Offen / nicht verifiziert:** finale, konsistente Marken- und Legal-Hierarchie auf allen Webseiten.

### Projekttyp
Hybrid aus:
- öffentlicher Conversion- und Informationswebseite,
- operativer Plattform,
- Bewerberportal,
- Agentur-/Affiliateportal,
- Kurs- und Schulungsbereich,
- Reporting- und Verwaltungsoberfläche.

## Zielbild

### Verifiziert
Das System soll die heutige manuelle Bearbeitung über E-Mail, WhatsApp, Excel, Einzellösungen und Drittanbieterportale in einer Plattform bündeln und weitgehend automatisieren.

### Plausibel abgeleitet
Das Zielbild besteht aus drei Schichten:
1. **Public Web Layer** für Discovery, Vertrauen, Angebotslogik, Beratung und Lead-Erfassung.
2. **Operations Layer** für CRM, Pipelines, Dokumente, Kommunikation, Zahlungen, Aufgaben, Reporting.
3. **Education / Service Layer** für Kurse, Prüfungen, Hilfen, Wissensdatenbank und Folgeangebote.

## Scope

### Muss-Scope Release 1
1. Zentrale Bewerberidentität mit Mehrfachzuordnung zu Bereichen.
2. Studienkolleg-Kernpipeline produktiv.
3. Lead-Ingest aus Formularen, Mail-/Manuell-Import und Partnerquellen.
4. Dublettenprüfung.
5. Rollenbasiertes Webportal für Superadmin, Admin, Staff, Applicant.
6. Basiszugang für Agenturen/Affiliates auf eigene Fälle.
7. Dokumentenmanagement mit sicherem Upload, Prüfstatus, Kommentaren und Nachforderung.
8. Bewerberportal mit Dashboard, Aufgaben, Status, Dokumenten, Nachrichten, Rechnungen.
9. Rechnungsstellung und Zahlungsstatus für den Studienkolleg-Kernprozess.
10. E-Mail-basierte Benachrichtigungen; WhatsApp optional scharf schaltbar nach Budget-/Policy-Freigabe.
11. Auditierbare Aktivitäten, Webhook-Idempotenz, Consent-Tracking und Automation-Logs.
12. Public Website / Landing- und Conversion-Logik mit sauberer Claim-Policy und rechtlich konsistenten Seiten.

### Soll-Scope nach Release 1
1. Sprachschule als vollwertiger Workspace.
2. Pflegefachschule und Arbeit/Ausbildung als produktive Fachbereiche.
3. Kursbuchung und direkter Kursabruf für interne Videokurse.
4. externe LMS-/Meeting-Integration.
5. Affiliate-Dashboard mit sichtbaren KPIs und Provisionen.
6. erweiterte Reporting-Exporte.
7. PWA-Härtung mit Push.

### Kann-Scope später
1. native Mobile App,
2. OCR-/KI-Vorprüfung von Dokumenten,
3. White-Label-Subdomains,
4. teilautomatisierter Behördenversand,
5. Matching für Unternehmen / Bewerber,
6. Botschaftsmonitoring,
7. tiefe Marketing-Automationen.

## Nicht-Scope Release 1

1. Vollautomatisches Matching von Bewerbern an Unternehmen.
2. Vollständig automatisierter Behördenversand.
3. produktionsreife native Stores-App.
4. vollautomatisches OCR-Freigabesystem ohne Human Review.
5. beliebig viele White-Label-Subdomains mit eigenem Frontend.
6. Inkasso- oder Steuerautomatik ohne rechtliche Freigabe.

## Primäre Ziele

### Geschäftsziele
- schnellere Bearbeitung und höhere Transparenz,
- höhere Abschlussrate,
- weniger Medienbrüche,
- skalierbarer Betrieb bei steigender Leadmenge,
- Grundlage für Cross-Sell zwischen Studienkolleg, Sprachschule, Pflege und Arbeit.

### Nutzerziele
- einfacher Zugang,
- klarer nächster Schritt,
- transparente Statussicht,
- sicherer Dokumentenprozess,
- gebündelte Kommunikation,
- nachvollziehbare Rechnungs- und Kurslogik.

### Betriebsziele
- weniger manuelle Koordination,
- klare Zuständigkeiten,
- reduzierter Inbox-/Excel-Aufwand,
- bessere Teamsteuerung,
- auditierbare Vorgänge.

### Qualitätsziele
- keine Schattenprozesse,
- keine ungesicherten Dokumente,
- keine widersprüchlichen Status,
- keine ungetesteten Rechtepfade,
- klare DoD- und Release-Gates.

## Prioritäten

### Priorität 1
Datenmodell, RLS, Applicant Journey, Dokumentenprozess, Rechnungs-/Zahlungsstatus, Audit, Public-Claim-Sicherheit.

### Priorität 2
Agency/Affiliate-Funktionalität, Course Release, Reporting, PWA-Veredelung.

### Priorität 3
Native App, White-Label-Ausbau, OCR, Matching, Embassy Monitoring.

## Risiken

### Verifiziert
- Steuer- und Payment-Logik unklar.
- RLS-Fehler wären geschäftskritisch.
- Widersprüchliche öffentliche Preis-/Legal-Angaben untergraben Vertrauen.
- WhatsApp-Kosten und 24h-Fenster sind operativ relevant.
- Ohne Queueing drohen Timeouts bei Webhooks, PDFs und Provisioning.

### Plausibel abgeleitet
- Scope-Explosion zwischen Plattformziel und MVP.
- doppelte oder widersprüchliche Kommunikation, falls Mailboxen und Plattform parallel „führend“ bleiben.
- hoher Migrationsaufwand, wenn Legacy-Daten unsauber sind.

## Annahmen

### Plausibel abgeleitet
1. Release 1 wird als Studienkolleg-first-MVP freigegeben.
2. Mobile Web/PWA deckt den mobilen Bedarf im Start ab.
3. Öffentliche Seiten bleiben mehrsprachig, die operative Backoffice-Oberfläche primär deutsch.
4. Kritische transaktionale Kommunikation läuft zunächst über E-Mail; WhatsApp wird nach Kosten-/Policy-Entscheid ergänzt oder gestaffelt aktiviert.

## Abhängigkeiten

1. finaler Commercial/Legal Source of Truth,
2. finalisierte Dokumentenmatrix je Bereich und Pipeline-Stufe,
3. abgestimmte Rechte- und Partnerstruktur,
4. definierte Nachrichtentemplates,
5. geklärte Zahlungs-/Refund-/VAT-Logik,
6. freigegebene Design-/Brand-Hierarchie.

## Strategische Scope-Entscheidung

**Empfehlung:** Das Projekt wird in der Umsetzung **nicht** als „alles gleichzeitig“ behandelt.  
Es wird als **plattformfähiges Kernsystem mit gestufter Geschäftsbereichsaktivierung** umgesetzt:

- **Release 1:** Studienkolleg Core + gemeinsame Plattformfundamente.
- **Release 2:** Sprachschule + Kurs-/LMS-Schicht + Agentur-/Affiliate-Härtung.
- **Release 3:** Pflege, Arbeit/Ausbildung, White-Label- und B2B-Ausbau.
