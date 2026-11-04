# Technisches Pflichtenheft: Datenbank-Schema (ERD) & API-Architektur

**Projekt:** Studienkolleg Aachen (`studienkolleg-aachen.de` / `prev.studienkolleg-aachen.de` – migriert von `https://deinstudienkolleg.de`)
**Träger:** W2G Academy GmbH, Theaterstr. 30–32, 52062 Aachen (HRB 23610)
**Umfang:** Multi-Tenant PostgreSQL-16-Datenbankdesign, Entity-Relationship-Spezifikationen, Hybride Domain- & Legacy-Auth-Koexistenz (`deinstudienkolleg.de`), BigBlueButton (BBB) Cluster- & Webhook-Architektur, Cloud-Drive-Onlinespeicher-Integration (WebDAV/OCS), First-Party-Besuchertracking & Google/AI-SEO-Engine, Twenty CRM GraphQL-Synchronisation, REST-/FastAPI-Microservices sowie HL7 FHIR R4, Revolut, DATEV und XRechnung-Schnittstellen.
**Version:** 13.0 (Produktionsreife Architektur-Spezifikation)

---

## 1. Multi-Tenant Datenbank-Architektur & Hybride Domain-Topologie (PostgreSQL 16+)

Um den Eigenstandort Aachen, kooperative Partnerstandorte sowie externe White-Label-Pflegeschulen nach **ISO/IEC 27017**, **ISO/IEC 27018** und **Art. 28/32 DSGVO** strikt voneinander zu trennen, nutzt das System auf einer zentralen PostgreSQL-16-Cluster-Instanz eine **Schema-per-Tenant-Architektur** kombiniert mit zwei globalen Funktions-Schemata.

### 1.1 Hybride Domain-, Staging- & Legacy-Koexistenz-Architektur (Reverse Proxy / DNS)
Vor der Datenbank- und Applikationsschicht regelt ein hochverfügbarer Reverse-Proxy-Cluster (Nginx / Cloudflare Enterprise mit EU-Data-Localization) die Koexistenz mit dem Bestandsportal auf `https://deinstudienkolleg.de` sowie den Stufen-Rollout:

1.  **Bestandsportal `https://deinstudienkolleg.de` (Legacy Co-Existence):**
    *   Das bestehende Portal ab dem Login-Pfad (`/login`, `/portal/*`, `/dashboard/*` auf `deinstudienkolleg.de`) bleibt auf seiner bisherigen Infrastruktur für Bestandsstudierende vollständig aktiv.
    *   Sämtliche bisherigen Vertriebs- und Bewerbungsstrecken ab dem Bewerbungsformular (*"Apply Now" / "Bewerbung starten"*, `/apply`, `/booking`) auf `deinstudienkolleg.de` werden per `301/302`-Redirect bzw. API-Proxy auf die neue Bewerbungs-Engine umgeleitet.
2.  **Staging- & Abnahme-Umgebung (`https://prev.studienkolleg-aachen.de` & `https://prev.studienkollage-aachen.de`):**
    *   Vollwertige Vorproduktions-Umgebung (verbunden mit der Staging-Datenbank, dem Twenty-CRM-Staging-Workspace, dem BigBlueButton-Testcluster und dem Staging-Cloud-Drive) zur visuellen und funktionalen Abnahme aller Dashboards und Flows im Designsystem von `deinstudienkolleg.de`.
    *   Auslieferung mit HTTP-Header `X-Robots-Tag: noindex, nofollow`, bis die Freigabe für den produktiven Cut-over erfolgt.
3.  **Produktions-Umgebung (`https://studienkolleg-aachen.de` & `https://studienkollage-aachen.de`):**
    *   Nach finaler Abnahme wird `studienkolleg-aachen.de` als primäre kanonische Hauptdomain geschaltet; `studienkollage-aachen.de` leitet per `301 Moved Permanently` (inkl. Pfad- und Query-String-Erhalt für UTM/GCLID-Tracking) auf `https://studienkolleg-aachen.de` weiter.

### 1.2 Aufteilung der Datenbank-Schemata
1.  **Schema `landlord` (Master-System & SaaS-Orchestrator):**
    *   Speichert die Mandanten-Stammdaten (Tenants), Custom-Domain-Routings, Design-System-Tokens (abgeleitet aus `deinstudienkolleg.de`), SaaS-Abonnements, Add-on-Freischaltungen, BigBlueButton-Server-Zuweisungen, Cloud-Drive-Quotas, die CI/CD-Build-Queue für die *Dedicated School Apps* sowie die elektronisch gezeichneten Auftragsverarbeitungsverträge (AVV).
2.  **Schema `anabin_global` (Zentrale KMK-Spiegeldatenbank & Vektor-Store):**
    *   Ein mandantenübergreifendes, schreibgeschütztes Referenz-Schema, das durch den Python-Playwright-Scraper monatlich aktualisiert wird und zugleich die Datenbasis für die programmatischen SEO-/AI-SEO-Länder-Landingpages liefert.
    *   Nutzt die PostgreSQL-Extensions `pg_trgm` (Trigram-Index für Fuzzy-Matching) und `pgvector` (für semantische Embeddings der ausländischen Abschlusstitel).
3.  **Schema `job_portal_global` (Anonymisierter Healthcare-Recruiting-Pool & B2B-Arbeitgeber):**
    *   Speichert die B2B-Arbeitgeber (Krankenhäuser, Pflegeheime), deren Abonnements, Match-Requests, geplante BigBlueButton-Video-Interviews und die **zu $100\%$ anonymisierten Talent-Cards** der Kandidaten aus Pool 1 (Eigenstandort Aachen), Pool 2 (White-Label-Partnerschulen nach Double-Opt-In) und Pool 3 (externe Bewerber).
    *   Enthält keinerlei Klardaten (PII) der Schüler. Die Auflösung der Identität und die temporäre Freigabe der Cloud-Drive-Bewerbungsmappe erfolgen erst nach aktivem Match-Opt-In über einen kryptographisch signierten Pointer in das jeweilige Mandanten-Schema.
4.  **Schema `tenant_{uuid}` (Isoliertes Mandanten-Schema pro Standort/Schule):**
    *   Jeder Standort (z. B. `tenant_aachen_main`, `tenant_partner_koeln`, `tenant_pflegeschule_muenchen`) erhält ein eigenes Datenbank-Schema.
    *   Beinhaltet alle 40+ ERP-Module, Schüler-/Studierendendaten, Noten, Stundenpläne, BigBlueButton-Meetings & Präsenzprotokolle, Cloud-Drive-Mounts & Datei-ACLs, First-Party-Besuchertracking & Marketing-Attribution, das Wohnungsportal (DIN 277 / WoFlV / GEG), den PflBG-Rotationsplaner, das E-Logbook, die Fehlzeitenüberwachung und die GoBD-konforme Finanzbuchhaltung.

### 1.3 Datenbank-Erweiterungen & Sicherheitsmechanismen
*   **Erforderliche PostgreSQL-Extensions:** `uuid-ossp`, `pgcrypto`, `pg_trgm`, `vector` (pgvector), `btree_gist` (für zeitliche Überschneidungsprüfungen im Stundenplan-, BigBlueButton-Raum-, Klassenzimmer- und Mietvertragsmanagement via `EXCLUDE USING gist`).
*   **Field-Level Encryption (AES-256-GCM):** Besonders schützenswerte Attribute (Passnummern, Gesundheits-/Fehlzeitengründe nach § 13 PflBG, Bankverbindungen, OAuth-/Drive-Tokens, BBB-Shared-Secrets) werden auf Applikationsebene vor dem DB-Write verschlüsselt.
*   **GoBD-Unveränderbarkeit (Immutability Trigger):** Auf allen finanz-, anwesenheits- und prüfungsrelevanten Tabellen (`invoices`, `payments`, `ledger_entries`, `elogbook_entries`, `bbb_attendance_logs`, `exam_results`) verhindert ein PostgreSQL `BEFORE UPDATE OR DELETE`-Trigger das Überschreiben oder Löschen finalisierter Datensätze; Korrekturen sind ausschließlich über Storno-Buchungen (Gegenbuchungen) möglich.

---

## 2. Entity-Relationship-Spezifikation & Kerntabellen (DDL)

Im Folgenden sind die zentralen Entitäten und deren relationale Verknüpfungen für alle Systembereiche definiert. Sämtliche Tabellen verwenden `UUID` (v7, zeitlich sortierbar) als Primärschlüssel (`id`).

### 2.1 Schema `landlord` (SaaS-Steuerung, Design-System & App-Generator)

```sql
CREATE SCHEMA IF NOT EXISTS landlord;

CREATE TABLE landlord.tenants (
    id UUID PRIMARY KEY,
    slug VARCHAR(64) UNIQUE NOT NULL, -- z.B. 'aachen', 'pflegeschule-bayern'
    school_code VARCHAR(16) UNIQUE NOT NULL, -- Fest einprogrammiert in Dedicated Apps
    name VARCHAR(255) NOT NULL, -- z.B. 'Studienkolleg Aachen (W2G Academy GmbH)'
    tenant_type VARCHAR(32) NOT NULL CHECK (tenant_type IN ('OWN_CAMPUS', 'PARTNER_CAMPUS', 'WHITELABEL_NURSING')),
    db_schema VARCHAR(64) UNIQUE NOT NULL,
    s3_bucket_prefix VARCHAR(128) NOT NULL,
    drive_instance_root_path VARCHAR(255) NOT NULL, -- Wurzelverzeichnis im Enterprise Cloud-Drive
    drive_storage_quota_gb INTEGER NOT NULL DEFAULT 1000,
    bbb_scalelite_pool_id VARCHAR(128) NOT NULL, -- Zugewiesener BigBlueButton Server-Pool
    twenty_workspace_id UUID NOT NULL,
    staging_domain VARCHAR(255) UNIQUE, -- z.B. 'prev.studienkolleg-aachen.de'
    custom_domain VARCHAR(255) UNIQUE, -- z.B. 'studienkolleg-aachen.de'
    legacy_portal_login_url VARCHAR(512), -- z.B. 'https://deinstudienkolleg.de/login' für Bestandsnutzer
    -- Design-System Tokens (abgeleitet aus deinstudienkolleg.de & DIN EN ISO 9241)
    branding_config JSONB NOT NULL, -- Primär-/Sekundärfarben, Typografie, Dark-Mode-Palette, HRB 23610 Impressum
    supported_locales VARCHAR(8)[] NOT NULL DEFAULT ARRAY['de','en','ar','ru','uk','es','fr','it'],
    enabled_modules JSONB NOT NULL, -- Array der freigeschalteten ERP-Module & Add-ons
    global_pool_sharing BOOLEAN DEFAULT FALSE, -- 200 EUR Rabatt-Hebel für Pflegeschulen
    license_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (license_status IN ('TRIAL', 'ACTIVE', 'PAST_DUE', 'SUSPENDED')),
    avv_signed_at TIMESTAMPTZ,
    avv_eidas_document_id VARCHAR(128),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE landlord.app_builds (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES landlord.tenants(id) ON DELETE RESTRICT,
    app_target VARCHAR(32) NOT NULL CHECK (app_target IN ('STUDENT_PARENT', 'STAFF_TEACHER', 'PRAXISANLEITER')),
    package_id VARCHAR(128) NOT NULL, -- z.B. 'de.studienkolleg_aachen.student'
    app_name VARCHAR(64) NOT NULL,
    version_string VARCHAR(32) NOT NULL,
    firebase_project_id VARCHAR(128) NOT NULL,
    build_status VARCHAR(32) NOT NULL CHECK (build_status IN ('PENDING', 'BUILDING', 'IN_REVIEW', 'PUBLISHED', 'FAILED')),
    android_aab_s3_key TEXT,
    ios_ipa_s3_key TEXT,
    store_links JSONB,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

### 2.2 Schema `anabin_global` (Gescrapte KMK-Datenbank & Programmatic SEO Store)

```sql
CREATE SCHEMA IF NOT EXISTS anabin_global;

CREATE TABLE anabin_global.countries (
    id UUID PRIMARY KEY,
    iso_code CHAR(2) UNIQUE NOT NULL,
    name_de VARCHAR(128) NOT NULL,
    name_translations JSONB NOT NULL, -- Übersetzungen in DE, EN, AR, RU, UK, ES, FR, IT für SEO-Landingpages
    grading_scale_max NUMERIC(6,2) NOT NULL, -- N_max für Bayerische Formel
    grading_scale_min_pass NUMERIC(6,2) NOT NULL, -- N_min für Bayerische Formel
    aps_required BOOLEAN NOT NULL DEFAULT FALSE, -- TRUE für CN, IN, VN
    last_scraped_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE anabin_global.degrees (
    id UUID PRIMARY KEY,
    country_id UUID NOT NULL REFERENCES anabin_global.countries(id),
    anabin_external_id VARCHAR(64) UNIQUE NOT NULL,
    seo_slug VARCHAR(255) UNIQUE NOT NULL, -- Für Programmatic SEO & AI-SEO (z.B. 'marokko-baccalaureat-studienkolleg')
    title_original VARCHAR(512) NOT NULL,
    title_de VARCHAR(512) NOT NULL,
    title_embedding vector(1536), -- OpenAI/Mistral Embedding für semantischen Abgleich
    assessment_class VARCHAR(64) NOT NULL, -- 'Direkter Zugang', 'Feststellungsprüfung (Studienkolleg)', 'Kein Zugang'
    eligible_courses VARCHAR(32)[] NOT NULL, -- z.B. ARRAY['T', 'W', 'M', 'G']
    conditions_logic JSONB NOT NULL, -- Strukturierter Entscheidungsbaum (Mindestnoten, Pflichtfächer, Hochschulaufnahmeprüfung)
    ai_seo_summary_markdown TEXT, -- Vorberechneter Markdown-Block für /llms-full.txt und Schema.org FAQPage
    raw_html_hash CHAR(64) NOT NULL
);

CREATE INDEX idx_anabin_degrees_trgm ON anabin_global.degrees USING gin (title_original gin_trgm_ops, title_de gin_trgm_ops);
CREATE INDEX idx_anabin_degrees_vec ON anabin_global.degrees USING hnsw (title_embedding vector_cosine_ops);

CREATE TABLE anabin_global.institutions (
    id UUID PRIMARY KEY,
    country_id UUID NOT NULL REFERENCES anabin_global.countries(id),
    name_original VARCHAR(512) NOT NULL,
    city VARCHAR(128),
    recognition_status VARCHAR(16) NOT NULL CHECK (recognition_status IN ('H+', 'H-', 'H+/-'))
);
```

### 2.3 Schema `tenant_{uuid}` – Zulassung, Studierende, Sprachschule & Akademischer Kern

```sql
-- Benutzer & Rollen (RBAC) inkl. Cloud-Drive-Kopplung
CREATE TABLE users (
    id UUID PRIMARY KEY,
    twenty_contact_id UUID UNIQUE, -- Verknüpfung zur Single-Source-of-Truth in Twenty CRM
    legacy_deinstudienkolleg_id VARCHAR(64) UNIQUE, -- Optionale Referenz für migrierte Bestandsnutzer
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_whatsapp VARCHAR(32),
    password_hash VARCHAR(255) NOT NULL,
    role_type VARCHAR(32) NOT NULL CHECK (role_type IN ('ADMIN', 'STAFF', 'TEACHER', 'STUDENT', 'PARENT', 'PRAXISANLEITER', 'AGENCY_PARTNER')),
    two_factor_secret TEXT,
    preferred_locale VARCHAR(8) DEFAULT 'de' CHECK (preferred_locale IN ('de','en','ar','ru','uk','es','fr','it','zh','tr')),
    fcm_tokens TEXT[],
    revolut_viban VARCHAR(34) UNIQUE, -- Individuelle virtuelle IBAN für 100% automatisches Zahlungs-Matching
    drive_user_id VARCHAR(128) UNIQUE, -- Account-ID im integrierten Cloud-Drive (Nextcloud/OwnCloud)
    drive_home_folder_path VARCHAR(512), -- z.B. '/Users/2026_8492_El_Amrani_Youssef/'
    drive_quota_bytes BIGINT DEFAULT 10737418240, -- Standard 10 GB persönlicher Cloud-Speicher
    portal_restricted BOOLEAN DEFAULT FALSE, -- Automatische Sperre bei Zahlungsverzug > X Tage
    restriction_reason VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Bewerbungen & KI-OCR-Anabin-Pipeline (Ersetzt das Alt-Vertriebsportal auf deinstudienkolleg.de)
CREATE TABLE applications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    twenty_opportunity_id UUID NOT NULL,
    visitor_session_id UUID, -- Verknüpfung zur First-Party-Besuchertracking-Historie & GCLID
    agency_partner_id UUID REFERENCES users(id), -- Falls über B2B-Bildungsagentur eingereicht
    target_track VARCHAR(32) NOT NULL CHECK (target_track IN ('STK_T', 'STK_W', 'STK_M', 'STK_G', 'LANG_A1_C1', 'NURSING_PFLBG', 'CAREER_RECOGNITION')),
    drive_application_folder_id UUID, -- Referenz auf '01_Bewerbung_&_Anabin/' im Cloud-Drive
    extracted_ocr_data JSONB, -- Strukturiertes JSON aus Vision-LLM (Noten, Fächer, Schule, Passdaten)
    matched_anabin_degree_id UUID REFERENCES anabin_global.degrees(id),
    anabin_match_confidence NUMERIC(5,2), -- 0.00 bis 100.00 %
    calculated_german_grade NUMERIC(3,2), -- Berechnet nach Bayerischer Formel (1,00 bis 4,00)
    traffic_light_score VARCHAR(16) CHECK (traffic_light_score IN ('GREEN', 'YELLOW', 'RED')),
    scoring_audit_log JSONB NOT NULL DEFAULT '[]', -- Begründung der KI für Sachbearbeiter
    status VARCHAR(32) NOT NULL CHECK (status IN ('DRAFT', 'UNDER_REVIEW', 'ADMITTED_CONDITIONAL', 'ADMITTED_UNCONDITIONAL', 'ENROLLED', 'REJECTED')),
    welcome_pdf_drive_file_id UUID, -- Automatisch im Drive abgelegtes dynamisches Welcome-PDF
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Visa- & Aufenthaltstitel-Tracker
CREATE TABLE visa_trackings (
    id UUID PRIMARY KEY,
    student_user_id UUID NOT NULL REFERENCES users(id),
    document_type VARCHAR(32) NOT NULL CHECK (document_type IN ('ENTRY_VISA', 'FIKTIONSBESCHEINIGUNG', 'EAT_PERMIT')),
    embassy_location VARCHAR(128),
    blocked_account_provider VARCHAR(32) CHECK (blocked_account_provider IN ('FINTIBA', 'EXPATRIO', 'OTHER')),
    blocked_account_verified BOOLEAN DEFAULT FALSE,
    health_insurance_provider VARCHAR(64),
    health_insurance_verified BOOLEAN DEFAULT FALSE,
    valid_from DATE,
    valid_until DATE NOT NULL,
    alert_90d_sent_at TIMESTAMPTZ,
    alert_60d_sent_at TIMESTAMPTZ,
    alert_30d_sent_at TIMESTAMPTZ,
    drive_document_file_id UUID NOT NULL -- Direkt verknüpft mit '03_Visum_&_Behoerden/' im Drive
);

-- Adaptiver KI-Sprachtest (GER / CEFR) & Online-Prüfungen
CREATE TABLE language_assessments (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    cat_ability_theta NUMERIC(5,3) NOT NULL, -- Item-Response-Theory (IRT) Fähigkeitsparameter
    writing_prompt TEXT NOT NULL,
    writing_submission TEXT,
    speaking_audio_drive_file_id UUID,
    speaking_transcript TEXT,
    llm_evaluation_json JSONB, -- Detailbewertung nach GER-Deskriptoren (Grammatik, Kohärenz, Wortschatz, Aussprache)
    assigned_cefr_level VARCHAR(8) CHECK (assigned_cefr_level IN ('A1.1', 'A1.2', 'A2.1', 'A2.2', 'B1.1', 'B1.2', 'B2.1', 'B2.2', 'C1.1', 'C1.2')),
    completed_at TIMESTAMPTZ
);
```

### 2.4 Schema `tenant_{uuid}` – BigBlueButton (BBB) Virtual Classrooms & Cloud-Drive-Speicher

```sql
-- Cloud-Drive Ordner-Mounts & automatische Berechtigungs-Synchronisation (Nextcloud/OwnCloud Core)
CREATE TABLE drive_nodes (
    id UUID PRIMARY KEY,
    owner_user_id UUID REFERENCES users(id), -- NULL bei Kurs- oder System-Gruppenordnern
    course_cohort_id UUID, -- Falls Gruppenordner einer Klasse (T-Kurs, B2-Kurs, Pflegeklasse)
    parent_node_id UUID REFERENCES drive_nodes(id),
    node_type VARCHAR(16) NOT NULL CHECK (node_type IN ('FOLDER', 'FILE')),
    category_tag VARCHAR(64) NOT NULL CHECK (category_tag IN (
        'USER_ROOT', 'APP_ANABIN_DOCS', 'CONTRACTS_CERTIFICATES', 'VISA_AUTHORITIES',
        'HOUSING_LEASE', 'INVOICES_RECEIPTS', 'PERSONAL_WORKSPACE',
        'COURSE_SYLLABUS_SLIDES', 'BBB_RECORDINGS', 'ASSIGNMENT_DROPBOX', 'AZAV_AUDIT_SAFE'
    )),
    virtual_path TEXT NOT NULL, -- Pfad im Drive-UI
    s3_object_key TEXT, -- Physischer Speicherort im verschlüsselten S3/R2-Backend
    webdav_etag VARCHAR(128),
    mime_type VARCHAR(128),
    file_size_bytes BIGINT DEFAULT 0,
    sha256_checksum CHAR(64),
    is_locked_by_finance BOOLEAN DEFAULT FALSE, -- Greift bei Zahlungsverzug für Zertifikate
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE drive_share_permissions (
    id UUID PRIMARY KEY,
    drive_node_id UUID NOT NULL REFERENCES drive_nodes(id) ON DELETE CASCADE,
    grantee_type VARCHAR(32) NOT NULL CHECK (grantee_type IN ('USER', 'ROLE', 'COURSE_COHORT', 'B2B_EMPLOYER_TEMP', 'EXTERNAL_AUDITOR_AZAV')),
    grantee_id UUID NOT NULL,
    permission_level VARCHAR(16) NOT NULL CHECK (permission_level IN ('READ_ONLY', 'FILE_DROP_WRITE_ONLY', 'READ_WRITE', 'MANAGE')),
    expires_at TIMESTAMPTZ, -- Zwingend gesetzt bei 'B2B_EMPLOYER_TEMP' (max. 180 Tage nach AGG!)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- BigBlueButton (BBB) Virtuelle Räume (Unterricht, Studienberatung, Prüfungen & Job-Interviews)
CREATE TABLE bbb_meetings (
    id UUID PRIMARY KEY,
    bbb_internal_meeting_id VARCHAR(128) UNIQUE NOT NULL,
    room_context_type VARCHAR(32) NOT NULL CHECK (room_context_type IN (
        'TIMETABLE_LESSON',       -- Regulärer Unterricht (Studienkolleg, Sprachschule, Pflegeschule)
        'ADMISSION_CONSULTATION', -- 'Book Free Consultation' aus dem Website-Funnel
        'ORAL_EXAM_PROCTORING',   -- Mündliche Sprachprüfung / FSP-Simulation
        'JOB_PORTAL_INTERVIEW'    -- B2B Video-Interview zwischen Krankenhaus und Pflegekraft
    )),
    reference_context_id UUID NOT NULL, -- ID der Unterrichtsstunde, der Beratung oder des Match-Requests
    room_title VARCHAR(255) NOT NULL,
    moderator_pw VARCHAR(64) NOT NULL,
    attendee_pw VARCHAR(64) NOT NULL,
    pre_uploaded_slides_drive_node_id UUID REFERENCES drive_nodes(id), -- Automatisch aus dem Kurs-Drive geladenes PDF
    record_session BOOLEAN NOT NULL DEFAULT TRUE,
    auto_publish_to_drive_folder_id UUID REFERENCES drive_nodes(id), -- Zielordner '02_BigBlueButton_Aufzeichnungen/'
    scheduled_start_at TIMESTAMPTZ NOT NULL,
    scheduled_end_at TIMESTAMPTZ NOT NULL,
    actual_started_at TIMESTAMPTZ,
    actual_ended_at TIMESTAMPTZ,
    recording_mp4_drive_node_id UUID REFERENCES drive_nodes(id),
    ai_transcript_drive_node_id UUID REFERENCES drive_nodes(id),
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'LIVE', 'PROCESSING_RECORDING', 'COMPLETED', 'CANCELLED'))
);

-- Manipulationssicheres BigBlueButton-Anwesenheitsprotokoll (für AZAV-, PflBG- & Visa-Compliance)
CREATE TABLE bbb_attendance_logs (
    id UUID PRIMARY KEY,
    bbb_meeting_id UUID NOT NULL REFERENCES bbb_meetings(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role_in_meeting VARCHAR(16) NOT NULL CHECK (role_in_meeting IN ('MODERATOR', 'VIEWER')),
    first_joined_at TIMESTAMPTZ NOT NULL,
    last_left_at TIMESTAMPTZ,
    Join_leave_events_json JSONB NOT NULL DEFAULT '[]', -- Exakte Liste aller Join/Leave-Zeitstempel via BBB-Webhook
    net_online_minutes NUMERIC(6,2) NOT NULL DEFAULT 0.00,
    required_lesson_minutes NUMERIC(6,2) NOT NULL,
    attendance_percentage NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN required_lesson_minutes > 0 THEN LEAST(100.00, ROUND((net_online_minutes / required_lesson_minutes) * 100.0, 2)) ELSE 100.00 END
    ) STORED,
    camera_active_seconds INTEGER DEFAULT 0,
    polls_answered_count SMALLINT DEFAULT 0,
    compliance_status VARCHAR(32) NOT NULL CHECK (compliance_status IN ('PRESENT_VERIFIED', 'PARTIAL_ABSENCE', 'ABSENT_UNEXCUSED')),
    synced_to_absence_monitor BOOLEAN DEFAULT FALSE
);
```

### 2.5 Schema `tenant_{uuid}` – Wohnungsportal (DIN 277, WoFlV & GEG)

```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    street_address VARCHAR(255) NOT NULL,
    postal_code VARCHAR(16) NOT NULL,
    city VARCHAR(128) NOT NULL DEFAULT 'Aachen',
    construction_year SMALLINT NOT NULL,
    -- Pflichtangaben nach § 87 Gebäudeenergiegesetz (GEG)
    geg_certificate_type VARCHAR(32) NOT NULL CHECK (geg_certificate_type IN ('BEDARFSAUSWEIS', 'VERBRAUCHSAUSWEIS')),
    geg_final_energy_value NUMERIC(6,2) NOT NULL, -- in kWh/(m²·a)
    geg_primary_energy_source VARCHAR(64) NOT NULL, -- z.B. 'Fernwärme', 'Erdgas', 'Wärmepumpe'
    geg_efficiency_class VARCHAR(4) NOT NULL CHECK (geg_efficiency_class IN ('A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')),
    geg_certificate_drive_node_id UUID NOT NULL REFERENCES drive_nodes(id)
);

CREATE TABLE housing_rooms (
    id UUID PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES properties(id),
    unit_number VARCHAR(32) NOT NULL,
    floor_level SMALLINT NOT NULL,
    room_type VARCHAR(32) NOT NULL CHECK (room_type IN ('SINGLE_APARTMENT', 'WG_ROOM', 'SHARED_TWIN')),
    -- Strikte Flächenberechnung nach DIN 277:2021-08 (in m²)
    din277_bgf NUMERIC(6,2) NOT NULL, -- Brutto-Grundfläche
    din277_kgf NUMERIC(6,2) NOT NULL, -- Konstruktions-Grundfläche
    din277_nrf NUMERIC(6,2) GENERATED ALWAYS AS (din277_bgf - din277_kgf) STORED, -- Netto-Raumfläche
    din277_nuf NUMERIC(6,2) NOT NULL, -- Nutzungsfläche
    din277_tf NUMERIC(6,2) NOT NULL DEFAULT 0, -- Technikfläche
    din277_vf NUMERIC(6,2) NOT NULL DEFAULT 0, -- Verkehrsfläche
    -- Wohnflächenberechnung nach WoFlV (in m²)
    woflv_area_full_2m NUMERIC(6,2) NOT NULL, -- Lichte Höhe >= 2,00 m (100 % Anrechnung)
    woflv_area_slope_1m_2m NUMERIC(6,2) NOT NULL DEFAULT 0, -- Lichte Höhe 1,00 m bis < 2,00 m (50 % Anrechnung)
    woflv_area_under_1m NUMERIC(6,2) NOT NULL DEFAULT 0, -- Lichte Höhe < 1,00 m (0 % Anrechnung)
    woflv_balcony_raw NUMERIC(6,2) NOT NULL DEFAULT 0, -- Balkon/Loggia Grundfläche (25 % Anrechnung)
    woflv_total_chargeable_area NUMERIC(6,2) GENERATED ALWAYS AS (
        ROUND(woflv_area_full_2m + (woflv_area_slope_1m_2m * 0.50) + (woflv_balcony_raw * 0.25), 2)
    ) STORED,
    cold_rent_cents INTEGER NOT NULL,
    utility_prepayment_cents INTEGER NOT NULL,
    deposit_cents INTEGER NOT NULL, -- Maximal 3 Kaltmieten nach § 551 BGB
    ai_expose_texts JSONB NOT NULL, -- Mehrsprachige Exposés in allen 8+ Sprachen {'de': '...', 'en': '...', 'ar': '...', 'ru': '...'}
    media_gallery JSONB NOT NULL, -- Array aus Originalfotos, 2D/3D-Grundrissen, Dormitory-Tour-Reels & KI-Virtual-Staging-Bildern
    is_published BOOLEAN DEFAULT FALSE,
    CONSTRAINT chk_geg_complete CHECK (geg_final_energy_value > 0)
);

CREATE TABLE lease_contracts (
    id UUID PRIMARY KEY,
    room_id UUID NOT NULL REFERENCES housing_rooms(id),
    tenant_user_id UUID NOT NULL REFERENCES users(id),
    application_id UUID NOT NULL REFERENCES applications(id), -- Gated Booking: Zwingende Verknüpfung zur Zulassung
    lease_period DATERANGE NOT NULL,
    deposit_type VARCHAR(32) NOT NULL CHECK (deposit_type IN ('REVOLUT_ESCROW', 'KAUTIONSFREI_BOND', 'SWK_BOND')),
    revolut_escrow_account_id VARCHAR(128),
    bond_certificate_number VARCHAR(128),
    bond_verified BOOLEAN DEFAULT FALSE,
    liability_insurance_provider VARCHAR(64), -- z.B. 'Getsafe'
    signed_contract_drive_node_id UUID REFERENCES drive_nodes(id), -- Automatisch im Drive-Ordner '04_Wohnen_&_Mietvertrag/'
    handover_protocol_drive_node_id UUID REFERENCES drive_nodes(id),
    eidas_envelope_id VARCHAR(128) NOT NULL,
    signed_by_tenant_at TIMESTAMPTZ,
    signed_by_landlord_at TIMESTAMPTZ,
    smart_lock_pin_released BOOLEAN DEFAULT FALSE,
    status VARCHAR(32) NOT NULL CHECK (status IN ('PENDING_SIGNATURE', 'PENDING_PAYMENT_INSURANCE', 'ACTIVE', 'TERMINATED')),
    -- Verhindert Doppelvermietung desselben Zimmers im selben Zeitraum auf Datenbankebene
    EXCLUDE USING gist (room_id WITH =, lease_period WITH &&) WHERE (status IN ('PENDING_SIGNATURE', 'PENDING_PAYMENT_INSURANCE', 'ACTIVE'))
);
```

### 2.6 Schema `tenant_{uuid}` – Digitale Pflegeschule (PflBG, PflAPrV & AZAV)

```sql
-- Kooperationskrankenhäuser & Praxisträger (Ausbildungsverbund)
CREATE TABLE nursing_cooperations (
    id UUID PRIMARY KEY,
    twenty_company_id UUID NOT NULL,
    institution_name VARCHAR(255) NOT NULL,
    care_sector VARCHAR(32) NOT NULL CHECK (care_sector IN ('ACUTE_HOSPITAL', 'LONG_TERM_CARE', 'AMBULATORY_CARE', 'PEDIATRICS', 'PSYCHIATRY')),
    fhir_base_url VARCHAR(512), -- HL7 FHIR R4 Endpunkt des KIS (z.B. SAP IS-H / Dedalus ORBIS)
    fhir_client_credentials_encrypted TEXT,
    shared_drive_folder_id UUID REFERENCES drive_nodes(id), -- Geteilter Drive-Ordner für Einsatzpläne mit der PDL
    station_capacities JSONB NOT NULL -- Kapazitätsmatrix pro Station und Zeitraum
);

-- Algorithmischer Praxis-Rotationsplaner nach Anlage 7 PflAPrV
CREATE TABLE nursing_rotations (
    id UUID PRIMARY KEY,
    student_user_id UUID NOT NULL REFERENCES users(id),
    cooperation_id UUID NOT NULL REFERENCES nursing_cooperations(id),
    deployment_category VARCHAR(32) NOT NULL CHECK (deployment_category IN (
        'ORIENTATION_400H',          -- 400 Std. Orientierungseinsatz
        'ACUTE_INPATIENT_400H',      -- 400 Std. Stationäre Akutpflege
        'LONG_TERM_INPATIENT_400H',  -- 400 Std. Stationäre Langzeitpflege
        'AMBULATORY_400H',           -- 400 Std. Ambulante Akut-/Langzeitpflege
        'PEDIATRICS_120H',           -- 120 Std. Pädiatrische Versorgung
        'PSYCHIATRY_120H',           -- 120 Std. Psychiatrische Versorgung
        'SPECIALIZATION_500H',       -- 500 Std. Vertiefungseinsatz
        'ELECTIVE_HOURS'             -- Frei verteilbare Stunden (Gesamt >= 2.500 Std.)
    )),
    station_name VARCHAR(128) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    planned_total_hours SMALLINT NOT NULL,
    planned_guidance_hours SMALLINT NOT NULL, -- Pflicht: Mindestens 10 % Praxisanleitung nach § 4 PflAPrV
    completed_total_hours NUMERIC(6,2) DEFAULT 0,
    completed_guidance_hours NUMERIC(6,2) DEFAULT 0,
    CONSTRAINT chk_10_percent_guidance CHECK (planned_guidance_hours >= (planned_total_hours * 0.10))
);

-- Digitaler Ausbildungsnachweis (E-Logbook) & Mobile QR-Abzeichnung
CREATE TABLE elogbook_entries (
    id UUID PRIMARY KEY,
    rotation_id UUID NOT NULL REFERENCES nursing_rotations(id),
    student_user_id UUID NOT NULL REFERENCES users(id),
    praxisanleiter_user_id UUID REFERENCES users(id),
    shift_date DATE NOT NULL,
    logged_work_hours NUMERIC(4,2) NOT NULL,
    logged_guidance_hours NUMERIC(4,2) NOT NULL DEFAULT 0,
    guidance_topic VARCHAR(255), -- z.B. 'Strukturierte Praxisanleitung: Aseptischer Verbandswechsel'
    pflaprv_competencies JSONB NOT NULL, -- Kompetenzbereiche I bis V nach Anlage 2 PflAPrV
    qr_handshake_token VARCHAR(128) UNIQUE,
    qr_token_expires_at TIMESTAMPTZ,
    instructor_rating SMALLINT CHECK (instructor_rating BETWEEN 1 AND 5),
    eidas_signature_hash CHAR(64), -- Manipulationssichere Signatur des Praxisanleiters vom Smartphone
    signed_pdf_drive_node_id UUID REFERENCES drive_nodes(id), -- Sofortige Ablage im Cloud-Drive des Schülers
    signed_at TIMESTAMPTZ,
    gps_coordinates POINT -- Optionaler Nachweis des Klinikstandorts
);

-- Gesetzliches Fehlzeiten-Frühwarnsystem (§ 13 PflBG & AZAV inkl. BigBlueButton-Zeiten)
CREATE TABLE nursing_absence_monitors (
    student_user_id UUID PRIMARY KEY REFERENCES users(id),
    azav_voucher_number VARCHAR(64), -- Bildungsgutschein-Nr. der Agentur für Arbeit / Jobcenter
    jobcenter_agency_code VARCHAR(32),
    theory_hours_missed NUMERIC(6,2) NOT NULL DEFAULT 0, -- Inkl. Fehlminuten aus bbb_attendance_logs
    theory_hours_max_allowed NUMERIC(6,2) NOT NULL DEFAULT 210.00, -- 10 % von 2.100 Std.
    practice_hours_missed NUMERIC(6,2) NOT NULL DEFAULT 0,
    practice_hours_max_allowed NUMERIC(6,2) NOT NULL DEFAULT 250.00, -- 10 % von 2.500 Std.
    escalation_stage SMALLINT NOT NULL DEFAULT 0 CHECK (escalation_stage IN (0, 1, 2, 3)), -- 0=OK, 1=5%, 2=7.5%, 3=9% (AZAV-Kritisch)
    last_jobcenter_report_drive_node_id UUID REFERENCES drive_nodes(id),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.7 Schema `job_portal_global` – Reverse Recruiting, Anonymes Matching & AGG-Compliance

```sql
CREATE SCHEMA IF NOT EXISTS job_portal_global;

-- Anonymisierte Talent-Cards (Pools 1, 2 und 3) – Strikte Trennung nach Art. 7 Abs. 4 DSGVO
CREATE TABLE job_portal_global.anonymous_talent_profiles (
    id UUID PRIMARY KEY,
    public_candidate_code VARCHAR(16) UNIQUE NOT NULL, -- z.B. '#A8492'
    source_pool VARCHAR(32) NOT NULL CHECK (source_pool IN ('POOL_1_AACHEN', 'POOL_2_WHITELABEL', 'POOL_3_EXTERNAL')),
    origin_tenant_id UUID REFERENCES landlord.tenants(id), -- NULL bei Pool 3
    encrypted_origin_user_pointer TEXT NOT NULL, -- AES-256 verschlüsselte User-ID (nur bei Match auflösbar)
    qualification_type VARCHAR(64) NOT NULL, -- 'Pflegefachkraft (Generalistik)', 'Intensivpflege', 'Anerkennungspraktikant'
    expected_exam_date DATE NOT NULL,
    current_practical_grade NUMERIC(3,2),
    completed_specializations VARCHAR(64)[], -- z.B. ARRAY['Pädiatrie', 'Notaufnahme', 'Akutpflege']
    verified_cefr_level VARCHAR(8) NOT NULL,
    desired_regions_zip_prefixes VARCHAR(8)[],
    max_commute_km SMALLINT DEFAULT 30,
    shift_preferences JSONB NOT NULL, -- {'three_shift': true, 'night_only': false, 'part_time': false}
    blacklisted_employer_ids UUID[] DEFAULT '{}', -- Eigener Ausbildungsbetrieb wird hier blockiert!
    double_opt_in_confirmed_at TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- B2B-Arbeitgeber (Krankenhäuser & Pflegeheime)
CREATE TABLE job_portal_global.b2b_employers (
    id UUID PRIMARY KEY,
    twenty_company_id UUID UNIQUE NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(32) NOT NULL CHECK (subscription_tier IN ('STARTER_399', 'PRO_999', 'ENTERPRISE_1899')),
    pay_per_hire_fee_cents INTEGER NOT NULL DEFAULT 250000, -- 2.500 EUR Standard / 1.500 EUR Enterprise
    monthly_match_quota SMALLINT NOT NULL, -- 0 (Starter), 25 (Pro), 9999 (Enterprise)
    used_matches_current_month SMALLINT NOT NULL DEFAULT 0,
    early_bird_access_enabled BOOLEAN GENERATED ALWAYS AS (subscription_tier = 'ENTERPRISE_1899') STORED,
    collective_agreement VARCHAR(128), -- z.B. 'TVöD-P', 'AVR Caritas'
    employer_pitch_profile JSONB NOT NULL, -- Gehaltsbänder, Startprämien, Kinderbetreuung, Stationsbilder
    avv_signed_at TIMESTAMPTZ NOT NULL
);

-- Match-Requests, BigBlueButton-Interviews & Automatisiertes 180-Tage-AGG-Löschkonzept
CREATE TABLE job_portal_global.match_requests (
    id UUID PRIMARY KEY,
    employer_id UUID NOT NULL REFERENCES job_portal_global.b2b_employers(id),
    talent_profile_id UUID NOT NULL REFERENCES job_portal_global.anonymous_talent_profiles(id),
    offered_department VARCHAR(128) NOT NULL,
    offered_gross_salary_monthly_cents INTEGER NOT NULL,
    offered_signing_bonus_cents INTEGER DEFAULT 0,
    custom_pitch_message TEXT NOT NULL,
    status VARCHAR(32) NOT NULL CHECK (status IN ('PENDING_CANDIDATE', 'CANDIDATE_DECLINED', 'MATCHED_OPEN', 'INTERVIEW_SCHEDULED_BBB', 'EMPLOYER_REJECTED', 'HIRED', 'AGG_PURGED')),
    candidate_responded_at TIMESTAMPTZ,
    unmasked_pii_snapshot JSONB, -- Wird ERST bei Status 'MATCHED_OPEN' befüllt und bei 'AGG_PURGED' auf NULL gesetzt!
    temp_drive_share_permission_id UUID, -- Temporärer Read-Only-Zugriff auf die Zeugnismappe im Cloud-Drive
    bbb_interview_meeting_id UUID, -- Integrierter BigBlueButton Video-Interview-Raum
    employer_notes TEXT, -- Wird bei 'AGG_PURGED' unwiderruflich gelöscht
    rejection_or_expiry_date TIMESTAMPTZ,
    agg_purge_scheduled_at TIMESTAMPTZ, -- Exakt rejection_or_expiry_date + INTERVAL '180 days' (§ 15 Abs. 4 AGG)
    agg_purged_at TIMESTAMPTZ,
    hire_invoice_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 2.8 Schema `tenant_{uuid}` – First-Party-Besuchertracking, Google Attribution, SEO & Finanzen

```sql
-- Vollwertiges First-Party-Besuchertracking & Multi-Touch-Attribution (Synchronisiert mit Twenty CRM & Google Ads)
CREATE TABLE web_visitor_sessions (
    id UUID PRIMARY KEY,
    visitor_fingerprint_hash CHAR(64) NOT NULL, -- Anonymisierter First-Party-Hash
    resolved_user_id UUID REFERENCES users(id), -- Sobald Bewerber Formular absendet (Identity Resolution)
    twenty_lead_id UUID,
    entry_domain VARCHAR(128) NOT NULL, -- z.B. 'prev.studienkolleg-aachen.de' oder 'studienkolleg-aachen.de'
    entry_url TEXT NOT NULL,
    referrer_url TEXT,
    country_iso CHAR(2),
    browser_locale VARCHAR(16),
    device_type VARCHAR(16) CHECK (device_type IN ('MOBILE', 'TABLET', 'DESKTOP')),
    -- Google & Kampagnen-Parameter
    gclid VARCHAR(255), -- Google Click ID für Offline-Conversion-Upload zu Google Ads
    gbraid VARCHAR(255),
    wbraid VARCHAR(255),
    fbclid VARCHAR(255),
    utm_source VARCHAR(128),
    utm_medium VARCHAR(128),
    utm_campaign VARCHAR(128),
    utm_term VARCHAR(128),
    utm_content VARCHAR(128),
    agency_ref_code VARCHAR(64),
    -- Google Consent Mode v2 Status nach TDDDG / DSGVO
    consent_mode_v2_state JSONB NOT NULL DEFAULT '{"ad_storage":"denied","analytics_storage":"denied","ad_user_data":"denied","ad_personalization":"denied"}',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE web_visitor_events (
    id UUID PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES web_visitor_sessions(id) ON DELETE CASCADE,
    event_name VARCHAR(64) NOT NULL, -- z.B. 'page_view', 'reel_video_watched', 'apply_step_2_completed', 'form_field_hesitation'
    page_path VARCHAR(512) NOT NULL,
    event_payload JSONB NOT NULL DEFAULT '{}', -- Scroll-Tiefe, geklicktes Element, Verweildauer in Sekunden
    forwarded_to_sgtm BOOLEAN DEFAULT FALSE, -- Server-Side Google Tag Manager Sync-Status
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_visitor_sessions_user ON web_visitor_sessions(resolved_user_id);
CREATE INDEX idx_visitor_sessions_gclid ON web_visitor_sessions(gclid) WHERE gclid IS NOT NULL;

-- GoBD-konforme Rechnungen (XRechnung 3.0 / ZUGFeRD 2.2) & Affiliate-Conversions
CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    invoice_number VARCHAR(64) UNIQUE NOT NULL, -- Fortlaufend, lückenlos nach GoBD
    debtor_type VARCHAR(32) NOT NULL CHECK (debtor_type IN ('STUDENT_B2C', 'AUSGLEICHSFONDS_B2G', 'JOBCENTER_AZAV_B2G', 'HOSPITAL_B2B', 'EMPLOYER_HIRE_FEE_B2B')),
    debtor_user_id UUID REFERENCES users(id),
    leitweg_id VARCHAR(64), -- Pflichtfeld für Behörden/Ausgleichsfonds (XRechnung B2G)
    net_amount_cents INTEGER NOT NULL,
    vat_rate NUMERIC(4,2) NOT NULL DEFAULT 0.00, -- 0% nach § 4 Nr. 21 UStG (Bildung) oder 19% (Recruiting/SaaS)
    gross_amount_cents INTEGER NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'EUR',
    due_date DATE NOT NULL,
    xrechnung_xml_drive_node_id UUID NOT NULL REFERENCES drive_nodes(id), -- EN 16931 / XRechnung 3.0 XML im Drive
    zugferd_pdf_drive_node_id UUID NOT NULL REFERENCES drive_nodes(id), -- ZUGFeRD 2.2 PDF/A-3 nach DIN 5008 im Drive
    gobd_prev_hash CHAR(64) NOT NULL, -- Blockchain-artige Verkettung aller Rechnungen zur Revisionssicherheit
    gobd_current_hash CHAR(64) NOT NULL,
    payment_status VARCHAR(32) NOT NULL CHECK (payment_status IN ('ISSUED', 'SWIFT_ANNOUNCED_AI_VERIFIED', 'PARTIALLY_PAID', 'PAID', 'OVERDUE', 'CANCELLED_BY_STORNO')),
    google_ads_offline_conversion_synced_at TIMESTAMPTZ, -- Meldet echten Zahlungseingang via GCLID an Google Ads
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE affiliate_conversions (
    id UUID PRIMARY KEY,
    student_user_id UUID NOT NULL REFERENCES users(id),
    sub_id_token VARCHAR(64) UNIQUE NOT NULL, -- Eingebettet in QR-Codes des dynamischen Welcome-PDFs
    partner_service VARCHAR(32) NOT NULL CHECK (partner_service IN ('FINTIBA', 'EXPATRIO', 'CARE_CONCEPT', 'MAWISTA', 'FEATHER', 'KAUTIONSFREI', 'SWK_BANK', 'GETSAFE', 'REVOLUT', 'FRAENK')),
    clicked_at TIMESTAMPTZ,
    converted_at TIMESTAMPTZ,
    expected_commission_cents INTEGER,
    commission_status VARCHAR(32) DEFAULT 'CLICKED' CHECK (commission_status IN ('CLICKED', 'LEAD_REGISTERED', 'APPROVED', 'PAID_OUT'))
);
```

---

## 3. Twenty CRM Datenmodell & Bidirektionale Synchronisation

**Twenty CRM** agiert als führendes System (Single-Source-of-Truth) für sämtliche Kontakt-, Besuchertracking-, Pipeline- und Kommunikationsprozesse. Die Synchronisation zwischen Twenty CRM, dem Laravel Core-ERP, dem BigBlueButton-Cluster und dem Cloud-Drive erfolgt über **GraphQL-Mutationen** und **signierte Webhooks (HMAC-SHA256)** über einen asynchronen Redis/RabbitMQ-Message-Broker.

### 3.1 Custom Objects & Pipelines in Twenty CRM
1.  **Object `StudentLifecycle` (B2C – ersetzt das Alt-Vertriebsportal auf `deinstudienkolleg.de`):**
    *   *Pipeline-Stages:* `00_Web_Visitor_Tracked` -> `01_Consultation_Booked_BBB` -> `02_Docs_Uploaded_To_Drive` -> `03_AI_Anabin_Green` (oder `03b_Manual_Review_Yellow`) -> `04_Offer_Sent` -> `05_Deposit_Paid` -> `06_Visa_Granted` -> `07_Housing_Booked` -> `08_Enrolled_Active` -> `09_Exam_Candidate` -> `10_Alumni`.
2.  **Object `LanguageUpsellPipeline` (B2C):**
    *   Überwacht Sprachschüler (A1–C1). Erreicht das Feld `passed_level` den Wert `B1` oder `B2`, triggert Twenty CRM vollautomatisch die Umwandlungs-Kampagne für den T-/W-/M-/G-Kurs des Studienkollegs oder die Pflegeschule Aachen.
3.  **Object `B2B_HealthcareEmployer` (B2B):**
    *   Vererbt den Vertragsstatus an `job_portal_global.b2b_employers`. Steuert das Recruiting-Pipeline-Board (`Match_Sent` -> `Candidate_Accepted` -> `BBB_Interview_Scheduled` -> `Contract_Signed_2500EUR_Trigger`).

### 3.2 Deterministische Webhook-Event-Matrix (Twenty CRM <-> Laravel ERP <-> BBB <-> Drive)

| Event-Name | Richtung | Auslösender Trigger | Deterministische Systemaktion im Zielsystem |
| :--- | :--- | :--- | :--- |
| `visitor.lead.identified` | Next.js Tracking -> Laravel -> Twenty CRM | Besucher sendet Bewerbungs- oder Beratungsformular ab | Verknüpft alle bisherigen anonymen `web_visitor_events` (inkl. `gclid`, UTM, angesehene Kurse/Videos) mit dem neuen Lead in Twenty CRM und provisioniert den persönlichen **Cloud-Drive-Tresor**. |
| `application.ocr_completed` | FastAPI -> Twenty CRM & ERP | Bewerber lädt Reisepass & Zeugnis ins Drive hoch | Schreibt extrahierte JSON-Daten, Anabin-Match-Score ($0-100\%$), umgerechnete deutsche Note und Ampelstatus (`GREEN`/`YELLOW`/`RED`) per GraphQL in Twenty CRM. |
| `crm.stage.admitted` | Twenty CRM -> Laravel ERP & Cloud-Drive | Stage wechselt auf `04_Offer_Sent` | 1. Generiert Zulassungsbescheid nach DIN 5008 und legt ihn in `02_Vertraege_&_Bescheide/` im Drive ab.<br>2. Generiert personalisiertes **Welcome-PDF** inkl. Sub-ID-QR-Codes.<br>3. Schaltet **Gated Booking** im Wohnungsportal frei.<br>4. Erstellt 1. Gebührenrechnung + Revolut vIBAN. |
| `revolut.payment.settled` | Revolut API -> Laravel ERP -> Twenty CRM & Google Ads | Geldeingang auf virtueller IBAN des Schülers/Mieters | 1. Gleicht offenen Posten im ERP ab und entsperrt Cloud-Drive-Zertifikate (`portal_restricted = FALSE`).<br>2. Setzt Stage in Twenty CRM auf `05_Deposit_Paid`.<br>3. Meldet den Zahlungseingang inkl. `GCLID` als **Offline-Conversion** an die Google Ads API. |
| `bbb.meeting.ended` | BigBlueButton -> Laravel ERP -> Cloud-Drive | Online-Unterricht oder Vorlesung in BBB wird beendet | 1. Berechnet die Netto-Anwesenheitsminuten aller Teilnehmer (`bbb_attendance_logs`) und aktualisiert das Klassenbuch / AZAV-Fehlzeitenkonto.<br>2. Verschiebt die gerenderte MP4-Aufzeichnung + KI-Transkript vollautomatisch in den Kurs-Ordner `02_BigBlueButton_Aufzeichnungen/` im Cloud-Drive. |
| `nursing.absence.threshold` | Laravel ERP -> Twenty CRM | Fehlzeiten erreichen $5\%$, $7,5\%$ oder $9\%$ (§ 13 PflBG) | Erstellt hochpriorisierte Task in Twenty CRM; versendet bei $9\%$ automatisch die AZAV-Veränderungsmeldung an die Agentur für Arbeit und legt sie im `/AZAV_Audit_Safe/` im Drive ab. |
| `jobportal.contract.signed` | Twenty CRM -> Laravel ERP | Klinik markiert gematchten Kandidaten als `Contract_Signed` | Erstellt sofort die GoBD-konforme Erfolgsrechnung über **$2.500\text{ EUR}$** (bzw. $1.500\text{ EUR}$) im Format **XRechnung 3.0 / ZUGFeRD 2.2** ins Drive und zieht den Betrag via Revolut SEPA-Firmenlastschrift ein. |

---

## 4. API-Architektur & Endpunkt-Spezifikation

Die gesamte Kommunikation zwischen den 8 Frontends (Next.js Web-Portale im Designsystem von `deinstudienkolleg.de`, Flutter Mobile Apps), dem Laravel-13-Kern, dem BigBlueButton-Cluster, dem Cloud-Drive und den Python-KI-Microservices ist strikt typisiert (OpenAPI 3.1 / JSON Schema).

### 4.1 Authentifizierung, Sicherheit & Tenant-Resolution
*   **Headers:** Jeder API-Request an das ERP muss zwingend folgende Header enthalten:
    *   `Authorization: Bearer {Sanctum_JWT_Token}`
    *   `X-Tenant-ID: {tenant_slug}` (wird bei *Dedicated School Apps* fest aus dem kompilierten App-Binary gesendet).
    *   `X-Idempotency-Key: {UUIDv4}` (Pflicht bei allen `POST`/`PUT`-Requests im Bereich Zahlungen, Prüfungsabgaben und E-Logbook-Signatur).
*   **Cloud-Drive & Pre-Signed Storage Streams:** Das Backend gibt niemals ungeschützte statische Datei-URLs zurück. Für jeden Dokumentenabruf aus dem Cloud-Drive prüft das ERP die Berechtigung in `drive_share_permissions` sowie den Zahlungsstatus (`is_locked_by_finance = FALSE`) und generiert eine auf $300\text{ Sekunden}$ befristete, kryptographisch signierte S3/R2- oder WebDAV-Stream-URL.

### 4.2 Core-ERP REST API Endpunkte (Auszug Schlüsselprozesse)

#### A. BigBlueButton (BBB) Live-Unterricht & Automatischer Drive-Folien-Upload
1.  **Dozent startet Live-Unterricht oder Beratungsgespräch:**
    *   `POST /api/v1/bbb/meetings/{meeting_id}/start`
    *   *System-Ablauf im Backend:*
        1.  Prüft, ob im verknüpften Kurs-Drive-Ordner (`01_Skripte_&_Vorlesungsfolien/`) eine Präsentation für diese Unterrichtseinheit hinterlegt ist, und übergibt deren Pre-Signed-URL im XML-Body des BigBlueButton-API-Calls (`create`).
        2.  Registriert den Webhook-Callback `/webhooks/bbb/events?meeting_id={id}` mittels `bbb-webhooks` am Scalelite-Load-Balancer.
        3.  Gibt die signierte Moderator-Join-URL für das eingebettete BBB-HTML5-Client-Interface zurück und signalisiert allen Kursteilnehmern per WebSocket (`Laravel Reverb`), dass der Raum live ist.
2.  **BigBlueButton Event- & Recording-Webhook (Server-to-Server):**
    *   `POST /webhooks/bbb/events`
    *   Verarbeitet `user-joined`, `user-left`, `poll-responded` und `rap-publish-ended` (Recording Ready), schreibt die sekundengenauen Präsenzzeiten in `bbb_attendance_logs` und synchronisiert die MP4-Aufzeichnung in das Cloud-Drive.

#### B. Cloud-Drive Onlinespeicher API (WebDAV / REST Bridge)
*   `GET /api/v1/drive/nodes?parent_id={uuid}`
    *   Liefert den kompletten Ordnerbaum und die Dateiliste des eingeloggten Studierenden, Dozenten oder Admins gemäß den in `drive_share_permissions` hinterlegten ACLs.
*   `POST /api/v1/drive/nodes/{folder_id}/upload-url`
    *   Generiert eine direkte, mehrteilige S3/WebDAV-Upload-URL für große Dateien (z. B. Hausaufgaben, Zeugnis-Scans oder Vorlesungsvideos) und triggert bei Upload in den Ordner `01_Bewerbung_&_Anabin/` vollautomatisch die KI-OCR-Anabin-Pipeline.
*   `POST /api/v1/drive/nodes/{file_id}/collabora-session`
    *   Generiert ein WOPI-Access-Token zum gemeinsamen Bearbeiten von Dokumenten direkt im Browser.

#### C. Praxisanleiter-App: Mobiler QR-Code-Handshake & eIDAS-Gegenzeichnung
1.  **Schüler generiert QR-Code am Schichtende (Student Flutter App):**
    *   `POST /api/v1/nursing/elogbook/generate-qr`
    *   *Request Payload:*
        ```json
        {
          "rotation_id": "018f3a2c-7b90-7000-8112-3456789abcde",
          "shift_date": "2026-10-19",
          "logged_work_hours": 8.0,
          "logged_guidance_hours": 1.5,
          "guidance_topic": "Gezielte Praxisanleitung: Medikamentenstellung und Tropfenberechnung",
          "pflaprv_competencies": ["I.1.a", "I.2.c", "II.1.b"]
        }
        ```
    *   *Response ($201\text{ Created}$):* Gibt einen zeitlich auf $180\text{ Sekunden}$ begrenzten, kryptographischen `qr_handshake_token` zurück und öffnet einen WebSocket-Channel (`private-elogbook.{entry_id}`).
2.  **Praxisanleiter scannt QR-Code & unterschreibt (Praxisanleiter Flutter App):**
    *   `POST /api/v1/nursing/elogbook/verify-and-sign`
    *   *Request Payload:*
        ```json
        {
          "qr_handshake_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "instructor_rating": 5,
          "signature_vector_points": "M 10 80 Q 52.5 10, 95 80 T 180 80",
          "eidas_device_attestation_token": "att_982374982374",
          "gps_location": { "lat": 50.7753, "lng": 6.0839 }
        }
        ```
    *   *System-Reaktion:* Prüft die 24-Stunden-Fortbildungs-Compliance des Praxisanleiters nach § 4 Abs. 3 PflAPrV, versiegelt den Eintrag mit einem SHA-256-Hash, speichert den aktualisierten PDF-Nachweis im Cloud-Drive des Schülers, aktualisiert das 10%-Praxisanleitungskonto und sendet per WebSocket ein Echtzeit-Bestätigungssignal an das Smartphone des Schülers.

#### D. Wohnungsportal: Gated Checkout, eIDAS-Mietvertrag & Kautions-Weiche
*   `POST /api/v1/housing/rooms/{room_id}/initiate-lease`
    *   *Pre-Condition Middleware:* Prüft in Echtzeit gegen `applications.status`, ob der Bewerber den Status `ADMITTED_CONDITIONAL`, `ADMITTED_UNCONDITIONAL` oder `ENROLLED` besitzt. Andernfalls wird `403 Forbidden (Gated_Booking_Requires_Admission)` zurückgegeben.
    *   *Request Payload:*
        ```json
        {
          "lease_start": "2026-11-01",
          "lease_end": "2027-10-31",
          "deposit_option": "KAUTIONSFREI_BOND",
          "liability_insurance_option": "GETSAFE_ONE_CLICK"
        }
        ```
    *   *Response ($200\text{ OK}$):* Liefert die eingebettete eIDAS-QES-Signatur-Session-URL (für den nach DIN 277 / WoFlV / GEG vorausgefüllten Mietvertrag), legt den Vertragsentwurf + GEG-Energieausweis in `04_Wohnen_&_Mietvertrag/` im Cloud-Drive ab und startet die Revolut-Checkout-Session sowie den Affiliate-API-Redirect zu `kautionsfrei.de` und `hellogetsafe.com`.

#### E. Healthcare Job-Portal: Anonymes Reverse-Recruiting, Drive-Freigabe & BBB-Interviews
*   `GET /api/v1/b2b/talent-pool/search` (Für eingeloggte Krankenhäuser)
    *   *Query-Parameter:* `?qualification=GENERALISTIK&exam_before=2027-04-01&min_cefr=B2&zip_prefix=52&shift_three=true`
    *   *Sicherheits-Filter auf SQL-Ebene:*
        ```sql
        WHERE is_active = TRUE
          AND NOT (:current_employer_id = ANY(blacklisted_employer_ids))
          AND (expected_exam_date <= CURRENT_DATE + INTERVAL '3 months' OR :employer_has_early_bird = TRUE)
        ```
*   `POST /api/v1/b2b/talent-pool/{talent_profile_id}/match-request`
    *   Sendet das konkrete Gehalts- und Stationsangebot der Klinik per FCM-Push und WhatsApp an den Kandidaten.
*   `POST /api/v1/student/job-portal/matches/{match_id}/respond`
    *   Klickt der Kandidat in der App auf `"accept": true`, entschlüsselt das Backend den `encrypted_origin_user_pointer`, kopiert den verifizierten Lebenslauf in `match_requests.unmasked_pii_snapshot`, legt in `drive_share_permissions` eine auf $180\text{ Tage}$ befristete `READ_ONLY`-Freigabe auf die Zeugnismappe des Kandidaten an und schaltet den 1-zu-1-Chat sowie die **BigBlueButton-Interview-Terminierung** zwischen Krankenhaus und Kandidat frei.

#### F. First-Party-Besuchertracking, SEO & AI-SEO Endpunkte
*   `POST /api/v1/telemetry/collect`
    *   Nimmt First-Party-Besucher-Events (`page_view`, `reel_video_progress`, `scroll_depth`, `form_hesitation`, `consent_updated`) entgegen, speichert sie in `web_visitor_events` und leitet sie (sofern Consent Mode v2 erteilt) serverseitig an den Google Tag Manager Server-Side Container (`metrics.studienkolleg-aachen.de`) weiter.
*   `GET /llms.txt` & `GET /llms-full.txt`
    *   Dynamisch aus der Datenbank generierte, strukturierte Markdown-Endpunkte für KI-Suchmaschinen (ChatGPT Search, Perplexity, Claude, Google AI Overviews) mit allen aktuellen Kursen, Gebühren, Anabin-Zulassungsregeln und Wohnheim-Verfügbarkeiten.

---

### 4.3 Python FastAPI KI-Microservices (`/internal/ai/v1/...`)

Die KI-Microservices laufen in einem internen, nicht öffentlich aus dem Internet erreichbaren Docker-Netzwerk (`internal_ai_net`) und kommunizieren ausschließlich mit dem Laravel-Backend, dem Cloud-Drive und der PostgreSQL-Datenbank.

#### 1. Service: OCR, Dokumenten-Forensik & Anabin-Matching
*   **Endpunkt:** `POST /internal/ai/v1/admissions/analyze-documents`
*   **Ablauf:**
    1.  Lädt das Dokument (Zeugnis, Reisepass oder SWIFT-MT103-Zahlungsbeleg) direkt aus dem Cloud-Drive (`drive_nodes.s3_object_key`).
    2.  Prüft EXIF-Metadaten und Error-Level-Analysis (ELA) auf digitale Bildmanipulationen.
    3.  Extrahiert über das Vision-LLM strukturierte Daten im strikten Pydantic-Schema.
    4.  Führt die kombinierte Trigram- und Vektor-Suche auf `anabin_global.degrees` aus und berechnet die deutsche Note nach der **Bayerischen Formel**:
        $$\text{Note}_{\text{DE}} = \max\left(1,0;\; \min\left(4,0;\; 1 + 3 \cdot \frac{N_{\max} - N_{\text{Bewerber}}}{N_{\max} - N_{\min}}\right)\right)$$
*   **Response Payload:**
    ```json
    {
      "document_authenticity_score": 0.98,
      "extracted_person": {
        "first_name": "Youssef",
        "last_name": "El Amrani",
        "passport_number": "MA9928374",
        "passport_expiry": "2031-05-14",
        "nationality_iso": "MA"
      },
      "academic_evaluation": {
        "country_iso": "MA",
        "original_degree_title": "Baccalauréat de l'Enseignement Secondaire (Série Sciences Physiques)",
        "matched_anabin_degree_id": "018f1111-2222-7000-8000-000000000001",
        "similarity_score": 96.4,
        "anabin_assessment": "Feststellungsprüfung (Studienkolleg)",
        "eligible_tracks": ["T", "M", "W"],
        "foreign_grade_raw": 15.50,
        "foreign_scale_max": 20.00,
        "foreign_scale_min_pass": 10.00,
        "calculated_german_grade": 2.35,
        "subject_requirements_met": true
      },
      "traffic_light_recommendation": "GREEN"
    }
    ```

#### 2. Service: Adaptiver Sprachtest (CAT) nach Item-Response-Theorie
*   **Endpunkt:** `POST /internal/ai/v1/language/next-question`
*   **Mathematisches Modell:** Nutzt das 3-Parameter-Logistische Modell (3PL) der *Item Response Theory (IRT)*. Nach jeder beantworteten Frage wird die Personenfähigkeit $\theta$ via Maximum-Likelihood-Schätzung aktualisiert und die nächste Frage aus der Datenbank gewählt, deren Schwierigkeitsparameter $b_i$ die höchste Fisher-Information $I(\theta)$ liefert:
    $$P(X_i = 1 \mid \theta) = c_i + \frac{1 - c_i}{1 + e^{-a_i(\theta - b_i)}}$$

#### 3. Service: BigBlueButton Vorlesungs-Transkription & KI-Zusammenfassung
*   **Endpunkt:** `POST /internal/ai/v1/bbb/transcribe-and-summarize`
*   Nimmt die fertige MP4-Aufzeichnung eines BigBlueButton-Meetings entgegen, erstellt mittels Whisper-Large-v3 ein zeitcodiertes Transkript, generiert ein strukturiertes Lernskript inkl. Prüfungsfragen im PDF-Format und legt dieses automatisch neben der Videoaufzeichnung im Kurs-Ordner des **Cloud-Drives** ab.

#### 4. Service: KI-Virtual-Staging & Mehrsprachiger Exposé-Generator
*   **Endpunkt:** `POST /internal/ai/v1/housing/stage-and-describe`
*   Nimmt Rohbilder eines Zimmers sowie die DIN-277-/WoFlV- und GEG-Parameter entgegen, generiert virtuell möblierte Renderings, bringt das rechtlich vorgeschriebene Wasserzeichen (*"Virtuell möbliert / Visualisierungsbeispiel"*) auf Pixelebene an und liefert die fertigen Exposé-Texte in allen 8+ Sprachen zurück.

---

### 4.4 Externe Standard-Schnittstellen (HL7 FHIR R4, Revolut, DATEV, Google APIs)

1.  **HL7 FHIR R4 Server/Client (`/api/fhir/r4/...`):**
    *   Implementiert die FHIR-Ressourcen `Practitioner` (Auszubildender / Praxisanleiter), `Organization` (Pflegeschule / Kooperationsklinik), `Schedule` (PflBG-Rotationsplan) und `Attendance` (Fehlzeitenmeldung).
    *   Ermöglicht den vollautomatischen Abgleich der Praxiseinsatzpläne mit den Dienstplanprogrammen (*ATOSS*, *TimeOffice*) und Krankenhausinformationssystemen (*SAP IS-H*, *Dedalus ORBIS*) der kooperierenden Kliniken in Aachen und NRW.
2.  **Revolut Business & Merchant API Integration:**
    *   `POST /webhooks/revolut/transaction-created`: Verarbeitet eingehende Zahlungen auf den virtuellen IBANs (`revolut_viban`) in Echtzeit.
    *   Automatische Anlage von verzinsten/isolierten Unterkonten (Vaults/Sub-Accounts) für Mietkautionen nach § 551 BGB.
3.  **DATEV & EN 16931 (XRechnung / ZUGFeRD) Export-Pipeline:**
    *   Generiert für jede Ausgangsrechnung valides XML nach dem Schema `urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0` und legt es im Cloud-Drive ab.
    *   Monatlicher Sammel-Export aller Debitoren-, Kreditoren- und Lohn-/Honorarbuchungen (basierend auf der QR- und BigBlueButton-Zeiterfassung der Dozenten) im DATEV-Format (EXTF / XML-Schnittstelle online) an die Steuerkanzlei.
4.  **Google Ads Offline-Conversion, Indexing & Search Console API:**
    *   Automatischer Push neuer Kurse, Wohnungen und Pflege-Jobs an die `Google Indexing API` (`URL_UPDATED`).
    *   Täglicher Upload verifizierter Revolut-Zahlungseingänge verknüpft mit der gespeicherten `GCLID` an die `Google Ads API` (`UploadClickConversions`).

---

## 5. Automatisierte System-Cronjobs & Compliance-Wächter

Zur Durchsetzung aller gesetzlichen Fristen (DSGVO, AGG, PflBG, AZAV, AufenthG) sowie der SEO- und Drive-Synchronisation führt der zentrale Laravel-Scheduler (`schedule:run`) folgende deterministische Hintergrundprozesse aus:

| Cronjob-Name | Intervall | Gesetzliche / Fachliche Grundlage | Technische Ausführung |
| :--- | :--- | :--- | :--- |
| `agg:purge-expired-matches` | Täglich um `01:00 Uhr` | § 15 Abs. 4 AGG & Art. 17 DSGVO | Selektiert alle Datensätze in `job_portal_global.match_requests` mit `agg_purge_scheduled_at <= NOW()`. Überschreibt `unmasked_pii_snapshot` und `employer_notes` mit `NULL`, widerruft und löscht die temporäre Cloud-Drive-Freigabe (`drive_share_permissions`), löscht Chat-Anhänge im S3-Bucket, setzt den Status auf `AGG_PURGED` und schreibt einen signierten Prüfvermerk in das Datenschutz-Audit-Log. |
| `pflbg:evaluate-absences` | Stündlich | § 13 PflBG & AZAV | Berechnet die kumulierten Theorie- und Praxisfehlzeiten aller Pflegeschüler (inkl. der automatischen Auswertung von `bbb_attendance_logs` aus Online-Unterrichtsstunden). Überschreitet ein Schüler $5\%$, $7,5\%$ oder $9\%$, wird die jeweilige Eskalationsstufe ausgelöst und der AZAV-Bericht im Cloud-Drive (`/AZAV_Audit_Safe/`) abgelegt. |
| `bbb:sync-recordings-to-drive` | Alle $15\text{ Minuten}$ | EOMS (ISO 21001) & Service-SLA | Prüft abgeschlossene BigBlueButton-Sessions, überträgt fertig konvertierte MP4-Aufzeichnungen und Whisper-KI-Transkripte in den zugehörigen Kurs-Ordner im Cloud-Drive und benachrichtigt die Kursteilnehmer per Push. |
| `visa:check-expirations` | Täglich um `07:00 Uhr` | AufenthG | Prüft `visa_trackings.valid_until`. Versendet exakt $90$, $60$ und $30\text{ Tage}$ vor Ablauf mehrsprachige Warnungen via Push, E-Mail und WhatsApp inkl. frisch im Cloud-Drive (`03_Visum_&_Behoerden/`) abgelegter Immatrikulations- und Anwesenheitsbescheinigung für die Ausländerbehörde. |
| `finance:enforce-restrictions` | Täglich um `02:00 Uhr` | BGB (Zurückbehaltungsrecht) | Prüft überfällige Raten in `installments`. Ist eine Rate um mehr als $X\text{ Tage}$ im Verzug, wird `users.portal_restricted = TRUE` und `drive_nodes.is_locked_by_finance = TRUE` gesetzt (Sperrung von Zertifikats-Downloads im Cloud-Drive und Prüfungsanmeldungen bis zum Zahlungseingang). |
| `seo:refresh-llms-and-sitemaps` | Täglich um `04:00 Uhr` | AI-SEO (GEO) & Google Indexing | Generiert die `/llms.txt`, `/llms-full.txt` sowie alle mehrsprachigen XML-Sitemaps aus den aktuellen Kurs-, Anabin-, Wohnungs- und Job-Daten neu und pingt die Google Search Console & Indexing API an. |
| `anabin:delta-sync` | Monatlich (1. Sonntag, `03:00 Uhr`) | KMK-Vorgaben | Startet den Playwright-Scraper-Container, prüft `anabin.kmk.org` auf geänderte Abschlüsse oder neue Schulen, berechnet die `pgvector`-Embeddings sowie die programmatischen SEO-Texte neu und alarmiert den Master-Admin bei DOM-Änderungen. |