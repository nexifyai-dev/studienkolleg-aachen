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

## Fehler 12: Task-Erstellung wirft 500 wegen ObjectId-Serialisierung
- **Fehlerbild**: POST /api/tasks lieferte 500 Internal Server Error
- **Ursache**: MongoDB insert_one() fügt _id (ObjectId) zum Dict hinzu; datetime-Objekte nicht serialisiert
- **Bereich**: Backend / tasks.py
- **Erkennung**: Testing Agent (iteration_12.json)
- **Behebung**: _id aus Response ausschließen, datetime zu ISO-String konvertieren
- **Vermeidungsregel**: Bei JEDEM insert_one() den Response-Dict von _id bereinigen und datetime-Felder serialisieren. Nie das Original-Dict direkt returnen.

## Fehler 13: Messaging ohne Konversation → leere Seite, kein Senden möglich
- **Fehlerbild**: Bewerber-Messaging zeigte "Noch keine Nachrichten" ohne Möglichkeit, eine Konversation zu starten
- **Ursache**: Frontend sendete conversation_id=undefined ohne recipient_id; Backend konnte keine sinnvolle Konversation erstellen
- **Bereich**: Backend messaging.py + Frontend MessagesPage.js
- **Erkennung**: User-Feedback in Phase 3.7i
- **Behebung**: Auto-Support-Conversation via GET /api/conversations/support; Auto-Staff-Zuweisung als Gesprächspartner
- **Vermeidungsregel**: Messaging-Systeme IMMER mit einem Default-Kanal bauen. Nie darauf vertrauen, dass eine Konversation bereits existiert.

## Fehler 14: Portalnavigation inkonsistent (Sidebar vs. Top-Header)
- **Fehlerbild**: Staff hatte Top-Header, Applicant noch linke Sidebar
- **Ursache**: Nur StaffLayout wurde in 3.7i umgebaut, ApplicantLayout nicht
- **Bereich**: Frontend / ApplicantLayout.js
- **Erkennung**: User-Feedback Phase 3.7j
- **Behebung**: ApplicantLayout komplett auf Top-Header umgebaut (identisches Prinzip wie StaffLayout)
- **Vermeidungsregel**: Strukturelle Änderungen IMMER portalweit denken. Wenn ein Layout-Konzept wechselt, ALLE Portal-Layouts prüfen.

## Fehler 15: Bewerbungsformular ohne Account-Erstellung
- **Fehlerbild**: Bewerber konnten Bewerbung einreichen, aber hatten keinen Portalzugang
- **Ursache**: leads/ingest erstellte User ohne Passwort; separater Registrierungsschritt nötig
- **Bereich**: Backend leads.py + Frontend ApplyPage.js
- **Erkennung**: Fachliche Anforderung Phase 3.7j
- **Behebung**: Passwort-Felder im Formular, Backend erstellt Account + setzt Auth-Cookies → Auto-Redirect
- **Vermeidungsregel**: Bewerbungsflows IMMER mit Account-Erstellung koppeln (Portal-first-Funnel)

## Fehler 16: i18n-Keys nicht übersetzt angezeigt
- **Fehlerbild**: Neue Formular-Felder zeigten Rohtext statt Übersetzung (z.B. "apply.account_title")
- **Ursache**: Neue t()-Aufrufe ohne korrespondierende JSON-Einträge
- **Bereich**: Frontend / locales
- **Erkennung**: Screenshot-Prüfung in Phase 3.7j
- **Behebung**: DE und EN Translations ergänzt
- **Vermeidungsregel**: Bei JEDEM neuen t()-Aufruf sofort BEIDE Sprachdateien prüfen und ergänzen

## Arbeitsprinzip: "Sichtbar reicht nicht – operativ bearbeitbar ist Pflicht"
- Dieses Prinzip gilt als Dauerregelung für alle zukünftigen Runs
- Jede UI-Komponente muss nicht nur angezeigt werden, sondern real operativ funktionieren
- Gilt für: Aufgaben, Nachrichten, Dokumente, Status, Wiedervorlagen, Export

---

## Prüfcheckliste vor jedem Run
1. Werden UI-Änderungen systemweit ausgerollt?
2. Sind DE + EN gleichzeitig aktualisiert?
3. Gibt es sichtbare Staging-/Debug-Hinweise im Frontend?
4. Wird der Preview-Zustand gegen die Änderungen verifiziert?
5. Sind die Drive-Anforderungen konkret gegengeprüft?
6. Keine Festpreise in neuen Texten/Templates?
7. KI nur über NSCall?
