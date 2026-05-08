# ADR-001: MongoDB + FastAPI + React statt Supabase + Next.js

**Status:** AKZEPTIERT  
**Datum:** 2026-04-03  
**Entscheider:** Projektleitung (implizit durch Umsetzungsentscheidung im Entwicklungsprozess)  
**Kategorie:** DECISION

---

## Kontext

Das Gesamtkonzept 2026 (Kapitel 13: Tech Stack und Systemarchitektur) empfiehlt folgenden Stack:

- **Frontend:** Next.js App Router + Tailwind CSS + shadcn/ui + next-intl
- **Backend:** Supabase (PostgreSQL + Auth + Edge Functions + RLS + Storage)
- **Datenbank:** PostgreSQL 15+ (managed via Supabase)

Die tatsaechliche Umsetzung erfolgte auf einer anderen Architektur, die durch die verfuegbare Entwicklungsumgebung und operative Rahmenbedingungen bedingt war.

---

## Urspruengliche Soll-Architektur (lt. Gesamtkonzept)

| Schicht | Soll-Technologie | Begruendung lt. Konzept |
|---------|-------------------|-------------------------|
| Frontend | Next.js App Router | SEO-faehig, SSR, Server Components |
| UI | shadcn/ui + Tailwind | Konsistentes Design-System |
| i18n | next-intl | Mehrsprachigkeit (DE/EN) |
| Backend | Supabase Edge Functions | Serverless, integriert mit Auth/Storage |
| Auth | Supabase Auth | Magic Links, MFA-faehig, RLS-Integration |
| Datenbank | PostgreSQL + RLS | Relationale Integritaet, Row-Level Security |
| Storage | Supabase Storage | Signed URLs, Bucket-Policies |
| Queue | pg_mq | PostgreSQL-native Job-Queue |

---

## Tatsaechliche Ist-Architektur

| Schicht | Ist-Technologie | Version |
|---------|-----------------|---------|
| Frontend | React (CRA) | 18.x |
| UI | shadcn/ui + Tailwind CSS | Aktuell |
| i18n | react-i18next | DE/EN |
| Backend | FastAPI (Python) | 0.104+ |
| Auth | Eigene JWT-Implementierung | Cookie-basiert, httpOnly |
| Datenbank | MongoDB | 7.x |
| Storage | Lokales Dateisystem / S3-vorbereitet | local / s3 / minio |
| Queue | Keine (synchron) | -- |
| AI/KI | nscale API (ehem. DeepSeek) | deepseek-chat / deepseek-reasoner |
| E-Mail | IMAP/SMTP (Strato) + Resend (vorbereitet) | Produktiv: IMAP, Transaktional: Resend |
| PDF | ReportLab (Python) | Serverseitig |

---

## Begruendung der Abweichung

1. **Entwicklungsumgebung:** Die verfuegbare Plattform (Emergent) stellt eine containerisierte Umgebung mit FastAPI + React + MongoDB bereit. Ein Wechsel auf Supabase/Next.js haette eine vollstaendige Infrastruktur-Migration erfordert.

2. **Zeitdruck:** Das System musste in kurzem Zeitrahmen fuer 200+ Bewerber produktiv gehen. Eine Architekturmigration waere mit dem Go-Live-Termin unvereinbar gewesen.

3. **Funktionale Vollstaendigkeit:** Die Ist-Architektur deckt alle MVP-Anforderungen ab:
   - Authentifizierung mit Brute-Force-Schutz (8 Rollen, RBAC)
   - Vollstaendige CRUD-Operationen fuer alle Kernobjekte
   - AI-Screening (nscale/DeepSeek)
   - PDF-Generierung
   - E-Mail-Integration (IMAP/SMTP)
   - WCAG 2.2 / EN 301 549 Barrierefreiheit
   - i18n (DE/EN)

4. **MongoDB vs. PostgreSQL:** MongoDB bietet fuer den aktuellen Projektumfang ausreichende Flexibilitaet. Die fehlende RLS wird durch middleware-basierte Rechtepruefung im FastAPI-Backend kompensiert.

---

## Konsequenzen

### Positiv
- Schnellere Entwicklungsgeschwindigkeit durch vertraute Umgebung
- Direkte Kontrolle ueber Auth-Logik (kein Vendor-Lock-in)
- Flexibles Schema (MongoDB) erleichterte iterative Entwicklung
- Vollstaendig funktionsfaehiges System innerhalb des Zeitrahmens

### Negativ / Risiken
- **Keine RLS:** Rechtelogik liegt vollstaendig im Anwendungscode (FastAPI-Middleware), nicht in der Datenbank. Ein Fehler im Middleware-Code koennte zu unbefugtem Zugriff fuehren.
- **Kein SSR/SEO:** React CRA rendert client-seitig. Public-Seiten (Home, Studienkolleg, FAQ) sind nicht SEO-optimiert.
- **Keine native Queue:** Langfristige Prozesse (PDF, Massen-E-Mails, Webhooks) laufen synchron. Bei Skalierung wird ein Queuing-System notwendig.
- **Manuelles Auth-Management:** JWT-Rotation, Refresh-Token-Logik und Brute-Force-Schutz sind eigenentwickelt und muessen separat gehaertet und geprueft werden.
- **Storage-Limitation:** Aktuell lokales Dateisystem. S3/MinIO-Code ist vorbereitet, aber nicht produktiv.

---

## Risiken

| Risiko | Schwere | Mitigation |
|--------|---------|------------|
| RBAC-Bypass durch Middleware-Fehler | HOCH | Umfassende Rollentests, Negativtests pro Rolle |
| Datenverlust bei MongoDB ohne Backup | HOCH | Backup-Routine einrichten (GO_LIVE_BLOCKER T6) |
| Skalierungsprobleme bei synchroner Verarbeitung | MITTEL | Queue-System (Celery/Redis) bei Bedarf einfuehren |
| SEO-Nachteile fuer Public-Seiten | MITTEL | Langfristig: Next.js fuer Public-Web, React fuer Portale |
| Vendor-Lock-in durch Emergent-Plattform | NIEDRIG | Standard-Stack (FastAPI/React/MongoDB) ist portabel |

---

## Auswirkungen auf zukuenftige Entscheidungen

1. **Migration auf Next.js:** Kann inkrementell erfolgen (Public-Seiten zuerst), ohne das gesamte System umzubauen. Die Backend-API bleibt stabil.
2. **Migration auf PostgreSQL:** Erfordert Schema-Migration und Anpassung aller MongoDB-Queries. Sinnvoll erst bei Bedarf fuer relationale Integritaet oder RLS.
3. **Supabase-Adoption:** Kann als Auth- und Storage-Provider ergaenzt werden, ohne das gesamte Backend zu ersetzen.
4. **Queue-Einfuehrung:** Celery + Redis ist mit FastAPI direkt kompatibel und kann ohne Architekturbruch eingefuehrt werden.

---

## Abgrenzung

Dieses ADR dokumentiert den aktuellen Architekturstand und die Gruende fuer die Abweichung vom Gesamtkonzept. Es rechtfertigt NICHT automatisch jede Folgeentscheidung. Zukuenftige Architekturentscheidungen (z.B. Queue-System, Storage-Provider, Frontend-Framework) erfordern eigene ADRs mit eigenstaendiger Begruendung.
