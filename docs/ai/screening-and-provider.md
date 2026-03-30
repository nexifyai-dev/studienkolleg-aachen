# AI- und Screening-Dokumentation

Stand: 2026-03-30

## Aktueller Provider
- **Produktiv-Provider:** DeepSeek (`services/deepseek_provider.py`).
- Aktivierung über `DEEPSEEK_API_KEY`.

## Provider-Wechselhistorie
- Historisch: nscale/NSCall.
- Aktuell: nscale nur als Legacy-Kompatibilitäts-Shim (`services/nscale_provider.py`) auf DeepSeek-Calls.
- Neue produktive Integrationen auf nscale/NSCALE_API_KEY sind untersagt.

## Fachlicher Zweck der KI
- KI unterstützt Staff bei Vorprüfung und Priorisierung.
- KI ersetzt keine fachlich/rechtlich finale Entscheidungsinstanz.

## Was KI prüft
- Strukturierte Voranalyse von Bewerberdaten, Dokumentstatus, Verlauf.
- Kurs-/Stage-Empfehlung als Entscheidungshilfe.

## Was KI nicht final entscheidet
- Keine Zulassungs- oder Ablehnungsendentscheidung.
- Keine automatische Faktenableitung nur aus Datei-Existenz.

## Prüfungsaufbau (verbindlich)
1. `completeness`
2. `formal_precheck`
3. `ai_recommendation`
4. `staff_decision`

## Kriterien, Regelmatrix, Evidenzlogik
- Lokale Rule-Matrix für Mindestdokumente, CEFR, Herkunfts-Kategorien.
- Evidenzquellen markiert (`application_form`, `uploaded_document_metadata`, `local_rulebook_v1`).
- Offene Punkte und Risiken müssen explizit ausgegeben werden.

## Daten-/Referenzbasis und Grenzen
- Local rulebook, keine Live-Anabin-Verifikation im Lauf.
- Ergebnis ist Vorprüfungshinweis, nicht behördliche Anerkennungsentscheidung.

## Auditierbarkeit
- Screening-Ergebnisse in `ai_screenings` gespeichert.
- Auslösung und Übernahmeaktionen als Audit-Events protokolliert.

## Risiken / offene Punkte
- Qualität hängt von Eingabedaten und Rulebook-Abdeckung ab.
- Live-Referenzanbindung (z. B. externe Datenbanken) derzeit nicht aktiv.
- Staff-Schulung zur korrekten Interpretation bleibt notwendig.
