# W2G Platform – Teststrategie

**Stand:** 2026-04-06

---

## 1. Testpyramide

### Unit/Integration (Backend)
- pytest fuer kritische Business-Logik
- Bewerbernummer-Generierung (Uniqueness, Format)
- Dokument-Validierung (Typ-Erkennung, Groessenprüfung)
- Invoice-Nummerierung
- Stage-Transition-Logik

### API-Tests (curl / httpie)
- Auth-Flow: Login → Me → Refresh → Logout
- CRUD: Applications, Documents, Invoices, Tasks
- Rollen-Tests: Applicant vs Staff vs Admin Zugriff
- Error Cases: 400, 401, 403, 404, 429

### E2E-Tests (Testing Agent / Playwright)
- Bewerbung anlegen (Public Apply → Portal Login)
- Dokument hochladen → Vorschau → Loeschen
- Rechnung erstellen → PDF → E-Mail
- Nachricht senden → Inbox anzeigen
- Sprache umschalten (DE ↔ EN)
- Task erstellen → Status aendern

### Visual Regression (Screenshot)
- Staff Dashboard (DE + EN)
- Fallakte / Bewerberprofil
- Bewerber-Portal Dashboard
- Rechnungs-PDF (DE + EN)

---

## 2. Rollen-Test-Matrix

| Flow | Applicant | Staff | Admin | Partner |
|------|----------|-------|-------|---------|
| Login/Logout | X | X | X | X |
| Bewerbung anlegen | X | X | - | - |
| Dokument hochladen | X | X | - | - |
| Dokument einsehen | X (eigene) | X (alle) | X (alle) | - |
| Rechnung erstellen | - | X | X | - |
| Rechnung einsehen | X (eigene) | X (alle) | X (alle) | - |
| Task erstellen | - | X | X | - |
| Task einsehen | X (public) | X | X | - |
| Nachricht senden | X | X | X | - |
| Sprache aendern | X | X | X | X |
| User verwalten | - | - | X | - |

---

## 3. Negative Tests

| Szenario | Erwartung |
|----------|-----------|
| Upload >10MB | HTTP 400 |
| Upload .exe Datei | HTTP 400 / Rejection |
| Login falsches PW (6x) | HTTP 429 nach 5x |
| Bewerber greift auf fremde App zu | HTTP 403 |
| Abgelaufener Token | HTTP 401 |
| Leere Rechnung | HTTP 400 |
| SQL Injection in Suchfeld | Keine Wirkung (NoSQL) |
| XSS in Nachricht | Escaped/sanitized |

---

## 4. Performance-Benchmarks

| Operation | Ziel | Messung |
|-----------|------|---------|
| /api/auth/me | < 50ms | curl Timing |
| /api/applications (100) | < 200ms | curl Timing |
| /api/conversations | < 150ms | curl Timing |
| /api/invoices/stats | < 100ms | curl Timing |
| PDF-Generierung | < 500ms | curl Timing |
| Dokumenten-Upload (1MB) | < 3s | curl Timing |

---

## 5. Test-Credentials

Siehe `/app/memory/test_credentials.md`
