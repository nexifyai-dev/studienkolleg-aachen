"""
Iteration 93: Document Ingestion & Plausibility Engine Tests (v2.2)

Tests for:
1. Ingestion & Normalization: strip_exif, normalize_image_dpi, preprocess_document
2. MRZ Detection & Parsing: detect_mrz_lines, parse_mrz, validate_mrz_checksum (TD3 format)
3. Plausibility Checks: check_passport_expiry, check_name_consistency, validate_certificate_number
4. Pipeline Integration: validate_document_with_ai includes ingestion, MRZ, plausibility
"""
import pytest
import os
import sys
from datetime import datetime, timedelta, timezone

# Add backend to path
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://live-demo-fix.preview.emergentagent.com').rstrip('/')


# ══════════════════════════════════════════════════════════════════════
# UNIT TESTS: Document Ingestion Functions
# ══════════════════════════════════════════════════════════════════════

class TestStripExif:
    """Tests for EXIF stripping function"""
    
    def test_strip_exif_non_image_returns_unchanged(self):
        """Non-image content types should return data unchanged"""
        from services.document_ingestion import strip_exif
        
        data = b"PDF content here"
        result = strip_exif(data, "application/pdf")
        assert result == data
        print("PASS: strip_exif returns unchanged data for non-image content types")
    
    def test_strip_exif_empty_content_type(self):
        """Empty content type should return data unchanged"""
        from services.document_ingestion import strip_exif
        
        data = b"some data"
        result = strip_exif(data, "")
        assert result == data
        result2 = strip_exif(data, None)
        assert result2 == data
        print("PASS: strip_exif handles empty/None content types")


class TestNormalizeDpi:
    """Tests for DPI normalization function"""
    
    def test_normalize_dpi_non_image_returns_unchanged(self):
        """Non-image content types should return data unchanged"""
        from services.document_ingestion import normalize_image_dpi
        
        data = b"PDF content here"
        result = normalize_image_dpi(data, "application/pdf")
        assert result == data
        print("PASS: normalize_image_dpi returns unchanged data for non-image content types")
    
    def test_normalize_dpi_empty_content_type(self):
        """Empty content type should return data unchanged"""
        from services.document_ingestion import normalize_image_dpi
        
        data = b"some data"
        result = normalize_image_dpi(data, "")
        assert result == data
        print("PASS: normalize_image_dpi handles empty content types")


class TestPreprocessDocument:
    """Tests for combined preprocessing function"""
    
    def test_preprocess_non_image_returns_unchanged(self):
        """Non-image files should pass through unchanged"""
        from services.document_ingestion import preprocess_document
        
        data = b"PDF content"
        result = preprocess_document(data, "application/pdf")
        assert result == data
        print("PASS: preprocess_document returns unchanged data for PDFs")
    
    def test_preprocess_empty_content_type(self):
        """Empty content type should return data unchanged"""
        from services.document_ingestion import preprocess_document
        
        data = b"some data"
        result = preprocess_document(data, "")
        assert result == data
        result2 = preprocess_document(data, None)
        assert result2 == data
        print("PASS: preprocess_document handles empty/None content types")


# ══════════════════════════════════════════════════════════════════════
# UNIT TESTS: MRZ Detection & Parsing
# ══════════════════════════════════════════════════════════════════════

class TestMrzDetection:
    """Tests for MRZ line detection"""
    
    def test_detect_mrz_lines_empty_text(self):
        """Empty text should return empty list"""
        from services.document_ingestion import detect_mrz_lines
        
        assert detect_mrz_lines("") == []
        assert detect_mrz_lines(None) == []
        print("PASS: detect_mrz_lines handles empty/None text")
    
    def test_detect_mrz_lines_valid_td3(self):
        """Should detect valid TD3 MRZ lines"""
        from services.document_ingestion import detect_mrz_lines
        
        text = """
        Some header text
        P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<
        L898902C<3UTO6908061F9406236ZE184226B<<<<<14
        Some footer text
        """
        lines = detect_mrz_lines(text)
        assert len(lines) == 2
        assert "ERIKSSON" in lines[0]
        assert "L898902C" in lines[1]
        print("PASS: detect_mrz_lines correctly detects TD3 MRZ lines")
    
    def test_detect_mrz_lines_no_mrz(self):
        """Text without MRZ should return empty list"""
        from services.document_ingestion import detect_mrz_lines
        
        text = "This is just regular text without any MRZ data"
        lines = detect_mrz_lines(text)
        assert lines == []
        print("PASS: detect_mrz_lines returns empty for non-MRZ text")


class TestMrzChecksum:
    """Tests for MRZ checksum validation (ICAO 9303)"""
    
    def test_validate_mrz_checksum_valid(self):
        """Valid checksum should return True"""
        from services.document_ingestion import validate_mrz_checksum
        
        # Test with known valid data: L898902C with check digit 3
        result = validate_mrz_checksum("L898902C<", "3")
        assert result == True
        print("PASS: validate_mrz_checksum validates correct checksum")
    
    def test_validate_mrz_checksum_invalid(self):
        """Invalid checksum should return False"""
        from services.document_ingestion import validate_mrz_checksum
        
        # Wrong check digit
        result = validate_mrz_checksum("L898902C<", "5")
        assert result == False
        print("PASS: validate_mrz_checksum rejects invalid checksum")
    
    def test_validate_mrz_checksum_special_chars(self):
        """Should handle < filler characters correctly"""
        from services.document_ingestion import validate_mrz_checksum
        
        # < should be treated as 0
        result = validate_mrz_checksum("<<<<<<", "0")
        assert result == True
        print("PASS: validate_mrz_checksum handles filler characters")


class TestMrzParsing:
    """Tests for MRZ parsing (TD3 passport format)"""
    
    def test_parse_mrz_valid_td3(self):
        """Should correctly parse TD3 passport MRZ"""
        from services.document_ingestion import parse_mrz
        
        # Standard ICAO example MRZ
        mrz_lines = [
            'P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<',
            'L898902C<3UTO6908061F9406236ZE184226B<<<<<14'
        ]
        result = parse_mrz(mrz_lines)
        
        assert result is not None
        assert result["format"] == "TD3"
        assert result["document_type"] == "P"
        assert result["issuing_country"] == "UTO"
        assert result["surname"] == "ERIKSSON"
        assert result["given_name"] == "ANNA MARIA"
        assert result["full_name"] == "ANNA MARIA ERIKSSON"
        assert result["passport_number"] == "L898902C"
        assert result["nationality"] == "UTO"
        assert result["gender"] == "female"
        assert result["date_of_birth"] == "1969-08-06"
        assert result["expiry_date"] == "1994-06-23"
        assert "checksums" in result
        print("PASS: parse_mrz correctly parses TD3 passport MRZ")
        print(f"  - Full name: {result['full_name']}")
        print(f"  - Passport: {result['passport_number']}")
        print(f"  - DOB: {result['date_of_birth']}")
        print(f"  - Expiry: {result['expiry_date']}")
    
    def test_parse_mrz_insufficient_lines(self):
        """Should return None for insufficient MRZ lines"""
        from services.document_ingestion import parse_mrz
        
        result = parse_mrz(['P<UTOERIKSSON<<ANNA<MARIA<<<<<<<<<<<<<<<<<<<'])
        assert result is None
        
        result2 = parse_mrz([])
        assert result2 is None
        print("PASS: parse_mrz returns None for insufficient lines")


# ══════════════════════════════════════════════════════════════════════
# UNIT TESTS: Plausibility Checks
# ══════════════════════════════════════════════════════════════════════

class TestPassportExpiry:
    """Tests for passport expiry validation (6-month visa requirement)"""
    
    def test_check_passport_expiry_valid_future(self):
        """Passport valid for > 6 months should pass"""
        from services.document_ingestion import check_passport_expiry
        
        # 1 year from now
        future_date = (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%d")
        result = check_passport_expiry(future_date)
        
        assert result["valid"] == True
        assert result["severity"] == "ok"
        assert result["remaining_days"] > 180
        print(f"PASS: check_passport_expiry validates passport with {result['remaining_days']} days remaining")
    
    def test_check_passport_expiry_less_than_6_months(self):
        """Passport expiring in < 6 months should fail"""
        from services.document_ingestion import check_passport_expiry
        
        # 3 months from now
        near_date = (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d")
        result = check_passport_expiry(near_date)
        
        assert result["valid"] == False
        assert result["severity"] == "warning"
        assert "mind. 6 Monate" in result["reason"]
        print(f"PASS: check_passport_expiry rejects passport expiring in {result['remaining_days']} days")
    
    def test_check_passport_expiry_already_expired(self):
        """Expired passport should fail with critical severity"""
        from services.document_ingestion import check_passport_expiry
        
        # 1 month ago
        past_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        result = check_passport_expiry(past_date)
        
        assert result["valid"] == False
        assert result["severity"] == "critical"
        assert "abgelaufen" in result["reason"]
        print("PASS: check_passport_expiry rejects expired passport with critical severity")
    
    def test_check_passport_expiry_empty_date(self):
        """Empty date should return warning"""
        from services.document_ingestion import check_passport_expiry
        
        result = check_passport_expiry("")
        assert result["valid"] == False
        assert "nicht erkannt" in result["reason"]
        
        result2 = check_passport_expiry(None)
        assert result2["valid"] == False
        print("PASS: check_passport_expiry handles empty/None dates")


class TestNameConsistency:
    """Tests for name consistency check (CRM profile matching)"""
    
    def test_check_name_consistency_exact_match(self):
        """Exact name match should return high confidence"""
        from services.document_ingestion import check_name_consistency
        
        result = check_name_consistency("Anna Maria Eriksson", "Anna Maria Eriksson")
        
        assert result["match"] == True
        assert result["confidence"] == "high"
        assert "Exakte" in result["reason"]
        print("PASS: check_name_consistency detects exact match")
    
    def test_check_name_consistency_partial_match(self):
        """Partial name match (2+ parts) should return high confidence"""
        from services.document_ingestion import check_name_consistency
        
        result = check_name_consistency("Anna Maria Eriksson", "Anna Eriksson")
        
        assert result["match"] == True
        assert result["confidence"] == "high"
        assert "Starke" in result["reason"]
        print("PASS: check_name_consistency detects partial match with 2+ parts")
    
    def test_check_name_consistency_single_part_match(self):
        """Single part match should return medium confidence"""
        from services.document_ingestion import check_name_consistency
        
        result = check_name_consistency("Anna Maria Eriksson", "Anna Schmidt")
        
        assert result["match"] == True
        assert result["confidence"] == "medium"
        print("PASS: check_name_consistency detects single part match")
    
    def test_check_name_consistency_no_match(self):
        """No match should return high confidence mismatch"""
        from services.document_ingestion import check_name_consistency
        
        result = check_name_consistency("Anna Maria Eriksson", "John Smith")
        
        assert result["match"] == False
        assert result["confidence"] == "high"
        assert "weicht" in result["reason"]
        print("PASS: check_name_consistency detects name mismatch")
    
    def test_check_name_consistency_empty_names(self):
        """Empty names should return unknown confidence"""
        from services.document_ingestion import check_name_consistency
        
        result = check_name_consistency("", "Anna Eriksson")
        assert result["match"] == False
        assert result["confidence"] == "unknown"
        
        result2 = check_name_consistency("Anna Eriksson", "")
        assert result2["match"] == False
        print("PASS: check_name_consistency handles empty names")
    
    def test_check_name_consistency_fuzzy_match(self):
        """Similar names (transliteration) should match with low confidence"""
        from services.document_ingestion import check_name_consistency
        
        # Mohammed vs Mohamed (common transliteration)
        result = check_name_consistency("Mohammed Ahmed", "Mohamed Ahmed")
        
        # Should match due to fuzzy matching
        assert result["match"] == True
        print(f"PASS: check_name_consistency handles transliteration (confidence: {result['confidence']})")


class TestCertificateNumberValidation:
    """Tests for certificate number structure validation"""
    
    def test_validate_goethe_certificate_valid(self):
        """Valid Goethe certificate number should pass"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("ABC123456789", "Goethe-Institut")
        
        assert result["valid"] == True
        assert "Goethe" in result["reason"]
        print("PASS: validate_certificate_number accepts valid Goethe number")
    
    def test_validate_goethe_certificate_invalid(self):
        """Invalid Goethe certificate number should fail"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("AB", "Goethe-Institut")
        
        assert result["valid"] == False
        print("PASS: validate_certificate_number rejects invalid Goethe number")
    
    def test_validate_telc_certificate_valid(self):
        """Valid telc certificate number should pass"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("12345678-001", "telc Deutsch B2")
        
        assert result["valid"] == True
        assert "telc" in result["reason"]
        print("PASS: validate_certificate_number accepts valid telc number")
    
    def test_validate_telc_certificate_invalid(self):
        """Invalid telc certificate number should fail"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("ABC", "telc Deutsch B2")
        
        assert result["valid"] == False
        print("PASS: validate_certificate_number rejects invalid telc number")
    
    def test_validate_testdaf_certificate_valid(self):
        """Valid TestDaF certificate number should pass"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("12345678901", "TestDaF")
        
        assert result["valid"] == True
        assert "TestDaF" in result["reason"]
        print("PASS: validate_certificate_number accepts valid TestDaF number")
    
    def test_validate_testdaf_certificate_invalid(self):
        """Invalid TestDaF certificate number should fail"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("12345", "TestDaF")
        
        assert result["valid"] == False
        print("PASS: validate_certificate_number rejects invalid TestDaF number")
    
    def test_validate_certificate_empty(self):
        """Empty certificate number should fail"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("", "Goethe")
        
        assert result["valid"] == False
        assert "Keine" in result["reason"] or "nicht" in result["reason"].lower()
        print("PASS: validate_certificate_number handles empty numbers")
    
    def test_validate_certificate_generic(self):
        """Unknown certificate type with valid length should pass with low confidence"""
        from services.document_ingestion import validate_certificate_number
        
        result = validate_certificate_number("ABCDE12345", "Unknown Institute")
        
        assert result["valid"] == True
        assert result.get("confidence") == "low"
        print("PASS: validate_certificate_number handles unknown certificate types")


# ══════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS: Plausibility Checks Orchestration
# ══════════════════════════════════════════════════════════════════════

class TestRunPlausibilityChecks:
    """Tests for the orchestrated plausibility checks"""
    
    def test_run_plausibility_checks_passport(self):
        """Should run passport-specific checks"""
        import asyncio
        from services.document_ingestion import run_plausibility_checks
        
        # Valid passport expiry
        future_date = (datetime.now(timezone.utc) + timedelta(days=365)).strftime("%Y-%m-%d")
        
        extracted_data = {
            "full_name": "Anna Eriksson",
            "expiry_date": future_date,
        }
        classification = {"document_type": "passport"}
        applicant_profile = {"full_name": "Anna Eriksson"}
        
        result = asyncio.get_event_loop().run_until_complete(
            run_plausibility_checks(
                extracted_data=extracted_data,
                classification=classification,
                applicant_profile=applicant_profile,
            )
        )
        
        assert "timestamp" in result
        assert "all_passed" in result
        assert "results" in result
        assert result["all_passed"] == True
        
        # Should have passport_expiry and name_consistency checks
        check_types = [r["check"] for r in result["results"]]
        assert "passport_expiry" in check_types
        assert "name_consistency" in check_types
        print("PASS: run_plausibility_checks runs passport-specific checks")
        print(f"  - Checks run: {check_types}")
    
    def test_run_plausibility_checks_passport_expired(self):
        """Should fail for expired passport"""
        import asyncio
        from services.document_ingestion import run_plausibility_checks
        
        # Expired passport
        past_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        
        extracted_data = {"expiry_date": past_date}
        classification = {"document_type": "passport"}
        
        result = asyncio.get_event_loop().run_until_complete(
            run_plausibility_checks(
                extracted_data=extracted_data,
                classification=classification,
            )
        )
        
        assert result["all_passed"] == False
        
        # Find passport_expiry check
        expiry_check = next((r for r in result["results"] if r["check"] == "passport_expiry"), None)
        assert expiry_check is not None
        assert expiry_check["valid"] == False
        print("PASS: run_plausibility_checks fails for expired passport")
    
    def test_run_plausibility_checks_with_mrz(self):
        """Should include MRZ checksum validation"""
        import asyncio
        from services.document_ingestion import run_plausibility_checks
        
        extracted_data = {"full_name": "Anna Eriksson"}
        classification = {"document_type": "passport"}
        mrz_data = {
            "full_name": "Anna Eriksson",
            "checksums": {
                "passport_valid": True,
                "dob_valid": True,
                "expiry_valid": True,
                "all_valid": True,
            }
        }
        
        result = asyncio.get_event_loop().run_until_complete(
            run_plausibility_checks(
                extracted_data=extracted_data,
                classification=classification,
                mrz_data=mrz_data,
            )
        )
        
        # Should have mrz_checksums check
        check_types = [r["check"] for r in result["results"]]
        assert "mrz_checksums" in check_types
        
        mrz_check = next((r for r in result["results"] if r["check"] == "mrz_checksums"), None)
        assert mrz_check["valid"] == True
        print("PASS: run_plausibility_checks includes MRZ checksum validation")
    
    def test_run_plausibility_checks_language_certificate(self):
        """Should run certificate number validation for language certificates"""
        import asyncio
        from services.document_ingestion import run_plausibility_checks
        
        extracted_data = {
            "certificate_number": "ABC123456789",
            "certificate_type": "Goethe-Institut",
        }
        classification = {"document_type": "language_certificate"}
        
        result = asyncio.get_event_loop().run_until_complete(
            run_plausibility_checks(
                extracted_data=extracted_data,
                classification=classification,
            )
        )
        
        check_types = [r["check"] for r in result["results"]]
        assert "certificate_number" in check_types
        print("PASS: run_plausibility_checks validates certificate numbers")


# ══════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS: Pipeline Version & Structure
# ══════════════════════════════════════════════════════════════════════

class TestPipelineVersion:
    """Tests for pipeline version and structure"""
    
    def test_pipeline_version_in_code(self):
        """Pipeline version should be v2.2_full_pipeline"""
        from services.document_validation import validate_document_with_ai
        import inspect
        
        source = inspect.getsource(validate_document_with_ai)
        assert "v2.2_full_pipeline" in source
        print("PASS: Pipeline version v2.2_full_pipeline is in code")
    
    def test_pipeline_imports_ingestion(self):
        """Pipeline should import preprocess_document"""
        from services.document_validation import validate_document_with_ai
        import inspect
        
        source = inspect.getsource(validate_document_with_ai)
        assert "preprocess_document" in source
        print("PASS: Pipeline imports preprocess_document")
    
    def test_pipeline_imports_mrz(self):
        """Pipeline should import MRZ functions"""
        from services.document_validation import validate_document_with_ai
        import inspect
        
        source = inspect.getsource(validate_document_with_ai)
        assert "detect_mrz_lines" in source
        assert "parse_mrz" in source
        print("PASS: Pipeline imports MRZ functions")
    
    def test_pipeline_imports_plausibility(self):
        """Pipeline should import run_plausibility_checks"""
        from services.document_validation import validate_document_with_ai
        import inspect
        
        source = inspect.getsource(validate_document_with_ai)
        assert "run_plausibility_checks" in source
        print("PASS: Pipeline imports run_plausibility_checks")


# ══════════════════════════════════════════════════════════════════════
# API TESTS: Document Validation Endpoint
# ══════════════════════════════════════════════════════════════════════

class TestDocumentValidationAPI:
    """Tests for document validation API endpoints"""
    
    def test_health_endpoint(self):
        """Backend should be healthy"""
        import requests
        
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("PASS: Backend health check passes")
    
    def test_login_staff(self):
        """Staff login should work"""
        import requests
        
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "staff@studienkolleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Cookie-based auth returns user data, not token
        assert "id" in data or "email" in data
        print("PASS: Staff login works")


# ══════════════════════════════════════════════════════════════════════
# FUNCTION EXISTENCE TESTS
# ══════════════════════════════════════════════════════════════════════

class TestFunctionExistence:
    """Tests that all required functions exist"""
    
    def test_ingestion_functions_exist(self):
        """All ingestion functions should exist"""
        from services.document_ingestion import (
            strip_exif,
            normalize_image_dpi,
            preprocess_document,
        )
        assert callable(strip_exif)
        assert callable(normalize_image_dpi)
        assert callable(preprocess_document)
        print("PASS: All ingestion functions exist")
    
    def test_mrz_functions_exist(self):
        """All MRZ functions should exist"""
        from services.document_ingestion import (
            detect_mrz_lines,
            parse_mrz,
            validate_mrz_checksum,
        )
        assert callable(detect_mrz_lines)
        assert callable(parse_mrz)
        assert callable(validate_mrz_checksum)
        print("PASS: All MRZ functions exist")
    
    def test_plausibility_functions_exist(self):
        """All plausibility functions should exist"""
        from services.document_ingestion import (
            check_passport_expiry,
            check_name_consistency,
            validate_certificate_number,
            run_plausibility_checks,
        )
        assert callable(check_passport_expiry)
        assert callable(check_name_consistency)
        assert callable(validate_certificate_number)
        assert callable(run_plausibility_checks)
        print("PASS: All plausibility functions exist")
    
    def test_validation_pipeline_exists(self):
        """validate_document_with_ai should exist"""
        from services.document_validation import validate_document_with_ai
        assert callable(validate_document_with_ai)
        print("PASS: validate_document_with_ai exists")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
