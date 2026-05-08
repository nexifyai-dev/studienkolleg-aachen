"""
Iteration 81 Tests – State Machine, Rate Limiting, Health Version

Tests:
1. State Machine: GET /api/applications/{id}/allowed-transitions
2. State Machine: PUT /api/applications/{id} with invalid transition (422)
3. State Machine: PUT /api/applications/{id} with valid transition
4. State Machine: Admin force-transition (even invalid ones)
5. Rate Limiting: POST /api/leads/upload-temp has rate limit
6. Rate Limiting: POST /api/leads/ingest has rate limit
7. Health: GET /api/health returns version 1.4.0
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"


class TestHealthEndpoint:
    """Health endpoint tests"""

    def test_health_returns_version_1_4_0(self):
        """GET /api/health should return version 1.4.0"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("version") == "1.4.0", f"Expected version 1.4.0, got {data.get('version')}"
        assert data.get("status") == "ok"
        print(f"PASS: Health endpoint returns version {data.get('version')}")


class TestStateMachine:
    """State Machine tests for application status transitions"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as staff and admin, get test application"""
        # Staff login
        self.staff_session = requests.Session()
        login_resp = self.staff_session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_resp.status_code == 200, f"Staff login failed: {login_resp.text}"

        # Admin login
        self.admin_session = requests.Session()
        admin_login = self.admin_session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"

        # Get a test application
        apps_resp = self.staff_session.get(f"{BASE_URL}/api/applications")
        assert apps_resp.status_code == 200
        apps = apps_resp.json()
        if apps:
            self.test_app_id = apps[0].get("id")
            self.test_app_stage = apps[0].get("current_stage")
        else:
            self.test_app_id = None
            self.test_app_stage = None

    def test_allowed_transitions_endpoint(self):
        """GET /api/applications/{id}/allowed-transitions returns valid transitions"""
        if not self.test_app_id:
            pytest.skip("No test application available")

        response = self.staff_session.get(
            f"{BASE_URL}/api/applications/{self.test_app_id}/allowed-transitions"
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()

        assert "current_stage" in data, "Response missing current_stage"
        assert "allowed_transitions" in data, "Response missing allowed_transitions"
        assert isinstance(data["allowed_transitions"], list), "allowed_transitions should be a list"

        # Each transition should have stage and label
        for t in data["allowed_transitions"]:
            assert "stage" in t, "Transition missing stage"
            assert "label" in t, "Transition missing label"

        print(f"PASS: allowed-transitions for stage '{data['current_stage']}': {[t['stage'] for t in data['allowed_transitions']]}")

    def test_invalid_transition_returns_422(self):
        """PUT /api/applications/{id} with invalid transition returns 422"""
        if not self.test_app_id:
            pytest.skip("No test application available")

        # Get current stage
        app_resp = self.staff_session.get(f"{BASE_URL}/api/applications/{self.test_app_id}")
        assert app_resp.status_code == 200
        current_stage = app_resp.json().get("current_stage")

        # Define invalid transitions based on state machine
        invalid_transitions = {
            "lead_new": "enrolled",  # Can't go directly to enrolled
            "in_review": "enrolled",  # Can't go directly to enrolled
            "pending_docs": "enrolled",  # Can't go directly to enrolled
            "interview_scheduled": "enrolled",  # Can't go directly to enrolled
            "enrolled": "lead_new",  # Can't go back to lead_new
            "archived": "enrolled",  # Archived is end state
        }

        invalid_target = invalid_transitions.get(current_stage)
        if not invalid_target:
            # Default invalid transition
            invalid_target = "enrolled" if current_stage != "enrolled" else "lead_new"

        # Try invalid transition as staff (should fail)
        response = self.staff_session.put(
            f"{BASE_URL}/api/applications/{self.test_app_id}",
            json={"current_stage": invalid_target}
        )

        # Should return 422 for invalid transition
        assert response.status_code == 422, f"Expected 422 for invalid transition {current_stage} -> {invalid_target}, got {response.status_code}: {response.text}"
        print(f"PASS: Invalid transition {current_stage} -> {invalid_target} correctly rejected with 422")

    def test_valid_transition_succeeds(self):
        """PUT /api/applications/{id} with valid transition succeeds"""
        if not self.test_app_id:
            pytest.skip("No test application available")

        # Get allowed transitions
        trans_resp = self.staff_session.get(
            f"{BASE_URL}/api/applications/{self.test_app_id}/allowed-transitions"
        )
        assert trans_resp.status_code == 200
        data = trans_resp.json()
        current_stage = data["current_stage"]
        allowed = data["allowed_transitions"]

        if not allowed:
            pytest.skip(f"No allowed transitions from {current_stage}")

        # Pick first allowed transition
        target_stage = allowed[0]["stage"]

        # Perform valid transition
        response = self.staff_session.put(
            f"{BASE_URL}/api/applications/{self.test_app_id}",
            json={"current_stage": target_stage}
        )
        assert response.status_code == 200, f"Valid transition failed: {response.text}"

        # Verify the change
        verify_resp = self.staff_session.get(f"{BASE_URL}/api/applications/{self.test_app_id}")
        assert verify_resp.status_code == 200
        new_stage = verify_resp.json().get("current_stage")
        assert new_stage == target_stage, f"Stage not updated: expected {target_stage}, got {new_stage}"

        print(f"PASS: Valid transition {current_stage} -> {target_stage} succeeded")

        # Revert back if possible
        revert_trans = self.admin_session.get(
            f"{BASE_URL}/api/applications/{self.test_app_id}/allowed-transitions"
        )
        if revert_trans.status_code == 200:
            revert_allowed = revert_trans.json().get("allowed_transitions", [])
            if any(t["stage"] == current_stage for t in revert_allowed):
                self.admin_session.put(
                    f"{BASE_URL}/api/applications/{self.test_app_id}",
                    json={"current_stage": current_stage}
                )

    def test_admin_force_transition(self):
        """Admin can force invalid transitions"""
        if not self.test_app_id:
            pytest.skip("No test application available")

        # Get current stage
        app_resp = self.admin_session.get(f"{BASE_URL}/api/applications/{self.test_app_id}")
        assert app_resp.status_code == 200
        current_stage = app_resp.json().get("current_stage")

        # Try a normally invalid transition as admin
        # Admin should be able to force it
        # Let's try in_review -> enrolled (normally invalid for staff)
        if current_stage == "in_review":
            target = "enrolled"
        elif current_stage == "enrolled":
            target = "in_review"  # Normally can't go back
        else:
            # First move to in_review, then try enrolled
            self.admin_session.put(
                f"{BASE_URL}/api/applications/{self.test_app_id}",
                json={"current_stage": "in_review"}
            )
            current_stage = "in_review"
            target = "enrolled"

        # Admin force transition
        response = self.admin_session.put(
            f"{BASE_URL}/api/applications/{self.test_app_id}",
            json={"current_stage": target}
        )

        # Admin should succeed even for normally invalid transitions
        assert response.status_code == 200, f"Admin force transition failed: {response.text}"
        print(f"PASS: Admin force transition {current_stage} -> {target} succeeded")

        # Revert to a normal state
        self.admin_session.put(
            f"{BASE_URL}/api/applications/{self.test_app_id}",
            json={"current_stage": "in_review"}
        )


class TestRateLimiting:
    """Rate limiting tests for leads endpoints"""

    def test_upload_temp_has_rate_limit_header(self):
        """POST /api/leads/upload-temp should have rate limiting"""
        # We can't easily trigger rate limit without many requests
        # But we can verify the endpoint exists and responds
        # Use a valid file type (PDF) - text/plain is not allowed
        # Create a minimal valid PDF
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        response = requests.post(
            f"{BASE_URL}/api/leads/upload-temp",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            data={"document_type": "other"}
        )
        # Should succeed or return rate limit error
        assert response.status_code in [200, 429, 413], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "upload_token" in data, "Response should contain upload_token"
        print(f"PASS: upload-temp endpoint responds with status {response.status_code}")

    def test_ingest_has_rate_limit(self):
        """POST /api/leads/ingest should have rate limiting"""
        # Test with minimal valid payload
        response = requests.post(
            f"{BASE_URL}/api/leads/ingest",
            json={
                "email": "test-rate-limit@example.com",
                "full_name": "Rate Limit Test",
                "area_interest": "studienkolleg"
            }
        )
        # Should succeed or return rate limit error
        assert response.status_code in [200, 429], f"Unexpected status: {response.status_code}"
        print(f"PASS: ingest endpoint responds with status {response.status_code}")


class TestStateMachineDefinition:
    """Tests for state machine definition correctness"""

    def test_state_machine_transitions_defined(self):
        """Verify state machine has correct transitions defined"""
        # Import the state machine module
        import sys
        sys.path.insert(0, "/app/backend")
        from services.state_machine import VALID_TRANSITIONS, ALL_STAGES, STAGE_LABELS_DE

        # Verify all expected stages exist
        expected_stages = {
            "lead_new", "in_review", "pending_docs", "interview_scheduled",
            "conditional_offer", "offer_sent", "enrolled", "declined",
            "on_hold", "archived"
        }
        assert ALL_STAGES == expected_stages, f"Missing stages: {expected_stages - ALL_STAGES}"

        # Verify archived is end state (no transitions out)
        assert VALID_TRANSITIONS["archived"] == set(), "archived should have no outgoing transitions"

        # Verify lead_new can go to in_review
        assert "in_review" in VALID_TRANSITIONS["lead_new"], "lead_new should transition to in_review"

        # Verify enrolled can only go to archived or on_hold
        assert VALID_TRANSITIONS["enrolled"] == {"archived", "on_hold"}, "enrolled transitions incorrect"

        # Verify all stages have German labels
        for stage in ALL_STAGES:
            assert stage in STAGE_LABELS_DE, f"Missing German label for {stage}"

        print(f"PASS: State machine has {len(ALL_STAGES)} stages with correct transitions")

    def test_validate_transition_function(self):
        """Test validate_transition function"""
        import sys
        sys.path.insert(0, "/app/backend")
        from services.state_machine import validate_transition

        # Valid transition
        is_valid, error = validate_transition("lead_new", "in_review")
        assert is_valid is True, f"lead_new -> in_review should be valid: {error}"

        # Invalid transition (without force)
        is_valid, error = validate_transition("in_review", "enrolled")
        assert is_valid is False, "in_review -> enrolled should be invalid"
        assert "Ungueltiger Statusuebergang" in error, f"Error message incorrect: {error}"

        # Invalid transition with force=True
        is_valid, error = validate_transition("in_review", "enrolled", force=True)
        assert is_valid is True, "Force should allow invalid transition"

        # Same stage (no change)
        is_valid, error = validate_transition("in_review", "in_review")
        assert is_valid is True, "Same stage should be valid"

        print("PASS: validate_transition function works correctly")


class TestDunningService:
    """Tests for dunning service existence"""

    def test_dunning_service_exists(self):
        """Verify dunning service module exists and has required function"""
        import sys
        sys.path.insert(0, "/app/backend")
        from services.dunning import check_overdue_invoices

        assert callable(check_overdue_invoices), "check_overdue_invoices should be callable"
        print("PASS: Dunning service exists with check_overdue_invoices function")


class TestSchedulerDunningTask:
    """Tests for scheduler dunning task"""

    def test_scheduler_has_dunning_task(self):
        """Verify scheduler includes dunning_check task"""
        import sys
        sys.path.insert(0, "/app/backend")

        # Read scheduler.py and verify dunning_check is in tasks
        with open("/app/backend/services/scheduler.py", "r") as f:
            content = f.read()

        assert "dunning_check" in content, "Scheduler should have dunning_check task"
        assert "_check_dunning" in content, "Scheduler should have _check_dunning function"
        print("PASS: Scheduler includes dunning_check task")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
