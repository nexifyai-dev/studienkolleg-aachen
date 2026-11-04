# Studienkolleg Aachen · Website & Portale

Quellstand des klickbaren, statischen Frontendpiloten. Die Ansichten verwenden fiktive Daten und lokale Simulationen; es gibt keine angebundenen produktiven Bewerbungs-, Zahlungs-, Nachrichten- oder Verwaltungssysteme.

## Lokal starten

Benötigt werden Python 3 und Node.js. Es gibt keinen Paketinstallations- oder Buildschritt.

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Danach http://127.0.0.1:4173/ öffnen. Die Anwendung verwendet Hash-Routen. Änderungen im Arbeitsspeicher gehen beim Neuladen verloren.

## Prüfungen

```sh
for test in test-*.cjs; do node "$test" || exit 1; done
```

Die Tests prüfen den Piloten und ersetzen keine fachliche, Sicherheits-, Barrierefreiheits- oder Produktionsabnahme. Browser und native Zoomdarstellung sind gesondert zu prüfen.

## Orientierung

- `dist/`: auslieferbarer statischer Frontendstand und Original-Referenzassets.
- `CONCEPT.md`, `V2-ARCHITECTURE.md`, `V2-TRACEABILITY.json`: Konzept, Architektur und fachliche Rückverfolgbarkeit.
- `FRONTEND-PAGE-MATRIX.md` und `FRONTEND-PROGRESS.json`: Seitenstand und ausdrücklich begrenzte lokale Nachweise.
- `V3-HANDOFF.md`: Umsetzungsstand, Tests und offene Punkte.
- `PROJEKTQUELLEN.md`: identifizierte externe Originalquellen und Grenzen der Bestandsaufnahme.

Die Unterlagen enthalten auch ältere Quellen und Entwürfe. Datierungen, fachliche Freigaben und Quellrang sind vor produktiver Nutzung zu prüfen. Geheimnisse gehören nicht ins Repository.
