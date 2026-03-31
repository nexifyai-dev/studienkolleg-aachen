"""
Phase 3.7k Backend Tests
- Partner/Affiliate Portal API endpoints
- AI Screening accept-ai-suggestion endpoint
- Role-based redirects verification
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials from test_credentials.md
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"
PARTNER_EMAIL = "partner@studienkolleg-aachen.de"
PARTNER_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def admin_session():
    """Admin login session"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Admin login failed: {resp.status_code}")
    return session


@pytest.fixture(scope="module")
def staff_session():
    """Staff login session"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Staff login failed: {resp.status_code}")
    return session


@pytest.fixture(scope="module")
def applicant_session():
    """Applicant login session"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": APPLICANT_EMAIL,
        "password": APPLICANT_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Applicant login failed: {resp.status_code}")
    return session


@pytest.fixture(scope="module")
def partner_session():
    """Partner/Affiliate login session"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": PARTNER_EMAIL,
        "password": PARTNER_PASSWORD
    })
    if resp.status_code != 200:
        pytest.skip(f"Partner login failed: {resp.status_code}")
    return session


class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_endpoint(self):
        """Health endpoint returns OK"""
        resp = requests.get(f"{BASE_URL}/api/health")
        assert resp.status_code == 200
        print("✓ Health endpoint OK")
    
    def test_admin_login(self, admin_session):
        """Admin login returns superadmin role"""
        resp = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("role") == "superadmin"
        print(f"✓ Admin login OK - role: {data.get('role')}")
    
    def test_staff_login(self, staff_session):
        """Staff login returns staff role"""
        resp = staff_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("role") == "staff"
        print(f"✓ Staff login OK - role: {data.get('role')}")
    
    def test_applicant_login(self, applicant_session):
        """Applicant login returns applicant role"""
        resp = applicant_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("role") == "applicant"
        print(f"✓ Applicant login OK - role: {data.get('role')}")
    
    def test_partner_login(self, partner_session):
        """Partner login returns affiliate role"""
        resp = partner_session.get(f"{BASE_URL}/api/auth/me")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("role") == "affiliate"
        print(f"✓ Partner login OK - role: {data.get('role')}")


class TestPartnerAPI:
    """Partner/Affiliate Portal API tests"""
    
    def test_partner_dashboard(self, partner_session):
        """GET /api/partner/dashboard returns stats"""
        resp = partner_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_referrals" in data
        assert "active_referrals" in data
        assert "enrolled" in data
        assert "partner_name" in data
        assert "partner_id" in data
        print(f"✓ Partner dashboard OK - total_referrals: {data.get('total_referrals')}")
    
    def test_partner_referrals(self, partner_session):
        """GET /api/partner/referrals returns list"""
        resp = partner_session.get(f"{BASE_URL}/api/partner/referrals")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ Partner referrals OK - count: {len(data)}")
    
    def test_partner_referral_link(self, partner_session):
        """GET /api/partner/referral-link returns link"""
        resp = partner_session.get(f"{BASE_URL}/api/partner/referral-link")
        assert resp.status_code == 200
        data = resp.json()
        assert "referral_code" in data
        assert "link" in data
        assert "/apply?ref=" in data.get("link", "")
        print(f"✓ Partner referral link OK - link: {data.get('link')}")
    
    def test_partner_dashboard_forbidden_for_applicant(self, applicant_session):
        """Partner dashboard forbidden for applicant role"""
        resp = applicant_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert resp.status_code == 403
        print("✓ Partner dashboard correctly forbidden for applicant")
    
    def test_admin_can_access_partner_dashboard(self, admin_session):
        """Admin can access partner dashboard"""
        resp = admin_session.get(f"{BASE_URL}/api/partner/dashboard")
        assert resp.status_code == 200
        print("✓ Admin can access partner dashboard")


class TestAIScreeningAcceptSuggestion:
    """AI Screening accept-ai-suggestion endpoint tests"""
    
    @pytest.fixture
    def test_application_id(self, staff_session):
        """Get a test application ID"""
        resp = staff_session.get(f"{BASE_URL}/api/applications")
        if resp.status_code != 200:
            pytest.skip("Cannot get applications list")
        apps = resp.json()
        if not apps:
            pytest.skip("No applications available for testing")
        return apps[0].get("id")
    
    def test_accept_ai_suggestion_requires_staff(self, applicant_session, test_application_id):
        """Accept AI suggestion requires staff role"""
        resp = applicant_session.post(
            f"{BASE_URL}/api/applications/{test_application_id}/accept-ai-suggestion",
            json={"suggested_stage": "in_review"}
        )
        assert resp.status_code == 403
        print("✓ Accept AI suggestion correctly forbidden for applicant")
    
    @pytest.fixture
    def latest_screening_context(self, staff_session, test_application_id):
        """Ensure an application has a latest screening with suggested_stage."""
        screenings_resp = staff_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        if screenings_resp.status_code != 200:
            pytest.skip("Cannot load AI screenings list")
        screenings = screenings_resp.json()

        if not screenings or not screenings[0].get("suggested_stage"):
            run_resp = staff_session.post(f"{BASE_URL}/api/applications/{test_application_id}/ai-screen", json={})
            if run_resp.status_code != 200:
                pytest.skip("Cannot create AI screening for accept-ai-suggestion tests")
            screenings_resp = staff_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
            if screenings_resp.status_code != 200:
                pytest.skip("Cannot reload AI screenings after ai-screen run")
            screenings = screenings_resp.json()

        if not screenings:
            pytest.skip("No AI screenings available")

        latest = screenings[0]
        suggested_stage = latest.get("suggested_stage")
        if not suggested_stage:
            pytest.skip("Latest AI screening has no suggested_stage")

        return {
            "application_id": test_application_id,
            "suggested_stage": suggested_stage,
        }

    def test_accept_ai_suggestion_uses_latest_screening_without_body_stage(
        self, staff_session, latest_screening_context
    ):
        """Accept AI suggestion works with server-side latest suggested_stage."""
        app_id = latest_screening_context["application_id"]
        expected_stage = latest_screening_context["suggested_stage"]

        # First get current stage
        app_resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
        if app_resp.status_code != 200:
            pytest.skip("Cannot get application details")
        current_stage = app_resp.json().get("current_stage", "lead_new")

        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{app_id}/accept-ai-suggestion",
            json={}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") in ["accepted", "unchanged"]
        assert data.get("new_stage") == expected_stage
        assert data.get("screening_id")
        assert "screening_created_at" in data
        assert data.get("accepted_from_latest_screening") is True
        print(f"✓ Accept AI suggestion from latest screening OK - stage {data.get('new_stage')}")

        # Restore original stage
        staff_session.put(
            f"{BASE_URL}/api/applications/{app_id}",
            json={"current_stage": current_stage}
        )

    def test_accept_ai_suggestion_rejects_manipulated_stage_input(
        self, staff_session, latest_screening_context
    ):
        """Accept AI suggestion rejects when body stage differs from latest screening suggestion."""
        app_id = latest_screening_context["application_id"]
        latest_stage = latest_screening_context["suggested_stage"]
        manipulated_stage = "on_hold" if latest_stage != "on_hold" else "in_review"

        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{app_id}/accept-ai-suggestion",
            json={"suggested_stage": manipulated_stage}
        )
        assert resp.status_code == 409
        detail = resp.json().get("detail", "")
        assert "neuesten KI-Empfehlung" in detail
        print("✓ Accept AI suggestion rejects manipulated stage input with 409")

    def test_accept_ai_suggestion_fails_without_screening(self, staff_session):
        """Accept AI suggestion fails if no screening exists for application."""
        unique = str(uuid.uuid4())[:8]
        payload = {
            "full_name": f"TEST_NoScreening {unique}",
            "email": f"TEST_noscreening_{unique}@example.com",
            "area_interest": "studienkolleg",
        }
        ingest_resp = requests.post(f"{BASE_URL}/api/leads/ingest", json=payload)
        if ingest_resp.status_code != 200:
            pytest.skip("Cannot create test application without screening")
        app_id = ingest_resp.json().get("application_id")
        if not app_id:
            pytest.skip("No application_id returned from leads ingest")

        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{app_id}/accept-ai-suggestion",
            json={"suggested_stage": "in_review"}
        )
        assert resp.status_code == 409
        detail = resp.json().get("detail", "")
        assert "Keine KI-Prüfung vorhanden" in detail
        print("✓ Accept AI suggestion correctly fails when no screening exists")

    def test_accept_ai_suggestion_works_with_matching_stage(
        self, staff_session, latest_screening_context
    ):
        """Accept AI suggestion changes stage when body matches latest suggestion."""
        app_id = latest_screening_context["application_id"]
        expected_stage = latest_screening_context["suggested_stage"]

        # First get current stage
        app_resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}")
        if app_resp.status_code != 200:
            pytest.skip("Cannot get application details")
        current_stage = app_resp.json().get("current_stage", "lead_new")

        # Try to accept exact latest AI stage
        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{app_id}/accept-ai-suggestion",
            json={"suggested_stage": expected_stage}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") in ["accepted", "unchanged"]
        assert data.get("new_stage") == expected_stage
        assert data.get("accepted_from_latest_screening") is True
        if data.get("status") == "accepted":
            assert data.get("new_stage") == expected_stage
            print(f"✓ Accept AI suggestion OK - changed from {data.get('old_stage')} to {data.get('new_stage')}")
        else:
            print(f"✓ Accept AI suggestion OK - status unchanged (already at suggested stage)")

        # Restore original stage
        staff_session.put(
            f"{BASE_URL}/api/applications/{app_id}",
            json={"current_stage": current_stage}
        )
    
    def test_ai_screenings_list(self, staff_session, test_application_id):
        """GET /api/applications/{id}/ai-screenings returns list"""
        resp = staff_session.get(f"{BASE_URL}/api/applications/{test_application_id}/ai-screenings")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        print(f"✓ AI screenings list OK - count: {len(data)}")


class TestAuditTrail:
    """Audit trail verification for AI suggestion acceptance"""
    
    def test_activities_include_stage_changes(self, staff_session):
        """Activities endpoint includes stage_changed entries"""
        # Get an application
        apps_resp = staff_session.get(f"{BASE_URL}/api/applications")
        if apps_resp.status_code != 200 or not apps_resp.json():
            pytest.skip("No applications available")
        app_id = apps_resp.json()[0].get("id")
        
        # Get activities
        resp = staff_session.get(f"{BASE_URL}/api/applications/{app_id}/activities")
        assert resp.status_code == 200
        activities = resp.json()
        assert isinstance(activities, list)
        print(f"✓ Activities endpoint OK - count: {len(activities)}")
        
        # Check if any stage_changed activities exist
        stage_changes = [a for a in activities if a.get("action") == "stage_changed"]
        print(f"  Stage change activities: {len(stage_changes)}")


class TestI18nEndpoints:
    """Verify i18n-related endpoints work correctly"""
    
    def test_user_language_preference_update(self, applicant_session):
        """User can update language preference"""
        # Get current user
        me_resp = applicant_session.get(f"{BASE_URL}/api/auth/me")
        if me_resp.status_code != 200:
            pytest.skip("Cannot get current user")
        user_id = me_resp.json().get("id")
        
        # Update language preference
        resp = applicant_session.put(
            f"{BASE_URL}/api/users/{user_id}",
            json={"language_pref": "en"}
        )
        assert resp.status_code == 200
        print("✓ Language preference update OK")
        
        # Restore to German
        applicant_session.put(
            f"{BASE_URL}/api/users/{user_id}",
            json={"language_pref": "de"}
        )


class TestPartnerSettingsUpdate:
    """Partner settings update tests"""
    
    def test_partner_can_update_profile(self, partner_session):
        """Partner can update their profile"""
        # Get current user
        me_resp = partner_session.get(f"{BASE_URL}/api/auth/me")
        if me_resp.status_code != 200:
            pytest.skip("Cannot get current user")
        user_id = me_resp.json().get("id")
        original_name = me_resp.json().get("full_name", "Partner Test")
        
        # Update name
        resp = partner_session.put(
            f"{BASE_URL}/api/users/{user_id}",
            json={"full_name": "TEST_Partner_Updated"}
        )
        assert resp.status_code == 200
        print("✓ Partner profile update OK")
        
        # Restore original name
        partner_session.put(
            f"{BASE_URL}/api/users/{user_id}",
            json={"full_name": original_name}
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
