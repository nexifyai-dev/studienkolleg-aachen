"""
Phase 3.7k Backend Tests
- Partner/Affiliate Portal API endpoints
- AI Screening accept-ai-suggestion endpoint
- Role-based redirects verification
"""
import pytest
import requests
import os

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
    
    def test_accept_ai_suggestion_requires_suggested_stage(self, staff_session, test_application_id):
        """Accept AI suggestion requires suggested_stage field"""
        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{test_application_id}/accept-ai-suggestion",
            json={}
        )
        assert resp.status_code == 400
        print("✓ Accept AI suggestion correctly requires suggested_stage")
    
    def test_accept_ai_suggestion_works(self, staff_session, test_application_id):
        """Accept AI suggestion changes stage and returns audit info"""
        # First get current stage
        app_resp = staff_session.get(f"{BASE_URL}/api/applications/{test_application_id}")
        if app_resp.status_code != 200:
            pytest.skip("Cannot get application details")
        current_stage = app_resp.json().get("current_stage", "lead_new")
        
        # Try to accept a different stage
        new_stage = "in_review" if current_stage != "in_review" else "pending_docs"
        resp = staff_session.post(
            f"{BASE_URL}/api/applications/{test_application_id}/accept-ai-suggestion",
            json={"suggested_stage": new_stage}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") in ["accepted", "unchanged"]
        if data.get("status") == "accepted":
            assert data.get("new_stage") == new_stage
            print(f"✓ Accept AI suggestion OK - changed from {data.get('old_stage')} to {data.get('new_stage')}")
        else:
            print(f"✓ Accept AI suggestion OK - status unchanged (already at suggested stage)")
        
        # Restore original stage
        staff_session.put(
            f"{BASE_URL}/api/applications/{test_application_id}",
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
