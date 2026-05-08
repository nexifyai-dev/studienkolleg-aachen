# ADR-002: Typografie – Arboria mit DM Sans Fallback

**Status:** AKZEPTIERT  
**Datum:** 2026-04-03  
**Entscheider:** Projektleitung  
**Kategorie:** DECISION

---

## Kontext

Die Projekt-Source-of-Truth definiert:
- **Arboria** fuer Headings, Branding, Navigation
- **Inter** fuer Body, UI, Labels, Formulare

Arboria ist eine lizenzpflichtige Schrift (Omnibus-Type), verfuegbar ueber Adobe Fonts (Typekit) oder Direktlizenz. Die Plattform verfuegt aktuell ueber keine Arboria-Lizenz.

## Entscheidung

1. CSS-Variable `--font-heading` wird auf `'Arboria', 'DM Sans', 'Inter', system-ui, sans-serif` gesetzt
2. DM Sans (Google Fonts, kostenlos) dient als visuell aehnlicher Fallback bis Arboria verfuegbar ist
3. Sobald Arboria-Webfont-Dateien (.woff2) bereitgestellt werden, koennen sie via `@font-face` in `index.css` geladen werden

## Aktion erforderlich

Fuer Arboria-Aktivierung:
1. Arboria-Lizenz beschaffen (Adobe Fonts oder Direktkauf)
2. .woff2-Dateien in `/app/frontend/public/fonts/` ablegen
3. `@font-face`-Deklaration in `index.css` ergaenzen
4. DM Sans-Fallback bleibt als Sicherheitsnetz bestehen

## Konsequenzen

- Headings rendern aktuell in DM Sans (visuell aehnlich: geometrisch, modern, klar)
- Kein funktionaler Unterschied, nur typografische Nuance
- Bei Arboria-Aktivierung aendert sich das Schriftbild automatisch durch CSS-Kaskade
