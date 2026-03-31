# Pull-Request Policy (verbindlich)

Diese Policy definiert **harte Merge-Kriterien**. Ein PR darf nur freigegeben werden, wenn alle Pflichtpunkte erfüllt sind.

## 1) Zwingende Merge-Kriterien

Ein PR ist nur mergebar, wenn:

1. **Tests grün**
   - Alle verpflichtenden CI-Jobs laufen erfolgreich.
   - Relevante gezielte Tests für geänderte Bereiche sind dokumentiert.
2. **Rollen-Impact bewertet**
   - Auswirkungen auf Public, Applicant, Staff, Admin, Partner sind explizit beschrieben.
   - Rollen-/Rechte-Regressionen sind ausgeschlossen oder klar als Risiko erfasst.
3. **Datenintegrität abgesichert**
   - Schema-, Migrations-, Validierungs- und Konsistenzauswirkungen sind geprüft.
   - Keine impliziten fachlichen Annahmen aus bloßem Dateiupload oder Dateivorhandensein.
4. **UX-Risiko bewertet**
   - Nutzerfluss, i18n-Texte, Zustände/Fehlermeldungen und „nächste Schritte“ sind geprüft.
   - Bei sichtbaren UI-Änderungen liegt visuelle Evidenz (Screenshot) vor.
5. **Release-Risiko bewertet**
   - Rollout-/Rollback-Plan und Betriebsrisiken sind dokumentiert.
   - Blocker/Kernmängel sind geschlossen.

## 2) Blocking-Regeln

Merge-Freigabe ist **verboten**, wenn einer der folgenden Punkte zutrifft:

- Pflichtfelder im PR-Template sind unvollständig.
- Offene Kernmängel wurden im PR markiert.
- CI-Status „PR Quality Gate“ oder „Node.js CI“ ist fehlgeschlagen.
- Erforderliche CODEOWNER-Reviews für kritische Pfade fehlen.

## 3) ADR-Pflicht

Eine ADR ist verpflichtend bei Änderungen an:

- **Architektur** (Systemgrenzen, Schnittstellen, Service-Splitting, zentrale Infrastrukturmuster)
- **Auth/Security** (Authentifizierung, Autorisierung, Session/Token-Handling, Sicherheitskontrollen)
- **Datenmodell** (Schema, Persistenzlogik, Konsistenzregeln, Datenflüsse)
- **AI-Entscheidungen** (Provider-Wahl, Prompt-/Risikostrategien, Screening-Entscheidungslogik)

Ohne ADR-Referenz (oder begründete ADR-Ausnahme im Template) keine Freigabe.

## 4) Definition „Kernmangel“

Kernmangel = Defekt mit hohem Business-/Compliance-/Security-Impact oder Gefahr von Datenverlust, Rollen-/Rechte-Fehlverhalten, Freigabe falscher fachlicher Entscheidungen.

Solange Kernmängel offen sind, bleibt der PR blockiert.
