# Changelog

Alle relevanten Änderungen werden hier nachvollziehbar dokumentiert.

## [2026-03-30] Dokumentationsbaseline v1
### Geändert
- README vollständig auf projektbezogene Betriebsdokumentation umgestellt.
- Verbindliche `docs/`-Informationsarchitektur mit fachlichen Source-of-Truth-Dateien eingeführt.
- ADR-System mit Template und initialen Kernentscheidungen eingeführt.
- Richtlinien für Contributors und Agenten (`CONTRIBUTING.md`, `AGENTS.md`, Dokumentationspolicy) verankert.

### Warum
- Vorlaufstatus war dokumentarisch fragmentiert und für Audit/Übergabe nicht ausreichend.
- Projekt benötigt konsistente, versionierte und belastbare Entscheidungs- und Betriebsdokumentation.

### Betroffene Bereiche
- Repo-Governance, Onboarding, Architekturtransparenz, Änderungsnachvollziehbarkeit.

### Risiken / Auswirkungen
- Zusätzlicher Pflegeaufwand pro Änderung (bewusst akzeptiert zugunsten Auditfähigkeit).
- Bestehende Legacy-Dokumente im Repo-Root müssen bei Konflikten aktiv abgeglichen werden.

### Migration / Nacharbeiten
- Bei jeder neuen Grundsatzentscheidung ADR fortführen.
- Go-Live-Blocker aus Memory laufend mit Operations-Doku synchron halten.
