# Design-Normen und Vorgaben – W2G Platform

## 1. Hero-Bild-Positionierung

### Drittel-Regel (Rule of Thirds)
- Hero in 3x3 Raster teilen
- Fokus-Element (Gesicht/Person) auf oberen rechten Schnittpunkt
- NICHT in der unteren Ecke – das wirkt unprofessionell

### Goldener Schnitt (1:1.618)
- Content-Bereich zu Bild-Bereich: ca. 7:5 Spalten (58%:42%)
- Bildbreite Desktop: min. 500px, empfohlen 40-50% des Containers
- Bildhöhe: 60-80% der Hero-Sektion (visuell dominant)

### Visual Weight Balance (ISO 9241, asymmetrisch)
- Große Headline links muss durch großes Bild rechts ausbalanciert werden
- Bild muss visuell GLEICHWERTIG sein, nicht untergeordnet
- Person vertikal ZENTRIERT, Gesicht auf oberer Drittellinie

## 2. Hero-Sektion Proportionen

| Eigenschaft | Desktop | Tablet | Mobile |
|---|---|---|---|
| Min-Height | 90vh / 720px | 600px | 560px |
| Bild-Breite | 480-560px (40-45% Container) | 360-420px | 280-340px |
| Grid-Split | 7/5 oder 8/4 Spalten | Full-width stacked | Full-width stacked |
| Padding Top | 120-160px (inkl. Nav) | 96-120px | 80-96px |
| Person vertikal | Zentriert (items-center) | Zentriert | Unter dem Text |

## 3. Bildgröße und Viewport

| Bild-Typ | Desktop (WxH) | Aspect Ratio | Max Dateigröße |
|---|---|---|---|
| Hero Hintergrund | 1920x1080 | 16:9 | <300KB |
| Hero Person/Grafik | 560x720+ | Ca. 3:4 | <200KB |
| Karten-Bilder | 800x500 | 16:10 | <100KB |

## 4. Spacing-Tokens (8px Basis-Grid)

| Token | Wert |
|---|---|
| --space-1 | 4px |
| --space-2 | 8px |
| --space-3 | 12px |
| --space-4 | 16px |
| --space-6 | 24px |
| --space-8 | 32px |
| --space-12 | 48px |
| --space-16 | 64px |
| --space-24 | 96px |
| --space-32 | 128px |

## 5. Section-zu-Section Abstände

| Kontext | Desktop | Tablet | Mobile |
|---|---|---|---|
| Section-Abstand | 96px | 72px | 56px |
| Label → Headline | 16px | 16px | 12px |
| Headline → Intro | 20-24px | 20px | 16px |
| Intro → Content | 32-40px | 32px | 24px |
| Grid Gap (groß) | 32px | 24px | 16px |
| Card Padding | 32px | 24px | 20px |

## 6. Typografie-Skala

| Element | Desktop | Tablet | Mobile | Line-Height |
|---|---|---|---|---|
| H1 | 56px | 44px | 36px | 1.08 |
| H2 | 40-48px | 32-36px | 28-32px | 1.1 |
| H3 | 28px | 24px | 20px | 1.2 |
| Body Large | 18px | 16px | 16px | 1.7 |
| Body Standard | 16px | 15px | 14px | 1.7 |
| Small/Meta | 13-14px | 12-13px | 12px | 1.5 |
| Overline | 11px | 11px | 10px | 1.4 |

## 7. Button-System

| Typ | Höhe | Min-Breite | Radius |
|---|---|---|---|
| Primary (CTA) | 56px | 160px | 4px |
| Secondary | 48px | 140px | 4px |
| Utility | 40px | 120px | 4px |

## 8. Quellen
- ISO 9241-110 (Dialogprinzipien)
- ISO 9241-161 (Visuelle Elemente)
- Nielsen Norman Group: Golden Ratio in UI Design
- Interaction Design Foundation: Rule of Thirds
- German DIN EN ISO 9241 Standards
