# Kommunikationsarchitektur – W2G Platform

## Uebersicht
Die Kommunikation ist als zentrale Inbox (3-Spalten-Layout) realisiert.
Zugang ueber: Staff Portal → Nachrichten

## Architektur
```
┌──────────────────────────────────────────────────────────────────────────┐
│ Kommunikation / Inbox                              [+ Neue Nachricht]   │
├──────────────────────────────────────────────────────────────────────────┤
│ Filter: [Kanal] [Status] [Suche]                                        │
├──────────────┬────────────────────────────────────┬──────────────────────┤
│ Konversation │ Thread / Verlauf                   │ Kontextpanel         │
│ sliste       │ - Kanal-Badge                      │ - Bewerber/Fall      │
│ - Avatar     │ - Richtung (ein/aus)               │ - aktueller Status   │
│ - Name       │ - Zeitstempel                      │ - offene Aufgaben    │
│ - Kanal      │ - Interne Notizen (gelb)           │ - Dokumente          │
│ - Status     │ - Anhaenge                         │ - Rechnungen         │
│ - Ungelesen  │ - Reply Composer                   │ - Kanal-Status       │
│ - Preview    │ - Notiz-Toggle                     │ - Quick Actions      │
└──────────────┴────────────────────────────────────┴──────────────────────┘
```

## Kanaele
| Kanal | Status | Backend | Frontend |
|-------|--------|---------|----------|
| Portal | AKTIV | Messages mit channel=portal | Voll integriert |
| E-Mail | VORBEREITET | channel=email, Signatur-API | UI vorbereitet, IMAP/SMTP nicht angebunden |
| WhatsApp | NUR LINK | channel=whatsapp | wa.me-Link, keine API-Integration |

## Signatur
Zentrale Signatur ueber GET /api/email-signature:
- Rollenbezogen (Staff=Studienberatung, Admin=Administration, Teacher=Lehrkraft)
- DE/EN per Query-Parameter
- Alle E-Mail-Aktionen im System nutzen dieselbe Signatur

## Konversations-Status
| Status | Bedeutung |
|--------|-----------|
| open | Neue/unbeantwortete Nachricht |
| answered | Staff hat geantwortet |
| escalated | Manuell eskaliert |
| closed | Abgeschlossen |

## Sichtbarkeit
| Typ | Sichtbar fuer |
|-----|---------------|
| public | Alle Teilnehmer |
| internal | Nur Staff (Applicants sehen keine internen Notizen) |

## Fallbezug
- Konversationen koennen ueber application_id einem Fall zugeordnet werden
- Kontextpanel zeigt automatisch: Fallstatus, Aufgaben, Dokumente, Rechnungen
- Deep Link in Fallakte aus Kontextpanel
