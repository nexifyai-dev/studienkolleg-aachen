# 10_funktions_und_modulmatrix.md

## Modulmatrix

| Modul / Funktion | Zweck | Owner-Rolle | Priorität | Abhängigkeiten | Datenquellen | Rollen | Prüfpfad | Statuslogik |
|---|---|---|---|---|---|---|---|---|
| Lead Ingest | neue Leads strukturiert anlegen | admin / staff ops | Muss | profiles, applications, source mapping | forms, imports, partner inputs | public, staff, agency | Pflichtfeldtest, Dublettenlogik, Audit | new / duplicate / queued |
| Dublettenprüfung | Doppelprofile verhindern | superadmin / admin | Muss | profiles, phone/email normalization | CRM DB | superadmin, admin | Fallprüfung, Merge-Test | flagged / approved / merged |
| Applicant Identity | zentrale Person als SOT | system / admin | Muss | auth, profiles | auth.users, profiles | alle kontextbezogen | RLS-Test, Profile Hook | active / dormant / archived |
| Workspace Membership | Mehrfachzuordnung je Bereich | system / admin | Muss | workspaces, applications | workspace_members | staff, applicant, agency | RLS-Test, Cross-workspace UX | active / archived / banned |
| Application Management | operative Vorgänge je Bereich | staff | Muss | pipelines, applicants, assignments | applications | staff/admin/applicant scoped | Statusvalidierung, Audit | new → completed |
| Pipeline Configuration | Bereichslogik konfigurieren | admin | Muss | workspaces | pipelines, stage configs | admin | Config review, smoke test | enabled / draft |
| Auto Assignment | faire Mitarbeiterzuweisung | admin / teamlead | Soll | staff availability, skills | profiles, departments, assignments | staff/admin | Load-distribution test | assigned / fallback |
| Applicant Dashboard | nächster Schritt für Bewerber | product / UX | Muss | tasks, docs, invoices, messages | aggregated portal view | applicant | mobile test, content QA | contextual |
| Document Management | sichere Dokumente, Prüfstatus | staff / applicant ops | Muss | storage, applications | documents, document_requests | applicant/staff/agency scoped | upload, access, version, signed URL | missing / uploaded / review / approved / rejected |
| Internal/Public Comments | Rückfragen und interne Notizen trennen | staff | Muss | documents, applications | comments | staff/applicant scoped | visibility test | internal / public |
| Communications Hub | Nachrichten bündeln | staff | Muss | conversations, notifications | messages, conversations, provider webhooks | applicant/staff/agency | delivery test, permissions | queued / sent / delivered / read / failed |
| Notification Router | Kanalwahl nach Präferenzen | system / admin | Soll | templates, prefs, providers | notification_preferences, templates | applicant/staff | fallback test, override test | queued / sent / failed |
| Invoice Engine | Rechnungen erzeugen und speichern | finance/admin | Muss | applications, payments | invoices, templates, storage | staff/admin/applicant | PDF test, tax review | draft / open / paid / void / partially_paid |
| Payment Processing | Zahlungsstatus verarbeiten | finance/system | Muss | providers, webhooks | transactions, invoices | staff/admin/applicant scoped | webhook idempotency, refund test | unpaid / partial / paid / refunded |
| Appointment Integration | Termine synchronisieren | staff / admin | Soll | external calendar | appointments, webhook events | applicant/staff | sync test | booked / completed / cancelled |
| Task Management | interne und Applicant-Aufgaben | staff | Muss | status triggers | tasks | applicant/staff/admin | due-date, delegation test | open / done / blocked / overdue |
| Audit Log | unveränderliche Nachweise | security/admin | Muss | all critical events | audit_logs | restricted admin | append-only, export test | immutable |
| Automation Runs | Debugging und Nachvollziehbarkeit | admin/devops | Muss | workflow engine | automation_runs | admin/devops | failed-run inspection | success / failed / retrying |
| Webhook Event Store | Idempotenz und Retry | devops | Muss | stripe/twilio/etc. | webhook_events | system/admin | duplicate test | pending / processed / failed |
| Consent Tracking | DSGVO-/Opt-in-Nachweis | admin/legal | Muss | auth, forms | user_consents | applicant/admin | version test, export test | granted / revoked |
| Course Catalog | Kurse definieren | admin/education | Soll | LMS provider | courses, providers | applicant/staff/admin | visibility test | active / hidden |
| Course Enrollment | Kurszugriff steuern | admin/system | Soll | payment / manual release | course_enrollments | applicant/staff/admin | provisioning test | active / revoked / expired |
| Knowledge Base | Hilfe und FAQ | content/admin | Soll | CMS/content repo | articles, FAQs | public/applicant | SEO/content/legal review | draft / published |
| Agency Dashboard | Partnerfälle sichtbar machen | partner ops | Soll | agency roles, applications | filtered CRM | agency roles | RLS and visibility test | contextual |
| Affiliate Dashboard | Links, Leads, Provisionen | growth/admin | Soll | tracking, commissions | affiliate_clicks, commissions | affiliate | attribution test | active / pending payout |
| Reporting Dashboard | Kennzahlen und Steuerung | admin/management | Soll | event and ops data | analytics + snapshots | admin/management | metric validation | n/a |
| Legal Content Management | Impressum/Datenschutz/AGB aktuell halten | admin/legal | Muss | CMS + review | legal pages | admin | legal release gate | draft / approved / published |
| White-Label Basics | Branding pro Partner | admin | Kann | organizations branding | organizations.branding_config | agency/admin | scope test | mvp level 1 |
| OCR / AI Review | Dokumentvorprüfung | admin/ops | Kann | storage, AI provider | document analysis outputs | staff | false positive review | ai_verified / manual_review |
