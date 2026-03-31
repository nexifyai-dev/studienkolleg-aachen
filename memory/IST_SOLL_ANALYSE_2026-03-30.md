# IST-/SOLL-Analyse (Stand: 30.03.2026)

## 1) IST-Zustand (vor Umsetzung)

### Architektur / Routing
- Rollenbasierte Routing-Welten (`Public`, `Applicant`, `Staff`, `Admin`, `Partner`) sind in `frontend/src/App.js` sauber getrennt.
- Keine Parallelwelt notwendig; bestehende Struktur ist tragfähig.

### CRM-/Operations-Reife
- Staff-Aufgabenmodul ist bereits CRM-nah: Detailansicht, Notizen, Anhänge, Verlauf, Suche, Filter, Bulk-Status.
- Admin-Bereich war funktional, aber UX-seitig nicht vollständig konsistent mit Staff/Applicant (u. a. eigenes Navigationsmuster).
- Nutzerverwaltung hatte Suche/Filter, aber keine systemische Bulk-Aktivierung für sichere Massenpflege.

### KI-Screening / Compliance
- Produktive KI-Pfade laufen bereits über DeepSeek (`services/deepseek_provider`, `services/ai_screening`).
- Trennung von Vollständigkeit, formaler Vorprüfung, KI-Empfehlung und Staff-Entscheidung ist in `screening_rules.py` + `ai_screening.py` bereits modelliert.
- Offener Stabilitätspunkt: Legacy-Referenzen in Doku/Test-Artefakten vorhanden, nicht im produktiven Inferenzpfad.

## 2) SOLL-Zustand (produktionsbereit)

### UX-Konsistenz (Admin ↔ Staff)
- Admin erhält gleiche Navigationslogik wie Staff (Topbar, aktive States, mobile Navigation).
- Einheitliches visuelles CRM-Muster: ruhiges Weiß + CI-Blau, konsistente Interaktionsmuster.

### Operative Admin-Nutzerpflege
- Bulk-Aktivieren/Deaktivieren für selektierte Nutzer, inkl. Sicherheitsleitplanken:
  - kein Selbst-Deaktivieren über Batch,
  - keine Superadmin-Massenänderung.
- In UI: Selektion sichtbarer Nutzer + Bulk-Quick-Actions.

### Governance / Nachvollziehbarkeit
- Jede Batch-Änderung erzeugt Audit-Events pro betroffenen Nutzer.
- Ergebnisobjekt liefert transparent: `requested`, `updated`, `skipped_superadmin`, `skipped_self`.

## 3) Umsetzungsergebnis
- SOLL-Zustand für oben priorisierte Blocker/Gap-Bereiche wurde implementiert.
- Keine Änderung an Rollen-/Rechte-Basisrouting; kein Regressionspfad auf Portaleintritt.
- KI-Entscheidungsgrenzen bleiben unverändert strikt nicht-faktisch (Vorprüfung + Staff-Entscheidung).

## 4) Verbleibende Restpunkte
- Historische Artefakte mit nscale-Begriffen in `memory/` und `test_reports/` sind weiterhin vorhanden (nicht produktiv wirksam), sollten aber in einem separaten Content-Hardening-Schritt bereinigt werden.
- Ein vollständiger E2E-GO-Live-Lauf (inkl. reale Backend-Umgebungsvariablen + Live-Datenflüsse) ist außerhalb dieser lokalen Änderung weiterhin erforderlich.
