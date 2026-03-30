# ADR-0010: Upload-Strategie mit Storage-Abstraktion (local/S3/MinIO)

- **Datum:** 2026-03-30
- **Status:** accepted

## Kontext
Dokumentenmanagement benötigt austauschbaren Persistenzlayer.

## Problem
Umgebungsabhängige Speicheranforderungen (lokal vs. objektbasiert).

## Entscheidung
Storage-Service mit Backend-Auswahl über Konfiguration (`local`, `s3`, `minio`).

## Begründung
Portable Deployments und kontrollierter Übergang zwischen Umgebungen.

## Alternativen
Hardcoded Local Storage (nicht skalierbar).

## Auswirkungen
Konfigurations- und Credential-Management wird betriebsrelevant.

## Betroffene Dateien/Bereiche
`backend/services/storage.py`, `backend/config.py`, Operations-Doku.

## Risiken / Folgeaufgaben
S3/MinIO-Credentials und Backupkonzept produktiv absichern.
