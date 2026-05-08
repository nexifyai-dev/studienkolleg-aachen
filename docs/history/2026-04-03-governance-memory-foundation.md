# History: Governance & Memory Foundation

**Datum:** 2026-04-03  
**Typ:** Strukturelle Ergaenzung (Dokumentation)  
**Ausloeser:** Audit-Feststellung fehlender Governance-Dokumente; 15-Punkte-Betriebsregeln durch Projektleitung vorgegeben.

---

## Was wurde strukturell ergaenzt

### Neue Dateien

| Datei | Zweck |
|-------|-------|
| `docs/governance/agent_memory_and_writeback_policy.md` | Verbindliche Regeln fuer Recall, Writeback, Memory-Kategorien, Handover und Definition of Done |
| `docs/adr/ADR-001-mongodb-fastapi-statt-supabase-nextjs.md` | Architekturentscheidungs-Record: Dokumentation der Abweichung von der Soll-Architektur (Supabase/Next.js) zur Ist-Architektur (MongoDB/FastAPI/React) |
| `docs/qa-release/DEPLOYMENT.md` | Deployment-Dokumentation mit ENV-Gruppen, Start-Reihenfolge, Health-Checks, Smoke-Tests und Rollback-Strategie |
| `docs/qa-release/RUNBOOK.md` | Operatives Runbook mit Incident-Triage, typischen Fehlerbildern, Pruefschritten und Eskalationslogik |
| `docs/wiki/AI_AGENT_MEMORY_AND_CONTINUITY_POLICY.md` | Wiki-taugliche Kurzfassung der Governance-Regeln |
| `docs/history/2026-04-03-governance-memory-foundation.md` | Dieser Eintrag |

### Aktualisierte Dateien

| Datei | Aenderung |
|-------|-----------|
| `README.md` | Von Einzeiler auf vollstaendige Projektbeschreibung erweitert |
| `memory/CHANGELOG.md` | Governance-Block dokumentiert |
| `memory/FEHLERREGISTER.md` | Neue Doku-Luecken als behoben dokumentiert |
| `memory/GO_LIVE_BLOCKERS.md` | Governance-Status aktualisiert |

---

## Warum es notwendig war

1. **Audit-Feststellung:** Fehlender ADR zur Architekturabweichung, fehlendes DEPLOYMENT.md, fehlendes RUNBOOK.md
2. **Projektregeln:** Die 15-Punkte-Betriebsregeln fordern explizit: Recall vor jedem Lauf, Writeback nach jedem Lauf, ADR-Pflicht, History-Pflicht, Wiki-Sync
3. **Kontinuitaetssicherung:** Ohne dokumentierte Memory-Policy verlieren Agentenlaeufe Kontext und wiederholen Fehler
4. **Betriebssicherheit:** Ohne Runbook und Deployment-Doku ist der Betrieb bei Incidents auf Einzelwissen angewiesen

---

## Welche Luecken damit geschlossen werden

- [GESCHLOSSEN] Fehlender ADR zur Architekturabweichung
- [GESCHLOSSEN] Fehlendes DEPLOYMENT.md
- [GESCHLOSSEN] Fehlendes RUNBOOK.md
- [GESCHLOSSEN] Fehlende Memory-/Writeback-Policy
- [GESCHLOSSEN] README.md nur Einzeiler
- [GESCHLOSSEN] Keine Wiki-Spiegelung

---

## Welche Luecken bewusst offen bleiben

| Luecke | Begruendung | Prioritaet |
|--------|-------------|------------|
| Automatische Mem0-API-Integration | Erfordert MEM0_API_KEY und externe Service-Anbindung; aktuell durch dateibasiertes Memory-System abgedeckt | P2 |
| CI/CD-Pipeline-Integration | Deployment-Plattform noch nicht stabil; Pipeline-Definition nach erfolgreicher Erstbereitstellung | P1 |
| Monitoring/Alerting (Sentry etc.) | Externe Service-Anbindung erfordert Account-Setup | P1 |
| MongoDB-Backup-Automatisierung | Abhaengig von Infra-Entscheidung (managed vs. self-hosted) | P0 |

---

## Naechster Umsetzungsblock

**Re-Screening bei Dokument-Upload (Delta-Logik)** (P1)
- Automatisches Neu-Screening, wenn Bewerber ein neues Dokument hochlaedt
- Delta-Analyse: Nur geaenderte/neue Informationen bewerten
- Ergebnis mit vorherigem Screening vergleichen und Aenderungen hervorheben
