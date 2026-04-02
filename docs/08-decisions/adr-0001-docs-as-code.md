# ADR-0001: Docs-as-code als Dokumentationsmodell

## Status

Accepted

## Kontext

Das Repository enthält bereits relevantes Projektwissen, aber bislang verteilt und uneinheitlich:

- technische Wahrheit im Code
- Produkt- und Zustandswissen in `memory/`
- kaum versionierte Einstiegspunkte für Architektur, Rollen, Datenmodell und Betrieb

Bei wachsender Repo-Komplexität führt ein externes oder lose gepflegtes Wiki schnell zu Wissensdrift.

## Entscheidung

Die primäre Projektdokumentation wird im Repository unter `docs/` gepflegt.

Das bedeutet:

- Dokumentation ist versioniert
- Doku kann zusammen mit Code in Pull Requests überprüft werden
- Architektur-, Rollen-, Datenmodell- und Operationswissen bleibt nah an der Implementierung
- weitere Formate wie GitHub Wiki oder statische Dokumentationsseiten sind nur nachgelagerte Darstellungen, nicht die primäre Quelle

## Begründung

### Vorteile

1. **Nähe zum Code**
Änderungen an Architektur, Env, Rollen oder Workflows können direkt mit der Dokumentation zusammen verändert werden.

2. **Reviewbarkeit**
Doku-Änderungen laufen durch denselben PR-Prozess wie Code.

3. **Historie**
Entscheidungen und Systemzustände bleiben commit- und diff-bar.

4. **Geringere Wissensdrift**
Es gibt weniger Risiko, dass ein separates Wiki veraltet.

5. **Bessere Onboarding-Fähigkeit**
Neue Mitwirkende finden Systemwissen direkt im Repo.

## Nachteile

1. Dokumentation erfordert aktive Disziplin im Entwicklungsprozess.
2. Ohne klare Pflege-Regeln kann auch Repo-Dokumentation veralten.
3. Nicht-technische Stakeholder bevorzugen unter Umständen ein aufbereitetes Frontend für Dokumentation.

## Konsequenzen

### Sofort
- `docs/` wird als kanonische Doku-Struktur eingeführt.
- Kernseiten für Architektur, Rollen, Datenmodell, Operations und Pflege werden im Repo angelegt.

### Künftig
- PRs mit strukturellen Änderungen müssen relevante Docs mitprüfen.
- `memory/`-Inhalte werden schrittweise in `docs/` überführt.
- Weitere ADRs dokumentieren wichtige Architekturentscheidungen.

## Nicht entschieden

Diese ADR entscheidet nicht darüber,

- welches statische Doku-Frontend später genutzt wird
- ob zusätzlich ein GitHub Wiki oder MkDocs-Spiegel gebaut wird
- wie tief API-Referenzseiten automatisiert erzeugt werden

## Folgearbeiten

- weitere Detailseiten für Backend-Domänen ergänzen
- PR-Checklisten um Doku-Prüfung erweitern
- `memory/PRD.md` und `memory/GO_LIVE_BLOCKERS.md` schrittweise auf `docs/` verweisen oder migrieren
