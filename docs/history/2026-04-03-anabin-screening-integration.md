# 2026-04-03 – Anabin-Screening-Integration + Feedback-Loop

## Kontext
Die Anabin-Wissensbasis wurde aktiv in den KI-Screening-Service integriert.
Unbekannte Abschluesse und Sonderfaelle werden automatisch an die Review-Queue
weitergeleitet. Staff-Entscheidungen fliessen ueber den Feedback-Loop in die
Wissensbasis zurueck.

## Aenderungen

### Backend: ai_screening.py
- `lookup_knowledge(country, degree_type, app_id)` ersetzt `lookup_country()`
- Erweiterter KI-Prompt mit Match-Typ, Konfidenz, Staff-Hinweis, Sonderfall-Flags
- Auto-Queue-Erstellung nach Screening bei unknown/fuzzy/special_case/D-Kategorie
- Erweiterte `_suggest_stage()` mit Sonderfall- und Konfidenz-Logik

### Backend: anabin_admin.py
- Neuer Endpoint: POST /api/anabin/review-queue/{id}/resolve
- Ruft `resolve_queue_with_feedback()` auf
- Aktualisiert optional die Wissensbasis (Feedback-Loop)
- Audit-Trail fuer jede Queue-Aufloesung

### Backend: anabin_knowledge.py (aus vorherigem Job)
- `lookup_knowledge()` mit Degree-Matching, Fuzzy-Search, Auto-Flag
- `create_queue_from_screening()` fuer externe Aufrufe
- `resolve_queue_with_feedback()` fuer Staff-Entscheidungen

### Frontend: AdminKnowledgePage.js
- Neues `ResolveWithFeedbackModal` mit KB-Formular
- Felder: Kategorie, Konfidenz, Operative Einstufung, Staff-Hinweis, Notizen
- Checkboxen: Sonderfall, Staff-Entscheid
- Toggle: Wissensbasis-Update ja/nein

## Testing
- Iteration 40: 100% Backend (18/18), 100% Frontend
- E2E-Flow: Queue → Resolve mit Feedback → Wissensbasis aktualisiert

## Betroffene Dateien
- /app/backend/services/ai_screening.py
- /app/backend/routers/anabin_admin.py
- /app/frontend/src/pages/admin/AdminKnowledgePage.js
