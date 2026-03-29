# 16_designsystem_ableitung.md

## Designprinzipien

### Verifiziert
- klar
- professionell
- ruhig
- vertrauenswürdig
- keine visuelle Unruhe
- keine beliebige Template-Optik
- mobile first
- barrierearm

### Projektspezifische Ableitung
Das System braucht zwei Designmodi innerhalb einer Designfamilie:
1. **Public Conversion Mode** – emotionaler, aber kontrolliert.
2. **Portal Operations Mode** – funktional, klar, status- und aufgabenorientiert.

## Design-Tokens

### Farben

#### Verifiziert aus Styleguide
- Dunkelblau: `#113655`
- Hellblau: `#B3CDE1`

#### Empfohlene Systemableitung
- `--color-primary: #113655`
- `--color-accent: #B3CDE1`
- `--color-accent-2`: aus Brand sekundär ableiten, erst nach finalem Systemtest festlegen
- neutrale Grauskala 100–900
- Statusfarben:
  - success
  - warning
  - danger
  - info

## Typografie

### Verifiziert
- **Arboria** für Fließtext / Standardschrift
- **KG Second Chances Sketch** als dekorative Display-Schrift

### Umsetzungsempfehlung
- Arboria als Primärschrift, sofern Lizenz und Webeinsatz gesichert sind.
- Falls webtechnisch/lizenzrechtlich nicht sauber verfügbar:
  - Fallback-Entscheidung dokumentiert treffen,
  - keine ungeprüfte Ersatzschrift stillschweigend austauschen.
- KG Second Chances Sketch nur sparsam und nicht in funktionalen UI-Bereichen.

## Komponentenbibliothek

### Pflicht-Komponenten Public
- Header / Nav
- Hero
- Feature Grid
- Trust / Proof Cards
- FAQ Accordion
- CTA Sections
- Formulare
- Footer

### Pflicht-Komponenten Portal
- Dashboard Cards
- Status Badges
- Timeline / Stepper
- Document Cards
- Message Thread
- Task List
- Invoice Table / Cards
- Course Cards
- Notification Center
- Search / Filter
- Drawer / Sheet
- Toast / Alert
- Empty State
- Error State

## Layoutlogik

### Public
- klare Hero-Zone,
- Abschnittswechsel mit ruhigen Flächen,
- starke CTA-Hierarchie,
- segmentierte Angebotskarten,
- Proof-Bausteine früh sichtbar.

### Portal
- informationshierarchisch,
- Task- und Statusfokus,
- Dashboard zuerst,
- Kontextpaneele statt tiefer Seitensprünge,
- mobile Karten statt komplexer Tabellen.

## Responsivität

### Pflicht-Breakpoints
- 360
- 375
- 390
- 430
- 480
- 768
- 820
- 1024
- 1280
- 1440
- 1920

### Mobile-First-Regeln
- Applicant-Portal auf 375 px zuerst entwerfen.
- Tabellen nur mit definierter Mobilstrategie.
- Upload, Timeline und Messages als Kernpfade mobil optimieren.

## Accessibility

### Pflicht
- WCAG-konforme Kontraste
- semantische Buttons/Links
- Fokusführung
- Screenreader-Struktur
- verständliche Fehlermeldungen
- Touch-Ziele mindestens 44x44 px
- Tastaturbedienung
- keine reinen Farbzustände ohne Text/Icon

## D/A/CH-Lokalisierung

- deutsches Datumsformat
- deutsches Preisformat
- keine US-Placeholders
- Validierungs- und Fehlermeldungen in sauberer Sprache
- Inhalte international, aber Formatlogik lokal korrekt

## UI-Regeln

1. max. drei CTA-Stile
2. Statusfarben konsistent
3. identische Formularlogik über Public und Portal
4. kein One-Off-UI
5. applicantseitig keine administrative Überfrachtung
6. Partner-Branding nur innerhalb definierter White-Label-Container

## Qualitätsregeln

1. keine abgeschnittenen Logos / inkonsistente Markennutzung
2. keine Preis- oder Kontaktinformationen als statische Grafik, wenn sie sich ändern können
3. keine unlesbaren Tabellen mobil
4. keine unklaren Badge-Farben ohne Text
5. keine dekorative Display-Schrift in langen UI-Texten
6. keine Bilder / Mockups mit faktisch unbestätigten Claims

## Konkrete Designempfehlungen aus den Quellen

### Applicant Portal
- Hero-Statuskarte oben
- offene Tasks prominent
- Dokumentstatus mit eindeutigen Badges
- Journey als Timeline / Stepper
- Learning Center als eigener Bereich
- Inbox im WhatsApp-ähnlichen Muster, aber ruhiger und strukturierter

### Public Website
- Ökosystem-Switchboard klar machen
- Studienkolleg / Sprachkurse / Unterkunft / Jobs / Uni als klare modulare Einstiege
- rechtliche und kommerzielle Angaben aus zentralem Config-Layer, nicht hart im Design verteilt
- FAQ und Prozessgrafiken als Trust-Inhalte nutzen

## Designentscheidungen mit Verifikationsstatus

### Verifiziert
- Blau-basierte Markenwelt,
- Arboria als funktionale Primärschrift,
- ruhige, professionelle Anmutung,
- klare Segment- und Kurskommunikation.

### Plausibel abgeleitet
- helles, vertrauensorientiertes Light Theme als Hauptmodus,
- dunkles Theme nur optional und nicht priorisiert,
- component-driven system mit gemeinsamem Public-/Portal-Fundament,
- Partner-Branding nur tokenbasiert, nicht per Sonderlayout.

### Offen / nicht verifizierbar
- finale Weblizenz- und Produktionsfähigkeit der Styleguide-Fonts,
- vollständige finale Brand-Hierarchie von WaytoGermany vs. Studienkolleg Aachen vs. W2G Academy,
- finale Preis- und Kontaktmodule im Design.
