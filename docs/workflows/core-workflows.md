# Workflow-Dokumentation

Stand: 2026-03-30

## 1) Bewerbungsflow
1. Bewerbung über Public-Formular.
2. Anlage/Befüllung von Applicant + Application.
3. Initiale Stage-Zuordnung im Funnel.
4. Staff übernimmt in Kanban/Detail.

## 2) Registrierung / Portalzugang
- Applicant registriert sich, authentifiziert per JWT-Cookies.
- Rollenabhängige Weiterleitung auf `/portal`, `/staff`, `/admin` oder `/partner`.

## 3) Dokumentenflow
- Applicant lädt Dokumente hoch.
- System verwaltet Dokumentmetadaten/Status.
- Staff prüft und ändert Dokumentstatus.
- Vollständigkeitsstatus beeinflusst Follow-up, nicht finale Zulassung.

## 4) Nachrichtenflow
- Thread-bezogene Kommunikation pro Bewerbung.
- Staff und Applicant kommunizieren bidirektional.
- Anhänge möglich; Verlauf bleibt nachvollziehbar.

## 5) Aufgabenflow
- Aufgaben werden erstellt, zugewiesen, priorisiert, terminiert.
- Notizen, Anhänge, Historie dokumentieren Bearbeitung.
- Kanban/Listen unterstützen operative Folgeaktionen.

## 6) Follow-up / Wiedervorlage
- Staff setzt Wiedervorlagen bei fehlenden Unterlagen/unklarer Lage.
- Wiedervorlagen sind Teil der operativen CRM-Steuerung.

## 7) Screening-/Prüfungslogik
- Stufe A: Vollständigkeit (`completeness`).
- Stufe B: formale Vorprüfung (`formal_precheck`).
- Stufe C: KI-Empfehlung (`ai_recommendation`).
- Stufe D: finale Staff-Entscheidung (`staff_decision`).

## 8) Staff-Entscheidungslogik
- KI darf nur Vorschläge liefern.
- Stage-Übernahme aus KI nur für erlaubte nicht-zulassungsfinale Stages.
- Staff bestätigt und verantwortet final.

## 9) Teacher-Zuweisung
- Nur zugewiesene Fälle, nur bei aktivem Consent.
- Kein Zugriff auf ausgeschlossene Datendomänen (z. B. interne Notizen/Finanzdaten).

## 10) Partner-Referral-Logik
- Referral-Link identifiziert Partner-Zuordnung.
- Partner sieht nur referral-relevante Daten.

## 11) Consent-/Datenschutzfluss
- Consent im Applicant-Portal verwaltbar.
- Consent-Änderungen beeinflussen Sichtbarkeit in Rollenmodellen.
