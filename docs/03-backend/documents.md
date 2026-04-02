# Documents Domain

## Zweck

Die Documents-Domäne beschreibt Upload, Speicherung, Review und Download von bewerbungsbezogenen Dokumenten. Das System trennt dabei bewusst zwischen sichtbaren Dokument-Metadaten und internen Storage-Details.

## Kernprinzipien

1. Dokumentzugriff ist an die Parent-Application gekoppelt.
2. Interne Storage Keys werden nicht an Clients offengelegt.
3. Downloads laufen serverseitig und authentifiziert.
4. Uploads werden auf MIME-Type und Dateigröße validiert.
5. Wichtige Aktionen werden audit-geloggt.

## Zugriffsmodell

### Applicant
- sieht nur Dokumente der eigenen Application
- lädt eigene Dokumente hoch
- lädt nur eigene Dokumente herunter

### Staff
- prüft Dokumente im Kontext zugänglicher Applications
- setzt Review-Status
- ergänzt interne Review-Hinweise

## Fachliche Hauptfunktionen

### Dokumentliste pro Application
Liefert Dokument-Metadaten für einen Fall.

Wichtig:
- `storage_key` wird vor der Rückgabe entfernt
- nur fachlich relevante Informationen gehen an den Client

### Dokument-Upload
Upload erfolgt application-bezogen.

Typische Felder:
- `document_type`
- `filename`
- `content_type`
- optional `file_data` als Base64

Verhalten:
- Dateiname wird sanitisiert
- Base64 wird dekodiert
- Upload wird validiert
- Storage-Key wird intern erzeugt
- Metadaten werden in MongoDB persistiert
- Upload wird geloggt

### Download
Der Download läuft serverseitig.

Wichtig:
- kein direkter Storage-Link für Browser
- kein Storage-Key in Responses
- klare Fehlerfälle bei fehlender Binärdatei oder fehlender Storage-Konfiguration

### Review
Staff kann Dokumente auf Zustände setzen wie:
- `in_review`
- `approved`
- `rejected`
- `superseded`

Optional:
- Ablehnungsgrund
- interner Kommentar

## Datenmodell auf hoher Ebene

Ein Dokument enthält typischerweise:

- `application_id`
- `document_type`
- `filename`
- `content_type`
- `file_size`
- `status`
- `uploaded_by`
- `uploaded_at`
- `visibility`
- `storage_key` (intern)
- `has_binary`

## Storage-Abstraktion

Die Documents-Domäne hängt direkt am Storage-Service.

Wichtige Hilfsfunktionen:
- `sanitize_filename()`
- `build_storage_key()`
- `validate_upload()`
- `storage().upload()`
- `storage().download()`

## Unterstützte Speicherstrategien

### Local Storage
- gut für Entwicklung und einfache Testumgebungen
- nicht geeignet für echte Produktion

### S3 / MinIO
- vorgesehene produktionsnahe Strategie
- benötigt Credentials und Backend-Konfiguration

### Metadata-only
- speichert nur Metadaten ohne echte Dateiablage
- nur für Demo-/Übergangsszenarien geeignet

## Gekoppelte Systeme

Die Documents-Domäne hängt eng zusammen mit:

- Applications
- Storage
- Audit
- Automation / Notifications
- Applicant Portal
- Staff Applicant Detail

## Dokumentationsregel

Diese Seite sollte angepasst werden, wenn:

- neue Dokumenttypen entstehen
- Upload- oder Download-Strategie geändert wird
- Storage-Backend geändert wird
- Review-Status oder Review-Prozess geändert wird
- Sichtbarkeit oder Ownership-Regeln geändert werden
