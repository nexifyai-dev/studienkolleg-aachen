# Storage

## Zweck

Diese Seite beschreibt die Speicherstrategie für Dokumente und die betriebliche Bedeutung der verschiedenen Storage-Backends.

## Architekturidee

Der Storage-Service kapselt die eigentliche Dateispeicherung hinter einer Abstraktion. Dadurch bleibt die Documents-Domäne unabhängig davon, ob Dateien lokal, in S3/MinIO oder nur als Metadaten behandelt werden.

## Speicherprinzipien

1. Interne Storage Keys bleiben serverintern.
2. Browser erhalten keine direkten Storage-Pfade.
3. Downloads laufen über authentifizierte Backend-Endpunkte.
4. Dateinamen werden sanitisiert.
5. Uploads werden auf Größe und MIME-Type geprüft.

## Storage-Backends

### Local Storage

Eigenschaften:
- speichert Dateien im Dateisystem unter `LOCAL_STORAGE_PATH`
- geeignet für Entwicklung und einfache Testumgebungen
- ungeeignet für echte Produktion ohne Redundanz und Betriebsmaßnahmen

Vorteile:
- einfach
- lokal gut nachvollziehbar
- keine externen Credentials nötig

Nachteile:
- keine Replikation
- kein CDN
- schwächerer Betriebsstandard
- problematisch für skalierte Produktionsumgebungen

### S3 / MinIO

Eigenschaften:
- produktionsnahe Objekt-Storage-Strategie
- nutzt `boto3`
- unterstützt Upload, Download, Delete und Presigned URLs auf Storage-Ebene
- im Produkt werden Dateien trotzdem serverseitig ausgeliefert

Voraussetzungen:
- `STORAGE_BACKEND=s3` oder `minio`
- `S3_ENDPOINT`
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_BUCKET`
- optional Region / Endpoint-Spezifika

Vorteile:
- robuster für Produktion
- besser skalierbar
- kompatibel mit MinIO / S3-ähnlichen Systemen

### Metadata-only

Eigenschaften:
- speichert nur Metadaten
- keine echte Binärablage
- nur für Demo-, MVP- oder Übergangsphasen geeignet

Risiko:
- UI kann Dokumentkontext zeigen, obwohl keine echte Datei verfügbar ist

## Dateivalidierung

Die Upload-Validierung prüft insbesondere:

- maximale Dateigröße
- erlaubte MIME-Types
- gültigen Dateinamen

Aktuell sind insbesondere typische PDF-, Bild- und Word-Formate vorgesehen.

## Storage-Key-Strategie

Storage Keys werden intern erzeugt und folgen einer strukturierten Pfadlogik pro:

- Dokumentbereich
- Application
- Dokumenttyp
- eindeutiger Dateikomponente

Das verbessert Nachvollziehbarkeit und Kollisionsschutz.

## Betriebsimplikationen

Storage ist ein Go-live-Thema, weil davon abhängen:

- echte Dokumenten-Uploads
- Wiederherstellbarkeit
- Download-Zuverlässigkeit
- Aufbewahrung und Datenschutz
- Skalierbarkeit im Produktivbetrieb

## Empfohlene Produktionsstrategie

Für echte Produktion sollte die Plattform nicht auf dauerhaftem Local Storage basieren. Ein objektbasierter Storage mit klarer Backup- und Betriebsstrategie ist der bessere Zielzustand.

## Prüfregeln bei Storage-Änderungen

Bei Änderungen an Storage bitte immer prüfen:

1. Sind Env-Variablen vollständig dokumentiert?
2. Muss die Go-live-Checkliste angepasst werden?
3. Ändern sich Upload-/Download-Flows im Frontend?
4. Müssen Datenschutz- oder Aufbewahrungshinweise ergänzt werden?
5. Muss Restore-/Backup-Dokumentation angepasst werden?

## Dokumentationsregel

Diese Seite sollte aktualisiert werden, wenn:

- ein neues Storage-Backend eingeführt wird
- Validierungsregeln geändert werden
- Download-Strategie geändert wird
- Presigned- oder direkte Download-Strategie geändert wird
- Aufbewahrungs- oder Betriebsanforderungen geändert werden
