# Rollen und Berechtigungen

> Zurück: [README](../README.md) · Architektur: [docs/architecture/overview.md](architecture/overview.md)

## Rollenmatrix (operativ)

| Rolle | Primäres Portal | Darf sehen | Darf ändern | Darf entscheiden |
|---|---|---|---|---|
| Public | Public | Öffentliche Inhalte | Kontakt-/Bewerbungsanstoß | Nein |
| Applicant | Applicant | Eigene Journey, Dokumente, Nachrichten | Eigene Angaben und Uploads | Nein |
| Staff | Staff | Zugewiesene Fälle, Aufgaben, Kommunikation | Fallstatus, Aufgaben, Notizen | Ja (operativ) |
| Admin | Admin | Systemweite Übersichten, Audit, Nutzer | Rollen, Policies, Freigaben | Ja (systemisch) |
| Partner | Partner | Eigene Referrals | Referral-Metadaten | Nein |
| Teacher | Staff/Teacher | Lehrrelevante Vorgänge | Feedback/Statusfelder | Nein (final) |

## Entscheidungsprinzipien

- KI-Empfehlungen sind nicht gleich Entscheidung.
- Staff-Entscheidung ist fachlich bindend; Admin definiert systemische Leitplanken.
- Keine Rolle darf über Portalgrenzen hinweg unautorisierte Aktionen erhalten.

## Verknüpfte Flows

- [Applicant-Workflow](workflows/applicant.md)
- [Staff-Workflow](workflows/staff.md)
- [Admin-Workflow](workflows/admin.md)
- [Partner-Workflow](workflows/partner.md)
- [Teacher-Workflow](workflows/teacher.md)

## Verknüpfte Governance

- [PR-Policy](governance/pr-policy.md)
- [Blocking-Kriterien](governance/blocking-criteria.md)
- [Dokumentationspflichten](governance/documentation-duties.md)

## Dokumentverantwortung

- **Owner:** Security & Access Control Owner
- **Update-Prozess:** Bei jeder PR mit Rollen-/Rechte-, Auth-, Routing- oder Portaländerungen.
