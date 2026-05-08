# Agent Memory & Writeback Policy
## Studienkolleg Aachen / Way2Germany / W2G Academy

**Version:** 1.0  
**Datum:** 2026-04-03  
**Status:** VERBINDLICH  
**Geltungsbereich:** Alle AI-Agenten-Laeufe und menschlichen Entwicklungszyklen auf diesem Repository.

---

## 1. Pflicht-Recall vor jedem Lauf

Jeder Agentenlauf MUSS vor dem ersten Code- oder Doku-Eingriff folgende Quellen pruefen:

| Quelle | Pfad | Zweck |
|--------|------|-------|
| PRD | `/app/memory/PRD.md` | Produktanforderungen, abgeschlossene Features, Backlog |
| CHANGELOG | `/app/memory/CHANGELOG.md` | Chronologie aller Aenderungen |
| FEHLERREGISTER | `/app/memory/FEHLERREGISTER.md` | Bekannte Fehler, wiederkehrende Muster |
| GO_LIVE_BLOCKERS | `/app/memory/GO_LIVE_BLOCKERS.md` | Produktionsblocker mit Status |
| Test-Credentials | `/app/memory/test_credentials.md` | Zugangsdaten fuer Testlaeufe |
| ROLES_MATRIX | `/app/memory/ROLES_MATRIX.md` | Rollenmodell und Berechtigungen |
| ADR-Verzeichnis | `/app/docs/adr/` | Architekturentscheidungen |
| History | `/app/docs/history/` | Chronologische Aenderungshistorie |
| Letzter Testbericht | `/app/test_reports/iteration_*.json` | Regressionspruefung |

**Reihenfolge:** PRD → FEHLERREGISTER → GO_LIVE_BLOCKERS → CHANGELOG → letzte Testberichte → ADRs

---

## 2. Pflicht-Writeback nach jedem Lauf

Nach jedem Lauf mit substanziellen Aenderungen MUSS der Agent folgende Dateien aktualisieren:

| Datei | Wann aktualisieren |
|-------|--------------------|
| `memory/PRD.md` | Neues Feature implementiert, Backlog-Item erledigt |
| `memory/CHANGELOG.md` | Jede funktionale Aenderung (append-only, neuester Eintrag oben) |
| `memory/FEHLERREGISTER.md` | Bug gefunden oder behoben |
| `memory/GO_LIVE_BLOCKERS.md` | Blocker geloest oder neuer Blocker entdeckt |
| `memory/test_credentials.md` | Zugangsdaten erstellt oder geaendert |
| `docs/history/YYYY-MM-DD-<thema>.md` | Bei jedem abgeschlossenen Arbeitsblock |
| `docs/adr/ADR-NNN-<titel>.md` | Bei jeder Architekturentscheidung mit Tragweite |

---

## 3. Memory-Kategorien

Jede persistierte Information MUSS einer der folgenden Kategorien zugeordnet werden:

| Kategorie | Beschreibung | Beispiel |
|-----------|-------------|---------|
| **STATE** | Aktueller Systemzustand | "Backend laeuft auf FastAPI 0.104, MongoDB 7.x" |
| **KNOWLEDGE** | Verifiziertes Fachwissen | "Anabin H+ bedeutet volle Anerkennung" |
| **TODO** | Offene Aufgabe | "Re-Screening Delta-Logik implementieren" |
| **RISK** | Identifiziertes Risiko | "Git-History enthaelt noch alte Credentials" |
| **DECISION** | Getroffene Entscheidung | "MongoDB statt PostgreSQL wegen Deployment-Constraints" |
| **RULE** | Verbindliche Projektregeln | "Keine Secrets in Memory-Dateien" |
| **SOURCE** | Referenzquelle | "Gesamtkonzept_2026.docx → extrahiert in /app/01-20_*.md" |
| **LESSON** | Gelernte Lektion | "Agent-Fertigmeldung ohne Screenshot fuehrt zu Fehlern" |
| **BLOCKER** | Aktiver Blocker | "Emergent-Deployment: Registry-Fehler, Code-seitig bereit" |

---

## 4. Verbotene Inhalte

Folgende Inhalte duerfen NIEMALS in Memory-, Wiki-, ADR-, History- oder sonstige Repo-Dateien geschrieben werden:

- Passwoerter (auch keine Seed-/Test-Passwoerter in Klartext ausserhalb von `test_credentials.md`)
- API-Keys, Tokens, Session-Cookies
- Private Keys, Zertifikate
- Datenbank-Connection-Strings mit Credentials
- Personenbezogene Echtdaten von Bewerbern
- Interne Strato/IMAP-Zugangsdaten

**Ausnahme:** `/app/memory/test_credentials.md` darf Test-Zugangsdaten fuer die Preview-Umgebung enthalten, da diese keine Produktionsdaten sind und der Testbetrieb dies erfordert.

**Regel:** Wenn auf Credentials verwiesen werden muss, wird nur der ENV-Variablenname genannt (z.B. "NSCALE_API_KEY muss gesetzt sein"), niemals der Wert.

---

## 5. Repo-/Wiki-/ADR-/History-Sync

### Sync-Hierarchie

```
Fuehrend (Source of Truth):
  /app/memory/PRD.md              → Produktstatus
  /app/memory/GO_LIVE_BLOCKERS.md → Produktionsblocker
  /app/docs/adr/ADR-NNN-*.md     → Architekturentscheidungen

Abgeleitet (muss synchron gehalten werden):
  /app/docs/wiki/*.md             → Wiki-taugliche Zusammenfassungen
  /app/docs/history/*.md          → Chronologische Eintraege
  /app/memory/CHANGELOG.md        → Feature-Chronologie
```

### Sync-Regeln

1. Aenderungen an fuehrenden Dateien MUESSEN in abgeleiteten Dateien gespiegelt werden.
2. Abgeleitete Dateien duerfen keine Informationen enthalten, die der fuehrenden Datei widersprechen.
3. Bei Widerspruch gilt die fuehrende Datei.
4. Wiki-Dateien sind Kurzfassungen; fuer Volltext wird auf die fuehrende Datei verwiesen.

---

## 6. Fluechtiges vs. persistiertes Wissen

| Typ | Persistieren? | Beispiel |
|-----|:---:|---------|
| Architekturentscheidung | JA → ADR | "Wechsel von Resend zu SMTP-Direkt" |
| Neues Feature | JA → CHANGELOG + PRD | "PDF-Export implementiert" |
| Bug-Fix | JA → FEHLERREGISTER + CHANGELOG | "ObjectId-Serialisierung in API gefixt" |
| Debugging-Schritte | NEIN | "curl -X POST getestet, 500 erhalten" |
| Temporaere Workarounds | JA → FEHLERREGISTER (als offen) | "CORS auf Wildcard wegen Preview" |
| Testlauf-Ergebnisse | JA → test_reports/ | "iteration_37.json: 100% pass" |
| Planueberlegungen | NEIN | "Koennte React Query nutzen statt fetch" |

---

## 7. Handover-Mindeststruktur

Jeder Agentenlauf, der an einen Folgeagenten uebergeben wird, MUSS folgende Informationen liefern:

1. **Letzter Arbeitsgegenstand** mit Status (ERLEDIGT / IN ARBEIT / BLOCKIERT)
2. **Offene Issues** mit Prioritaet und Debug-Hinweisen
3. **Geaenderte Dateien** (Liste)
4. **Teststand** (letzter Testbericht, offene Regressionen)
5. **Naechster empfohlener Arbeitsblock**
6. **Bekannte Risiken und Blocker**
7. **Credentials-Status** (welche ENV-Variablen gesetzt sein muessen)

---

## 8. Definition of Done fuer agentische Laeufe

Ein Arbeitsblock gilt als ERLEDIGT, wenn:

1. Alle Deliverables erstellt oder substanziell vervollstaendigt sind
2. Code kompiliert und Backend/Frontend starten fehlerfrei
3. Aenderungen getestet sind (mindestens Smoke-Test, bei Feature-Arbeit Testing Agent)
4. Memory-Dateien aktualisiert sind (Writeback)
5. History-Eintrag fuer den Arbeitsblock erstellt ist
6. Offene Punkte explizit als OFFEN markiert sind
7. Keine Secrets in neuen oder geaenderten Dateien enthalten sind
8. Der naechste Arbeitsblock benannt ist
