# Projekt-Historie (fachlich + technisch)

## 2026-03-30 – Dokumentationsbaseline v1
- Vollständige Dokumentationsarchitektur unter `docs/` eingeführt.
- README von Platzhalter auf operatives Betriebsdokument gehoben.
- ADR-System für Architektur-/Workflow-/Provider-Entscheidungen etabliert.
- Verbindliche Dokumentationsrichtlinie für künftige AI-/Contributor-Läufe verankert.
- Begründung: Auditfähigkeit, Übergabefähigkeit und konsistente Source-of-Truth-Struktur herstellen.
- Auswirkungen: Onboarding, Betrieb, Review-Qualität und Änderungsnachvollziehbarkeit verbessert.

## 2026-03-30 – DeepSeek- und Screening-Klarstellung (laufende Umsetzung)
- AI-Provider-Basis auf DeepSeek vereinheitlicht.
- Screening-Ausgaben fachlich in vier Ebenen getrennt (`completeness`, `formal_precheck`, `ai_recommendation`, `staff_decision`).
- Begründung: Keine impliziten Finalentscheidungen aus Uploads oder KI-Texten.

## 2026-03-29 und früher – Plattformfundament
- Multi-Portal-Architektur (Public/Applicant/Staff/Admin/Partner) umgesetzt.
- Aufgabenmodul auf operativen CRM-Stand (Detail, Notizen, Anhänge, Verlauf) gebracht.
- i18n, SEO, Consent-Banner, Auth/RBAC, Messaging und Audit-Grundlagen implementiert.
- Offene Go-Live-Themen verblieben in Rechts-/Infra-/Provider-Track.
