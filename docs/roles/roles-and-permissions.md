# Rollen- und Rechte-Dokumentation

Stand: 2026-03-30

## Rollen
- superadmin
- admin
- staff
- accounting_staff
- teacher
- applicant
- affiliate

## Sichtbarkeit und Grenzen
- **Applicant:** ausschließlich eigene Bewerbungs-, Dokument- und Nachrichtenobjekte.
- **Staff/Admin:** vollständige operative Sicht je nach Modul.
- **Teacher:** nur zugewiesene Bewerber und nur bei aktivem Consent für Lehrzugriff.
- **Affiliate/Partner:** referral-bezogene Sicht, kein Vollzugriff auf interne Staff-/Admin-Daten.

## Consent-gated Bereiche
- Teacher-Zugriff ist zwingend an Consent + Assignment gekoppelt.
- Widerruf des Consent muss Zugriffswirkung sofort begrenzen.

## Teacher Assignment Logic
- Zuweisung durch Staff/Admin über dedizierte Assignment-Prozesse.
- Ohne Assignment kein Zugriff, auch bei Teacher-Rolle.

## Administrative Sonderrechte
- Nutzerverwaltung, Rollenänderung, Audit-Einsicht nur Admin/Superadmin.

## Applicant/Partner/Staff/Admin Abgrenzungen
- Keine Rollenüberlagerung ohne explizite Rollenprüfung.
- Partner hat keinen direkten Schreibzugriff auf interne Bewerberentscheidungen.

## Serverseitige Prüflogik (dokumentierbar)
- `require_roles(...)` im Backend als primäre Zugriffsschranke.
- Objektbezogene Ownership-/Assignment-Checks in Routerlogik.
- Sensible Aktionen erzeugen Audit-Einträge.

## Sicherheitsgrundsätze
- Need-to-know statt Vollsicht.
- Datenminimierung (insb. Teacher-Ansicht).
- Keine clientseitige Autorisierung als alleinige Schutzmaßnahme.
