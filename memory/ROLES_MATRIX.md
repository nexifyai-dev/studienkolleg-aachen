# Rollen- und Rechtematrix – W2G Platform v1.3.2

## Rollenübersicht

| Rolle | Systemname | Portal | Beschreibung |
|-------|-----------|--------|-------------|
| Superadmin | `superadmin` | Staff | Vollzugriff auf alle Module, Nutzerverwaltung, Audit |
| Admin | `admin` | Staff | Wie Superadmin, ohne Systemkonfiguration |
| Mitarbeiter | `staff` | Staff | Bewerbungsbearbeitung, Dokumentenprüfung, Kommunikation |
| Buchhaltung | `accounting_staff` | Staff | Finanzen, Rechnungen, eingeschränkter Bewerberzugriff |
| Lehrer | `teacher` | Staff (eingeschränkt) | Nur zugewiesene Schüler, zweckgebundener Datenzugriff |
| Bewerber | `applicant` | Applicant | Eigenes Portal, Bewerbung, Dokumente, Nachrichten |
| Agentur-Admin | `agency_admin` | Partner | Verwaltung eigener Agenten und Bewerber |
| Agentur-Agent | `agency_agent` | Partner | Bewerber der eigenen Agentur |
| Affiliate | `affiliate` | Partner | Empfehlungs-Dashboard |

## Detailmatrix: Berechtigungen nach Ressource

### Bewerberdaten

| Berechtigung | Superadmin | Admin | Staff | Buchhaltung | Lehrer | Bewerber |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Alle Bewerber lesen | ja | ja | ja | eingeschränkt | NEIN | NEIN |
| Zugewiesene Bewerber lesen | ja | ja | ja | ja | ja (Consent) | n/a |
| Eigene Daten lesen | n/a | n/a | n/a | n/a | n/a | ja |
| Bewerberdaten anlegen | ja | ja | ja | NEIN | NEIN | eigene |
| Bewerberdaten bearbeiten | ja | ja | ja | NEIN | NEIN | eigene |
| Bewerberdaten löschen | ja | NEIN | NEIN | NEIN | NEIN | NEIN |
| Bewerberdaten exportieren | ja | ja | ja | eingeschränkt | NEIN | eigene |

### Dokumente

| Berechtigung | Superadmin | Admin | Staff | Buchhaltung | Lehrer | Bewerber |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Alle Dokumente lesen | ja | ja | ja | NEIN | NEIN | NEIN |
| Zugewiesene Dokumente lesen | ja | ja | ja | NEIN | Status nur | n/a |
| Eigene Dokumente lesen | n/a | n/a | n/a | n/a | n/a | ja |
| Dokumente hochladen | ja | ja | ja | NEIN | NEIN | ja |
| Dokumente prüfen/freigeben | ja | ja | ja | NEIN | NEIN | NEIN |
| Sensible Dokumente (Pass) | ja | ja | ja | NEIN | NEIN | eigene |

### Kommunikation

| Berechtigung | Superadmin | Admin | Staff | Buchhaltung | Lehrer | Bewerber |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Alle Nachrichten lesen | ja | ja | ja | NEIN | NEIN | NEIN |
| Zugewiesene Nachrichten | ja | ja | ja | NEIN | zugewiesene | n/a |
| Eigene Nachrichten | n/a | n/a | n/a | n/a | n/a | ja |
| Nachrichten senden | ja | ja | ja | NEIN | zugewiesene | ja |
| Systemnachrichten versenden | ja | ja | NEIN | NEIN | NEIN | NEIN |

### Finanzen

| Berechtigung | Superadmin | Admin | Staff | Buchhaltung | Lehrer | Bewerber |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Alle Finanzdaten lesen | ja | ja | NEIN | ja | NEIN | NEIN |
| Eigene Rechnungen lesen | n/a | n/a | n/a | n/a | n/a | ja |
| Rechnungen erstellen | ja | ja | NEIN | ja | NEIN | NEIN |
| Zahlungsstatus ändern | ja | ja | NEIN | ja | NEIN | NEIN |

### AI-Screening

| Berechtigung | Superadmin | Admin | Staff | Buchhaltung | Lehrer | Bewerber |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| AI-Report einsehen | ja | ja | ja | NEIN | NEIN | NEIN |
| AI-Screening auslösen | ja | ja | ja | NEIN | NEIN | NEIN |

### Nutzer- & Systemverwaltung

| Berechtigung | Superadmin | Admin | Staff | Buchhaltung | Lehrer | Bewerber |
|-------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Nutzer anlegen/einladen | ja | ja | NEIN | NEIN | NEIN | NEIN |
| Nutzer deaktivieren | ja | ja | NEIN | NEIN | NEIN | NEIN |
| Rollen zuweisen | ja | ja | NEIN | NEIN | NEIN | NEIN |
| Audit-Logs lesen | ja | ja | NEIN | NEIN | NEIN | NEIN |
| Workspaces verwalten | ja | ja | NEIN | NEIN | NEIN | NEIN |

### Lehrer-spezifische Berechtigungen

| Berechtigung | Ergebnis | Details |
|-------------|---------|---------|
| Schüler sehen | Nur zugewiesene | assignment-basiert via `teacher_assignments` |
| Daten-Scope | Zweckgebunden | Name, E-Mail, Telefon, Kurstyp, Sprachniveau, Bewerbungsstatus |
| Ausgeschlossen | Immer | Finanzdaten, AI-Reports, interne Notizen, Passdaten, Referral-Codes |
| Consent erforderlich | Ja | Bewerber muss `teacher_data_access` Consent aktiv erteilen |
| Aktiv/Inaktiv-Schaltung | Durch Admin | via User-Update (`active: true/false`) |
| Zuweisung von Schülern | Durch Staff/Admin | via `/api/teacher/assignments` |
| Audit-Trail | Vollständig | Jeder Datenzugriff wird protokolliert |

## Archiv- und Ablehnungslogik

| Status | Sichtbarkeit | Reaktivierung | Lehrer-Zugriff |
|--------|-------------|---------------|----------------|
| `archived` | Staff+Admin: Separater Bereich | Ja, durch Staff/Admin | NEIN (Zuweisung wird deaktiviert) |
| `declined` | Staff+Admin: Separater Bereich | Ja, durch Staff/Admin | NEIN |
| `on_hold` | Staff+Admin: Pipeline | Ja, automatisch | Nach Zuweisung + Consent |

## Datenschutz-Prinzipien

1. **Datenminimierung**: Lehrer sehen nur das Nötigste für den Unterrichtszweck
2. **Zweckbindung**: Datenzugriff ist strikt an den Betreuungszweck gebunden
3. **Need-to-know**: Kein pauschaler Leserecht für Lehrer
4. **Consent-Pflicht**: Bewerber müssen der Datenweitergabe an Lehrpersonal explizit zustimmen
5. **Widerruf**: Consent ist jederzeit widerrufbar, Zugriff wird sofort entzogen
6. **Protokollierung**: Alle Zugriffe werden im Audit-Log festgehalten
7. **Rollenbegrenzung**: Lehrer haben keinen Zugang zu Admin-, Finanz- oder HR-Funktionen

## Offene rechtliche Punkte

- [OFFEN] Finale juristische Prüfung der Datenschutzlogik vor Go-Live
- [OFFEN] Prüfung ob Einwilligung für Lehrzugriff als Auftragsverarbeitung klassifiziert werden muss
- [OFFEN] Löschkonzept: Aufbewahrungsfristen für Bewerberdaten nach Ablehnung/Archivierung
- [OFFEN] Recht auf Datenportabilität: Export-Format für Bewerber definieren
