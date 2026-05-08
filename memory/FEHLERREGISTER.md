# Fehlerregister – W2G Platform

## Behobene Fehler

### Block 14 (2026-03-31)
- **TEST_-Artefakte in DB**: 2 TEST_-Nachrichten und 6 leere Konversationen entfernt
- **Fallakte-KPIs mit Bindestrichen**: Bindestriche durch "Offen"/"k.A." ersetzt
- **Empty States ohne CTA**: Aufgaben, Rechnungen, Screening, Wiedervorlagen, Dokumente erhalten echte CTAs
- **Messaging nur 2-Spalten**: Auf 3-Spalten mit Kontextpanel erweitert
- **Omnichannel-Behauptung**: Ehrlich als Portal=Aktiv, E-Mail=Vorbereitet, WhatsApp=Nur Link klassifiziert
- **Fehlende interne Notizen**: Visibility-System mit internal/public implementiert
- **Konversations-Status fehlt**: open/answered/escalated/closed hinzugefuegt

### Block 13 (2026-03-31)
- **Dokumente nicht aufrufbar**: Download/Oeffnen-Links mit has_binary-Pruefung hinzugefuegt

### Block 12 (2026-03-31)
- **Suchleiste ueberlappt Filter-Pills**: Wrapper-Breiten standardisiert
- **Hover-Kontrast auf Services**: Feature-Cards gefixt

### Wiederkehrende Muster
- Agent fragt nach Bestaetigung statt autonom zu arbeiten (4x aufgetreten, behoben)
- Falsche "Fertig"-Claims ohne Preview-Verifikation (behoben durch Pflicht-Screenshots + Testing Agent)

### Governance-Foundation (2026-04-03)
- **Fehlender ADR zur Architekturabweichung**: ADR-001 angelegt (MongoDB/FastAPI statt Supabase/Next.js)
- **Fehlendes DEPLOYMENT.md**: Deployment-Doku mit ENV-Gruppen, Health-Checks und Rollback erstellt
- **Fehlendes RUNBOOK.md**: Operatives Runbook mit Incident-Triage und Fehlerbildern erstellt
- **Fehlende Memory-/Writeback-Policy**: Governance-Datei mit Recall-, Writeback- und Sync-Regeln erstellt
- **README.md nur Einzeiler**: Vollstaendige Projektbeschreibung mit Struktur und Links erstellt

## Offene Punkte
- IMAP/SMTP nicht produktiv angebunden (architektonisch vorbereitet)
- WhatsApp keine bidirektionale Integration (nur wa.me-Link)
- Lehrer-Zuweisung in Fallakte: nur anzeigen wenn fachlich erforderlich
