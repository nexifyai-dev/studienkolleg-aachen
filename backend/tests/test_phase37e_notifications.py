"""
Phase 3.7e Tests: Notification System & Multilingual Email Templates

Tests:
- GET /api/notifications - list notifications for logged-in user
- GET /api/notifications/unread-count - unread count for badge
- PATCH /api/notifications/{id}/read - mark single notification as read
- PATCH /api/notifications/read-all - mark all notifications as read
- Auth flows for all 4 roles (admin, staff, teacher, applicant)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials from test_credentials.md
CREDENTIALS = {
    "admin": {"email": "admin@studienkolleg-aachen.de", "password": os.environ["TEST_ADMIN_PASSWORD"]},
    "staff": {"email": "staff@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]},
    "teacher": {"email": "teacher@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]},
    "applicant": {"email": "applicant@studienkolleg-aachen.de", "password": os.environ["TEST_DEFAULT_PASSWORD"]},
}


class TestHealth:
    """Health check - run first"""

    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health endpoint OK")


class TestAuthFlows:
    """Test login for all 4 roles"""

    def test_admin_login(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["admin"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "superadmin"
        print(f"✓ Admin login OK - role: {data['role']}")

    def test_staff_login(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["staff"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "staff"
        print(f"✓ Staff login OK - role: {data['role']}")

    def test_teacher_login(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["teacher"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "teacher"
        print(f"✓ Teacher login OK - role: {data['role']}")

    def test_applicant_login(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["applicant"],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "applicant"
        print(f"✓ Applicant login OK - role: {data['role']}")


class TestNotificationEndpoints:
    """Test notification CRUD endpoints"""

    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["applicant"],
        )
        assert response.status_code == 200
        return session

    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["staff"],
        )
        assert response.status_code == 200
        return session

    @pytest.fixture
    def teacher_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["teacher"],
        )
        assert response.status_code == 200
        return session

    def test_notifications_requires_auth(self):
        """GET /api/notifications requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 401
        print("✓ GET /api/notifications requires auth (401)")

    def test_unread_count_requires_auth(self):
        """GET /api/notifications/unread-count requires authentication"""
        response = requests.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 401
        print("✓ GET /api/notifications/unread-count requires auth (401)")

    def test_list_notifications_applicant(self, applicant_session):
        """Applicant can list their notifications"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Applicant can list notifications - count: {len(data)}")
        # Verify notification structure if any exist
        if data:
            notif = data[0]
            assert "id" in notif
            assert "title" in notif
            assert "message" in notif
            assert "read" in notif
            assert "created_at" in notif
            print(f"  - First notification: {notif['title']}")

    def test_list_notifications_with_limit(self, applicant_session):
        """Notifications endpoint supports limit parameter"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        print(f"✓ Notifications limit param works - returned: {len(data)}")

    def test_list_notifications_unread_only(self, applicant_session):
        """Notifications endpoint supports unread_only filter"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications?unread_only=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All returned should be unread
        for notif in data:
            assert notif.get("read") == False
        print(f"✓ Notifications unread_only filter works - unread count: {len(data)}")

    def test_unread_count_applicant(self, applicant_session):
        """Applicant can get unread notification count"""
        response = applicant_session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 0
        print(f"✓ Applicant unread count: {data['count']}")

    def test_list_notifications_staff(self, staff_session):
        """Staff can list their notifications"""
        response = staff_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Staff can list notifications - count: {len(data)}")

    def test_unread_count_staff(self, staff_session):
        """Staff can get unread notification count"""
        response = staff_session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        print(f"✓ Staff unread count: {data['count']}")

    def test_list_notifications_teacher(self, teacher_session):
        """Teacher can list their notifications"""
        response = teacher_session.get(f"{BASE_URL}/api/notifications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Teacher can list notifications - count: {len(data)}")


class TestMarkNotificationRead:
    """Test marking notifications as read"""

    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["applicant"],
        )
        assert response.status_code == 200
        return session

    def test_mark_read_requires_auth(self):
        """PATCH /api/notifications/{id}/read requires authentication"""
        response = requests.patch(f"{BASE_URL}/api/notifications/fake-id/read")
        assert response.status_code == 401
        print("✓ PATCH /api/notifications/{id}/read requires auth (401)")

    def test_mark_all_read_requires_auth(self):
        """PATCH /api/notifications/read-all requires authentication"""
        response = requests.patch(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 401
        print("✓ PATCH /api/notifications/read-all requires auth (401)")

    def test_mark_single_notification_read(self, applicant_session):
        """Applicant can mark a single notification as read"""
        # First get notifications
        list_response = applicant_session.get(f"{BASE_URL}/api/notifications")
        assert list_response.status_code == 200
        notifications = list_response.json()

        if not notifications:
            pytest.skip("No notifications to test mark-read")

        notif_id = notifications[0]["id"]
        response = applicant_session.patch(f"{BASE_URL}/api/notifications/{notif_id}/read")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["ok", "not_found"]
        print(f"✓ Mark single notification read - status: {data.get('status')}")

    def test_mark_all_notifications_read(self, applicant_session):
        """Applicant can mark all notifications as read"""
        response = applicant_session.patch(f"{BASE_URL}/api/notifications/read-all")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        assert "updated" in data
        print(f"✓ Mark all notifications read - updated: {data.get('updated')}")

        # Verify unread count is now 0
        count_response = applicant_session.get(f"{BASE_URL}/api/notifications/unread-count")
        assert count_response.status_code == 200
        count_data = count_response.json()
        assert count_data["count"] == 0
        print(f"✓ Verified unread count is now 0")

    def test_mark_nonexistent_notification_read(self, applicant_session):
        """Marking non-existent notification returns not_found"""
        # Use a valid ObjectId format but non-existent
        fake_id = "000000000000000000000000"
        response = applicant_session.patch(f"{BASE_URL}/api/notifications/{fake_id}/read")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "not_found"
        print("✓ Non-existent notification returns not_found status")


class TestNotificationTriggers:
    """Test that notification triggers are wired correctly (integration tests)"""

    @pytest.fixture
    def staff_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["staff"],
        )
        assert response.status_code == 200
        return session

    @pytest.fixture
    def applicant_session(self):
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json=CREDENTIALS["applicant"],
        )
        assert response.status_code == 200
        return session

    def test_consent_types_include_teacher_data_access(self, applicant_session):
        """Consent types endpoint includes teacher_data_access"""
        response = applicant_session.get(f"{BASE_URL}/api/consents/types")
        assert response.status_code == 200
        data = response.json()
        assert "teacher_data_access" in data
        consent_def = data["teacher_data_access"]
        assert "purpose_de" in consent_def
        assert "purpose_en" in consent_def
        assert "scope" in consent_def
        assert "excludes" in consent_def
        print("✓ Consent types include teacher_data_access with DE/EN purposes")

    def test_teacher_list_endpoint(self, staff_session):
        """Staff can list teachers for assignment"""
        response = staff_session.get(f"{BASE_URL}/api/teacher/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            teacher = data[0]
            assert "id" in teacher
            assert "full_name" in teacher
            assert "email" in teacher
        print(f"✓ Teacher list endpoint works - count: {len(data)}")


class TestEmailTemplateLanguageSupport:
    """Verify email templates support DE/EN (code review checks)"""

    def test_email_service_has_bilingual_templates(self):
        """Verify email.py has DE/EN templates (code structure check)"""
        import sys
        sys.path.insert(0, "/app/backend")
        from services.email import (
            send_welcome,
            send_application_received,
            send_document_requested,
            send_status_changed,
            send_password_reset,
            send_invite,
            send_teacher_assigned,
        )
        # All functions should accept lang parameter
        import inspect
        for func in [send_welcome, send_application_received, send_document_requested,
                     send_status_changed, send_password_reset, send_invite, send_teacher_assigned]:
            sig = inspect.signature(func)
            assert "lang" in sig.parameters, f"{func.__name__} missing lang parameter"
        print("✓ All 7 email templates support lang parameter (DE/EN)")

    def test_notification_templates_have_de_en(self):
        """Verify notification templates have DE/EN versions"""
        import sys
        sys.path.insert(0, "/app/backend")
        from services.notifications import NOTIFICATION_TEMPLATES

        expected_types = [
            "application_received", "status_changed", "document_requested",
            "document_uploaded", "teacher_assigned", "consent_granted",
            "consent_revoked", "new_message"
        ]
        for ntype in expected_types:
            assert ntype in NOTIFICATION_TEMPLATES, f"Missing template: {ntype}"
            assert "de" in NOTIFICATION_TEMPLATES[ntype], f"{ntype} missing DE template"
            assert "en" in NOTIFICATION_TEMPLATES[ntype], f"{ntype} missing EN template"
            assert "title" in NOTIFICATION_TEMPLATES[ntype]["de"]
            assert "title" in NOTIFICATION_TEMPLATES[ntype]["en"]
        print(f"✓ All {len(expected_types)} notification types have DE/EN templates")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
