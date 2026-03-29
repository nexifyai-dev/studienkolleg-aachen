# Fehlerregister (Mem0) – Studienkolleg Aachen / Way2Germany

## Dauerpflichten
1. **Mem0 laden** vor jedem Lauf
2. **Google-Drive-Ordner** erneut prüfen (`https://drive.google.com/drive/folders/1325C5JMqfIYuSfZNN7FlhkNWGvsCgBnW`)
3. **Fehlerregister** gegenprüfen
4. Arbeitsplan gegen **Drive + Mem0 + Fehlerregister + Preview** synchronisieren
5. Nach jeder Änderung **Mem0 aktualisieren**
6. **Preview schlägt Handoff** – nichts als fertig melden, was im sichtbaren Zustand nicht stimmt
7. KI nur über **NSCall / nscale**
8. **Keine Potenzielle Verbesserungen** im Finish-Summary
9. Sprache: **Deutsch** in allen Interaktionen

## Vermeidungsregeln (dauerhaft)

### V1 – "Sichtbar reicht nicht"
Jede operative Funktion (Aufgaben, Nachrichten, KI-Tools, Dokumente) muss **wirklich bearbeitbar** sein:
- aufrufbar, editierbar, statusfähig, filterbar, zuweisbar, weiterverarbeitbar, historisiert
- Eine reine Anzeige/Vorschau ohne echte Aktion ist KEIN fertiges Feature

### V2 – CI-Blau-Button-Regel
- **Alle** Portal-Buttons: CI-Blau (`primary` = #113655) als Standard
- Sekundär: Outline/Neutral nur bei Primär-/Sekundär-Paaren
- Kein zufälliges Amber/Grün/Orange für Standard-Aktionen
- Hover/Disabled/Active/Focus konsistent

### V3 – Daten-Joining bei GET-Endpunkten
Wenn ein Backend-Endpunkt eine MongoDB-Entität zurückgibt, die eine Referenz-ID enthält (z.B. `applicant_id`), MUSS das referenzierte Objekt gejoined und als Unterobjekt mitgeliefert werden. Leere Detailansichten = Bug.

### V4 – i18n-Synchronisation
`language_pref` des Benutzers MUSS bei Login/Auth-Check mit i18next synchronisiert werden. Browser-Language-Detection allein reicht nicht.

### V5 – CORS + Cookies für Deployment
- `REACT_APP_BACKEND_URL` = leer (relative URLs → Same-Origin)
- `COOKIE_SECURE=true`, `COOKIE_SAMESITE=none` für HTTPS-Deployment
- Keine absolute URLs für API-Calls im Frontend

### V6 – Keine generischen Platzhalter
- Kein "React App" als Seitentitel
- Favicon = Marken-Icon, nicht Default-React
- Meta-Descriptions = sinnvoll, nicht generisch

### V7 – JSON-Sonderzeichen
Deutsche typografische Anführungszeichen (z.B. „…") dürfen NICHT in JSON-Dateien verwendet werden. Nur ASCII-Quotes ('...').

## Bekannte Fehlerhistorie

### Phase 3.7i–3.7j
- CORS-Konfiguration für Deployment fehlerhaft → gefixt (Wildcard + Credentials ungültig)
- N+1-Queries in applications/messaging/teacher → gefixt
- Sidebar-Navigation → ersetzt durch Top-Navigation

### Phase 3.7k
- Hardcodierte Deutsche Texte im Bewerberportal → alle auf t() umgestellt
- Messaging-UI: Tote Flächen, nicht bündig → Flex-Layout gefixt
- KI-Prüfung passiv → "Vorschlag übernehmen" mit Statuswechsel + Audit
- Login-Bug deployed: CORS * + credentials: true → relative URLs als Fix
- index.html: "React App" → "Studienkolleg Aachen – Way2Germany"
- SEO: Fehlende Meta-Tags auf allen Public Pages → react-helmet-async

### Phase 3.7l
- Aufgaben-Modul: Flache Liste ohne Bearbeitbarkeit → komplettes Rewrite mit Detail-Modal, Notizen, Anhänge, Historie, Filter, Zuweisung
- CI-Blau: Amber/Grün-Buttons in Dashboard/Detail/Consents → einheitlich CI-Blau
- Favicon: Fehlend → W2G-Icon generiert und eingebunden
- Bewerberdetail: Leere Kernfelder (Name, E-Mail, Telefon) → Backend-Join gefixt
- i18n: Browser-Language statt User-Pref → syncLanguage bei Login/Auth-Check
- Partner-Portal: referral_code vs referred_by Mapping-Fehler → gefixt

## Lessons Learned
1. Backend-GET-Endpunkte für Detailansichten IMMER mit Joins testen
2. i18n-Sprachwechsel darf nicht allein auf Browser-Detection basieren
3. CORS-Wildcard mit Credentials = Browser-Blockade
4. Relative Frontend-URLs lösen Cross-Origin-Probleme dauerhaft
5. Aufgaben/operative Module müssen VOR Fertigmeldung real bearbeitbar sein, nicht nur anzeigbar
6. CI-Farben systemweit, nicht punktuell

## Pre-Run-Checkliste
1. Mem0 geladen?
2. Drive-Ordner geprüft?
3. Fehlerregister gegengeprüft?
4. Preview-Screenshots als Prüfgrundlage?
5. Aufgaben-/Feature-Operabilität getestet (nicht nur sichtbar)?
6. CI-Blau durchgehend?
7. KI nur über NSCall?
