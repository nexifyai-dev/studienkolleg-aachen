# Agentenrichtlinie (verbindlich)

Gültig ab: 2026-03-30

## Kernpflichten für alle AI-Agenten
- Keine relevante Code- oder Strukturänderung ohne dokumentierte Begründung.
- Jede relevante Architektur-/Workflow-/Rollen-/Provider-/Security-Entscheidung benötigt ADR.
- Jede relevante Änderung benötigt Changelog-Eintrag.
- README/Fachdoku müssen bei neuen oder geänderten Modulen aktualisiert werden.
- Tests/Validierung müssen ausgeführt und protokolliert werden.
- Datum, Kontext, Scope und Risiken müssen nachvollziehbar erfasst werden.
- Keine stillen Änderungen; keine unkommentierten Brüche.
- Keine Widersprüche zwischen Code, Dokumentation und Memory tolerieren.

## AI- und Screening-spezifisch
- Produktive KI über DeepSeek.
- Keine Finalentscheidung aus Uploads oder KI-Output ableiten.
- Trennung `completeness` / `formal_precheck` / `ai_recommendation` / `staff_decision` respektieren.

## Qualität
- Änderungen müssen für neue Entwickler/Agenten ohne implizites Wissen verständlich sein.
- Dokumentation muss auditierbar statt dekorativ sein.
