# NeXify AI - Workflow-Vorschlag für Studienkolleg

**Programme, Kurse, Teilnehmer, Lehrkräfte, Stundenplan, Anwesenheit und Zertifikate**

Stand: 01.10.2026 | Version 1.0 | Zur fachlichen Abstimmung

Chat it. Automate it.

## Zielbild und Gesamtprozess

01 / Ein durchgängiger Ablauf für Verwaltung, Lehrkräfte und Teilnehmer

NeXify AI schlägt einen zentral gesteuerten Workflow für Programme, Kurse, Teilnehmer und Lehrkräfte vor. Buchung, Freischaltung, Stundenplan, Anwesenheit und Zertifikate greifen ineinander und verwenden dieselbe fachliche Datenbasis.

> Kernziel: Nach bestätigter Zahlung oder berechtigter manueller Freigabe erhält der Teilnehmer Zugang zur gebuchten Durchführung - auch bereits vor dem ersten Unterrichtstag.

| Schritt | Ablauf und Ergebnis |
| --- | --- |
| 1. Angebot vorbereiten | Kurse und Programme anlegen oder aus Excel importieren; fehlende Angaben nachvollziehbar ergänzen. |
| 2. Durchführung planen | Zeitraum, enthaltene Kurse, Lehrkräfte, Unterrichtstermine, Räume, Online-Meetings und Plätze zuordnen. |
| 3. Buchung freischalten | Zahlung oder manuelle Freigabe prüfen; Plätze und erforderliche Mitgliedschaften konsistent bereitstellen. |
| 4. Unterricht begleiten | Individuelle Stundenpläne anzeigen; Anwesenheiten erfassen und Online-Teilnahmedaten zur Prüfung bereitstellen. |
| 5. Nachweise ausstellen | Abschlussbedingungen prüfen; Kurs- und Programmzertifikate als versionierte PDF-Dokumente bereitstellen. |
| Parallel: Gebäudeliste | Gebäude-Check-in und Check-out separat führen; aktuelle Notfallliste für berechtigte Personen exportieren. |

### Klare Zuständigkeiten

Die Kursadministration pflegt Angebote und Zuordnungen. Berechtigte Backoffice-Mitarbeiter bestätigen Zahlungen oder erteilen manuelle Freigaben. Lehrkräfte erfassen und prüfen Anwesenheiten ihrer Termine. Teilnehmer sehen ihre eigenen Daten und melden Unstimmigkeiten. Die Zertifikatsverantwortlichen entscheiden über Freigaben und Neuausstellungen.

Das Dokument beschreibt den vorgeschlagenen Sollprozess. Es ist keine Bestätigung einer bereits implementierten Integration, kein Preisangebot und keine Zusage eines Fertigstellungstermins.

## Kurse, Programme und Excel-Import

02 / Wiederverwendbare Stammdaten und konkrete Durchführungen

### Vorlage und Durchführung trennen

Eine Kursvorlage beschreibt beispielsweise „Mathematik 1“. Die konkrete Durchführung legt Jahrgang, Start, Ende, Lehrkräfte und Unterrichtstermine fest. Programme wie Studienkolleg M, T oder W bestehen aus mehreren zugeordneten Kursdurchführungen. Pflichtkurse, Reihenfolge und Zertifikatsrelevanz werden ausdrücklich hinterlegt.

| Bereich | Vorgesehene Angaben |
| --- | --- |
| Kurs | Bezeichnung; für Teilnehmer sichtbare Beschreibung; Kursstart und Kursende; UE pro Woche; Gesamt-UE; Lehrkraft bzw. Lehrkräfte; Preis; Plätze für Präsenz und Online. |
| Kurszertifikat | Zertifikatsbezeichnung; auszuweisende UE; Inhalte; zugehörige Vorlage und Abschlussbedingungen. |
| Programm | Bezeichnung; Beschreibung; Zeitraum; enthaltene Kurse; Gesamt- oder Einzelbuchung; Programmpreis und Zertifikatskonfiguration. |
| Interne Verwaltung | Interne Bemerkungen; eindeutige Kennung; Bearbeitungsstatus; Änderungsverlauf. Interne Bemerkungen sind für Teilnehmer nicht sichtbar. |

### Vorgeschlagener Importablauf

1. Excel-Datei anhand einer bereitgestellten Vorlage hochladen. 2. Spalten zuordnen und Vorschau anzeigen. 3. Pflichtfelder, Kennungen, Datumswerte, Preise und Kapazitäten prüfen. 4. Neue Datensätze und Änderungen getrennt darstellen. 5. Den geprüften Import ausführen und ein Ergebnisprotokoll bereitstellen.

Fehlende nichtkritische Angaben dürfen als Entwurf gespeichert und später ergänzt werden. Vor Buchbarkeit und Freischaltung müssen die jeweils notwendigen Angaben vollständig sein. Fehlerhafte Zeilen erhalten eine konkrete Meldung; bestehende Daten werden bei wiederholtem Import nicht ungeprüft überschrieben.

> Empfehlung: Stabile Kurs- und Programmkennungen verhindern Duplikate. Verknüpfungen zwischen Programmen und Kursen werden bereits in der Importvorschau geprüft.

Änderungen an Vorlagen verändern laufende oder abgeschlossene Durchführungen nicht automatisch. Anpassungen bestehender Programme werden mit ihren Auswirkungen auf Teilnehmer und Zertifikate nachvollziehbar freigegeben.

## Buchung, Plätze und Freischaltung

03 / Verlässlicher Zugang nach Zahlung oder manueller Freigabe

### Vorgeschlagener Ablauf

Eine Buchung bezieht sich auf einen konkreten Kurs- oder Programmdurchlauf. Zahlungsbestätigung und manuelle Freigabe lösen denselben Aktivierungsprozess aus. Eine manuelle Freigabe erfordert eine berechtigte Rolle und wird mit Person, Zeitpunkt und Begründung protokolliert.

| Situation | Vorgesehenes Verhalten |
| --- | --- |
| Noch keine Freigabe | Die Buchung bleibt ausstehend; es erfolgt keine Unterrichtsfreischaltung. |
| Freigabe vor Kursstart | Der Teilnehmer sieht das gebuchte Angebot und den Stundenplan im Dashboard. Die Öffnung einzelner Lerninhalte kann separat terminiert werden. |
| Programmbuchung | Das System ordnet den Teilnehmer dem Programm und allen vorgesehenen erforderlichen Kursen zu. |
| Doppelte Zahlungsnachricht | Der vorhandene Vorgang wird erkannt. Es entstehen keine zusätzlichen Plätze, Mitgliedschaften oder Aktivierungen. |
| Kein passender Platz | Der Vorgang erhält einen nachvollziehbaren Wartestatus. Bei bereits eingegangener Zahlung entscheidet das Backoffice über Alternative oder Rückerstattung. |
| Technischer Fehler | Die Freischaltung bleibt als unvollständig sichtbar; Wiederholung und Verwaltungsbenachrichtigung sichern die Nachbearbeitung. |

### Kapazität und Preise

Präsenz- und Onlineplätze werden getrennt geführt. Bei Programmen sind alle benötigten Kursplätze gemeinsam zu prüfen. Reservierungen verhindern, dass derselbe letzte Platz mehrfach vergeben wird. Reservierungsdauer und Zeitpunkt der Platzsicherung werden vor Umsetzung verbindlich festgelegt.

Gesamtprogrammbuchung und Einzelkursbuchung können unterschiedliche Preise haben. Maßgeblich bleibt der beim Buchen bestätigte Preis mit Währung und zugehöriger Preisversion. Ein Wechsel von Präsenz zu Online setzt einen freien Zielplatz voraus; die Umstellung erfolgt zusammenhängend.

### Storno und Wiederherstellung

Storno, Rückerstattung, Zugangssperre und Umbuchung erhalten ausdrücklich festgelegte Regeln. Finanzielle Erstattungen erfolgen nicht allein aufgrund eines technischen Fehlers. Eine Fehlerkorrektur darf nur neu entstandene Zuordnungen zurücknehmen; vorher bestehende Mitgliedschaften und historische Daten bleiben erhalten.

## Unterrichtsplanung und Stundenplan

04 / Persönliche Termine mit Raum, Lehrkraft und Onlinezugang

### Ein Termin als gemeinsame Planungsgrundlage

Jeder Unterrichtstermin enthält Kursdurchführung, Datum, Beginn, Ende, Unterrichtseinheiten, zuständige Lehrkraft, gegebenenfalls Vertretung, Raum bzw. Online-Meeting sowie den Status geplant, durchgeführt oder ausgefallen. Ob Anwesenheit erforderlich ist, wird am Termin hinterlegt.

| Perspektive | Vorgesehene Funktionen |
| --- | --- |
| Teilnehmer | Persönlicher Stundenplan für alle zugeordneten Kurse; Raum, Uhrzeit, Lehrkraft und berechtigter Onlinezugang; erkennbare Änderungen und Ausfälle. |
| Lehrkraft | Eigene Unterrichtstermine; Teilnehmerlisten der zugewiesenen Kurse; Anwesenheitserfassung und Zugang zum jeweiligen Online-Meeting. |
| Administration | Terminplanung, Lehrkraftzuordnung, Raumbelegung, Kapazitätskontrolle, Vertretungen und Terminänderungen. |

### Änderungen ohne Verlust der Historie

Lehrkraftwechsel gelten ab einem festgelegten Zeitpunkt. Bereits durchgeführte Termine behalten die damalige Zuordnung. Terminverlegungen aktualisieren die betroffenen Stundenpläne und lösen eine Mitteilung aus. Ausgefallene Termine werden nicht als fehlende Teilnahme gewertet.

Als ergänzende Prüfung empfiehlt NeXify AI Hinweise auf Überschneidungen bei Lehrkräften, Räumen und Teilnehmern sowie auf unpassende Raumkapazitäten. Kalenderanzeige und Benachrichtigung verwenden einheitliche Zeitzonen.

### Einbindung von OpenOlat

OpenOlat dokumentiert im Course Planner Produkte, Durchführungen und Unterrichtstermine. Termine können unter anderem Ort, Lehrkräfte und Online-Meetings enthalten [1]. Diese Konzepte sollen, soweit in der vorhandenen Installation verfügbar, als Grundlage genutzt werden.

> Vor Umsetzung werden die installierte OpenOlat-Version, aktivierte Module, verfügbare Schnittstellen und die tatsächliche Meeting-Konfiguration geprüft. Die Produktdokumentation ersetzt diese Bestandsprüfung nicht.

NeXify AI empfiehlt eine klar definierte führende Datenquelle pro Bereich. Buchung und Zahlungsstatus, Kursmitgliedschaften, Stundenplan sowie Zertifikate dürfen nicht durch widersprüchliche Parallelpflege auseinanderlaufen.

## Anwesenheit und Rückmeldungen

05 / Prüffähige Erfassung mit transparenter Auswertung

| Status | Erfassung |
| --- | --- |
| Anwesend in Präsenz | Physische Unterrichtsteilnahme durch die Lehrkraft bestätigt. |
| Anwesend online | Online-Unterrichtsteilnahme durch die Lehrkraft bestätigt. |
| Entschuldigt abwesend | Fehlzeit mit entsprechendem Freigabestatus. |
| Unentschuldigt abwesend | Fehlzeit ohne bestätigte Entschuldigung. |
| Noch ungeprüft / nicht erforderlich | Offene Erfassung oder Termin ohne Anwesenheitspflicht; wird gesondert ausgewiesen. |

### Online-Teilnahme als Erfassungshilfe

Soweit die eingesetzte Meeting-Plattform dies unterstützt, werden Beitritte, Austritte und die zugeordnete Teilnahmedauer der Lehrkraft angezeigt. Mehrere Sitzungen derselben Person werden zusammengeführt; überlappende Verbindungen zählen nicht doppelt. Nicht sicher zuordenbare Teilnahmen werden zur Prüfung vorgelegt.

Ein Meeting-Beitritt allein bestätigt keine fachliche Anwesenheit. Die Lehrkraft prüft und bestätigt den Status. Bei fehlenden oder verspäteten Meeting-Daten bleibt eine manuelle Erfassung möglich. Mindestdauer und Regeln bei verspäteter Teilnahme werden vor Umsetzung festgelegt.

### Statistik pro Kurs und frei wählbarem Zeitraum

Die Auswertung verwendet tatsächlich durchgeführte, anwesenheitsrelevante UE während der gültigen Teilnehmerzuordnung. Ausgefallene Termine und Zeiträume vor einem gültigen Eintritt werden ausgeschlossen. Bei null relevanten UE wird keine Prozentquote ausgewiesen.

> Anwesenheitsquote = bestätigte anwesende UE ÷ relevante durchgeführte UE × 100. Präsenz, Online, entschuldigte und unentschuldigte Fehlzeiten verwenden denselben Nenner. Offene Erfassungen werden zusätzlich sichtbar gemacht.

Beispiel bei vollständig geprüften Daten: 40 % online + 30 % Präsenz + 20 % unentschuldigt + 10 % entschuldigt = 100 %. Die gesamte Anwesenheit beträgt 70 %. Teilanwesenheit und UE-Dauer benötigen eine einheitlich definierte Regel.

### Teilnehmermeldung und Korrektur

Teilnehmer sehen ausschließlich ihre eigenen Anwesenheiten und können eine Abweichung melden. Lehrkraft oder Administration prüft die Meldung, dokumentiert die Entscheidung und erstellt bei Bedarf eine nachvollziehbare Korrektur. Die ursprüngliche Erfassung bleibt im Änderungsverlauf erhalten; Statistik und Abschlussprüfung werden neu berechnet.

## Abschluss und Zertifikate

06 / Verlässliche Kurs- und Programmnachweise

### Prüfung vor Ausstellung

Nach Kurs- oder Programmabschluss prüft das System die hinterlegten Bedingungen: erforderliche Kurse, Leistungen bzw. Noten und gegebenenfalls Mindestanwesenheit. Nicht erfüllte oder noch ungeprüfte Voraussetzungen führen zu einem verständlichen Prüfstatus mit Begründung.

NeXify AI empfiehlt für die Einführung eine Freigabe durch die zuständige Zertifikatsrolle. Eine spätere automatische Ausstellung kann für eindeutig definierte Kriterien aktiviert werden. Die Abschlusslogik muss sämtliche Pflichtkurse tatsächlich prüfen; eine bloße technische Programmzuordnung genügt nicht.

| Inhaltsbereich | Vorgesehene Zertifikatsdaten |
| --- | --- |
| Teilnehmer | TN-Kennung, Vorname und Nachname; Geburtsdatum, Geburtsort und Geburtsland entsprechend der freigegebenen Vorlage und dem erforderlichen Zweck. |
| Kurs oder Programm | Bezeichnung, Zeitraum, Zertifikatsbezeichnung, ausgewiesene Unterrichtseinheiten und Inhalte. |
| Leistung | Kursbezogene Noten bzw. Ergebnisse nach vereinbarter Skala; optional Gesamtanwesenheit. |
| Ausstellung | Aussteller, Ausstellungsdatum, eindeutige Zertifikatsnummer und Version der verwendeten Vorlage. |

### Vorlagen und Bereitstellung

Für Studienkolleg, Pflegeschule und Way2Germany können getrennte, jeweils freigegebene Zertifikatsvorlagen verwendet werden. Der Aussteller und das zugehörige Erscheinungsbild werden je Vorlage verbindlich zugeordnet. Teilnehmer erhalten ausschließlich ihre eigenen Zertifikate als PDF im Dashboard.

Bei Ausstellung wird der damalige Datenstand festgehalten. Spätere Änderungen an Kursnamen, Personendaten oder Vorlagen verändern bestehende PDF-Dokumente nicht stillschweigend. Eine berechtigte Neuausstellung erzeugt eine neue Version; Widerruf und Ersetzung werden nachvollziehbar dokumentiert. Wiederholte technische Auslöser erzeugen kein Doppelzertifikat.

### OpenOlat als mögliche Zertifikatsgrundlage

Die offizielle Dokumentation unterscheidet Zertifikate einzelner Kurse von Zertifikatsprogrammen für Durchführungen bzw. mehrere Kurse [2]. Die konkrete Kombination mit Noten, UE, Anwesenheitsbedingungen und kundenspezifischen Vorlagen wird in der vorhandenen Installation gesondert geprüft.

## Notfallliste, Rechte und Betrieb

07 / Gebäudeanwesenheit separat und nachvollziehbar führen

> Eine Unterrichtsanwesenheit oder ein geplanter Termin belegt nicht, dass sich eine Person jetzt im Gebäude befindet. Die Notfallliste benötigt deshalb eine eigene Erfassung von Ein- und Austritten.

### Vorgeschlagener Gebäudeworkflow

Teilnehmer und Lehrkräfte werden beim Betreten des betreffenden Gebäudes eingecheckt und beim Verlassen ausgecheckt. Als Verfahren kommen eine vorhandene Zutrittskontrolle, QR-Check-in und Check-out, der Empfang oder berechtigte manuelle Erfassung infrage. Die Auswahl erfolgt passend zum tatsächlichen Betrieb.

Die exportierbare Liste zeigt die zuletzt als anwesend registrierten Personen, Gebäude und gegebenenfalls Bereich, Aktualisierungszeit sowie erkennbare ungeklärte Einträge. Vergessene Check-outs benötigen ein betriebliches Prüfverfahren. Die Aussagekraft hängt von der vollständigen Erfassung ab; sie ersetzt keine Evakuierungs- oder Vollzähligkeitsprüfung.

| Rolle | Vorgeschlagener Zugriff |
| --- | --- |
| Teilnehmer | Eigene Buchungen, Kurse, Stundenpläne, Anwesenheiten und Zertifikate. |
| Lehrkraft | Zugewiesene Kurse und Termine sowie die dafür erforderlichen Teilnehmer- und Anwesenheitsdaten. |
| Administration / Backoffice | Aufgabenbezogene Pflege, Zahlungsprüfung, Freigaben und Korrekturen gemäß Rollenberechtigung. |
| Zertifikatsrolle | Abschlussprüfung, Ausstellung, Neuausstellung und nachvollziehbarer Widerruf. |
| Empfang / Sicherheitsrolle | Erforderliche Gebäudeanwesenheitsdaten und freigegebener Notfalllistenexport. |

### Daten und Betriebsqualität

Personen-, Geburts-, Noten-, Anwesenheits- und Meeting-Daten werden zweckgebunden und mit begrenzten Zugriffsrechten verarbeitet. Exporte und Änderungen werden protokolliert. Aufbewahrungsfristen, Datenschutzinformationen und Zuständigkeiten werden vor dem produktiven Einsatz festgelegt. Zugangsdaten gehören in eine geschützte Konfiguration.

Technische Ausfälle erhalten einen sichtbaren Bearbeitungsstatus. Aktivierungs-, Termin- und Zertifikatsfehler werden automatisch wiederholt, soweit sicher möglich, und bei dauerhaftem Fehler an die zuständige Verwaltung gemeldet. Vorgeschlagene Zielwerte: Zugang und Stundenplanänderungen innerhalb von fünf Minuten; Anwesenheitserinnerung nach 24 Stunden, Eskalation nach 72 Stunden. Diese Werte sind vor Betrieb zu vereinbaren.

## Umsetzung und Abnahme

08 / Entscheidungen bündeln und den gesamten Ablauf prüfen

### Empfohlene Reihenfolge

1. Vorhandene Systeme, Daten, Schnittstellen und Rollen aufnehmen. 2. Import und Kurs-/Programmverwaltung umsetzen. 3. Buchung, Kapazitäten und Freischaltung verbinden. 4. Stundenplan und Anwesenheitsprüfung integrieren. 5. Zertifikate sowie Gebäudeanwesenheit bereitstellen. 6. Mit einem begrenzten Pilotdurchlauf prüfen und anschließend geordnet in Betrieb nehmen.

Falls Bestandsdaten zu übernehmen sind: Zuordnung planen, Testimport durchführen, Ergebnis abgleichen und erst danach kontrolliert umstellen. Bestehende Funktionen und Daten werden gesichert; ein Rückkehrpfad wird vor der Umstellung festgelegt.

### Vor Umsetzung festzulegen

| Thema | Erforderliche Festlegung |
| --- | --- |
| Systeme und Zuordnung | Zahlungssystem, OpenOlat-Version und Schnittstellen, Meeting-Plattform, bestehende Daten und führende Datenquellen. |
| Buchung und Preise | Reservierungsdauer, Präsenz-/Onlinewechsel, Gesamt-/Einzelpreise, spätere Eintritte, Storno und Erstattung. |
| Anwesenheit und Abschluss | UE-Dauer, Teilanwesenheit, Online-Mindestdauer, Reklamationszuständigkeit, Notenskala und Zertifikatsbedingungen. |
| Betrieb und Datenschutz | Rollen, Gebäude-Check-in, Zertifikatsvorlagen, Aufbewahrungsfristen, Benachrichtigungen und Betriebszielwerte. |

### Vorgesehene Abnahmeprüfungen

Freischaltung vor Kursstart; gleiche Wirkung bei Zahlung und manueller Freigabe; vollständige Programmkurszuordnung; keine Doppelaktivierung; kein überbuchter letzter Platz; fehlerhafter Excel-Import ohne Datenverlust; persönliche Stundenpläne mit Raum und Online-Link; manuelle Anwesenheit bei fehlenden Meeting-Daten; korrekte Zeitraumstatistik; nachvollziehbare Reklamation; einmalige Zertifikatsausstellung; Wiederaufnahme nach Systemausfall; rollenabhängige Zugriffe und geschützter Notfalllistenexport.

### Dokumentgrundlage und Quellen

Grundlage: übermittelte Workflow-Spezifikation vom 01.10.2026. Status: Workflow-Vorschlag, Version 1.0. Die vorhandene Installation wurde für dieses Dokument nicht technisch geprüft. Nächster Schritt ist die fachliche Abstimmung der genannten Betriebsregeln und die Bestandsprüfung.

[1] OpenOlat: Course Planner - Events. [2] OpenOlat: Certification programs. Offizielle Dokumentation, abgerufen am 01.10.2026. Verweise in der digitalen PDF-Version sind anklickbar.

## Begriffe und Kurzüberblick

Der Workflow verbindet die administrative Vorbereitung mit dem täglichen Unterricht und dem Abschlussnachweis. „Durchführung“ bedeutet immer den konkreten Kurs oder das konkrete Programm eines bestimmten Jahrgangs. Eine Vorlage dagegen enthält wiederverwendbare Angaben. Unterrichtsanwesenheit und Gebäudeanwesenheit werden getrennt geführt.

### Begriffserklärung DE ↔ NL


| Deutsch | Niederländisch | Bedeutung |
| --- | --- | --- |
| Teilnehmer (TN) | Deelnemer | Person mit Kurs- oder Programmbuchung |
| Lehrkraft (LK) | Docent | Verantwortliche Person für den Unterricht |
| Unterrichtseinheit (UE) | Onderwijseenheid | Einheit mit vorab festgelegter Dauer |
| Durchführung | Uitvoering | Konkreter Kurs- oder Programmdurchlauf |
| Anwesenheit | Aanwezigheid | Bestätigte Teilnahme am Unterricht |
| Zertifikat | Certificaat | Ausgestellter Abschluss- oder Teilnahmenachweis |

[1] https://docs.openolat.org/en/manual_user/area_modules/Course_Planner_Events/
[2] https://docs.openolat.org/en/manual_user/area_modules/Course_Planner_Certification_Programs/

### Nederlandse toelichting

Het voorgestelde proces verbindt de inschrijving, betaling of handmatige vrijgave, cursusplanning, aanwezigheid en certificering. De deelnemer krijgt na vrijgave al vóór de start toegang tot de geboekte uitvoering. Online deelnamegegevens ondersteunen de beoordeling door de docent. Aanwezigheid in het gebouw wordt apart geregistreerd. De bestaande systemen en de concrete bedrijfsregels moeten vóór implementatie worden gecontroleerd en vastgesteld.
