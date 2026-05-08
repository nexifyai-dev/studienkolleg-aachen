# W2G Platform – Prioritaetenplan & Risk-Analyse

**Stand:** 2026-04-06

---

## P0 – Go-Live-kritisch

### 1. DB-Performance-Indizes (LOW RISK, HIGH IMPACT)
**Dateien:** `database.py`
**Aufwand:** 30min
**Test:** `db.command('listIndexes', ...)` + Query-Timing

Fehlende Indizes:
- `messages`: (conversation_id, sent_at)
- `conversations`: (participants, last_message_at)
- `documents`: (application_id, status)
- `applications`: (applicant_id), (current_stage, workspace_id)
- `tasks`: (application_id, status), (assigned_to, status)
- `invoices`: (applicant_id, status)
- `audit_logs`: (entity_id, action)

### 2. Bewerbernummer (applicant_number) (MED RISK, HIGH IMPACT)
**Dateien:** `routers/applications.py`, `routers/invoices.py`, Frontend
**Aufwand:** 2-3h
**Test:** curl Create App → Check Number, Frontend Screenshot

Format: `STK-JJJJ-NNNN` (z.B. STK-2026-0001)
- Einfuegen in `create_application()` + Lead-Ingest
- Anzeige in Fallakte, Fallliste, Rechnungen, Portal

### 3. Bewerbungsprozess Fehler (HIGH RISK)
**Dateien:** `routers/leads.py`, `pages/public/ApplyPage.js`
**Aufwand:** 1-2h (Debugging)
**Test:** Testing Agent: Apply-Flow E2E

- Reproduktion: ApplyPage → Submit → Error
- Root-Cause-Analyse: S3, File-Size, Timeout, Validation

### 4. Dokumenten-Upload Bewerber (MED RISK)
**Dateien:** `pages/portal/DocumentsPage.js`, `routers/documents.py`
**Aufwand:** 2h
**Test:** Testing Agent: Upload → View → Delete → Replace

- Bewerber-Upload-Flow pruefen
- Delete + Replace UI hinzufuegen
- In-Portal-Vorschau sicherstellen

### 5. i18n Komplett-Rollout (LOW RISK, HIGH EFFORT)
**Dateien:** 15+ Frontend-Seiten, 2 JSON-Dateien
**Aufwand:** 4-6h
**Test:** Screenshot DE vs EN Toggle

Betroffene Seiten (hardcodierte DE-Strings):
- StaffDashboard.js
- ApplicantDetailPage.js (937 Zeilen!)
- StaffTasksPage.js
- StaffInvoicesPage.js
- StaffMessagingPage.js
- StaffDocumentsReviewPage.js
- StaffCasesPage.js
- KanbanPage.js
- AdminDashboard.js
- Alle Portal-Seiten

### 6. Rechnungs-PDF i18n (LOW RISK)
**Dateien:** `routers/invoices.py` (Zeile 252-582)
**Aufwand:** 1-2h
**Test:** curl Download PDF EN vs DE

### 7. AuthContext Loading-Timeout (LOW RISK)
**Dateien:** `contexts/AuthContext.js`
**Aufwand:** 30min
**Test:** Manuell: Cookie loeschen → Seite laden → kein Haengen

---

## P1 – Betriebsrelevant

### 8. Aufgaben-Erweiterung
- Filter nach Name/Bewerber/Mitarbeiter
- due_date Sortierung + Ueberfaellig-Markierung
- Bewerber-Task-Erstellung
**Aufwand:** 3-4h

### 9. Messaging-Performance
- DB-Indizes (bereits in P0 #1)
- Pagination auf 50/Seite
**Aufwand:** 1h

### 10. Fallliste erweitern
- Mitarbeiter-/Bewerbernummer-Filter
- Gesamtzahl-Header
**Aufwand:** 1-2h

### 11. Dashboard Layout-Fix
- Responsive: zweite Spalte sichtbar
**Aufwand:** 30min

### 12. E-Mail-Sprache
- Templates DE/EN basierend auf language_pref
**Aufwand:** 1-2h

### 13. Dokument-Status-Grouping
- Frontend: Gruppierung nach akzeptiert/abgelehnt/offen
**Aufwand:** 1h

---

## P2 – Ausbau

### 14. Reporting-Erweiterung (Zeitraum-Filter, Diagramme)
### 15. Kalender-Integration
### 16. Virenscanning (ClamAV)
### 17. Partner-Reports
### 18. Profilzentrierung Bewerber-Portal

---

## Risk-Matrix

| Risk | Wahrscheinlichkeit | Impact | Mitigation |
|------|-------------------|--------|------------|
| Bewerbernummer Race-Condition | Mittel | Hoch | MongoDB findOneAndUpdate mit $inc |
| i18n Keys fehlen in EN | Hoch | Mittel | Fallback auf DE |
| S3 Storage nicht erreichbar | Niedrig | Hoch | Fallback auf MongoDB Binary |
| DeepSeek API Down | Mittel | Mittel | Validierung laeuft ohne KI weiter |
| Breaking Change bei PDF-Gen | Niedrig | Mittel | Unit-Test fuer PDF |
