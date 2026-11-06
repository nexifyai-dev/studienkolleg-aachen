# 17_qa_release_und_abnahme.md

## QA-Plan

## Prüfkategorien
1. fachlich
2. visuell
3. funktional
4. responsiv
5. rollenbezogen
6. datenbezogen
7. rechtlich
8. lokalisierungsbezogen
9. accessibility-bezogen
10. sicherheitsbezogen
11. integrationsbezogen
12. performance-bezogen

## Breakpoints
- 1920
- 1440
- 1280
- 1024
- 820
- 768
- 480
- 430
- 390
- 375
- 360

## Release-Gates

### Gate A – Scope / Rollen / Datenquellen klar
- ERD final
- Rollenmatrix final
- RLS-Matrix final
- Legal/Commercial offene Punkte dokumentiert
- MVP-Scope schriftlich bestätigt

### Gate B – Kernflows implementiert
- Lead-Ingest
- Dublettenflow
- Applicant Login/Onboarding
- Dokumentenprozess
- Staff Kanban
- Rechnungsgrundlage
- Audit/Logs
- Public Core Pages

### Gate C – Volltest / Rechtslage / D/A/CH / Accessibility / Security
- RLS Tests grün
- Legal-Content konsistent
- Consent aktiv
- Accessibility-Basis erfüllt
- Monitoring/Alerts aktiv
- Performance im grünen Bereich

### Gate D – Release Candidate
- Staging-Fachabnahme
- keine kritischen Bugs
- Rollback dokumentiert
- offene Punkte nur nicht-blockierend

### Gate E – Produktivfreigabe
- manuelle finale Freigabe
- Deploy nach dokumentiertem Release-Prozess
- Smoke Tests in Produktion

## Abnahme-Logik

### Fachabnahme
Ein Kernprozess gilt nur dann als abgenommen, wenn der Fachbereich ihn im Staging vollständig durchspielen konnte:
- Leadanlage
- Aktivierung
- Dokumentenanforderung
- Dokumentenprüfung
- Rechnung
- Zahlung
- Statuswechsel
- Applicant-Kommunikation

### Sicherheitsabnahme
- keine unberechtigten Datenzugriffe
- keine öffentlichen Dokumente
- Audit-Events vorhanden
- Webhook-Signatur und Idempotenz geprüft

### Inhaltsabnahme
- Copy-Compiler erfüllt
- Claims scoped
- keine Platzhalter
- keine widersprüchlichen Preis-/Rechtsangaben

## Freigaben

| Bereich | Freigabe durch |
|---|---|
| Architektur | Technical Lead / Admin |
| Rollen/RLS | Security + Technical |
| Public Content | Content + Legal/Commercial |
| Payment | Finance + Legal + Technical |
| Applicant UX | Product/UX + Fachbereich |
| Release | Projektverantwortliche Freigabe |

## Testberichte

### Pflichtartefakte
1. Testfallliste
2. Ergebnisstatus je Prüffall:
   - erfüllt
   - teilweise erfüllt
   - nicht erfüllt
   - blockiert
3. Screenshots / Evidence
4. Bugliste
5. Abweichungen / Risiken
6. Freigabelog

## Rollback-Plan

1. Release-Tag und Changelog vorhanden
2. DB-Migrationen reversibel oder kompensierbar dokumentiert
3. Feature Flags für riskante UI-/Funktionsteile
4. Staging-Backup vorhanden
5. Incident Owner definiert
6. Rollback-Kommunikationsweg definiert

## Definition of Done

### Technisch
- lint grün
- typecheck grün
- tests grün
- build grün
- keine kritischen CVEs
- secrets sauber
- Performance ausreichend

### Inhaltlich
- Copy-Compiler vollständig
- Claims sauber scoped
- CTA klar
- Glossar konsistent
- Interne Verlinkung sauber

### Design
- nur Designsystem-Komponenten
- responsive geprüft
- barrierearme Basis erfüllt

### Tracking & Automationen
- relevante Events implementiert
- Trigger/Aktionen getestet
- Automation Logs sichtbar
- Dashboarddaten plausibel

### Governance
- Ziel, Risiko, KPI und Funnel-Zuordnung dokumentiert
- Reviewer-Freigabe vorhanden
- Audit-/Änderungsnachweis vorhanden
- Rollback dokumentiert

## Projektbezogene Zusatzkriterien

1. Legal- und Preiswidersprüche sind vor Public Release geschlossen.
2. Applicant darf niemals falsche Gewissheit über FSP/Uni-Zulassung bekommen.
3. Payment-Modul geht nicht live, bevor Steuer-/Refundlogik schriftlich geklärt ist.
4. Rechteprüfung wird nicht manuell „geglaubt“, sondern automatisiert getestet.
