# KI-Pruefungs-Arbeitsweise – Technische Dokumentation

## Architektur: Retrieval-First + Delta-orientiert

### Ueberblick

Die KI-gestuetzte Bewerberpruefung des Studienkolleg Aachen arbeitet nach dem
**Retrieval-first-Prinzip**: Vor jedem KI-Call werden persistierte Wissensbasen
und gecachte Ergebnisse abgefragt. Ein KI-Call erfolgt nur, wenn sich relevante
Daten seit der letzten Pruefung geaendert haben (Delta-Logik).

### Ablauf einer KI-Pruefung

```
1. CACHE CHECK
   ├── Fingerprint aus Bewerbungsdaten berechnen (SHA256)
   ├── Letzte Pruefung fuer diese Bewerbung aus DB laden
   └── Fingerprint vergleichen → HIT = cached result zurueck, KEIN KI-Call

2. ANABIN RETRIEVAL (MongoDB)
   ├── Land des Abschlusses in anabin_knowledge Collection suchen
   ├── Exakt-Match → Kategorie + Einschaetzung zurueck
   ├── Fuzzy-Match → Aehnlichkeitstreffer
   └── Kein Match → auto_flagged + manuelle Pruefung markiert

3. REGELBASIERTE CHECKS (kein KI)
   ├── Vollstaendigkeit: Pflichtdokumente vorhanden?
   ├── Sprachniveau: CEFR-Level ausreichend fuer Kurstyp?
   └── Formale Eignung: Anabin-Kategorie + Sprachniveau

4. KI-CALL (nur bei Delta)
   ├── DeepSeek API (deepseek-chat Modell)
   ├── Strukturierter Prompt mit 10-Punkte-Ergebnisstruktur
   ├── Delta-Kontext: Was hat sich seit letzter Pruefung geaendert?
   └── Ergebnis wird mit Fingerprint in DB persistiert

5. PERSISTENZ
   ├── Screening-Ergebnis in ai_screenings Collection
   ├── data_fingerprint fuer naechsten Cache-Check
   └── Audit-Trail via audit_logs
```

### Datenmodell

#### anabin_knowledge Collection
```json
{
  "country": "Iran",
  "country_lower": "iran",
  "category": "H",
  "notes": "Anerkennbar mit moeglichen Auflagen",
  "last_verified": "2026-01-15T00:00:00Z",
  "source": "anabin_seed | staff_manual | ai_research | auto_flagged"
}
```

#### ai_screenings Collection
```json
{
  "screening_id": "uuid",
  "application_id": "...",
  "data_fingerprint": "sha256[:16]",
  "cache_hit": false,
  "ai_report": "Strukturierter Bericht...",
  "local_checks": {
    "completeness": {...},
    "anabin_assessment": {...},
    "language_level_check": {...}
  },
  "suggested_stage": "in_review",
  "staff_decision_required": true
}
```

### Fingerprint-Berechnung

Der Fingerprint wird aus folgenden Feldern berechnet:
- course_type, language_level, degree_country, current_stage
- Dokumenttypen + Status (sortiert)
- Anzahl der Nachrichten

Aenderung in einem dieser Felder → neuer Fingerprint → Cache Miss → KI-Call.

### Kostenersparnis

- **~70-90% weniger KI-Calls** fuer ungeaenderte Bewerbungen
- Regelbasierte Checks laufen immer lokal (kein KI-Call noetig)
- Nur echte Datenaenderungen triggern einen KI-Call

### Eskalationslogik

Staff-Entscheid wird als **zwingend erforderlich** markiert wenn:
- Pflichtdokumente fehlen
- Sprachniveau unzureichend
- Anabin-Kategorie = D (eingeschraenkte Anerkennung)
- Anabin-Kategorie = pruefen/unbekannt (Land nicht in Wissensbasis)

### Ergebnisstruktur (10 Punkte)

1. **VOLLSTAENDIGKEIT**: Beurteilung der Unterlagen
2. **DOKUMENTGUELTIGKEIT**: Plausibilitaet
3. **FORMALE VORPRUEFUNG**: Anabin-Einschaetzung
4. **FSP-VORPRUEFUNG**: Feststellungspruefung-Relevanz
5. **SPRACHSTAND**: Niveau, Mindestanforderung, Empfehlung
6. **EMPFEHLUNGSPFAD**: Kurs + Begruendung
7. **RISIKEN**: Probleme, Unsicherheiten
8. **OFFENE PUNKTE**: Was noch zu klaeren ist
9. **NAECHSTE SCHRITTE**: Konkrete Aktionen
10. **STAFF-ENTSCHEID NOTWENDIG**: Ja/Nein mit Begruendung

### Quellenlogik

| Quelle | Typ | Persistenz |
|--------|-----|-----------|
| Anabin Knowledge Base | MongoDB Collection | Persistent, erweiterbar |
| Screening Cache | MongoDB (ai_screenings) | Fingerprint-basiert |
| Mail-Historie | MongoDB (messages) | Live-Abfrage, letzte 5 im Prompt |
| Dokumentenstatus | MongoDB (documents) | Teil des Fingerprints |
| DeepSeek API | Externer Service | Ergebnis wird persistiert |

### Offene Punkte

- [ ] Admin-UI zum Bearbeiten der Anabin-Wissensbasis
- [ ] Automatisches Re-Screening bei Dokumenten-Upload (Webhook)
- [ ] Batch-Screening fuer mehrere Bewerbungen
- [ ] Export der KI-Berichte als PDF
- [ ] Integration mit echtem Anabin-Webservice (wenn API verfuegbar)
