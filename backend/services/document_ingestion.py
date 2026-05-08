"""
Dokumenten-Ingestion & Plausibilitaets-Engine (v2.2)

Schritt 1: Ingestion & Normalisierung
  - EXIF-Stripping (Sicherheit)
  - DPI-Normalisierung (300 DPI fuer OCR)
  - Bild-Optimierung

Schritt 4: Plausibilitaets-Checks (nach Klassifikation)
  - Reisepass-Ablaufdatum (mind. 6 Monate in der Zukunft)
  - Namensabgleich mit CRM-Profil
  - MRZ-Pruefsummen-Validierung (Reisepaesse)
  - Zertifikatsnummer-Strukturpruefung (Goethe, telc)
  - Automatischer Status-Update bei vollstaendiger Validierung
"""
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════
# SCHRITT 1: INGESTION & NORMALISIERUNG
# ══════════════════════════════════════════════════════════════════════

def strip_exif(image_data: bytes, content_type: str) -> bytes:
    """Entfernt EXIF-Metadaten aus Bilddateien (Sicherheit/Datenschutz)."""
    if not content_type or not content_type.startswith("image/"):
        return image_data
    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(image_data))
        # Orientation beibehalten, alles andere entfernen
        orientation = None
        if hasattr(img, '_getexif') and img._getexif():
            exif = img._getexif()
            orientation = exif.get(274)  # 274 = Orientation tag
        # Ohne EXIF speichern
        clean = BytesIO()
        fmt = "JPEG" if content_type in ("image/jpeg", "image/jpg") else "PNG"
        if orientation and orientation != 1:
            rotations = {3: 180, 6: 270, 8: 90}
            if orientation in rotations:
                img = img.rotate(rotations[orientation], expand=True)
        img.save(clean, format=fmt, quality=92)
        logger.info(f"[INGESTION] EXIF gestrippt: {len(image_data)} → {clean.tell()} bytes")
        return clean.getvalue()
    except Exception as e:
        logger.warning(f"[INGESTION] EXIF-Strip fehlgeschlagen: {e}")
        return image_data


def normalize_image_dpi(image_data: bytes, content_type: str, target_dpi: int = 300) -> bytes:
    """Skaliert Bilder auf mindestens target_dpi fuer optimale OCR-Erkennung."""
    if not content_type or not content_type.startswith("image/"):
        return image_data
    try:
        from PIL import Image
        from io import BytesIO
        img = Image.open(BytesIO(image_data))
        w, h = img.size
        # Wenn Bild zu klein (< 1000px Breite), hochskalieren
        if w < 1000:
            scale = 1000 / w
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            out = BytesIO()
            fmt = "JPEG" if content_type in ("image/jpeg", "image/jpg") else "PNG"
            img.save(out, format=fmt, quality=92, dpi=(target_dpi, target_dpi))
            logger.info(f"[INGESTION] DPI-Normalisierung: {w}x{h} → {new_w}x{new_h} @ {target_dpi}DPI")
            return out.getvalue()
        return image_data
    except Exception as e:
        logger.warning(f"[INGESTION] DPI-Normalisierung fehlgeschlagen: {e}")
        return image_data


def preprocess_document(file_data: bytes, content_type: str) -> bytes:
    """Vollstaendige Vorverarbeitung: EXIF-Strip + DPI-Normalisierung."""
    if not content_type or not content_type.startswith("image/"):
        return file_data
    data = strip_exif(file_data, content_type)
    data = normalize_image_dpi(data, content_type)
    return data


# ══════════════════════════════════════════════════════════════════════
# MRZ-ERKENNUNG & VALIDIERUNG (Reisepaesse)
# ══════════════════════════════════════════════════════════════════════

MRZ_LINE_PATTERN = re.compile(r'[A-Z0-9<]{30,44}')


def detect_mrz_lines(text: str) -> list:
    """Erkennt MRZ-Zeilen (Machine Readable Zone) in extrahiertem Text."""
    if not text:
        return []
    lines = text.split('\n')
    mrz_lines = []
    for line in lines:
        cleaned = line.strip().replace(' ', '')
        if MRZ_LINE_PATTERN.match(cleaned) and len(cleaned) >= 30:
            mrz_lines.append(cleaned)
    return mrz_lines[:3]


def validate_mrz_checksum(data: str, check_digit: str) -> bool:
    """Validiert MRZ-Pruefsumme (ICAO 9303 Standard)."""
    weights = [7, 3, 1]
    total = 0
    for i, ch in enumerate(data):
        if ch == '<':
            val = 0
        elif ch.isdigit():
            val = int(ch)
        elif ch.isalpha():
            val = ord(ch) - ord('A') + 10
        else:
            val = 0
        total += val * weights[i % 3]
    return str(total % 10) == check_digit


def parse_mrz(mrz_lines: list) -> Optional[dict]:
    """Parst MRZ-Daten aus 2 oder 3 Zeilen (TD1/TD2/TD3 Formate)."""
    if len(mrz_lines) < 2:
        return None
    try:
        if len(mrz_lines[0]) >= 44:  # TD3 (Reisepass)
            line1 = mrz_lines[0]
            line2 = mrz_lines[1]
            doc_type = line1[0:2].replace('<', '')
            country = line1[2:5].replace('<', '')
            names = line1[5:].split('<<')
            surname = names[0].replace('<', ' ').strip() if names else ''
            given = names[1].replace('<', ' ').strip() if len(names) > 1 else ''
            passport_no = line2[0:9].replace('<', '')
            passport_check = line2[9]
            nationality = line2[10:13].replace('<', '')
            dob = line2[13:19]
            dob_check = line2[19]
            gender = line2[20]
            expiry = line2[21:27]
            expiry_check = line2[27]
            # Pruefsummen validieren
            passport_valid = validate_mrz_checksum(line2[0:9], passport_check)
            dob_valid = validate_mrz_checksum(dob, dob_check)
            expiry_valid = validate_mrz_checksum(expiry, expiry_check)
            # Datum parsen
            dob_date = _parse_mrz_date(dob)
            expiry_date = _parse_mrz_date(expiry)
            return {
                "format": "TD3",
                "document_type": doc_type,
                "issuing_country": country,
                "surname": surname,
                "given_name": given,
                "full_name": f"{given} {surname}".strip(),
                "passport_number": passport_no,
                "nationality": nationality,
                "date_of_birth": dob_date,
                "gender": {"M": "male", "F": "female"}.get(gender, "unknown"),
                "expiry_date": expiry_date,
                "checksums": {
                    "passport_valid": passport_valid,
                    "dob_valid": dob_valid,
                    "expiry_valid": expiry_valid,
                    "all_valid": passport_valid and dob_valid and expiry_valid,
                },
            }
    except Exception as e:
        logger.warning(f"[MRZ] Parse-Fehler: {e}")
    return None


def _parse_mrz_date(yymmdd: str) -> Optional[str]:
    """Konvertiert MRZ-Datum (YYMMDD) in ISO-Format."""
    if len(yymmdd) != 6 or not yymmdd.isdigit():
        return None
    yy, mm, dd = int(yymmdd[:2]), int(yymmdd[2:4]), int(yymmdd[4:6])
    year = 1900 + yy if yy > 50 else 2000 + yy
    try:
        return f"{year:04d}-{mm:02d}-{dd:02d}"
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════════════
# PLAUSIBILITAETS-CHECKS (Schritt 4)
# ══════════════════════════════════════════════════════════════════════

def check_passport_expiry(expiry_date: str, min_months: int = 6) -> dict:
    """Prueft ob der Reisepass mindestens min_months gueltig ist (Visum-Vorgabe)."""
    if not expiry_date:
        return {"valid": False, "reason": "Ablaufdatum nicht erkannt", "severity": "warning"}
    try:
        exp = datetime.strptime(expiry_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        min_date = now + timedelta(days=min_months * 30)
        remaining_days = (exp - now).days
        if exp < now:
            return {"valid": False, "reason": f"Reisepass ist abgelaufen (seit {abs(remaining_days)} Tagen)", "severity": "critical", "remaining_days": remaining_days}
        if exp < min_date:
            return {"valid": False, "reason": f"Reisepass laeuft in {remaining_days} Tagen ab (mind. {min_months} Monate erforderlich fuer Visum)", "severity": "warning", "remaining_days": remaining_days}
        return {"valid": True, "reason": f"Reisepass gueltig ({remaining_days} Tage verbleibend)", "severity": "ok", "remaining_days": remaining_days}
    except Exception:
        return {"valid": False, "reason": "Ablaufdatum nicht parsbar", "severity": "warning"}


def check_name_consistency(extracted_name: str, profile_name: str) -> dict:
    """Prueft ob der Name auf dem Dokument mit dem CRM-Profil uebereinstimmt."""
    if not extracted_name or not profile_name:
        return {"match": False, "confidence": "unknown", "reason": "Name nicht verfuegbar"}
    ext = extracted_name.lower().strip()
    prof = profile_name.lower().strip()
    if ext == prof:
        return {"match": True, "confidence": "high", "reason": "Exakte Uebereinstimmung"}
    # Teilname-Match (Vorname oder Nachname)
    ext_parts = set(ext.split())
    prof_parts = set(prof.split())
    overlap = ext_parts & prof_parts
    if len(overlap) >= 2:
        return {"match": True, "confidence": "high", "reason": f"Starke Uebereinstimmung ({len(overlap)} Namen-Teile)"}
    if len(overlap) == 1:
        return {"match": True, "confidence": "medium", "reason": f"Teilweise Uebereinstimmung ({overlap.pop()})"}
    # Levenshtein-aehnlicher Check
    if _fuzzy_name_match(ext, prof):
        return {"match": True, "confidence": "low", "reason": "Aehnliche Schreibweise (moegl. Transliteration)"}
    return {"match": False, "confidence": "high", "reason": f"Name auf Dokument '{extracted_name}' weicht von Profil '{profile_name}' ab"}


def _fuzzy_name_match(a: str, b: str) -> bool:
    """Einfacher Fuzzy-Match fuer Transliterationen (z.B. Mohammed/Mohamed)."""
    if not a or not b:
        return False
    a_clean = re.sub(r'[^a-z]', '', a)
    b_clean = re.sub(r'[^a-z]', '', b)
    if len(a_clean) < 3 or len(b_clean) < 3:
        return False
    # Gemeinsame Bigramme
    a_bigrams = set(a_clean[i:i+2] for i in range(len(a_clean)-1))
    b_bigrams = set(b_clean[i:i+2] for i in range(len(b_clean)-1))
    if not a_bigrams or not b_bigrams:
        return False
    overlap = len(a_bigrams & b_bigrams)
    total = len(a_bigrams | b_bigrams)
    return (overlap / total) > 0.5


def validate_certificate_number(cert_number: str, cert_type: str) -> dict:
    """Prueft Zertifikatsnummer-Struktur (Goethe, telc, TestDaF)."""
    if not cert_number:
        return {"valid": False, "reason": "Keine Zertifikatsnummer erkannt"}
    # Goethe: Typisch 10-15 Zeichen, alphanumerisch
    if cert_type and "goethe" in cert_type.lower():
        if re.match(r'^[A-Z0-9]{6,20}$', cert_number.replace('-', '').replace(' ', '')):
            return {"valid": True, "reason": "Goethe-Zertifikatsnummer plausibel"}
        return {"valid": False, "reason": "Goethe-Zertifikatsnummer hat ungueltiges Format"}
    # telc: Typisch mit Bindestrich, z.B. "12345678-001"
    if cert_type and "telc" in cert_type.lower():
        if re.match(r'^[0-9]{6,12}(-[0-9]{2,4})?$', cert_number.replace(' ', '')):
            return {"valid": True, "reason": "telc-Zertifikatsnummer plausibel"}
        return {"valid": False, "reason": "telc-Zertifikatsnummer hat ungueltiges Format"}
    # TestDaF: Numerisch, 8-12 Stellen
    if cert_type and "testdaf" in cert_type.lower():
        if re.match(r'^[0-9]{8,14}$', cert_number.replace(' ', '').replace('-', '')):
            return {"valid": True, "reason": "TestDaF-Nummer plausibel"}
        return {"valid": False, "reason": "TestDaF-Nummer hat ungueltiges Format"}
    # Generic
    if len(cert_number) >= 5:
        return {"valid": True, "reason": "Zertifikatsnummer vorhanden (Format unbekannt)", "confidence": "low"}
    return {"valid": False, "reason": "Zertifikatsnummer zu kurz"}


async def run_plausibility_checks(
    extracted_data: dict,
    classification: dict,
    applicant_profile: Optional[dict] = None,
    mrz_data: Optional[dict] = None,
) -> dict:
    """
    Fuehrt alle Plausibilitaets-Checks durch:
    - Reisepass-Ablauf (Visum: 6 Monate)
    - Namensabgleich CRM
    - MRZ-Validierung
    - Zertifikatsnummer-Pruefung
    """
    checks = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "all_passed": True,
        "results": [],
    }
    doc_type = classification.get("document_type", "other")

    # 1. Reisepass-Ablauf
    if doc_type == "passport":
        expiry = extracted_data.get("expiry_date")
        if not expiry and mrz_data:
            expiry = mrz_data.get("expiry_date")
        result = check_passport_expiry(expiry)
        checks["results"].append({"check": "passport_expiry", **result})
        if not result["valid"]:
            checks["all_passed"] = False

    # 2. Namensabgleich
    if applicant_profile:
        extracted_name = extracted_data.get("full_name") or ""
        if mrz_data and mrz_data.get("full_name"):
            extracted_name = mrz_data["full_name"]
        profile_name = applicant_profile.get("full_name", "")
        if extracted_name:
            result = check_name_consistency(extracted_name, profile_name)
            checks["results"].append({"check": "name_consistency", **result})
            if not result["match"] and result["confidence"] == "high":
                checks["all_passed"] = False

    # 3. MRZ-Validierung
    if mrz_data and mrz_data.get("checksums"):
        cs = mrz_data["checksums"]
        checks["results"].append({
            "check": "mrz_checksums",
            "valid": cs.get("all_valid", False),
            "reason": "MRZ-Pruefsummen " + ("alle gueltig" if cs["all_valid"] else "ungueltig"),
            "severity": "ok" if cs["all_valid"] else "warning",
            "details": cs,
        })
        if not cs.get("all_valid"):
            checks["all_passed"] = False

    # 4. Zertifikatsnummer
    if doc_type == "language_certificate":
        cert_num = extracted_data.get("certificate_number") or extracted_data.get("score")
        cert_type = extracted_data.get("certificate_type") or extracted_data.get("issuing_institution") or ""
        if cert_num:
            result = validate_certificate_number(str(cert_num), cert_type)
            checks["results"].append({"check": "certificate_number", **result})

    return checks
