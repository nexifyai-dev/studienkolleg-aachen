"""
Externe Wissensbasis – Referenzquellen fuer KI-Kontext.

Enthalt strukturiertes Wissen aus:
- Anabin (Zeugnisbewertung)
- uni-assist (Hochschulzugang)
- TestAS (Studierfaehigkeitstest)
- Auswaertiges Amt (Visa/Aufenthalt)
- BAMF (Aufenthaltsgesetz)
- Goethe/telc/TestDaF (Sprachzertifikate)
- PRADO (Ausweisdokumente)
- Berufsanerkennung (Pflege)

Diese Daten werden als System-Prompt-Kontext in KI-Calls verwendet.
"""
import logging

logger = logging.getLogger(__name__)


EXTERNAL_KNOWLEDGE_BASE = {
    "anabin": {
        "name": "Anabin – Informationsportal zu auslaendischen Bildungsabschluessen",
        "url": "https://anabin.kmk.org/",
        "focus": "Bewertung auslaendischer Schul- und Hochschulabschluesse fuer deutschen Hochschulzugang",
        "categories": {
            "H+": "Direkter Hochschulzugang (Abschluss vollstaendig anerkannt)",
            "H+/-": "Bedingter Zugang – Feststellungspruefung (FSP) am Studienkolleg erforderlich",
            "H-": "Kein direkter Zugang – TestAS oder Berufsausbildung empfohlen",
            "D": "Defizitbescheid – Anpassungslehrgang oder Kenntnisspruefung noetig",
        },
        "rules": [
            "Abschluss wird nach Herkunftsland + Abschlussart bewertet",
            "EU-Abschluesse sind meist H+ (Bologna-Konformitaet)",
            "Laender wie Marokko, Tunesien: meist H+/- (Studienkolleg)",
            "Laender wie Indien: teils H+ bei 12-jaehriger Schulzeit + Uni-Jahr",
        ],
    },
    "uni_assist": {
        "name": "uni-assist – Servicestelle fuer internationale Studienbewerbungen",
        "url": "https://www.uni-assist.de/tools/check-hochschulzugang/",
        "focus": "Laender- und zeugnisspezifische Anforderungen fuer deutsche Hochschulen",
        "key_info": [
            "Bearbeitungszeit: 4-6 Wochen (Vorabpruefung moeglich)",
            "Kosten: 75 EUR (erste Bewerbung), 30 EUR (jede weitere)",
            "Fristen: Sommersemester 15.01., Wintersemester 15.07.",
        ],
    },
    "testas": {
        "name": "TestAS – Test fuer Auslaendische Studierende",
        "url": "https://www.testas.de/",
        "focus": "Studierfaehigkeitstest bei fehlendem direktem Hochschulzugang",
        "key_info": [
            "Dauer: ca. 4 Stunden (Kerntest + Fachmodul)",
            "Kosten: 100 EUR",
            "Gueltig: unbegrenzt",
            "Module: Geistes-/Kultur-, Ingenieur-, Mathematik/Naturwissenschaften, Wirtschaft",
            "Ergebnis: Standardwert (100 = Durchschnitt, >110 = gut)",
        ],
    },
    "visa_requirements": {
        "name": "Auswaertiges Amt – Visa und Aufenthalt",
        "url": "https://www.auswaertiges-amt.de/de/service/visa-und-aufenthalt",
        "focus": "Dokumentenanforderungen fuer Studienvisum",
        "required_documents": [
            "Reisepass (mind. 6 Monate gueltig ueber Aufenthaltsdauer hinaus)",
            "Zulassungsbescheid der Hochschule/Studienkolleg",
            "Finanzierungsnachweis (Sperrkonto: 11.208 EUR/Jahr, Stand 2026)",
            "Krankenversicherungsnachweis",
            "Motivationsschreiben (bei manchen Botschaften)",
            "Sprachnachweis (mind. B1 fuer Studienkolleg, C1 fuer Direktstudium)",
        ],
        "visa_types": {
            "studienvorbereitung": "§16b Abs. 1 AufenthG – Studienkolleg/Sprachkurs (max 2 Jahre)",
            "studium": "§16b Abs. 1 AufenthG – Fachstudium (Dauer des Studiums + 18 Monate)",
            "ausbildung": "§16a AufenthG – Berufsausbildung (Dauer der Ausbildung)",
            "fachkraft": "§18a/b AufenthG – Fachkraefte mit Berufsausbildung/Hochschulabschluss",
        },
    },
    "bamf": {
        "name": "BAMF – Bundesamt fuer Migration und Fluechtlinge",
        "url": "https://www.bamf.de/",
        "focus": "Aufenthaltsrecht, Integration, Chancenkarte",
        "key_paragraphs": {
            "16a": "Berufsausbildung – Aufenthaltserlaubnis zum Zweck der Berufsausbildung",
            "16b": "Studium – Aufenthaltserlaubnis zum Studium (inkl. Studienkolleg)",
            "18a": "Fachkraefte mit Berufsausbildung",
            "18b": "Fachkraefte mit akademischer Ausbildung",
            "20a": "Chancenkarte – Punktesystem fuer Fachkraefte",
        },
    },
    "language_certificates": {
        "goethe": {
            "name": "Goethe-Institut",
            "url": "https://www.goethe.de/ins/de/de/prf.html",
            "verification": "https://www.goethe.de/ins/de/de/prf/ver.html",
            "levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "validity": "Unbegrenzt (kein Ablaufdatum)",
            "acceptance": "Weltweit anerkannt, Standard fuer DSH-Befreiung ab C2",
        },
        "telc": {
            "name": "telc – The European Language Certificates",
            "url": "https://www.telc.net/",
            "verification": "https://www.telc.net/pruefungsteilnehmende/zertifikat-verifizieren.html",
            "special": "telc Deutsch B1-B2 Pflege (speziell fuer Pflegeberufe)",
            "validity": "Unbegrenzt",
        },
        "testdaf": {
            "name": "TestDaF – Test Deutsch als Fremdsprache",
            "url": "https://www.testdaf.de/",
            "levels": ["TDN 3", "TDN 4", "TDN 5"],
            "requirement": "TDN 4 in allen Bereichen = DSH-2 Aequivalent (Direktzugang)",
            "validity": "Unbegrenzt",
            "areas": ["Leseverstehen", "Hoerverstehen", "Schriftlicher Ausdruck", "Muendlicher Ausdruck"],
        },
    },
    "document_verification": {
        "prado": {
            "name": "PRADO – Public Register of Authentic travel and identity Documents Online",
            "url": "https://www.consilium.europa.eu/prado/de/prado-start-page.html",
            "focus": "Offizielle Layouts, MRZ-Strukturen, Sicherheitsmerkmale globaler Ausweisdokumente",
        },
        "edisontd": {
            "name": "EdisonTD – Travel Documents System",
            "url": "https://www.edisontd.net/",
            "focus": "Ergaenzende DB fuer MRZ-Codes und Dokumenten-Gueltigkeiten",
        },
    },
    "professional_recognition": {
        "name": "Anerkennung in Deutschland",
        "url": "https://www.anerkennung-in-deutschland.de/",
        "focus": "Reglementierte Berufe (Pflege): Defizitbescheide, Anpassungslehrgaenge",
        "nursing": {
            "name": "Pflegeausbildung – BMFSFJ",
            "url": "https://www.pflegeausbildung.net/",
            "requirements": [
                "Mittlerer Schulabschluss (oder aequivalent nach Anabin)",
                "Deutschkenntnisse mind. B2 (telc B1-B2 Pflege akzeptiert)",
                "Gesundheitszeugnis",
                "Aufenthaltserlaubnis §16a AufenthG",
            ],
            "duration": "3 Jahre (generalistische Pflegeausbildung)",
        },
    },
}


def get_knowledge_context_for_ai(task: str = "general") -> str:
    """Gibt strukturierten Wissenskontext fuer KI-System-Prompts zurueck."""
    kb = EXTERNAL_KNOWLEDGE_BASE

    context_parts = [
        "=== WISSENSBASIS: Deutsches Bildungs- und Aufenthaltsrecht ===\n",
    ]

    if task in ("screening", "qualification", "general"):
        context_parts.append("ANABIN-KATEGORIEN:")
        for cat, desc in kb["anabin"]["categories"].items():
            context_parts.append(f"  {cat}: {desc}")
        context_parts.append("")
        for rule in kb["anabin"]["rules"]:
            context_parts.append(f"  - {rule}")
        context_parts.append("")

    if task in ("screening", "qualification", "general"):
        context_parts.append("VISA-ANFORDERUNGEN:")
        for doc in kb["visa_requirements"]["required_documents"]:
            context_parts.append(f"  - {doc}")
        context_parts.append("")

    if task in ("document", "verification", "general"):
        context_parts.append("SPRACHZERTIFIKATE:")
        for key, cert in kb["language_certificates"].items():
            name = cert.get("name", key)
            context_parts.append(f"  {name}: {cert.get('validity', '')}")
        context_parts.append("  TestDaF: TDN 4 alle Bereiche = Direktzugang Hochschule")
        context_parts.append("  Goethe C2 = DSH-Befreiung")
        context_parts.append("")

    if task in ("screening", "qualification", "nursing", "general"):
        context_parts.append("PFLEGEAUSBILDUNG:")
        for req in kb["professional_recognition"]["nursing"]["requirements"]:
            context_parts.append(f"  - {req}")
        context_parts.append(f"  Dauer: {kb['professional_recognition']['nursing']['duration']}")
        context_parts.append("")

    if task in ("screening", "general"):
        context_parts.append("AUFENTHALTSGESETZ:")
        for para, desc in kb["bamf"]["key_paragraphs"].items():
            context_parts.append(f"  §{para}: {desc}")

    return "\n".join(context_parts)


def get_all_reference_urls() -> list:
    """Gibt alle externen Referenz-URLs zurueck."""
    urls = []
    kb = EXTERNAL_KNOWLEDGE_BASE
    for key, val in kb.items():
        if isinstance(val, dict):
            if "url" in val:
                urls.append({"key": key, "name": val.get("name", key), "url": val["url"]})
            for subkey, subval in val.items():
                if isinstance(subval, dict) and "url" in subval:
                    urls.append({"key": f"{key}.{subkey}", "name": subval.get("name", subkey), "url": subval["url"]})
    return urls
