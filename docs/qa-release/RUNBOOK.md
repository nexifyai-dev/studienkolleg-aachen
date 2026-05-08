# Runbook – W2G Platform

**Version:** 1.0  
**Datum:** 2026-04-03  
**Zielgruppe:** Betrieb, Entwicklung, AI-Agenten

---

## 1. Incident-Triage

| Schwere | Kriterium | Reaktionszeit | Beispiel |
|---------|-----------|---------------|---------|
| **KRITISCH** | System nicht erreichbar, Datenverlust, Auth-Bypass | Sofort | Backend-Crash, MongoDB-Ausfall |
| **HOCH** | Kernfunktion nicht nutzbar | < 1 Stunde | Login fehlerhaft, Bewerbungen nicht anlegbar |
| **MITTEL** | Teilfunktion eingeschraenkt | < 4 Stunden | PDF-Export fehlerhaft, Filter defekt |
| **NIEDRIG** | Kosmetisch, UX-Verbesserung | Naechster Sprint | Button-Alignment, Tippfehler |

---

## 2. Erste Pruefschritte bei jedem Incident

```bash
# 1. Service-Status pruefen
sudo supervisorctl status

# 2. Backend-Logs pruefen (letzte 100 Zeilen)
tail -n 100 /var/log/supervisor/backend.err.log
tail -n 100 /var/log/supervisor/backend.out.log

# 3. Frontend-Logs pruefen
tail -n 100 /var/log/supervisor/frontend.err.log

# 4. Health-Check
curl -s $BACKEND_URL/api/health

# 5. MongoDB-Verbindung pruefen
mongosh --eval "db.adminCommand('ping')"

# 6. Disk-Space pruefen
df -h /app
```

---

## 3. Logs, Signale und Health-Indikatoren

| Signal | Quelle | Bedeutung |
|--------|--------|-----------|
| `{"status":"ok"}` | `/api/health` | System laeuft |
| `email_enabled: true/false` | `/api/health` | E-Mail-Konfiguration aktiv/inaktiv |
| `storage_backend: local/s3` | `/api/health` | Storage-Modus |
| Backend RUNNING | supervisorctl | FastAPI-Prozess laeuft |
| MongoDB RUNNING | supervisorctl | Datenbank erreichbar |
| HTTP 401 | API-Antwort | Token abgelaufen oder ungueltig |
| HTTP 403 | API-Antwort | Fehlende Rolle/Berechtigung |
| HTTP 422 | API-Antwort | Validierungsfehler (Pydantic) |
| HTTP 500 | API-Antwort | Interner Serverfehler → Backend-Logs pruefen |

---

## 4. Typische Fehlerbilder und Vorgehen

### 4.1 Auth-Probleme

**Symptom:** Login schlaegt fehl, 401-Fehler, "Unauthorized"

**Pruefschritte:**
1. Korrekte Credentials pruefen (vgl. `/app/memory/test_credentials.md`)
2. Backend-Logs auf Fehlermeldung pruefen
3. Brute-Force-Lockout pruefen:
   ```bash
   # In MongoDB nachschauen
   mongosh w2g_platform --eval "db.users.findOne({email:'<EMAIL>'}, {failed_login_attempts:1, locked_until:1})"
   ```
4. Bei Lockout: 15 Minuten warten oder manuell zuruecksetzen:
   ```bash
   mongosh w2g_platform --eval "db.users.updateOne({email:'<EMAIL>'}, {\$set:{failed_login_attempts:0, locked_until:null}})"
   ```
5. JWT_SECRET Aenderung? → Alle Sessions ungueltig, Nutzer muessen neu einloggen
6. COOKIE_SECURE=true bei HTTP? → Cookies werden nicht gesetzt

**Produktkritisch:** JA

---

### 4.2 Dokumenten-Upload-Probleme

**Symptom:** Upload schlaegt fehl, Dokument nicht gespeichert

**Pruefschritte:**
1. Storage-Backend pruefen: `STORAGE_BACKEND` in `.env`
2. Bei `local`: Schreibrechte auf `/app/storage` pruefen:
   ```bash
   ls -la /app/storage/
   ```
3. Bei `s3/minio`: S3-Credentials und Bucket-Zugang pruefen
4. Dateigroesse pruefen (FastAPI-Limit: 50MB default)
5. Backend-Logs auf Fehlermeldung pruefen

**Produktkritisch:** JA (Bewerber muessen Dokumente hochladen koennen)

---

### 4.3 Messaging-/Mail-Probleme

**Symptom:** Nachrichten werden nicht zugestellt, IMAP-Sync fehlerhaft

**Pruefschritte:**
1. Portal-Nachrichten (channel=portal): Immer verfuegbar, keine externe Abhaengigkeit
2. E-Mail-Sync: IMAP-Credentials pruefen (`IMAP_HOST`, `EMAIL_USER`, `EMAIL_PASSWORD`)
3. SMTP-Versand: SMTP-Credentials pruefen
4. Resend (transaktional): `RESEND_API_KEY` pruefen
5. Bounce-Filter: `/api/messages/sync` gibt gefilterte Nachrichten zurueck
6. Backend-Logs fuer IMAP-Verbindungsfehler pruefen

**Produktkritisch:** Portal-Nachrichten JA, E-Mail NEIN (graceful degradation)

---

### 4.4 PDF-/Export-Probleme

**Symptom:** Fallakte-PDF leer, fehlerhaft oder Download schlaegt fehl

**Pruefschritte:**
1. Endpunkt direkt testen:
   ```bash
   curl -s -b /tmp/cookies "$URL/api/applications/<ID>/pdf" -o test.pdf
   ```
2. Backend-Logs auf ReportLab-Fehler pruefen
3. Bewerbungs-ID validieren (existiert der Datensatz?)
4. Speicherplatz pruefen (PDF wird im Memory generiert und gestreamt)

**Produktkritisch:** NEIN (Fallakte ist auch ohne PDF im Portal einsehbar)

---

### 4.5 AI-Screening-Probleme

**Symptom:** KI-Bewertung schlaegt fehl, leere Ergebnisse

**Pruefschritte:**
1. `NSCALE_API_KEY` gesetzt?
2. nscale-API erreichbar? (externer Service)
3. Backend-Logs fuer API-Timeout oder Rate-Limiting pruefen
4. Eingabedaten validieren (genug Informationen fuer Screening?)

**Produktkritisch:** NEIN (manuelle Bewertung weiterhin moeglich)

---

### 4.6 Deployment-/Config-Probleme

**Symptom:** Service startet nicht, 502-Fehler, leere Seite

**Pruefschritte:**
1. Supervisor-Status: `sudo supervisorctl status`
2. Backend-Fehlerlog: `tail -n 100 /var/log/supervisor/backend.err.log`
3. Frontend-Fehlerlog: `tail -n 100 /var/log/supervisor/frontend.err.log`
4. Fehlende ENV-Variable? → Backend gibt beim Start RuntimeError aus
5. Port-Konflikt? → Backend MUSS auf 8001, Frontend MUSS auf 3000
6. MongoDB nicht erreichbar? → `mongosh --eval "db.adminCommand('ping')"`
7. Neustart:
   ```bash
   sudo supervisorctl restart backend
   sudo supervisorctl restart frontend
   ```

**Produktkritisch:** JA

---

## 5. Eskalationslogik

| Stufe | Wer | Wann |
|-------|-----|------|
| L1: Agent/Entwickler | Selbstdiagnose mit Runbook | Bei jedem Incident |
| L2: Projektleitung | Agent kann Problem nicht loesen | Nach 2 fehlgeschlagenen Fix-Versuchen |
| L3: Plattform-Support | Infrastruktur-/Plattformfehler | Bei Deployment-/Registry-/DNS-Problemen |
| L4: Externer Provider | Drittanbieter-Ausfall | nscale-API, Strato-Mail, Resend nicht erreichbar |

---

## 6. Produktkritisch vs. nicht produktkritisch

### Produktkritisch (sofortige Reaktion)
- Auth/Login
- Bewerbungs-CRUD
- Dokument-Upload und -Anzeige
- Portal-Messaging
- Rollenzugriff (RBAC)
- MongoDB-Verfuegbarkeit

### Nicht produktkritisch (geplante Behebung)
- AI-Screening (manuelle Alternative vorhanden)
- E-Mail-Sync (Portal-Nachrichten als Fallback)
- PDF-Export (Daten sind im Portal sichtbar)
- Kostenkalkulator
- Partner-Dashboard (eingeschraenkte Nutzergruppe)
