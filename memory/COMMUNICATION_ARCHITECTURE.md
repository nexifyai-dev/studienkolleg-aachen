# Kommunikationsarchitektur – Studienkolleg Aachen Platform
# Stand: Phase 3.5 (März 2026)
# Status: Architektonisch vorbereitet – nicht alle Kanäle live in v1.2.0

---

## 1. Telefon (Click-to-Dial) – LIVE in v1.2.0

**Status:** Implementiert  
**Wo:** Staff > Applicant Detail Page

Implementierung: `<a href="tel:+4924199032292">Anrufen</a>`

Jede Bewerber-Detailseite zeigt:
- Direkt-Anruf-Button (tel: Link)  
- WhatsApp-Direct-Link (wa.me/NUMMER)  
- E-Mail-Link mit vorausgefülltem Betreff  

---

## 2. E-Mail – Vorbereitet / Teilweise live

**Status:** E-Mail-Versand via Resend (Template-basiert) live.  
Direktes IMAP/SMTP-Threading noch nicht implementiert.  

### Aktueller Stand
- Ausgehende E-Mails: Resend mit Templates (Bewerbungseingang, Dokumentenanforderung, Status-Change, Reset, Invite)
- Domain: `stk-aachen.de` → muss in Resend verifiziert werden (Go-Live-Blocker!)

### Architektur-Vorbereitung: IMAP/SMTP-Threading

```
Für Pro-Mitarbeiter-Mailanbindung:
- IMAP-Credentials per Mitarbeiter-Account speichern (verschlüsselt)
- SMTP-Versand mit Mitarbeiter-Absender konfigurieren
- Thread-ID in E-Mails einbetten → Zuordnung zum Bewerberfall
- Collection: email_threads { thread_id, application_id, from, to, subject, body, direction, received_at }
```

### Empfohlene nächste Schritte
1. Resend-Domain verifizieren
2. Gemeinsame Inbox-Anbindung via IMAP (`info@stk-aachen.de`)
3. E-Mail-Thread-View in Staff-Detailseite einbauen
4. Pro-Mitarbeiter-SMTP ermöglichen (Settings in UserAccount)

---

## 3. WhatsApp Business – Architektonisch vorbereitet

**Status:** WhatsApp-Links live (wa.me + bestehender QR-Code-Link eingebunden).  
Session-Kopplung noch nicht implementiert.  

### Empfohlene Lösung: whatsapp-web.js (QR-Kopplung)

Begründung: Nutzt bestehenden WhatsApp Business-Account des Kunden ohne Meta-API-Genehmigungsverfahren.

**Wichtig: Risiken kommunizieren**
- whatsapp-web.js ist inoffizielle Bibliothek (WhatsApp ToS Graubereich)
- Für Testbetrieb / kleine Teams akzeptabel
- Für Skalierung → offiziell WhatsApp Business Cloud API über Meta (Antragsprozess ~4-8 Wochen)

### Architektur-Entwurf (Node.js Service, getrennt vom Python-Backend)

```
/app/whatsapp-service/
├── index.js          # Express + whatsapp-web.js Client
├── qr.js             # QR-Code-Generierung + Session-Speicherung
├── handlers.js       # Eingehende Nachrichten → Backend-Webhook
├── sender.js         # Ausgehende Nachrichten (via REST API)
└── .wwebjs_auth/     # Session-Persistenz (gitignore!)
```

**Endpoints (intern, staff-only):**
- `GET /wa/qr`         → QR-Code für Erstverbindung anzeigen
- `GET /wa/status`     → Verbindungsstatus prüfen
- `POST /wa/send`      → Nachricht an Bewerber senden
- `POST /wa/webhook`   → Eingehende Nachrichten ans Backend weiterleiten

**Integration in Platform-Backend:**
```python
# services/whatsapp.py
async def send_whatsapp(phone: str, message: str):
    """Sendet WhatsApp-Nachricht über den Node.js-Dienst."""
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(WA_SERVICE_URL + "/wa/send", json={"phone": phone, "message": message})
```

**RBAC:** Nur Staff/Admin darf Nachrichten senden. Verlauf wird in `messages` Collection gespeichert.

**Datenschutz:**
- Nachrichten werden wie alle anderen Kommunikationen im Audit-Log erfasst
- Kein Speichern von Medien ohne Einwilligung
- DSGVO: Kommunikation über WhatsApp setzt Einwilligung des Bewerbers voraus (im Formular abfragen)

### Bestehender WhatsApp-Link (sofort nutzbar)
```
https://api.whatsapp.com/message/RVKVWFEKNCIRG1?autoload=1&app_absent=0
```
Dieser Link leitet zu einem bestehenden WhatsApp-Account weiter. Bereits eingebunden in Footer, ContactPage und ApplicantDetailPage.

### Empfohlene nächste Schritte für vollständige Integration
1. Node.js whatsapp-web.js Service aufsetzen
2. QR-Code-Ansicht im Staff-Admin einbauen (einmalig scannen)
3. Session persistieren (`.wwebjs_auth/` außerhalb des Repos)
4. Incoming-Message-Webhook → Nachrichten in `messages` Collection speichern
5. Staff kann über das Portal WhatsApp-Nachrichten senden/empfangen
6. Langfristig: Migration zu offizieller Meta Business Cloud API

---

## 4. Zusammenfassung

| Kanal         | Status           | Priorität | Aufwand |
|---------------|------------------|-----------|---------|
| Telefon       | LIVE (click-to-dial) | –    | Fertig  |
| WhatsApp Link | LIVE (wa.me + Footer) | –   | Fertig  |
| E-Mail Resend | LIVE (Domain ausstehend) | P0 | Domain verifizieren |
| WhatsApp WA-Web.js | Vorbereitet | P1 | Mittel (Node.js Service) |
| IMAP/SMTP Threading | Vorbereitet | P1 | Mittel |
| Meta Business API | Geplant | P2 | Hoch (Genehmigung) |
