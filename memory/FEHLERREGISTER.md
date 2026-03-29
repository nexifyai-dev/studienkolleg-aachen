# Fehlerregister & Lessons Learned – W2G Platform

## Zweck
Strukturiertes Verzeichnis bereits gemachter Fehler und daraus abgeleiteter Vermeidungsregeln.
Vor jedem Run gegen dieses Register prüfen.

---

## Fehler 1: Home-Seite angepasst, Unterseiten nicht konsequent mitgezogen
- **Fehlerbild**: Farb-/Design-Änderungen wurden auf der Home-Seite gemacht, aber Unterseiten (Courses, Services, Contact, Legal) nicht aktualisiert.
- **Ursache**: Änderungen wurden nur punktuell in einer Datei vorgenommen statt systemweit über CSS-Variablen / Tailwind-Config.
- **Bereich**: Frontend / Public Pages
- **Erkennung**: Visueller Vergleich zwischen Seiten
- **Behebung**: Alle Public Pages nachträglich gleichgezogen
- **Vermeidungsregel**: Bei jeder Farb-/Spacing-/Schrift-Änderung: Tailwind-Config oder CSS-Variablen ändern, NICHT einzelne Dateien. Nach Änderung alle Seiten visuell gegenchecken.

## Fehler 2: Handoff sagte "fertig", Preview zeigte etwas anderes
- **Fehlerbild**: Abschluss-Summary meldete Feature als "done", aber der tatsächliche Preview-Zustand war inkonsistent.
- **Ursache**: Agent verließ sich auf Code-Annahmen statt den sichtbaren Zustand zu verifizieren.
- **Bereich**: Arbeitsweise / QA
- **Erkennung**: User-Feedback nach Lauf-Abschluss
- **Behebung**: Regel "Preview schlägt Handoff" eingeführt
- **Vermeidungsregel**: Vor jedem finish: mindestens 1 Screenshot der betroffenen Seite machen und gegen das Summary verifizieren. Keine Behauptung ohne visuelle Bestätigung.

## Fehler 3: Rechtsseiten wirkten trotz Codeänderung weiter unfertig
- **Fehlerbild**: [OFFEN]- und [HINWEIS]-Blöcke waren als sichtbare UI-Warnboxen implementiert und wurden erst spät als Problem erkannt.
- **Ursache**: Staging-Hinweise wurden als Teil des Content-Modells eingebaut statt als interne Kommentare.
- **Bereich**: Frontend / LegalPage.js
- **Erkennung**: User-Review der Datenschutz-/Impressum-Seiten
- **Behebung**: Alle [OFFEN]/[HINWEIS]-Blöcke entfernt, offene Punkte intern in PRD.md dokumentiert
- **Vermeidungsregel**: Keine Staging-/Vorbehalts-Texte in sichtbare UI einbauen. Offene rechtliche Punkte IMMER NUR intern (PRD.md, Mem0) dokumentieren.

## Fehler 4: Farb-/Spacing-Anpassungen nicht systemweit ausgerollt
- **Fehlerbild**: Header-Spacing wurde in PublicNav optimiert, aber andere Layouts (Staff, Applicant) wurden nicht geprüft.
- **Ursache**: Isolierte Änderung ohne Systemcheck
- **Bereich**: Frontend / Layout-Komponenten
- **Erkennung**: Visueller Vergleich
- **Behebung**: Alle Layouts konsistent geprüft und angepasst
- **Vermeidungsregel**: Bei Layout-/Spacing-Änderungen ALLE Layout-Dateien prüfen (PublicNav, StaffLayout, ApplicantLayout, PublicFooter).

## Fehler 5: i18n nicht auf allen Public-Seiten konsistent
- **Fehlerbild**: Einige Textschlüssel fehlten in EN-Locale oder waren nicht übersetzt.
- **Ursache**: Neue Texte wurden nur in DE angelegt, EN-Pendant vergessen.
- **Bereich**: Frontend / Locales
- **Erkennung**: Sprachumschaltung im Preview
- **Behebung**: Fehlende EN-Schlüssel nachgetragen
- **Vermeidungsregel**: Jeder neue Text-Schlüssel MUSS sofort in BEIDEN Locales (de + en) angelegt werden. Kein Commit ohne DE+EN Paar.

## Fehler 6: Sichtbarer UI-Zustand nicht gegen Codezustand verifiziert
- **Fehlerbild**: Code-Changes wurden gemacht, aber nicht visuell im Preview bestätigt.
- **Ursache**: Vertrauen auf Code statt auf sichtbares Ergebnis
- **Bereich**: Arbeitsweise
- **Erkennung**: User-Feedback
- **Behebung**: Screenshot-Pflicht vor Abschluss eingeführt
- **Vermeidungsregel**: Nach jeder UI-relevanten Änderung: Screenshot oder curl-Verifizierung. Nicht "blind" abschließen.

## Fehler 7: Projektanforderungen nicht vollständig gegen Quellen geprüft
- **Fehlerbild**: Anforderungen aus Drive-Dokumenten wurden teilweise übersehen oder nicht explizit gegengeprüft.
- **Ursache**: Drive-Check war oberflächlich ("Drive geprüft" ohne Inhalt)
- **Bereich**: Arbeitsweise / Anforderungsmanagement
- **Erkennung**: User-Feedback
- **Behebung**: Drive-Gegenprüfung mit konkreter Dokumentation welche Quellen geprüft, was verifiziert/offen
- **Vermeidungsregel**: Drive-Check MUSS im Abschluss belastbar dokumentiert werden: Welche Dateien, welche Anforderungen, was verifiziert, was offen.

## Fehler 8: Cookie-Consent nur einmalig, nicht nachträglich bearbeitbar
- **Fehlerbild**: Cookie-Banner konnte nur beim ersten Besuch bedient werden, danach keine Änderungsmöglichkeit.
- **Ursache**: Nur "first-visit" Logik implementiert, kein Reopen-Mechanismus
- **Bereich**: Frontend / CookieBanner
- **Erkennung**: User-Review in Phase 3.7g
- **Behebung**: Manage-Modus, Footer-Link, Event-basierter Reopen
- **Vermeidungsregel**: Consent-Systeme IMMER mit Änderungsmöglichkeit bauen. Footer-Link ist Pflicht.

## Fehler 9: Dashboard ohne operative Arbeitsfähigkeit
- **Fehlerbild**: Dashboard zeigte nur statische KPI-Karten und eine Tabelle ohne klickbare Zeilen. Kein direkter Zugriff auf Bewerber möglich.
- **Ursache**: Rein dekorativer Aufbau statt operativem Arbeits-Dashboard
- **Bereich**: Frontend / StaffDashboard.js
- **Erkennung**: User-Review der Portal-Screenshots in Phase 3.7h
- **Behebung**: Kompletter Rewrite mit klickbaren Zeilen, Quick Actions, Handlungsbedarf-Sidebar
- **Vermeidungsregel**: Dashboards IMMER als Arbeits-Tool bauen. Jeder angezeigte Datensatz muss anklickbar/bearbeitbar sein.

## Fehler 10: Bewerberdaten nicht manuell bearbeitbar
- **Fehlerbild**: Alle Felder in der Bewerberdetailansicht waren read-only. Kein Edit-Mechanismus.
- **Ursache**: Nur Anzeige-Logik implementiert, keine Inline-Edit-Funktionalität
- **Bereich**: Frontend + Backend / ApplicantDetailPage + applications.py
- **Erkennung**: User-Review in Phase 3.7h
- **Behebung**: EditableField-Komponente, PUT /profile Endpunkt, Audit-Trail
- **Vermeidungsregel**: Bei Datenansichten IMMER prüfen: Muss dieses Feld editierbar sein? Staff/Admin brauchen operative Bearbeitungsmöglichkeiten.

## Fehler 11: Keine Bearbeitungshistorie sichtbar im UI
- **Fehlerbild**: Audit-Trail existierte im Backend, war aber im Frontend nicht sichtbar.
- **Ursache**: Backend-only Audit ohne UI-Darstellung
- **Bereich**: Frontend / ApplicantDetailPage
- **Erkennung**: User-Review in Phase 3.7h
- **Behebung**: ActivityHistory-Komponente, GET /activities Endpunkt, unified stream
- **Vermeidungsregel**: Audit-Daten IMMER auch im UI zugänglich machen (mindestens als "Bearbeitungsverlauf").

---

## Prüfcheckliste vor jedem Run
1. Werden UI-Änderungen systemweit ausgerollt?
2. Sind DE + EN gleichzeitig aktualisiert?
3. Gibt es sichtbare Staging-/Debug-Hinweise im Frontend?
4. Wird der Preview-Zustand gegen die Änderungen verifiziert?
5. Sind die Drive-Anforderungen konkret gegengeprüft?
6. Keine Festpreise in neuen Texten/Templates?
7. KI nur über NSCall?
