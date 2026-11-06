# Technisches Gutachten

## Digitale Bewerbungs- und Screening-Plattform Studienkolleg Aachen — Eignung für den Live-Betrieb, Nachvollziehbarkeit der KI-gestützten Vorprüfung und regulatorische Einordnung

**Dokumentnummer:** NEXIFYAI-GU-2026-09-54564
**Fassung:** 1.1 — Entwurf mit Nachtrag 1, fachliche Freigabe ausstehend
**Erstellt:** 08.09.2026, 00:26 Uhr Europe/Berlin
**Verfasser:** NeXify AI
**Gutachtenart:** Privatgutachten (Kurzgutachten mit Beweissicherungsanteil)
**Fachgebiet:** IT / Cyber / KI
**Stichtag der Beurteilung:** 08.09.2026

---

## 1. Dokumentkontrolle

| Feld | Inhalt |
| --- | --- |
| Dokumentnummer | NEXIFYAI-GU-2026-09-54564 |
| Fassung | 1.1 (Entwurf, mit Nachtrag 1 vom 08.09.2026) |
| Datum | 08.09.2026 |
| Verfasser | NeXify AI |
| Prüfer | ausstehend |
| Änderungsgrund | Erstfassung; Nachtrag 1 verifiziert einen zuvor offenen Punkt (F-19) |
| Untersuchungszeitraum | 07.09.2026 19:00 UTC bis 08.09.2026 00:26 CEST |
| Erhebungsart | ausschließlich lesende Fernerhebung am Live-System |
| Ortstermin | **nicht durchgeführt** |

---

## 2. Auftrag, Gutachtenart und Adressat

**Auftraggeber und Adressat:** Pascal Courbois, Inhaber, NeXify AI.

**Auftragswortlaut:** „Erstelle das Gutachten mit dem SKILL für das Studienkolleg Aachen Projekt." — „Für das gesamte Studienkolleg Aachen Projekt."

**Gutachtenart:** Privatgutachten. Es liegt kein gerichtlicher Beweisbeschluss vor, keine Beauftragung durch eine Behörde und keine Schiedsgutachterabrede. Das Gutachten ist **nicht gerichtsfest** und nicht als solches gedacht.

**Verwendungszweck:** interne Grundlage für Priorisierung, Risikosteuerung und Nachweisführung im laufenden Kundenprojekt.

**Untersuchungsgegenstand:** die im Live-Betrieb befindliche digitale Bewerbungs- und Verwaltungsplattform des Studienkollegs Aachen (Betreiber: W2G Academy GmbH), betrieben auf dem dedizierten Server srv1900840, einschließlich der KI-gestützten Vorprüfung von Bewerbungen und der nachgelagerten Wissensverdichtung aus dem Mailbestand.

**Auftragsumfang, wie ich ihn verstanden habe:** „das gesamte Projekt" wird ausgelegt als technischer Ist-Zustand der produktiven Plattform, ihrer KI-Komponenten und ihres Betriebs. Nicht Gegenstand sind: Vertragsverhältnis und Vergütung zwischen NeXify AI und der W2G Academy GmbH, betriebswirtschaftliche Bewertung, Marketing, sowie die Frage der Wirksamkeit einzelner Vertragsklauseln. Diese Abgrenzung wurde von mir gesetzt, nicht vorgegeben.

**Honorar-/Kostenrahmen:** nicht vereinbart, nicht Gegenstand.

**Frist:** keine gesetzt. Erstellung in der Nacht vom 07. auf den 08.09.2026.

---

## 3. Unabhängigkeit, Kompetenz und Interessenkonflikt

### 3.1 Offenlegung eines Interessenkonflikts

**Es besteht ein Interessenkonflikt, und er ist erheblich.**

Der Verfasser dieses Gutachtens hat am 06. und 07.09.2026 selbst an dem begutachteten System gearbeitet: unter anderem an der Wissensbasis, an Prüfwerkzeugen, an der Aktenansicht und an der Analyse der Verdichtungskette. Mehrere der unten festgestellten Abweichungen betreffen Code und Konfiguration, an denen der Verfasser beteiligt war oder die er hätte bemerken müssen.

Konkret richten sich die Befunde **F-03**, **F-09** und Teile von **F-01** gegen die eigene Arbeit des Verfassers. Befund F-09 korrigiert zusätzlich eine am 07.09.2026 abends von ihm selbst aufgestellte, falsch begründete Behauptung.

Ein Privatgutachten, dessen Verfasser zugleich am Gegenstand mitgewirkt hat, ist kein unabhängiges Gutachten. Es kann Befunde belegen, aber es kann seine eigene Vollständigkeit nicht bezeugen — der Verfasser kann nicht wissen, welche Fehler er systematisch übersieht, weil er sie selbst eingebaut hat. **Für eine belastbare Aussage über das Gesamtsystem ist eine zweite, unbeteiligte Prüfinstanz erforderlich.** Dieser Punkt ist als Maßnahme M-14 aufgenommen.

### 3.2 Kompetenzgrenzen

Der Verfasser ist ein KI-System. Er ist **nicht** öffentlich bestellt, nicht vereidigt, nicht akkreditiert und nicht zertifiziert. Es wird ausdrücklich keine Sachverständigenqualifikation behauptet.

Die im Abschnitt 6 dargestellten rechtlichen Einordnungen sind **keine Rechtsberatung**. Sie geben den Wortlaut abgerufener Primärquellen wieder und ordnen den technischen Sachverhalt darunter ein. Die abschließende rechtliche Bewertung — insbesondere zur Anbieterrolle nach der KI-Verordnung, zur Reichweite von Art. 22 DSGVO und zur Ausgestaltung der Auftragsverarbeitung — ist einer Rechtsanwältin oder einem Rechtsanwalt mit Schwerpunkt IT- und Datenschutzrecht vorbehalten.

### 3.3 Zugang und Vertraulichkeit

Der Zugang zum Server erfolgte über einen bestehenden, vom Auftraggeber eingerichteten SSH-Zugang. Sämtliche Erhebungen waren **lesend**. Es wurde keine Datei geändert, kein Dienst neu gestartet, keine Datenbank beschrieben. Grund: Zum Erhebungszeitpunkt galt die Betriebszeiten-Sperre (Schreibaktionen am Kundensystem nur Mo–Fr 08:00–18:00 Europe/Berlin), und es lag keine Notfallmeldung vor, die eine Ausnahme getragen hätte.

Personenbezogene Daten von Bewerbern wurden **nicht** eingesehen. Alle Datenbankabfragen erhoben Anzahlen, Feldnamen und Werteverteilungen. Wo einzelne Datensätze angezeigt wurden (anabin-Beispiel), enthielten sie keinen Personenbezug. Bewerbungs-IDs erscheinen im Gutachten als technische Kennungen ohne Namensbezug.

---

## 4. Beweisfragen

| Nr. | Beweisfrage |
| --- | --- |
| **B1** | Welche Abweichungen vom technischen Sollzustand bestehen am Stichtag im Live-Betrieb der Plattform, insbesondere in der KI-gestützten Vorprüfung? |
| **B2** | Wie ist die KI-gestützte Vorprüfung nach der zum Stichtag geltenden KI-Verordnung einzuordnen, und welche Pflichten treffen den Betreiber wann? |
| **B3** | Lässt sich die im Rechtstext der Plattform aufgestellte Aussage, es finde keine automatisierte Entscheidungsfindung im Sinne von Art. 22 DSGVO statt, mit den vorhandenen Daten belegen? |
| **B4** | Ist der Betrieb so protokolliert und überwacht, dass fachliche Fehler erkannt werden, bevor sie wirken? |
| **B5** | Ist das eingesetzte Fachwissen (Wissensbasis, Länderklassifikation) inhaltlich tragfähig, und erreicht es die prüfende KI? |
| **B6** | Welche Maßnahmen sind mit welcher Dringlichkeit erforderlich? |

Die Beweisfragen wurden vom Verfasser aus dem allgemein gehaltenen Auftrag abgeleitet und neutral formuliert. Rechtsfragen sind als solche gekennzeichnet und werden nicht als technische Tatsachenfeststellung beantwortet.

---

## 5. Untersuchungsgegenstand, Stichtag und Grenzen

### 5.1 Gegenstand

| Komponente | Ausprägung am Stichtag |
| --- | --- |
| Server | srv1900840, dediziert für dieses Kundenprojekt |
| Dienste | `backend`, `frontend`, `mongo`, `minio` (Docker Compose) |
| Datenbank | MongoDB, Datenbank `w2g`, 36 Sammlungen |
| KI-Vorprüfung | `backend/services/ai_screening.py` — Delta-Screening je Bewerbung |
| Wissensaufbau | `scripts/knowledge_ingest_mail.py`, `scripts/knowledge_distill.py`, gesteuert durch `w2g-knowledge.timer` |
| Modellzugang | `openrouter_provider` (primär), `nscale_provider` (Rückfall) |
| Öffentliche Rechtstexte | `frontend/src/pages/public/LegalPage.js` |

### 5.2 Maßgeblicher Zeitpunkt

**Stichtag ist der 08.09.2026** — der heutige Zustand. Das ist bewusst gewählt: Die Plattform ist seit dem 07.09.2026 im ersten produktiven Kundenbetrieb. Für die regulatorische Einordnung ist der heutige Rechtsstand maßgeblich; wo Pflichten erst künftig greifen, ist das Datum ausdrücklich genannt.

### 5.3 Grenzen dieser Untersuchung

Diese Grenzen sind Teil des Ergebnisses und nicht stillschweigend zu übergehen:

1. **Kein Ortstermin.** Es wurde ausschließlich fernerhoben. Physische Infrastruktur, Zugangssicherung des Rechenzentrums und organisatorische Abläufe beim Kunden wurden nicht geprüft.
2. **Keine Befragung.** Es wurde niemand beim Kunden befragt. Aussagen über das tatsächliche Verhalten der Sachbearbeitung — insbesondere wie intensiv KI-Empfehlungen geprüft werden — konnten nicht erhoben werden. Das ist für Beweisfrage B3 die entscheidende Lücke.
3. **Keine schreibenden Tests.** Es wurde kein Testfall durch das System geschickt, kein Screening ausgelöst, kein Fehlerfall provoziert. Sämtliche Aussagen über Laufzeitverhalten beruhen auf Code, Konfiguration, gespeicherten Ergebnissen und Protokollen.
4. **Kein vollständiger Sicherheits-Audit.** Es wurde kein Penetrationstest, keine Abhängigkeitsanalyse auf Schwachstellen und keine Prüfung der Zugriffsrechte im Detail durchgeführt.
5. **Keine Prüfung der Vertragslage.** Ob mit den eingesetzten Modellanbietern Auftragsverarbeitungsverträge bestehen, konnte technisch nicht festgestellt werden und wurde nicht erfragt.
6. **Geringe Fallzahl.** Der produktive Bestand umfasst am Stichtag 71 Bewerbungen, davon 8 mit vollständigen Fachdaten, und 32 gespeicherte Screenings. Statistische Aussagen sind auf dieser Grundlage nicht möglich; alle Quoten sind als Anhaltspunkt und nicht als Kennzahl zu lesen.

---

## 6. Methodik und Beweismittel

### 6.1 Vorgehen

Der Untersuchungsplan wurde vor der Auswertung festgelegt: zuerst Beweisfragen, dann Erhebungsplan je Frage, dann Erhebung, dann Auswertung. Zu jeder Hauptschlussfolgerung wurde die Gegenhypothese gebildet und geprüft (Abschnitt 9).

Zwei Grundsätze wurden durchgehend angewandt:

- **Laufzeitwert vor Quelltextname.** Es wird gemessen, was das System tut, nicht was seine Bezeichner behaupten. Befund F-09 zeigt, warum das nötig ist.
- **Primärquelle vor Erinnerung.** Jede normative Aussage wurde am Stichtag aus der amtlichen Quelle abgerufen. Befund F-11 zeigt, warum das nötig ist: Der Rechtsstand hat sich seit Erlass der KI-Verordnung wesentlich geändert.

### 6.2 Beweismittelverzeichnis

| ID | Art | Bezeichnung | Erhebung |
| --- | --- | --- | --- |
| L-01 | Log | `docker compose ps` — Dienststatus | 07.09.2026 22:21 UTC |
| D-01 | Dokument | `backend/services/ai_screening.py`, Z. 355–375 | 07.09.2026 22:21 UTC |
| D-02 | Dokument | `backend/services/ai_learning.py`, Z. 15–45 | 07.09.2026 22:21 UTC |
| D-03 | Dokument | `backend/services/ai_screening.py`, Z. 530–615 | 07.09.2026 22:21 UTC |
| D-04 | Dokument | `frontend/src/pages/public/LegalPage.js`, Abschnitte 4 und 12 | 07.09.2026 22:24 UTC |
| D-05 | Dokument | `scripts/knowledge_distill.py` | 07.09.2026 21:2x UTC |
| D-06 | Dokument | `scripts/w2g-knowledge-sync.sh` | 07.09.2026 21:2x UTC |
| D-07 | Dokument | `deploy/.env` — Laufzeitwerte (ohne Geheimnisse) | 07.09.2026 21:26 UTC |
| M-01 | Messung | Bestandsaufnahme aller 36 Sammlungen | 07.09.2026 22:22 UTC |
| M-02 | Messung | Feldnamen und Werteverteilungen `applications`, `ai_screenings` | 07.09.2026 22:23 UTC |
| M-03 | Messung | Detailbeweise: Zuordenbarkeit, Wertebereiche, Pflegefelder, Protokollierung | 07.09.2026 22:24 UTC |
| M-04 | Messung | Modellvergleich nscale, 5 Läufe je Modell, synthetische Daten | 07.09.2026 21:36–21:47 UTC |
| M-05 | Messung | Abruf `GET /v1/models` bei nscale, HTTP 200, 23 Modelle | 07.09.2026 21:30 UTC |
| N-01 ff. | Norm/Regel | Normenregister, Abschnitt 7 | 08.09.2026 |
| A-01 | Fremdangabe | Prämortem vom 07.09.2026 (eigene frühere Arbeit des Verfassers) | — |

Die Mess-Skripte `messung_gutachten.js`, `messung2.js`, `messung3.js` und `vergleich_modelle.py` liegen unverändert auf dem Server unter `/root/patches-morgen-08-09/` und sind wiederholbar. Sie enthalten ausschließlich lesende Operationen.

**Beweismittel-Integrität:** Die Originaldateien auf dem Server wurden nicht verändert. Es wurden keine Kopien mit eigener Ableitungs-ID erzeugt, weil keine Bearbeitung stattfand. Hashes wurden nicht gebildet — das ist eine Lücke gegenüber einer beweissichernden Erhebung und wäre bei einer streitigen Verwendung nachzuholen.

---

## 7. Regelwerke und Normenregister

Alle Einträge wurden am 07./08.09.2026 aus der jeweiligen Primärquelle abgerufen. Kein Eintrag stammt aus Erinnerung oder Sekundärliteratur.

### 7.1 Tragende Rechtsakte

Alle fünf Rechtsakte sind am Stichtag **anwendbar**; die Spalte „Status" nennt jeweils den heutigen Stand.

| ID | Bezeichnung, Ausgabe | Status | Bindungsgrund | Quelle |
| --- | --- | --- | --- | --- |
| N-01 | VO (EU) 2024/1689 (KI-VO), **konsolidierte Fassung Stand 27.07.2026**, CELEX 02024R1689-20260727 | verifiziert | unmittelbar geltendes EU-Recht | EUR-Lex, Volltext |
| N-02 | **VO (EU) 2026/1744** vom 08.07.2026 (Digital-Omnibus-Verordnung zur KI), ABl. 24.07.2026, in Kraft 27.07.2026 | verifiziert | ändert N-01 | EUR-Lex, Volltext |
| N-03 | VO (EU) 2016/679 (DSGVO), CELEX 32016R0679 | verifiziert | unmittelbar geltendes EU-Recht | EUR-Lex, Volltext |
| N-04 | Durchführungsbeschluss (EU) 2023/1795 (EU-US Data Privacy Framework) | verifiziert — in Kraft, keine ändernden oder aufhebenden Rechtsakte verzeichnet | Angemessenheitsbeschluss nach Art. 45 DSGVO | EUR-Lex, Rechtsaktsuche |
| N-05 | Durchführungsbeschluss (EU) 2021/914 (Standardvertragsklauseln) | verifiziert — in Kraft; einschlägig, falls Empfänger nicht DPF-zertifiziert | Art. 46 Abs. 2 lit. c DSGVO | EUR-Lex |

### 7.2 Rechtsprechung

| ID | Entscheidung | Status | Tragende Aussage für diesen Fall |
| --- | --- | --- | --- |
| N-06 | EuGH, 07.12.2023, **C-634/21** (SCHUFA), ECLI:EU:C:2023:957 | `CURRENT_VERIFIED` | Eine automatisiert erzeugte Bewertung ist bereits selbst eine „Entscheidung" i. S. v. Art. 22 Abs. 1 DSGVO, wenn das Handeln des Dritten von ihr „maßgeblich geleitet" wird (Rn. 48, 50). |
| N-07 | EuGH, 27.02.2025, **C-203/22** (Dun & Bradstreet Austria), ECLI:EU:C:2025:117 | `CURRENT_VERIFIED` | Betroffene können die konkret angewandten Verfahren und Grundsätze erläutert verlangen; ein pauschaler Verweis auf Geschäftsgeheimnisse sperrt den Anspruch nicht. |
| N-08 | EuG, 03.09.2025, **T-553/23** (Latombe/Kommission), ECLI:EU:T:2025:831 | `CURRENT_VERIFIED` | Klage gegen den DPF-Angemessenheitsbeschluss abgewiesen. Rn. 683: Ein Auftragsverarbeiter im Drittland, der für einen Verantwortlichen in der Union handelt, unterliegt nach Art. 3 Abs. 1 selbst der DSGVO. |
| N-09 | EuGH, **C-703/25 P** (Rechtsmittel Latombe), eingelegt 31.10.2025 | anhängig, **kein Urteil am Stichtag**; Rechtsmittel haben nach Art. 60 Abs. 1 der Satzung **keine aufschiebende Wirkung** | Restrisiko einer künftigen Aufhebung des DPF |
| N-10 | EuGH, **C-568/25** (Universal Versand), Vorlage des OGH vom 27.08.2025 | anhängig, kein Urteil am Stichtag | betrifft u. a., ob es darauf ankommt, dass die Entscheidung mit vertretbarem Aufwand auch durch Menschen erfolgen könnte |

### 7.3 Behördliche Leitlinien und Orientierungshilfen

| ID | Dokument | Status | Relevanz |
| --- | --- | --- | --- |
| N-11 | Art.-29-Gruppe, **WP251rev.01**, zuletzt angenommen 06.02.2018, vom EDSA am 25.05.2018 bestätigt | `HISTORICAL_APPLICABLE` — weiterhin die maßgebliche Leitlinie zu Art. 22; keine EDSA-Leitlinie 2025/2026 ersetzt sie | Maßstab für „echte" menschliche Beteiligung |
| N-12 | DSK, **Orientierungshilfe „Künstliche Intelligenz und Datenschutz", Version 1.0 vom 06.05.2024** | `CURRENT_VERIFIED` — DSK-Übersichtsseite weist keine neuere Fassung aus | Ziffer 1.6: tatsächlicher Entscheidungsspielraum, keine bloß formelle Beteiligung |
| N-13 | DSK, **Muss-Liste nach Art. 35 Abs. 4 DSGVO, nicht-öffentlicher Bereich, Version 1.1 vom 17.10.2018** | `CURRENT_VERIFIED` — von LDI NRW am Stichtag weiterhin als geltend geführt | Eintrag Nr. 11: KI-Einsatz zur Bewertung persönlicher Aspekte → DSFA-Pflicht |
| N-14 | DSK, **OH zu TOM bei KI-Systemen, Version 1.0, Juni 2025** | `CURRENT_VERIFIED` | Ziffer 2.2.4: Interventionsmöglichkeiten technisch vorsehen |
| N-15 | EDSA, **Stellungnahme 28/2024**, angenommen 02.12.2024 | `CURRENT_VERIFIED` | Sorgfaltspflicht des Einsetzenden bei fremdentwickelten Modellen |
| N-16 | DSK, **OH zu generativer KI mit RAG-Methode, Version 1.0, Oktober 2025** | `CURRENT_VERIFIED` als existierend; **inhaltlich NICHT AUSGEWERTET** | einschlägig für die Verdichtungskette — Auswertung steht aus |

### 7.4 Ausdrücklich nicht herangezogen

- **DIN EN 16775, ISO/IEC 17020, ISO/IEC 17025, ISO 19011, ISO 31000, ISO 9001** wurden **nicht** als Prüfmaßstab verwendet. Grund: Es liegt kein lizenzierter Volltext vor. Nach dem Grundsatz, keine Klausel zu zitieren, deren Wortlaut nicht vorliegt, werden sie hier weder zitiert noch als Maßstab behauptet. Status daher `BLOCKED_BY_ACCESS`.
- Die Risikodarstellung in Abschnitt 10 folgt daher **keiner** benannten Norm, sondern einer im Dokument selbst offengelegten, einfachen Einstufung.
- **Entwurf der Kommissionsleitlinien zur Einstufung von Hochrisiko-KI-Systemen** (veröffentlicht 19.05.2026, Seitenstand 23.07.2026): Status **Entwurf**, rechtlich unverbindlich. Nicht als Maßstab verwendet. Ob inzwischen eine Endfassung vorliegt: `NICHT VERIFIZIERT`.

---

## 8. Befunde

Jeder Befund nennt Beweismittel, Sollzustand, Abweichung, Ursache, Auswirkung, Aussageklasse und Konfidenz. Aussageklassen: `TATSACHE`, `FREMDANGABE`, `BERECHNUNG`, `FACHLICHE_BEWERTUNG`, `HYPOTHESE`, `RECHTSFRAGE`.

### 8.1 Befunde zu B1 — Abweichungen vom technischen Sollzustand

---

#### F-01 — Zwei stille Fehlerschlucker, der einzige Protokollierungspfad ist unerreichbar

**Beweismittel:** D-01.

**Ist-Zustand.** In `ai_screening.py` stehen zwei aufeinanderfolgende `try`-Blöcke. Der erste lädt das institutionelle Wissen, der zweite das externe Wissen. Beide enden auf `except Exception: pass`. Danach folgt ein dritter Handler `except Exception as e:` mit einem `logger.warning`. Dieser dritte Handler ist syntaktisch an den zweiten `try` gebunden, der bereits durch den vorangehenden Handler abgedeckt ist — er wird **nie erreicht**.

**Sollzustand.** Ein Fehler beim Laden der Wissensbasis muss sichtbar werden, weil er das Ergebnis der Vorprüfung inhaltlich verändert: Die KI prüft dann ohne das Wissen, mit dem sie prüfen soll.

**Abweichung.** Zwei Fehlerpfade schlucken lautlos. Der einzige vorhandene Protokollierungspfad ist toter Code. Das Screening läuft weiter und liefert ein Ergebnis, das äußerlich nicht von einem vollständigen Ergebnis zu unterscheiden ist.

**Ursache.** Redaktioneller Fehler beim Einfügen des zweiten `try`-Blocks. `py_compile` warnt hier nicht — der Code ist gültig. Kausalitätsgrad: **hoch gestützt**, der Quelltext liegt vor und ist eindeutig.

**Auswirkung.** Dies ist die technische Entsprechung des im Prämortem (A-01) als wahrscheinlichstes Scheitern benannten Musters: ein Fehler, der monatelang plausibel aussieht. Betroffen sind Funktion und Nachvollziehbarkeit, nicht Sicherheit.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

#### F-02 — Die 648 aus den Mails gewonnenen Betriebsregeln erreichen die prüfende KI nicht

**Beweismittel:** D-02, M-01.

**Ist-Zustand.** `gather_institutional_knowledge()` wird vor jedem Screening aufgerufen und sammelt: Portal-Nachrichten (`messages`, 309 Dokumente), Prüfprotokolle und Entscheidungshistorie. Die aus dem Mailbestand verdichteten Betriebsregeln liegen in `brain_memories` mit `entity_type: "institution"` — **648 Dokumente** — und werden von dieser Funktion **nicht gelesen**.

**Sollzustand.** Das aus 25.061 Mails gewonnene Betriebswissen soll in die Vorprüfung einfließen. Das ist der erklärte Zweck der gesamten Verdichtungskette.

**Abweichung.** Die Verdichtungskette produziert Regeln, die im Prüfpfad nicht ankommen. Der aufwendigste Teil der Wissensarbeit wirkt sich auf die Vorprüfung nicht aus.

**Ursache.** Die Wissensbasis wurde nach dem Screening-Pfad gebaut; die Anbindung wurde nicht nachgezogen. Kausalitätsgrad: **hoch gestützt** — beide Seiten sind im Quelltext belegt.

**Auswirkung.** Der wirtschaftliche Aufwand der Verdichtung (Modellkosten, Laufzeit, Entwicklung) erzeugt derzeit keinen Nutzen im Prüfpfad. Zusammen mit F-01 gilt: Selbst wenn die Anbindung bestünde, würde ihr Ausfall nicht auffallen.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

#### F-03 — Die gespeicherte Herkunft der KI-Empfehlung ist unzutreffend

**Beweismittel:** D-03, M-02.

**Ist-Zustand.** In `screening_result` ist `"ai_provider": "deepseek"` als Festwert eingetragen. Gemessen über alle 32 gespeicherten Screenings: `ai_provider` lautet in **32 von 32** Fällen „deepseek". Das Feld `ai_model` zeigt demgegenüber: `deepseek/deepseek-v4-flash-0731` (20), `(null)` (10), `deepseek-v4-flash` (1), **`gpt-4o-mini` (1)**.

**Sollzustand.** Der Prüfdatensatz muss festhalten, welches Modell welchen Anbieters die Empfehlung erzeugt hat. Das ist die Grundlage jeder späteren Nachprüfung.

**Abweichung.** In mindestens einem Fall wurde ein Modell eines anderen Anbieters verwendet, der Datensatz weist dennoch „deepseek" aus. In zehn Fällen ist gar kein Modell vermerkt, der Anbieter aber schon. Der Aufruf erfolgt zudem über einen Aggregator, dessen Umgebungsvariable `NEXIFY_ROUTER_*` heißt (vgl. F-09) — die tatsächliche Verarbeitungskette ist aus dem Datensatz nicht rekonstruierbar.

**Ursache.** Festwert statt Auslesen des tatsächlich verwendeten Anbieters. Kausalitätsgrad: **hoch gestützt**.

**Auswirkung.** Nachvollziehbarkeit und Beweiskraft. Wird künftig zu belegen sein, welches System eine bestimmte Empfehlung erzeugt hat — etwa auf Auskunftsverlangen nach N-07 —, ist der eigene Datenbestand keine taugliche Grundlage. Dieser Befund richtet sich gegen die Arbeit des Verfassers.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

#### F-04 — Knapp ein Drittel der Screenings lief mit fehlgeschlagenem KI-Aufruf

**Beweismittel:** M-02.

**Ist-Zustand.** Von 32 gespeicherten Screenings tragen **10 einen Wert im Feld `ai_error`**:

| Fehlerart | Anzahl |
| --- | --- |
| `Error code: 402 – Insufficient Balance` | 4 |
| `Error code: 401 – Authentication Fail…` | 2 |
| `HTTP 402` | 2 |
| `Antwort abgeschnitten (Token-Limit, finish_reason=length)` | 2 |
| kein Fehler (`null`) | 22 |

Das sind **31,3 Prozent** der Screenings. Die betroffenen Datensätze enthalten gleichwohl einen `suggested_stage` — erzeugt durch die lokalen, regelbasierten Prüfungen — und sind als Screening gespeichert.

**Sollzustand.** Ein Screening, dessen KI-Anteil nicht zustande kam, muss als solches erkennbar sein und darf nicht denselben Status tragen wie ein vollständiges.

**Abweichung.** Der Fehler ist zwar im Feld `ai_error` vermerkt — das ist gut und wird ausdrücklich anerkannt —, aber er führt weder zu einem abweichenden Status noch zu einer Kennzeichnung in der Aktenansicht, und der Datensatz weist weiterhin einen Anbieter aus (F-03). Vier der Fehler (`Insufficient Balance`) bedeuten, dass ein Guthabenkonto leer war; zwei (`401`) deuten auf einen ungültigen Schlüssel.

**Ursache.** Erschöpftes Guthaben beziehungsweise Schlüsselwechsel beim Modellzugang, ohne Überwachung dieses Zustands. Kausalitätsgrad: **überwiegend gestützt** — die Fehlertexte sind eindeutig, der genaue Zeitpunkt und die Dauer wurden nicht rekonstruiert.

**Auswirkung.** Fachlich erheblich. Eine Empfehlung ohne KI-Anteil ist eine andere Empfehlung. Für die Sachbearbeitung ist der Unterschied am Bildschirm nicht sichtbar.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

#### F-05 — 27 von 32 Screenings lassen sich keiner Bewerbung zuordnen

**Beweismittel:** M-02, M-03.

**Ist-Zustand.** Die Verknüpfung `ai_screenings.application_id` → `applications` gelingt für **5 von 32** Datensätzen. Für 27 findet sich keine zugehörige Bewerbung, weder über `_id` noch über ein Feld `id` (ein solches Feld existiert in `applications` nicht; die Sammlung führt `_id`, `applicant_id`, `current_stage` und weitere).

**Sollzustand.** Jedes Prüfergebnis muss dauerhaft der Bewerbung zugeordnet bleiben, auf die es sich bezieht.

**Abweichung.** 84 Prozent der gespeicherten Prüfergebnisse sind verwaist.

**Ursache — zwei Hypothesen, beide offen.** (a) Die zugehörigen Bewerbungen wurden gelöscht, etwa im Rahmen von Testläufen vor dem Produktivgang. (b) Das Kennungsschema hat sich geändert, die Altbestände wurden nicht mitgezogen. Beide sind mit einer Stichprobe prüfbar; die Prüfung wurde nicht durchgeführt, weil sie ohne Schreibrechte und ohne Kenntnis der Löschhistorie nicht abschließbar ist. Kausalitätsgrad: **beobachtet**.

**Auswirkung.** Die Prüfhistorie ist als Nachweis nicht verwendbar. Für Beweisfrage B3 ist das der begrenzende Faktor.

**Aussageklasse:** `TATSACHE` für den Messwert, `HYPOTHESE` für beide Ursachen. **Konfidenz der Ursache: niedrig.**

---

#### F-06 — KI-Empfehlung und Bewerbungsstatus verwenden unterschiedliche Begriffssysteme

**Beweismittel:** M-03.

**Ist-Zustand.**

| Seite | Vorkommende Werte |
| --- | --- |
| KI-Vorschlag (`suggested_stage`) | `eligible`, `in_review`, `pending_docs` |
| Tatsächliche Stufe (`current_stage`) | `conditional_offer`, `enrolled`, `in_review`, `interview_scheduled`, `lead_new`, `offer_sent` |
| **Schnittmenge** | **nur `in_review`** |

**Sollzustand.** Empfehlung und Ergebnis müssen vergleichbar sein, sonst lässt sich nicht feststellen, ob der Empfehlung gefolgt wurde.

**Abweichung.** Die beiden Wertebereiche sind bis auf einen einzigen Wert disjunkt. Eine Übernahmequote ist aus dem Datenbestand **nicht ermittelbar** — weder für noch gegen den Betreiber.

**Ursache.** Die KI-Vorprüfung und die Fallführung wurden unabhängig voneinander modelliert. Kausalitätsgrad: **überwiegend gestützt**.

**Auswirkung.** Dies ist der zentrale Befund für Beweisfrage B3 und für die spätere Pflicht zur menschlichen Aufsicht. Ohne Vergleichbarkeit gibt es keinen Nachweis über das Zusammenspiel von Mensch und System.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

#### F-07 — Die Länderklassifikation ist als „geprüft" markiert, aber inhaltlich nicht gepflegt

**Beweismittel:** M-01, M-03.

**Ist-Zustand.** Die Sammlung `anabin_knowledge` enthält **85 Einträge** für 85 Länder. Gemessen:

| Feld | Befund |
| --- | --- |
| `source_url` | in 85/85 vorhanden, in **85/85 leer** (`""`) |
| `operational_classification` | in 85/85 leer |
| `staff_note` | in 85/85 leer |
| `standard_response` | in 85/85 leer |
| `notes` | in 85/85 **gefüllt** |
| `status: "verified"` | **80/85** |
| `last_verified_by: "system"` | **85/85** |
| `usage_count: 0` | 66/85 |
| `source` | `anabin_seed` |

Beispieldatensatz (ohne Personenbezug): Land „Tschad", Kategorie „D", Notiz „Eingeschraenkte Anerkennung – intensive Einzelfallpruefung erforderlich", `last_verified: 2026-03-31`, `last_verified_by: system`, `source_url: ""`.

**Sollzustand.** Eine Wissensbasis, auf die sich Zugangsentscheidungen stützen, muss belegen, woher jede Aussage stammt, und ihr Prüfstatus muss den tatsächlichen Prüfvorgang abbilden.

**Abweichung — und das ist der schwerwiegendste Teil.** 80 Einträge tragen den Status „verified", obwohl als prüfende Instanz durchgehend „system" eingetragen ist und keine einzige Quellenangabe hinterlegt ist. Der Status behauptet eine Prüfung, die nicht stattgefunden hat. Das ist keine bloße Lücke, sondern eine **Scheingenauigkeit**: Die Oberfläche signalisiert Verlässlichkeit, wo Saatdaten stehen.

**Ursache.** Bei der Erstbefüllung („seed") wurde der Status pauschal gesetzt statt neutral („unverified"). Kausalitätsgrad: **überwiegend gestützt** — `source: anabin_seed` und `last_verified_by: system` in allen Datensätzen belegen die maschinelle Herkunft.

**Auswirkung.** Eine Sachbearbeiterin, die einen Eintrag als „verified" sieht, hat keinen Anlass zur Rückfrage. Genau diese nachlassende Widerspruchsbereitschaft ist im Prämortem (A-01) als zweitgrößtes Risiko benannt. Hier ist der technische Auslöser dafür.

**Aussageklasse:** `TATSACHE` für die Messwerte, `FACHLICHE_BEWERTUNG` für die Einordnung als Scheingenauigkeit. **Konfidenz: hoch.**

---

#### F-08 — Die Wissensverdichtung steht bei 3,8 Prozent

**Beweismittel:** M-01, M-03, D-05, D-06.

**Ist-Zustand.** 25.061 Mails im Bestand, **945 verdichtet (3,8 %)**, 24.116 offen. Der nächtliche Lauf verarbeitet nach Konfiguration bis zu 4.000 Mails (200 + 200 Stapel zu je 10). Rechnerisch sind das **7 weitere Nächte** bis zur Vollständigkeit — sofern kein Stapel ausfällt.

**Sollzustand.** Der Bestand soll planbar abgearbeitet werden.

**Abweichung.** Im Lauf vom 07.09.2026 blieben ausweislich des Protokolls mehrere Stapel mit der Meldung „keine Liste erhalten" offen — in der protokollierten Sequenz 5 von 12 sichtbaren Stapeln. Die Ausfallquote ist nicht gemessen, aber sichtbar erheblich. Sie verlängert die Restlaufzeit entsprechend.

**Ursache.** Das Modell liefert in diesen Fällen keine als JSON-Liste erkennbare Antwort. Der Code fängt das ab und markiert die Mails nicht — sie werden später erneut aufgegriffen; das ist sauber gelöst. Kausalitätsgrad: **überwiegend gestützt**.

**Auswirkung.** Zeitverzug, keine Datenverluste. In Verbindung mit F-02 derzeit ohne Wirkung auf die Vorprüfung.

**Aussageklasse:** `TATSACHE` für Bestand und Rechnung; `BERECHNUNG` für die 7 Nächte. **Konfidenz: mittel** — die Rechnung unterstellt eine Ausfallquote von null.

---

#### F-09 — Der Bezeichner der Modellzugangs-Konfiguration widerspricht ihrem Inhalt

**Beweismittel:** D-07, M-05.

**Ist-Zustand.** Die Umgebungsvariable heißt `NEXIFY_ROUTER_BASE_URL`, ihr Docstring im Quelltext lautet „LLM-Client via NeXify-Router (9Router) — Kanon V-01. Fallback: DeepSeek-direkt." Der im laufenden Container gemessene Wert lautet:

```
NEXIFY_ROUTER_BASE_URL = https://openrouter.ai/api/v1
LLM_MODEL              = deepseek/deepseek-v4-flash-0731
```

Es handelt sich also nicht um eigene Infrastruktur, sondern um einen fremden Aggregator.

**Sollzustand.** Bezeichner und Dokumentation müssen den Inhalt zutreffend beschreiben, sonst führen sie jede spätere Prüfung in die Irre.

**Abweichung.** Name und Docstring behaupten eigene Infrastruktur, der Laufzeitwert zeigt auf einen Dritten. Für die datenschutzrechtliche Bewertung ist das ein erheblicher Unterschied.

**Ursache.** Historisch gewachsen: Die Variable stammt aus einer Phase, in der ein eigener Router vorgesehen war; das Ziel wurde geändert, der Name nicht. Kausalitätsgrad: **überwiegend gestützt**.

**Auswirkung.** Dieser Befund ist zugleich eine **Korrektur einer eigenen Fehlaussage des Verfassers**: Am Abend des 07.09.2026 wurde die Aussage „die Verdichtung läuft über OpenRouter" zunächst allein aus dem Funktionsnamen `_get_openrouter_client` abgeleitet — also aus einem Namen, nicht aus dem Verhalten. Die Aussage traf zu, die Begründung war falsch. Erst die Messung des Laufzeitwerts belegte sie.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

#### F-10 — Der produktive Bestand ist deutlich kleiner, als die Gesamtzahl nahelegt

**Beweismittel:** M-02, M-03.

**Ist-Zustand.** 71 Bewerbungen, davon **62 im Status `lead_new`**. Fachdaten sind nur bei 8 Datensätzen vorhanden (`course_type`, `degree_country`, `language_level`, `applicant_number` je 8/71); ein Qualifizierungspfad ist bei 11/71 berechnet.

**Bewertung.** Die tatsächliche fachliche Last am Stichtag beträgt in der Größenordnung **8 bis 11 Vorgänge**, nicht 71. Das entlastet die Betriebslage erheblich und ist bei jeder Aussage über Fehlerquoten zu berücksichtigen: Alle in diesem Gutachten genannten Anteile beruhen auf sehr kleinen Grundgesamtheiten.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

### 8.2 Befunde zu B2 — Einordnung nach der KI-Verordnung

---

#### F-11 — Die Vorprüfung erfüllt den Tatbestand eines Hochrisiko-KI-Systems

**Beweismittel:** N-01, D-03.

Anhang III Nummer 3 Buchstabe a der KI-VO lautet wörtlich:

> „KI-Systeme, die bestimmungsgemäß zur Feststellung des Zugangs oder der Zulassung oder zur Zuweisung natürlicher Personen zu Einrichtungen aller Ebenen der allgemeinen und beruflichen Bildung verwendet werden sollen"

Art. 6 Abs. 2 KI-VO: „Zusätzlich zu den in Absatz 1 genannten Hochrisiko-KI-Systemen gelten die in Anhang III genannten KI-Systeme als hochriskant."

**Subsumtion.** Die Vorprüfung erzeugt je Bewerbung einen Vorschlag zum weiteren Verfahrensweg (`eligible`, `pending_docs`, `in_review`) auf Grundlage von Zeugnisdaten, Sprachniveau und Länderklassifikation. Das ist eine Feststellung des Zugangs zu einer Bildungseinrichtung. Der Wortlaut unterscheidet nicht nach Trägerschaft; „Einrichtungen aller Ebenen" erfasst private Träger.

**Zur Ausnahme des Art. 6 Abs. 3.** Sie setzt kumulativ voraus, dass das System das Entscheidungsergebnis nicht wesentlich beeinflusst, dass eine der Bedingungen a–d vorliegt und dass **kein Profiling** stattfindet. Der letzte Halbsatz ist absolut: „Ungeachtet des Unterabsatzes 1 gilt ein in Anhang III aufgeführtes KI-System immer dann als hochriskant, wenn es ein Profiling natürlicher Personen vornimmt." Da das System personenbezogene Unterlagen automatisiert auswertet, um Eignung zu bewerten, dürfte Profiling im Sinne von Art. 4 Nr. 4 DSGVO (über Art. 3 Nr. 52 KI-VO) vorliegen. Die Ausnahme greift dann nicht — unabhängig von allem anderen.

**Aussageklasse:** `RECHTSFRAGE` mit technischer Subsumtion durch den Verfasser. **Konfidenz: mittel-hoch.** Abschließend zu bewerten durch eine Rechtsanwältin oder einen Rechtsanwalt.

---

#### F-12 — Die Hochrisiko-Pflichten gelten erst ab dem 2. Dezember 2027, nicht seit dem 2. August 2026

**Beweismittel:** N-01, N-02.

**Dies ist der wichtigste einzelne Befund dieses Gutachtens, weil er die Dringlichkeit aller regulatorischen Maßnahmen bestimmt — und weil eine Bewertung aus dem Stand von 2024 hier falsch gewesen wäre.**

Durch **Verordnung (EU) 2026/1744** vom 08.07.2026 (ABl. 24.07.2026, in Kraft seit 27.07.2026) wurde Art. 113 Abs. 3 Buchst. c der KI-VO neu gefasst. Er lautet nun:

> „Kapitel III Abschnitte 1, 2 und 3, mit Ausnahme von Artikel 6 Absatz 5, gelten ab dem:
> i) **2. Dezember 2027** in Bezug auf KI-Systeme, die gemäß Artikel 6 Absatz 2 und Anhang III als hochriskant eingestuft sind"

Damit gelten die Anforderungen an Hochrisiko-Systeme und die Pflichten von Anbietern und Betreibern (Art. 6–27) für dieses System **noch nicht**. Es verbleiben rund 15 Monate.

**Was bereits heute gilt:** Art. 4 KI-VO (KI-Kompetenz), seit 02.02.2025, seit dem 27.07.2026 in abgeschwächter Fassung als Förderpflicht: Anbieter und Betreiber „ergreifen Maßnahmen, um die Entwicklung der KI-Kompetenz ihres Personals zu unterstützen"; die Vorschrift „verpflichtet Anbieter oder Betreiber nicht, für irgendeine Person ein bestimmtes Niveau an KI-Kompetenz zu garantieren." Ebenfalls bereits anwendbar sind die Transparenzpflichten des Art. 50 (Kapitel IV).

**Bewertung.** Die Frist ist eine Chance, kein Freibrief. Die Maßnahmen M-01 bis M-06 sind ohnehin aus anderen Gründen erforderlich (Nachvollziehbarkeit, DSGVO) und schaffen zugleich die Grundlage für die Nachweise, die ab Dezember 2027 verlangt werden.

**Aussageklasse:** `TATSACHE` (Wortlaut der geltenden Fassung). **Konfidenz: hoch.**

---

#### F-13 — Der Betreiber ist voraussichtlich zugleich Anbieter

**Beweismittel:** N-01.

Art. 3 Nr. 3 KI-VO definiert den Anbieter als eine Person, „die ein KI-System … **entwickelt oder entwickeln lässt** und es unter ihrem eigenen Namen oder ihrer Handelsmarke … in Betrieb nimmt".

**Subsumtion.** Die W2G Academy GmbH lässt das System entwickeln und setzt es unter eigenem Namen ein. Beide Merkmale sind damit erfüllt — sie wäre Anbieter **und** Betreiber, mit den Pflichten aus Art. 16 wie aus Art. 26 und 27. NeXify AI wäre in dieser Konstellation Dritter in der Wertschöpfungskette, nicht Anbieter, solange das System nicht unter eigenem Namen als Produkt angeboten wird.

Zusätzlich zu beachten ist Art. 25 Abs. 1 Buchst. c: Wer die Zweckbestimmung eines nicht hochriskanten Systems so verändert, dass es hochriskant wird, gilt als Anbieter. Der Einsatz eines allgemeinen Sprachmodells über einen Aggregator für Zulassungsentscheidungen ist genau dieser Fall.

**Hinweis zur Vertragslage.** Sofern die Nutzungsbedingungen eines eingesetzten Vorprodukts den Einsatz in Hochrisiko-Anwendungen ausschließen, wäre der Einsatz vertragswidrig und die Unterstützungsansprüche nach Art. 25 Abs. 2 entfielen. **Dies wurde nicht geprüft** und ist als Maßnahme M-10 aufgenommen.

**Aussageklasse:** `RECHTSFRAGE`. **Konfidenz: mittel.**

---

#### F-14 — Die Transparenzpflicht nach Art. 50 ist bereits umgesetzt

**Beweismittel:** D-04.

Der öffentliche Rechtstext der Plattform enthält einen eigenen Abschnitt 12 „KI-Systeme und Transparenz (EU AI Act Art. 50)", der den Einsatz KI-gestützter Vorprüfung und des KI-Assistenten benennt und ausdrücklich auf Art. 50 verweist. Zusätzlich weist Abschnitt 4 darauf hin, dass KI-Ergebnisse keine bindenden Entscheidungen darstellen.

**Bewertung.** Das ist eine ordentliche Umsetzung und deutlich mehr, als bei vergleichbaren Anwendungen üblich ist. Sie wird ausdrücklich positiv festgestellt. Zur Belastbarkeit der dort zusätzlich getroffenen Aussage über Art. 22 DSGVO siehe F-15.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

---

### 8.3 Befunde zu B3 — Art. 22 DSGVO

---

#### F-15 — Die Aussage „keine automatisierte Entscheidungsfindung" ist plausibel, aber mit den vorhandenen Daten nicht belegbar

**Beweismittel:** D-04, M-02, M-03, N-06, N-11, N-12.

**Die geprüfte Aussage.** Im Rechtstext, Abschnitt 12, heißt es: „Es findet keine automatisierte Entscheidungsfindung im Einzelfall mit rechtlicher Wirkung statt (Art. 22 DSGVO). Die Verarbeitung erfolgt unter menschlicher Aufsicht."

**Der Maßstab.** Nach EuGH C-634/21 (N-06) kommt es nicht darauf an, wer formal entscheidet, sondern ob das Handeln des Menschen von der maschinellen Bewertung „maßgeblich geleitet" wird. Die Leitlinie WP251rev.01 (N-11) verlangt, dass die Beteiligung „nicht nur eine symbolische Geste" ist und die Entscheidung „von einer Person getroffen wird, die zur Änderung derselben befugt und befähigt ist". Die DSK (N-12, Ziffer 1.6) ergänzt: „Unzureichende Personalressourcen, Zeitdruck und fehlende Transparenz über den Entscheidungsweg der KI-gestützten Vorarbeit dürfen nicht dazu führen, dass Ergebnisse ungeprüft übernommen werden."

**Was für die Aussage spricht.**
- `staff_decision_required` ist in **30 von 32** Screenings auf `true` gesetzt (93,8 %). Das System verlangt also fast immer eine Staff-Entscheidung.
- Der Datensatz trägt den Vermerk „KI-Vorpruefung (Retrieval-first + Delta). Keine bindende Entscheidung. Staff-Review erforderlich."
- In allen **5** überhaupt vergleichbaren Fällen wich die tatsächliche Stufe vom KI-Vorschlag ab: zweimal Vorschlag `eligible` bei tatsächlich `lead_new`, zweimal Vorschlag `pending_docs` bei tatsächlich `conditional_offer`, einmal Vorschlag `pending_docs` bei tatsächlich `lead_new`.

**Was den Beleg verhindert.**
- Diese 5 Fälle sind die **einzigen** zuordenbaren (F-05); 27 Screenings sind verwaist.
- Die Wertebereiche sind bis auf `in_review` disjunkt (F-06). Eine Abweichung kann also auch bloß bedeuten, dass die beiden Felder Unterschiedliches beschreiben — sie ist kein Nachweis einer eigenständigen menschlichen Entscheidung.
- **In 4 der 5 vergleichbaren Fälle lag ein `ai_error` vor.** Es ist damit offen, ob der Mensch von der KI abwich oder ob gar keine KI-Empfehlung vorlag.
- Keine Protokollaktion hält fest, welche Empfehlung ein Bearbeiter gesehen und wie er entschieden hat. Die 46 Einträge mit Bezug zum Screening in `audit_logs` verteilen sich auf `auto_rescreening_triggered` (31) und `manual_rescreening` (15) — sie protokollieren die **Auslösung**, nicht Inhalt und Folge.

**Bewertung.** Die Aussage im Rechtstext ist nach dem heutigen Systemverhalten **plausibel** und wird durch die 94-Prozent-Quote der Staff-Pflicht gestützt. Sie ist aber gegenüber einer Aufsichtsbehörde oder einem Gericht **derzeit nicht nachweisbar**, weil die Daten, die den Nachweis führen müssten, nicht in vergleichbarer Form vorliegen. Das ist kein Vorwurf einer Falschaussage — es ist eine Beweislücke.

Die Rechenschaftspflicht nach Art. 5 Abs. 2 DSGVO verlangt, die Einhaltung nachweisen zu können. Eine Aussage, die man öffentlich trifft und intern nicht belegen kann, ist ein Risiko.

**Aussageklasse:** `FACHLICHE_BEWERTUNG`, gestützt auf `TATSACHE`-Befunde F-05, F-06, F-04. **Konfidenz: hoch** für die Beweislücke, **mittel** für die inhaltliche Plausibilität der Aussage.

---

#### F-16 — Eine Datenschutz-Folgenabschätzung ist erforderlich; ihr Vorliegen konnte nicht festgestellt werden

**Beweismittel:** N-03, N-13.

Art. 35 Abs. 3 lit. a DSGVO nennt als Pflichtfall die „systematische und umfassende Bewertung persönlicher Aspekte natürlicher Personen, die sich auf automatisierte Verarbeitung einschließlich Profiling gründet und die ihrerseits als Grundlage für Entscheidungen dient, die Rechtswirkung gegenüber natürlichen Personen entfalten oder diese in ähnlich erheblicher Weise beeinträchtigen".

Die DSK-Muss-Liste (N-13) führt unter **Nr. 11** ausdrücklich: „Einsatz von künstlicher Intelligenz zur Verarbeitung personenbezogener Daten zur Steuerung der Interaktion mit den Betroffenen oder **zur Bewertung persönlicher Aspekte der betroffenen Person**". Ergänzend einschlägig sind die Einträge Nr. 5 und Nr. 7.

**Zusätzlich gesondert zu betrachten** ist die nächtliche Verdichtung: Sie ist ein eigenständiger Verarbeitungsvorgang mit Zweckänderung (Bewerbungsbearbeitung → Wissensgewinnung) und Drittlandbezug.

**Feststellung.** Ob eine DSFA vorliegt, ließ sich technisch nicht ermitteln; das Vorhandensein eines solchen Dokuments ist am System nicht ablesbar. Diese Frage ist bereits als offener Punkt beim Auftraggeber vermerkt.

**Aussageklasse:** `RECHTSFRAGE`; das Vorliegen: `NICHT VERIFIZIERT`.

---

#### F-17 — Drittlandtransfer: Rechtsrahmen steht, die konkrete Deckung ist offen

**Beweismittel:** D-05, D-07, N-04, N-05, N-08, N-09.

**Was übermittelt wird.** Nach `knowledge_distill.py` gehen je Mail in den Prompt: Richtung, Betreff (200 Zeichen) und Nachrichtentext (600 Zeichen). Die Absenderadresse wird zwar aus der Datenbank geladen, aber **nicht** in den Prompt geschrieben — das ist eine bewusste und richtige Datensparsamkeit und wird positiv festgestellt. Der Nachrichtentext selbst enthält indes typischerweise Namen, Herkunftsland und Abschluss. Er bleibt damit personenbezogen; das Weglassen der Absenderadresse bewirkt keine Anonymisierung.

**Menge.** Bis zu 4.000 Mails je Nacht (200 + 200 Stapel zu je 10).

**Empfänger.** Ein US-Aggregator (F-09), der seinerseits an Modellanbieter weiterreicht.

**Rechtsrahmen am Stichtag.** Der Angemessenheitsbeschluss (EU) 2023/1795 ist **in Kraft**; die Nichtigkeitsklage wurde am 03.09.2025 abgewiesen (N-08). Das Rechtsmittel C-703/25 P ist anhängig und hat **keine aufschiebende Wirkung** (N-09). Ist der Empfänger nicht zertifiziert, greift der Beschluss nicht; dann sind Standardvertragsklauseln (N-05) nebst Transferfolgenabschätzung erforderlich.

**Offen.** Ob der eingesetzte Aggregator auf der Data-Privacy-Framework-Liste steht — und ob die von ihm eingeschalteten Modellanbieter je einzeln gedeckt sind —, konnte nicht festgestellt werden: Die amtliche Liste ist nur browserseitig durchsuchbar. **`NICHT VERIFIZIERT`.**

Ebenfalls nicht feststellbar war, ob ein Auftragsverarbeitungsvertrag nach Art. 28 DSGVO besteht und ob die Weiterverarbeitung zu eigenen Zwecken (Training) vertraglich ausgeschlossen ist. Nach Art. 28 Abs. 10 DSGVO gilt: Wer als Auftragsverarbeiter Zwecke und Mittel selbst bestimmt, ist insoweit eigener Verantwortlicher — die Konstruktion „reine Auftragsverarbeitung" scheitert dann.

**Bewertung.** Der Rechtsrahmen ist begehbar. Ob er tatsächlich begangen wird, ist eine Frage der Vertragslage, nicht der Technik. **Es ist mit einem messbaren Restrisiko zu rechnen**, das mit dem Ausgang von C-703/25 P steigen kann.

**Aussageklasse:** `TATSACHE` für Datenfluss und Menge; `RECHTSFRAGE` für die Bewertung; `NICHT VERIFIZIERT` für die konkrete Deckung.

---

### 8.4 Befunde zu B4 — Protokollierung und Überwachung

---

#### F-18 — Der Betrieb ist überwacht; die fachliche Ebene ist es nicht

**Beweismittel:** L-01, M-01, M-03, A-01.

**Was funktioniert.** Alle vier Dienste laufen (`backend` und `frontend` seit 6 Stunden, `mongo` und `minio` seit 6 Tagen). Es bestehen mehrere unabhängige Sicherungsebenen für den Betreuungskanal (Prozesswächter mit Herzschlagprüfung, stündlicher externer Erreichbarkeitscheck, systemd-Timer). 593 Protokolleinträge und 312 Telemetrie-Ereignisse liegen vor. Anmeldungen, Dokumenten-Uploads, -Freigaben und -Ablehnungen werden protokolliert.

**Was fehlt.** Kein Protokolleintrag hält den **Inhalt** einer KI-Empfehlung und die darauf folgende menschliche Entscheidung fest (`action ~ /ai_/i`: 0 Treffer; `~ /recommend/i`: 0 Treffer). Kein Alarm ist auf den Zustand „KI-Aufruf schlägt fehl" gelegt — die vier Fälle „Insufficient Balance" (F-04) blieben unbemerkt, bis sie im Rahmen dieser Erhebung auffielen.

**Bewertung.** Die Überwachung sichert die **Verfügbarkeit** ab, nicht die **fachliche Richtigkeit**. Das entspricht genau der im Prämortem (A-01) benannten Gefahr: nicht der Ausfall ist das Problem, sondern der stille Fehler. Die technische Ebene ist gut abgesichert, die fachliche Ebene ist blind.

**Aussageklasse:** `TATSACHE` für die Messwerte, `FACHLICHE_BEWERTUNG` für die Einordnung. **Konfidenz: hoch.**

---

## 9. Ursachen und Alternativhypothesen

### 9.1 Gemeinsame Ursache

Die Befunde F-01, F-03, F-05 und F-06 haben ein gemeinsames Muster: **Es fehlt eine durchgehende Prüfung der Datenwege von Ende zu Ende.** Jede Komponente funktioniert für sich — das Screening erzeugt ein Ergebnis, die Wissensbasis erzeugt Regeln, die Fallführung führt Stufen —, aber die Übergänge zwischen ihnen wurden nie als Ganzes geprüft. Deshalb fallen Brüche an genau diesen Übergängen auf: Wissen erreicht den Prüfpfad nicht, Prüfergebnisse verlieren ihre Bewerbung, Empfehlung und Ergebnis sprechen verschiedene Sprachen, und der Fehlerpfad protokolliert nicht.

Daraus folgt für die Maßnahmen: **Einzelkorrekturen genügen nicht.** Erforderlich ist ein Durchstich, der einen Vorgang von der Bewerbung über das Screening bis zur Entscheidung durchgängig prüft (Maßnahme M-01).

### 9.2 Geprüfte Gegenhypothesen

| Zu Befund | Gegenhypothese | Prüfung | Ergebnis |
| --- | --- | --- | --- |
| F-01 | „Der dritte Handler ist erreichbar, ich lese den Code falsch." | Quelltext Z. 355–375 vollständig gelesen; der zweite `try` hat bereits einen `except Exception`. | Gegenhypothese **widerlegt**. Der Handler ist unerreichbar. |
| F-02 | „Die Regeln werden an anderer Stelle geladen, nicht in `gather_institutional_knowledge`." | Nur teilweise geprüft — die Funktion wurde gelesen, nicht der gesamte Aufrufpfad des Screenings. | **Nicht abschließend widerlegt.** Restunsicherheit ausgewiesen; Prüfauftrag M-02. |
| F-05 | „Die Zuordnung gelingt über ein anderes Feld." | Beide plausiblen Felder (`_id`, `id`) geprüft; `applications` führt kein Feld `id`. | Gegenhypothese **widerlegt** für die geprüften Felder; eine dritte Verknüpfung ist nicht ausgeschlossen. |
| F-06 | „Es gibt eine Abbildungstabelle zwischen den Wertebereichen." | Nicht geprüft. | **Offen.** Sollte eine solche Abbildung existieren, entfällt der Befund teilweise. Prüfauftrag in M-03. |
| F-07 | „`status: verified` bedeutet etwas anderes als eine inhaltliche Prüfung." | Nicht abschließend geprüft — die Semantik des Feldes wurde nicht im Code verifiziert. | **Offen.** Die Kombination mit leerem `source_url` und `last_verified_by: system` stützt die Lesart als Scheingenauigkeit, beweist sie aber nicht. |
| F-12 | „Die ursprüngliche Frist 02.08.2026 gilt weiter." | Konsolidierte Fassung der KI-VO mit Änderungsmarkierung geprüft, Änderungsrechtsakt im Volltext abgerufen. | Gegenhypothese **widerlegt**. |
| F-15 | „Die Übernahmequote ist doch messbar, ich habe die falsche Verknüpfung genutzt." | Zuordnung und Wertebereiche beide separat gemessen. | Gegenhypothese **widerlegt** für die vorhandene Datenlage. |

**Was auch bei Wegfall des schwächsten Belegs bestehen bleibt:** Selbst wenn F-02, F-06 und F-07 sich durch weitere Prüfung entschärfen sollten, bleiben F-01, F-03, F-04 und F-05 unberührt — sie beruhen auf unmittelbar abgelesenem Quelltext und auf Zählungen im Datenbestand.

---

## 10. Technische Bewertung und Risiken

### 10.1 Einstufungsmaßstab

Die folgende Einstufung folgt **keiner benannten Norm** (siehe Abschnitt 7.4), sondern dieser im Dokument offengelegten Skala. Die Zahlen sind eine Ordnungshilfe, keine Messung; maßgeblich ist die Begründung im Text.

- **Eintritt:** 1 = unwahrscheinlich · 2 = möglich · 3 = wahrscheinlich · 4 = bereits eingetreten
- **Auswirkung:** 1 = gering · 2 = spürbar · 3 = erheblich · 4 = existenzgefährdend für das Projekt

### 10.2 Risikoregister

| ID | Risiko | Befund | Eintritt | Auswirkung | Bewertung |
| --- | --- | --- | --- | --- | --- |
| R-01 | Eine fehlerhafte Vorprüfung bleibt monatelang unbemerkt, weil Fehler stumm geschluckt werden | F-01, F-18 | 4 (eingetreten: der Fehlerpfad ist blind) | 3 | **hoch** |
| R-02 | Eine Zugangsentscheidung stützt sich auf eine als „geprüft" markierte, tatsächlich ungeprüfte Länderangabe | F-07 | 3 | 3 | **hoch** |
| R-03 | Der Nachweis, dass keine automatisierte Entscheidung stattfindet, kann nicht geführt werden | F-05, F-06, F-15 | 4 (eingetreten) | 3 | **hoch** |
| R-04 | Die Vorprüfung läuft ohne KI-Anteil, ohne dass es der Sachbearbeitung auffällt | F-04 | 4 (eingetreten, 10 von 32) | 2 | **mittel-hoch** |
| R-05 | Drittlandübermittlung ohne belegte vertragliche Grundlage | F-17 | 2 | 3 | **mittel-hoch** |
| R-06 | Die Wissensverdichtung kostet Geld und Laufzeit ohne Wirkung im Prüfpfad | F-02, F-08 | 4 (eingetreten) | 2 | **mittel** |
| R-07 | Bei einer Prüfung ist nicht rekonstruierbar, welches Modell eine Empfehlung erzeugt hat | F-03 | 3 | 2 | **mittel** |
| R-08 | Die Hochrisiko-Pflichten treffen das Projekt unvorbereitet zum 02.12.2027 | F-11, F-12, F-13 | 2 | 3 | **mittel** |
| R-09 | Die Sachbearbeitung gewöhnt sich an, KI-Vorschläge ungeprüft zu übernehmen | F-07, F-15, A-01 | 3 | 3 | **hoch** |
| R-10 | Das Gutachten selbst übersieht Fehler, weil sein Verfasser am Gegenstand mitgewirkt hat | Abschnitt 3.1 | 3 | 2 | **mittel** |

### 10.3 Was ausdrücklich gut ist

Ein Gutachten, das nur Mängel auflistet, ist unvollständig. Positiv festzustellen:

1. **Die Transparenzpflicht nach Art. 50 KI-VO ist umgesetzt** (F-14) — mit eigenem Abschnitt und ausdrücklichem Verweis. Das ist bei vergleichbaren Anwendungen selten.
2. **Der Staff-Vorbehalt ist im System verankert** (F-15) — 93,8 % der Screenings verlangen eine Staff-Entscheidung, und der Datensatz trägt einen expliziten Vermerk, dass keine bindende Entscheidung vorliegt.
3. **Datensparsamkeit in der Verdichtung** (F-17) — die Absenderadresse wird geladen, aber bewusst nicht an das Modell übermittelt.
4. **Fehlertoleranz der Verdichtungskette** (F-08) — ein Aussetzer des Anbieters „verbrennt" die betroffenen Mails nicht; sie bleiben unmarkiert und werden erneut aufgegriffen. Das ist sauber gelöst.
5. **Der KI-Fehler wird im Datensatz festgehalten** (F-04) — das Feld `ai_error` existiert und ist gefüllt. Ohne dieses Feld wäre dieser Befund gar nicht erhebbar gewesen.
6. **Mehrere unabhängige Sicherungsebenen** für die Betriebsverfügbarkeit (F-18).

---

## 11. Maßnahmen

Jede Maßnahme nennt Zielzustand, Dringlichkeit und Erfolgskontrolle. Dringlichkeitsstufen: `SOFORT` (akute Gefahr), `KURZFRISTIG` (erheblicher Schaden oder Eskalationsrisiko), `PLANBAR` (Mangel ohne akute Gefahr), `BEOBACHTEN`.

| ID | Maßnahme | Zu Befund | Dringlichkeit | Erfolgskontrolle |
| --- | --- | --- | --- | --- |
| **M-01** | Doppelten `except`-Block bereinigen: beide Fehlerpfade protokollieren, je Abruf die Trefferzahl mitschreiben | F-01 | **KURZFRISTIG** | Ein absichtlich fehlerhafter Abruf erzeugt einen Protokolleintrag mit Trefferzahl 0 |
| **M-02** | `gather_institutional_knowledge` um die 648 `institution`-Regeln erweitern; anschließend prüfen, ob sie im Prompt ankommen | F-02 | **KURZFRISTIG** | Der an das Modell gesendete Prompt enthält nachweislich Regeln aus `brain_memories` |
| **M-03** | Gemeinsames Begriffssystem zwischen `suggested_stage` und `current_stage` herstellen — entweder gleiche Werte oder eine dokumentierte Abbildungstabelle | F-06, F-15 | **KURZFRISTIG** | Für jeden Screening-Datensatz ist maschinell entscheidbar, ob der Empfehlung gefolgt wurde |
| **M-04** | Entscheidungsprotokoll einführen: je Vorgang festhalten, welche Empfehlung angezeigt wurde, wer entschieden hat, ob abgewichen wurde und mit welcher Begründung | F-15, F-18, R-03, R-09 | **KURZFRISTIG** | Eine Abweichungsquote ist jederzeit berichtbar |
| **M-05** | `ai_provider` aus dem tatsächlich verwendeten Anbieter befüllen statt als Festwert; Aggregator und Modell getrennt speichern | F-03 | **KURZFRISTIG** | Für jeden Datensatz ist die Verarbeitungskette rekonstruierbar |
| **M-06** | Screenings mit `ai_error` in der Aktenansicht sichtbar kennzeichnen; Alarm auf den Zustand „KI-Aufruf schlägt fehl" legen | F-04, R-04 | **KURZFRISTIG** | Ein herbeigeführter 402-Fehler erzeugt binnen einer Stunde eine Meldung, und die Akte zeigt den Hinweis |
| **M-07** | `status` in `anabin_knowledge` für alle nicht menschlich geprüften Einträge auf `unverified` zurücksetzen; in der Oberfläche kenntlich machen; Pflegefelder befüllen | F-07, R-02, R-09 | **KURZFRISTIG** | Kein Eintrag trägt `verified` ohne benannte prüfende Person und Quellenangabe |
| **M-08** | Ursache der 27 verwaisten Screenings klären (Löschung oder Kennungswechsel) und Wiederholung ausschließen | F-05 | **PLANBAR** | Neu erzeugte Screenings sind zu 100 % zuordenbar |
| **M-09** | Umgebungsvariablen `NEXIFY_ROUTER_*` umbenennen oder mit einem Kommentar versehen, der das tatsächliche Ziel benennt | F-09 | **PLANBAR** | Name und Laufzeitwert widersprechen sich nicht mehr |
| **M-10** | Vertragslage klären: Auftragsverarbeitungsvertrag, Ausschluss der Trainingsnutzung, Unterauftragsverarbeiterliste, DPF-Zertifizierung oder Standardvertragsklauseln, Zulässigkeit des Hochrisiko-Einsatzes nach den Nutzungsbedingungen | F-17, F-13, R-05 | **KURZFRISTIG** | Für jeden Empfänger liegt eine benannte Rechtsgrundlage vor |
| **M-11** | Datenschutz-Folgenabschätzung erstellen oder vorhandene um die KI-Vorprüfung und die nächtliche Verdichtung ergänzen | F-16 | **KURZFRISTIG** | Dokument liegt vor, beide Verarbeitungsvorgänge sind gesondert behandelt |
| **M-12** | Verdichtungspfad auf kontrollierbare Infrastruktur umstellen — gemessen empfiehlt sich `openai/gpt-oss-120b` bei nscale | F-17, F-08 | **PLANBAR** | Gegentest auf 10 echten Mails liefert gleichwertige Regeln; Formattreue ≥ 90 % |
| **M-13** | Schulung und Handreichung für die Sachbearbeitung: wie eine KI-Empfehlung zu prüfen ist, wann ihr zu widersprechen ist, was `ai_error` bedeutet | R-09, Art. 4 KI-VO | **PLANBAR** | Teilnahme dokumentiert; Art.-4-Pflicht nachweisbar erfüllt |
| **M-14** | Zweite, unbeteiligte Prüfinstanz für das Gesamtsystem beauftragen | Abschnitt 3.1, R-10 | **PLANBAR** | Ein Prüfbericht liegt vor, der nicht vom Verfasser dieses Gutachtens stammt |
| **M-15** | Vorbereitung auf den 02.12.2027: Rollenklärung Anbieter/Betreiber, Risikomanagement, technische Dokumentation, Protokollierung (mind. 6 Monate), Grundrechte-Folgenabschätzung | F-11, F-12, F-13, R-08 | **PLANBAR** | Ein Fahrplan mit Zwischenzielen liegt bis Ende Q1/2027 vor |
| **M-16** | DSK-Orientierungshilfe zu RAG (Oktober 2025) auswerten und auf die Verdichtungskette anwenden | N-16 | **PLANBAR** | Auswertung dokumentiert, Abweichungen benannt |

**Zur Reihenfolge.** M-01 bis M-07 sind kurzfristig, weil sie entweder eine bereits eingetretene Blindheit beheben (M-01, M-06), den Nachweis erst ermöglichen (M-03, M-04, M-05) oder eine Scheingenauigkeit beseitigen, auf die sich Menschen bereits verlassen (M-07). **M-01 und M-02 gehören zusammen** — die Anbindung des Wissens ohne Fehlerprotokollierung würde nur einen weiteren stillen Pfad schaffen.

**Kosten.** Es werden bewusst **keine** Kostenangaben gemacht. Grundlage dafür wären Mengengerüst, Preisstand, Region und Umsatzsteuerstatus; nichts davon wurde erhoben.

---

## 12. Direkte Beantwortung der Beweisfragen

**B1 — Welche Abweichungen vom technischen Sollzustand bestehen?**
Zehn Abweichungen sind belegt (F-01 bis F-10). Die vier gewichtigsten: (1) Zwei Fehlerpfade schlucken lautlos, der einzige Protokollierungspfad ist toter Code. (2) Die 648 aus dem Mailbestand gewonnenen Betriebsregeln erreichen die prüfende KI nicht. (3) 31 % der gespeicherten Screenings liefen mit fehlgeschlagenem KI-Aufruf, ohne dass dies für die Sachbearbeitung sichtbar wäre. (4) Die Länderklassifikation ist zu 94 % als „geprüft" markiert, obwohl keine Quellenangabe hinterlegt und als prüfende Instanz durchgehend „system" eingetragen ist.

**B2 — Einordnung nach der KI-Verordnung und Zeitpunkt der Pflichten.**
Die Vorprüfung erfüllt den Tatbestand des Anhangs III Nr. 3 Buchst. a und ist damit ein Hochrisiko-KI-System; die Ausnahme des Art. 6 Abs. 3 dürfte wegen Profilings absolut ausgeschlossen sein. **Die zugehörigen Pflichten gelten jedoch erst ab dem 2. Dezember 2027**, nachdem Art. 113 durch die Verordnung (EU) 2026/1744 geändert wurde. Heute bereits anwendbar sind Art. 4 (KI-Kompetenz) und Art. 50 (Transparenz) — Letzterer ist umgesetzt. Es verbleiben rund 15 Monate Vorlauf. Die abschließende rechtliche Bewertung, insbesondere zur Anbieterrolle, ist anwaltlich zu klären.

**B3 — Ist die Aussage zu Art. 22 DSGVO belegbar?**
**Nein, derzeit nicht.** Die Aussage ist nach dem Systemverhalten plausibel — 93,8 % der Screenings verlangen eine Staff-Entscheidung, und in allen fünf vergleichbaren Fällen wich das Ergebnis vom Vorschlag ab. Ein Nachweis ist aber nicht führbar: 27 von 32 Screenings sind keiner Bewerbung zuordenbar, die Wertebereiche von Empfehlung und Ergebnis sind bis auf einen Wert disjunkt, in vier der fünf vergleichbaren Fälle lag ohnehin ein KI-Fehler vor, und kein Protokoll hält Empfehlung und Entscheidung nebeneinander fest. Die Rechenschaftspflicht nach Art. 5 Abs. 2 DSGVO verlangt einen solchen Nachweis. **Das ist eine Beweislücke, kein Vorwurf einer Falschaussage.**

**B4 — Ist der Betrieb ausreichend protokolliert und überwacht?**
Für die Verfügbarkeit ja, für die fachliche Richtigkeit nein. Dienste, Erreichbarkeit und Betreuungskanal sind mehrfach und unabhängig abgesichert. Auf der fachlichen Ebene fehlt beides: kein Protokoll über Empfehlung und Entscheidung, kein Alarm auf „KI-Aufruf schlägt fehl". Dass vier Screenings an einem leeren Guthabenkonto scheiterten, fiel erst bei dieser Erhebung auf.

**B5 — Ist das Fachwissen tragfähig, und erreicht es die prüfende KI?**
Beides ist zu verneinen. Die Länderklassifikation umfasst 85 Länder, aber alle Pflegefelder sind leer, und der Status „verified" ist nicht durch eine Prüfung gedeckt (F-07). Das aus 25.061 Mails gewonnene Wissen ist zu 3,8 % verdichtet (F-08) und erreicht den Prüfpfad überhaupt nicht (F-02).

**B6 — Welche Maßnahmen mit welcher Dringlichkeit?**
Sieben kurzfristige Maßnahmen (M-01 bis M-07), dazu M-10 und M-11 aus rechtlichen Gründen; sieben planbare. Keine Maßnahme ist als `SOFORT` eingestuft: Es besteht **keine akute Gefahr**, die einen sofortigen Betriebsstopp rechtfertigen würde. Die kurzfristigen Maßnahmen beheben eingetretene Blindheit und Scheingenauigkeit — beides wirkt sich mit jedem weiteren Vorgang aus, aber nicht schlagartig.

---

## 13. Einschränkungen und weiterer Prüfbedarf

**Nicht geprüft, aber prüfbedürftig:**

1. Der vollständige Aufrufpfad des Screenings (nur `gather_institutional_knowledge` gelesen) — betrifft die Verlässlichkeit von F-02.
2. Ob eine Abbildungstabelle zwischen `suggested_stage` und `current_stage` existiert — betrifft F-06.
3. Die Semantik des Feldes `status` in `anabin_knowledge` im Code — betrifft F-07.
4. Ursache der 27 verwaisten Screenings — betrifft F-05.
5. Sicherheit: kein Penetrationstest, keine Schwachstellenanalyse der Abhängigkeiten, keine Detailprüfung der Zugriffsrechte.
6. Wiederherstellbarkeit: Sicherungen und ein Wiederanlauf wurden **nicht** geprüft. Das ist eine erhebliche Lücke für ein Live-System und sollte gesondert beauftragt werden.
7. Barrierefreiheit und die Anforderungen des Barrierefreiheitsstärkungsgesetzes wurden nicht geprüft.
8. Das tatsächliche Verhalten der Sachbearbeitung — nur durch Befragung und Beobachtung feststellbar.

**Ausdrücklich als `NICHT VERIFIZIERT` gekennzeichnet:**

- Ob eine Datenschutz-Folgenabschätzung vorliegt.
- Ob der eingesetzte Aggregator und die von ihm eingeschalteten Modellanbieter auf der Data-Privacy-Framework-Liste stehen.
- Ob ein Auftragsverarbeitungsvertrag besteht und ob die Trainingsnutzung ausgeschlossen ist.
- Ob die Kommissionsleitlinien zur Einstufung von Hochrisiko-KI-Systemen inzwischen final vorliegen.
- Der Inhalt der DSK-Orientierungshilfe zu RAG (Oktober 2025).
- Ob ein zweiter periodischer Überprüfungsbericht der Kommission zum Data Privacy Framework existiert.

---

## 14. Erklärung zu Unparteilichkeit, Hilfsmitteln und KI-Unterstützung

Dieses Gutachten wurde vollständig von einem KI-System erstellt. Es besteht **keine** öffentliche Bestellung, Vereidigung, Akkreditierung oder Zertifizierung des Verfassers.

Der Verfasser ist **nicht unabhängig**: Er hat am 06. und 07.09.2026 selbst am Untersuchungsgegenstand gearbeitet. Die Befunde F-03, F-09 und Teile von F-01 richten sich gegen die eigene Arbeit; F-09 korrigiert eine eigene, tags zuvor falsch begründete Aussage. Diese Offenlegung ersetzt keine Unabhängigkeit — sie macht sie nur überprüfbar. Maßnahme M-14 sieht deshalb eine zweite, unbeteiligte Prüfinstanz vor.

**Eingesetzte Hilfsmittel:** lesender SSH-Zugang zum Server; MongoDB-Abfragen (ausschließlich lesend); Quelltextlesung; Abruf amtlicher Primärquellen über Websuche und Direktabruf; ein eigens erstellter Modellvergleich auf **synthetischen, selbst geschriebenen** Testdaten ohne Personenbezug.

**Keine Erfindungen:** Es wurde kein Ortstermin behauptet, keine Messung erfunden und keine Normklausel zitiert, deren Wortlaut nicht vorlag. Wo Wissen fehlte, steht `NICHT VERIFIZIERT`.

**Verantwortung:** Ergebnis und Quellen sind vor jeder Verwendung durch einen verantwortlichen Menschen zu prüfen und freizugeben. Das Dokument trägt den Status **Entwurf**.

---

## 15. Anlagen- und Quellenverzeichnis

### 15.1 Anlagen auf dem Server

Verzeichnis `/root/patches-morgen-08-09/` auf srv1900840:

| Datei | Inhalt |
| --- | --- |
| `messung_gutachten.js` | Bestandsaufnahme aller Sammlungen (M-01) |
| `messung2.js` | Feldnamen und Werteverteilungen (M-02) |
| `messung3.js` | Detailbeweise Zuordenbarkeit, Wertebereiche, Pflegefelder (M-03) |
| `vergleich_modelle.py`, `vergleich_modelle.log` | Modellvergleich mit synthetischen Daten (M-04) |
| `nscale_modelle.py` | Abruf der Modellliste (M-05) |
| `BEFUND-WISSENSINTEGRATION.md` | Vorbefund zur Wissensintegration |
| `BEFUND-ANABIN-RECHTSLAGE.md` | Rechtslage zur Nutzung der anabin-Datenbanken |
| `BEFUND-LLM-PFAD-UND-NSCALE.md` | Modellpfad, Korrektur und Umstellungsvorschlag |
| `BEFUND-DATUMSTYPEN-VOLLBILD.md` | Vorbefund zu Datumstypen |

### 15.2 Amtliche Quellen (alle am 07./08.09.2026 abgerufen)

- Verordnung (EU) 2024/1689 (KI-VO), konsolidierte Fassung Stand 27.07.2026 — CELEX 02024R1689-20260727, EUR-Lex
- Verordnung (EU) 2026/1744 (Digital-Omnibus-Verordnung zur KI) — ABl. L, 2026/1744, 24.07.2026, EUR-Lex
- Verordnung (EU) 2016/679 (DSGVO) — CELEX 32016R0679, EUR-Lex
- Durchführungsbeschluss (EU) 2023/1795 (EU-US Data Privacy Framework) — CELEX 32023D1795, EUR-Lex
- Durchführungsbeschluss (EU) 2021/914 (Standardvertragsklauseln) — CELEX 32021D0914, EUR-Lex
- EuGH, 07.12.2023, C-634/21, ECLI:EU:C:2023:957 — EUR-Lex
- EuGH, 27.02.2025, C-203/22, ECLI:EU:C:2025:117 — EUR-Lex
- EuG, 03.09.2025, T-553/23, ECLI:EU:T:2025:831 — EUR-Lex
- EuGH, C-703/25 P (anhängig) — ABl. C, C/2025/6610, 22.12.2025
- EuGH, C-568/25 (anhängig) — ABl. C, C/2025/6156, 24.11.2025
- Artikel-29-Datenschutzgruppe, WP251rev.01, angenommen 06.02.2018, vom EDSA bestätigt 25.05.2018
- DSK, Orientierungshilfe „Künstliche Intelligenz und Datenschutz", Version 1.0, 06.05.2024
- DSK, Muss-Liste nach Art. 35 Abs. 4 DSGVO, nicht-öffentlicher Bereich, Version 1.1, 17.10.2018
- DSK, Orientierungshilfe zu TOM bei KI-Systemen, Version 1.0, Juni 2025
- DSK, Orientierungshilfe zu generativer KI mit RAG-Methode, Version 1.0, Oktober 2025 (nicht ausgewertet)
- EDSA, Stellungnahme 28/2024, angenommen 02.12.2024
- Europäische Kommission, Entwurf der Leitlinien zur Einstufung von Hochrisiko-KI-Systemen, 19.05.2026 (Entwurf, nicht verwendet)

### 15.3 Abkürzungen

| Abkürzung | Bedeutung |
| --- | --- |
| DSFA | Datenschutz-Folgenabschätzung (Art. 35 DSGVO) |
| DSK | Konferenz der unabhängigen Datenschutzaufsichtsbehörden des Bundes und der Länder |
| DPF | EU-US Data Privacy Framework |
| EDSA | Europäischer Datenschutzausschuss |
| KI-VO | Verordnung (EU) 2024/1689 über künstliche Intelligenz |
| LLM | großes Sprachmodell |
| SCC | Standardvertragsklauseln nach Art. 46 Abs. 2 lit. c DSGVO |

---

*Ende des Gutachtens NEXIFYAI-GU-2026-09-54564, Fassung 1.0 (Entwurf), 08.09.2026.*

---

## 16. Nachtrag 1 zur Fassung 1.0

**Erstellt:** 08.09.2026, 01:00 Uhr Europe/Berlin
**Änderungsgrund:** Ein in Fassung 1.0 als `NICHT VERIFIZIERT` ausgewiesener Punkt wurde nachträglich verifiziert.
**Betroffene Stelle:** Abschnitt 8.3, Befund **F-17**, dort der Absatz „Offen", sowie Abschnitt 13 (Liste der nicht verifizierten Punkte) und Abschnitt 10.2, Risiko **R-05**.

Dieser Nachtrag überschreibt Fassung 1.0 nicht. Fassung 1.0 bleibt in ihrem Wortlaut gültig; die dort getroffene Feststellung „`NICHT VERIFIZIERT`" war zum Zeitpunkt ihrer Erstellung zutreffend.

### 16.1 Neuer Befund F-19 — Der eingesetzte Aggregator ist nicht DPF-zertifiziert

**Beweismittel:** B-01 (neu) — eigene Abfrage der amtlichen Data-Privacy-Framework-Liste des U.S. Department of Commerce, `dataprivacyframework.gov/list`, am 08.09.2026 gegen 00:53 Uhr Europe/Berlin.

**Vorgehen und Ergebnis.** In Fassung 1.0 konnte dieser Punkt nicht geklärt werden, weil die amtliche Liste eine rein browserseitig gerenderte Anwendung ist und ihre Datenendpunkte nicht öffentlich antworten. Die Abfrage wurde daher im Browser durchgeführt:

1. Suchbegriff „OpenRouter", Filter **ALL** (also aktive *und* inaktive Teilnehmer): **„Query returned no results."**
2. Zusätzlich wurde die Schaltfläche „Inactive Participants" betätigt — ebenfalls kein Treffer.

**Gegenprobe.** Damit der Negativbefund nicht auf einer defekten Suche beruht, wurde derselbe Suchweg mit dem Kontrollbegriff „Salesforce" durchlaufen. Dieser lieferte Treffer (unter anderem „Krux Digital LLC" und „Demandware LLC"). **Die Suche funktioniert; der Negativbefund ist echt.**

**Feststellung.** Der für die nächtliche Wissensverdichtung eingesetzte Aggregator ist am Stichtag **nicht** auf der Data-Privacy-Framework-Liste geführt.

**Aussageklasse:** `TATSACHE`. **Konfidenz: hoch.**

### 16.2 Auswirkung auf F-17 und R-05

Der Angemessenheitsbeschluss (EU) 2023/1795 (N-04) gilt ausschließlich für Übermittlungen an Organisationen, die auf dieser Liste geführt werden. **Für diese Übermittlung greift Art. 45 DSGVO damit nicht.**

Es verbleiben:

- **Art. 46 Abs. 2 lit. c DSGVO** — Standardvertragsklauseln nach Durchführungsbeschluss (EU) 2021/914 (N-05), Modul 2 beziehungsweise Modul 3 bei Weiterreichung an Modellanbieter, zusammen mit einer Transfer-Folgenabschätzung nach Klausel 14. Ob solche Klauseln vereinbart sind, ist eine Vertragsfrage und war technisch nicht feststellbar; sie bleibt offen (Maßnahme M-10).
- **Art. 49 DSGVO** — als eng auszulegende Ausnahme für Einzelfälle. Für einen wiederkehrenden nächtlichen Massenversand von bis zu 4.000 Nachrichten ist das **kein tragfähiger Weg**.

**Neubewertung von R-05** („Drittlandübermittlung ohne belegte vertragliche Grundlage"): Eintritt steigt von 2 (möglich) auf **3 (wahrscheinlich)**, da der einfachste Rechtfertigungsweg nachweislich ausscheidet und der verbleibende Weg unbelegt ist. Auswirkung bleibt 3. Bewertung damit **hoch** statt mittel.

**Maßnahme M-10 wird von `KURZFRISTIG` auf die höchste Dringlichkeitsstufe innerhalb der kurzfristigen Maßnahmen gehoben** und ist vor der nächsten planmäßigen Übermittlung zu klären. Eine `SOFORT`-Einstufung im Sinne einer akuten Gefahr für Gesundheit oder Sicherheit liegt weiterhin nicht vor; die Dringlichkeit ist rechtlicher, nicht sicherheitstechnischer Natur.

### 16.3 Handlungsempfehlung

Solange keine Standardvertragsklauseln nebst Transfer-Folgenabschätzung belegt sind, empfiehlt sich, die nächtliche Verdichtung **auszusetzen**. Der Preis dafür ist gering und vollständig umkehrbar: ein Tag Verzug bei einem Bestand, dessen Abarbeitung ohnehin mehrere Nächte braucht, und der derzeit — siehe Befund F-02 — im Prüfpfad ohnehin keine Wirkung entfaltet.

Der Gegenweg ist ebenfalls vorbereitet: Die Umstellung des Verdichtungspfads auf einen kontrollierbaren Anbieter (Maßnahme M-12, gemessen empfohlen `openai/gpt-oss-120b` bei nscale) beseitigt die Frage in der Sache, statt sie vertraglich zu verwalten.

**Nicht getan und warum:** Der Verfasser hat den Zeitplan der nächtlichen Verdichtung **nicht** angehalten. Eine solche Änderung wäre eine schreibende Aktion an Kundeninfrastruktur außerhalb des vereinbarten Betriebsfensters (Mo–Fr 08:00–18:00 Europe/Berlin); eine Kundenmeldung, die die Notfall-Ausnahme trägt, liegt nicht vor. Die Entscheidung ist dem Auftraggeber vorgelegt und ihm vorbehalten.

### 16.4 Fortbestehende offene Punkte

Unberührt von diesem Nachtrag bleiben offen: das Vorliegen einer Datenschutz-Folgenabschätzung, das Bestehen und der Inhalt eines Auftragsverarbeitungsvertrags, der Ausschluss der Trainingsnutzung, die Zertifizierungslage der vom Aggregator eingeschalteten Modellanbieter je einzeln, sowie sämtliche unter Abschnitt 13 genannten technischen Prüfaufträge.

---

*Ende des Nachtrags 1 zu NEXIFYAI-GU-2026-09-54564, 08.09.2026.*
