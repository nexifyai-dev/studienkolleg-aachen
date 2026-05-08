"""
Delta Screening Feature Tests - Block 11 Layout
Tests for:
- GET /api/applications/{app_id}/screening-delta
- POST /api/applications/{app_id}/manual-rescreen
- is_screening_relevant_upload function
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDeltaScreeningEndpoints:
    """Tests for Delta Screening API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as staff and get session"""
        self.session = requests.Session()
        login_resp = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "staff@studienkolleg-aachen.de",
                "password": "DevSeed@2026!"
            }
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"
        self.staff_user = login_resp.json()
        self.test_app_id = "69cb8e9a3f026e1d41dd4800"  # Ahmed Hassan application
    
    def test_health_check(self):
        """Test backend health endpoint"""
        resp = self.session.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        print("✓ Health check passed")
    
    def test_screening_delta_endpoint_returns_200(self):
        """GET /api/applications/{app_id}/screening-delta returns 200"""
        resp = self.session.get(f"{BASE_URL}/api/applications/{self.test_app_id}/screening-delta")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ Screening delta endpoint returns 200")
    
    def test_screening_delta_response_structure(self):
        """Verify screening-delta response has correct structure"""
        resp = self.session.get(f"{BASE_URL}/api/applications/{self.test_app_id}/screening-delta")
        assert resp.status_code == 200
        data = resp.json()
        
        # Check required fields
        assert "has_screening" in data, "Missing 'has_screening' field"
        assert "delta" in data, "Missing 'delta' field"
        assert "latest" in data, "Missing 'latest' field"
        
        if data["has_screening"]:
            # Verify delta structure
            delta = data["delta"]
            assert "has_previous" in delta, "Missing 'has_previous' in delta"
            assert "changes" in delta, "Missing 'changes' in delta"
            assert "confidence" in delta, "Missing 'confidence' in delta"
            assert "risk_change" in delta, "Missing 'risk_change' in delta"
            assert "summary" in delta, "Missing 'summary' in delta"
            
            # Verify latest screening structure
            latest = data["latest"]
            assert "screening_id" in latest, "Missing 'screening_id' in latest"
            assert "application_id" in latest, "Missing 'application_id' in latest"
            assert "suggested_stage" in latest, "Missing 'suggested_stage' in latest"
            
        print("✓ Screening delta response structure is correct")
    
    def test_screening_delta_confidence_levels(self):
        """Verify confidence levels are valid"""
        resp = self.session.get(f"{BASE_URL}/api/applications/{self.test_app_id}/screening-delta")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["has_screening"] and data["delta"]:
            confidence = data["delta"]["confidence"]
            valid_levels = ["high", "medium", "low", "unknown"]
            assert confidence in valid_levels, f"Invalid confidence level: {confidence}"
            print(f"✓ Confidence level '{confidence}' is valid")
    
    def test_screening_delta_risk_change_values(self):
        """Verify risk_change values are valid"""
        resp = self.session.get(f"{BASE_URL}/api/applications/{self.test_app_id}/screening-delta")
        assert resp.status_code == 200
        data = resp.json()
        
        if data["has_screening"] and data["delta"]:
            risk_change = data["delta"]["risk_change"]
            valid_values = ["increased", "decreased", "unchanged", "mixed", "neutral"]
            assert risk_change in valid_values, f"Invalid risk_change: {risk_change}"
            print(f"✓ Risk change '{risk_change}' is valid")
    
    def test_manual_rescreen_endpoint_returns_200(self):
        """POST /api/applications/{app_id}/manual-rescreen returns 200"""
        resp = self.session.post(f"{BASE_URL}/api/applications/{self.test_app_id}/manual-rescreen")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("✓ Manual rescreen endpoint returns 200")
    
    def test_manual_rescreen_response_structure(self):
        """Verify manual-rescreen response has correct structure"""
        resp = self.session.post(f"{BASE_URL}/api/applications/{self.test_app_id}/manual-rescreen")
        assert resp.status_code == 200
        data = resp.json()
        
        # Check required fields
        assert "screening_id" in data, "Missing 'screening_id'"
        assert "application_id" in data, "Missing 'application_id'"
        assert "is_delta_screening" in data, "Missing 'is_delta_screening'"
        assert "delta" in data, "Missing 'delta'"
        assert "suggested_stage" in data, "Missing 'suggested_stage'"
        assert "trigger_reason" in data, "Missing 'trigger_reason'"
        
        # Verify it's marked as delta screening
        assert data["is_delta_screening"] == True, "Should be marked as delta screening"
        
        # Verify trigger reason
        assert "Manuelles Re-Screening" in data["trigger_reason"], "Should indicate manual trigger"
        
        print("✓ Manual rescreen response structure is correct")
    
    def test_manual_rescreen_includes_delta_comparison(self):
        """Verify manual-rescreen includes delta comparison"""
        resp = self.session.post(f"{BASE_URL}/api/applications/{self.test_app_id}/manual-rescreen")
        assert resp.status_code == 200
        data = resp.json()
        
        delta = data.get("delta", {})
        assert "has_previous" in delta, "Delta should have 'has_previous'"
        assert "changes" in delta, "Delta should have 'changes'"
        assert "confidence" in delta, "Delta should have 'confidence'"
        
        print("✓ Manual rescreen includes delta comparison")
    
    def test_screening_delta_invalid_app_id(self):
        """Test screening-delta with invalid app_id returns 400 or 404"""
        resp = self.session.get(f"{BASE_URL}/api/applications/invalid_id/screening-delta")
        assert resp.status_code in [400, 404], f"Expected 400/404, got {resp.status_code}"
        print("✓ Invalid app_id handled correctly")
    
    def test_manual_rescreen_invalid_app_id(self):
        """Test manual-rescreen with invalid app_id returns 400 or 404"""
        resp = self.session.post(f"{BASE_URL}/api/applications/invalid_id/manual-rescreen")
        assert resp.status_code in [400, 404], f"Expected 400/404, got {resp.status_code}"
        print("✓ Invalid app_id handled correctly for manual-rescreen")
    
    def test_screening_delta_requires_auth(self):
        """Test screening-delta requires authentication"""
        # Use a new session without login
        new_session = requests.Session()
        resp = new_session.get(f"{BASE_URL}/api/applications/{self.test_app_id}/screening-delta")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print("✓ Screening delta requires authentication")
    
    def test_manual_rescreen_requires_auth(self):
        """Test manual-rescreen requires authentication"""
        # Use a new session without login
        new_session = requests.Session()
        resp = new_session.post(f"{BASE_URL}/api/applications/{self.test_app_id}/manual-rescreen")
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print("✓ Manual rescreen requires authentication")


class TestIsScreeningRelevantUpload:
    """Tests for is_screening_relevant_upload function"""
    
    def test_relevant_doc_types(self):
        """Test that relevant document types return True"""
        from services.delta_screening import is_screening_relevant_upload
        
        relevant_types = [
            "passport", "transcript", "language_certificate", 
            "highschool_diploma", "degree_certificate", "cv",
            "motivation_letter", "recommendation", "visa", "financial_proof"
        ]
        
        for doc_type in relevant_types:
            result = is_screening_relevant_upload(doc_type)
            assert result == True, f"Expected True for '{doc_type}', got {result}"
        
        print(f"✓ All {len(relevant_types)} relevant doc types return True")
    
    def test_irrelevant_doc_types(self):
        """Test that irrelevant document types return False"""
        from services.delta_screening import is_screening_relevant_upload
        
        irrelevant_types = ["other", "random_type", "photo", "receipt", "invoice"]
        
        for doc_type in irrelevant_types:
            result = is_screening_relevant_upload(doc_type)
            assert result == False, f"Expected False for '{doc_type}', got {result}"
        
        print(f"✓ All {len(irrelevant_types)} irrelevant doc types return False")


class TestComputeDelta:
    """Tests for compute_delta function"""
    
    def test_compute_delta_no_previous(self):
        """Test compute_delta with no previous screening"""
        from services.delta_screening import compute_delta
        
        current = {"is_complete": True, "suggested_stage": "eligible"}
        delta = compute_delta(None, current)
        
        assert delta["has_previous"] == False
        assert delta["is_initial"] == True
        assert delta["changes"] == []
        assert "Erstbewertung" in delta["summary"]
        
        print("✓ compute_delta handles no previous screening correctly")
    
    def test_compute_delta_no_changes(self):
        """Test compute_delta with identical screenings"""
        from services.delta_screening import compute_delta
        
        previous = {
            "is_complete": True,
            "missing_documents": [],
            "anabin_category": "H+",
            "language_level_ok": True,
            "suggested_stage": "eligible"
        }
        current = previous.copy()
        
        delta = compute_delta(previous, current)
        
        assert delta["has_previous"] == True
        assert delta["changes"] == []
        assert delta["risk_change"] == "unchanged"
        assert delta["confidence"] == "high"
        
        print("✓ compute_delta handles no changes correctly")
    
    def test_compute_delta_positive_change(self):
        """Test compute_delta with positive change (completeness improved)"""
        from services.delta_screening import compute_delta
        
        previous = {"is_complete": False, "missing_documents": ["passport"]}
        current = {"is_complete": True, "missing_documents": []}
        
        delta = compute_delta(previous, current)
        
        assert delta["has_previous"] == True
        assert len(delta["changes"]) > 0
        assert delta["positive_count"] > 0
        assert delta["risk_change"] == "decreased"
        assert delta["confidence"] == "high"
        
        print("✓ compute_delta handles positive changes correctly")
    
    def test_compute_delta_negative_change(self):
        """Test compute_delta with negative change"""
        from services.delta_screening import compute_delta
        
        previous = {"is_complete": True, "missing_documents": []}
        current = {"is_complete": False, "missing_documents": ["passport"]}
        
        delta = compute_delta(previous, current)
        
        assert delta["has_previous"] == True
        assert len(delta["changes"]) > 0
        assert delta["negative_count"] > 0
        assert delta["risk_change"] == "increased"
        assert delta["confidence"] == "low"
        
        print("✓ compute_delta handles negative changes correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
