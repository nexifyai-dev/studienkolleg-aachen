# Screening-Regelmatrix

Die Datei `screening_rule_matrix.v1.0.json` ist das versionierte Regelartefakt für die lokale Vorprüfung.

## Lokal implementierte Regeln (automatisch auswertbar)

- `docs_required_uploaded`  
  Prüft Vollständigkeit der kursspezifischen Pflichtdokumente.
- `language_min_met`  
  Prüft Mindest-CEFR-Level pro Kurstyp.
- `degree_country_classified`  
  Prüft, ob das Herkunftsland in der lokalen Länderklassifikation vorhanden ist.

## Nur manuell prüfbare Regeln

- `anabin_external_database_verification`  
  Externer Anabin-Abgleich und finale fachliche Einordnung bleiben **immer** Staff-Aufgabe.

## Versionierungsmodell

- `active_version`: Standard-Regelset für neue Auswertungen.
- `deprecated_versions`: weiterhin auflösbare Altversionen für rückwärtskompatible Re-Evaluation.
- `versioned_rule_sets`: konkrete Regeln, Quellenbezug (Pflichtenheft + Drive-Dokument-ID), Scope, Schweregrad und Next-Action-Mapping je Version.
