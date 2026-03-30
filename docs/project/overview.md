# Projektüberblick

Stand: 2026-03-30

## Projektziel
Eine mehrsprachige (DE/EN), rollenbasierte Applicant-Management- und CRM-Plattform für das Studienkolleg Aachen, die Bewerbungen operativ verarbeitet und nachvollziehbar dokumentiert.

## Scope (In Scope)
- Öffentliche Lead-/Bewerbungserfassung.
- Applicant-Portal (Journey, Dokumente, Nachrichten, Consent, Einstellungen).
- Staff-CRM (Kanban, Applicant-Detail, Aufgaben inkl. Notizen/Anhänge/Verlauf, Messaging, Follow-ups).
- Teacher-Zugriff auf zugewiesene Fälle unter Consent-Bedingungen.
- Admin-Funktionen (User, Audit).
- Partner-Referral-Portal.
- AI-basierte Vorprüfung mit klarer Nicht-Finalitätsgrenze.

## Nicht-Scope (aktuell)
- Finale juristische Bewertung von Bewerberdokumenten durch das System.
- Vollständige Zahlungsabwicklung (Finanzmodul noch vorbereitet).
- Vollständiges IMAP-/WhatsApp-Threading als Kernfunktion.

## Projektstatus
- **Technischer Status:** Kernfunktionen funktionsfähig, modulare API und Multi-Portal-Frontend etabliert.
- **Betriebsstatus:** Nicht vollständig go-live-fähig wegen externer/rechtlicher/infra-seitiger Blocker.

## Zielmärkte und Sprachen
- Primärmarkt: deutschsprachiger Studienkolleg-Betrieb mit internationalem Bewerberfokus.
- Sprachen: Deutsch (Default), Englisch (voll unterstützt).

## Rollen
- superadmin, admin, staff, accounting_staff, teacher, applicant, affiliate.

## Hauptprozesse
1. Bewerbungseingang und Funnel-Steuerung.
2. Dokumenten- und Vollständigkeitsmanagement.
3. Staff-Kommunikation und Aufgabensteuerung.
4. KI-Vorprüfung + Staff-Entscheidung.
5. Partner-Referral-Übergaben.

## Kritische Abhängigkeiten
- MongoDB Verfügbarkeit/Backups.
- E-Mail-Versand über Resend.
- DeepSeek API für KI-Berichte.
- Deployment/TLS für sichere Cookies.

## Aktuelle Blocker
- Rechtstexte und Impressumsdaten finalisieren.
- Resend Domain produktiv verifizieren.
- Backup-/Restore-Routine produktionstauglich etablieren.
- TLS-/Cookie-Härtung final verifizieren.

## Umsetzungsstand (kompakt)
- Applicant, Staff, Admin, Partner, Teacher Flows implementiert.
- Aufgaben-/Messaging-Module operativ mit Historie/Anhängen.
- AI-Screening via DeepSeek implementiert, inkl. Trennung von Vorprüfung und Staff-Entscheidung.
