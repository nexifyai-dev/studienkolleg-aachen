# 11_rollen_und_rechte_matrix.md

## Rollenmodell

### Kernrollen Release 1
- superadmin
- admin
- staff
- accounting_staff
- agency_admin
- agency_agent
- affiliate
- applicant

### Erweiterungsrollen später
- teamlead
- content_admin
- company_user
- reviewer / compliance
- education_manager

## Rechteprinzipien

1. Rechte werden **serverseitig** geprüft.
2. UI zeigt nur erlaubte Aktionen.
3. Workspace- und Tenant-Kontext sind bindend.
4. Applicant sieht nur eigene Daten.
5. Agency sieht nur eigene Fälle.
6. Accounting sieht Finanzdaten, aber nicht beliebige interne Inhalte ohne Freigabe.
7. Superadmin ist Eskalations- und Governance-Rolle, nicht operative Default-Rolle.

## Rollenmatrix

| Rolle | lesen | anlegen | bearbeiten | löschen | exportieren | versenden | freigeben | veröffentlichen | archivieren |
|---|---|---|---|---|---|---|---|---|---|
| superadmin | alles | alles | alles | streng kontrolliert | alles | alles | alles | alles | alles |
| admin | fast alles im eigenen Tenant | Nutzer, Workspaces, Fälle, Regeln | fast alles | eingeschränkt | Reports, Fälle, Finance nach Freigabe | ja | ja | ja | ja |
| staff | eigene / berechtigte Fälle | Fälle, Tasks, Kommentare, Nachrichten, Dokumentanforderungen | eigene / zugewiesene Fälle | nein physisch, nur Soft-Delete-Antrag | eingeschränkt | Bewerber-/Partnerkommunikation | Dokumente / Status je Berechtigung | nein | Fälle in definierter Logik |
| accounting_staff | Rechnungen, Transaktionen, Zahlungsstatus | Zahlungsbuchungen / manuelle Markierungen | Finanzstatus | nein | Finance-Exporte | Rechnungsversand | Zahlungseingänge bestätigen | nein | nein |
| agency_admin | eigene Organisation / eigene Kandidaten | Kandidaten, Agency-User | eigene Kandidaten / Agency-Struktur | keine harten Löschungen | eigene Reports | eigene Nachrichten | nein, außer agency-interne Freigaben | Branding Level 1 eingeschränkt | eigene archivierte Sicht |
| agency_agent | eigene oder zugewiesene Kandidaten | Kandidaten | begrenzte Felder / Uploads / Kommunikation | nein | nein | Nachrichten im erlaubten Scope | nein | nein | nein |
| affiliate | eigene Leads / Links / Provisionen | Links / Lead-Erfassung je Modell | Profildaten eingeschränkt | nein | eigene Provisionen | Nachrichten eingeschränkt | nein | eigene Landing-Meta ggf. später | nein |
| applicant | eigenes Profil / eigene Bereiche | eigenes Profil ergänzen, Uploads, Nachrichten | eigene Daten im erlaubten Scope | nein | eigene Rechnungen / Nachweise herunterladen | Nachrichten senden | keine Systemfreigaben | nichts veröffentlichen | Archivansicht nein |

## Objektbezogene Rechte

### profiles
- applicant: eigenes Profil lesen/bearbeiten
- staff: nur berechtigte Applicant-Profile im Arbeitskontext
- admin/superadmin: tenantweit
- agency: nur eigene Kandidatenprofile im erlaubten Scope
- affiliate: kein Vollprofil, nur Lead-/Provisionssicht

### applications
- applicant: eigene Applications
- staff: zugewiesene / bereichsberechtigte Applications
- admin: tenantweit
- agency: eigene Organisationsfälle
- affiliate: keine vollständige Application, nur Lead-/Statussicht falls freigegeben

### documents
- applicant: eigene Dokumente hochladen und Status sehen
- staff: prüfen / kommentieren / anfordern
- agency: je Modell und Freigabe
- affiliate: nur wenn fachlich vorgesehen; sonst nein
- public access: niemals

### invoices / transactions
- applicant: eigene Rechnungen / Zahlungen
- accounting_staff: volle Bearbeitung
- staff: lesen / anstoßen je Rolle
- agency / affiliate: nur provisions- oder partnerrelevante Finanzsicht, keine fremden Bewerberumsätze

### messages
- applicant: eigene Konversationen
- staff: berechtigte Konversationen
- agency: eigene Fallkontexte
- affiliate: eingeschränkt
- internal visibility muss separat abbildbar sein

## Sichtbarkeitslogik

### Applicant
- sieht nur aktive und eigene Workspaces,
- kein Einblick in interne Notizen,
- keine Einsicht in andere Bewerber oder Partnerstrukturen.

### Agency
- sieht nur Fälle der eigenen Organisation,
- agency_admin sieht alle eigenen Fälle,
- agency_agent nur eigene / zugewiesene,
- keine Sicht in interne Admin-/Finance-/anderen Agentur-Daten.

### Staff
- arbeitet im Workspace-Kontext,
- 360°-Sicht auf weitere Bereiche nur, wenn explizit berechtigt,
- Buchhaltung, Compliance und Content nur nach Zusatzrolle.

## Serverseitige Rechteprüfung

### Pflichtregeln
1. JWT / Session allein reicht nicht; Rechte müssen gegen DB-Kontext geprüft werden.
2. RLS für lesende und schreibende Queries.
3. Edge Functions validieren actor, workspace, tenant und Objektbezug.
4. Storage-Zugriffe referenzieren DB-Rechte.
5. Exporte sind rollen- und datensatzbegrenzt.

## RLS-/Rollen-Testmatrix

### Pflichttests vor Freigabe
- applicant kann fremde Application nicht lesen.
- agency_admin kann keine fremde Organisation sehen.
- agency_agent kann keine admin-only Felder ändern.
- staff ohne Finance-Rolle kann Transaktionen nicht exportieren.
- direct storage URL ohne Signed URL funktioniert nicht.
- deleted/archived Status wird korrekt gefiltert.

## Freigabe- und Publishing-Logik

| Aktion | Rolle |
|---|---|
| Dublette freigeben | superadmin / admin |
| Rechtsseite veröffentlichen | admin + Legal-Freigabe |
| Preisänderung veröffentlichen | admin + Commercial/Legal-Freigabe |
| Dokument akzeptieren / ablehnen | staff / reviewer |
| Rechnung final freigeben | accounting_staff / admin |
| Kurs manuell freischalten | admin / education_manager |
| White-Label-Branding ändern | superadmin / admin |
| Audit-Export ziehen | superadmin / compliance |

## No-Go-Punkte

1. Rechte nur im Frontend zu lösen.
2. Agency- oder Applicant-Filter nur auf URL-/UI-Ebene.
3. öffentliche Dokument-Buckets.
4. unprotokollierte Rollenänderungen.
5. Sammelrollen „kann alles“ ohne Audit.
