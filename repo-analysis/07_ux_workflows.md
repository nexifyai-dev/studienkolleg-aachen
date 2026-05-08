# 07_ux_workflows.md

## UX-Grundregeln

1. Kein Nutzer darf in einer Sackgasse enden.
2. Jeder Screen zeigt eine Hauptaktion.
3. Status ist sichtbar, aber niemals die einzige Information; es muss immer klar sein, **was jetzt zu tun ist**.
4. Applicant-Flows sind mobil priorisiert.
5. Staff-Flows minimieren Kontextwechsel und Suchaufwand.

## Kern-Nutzerflows

## Flow 1 – Lead zu Portalzugang

1. Lead kommt aus Formular, Kontaktanfrage, Partner oder manueller Erfassung.
2. System prüft Pflichtfelder und Dubletten.
3. Kein Treffer:
   - Profil anlegen,
   - Workspace-Membership anlegen,
   - Application anlegen,
   - zuständigen Mitarbeiter zuweisen,
   - Welcome-/Portalzugang versenden.
4. Treffer:
   - bestehendes Profil wiederverwenden,
   - neue Application/Notiz erzeugen,
   - kein zweiter Login versenden,
   - „Willkommen zurück“-Logik starten.
5. Applicant landet via Magic Link / First Login in Onboarding.

**Friktion:** doppelte Datensätze, unscharfe Leadzuordnung.  
**Optimierung:** klare Quelle, trigger_source, Dublettenqueue, Freigabe-Flow.

## Flow 2 – First Login / Onboarding

1. Applicant öffnet Link.
2. Passwort setzen oder Magic Link bestätigen.
3. Sprache wählen.
4. Profil vervollständigen.
5. Notification- und Kanalpräferenzen sehen.
6. Erste Aufgabe starten.
7. Landing auf Dashboard.

**Quick Actions:** Profil vervollständigen, ersten Upload starten, Nachricht an Team senden.  
**Error State:** Link abgelaufen → neuen Zugang anfordern.

## Flow 3 – Dokument-Upload und Korrekturschleife

1. Applicant sieht offene Dokumentenanforderung.
2. Klick auf Dokument führt direkt in Upload.
3. Upload speichert Datei privat, erzeugt Metadaten, setzt Status auf „hochgeladen / in Prüfung“.
4. Staff prüft:
   - akzeptiert → Applicant sieht „akzeptiert“,
   - abgelehnt → Applicant sieht Grund und CTA „neu hochladen“.
5. Re-Upload erzeugt neue Version / neuen Prüfzyklus.
6. Wenn alle Blocker-Dokumente vollständig sind, wird nächster Status oder Rechnung ausgelöst.

**Friktion:** unklare Ablehnungsgründe, Medienbruch, langsame Rückmeldung.  
**Optimierung:** Pflichtfeld Ablehnungsgrund, visuelle Checkliste, automatische Reminder.

## Flow 4 – Statuswechsel im Kernprozess

1. Staff bewegt Application im Kanban oder setzt Status im Detailprofil.
2. System validiert erlaubten Übergang.
3. Alte Aufgaben werden geschlossen oder entwertet.
4. Neue Aufgaben / Nachrichten / Rechnungen / Notifications werden erzeugt.
5. Applicant und ggf. Agentur erhalten kontextspezifische Information.
6. Audit Log schreibt alten und neuen Wert.

**Friktion:** Race Conditions, widersprüchliche Automationen.  
**Optimierung:** State Machine + optimistic locking + trigger_source.

## Flow 5 – Rechnung und Zahlung

1. Trigger: Status erreicht zahlungsrelevanten Punkt oder manuelle Freigabe.
2. System erstellt Invoice-Record.
3. PDF wird generiert und sicher gespeichert.
4. Applicant sieht Rechnung im Portal und per E-Mail.
5. Zahlung:
   - Stripe / PayPal / manuell erfasste Banküberweisung.
6. Webhook oder manuelle Bestätigung setzt Ledger/Status.
7. Nächste Prozessstufe startet.
8. Mahnlogik bei Überfälligkeit.

**Friktion:** Chargebacks, Teilzahlungen, VAT.  
**Optimierung:** Ledger-Modell, partially_paid-Status, fachliche Klärung vor Go-Live.

## Flow 6 – Beratung / Termin

1. Public CTA führt zu Calendly oder ähnlichem Tool.
2. Terminbuchung erzeugt Appointment im Profil.
3. Bewerber und zuständiger Mitarbeiter erhalten Bestätigung.
4. Vor dem Termin Reminder.
5. Nach dem Termin Task: Gespräch auswerten / nächster Schritt setzen.

**Friktion:** unverbundene Kalender, verlorene Informationen.  
**Optimierung:** Webhook-Sync + Follow-up Task.

## Flow 7 – Kursfreigabe / Kursbuchung / Kursnutzung

1. Sprachbedarf oder manuelle Freigabe erkannt.
2. Geeigneter Kurs erscheint im Portal.
3. Applicant bucht oder bekommt Zugriff.
4. Zahlung / Freigabe triggert Enrollment.
5. Interner Videokurs:
   - Start direkt im Portal.
6. Externer Kurs:
   - Zugriffskarte / Provisioning.
7. Kursfortschritt und Prüfung/Nachweise fließen ins Profil zurück.

**Friktion:** doppelte Dateneingabe, externer LMS-Umbruch.  
**Optimierung:** zentrale Enrollment- und Provisioning-Schicht.

## Flow 8 – Agency Workflow

1. Agency-User legt Kandidaten an oder sieht eingereichte Kandidaten.
2. Kandidat wird der Agentur und internem Verantwortlichen zugeordnet.
3. Agency sieht nur eigene Kandidaten, Status, ggf. Dokumente und Provisionen.
4. Interne Bearbeitung bleibt führend, sofern Agenturmodell B aktiv ist.
5. Änderungen und Nachrichten erscheinen im gemeinsamen Verlauf mit sauberer Sichtbarkeit.

**Friktion:** Rollenunklarheit, Überschneidung interner/externer Bearbeitung.  
**Optimierung:** Modell A/B als konfigurierbarer Workflow, sichtbare Zuständigkeit.

## Interne Betriebsflows

## Staff-Inbox / Kanban
- Eingang neuer Fälle
- Dublettenfreigabe
- Dokumentenprüfung
- Rückfrage an Bewerber
- Rechnungsfreigabe
- Eskalationsbearbeitung
- Archivierung

## Finance-Flow
- offene Rechnungen
- Teilzahlung / Zahlungseingang
- Storno / Refund
- Export / Steuerberater
- Provisionsberechnung

## Admin-/Governance-Flow
- Rollen anlegen
- Agentur-/Affiliate-Strukturen verwalten
- Pipelines / Dokumentenmatrizen / Standardtexte pflegen
- Legal-/Pricing-Content freigeben
- Audit-Fälle prüfen
- Monitoring / Failed Webhooks / Automation Runs prüfen

## CRM-/Bearbeitungslogik

### Zentrale Regel
Das Bewerberprofil ist die 360°-Ansicht und operative Zentrale. Von dort müssen direkt erreichbar sein:
- Status je Bereich,
- offene Aufgaben,
- Dokumente,
- Nachrichten,
- Zahlungen,
- Kurse,
- Termine,
- Notizen,
- Audit-Hinweise,
- weitere aktive Bereiche.

## Statuswechsel

### Mindestzustände je Bereich
- lead_new
- contacted
- docs_requested
- docs_received
- docs_review
- invoice_open
- payment_received
- next_step / application_submitted / course_active
- completed
- dormant / archived

**Hinweis:** konkrete Stage-Namen pro Bereich im Konfigurationslayer, nicht hart im Frontend.

## Such- und Filterlogik

### Applicant
- keine Suche nötig als Primärinteraktion,
- stattdessen klare Karten, Aufgaben und direkte Sprung-CTAs.

### Staff/Admin
- globale Suche,
- gespeicherte Filter („meine offenen Dokumente“, „überfällige Rechnungen“, „inaktive Leads >14 Tage“),
- Bulk-Ansichten nur dort, wo operativ sinnvoll.

## Leere Zustände

### Applicant
- „Du hast aktuell keine offene Rechnung.“
- „Es gibt momentan keine neuen Nachrichten.“
- „Dir ist noch kein Kurs freigeschaltet.“

### Staff
- „Heute keine neuen Dubletten.“
- „Keine überfälligen Stages in diesem Bereich.“

## Fehlerzustände

### Applicant
- technische Ursache in Klartext übersetzen,
- immer mit Aktion:
  - erneut versuchen,
  - später erneut,
  - Support kontaktieren.

### Staff/Admin
- Fehler mit Logreferenz,
- Retry,
- Eskalationsflag,
- Incident-Hinweis bei systemischen Problemen.

## Quick Actions

### Applicant
- Dokument hochladen
- Rechnung öffnen
- Nachricht senden
- Termin öffnen
- Kurs starten

### Staff
- Status ändern
- Dokument anfordern
- Nachricht schicken
- Rechnung erstellen
- Dublette prüfen
- Bewerber anderem Mitarbeiter zuweisen

### Admin
- Pipeline-Regel ändern
- Template freigeben
- Agentur anlegen
- Audit-Fall öffnen
- Webhook erneut verarbeiten

## UX-Risiken und Gegenmaßnahmen

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| zu viele Bereiche auf einmal sichtbar | Überforderung | Workspace-Kontext, progressive Offenlegung |
| unklare FSP-Kommunikation | Vertrauens- und Rechtsrisiko | Claim-Scope + Standardtexte |
| getrennte Mail-/WhatsApp-/Portal-Verläufe | Informationsverlust | zentrale Conversations-Schicht |
| Tabellen ohne mobile Strategie | unbenutzbar auf Smartphone | Karten/Drawer mobil, Tabellen erst desktop |
| RLS-Fehler nur im UI kaschiert | Datenleck | serverseitige Prüfung + Tests |
