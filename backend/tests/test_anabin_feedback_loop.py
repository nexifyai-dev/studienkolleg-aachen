"""
Anabin Feedback Loop Tests - Iteration 40
Tests for: 
1) POST /api/anabin/review-queue - Manual review case creation
2) POST /api/anabin/review-queue/{id}/resolve - Resolve with feedback (knowledge base update)
3) GET /api/anabin/stats - Stats with queue counter
4) GET /api/anabin/review-queue - Queue list
5) GET /api/anabin/entries - Knowledge base entries
6) GET /api/anabin/knowledge-gaps - Knowledge gaps
7) E2E: Queue create → Resolve with feedback → Verify knowledge base updated
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"


@pytest.fixture(scope="module")
def admin_session():
    """Authenticated admin session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code}")
    return session


@pytest.fixture(scope="module")
def staff_session():
    """Authenticated staff session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    response = session.post(f"{BASE_URL}/api/auth/login", json={
        "email": STAFF_EMAIL,
        "password": STAFF_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Staff login failed: {response.status_code}")
    return session


class TestHealthCheck:
    """Basic health check"""
    
    def test_health_endpoint(self):
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health check passed")


class TestAnabinStatsWithQueueCounter:
    """GET /api/anabin/stats - Dashboard statistics with queue_open counter"""
    
    def test_stats_includes_queue_open(self, admin_session):
        """Stats should include queue_open counter"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "queue_open" in data
        assert isinstance(data["queue_open"], int)
        print(f"✓ Stats includes queue_open: {data['queue_open']}")
    
    def test_stats_all_fields_present(self, admin_session):
        """Verify all required stats fields"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        data = response.json()
        
        required_fields = ["total", "verified", "in_review", "special_cases", 
                          "unknown", "queue_open", "categories", "recent_changes"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        print(f"✓ All stats fields present: total={data['total']}, queue_open={data['queue_open']}")


class TestReviewQueueCreation:
    """POST /api/anabin/review-queue - Manual review case creation"""
    
    def test_create_review_queue_item(self, staff_session):
        """Staff can create a manual review case"""
        unique_country = f"TEST_FeedbackCountry_{uuid.uuid4().hex[:6]}"
        payload = {
            "country": unique_country,
            "degree_type": "Bachelor",
            "reason": "manual_review",
            "reason_label": "Pytest feedback loop test",
            "priority": "high",
            "next_action": "Verify mapping and update knowledge base"
        }
        
        response = staff_session.post(f"{BASE_URL}/api/anabin/review-queue", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["country"] == unique_country
        assert data["degree_type"] == "Bachelor"
        assert data["priority"] == "high"
        assert data["status"] == "open"
        assert "id" in data
        assert "queue_id" in data
        assert "created_at" in data
        assert "created_by" in data
        
        # Store for later tests
        TestReviewQueueCreation.created_item_id = data["id"]
        TestReviewQueueCreation.created_country = unique_country
        print(f"✓ Review queue item created: {data['queue_id']} for {unique_country}")
    
    def test_create_review_queue_requires_auth(self):
        """Review queue creation requires authentication"""
        payload = {"country": "TestCountry", "reason": "manual_review"}
        response = requests.post(f"{BASE_URL}/api/anabin/review-queue", json=payload)
        assert response.status_code in [401, 403]
        print("✓ Review queue creation requires auth")
    
    def test_review_queue_list_shows_created_item(self, staff_session):
        """Created item appears in queue list"""
        item_id = getattr(TestReviewQueueCreation, 'created_item_id', None)
        if not item_id:
            pytest.skip("No item created")
        
        response = staff_session.get(f"{BASE_URL}/api/anabin/review-queue")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        # Find our created item
        found = any(item["id"] == item_id for item in data["items"])
        assert found, "Created item not found in queue list"
        print(f"✓ Created item found in queue list (total: {data['total']})")


class TestResolveWithFeedback:
    """POST /api/anabin/review-queue/{id}/resolve - Resolve with feedback loop"""
    
    def test_resolve_without_knowledge_update(self, staff_session):
        """Resolve queue item without updating knowledge base"""
        # Create a new item to resolve
        unique_country = f"TEST_ResolveNoKB_{uuid.uuid4().hex[:6]}"
        create_payload = {
            "country": unique_country,
            "degree_type": "Diploma",
            "reason": "manual_review",
            "priority": "medium"
        }
        create_resp = staff_session.post(f"{BASE_URL}/api/anabin/review-queue", json=create_payload)
        assert create_resp.status_code == 200
        item_id = create_resp.json()["id"]
        
        # Resolve without knowledge update
        resolve_payload = {
            "resolution_note": "Mapping verified - no KB update needed"
        }
        response = staff_session.post(f"{BASE_URL}/api/anabin/review-queue/{item_id}/resolve", json=resolve_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["resolved"] == True
        assert data["knowledge_updated"] == False
        print(f"✓ Queue item resolved without KB update")
    
    def test_resolve_with_knowledge_update(self, staff_session):
        """Resolve queue item AND update knowledge base (feedback loop)"""
        # Create a new item to resolve
        unique_country = f"TEST_ResolveWithKB_{uuid.uuid4().hex[:6]}"
        create_payload = {
            "country": unique_country,
            "degree_type": "Master",
            "reason": "manual_review",
            "priority": "high"
        }
        create_resp = staff_session.post(f"{BASE_URL}/api/anabin/review-queue", json=create_payload)
        assert create_resp.status_code == 200
        item_id = create_resp.json()["id"]
        
        # First, create a knowledge base entry for this country
        kb_create_payload = {
            "country": unique_country,
            "degree_type": "Master",
            "category": "pruefen",
            "confidence": "unknown",
            "status": "in_review",
            "notes": "Initial entry for feedback loop test"
        }
        kb_resp = staff_session.post(f"{BASE_URL}/api/anabin/entries", json=kb_create_payload)
        assert kb_resp.status_code == 200
        kb_entry_id = kb_resp.json()["id"]
        
        # Resolve WITH knowledge update (feedback loop)
        resolve_payload = {
            "resolution_note": "Mapping verified and knowledge base updated",
            "update_knowledge": {
                "category": "H",
                "confidence": "high",
                "status": "verified",
                "is_special_case": False,
                "requires_staff_decision": False,
                "notes": "Verified via feedback loop - pytest test",
                "staff_note": "Confirmed by staff review",
                "operational_classification": "bedingt_anerkennbar"
            }
        }
        response = staff_session.post(f"{BASE_URL}/api/anabin/review-queue/{item_id}/resolve", json=resolve_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["resolved"] == True
        assert data["knowledge_updated"] == True
        
        # Store for verification
        TestResolveWithFeedback.kb_entry_id = kb_entry_id
        TestResolveWithFeedback.unique_country = unique_country
        print(f"✓ Queue item resolved WITH KB update (feedback loop)")
    
    def test_knowledge_base_was_updated(self, staff_session):
        """Verify knowledge base was actually updated by feedback loop"""
        kb_entry_id = getattr(TestResolveWithFeedback, 'kb_entry_id', None)
        if not kb_entry_id:
            pytest.skip("No KB entry to verify")
        
        response = staff_session.get(f"{BASE_URL}/api/anabin/entries/{kb_entry_id}")
        assert response.status_code == 200
        
        data = response.json()
        # Verify the feedback loop updated these fields
        assert data["category"] == "H", f"Expected category 'H', got '{data['category']}'"
        assert data["confidence"] == "high", f"Expected confidence 'high', got '{data['confidence']}'"
        assert data["status"] == "verified", f"Expected status 'verified', got '{data['status']}'"
        assert data["operational_classification"] == "bedingt_anerkennbar"
        assert "Verified via feedback loop" in data["notes"]
        assert "Confirmed by staff review" in data["staff_note"]
        
        # Verify change_history includes the feedback loop action
        assert "change_history" in data
        feedback_action = any(
            h.get("action") == "queue_resolution_feedback" 
            for h in data["change_history"]
        )
        assert feedback_action, "change_history should include 'queue_resolution_feedback' action"
        
        # Verify version was incremented
        assert data["version"] >= 2, f"Version should be >= 2 after feedback update, got {data['version']}"
        
        print(f"✓ Knowledge base verified: category={data['category']}, confidence={data['confidence']}, version={data['version']}")
    
    def test_resolve_invalid_queue_id(self, staff_session):
        """Resolve with invalid queue ID returns error"""
        resolve_payload = {"resolution_note": "Test"}
        response = staff_session.post(f"{BASE_URL}/api/anabin/review-queue/invalid-id/resolve", json=resolve_payload)
        assert response.status_code == 400
        print("✓ Invalid queue ID returns 400")
    
    def test_resolve_nonexistent_queue_id(self, staff_session):
        """Resolve with non-existent queue ID returns error"""
        resolve_payload = {"resolution_note": "Test"}
        response = staff_session.post(f"{BASE_URL}/api/anabin/review-queue/000000000000000000000000/resolve", json=resolve_payload)
        assert response.status_code == 400
        print("✓ Non-existent queue ID returns 400")
    
    def test_resolve_requires_auth(self):
        """Resolve endpoint requires authentication"""
        resolve_payload = {"resolution_note": "Test"}
        response = requests.post(f"{BASE_URL}/api/anabin/review-queue/000000000000000000000000/resolve", json=resolve_payload)
        assert response.status_code in [401, 403]
        print("✓ Resolve requires auth")


class TestKnowledgeGapsEndpoint:
    """GET /api/anabin/knowledge-gaps - Knowledge gaps analysis"""
    
    def test_knowledge_gaps_returns_200(self, staff_session):
        response = staff_session.get(f"{BASE_URL}/api/anabin/knowledge-gaps")
        assert response.status_code == 200
        print("✓ Knowledge gaps returns 200")
    
    def test_knowledge_gaps_structure(self, staff_session):
        response = staff_session.get(f"{BASE_URL}/api/anabin/knowledge-gaps")
        data = response.json()
        
        assert "gaps" in data
        assert "total" in data
        assert isinstance(data["gaps"], list)
        
        # If there are gaps, verify structure
        if data["gaps"]:
            gap = data["gaps"][0]
            assert "id" in gap
            assert "country" in gap
            assert "screening_frequency" in gap
        print(f"✓ Knowledge gaps structure valid: {data['total']} gaps")


class TestEntriesEndpoint:
    """GET /api/anabin/entries - Knowledge base entries"""
    
    def test_entries_returns_200(self, staff_session):
        response = staff_session.get(f"{BASE_URL}/api/anabin/entries")
        assert response.status_code == 200
        print("✓ Entries returns 200")
    
    def test_entries_structure(self, staff_session):
        response = staff_session.get(f"{BASE_URL}/api/anabin/entries?limit=5")
        data = response.json()
        
        assert "entries" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        print(f"✓ Entries structure valid: {data['total']} total entries")


class TestE2EFeedbackLoop:
    """End-to-End test: Queue create → Resolve with feedback → Verify KB updated"""
    
    def test_full_feedback_loop_flow(self, admin_session):
        """Complete E2E test of the feedback loop"""
        unique_country = f"TEST_E2E_FeedbackLoop_{uuid.uuid4().hex[:6]}"
        
        # Step 1: Create a knowledge base entry (simulating auto-flagged unknown country)
        kb_payload = {
            "country": unique_country,
            "degree_type": "Bachelor",
            "category": "pruefen",
            "confidence": "unknown",
            "status": "in_review",
            "notes": f"Auto-flagged: '{unique_country}' not in knowledge base",
            "source": "auto_flagged"
        }
        kb_resp = admin_session.post(f"{BASE_URL}/api/anabin/entries", json=kb_payload)
        assert kb_resp.status_code == 200
        kb_entry_id = kb_resp.json()["id"]
        print(f"  Step 1: Created KB entry for {unique_country} (id={kb_entry_id})")
        
        # Step 2: Create a review queue item for this country
        queue_payload = {
            "country": unique_country,
            "degree_type": "Bachelor",
            "reason": "no_mapping_found",
            "reason_label": f"Kein belastbares Mapping fuer '{unique_country}' gefunden",
            "priority": "high",
            "next_action": "Anabin pruefen und operative Einstufung vornehmen"
        }
        queue_resp = admin_session.post(f"{BASE_URL}/api/anabin/review-queue", json=queue_payload)
        assert queue_resp.status_code == 200
        queue_item_id = queue_resp.json()["id"]
        print(f"  Step 2: Created queue item (id={queue_item_id})")
        
        # Step 3: Verify queue item appears in stats
        stats_resp = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        assert stats_resp.status_code == 200
        initial_queue_open = stats_resp.json()["queue_open"]
        print(f"  Step 3: Stats show queue_open={initial_queue_open}")
        
        # Step 4: Resolve the queue item WITH feedback to knowledge base
        resolve_payload = {
            "resolution_note": "E2E Test: Mapping verified via Anabin database",
            "update_knowledge": {
                "category": "H+",
                "confidence": "high",
                "status": "verified",
                "is_special_case": False,
                "requires_staff_decision": False,
                "notes": f"E2E Test: {unique_country} verified as H+ category",
                "staff_note": "Verified by E2E pytest test",
                "operational_classification": "vollstaendig_anerkennbar"
            }
        }
        resolve_resp = admin_session.post(f"{BASE_URL}/api/anabin/review-queue/{queue_item_id}/resolve", json=resolve_payload)
        assert resolve_resp.status_code == 200
        resolve_data = resolve_resp.json()
        assert resolve_data["resolved"] == True
        assert resolve_data["knowledge_updated"] == True
        print(f"  Step 4: Queue item resolved with KB update")
        
        # Step 5: Verify knowledge base was updated
        kb_verify_resp = admin_session.get(f"{BASE_URL}/api/anabin/entries/{kb_entry_id}")
        assert kb_verify_resp.status_code == 200
        kb_data = kb_verify_resp.json()
        
        assert kb_data["category"] == "H+", f"Expected 'H+', got '{kb_data['category']}'"
        assert kb_data["confidence"] == "high"
        assert kb_data["status"] == "verified"
        assert kb_data["operational_classification"] == "vollstaendig_anerkennbar"
        assert "E2E Test" in kb_data["notes"]
        
        # Verify change_history includes feedback action
        feedback_in_history = any(
            h.get("action") == "queue_resolution_feedback" 
            for h in kb_data.get("change_history", [])
        )
        assert feedback_in_history, "change_history should include feedback action"
        print(f"  Step 5: KB verified - category={kb_data['category']}, version={kb_data['version']}")
        
        # Step 6: Verify queue item is now resolved
        queue_list_resp = admin_session.get(f"{BASE_URL}/api/anabin/review-queue?status=resolved")
        assert queue_list_resp.status_code == 200
        resolved_items = queue_list_resp.json()["items"]
        resolved_item = next((i for i in resolved_items if i["id"] == queue_item_id), None)
        assert resolved_item is not None, "Resolved item should appear in resolved queue"
        assert resolved_item["status"] == "resolved"
        assert resolved_item["resolved_at"] is not None
        print(f"  Step 6: Queue item confirmed resolved")
        
        # Cleanup
        admin_session.delete(f"{BASE_URL}/api/anabin/entries/{kb_entry_id}")
        print(f"✓ E2E Feedback Loop test PASSED for {unique_country}")


class TestCleanup:
    """Cleanup test data created during tests"""
    
    def test_cleanup_test_entries(self, admin_session):
        """Remove TEST_ prefixed entries"""
        # Get all entries with TEST_ prefix
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?q=TEST_&limit=100")
        if response.status_code == 200:
            entries = response.json().get("entries", [])
            deleted = 0
            for entry in entries:
                if entry.get("country", "").startswith("TEST_"):
                    del_resp = admin_session.delete(f"{BASE_URL}/api/anabin/entries/{entry['id']}")
                    if del_resp.status_code == 200:
                        deleted += 1
            print(f"✓ Cleanup: Deleted {deleted} TEST_ entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
