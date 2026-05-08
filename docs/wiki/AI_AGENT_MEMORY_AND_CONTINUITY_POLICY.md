# AI Agent Memory & Continuity Policy (Wiki)

**Fuehrende Datei:** [`docs/governance/agent_memory_and_writeback_policy.md`](../governance/agent_memory_and_writeback_policy.md)  
**Stand:** 2026-04-03

---

## Kurzfassung

### Vor jedem Lauf (Recall)
1. `memory/PRD.md` lesen → Was ist gebaut? Was ist offen?
2. `memory/FEHLERREGISTER.md` lesen → Bekannte Bugs und Muster
3. `memory/GO_LIVE_BLOCKERS.md` lesen → Was blockiert Produktion?
4. `memory/CHANGELOG.md` lesen → Letzte Aenderungen
5. Letzte Testberichte pruefen → Regressionen?
6. ADRs in `docs/adr/` pruefen → Architekturentscheidungen

### Nach jedem Lauf (Writeback)
- PRD aktualisieren (neue Features, erledigte Backlog-Items)
- CHANGELOG ergaenzen (was wurde geaendert)
- FEHLERREGISTER aktualisieren (neue/behobene Bugs)
- History-Eintrag erstellen (`docs/history/YYYY-MM-DD-<thema>.md`)
- Bei Architekturentscheidungen: ADR anlegen

### Memory-Kategorien
STATE, KNOWLEDGE, TODO, RISK, DECISION, RULE, SOURCE, LESSON, BLOCKER

### Verboten in jeder Doku-Datei
Passwoerter, API-Keys, Tokens, Session-Cookies, personenbezogene Echtdaten.
Ausnahme: `test_credentials.md` fuer Preview-Umgebung.

---

## Sync-Regeln

| Fuehrend | Abgeleitet |
|----------|------------|
| `memory/PRD.md` | Wiki-Zusammenfassungen |
| `docs/adr/ADR-NNN-*.md` | Wiki-Verweise |
| `memory/GO_LIVE_BLOCKERS.md` | Deployment-Doku |

Bei Widerspruch gilt die fuehrende Datei.

---

## Betreiber- und Agentenlogik

| Rolle | Verantwortung |
|-------|---------------|
| **Projektleitung (Mensch)** | Architekturentscheidungen freigeben, Blocker klaeren, Go-Live-Entscheidung |
| **AI-Agent** | Recall ausfuehren, Code implementieren, testen, Writeback durchfuehren, Handover liefern |
| **Naechster Agent** | Recall ausfuehren, offene Items fortfuehren, keine Wiederholung abgeschlossener Arbeit |

---

## Definition of Done

Ein Lauf ist ERLEDIGT, wenn:
1. Deliverables erstellt/vervollstaendigt
2. Code kompiliert und startet
3. Getestet (min. Smoke-Test)
4. Memory-Dateien aktualisiert
5. History-Eintrag erstellt
6. Offene Punkte als OFFEN markiert
7. Keine Secrets in Dateien
8. Naechster Block benannt

---

*Fuer die vollstaendige Policy siehe die [fuehrende Governance-Datei](../governance/agent_memory_and_writeback_policy.md).*
