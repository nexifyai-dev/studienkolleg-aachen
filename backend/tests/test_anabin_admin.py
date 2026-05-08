"""
Anabin Admin API Tests - Iteration 39
Tests for: Dashboard Stats, Entries CRUD, Review Queue, Knowledge Gaps, Bulk Actions
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


class TestAnabinStats:
    """GET /api/anabin/stats - Dashboard statistics"""
    
    def test_stats_returns_200(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        assert response.status_code == 200
        print("✓ Stats endpoint returns 200")
    
    def test_stats_response_structure(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        data = response.json()
        
        # Verify all required fields
        assert "total" in data
        assert "verified" in data
        assert "in_review" in data
        assert "special_cases" in data
        assert "unknown" in data
        assert "queue_open" in data
        assert "categories" in data
        assert "recent_changes" in data
        
        # Verify data types
        assert isinstance(data["total"], int)
        assert isinstance(data["verified"], int)
        assert isinstance(data["categories"], dict)
        assert isinstance(data["recent_changes"], list)
        print(f"✓ Stats structure valid: total={data['total']}, verified={data['verified']}")
    
    def test_stats_has_80_seeded_entries(self, admin_session):
        """Verify 80 country entries were seeded"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        data = response.json()
        assert data["total"] >= 80, f"Expected at least 80 entries, got {data['total']}"
        print(f"✓ Seeded entries verified: {data['total']} total")
    
    def test_stats_category_distribution(self, admin_session):
        """Verify category distribution (H+, H, D)"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/stats")
        data = response.json()
        categories = data["categories"]
        
        assert "H+" in categories or "H" in categories or "D" in categories
        total_categorized = sum(categories.values())
        assert total_categorized > 0
        print(f"✓ Category distribution: {categories}")
    
    def test_stats_requires_auth(self):
        """Stats endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/anabin/stats")
        assert response.status_code in [401, 403]
        print("✓ Stats requires authentication")


class TestAnabinEntriesList:
    """GET /api/anabin/entries - List with search/filter/sort/pagination"""
    
    def test_entries_list_returns_200(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries")
        assert response.status_code == 200
        print("✓ Entries list returns 200")
    
    def test_entries_response_structure(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?limit=5")
        data = response.json()
        
        assert "entries" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert isinstance(data["entries"], list)
        print(f"✓ Entries structure valid: {len(data['entries'])} entries, total={data['total']}")
    
    def test_entries_entry_schema(self, admin_session):
        """Verify extended schema fields on entries"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?limit=1")
        data = response.json()
        
        if data["entries"]:
            entry = data["entries"][0]
            # Required fields from extended schema
            assert "id" in entry
            assert "country" in entry
            assert "category" in entry
            assert "status" in entry
            assert "confidence" in entry
            assert "degree_type" in entry
            assert "change_history" in entry
            assert "version" in entry
            print(f"✓ Entry schema valid: {entry['country']} ({entry['category']})")
    
    def test_entries_search_by_country(self, admin_session):
        """Search entries by country name"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?q=Deutschland")
        data = response.json()
        
        assert data["total"] >= 1
        assert any("Deutschland" in e["country"] for e in data["entries"])
        print(f"✓ Search by country works: found {data['total']} for 'Deutschland'")
    
    def test_entries_filter_by_category(self, admin_session):
        """Filter entries by category"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?category=H%2B")
        data = response.json()
        
        assert data["total"] > 0
        for entry in data["entries"]:
            assert entry["category"] == "H+"
        print(f"✓ Filter by category works: {data['total']} H+ entries")
    
    def test_entries_filter_by_status(self, admin_session):
        """Filter entries by status"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?status=verified")
        data = response.json()
        
        assert data["total"] > 0
        for entry in data["entries"]:
            assert entry["status"] == "verified"
        print(f"✓ Filter by status works: {data['total']} verified entries")
    
    def test_entries_pagination(self, admin_session):
        """Test pagination with skip/limit"""
        # Get first page
        response1 = admin_session.get(f"{BASE_URL}/api/anabin/entries?skip=0&limit=10")
        data1 = response1.json()
        
        # Get second page
        response2 = admin_session.get(f"{BASE_URL}/api/anabin/entries?skip=10&limit=10")
        data2 = response2.json()
        
        assert data1["skip"] == 0
        assert data2["skip"] == 10
        
        # Entries should be different
        if data1["entries"] and data2["entries"]:
            ids1 = {e["id"] for e in data1["entries"]}
            ids2 = {e["id"] for e in data2["entries"]}
            assert ids1.isdisjoint(ids2), "Pagination returned duplicate entries"
        print("✓ Pagination works correctly")
    
    def test_entries_sort_by_country(self, admin_session):
        """Test sorting by country"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries?sort_by=country&sort_dir=1&limit=10")
        data = response.json()
        
        countries = [e["country"] for e in data["entries"]]
        assert countries == sorted(countries), "Entries not sorted by country ascending"
        print(f"✓ Sort by country works: {countries[:3]}...")


class TestAnabinEntryCRUD:
    """CRUD operations for knowledge entries"""
    
    def test_create_entry(self, admin_session):
        """POST /api/anabin/entries - Create new entry"""
        unique_country = f"TEST_Testland_{uuid.uuid4().hex[:6]}"
        payload = {
            "country": unique_country,
            "degree_type": "Bachelor",
            "category": "pruefen",
            "confidence": "low",
            "status": "draft",
            "notes": "Test entry for pytest",
            "is_special_case": True
        }
        
        response = admin_session.post(f"{BASE_URL}/api/anabin/entries", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["country"] == unique_country
        assert data["category"] == "pruefen"
        assert data["status"] == "draft"
        assert data["is_special_case"] == True
        assert "id" in data
        assert data["version"] == 1
        assert len(data["change_history"]) == 1
        assert data["change_history"][0]["action"] == "created"
        
        # Store for cleanup
        TestAnabinEntryCRUD.created_entry_id = data["id"]
        print(f"✓ Entry created: {unique_country} (id={data['id']})")
    
    def test_get_entry_by_id(self, admin_session):
        """GET /api/anabin/entries/{id} - Get single entry"""
        entry_id = getattr(TestAnabinEntryCRUD, 'created_entry_id', None)
        if not entry_id:
            pytest.skip("No entry created to fetch")
        
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries/{entry_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == entry_id
        assert "country" in data
        assert "change_history" in data
        print(f"✓ Entry fetched: {data['country']}")
    
    def test_update_entry_versioned(self, admin_session):
        """PUT /api/anabin/entries/{id} - Update with versioning"""
        entry_id = getattr(TestAnabinEntryCRUD, 'created_entry_id', None)
        if not entry_id:
            pytest.skip("No entry created to update")
        
        payload = {
            "category": "H",
            "confidence": "medium",
            "status": "in_review",
            "notes": "Updated by pytest"
        }
        
        response = admin_session.put(f"{BASE_URL}/api/anabin/entries/{entry_id}", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["category"] == "H"
        assert data["confidence"] == "medium"
        assert data["status"] == "in_review"
        assert data["version"] == 2, f"Expected version 2, got {data['version']}"
        
        # Verify change_history was updated
        assert len(data["change_history"]) >= 2
        last_change = data["change_history"][-1]
        assert last_change["action"] == "updated"
        assert "category" in last_change["fields"]
        assert "previous_values" in last_change
        print(f"✓ Entry updated: version={data['version']}, history={len(data['change_history'])} entries")
    
    def test_get_entry_invalid_id(self, admin_session):
        """GET /api/anabin/entries/{id} - Invalid ID returns 400"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries/invalid-id")
        assert response.status_code == 400
        print("✓ Invalid ID returns 400")
    
    def test_get_entry_not_found(self, admin_session):
        """GET /api/anabin/entries/{id} - Non-existent ID returns 404"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/entries/000000000000000000000000")
        assert response.status_code == 404
        print("✓ Non-existent ID returns 404")
    
    def test_create_entry_missing_country(self, admin_session):
        """POST /api/anabin/entries - Missing country returns 400"""
        payload = {"category": "H", "notes": "No country"}
        response = admin_session.post(f"{BASE_URL}/api/anabin/entries", json=payload)
        assert response.status_code == 400
        print("✓ Missing country returns 400")
    
    def test_delete_entry_admin_only(self, admin_session):
        """DELETE /api/anabin/entries/{id} - Admin can delete"""
        entry_id = getattr(TestAnabinEntryCRUD, 'created_entry_id', None)
        if not entry_id:
            pytest.skip("No entry created to delete")
        
        response = admin_session.delete(f"{BASE_URL}/api/anabin/entries/{entry_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted"] == True
        
        # Verify deletion
        get_response = admin_session.get(f"{BASE_URL}/api/anabin/entries/{entry_id}")
        assert get_response.status_code == 404
        print(f"✓ Entry deleted and verified: {entry_id}")


class TestAnabinReviewQueue:
    """Review Queue CRUD operations"""
    
    def test_review_queue_list_empty(self, admin_session):
        """GET /api/anabin/review-queue - List (starts empty)"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/review-queue")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
        print(f"✓ Review queue list: {data['total']} items")
    
    def test_create_review_item(self, admin_session):
        """POST /api/anabin/review-queue - Create review case"""
        payload = {
            "country": "TEST_ReviewCountry",
            "degree_type": "HND",
            "reason": "manual_review",
            "reason_label": "Pytest test case",
            "priority": "high",
            "next_action": "Verify mapping in Anabin database"
        }
        
        response = admin_session.post(f"{BASE_URL}/api/anabin/review-queue", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["country"] == "TEST_ReviewCountry"
        assert data["priority"] == "high"
        assert data["status"] == "open"
        assert "id" in data
        assert "queue_id" in data
        
        TestAnabinReviewQueue.created_queue_id = data["id"]
        print(f"✓ Review item created: {data['queue_id']} (id={data['id']})")
    
    def test_update_review_item_status(self, admin_session):
        """PUT /api/anabin/review-queue/{id} - Update status"""
        item_id = getattr(TestAnabinReviewQueue, 'created_queue_id', None)
        if not item_id:
            pytest.skip("No review item created")
        
        payload = {"status": "in_progress", "owner": "admin@studienkolleg-aachen.de"}
        response = admin_session.put(f"{BASE_URL}/api/anabin/review-queue/{item_id}", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["owner"] == "admin@studienkolleg-aachen.de"
        print(f"✓ Review item updated to in_progress")
    
    def test_resolve_review_item(self, admin_session):
        """PUT /api/anabin/review-queue/{id} - Resolve item"""
        item_id = getattr(TestAnabinReviewQueue, 'created_queue_id', None)
        if not item_id:
            pytest.skip("No review item created")
        
        payload = {"status": "resolved", "resolution": "Mapping verified and accepted"}
        response = admin_session.put(f"{BASE_URL}/api/anabin/review-queue/{item_id}", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "resolved"
        assert data["resolution"] == "Mapping verified and accepted"
        assert data["resolved_at"] is not None
        assert data["resolved_by"] is not None
        print(f"✓ Review item resolved")
    
    def test_review_queue_filter_by_status(self, admin_session):
        """GET /api/anabin/review-queue?status=resolved"""
        response = admin_session.get(f"{BASE_URL}/api/anabin/review-queue?status=resolved")
        assert response.status_code == 200
        
        data = response.json()
        for item in data["items"]:
            assert item["status"] == "resolved"
        print(f"✓ Filter by status works: {data['total']} resolved items")


class TestAnabinKnowledgeGaps:
    """GET /api/anabin/knowledge-gaps - Knowledge gaps analysis"""
    
    def test_knowledge_gaps_returns_200(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/anabin/knowledge-gaps")
        assert response.status_code == 200
        print("✓ Knowledge gaps returns 200")
    
    def test_knowledge_gaps_response_structure(self, admin_session):
        response = admin_session.get(f"{BASE_URL}/api/anabin/knowledge-gaps")
        data = response.json()
        
        assert "gaps" in data
        assert "total" in data
        assert isinstance(data["gaps"], list)
        print(f"✓ Knowledge gaps structure valid: {data['total']} gaps")
    
    def test_knowledge_gaps_includes_screening_frequency(self, admin_session):
        """Gaps should include screening_frequency field"""
        # First create a gap entry
        payload = {
            "country": "TEST_GapCountry",
            "category": "pruefen",
            "confidence": "low",
            "status": "in_review"
        }
        create_resp = admin_session.post(f"{BASE_URL}/api/anabin/entries", json=payload)
        if create_resp.status_code == 200:
            entry_id = create_resp.json()["id"]
            
            # Now check gaps
            response = admin_session.get(f"{BASE_URL}/api/anabin/knowledge-gaps")
            data = response.json()
            
            if data["gaps"]:
                gap = data["gaps"][0]
                assert "screening_frequency" in gap
                print(f"✓ Gap includes screening_frequency: {gap.get('screening_frequency', 0)}")
            
            # Cleanup
            admin_session.delete(f"{BASE_URL}/api/anabin/entries/{entry_id}")


class TestAnabinBulkUpdate:
    """POST /api/anabin/bulk-update - Bulk status/category changes"""
    
    def test_bulk_update_requires_admin(self, staff_session):
        """Bulk update requires admin role"""
        payload = {"ids": ["000000000000000000000000"], "update": {"status": "verified"}}
        response = staff_session.post(f"{BASE_URL}/api/anabin/bulk-update", json=payload)
        # Staff should be denied (only superadmin/admin allowed)
        assert response.status_code in [401, 403]
        print("✓ Bulk update requires admin role")
    
    def test_bulk_update_entries(self, admin_session):
        """Bulk update multiple entries"""
        # Create test entries
        entry_ids = []
        for i in range(2):
            payload = {
                "country": f"TEST_BulkCountry_{i}_{uuid.uuid4().hex[:4]}",
                "category": "pruefen",
                "status": "draft"
            }
            resp = admin_session.post(f"{BASE_URL}/api/anabin/entries", json=payload)
            if resp.status_code == 200:
                entry_ids.append(resp.json()["id"])
        
        if len(entry_ids) < 2:
            pytest.skip("Could not create test entries for bulk update")
        
        # Bulk update
        bulk_payload = {
            "ids": entry_ids,
            "update": {"status": "verified", "category": "H"}
        }
        response = admin_session.post(f"{BASE_URL}/api/anabin/bulk-update", json=bulk_payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["modified"] == 2
        
        # Verify updates
        for eid in entry_ids:
            get_resp = admin_session.get(f"{BASE_URL}/api/anabin/entries/{eid}")
            entry = get_resp.json()
            assert entry["status"] == "verified"
            assert entry["category"] == "H"
            # Verify change_history includes bulk_updated
            assert any(h["action"] == "bulk_updated" for h in entry["change_history"])
        
        # Cleanup
        for eid in entry_ids:
            admin_session.delete(f"{BASE_URL}/api/anabin/entries/{eid}")
        
        print(f"✓ Bulk update worked: {data['modified']} entries modified")
    
    def test_bulk_update_missing_ids(self, admin_session):
        """Bulk update with missing IDs returns 400"""
        payload = {"update": {"status": "verified"}}
        response = admin_session.post(f"{BASE_URL}/api/anabin/bulk-update", json=payload)
        assert response.status_code == 400
        print("✓ Missing IDs returns 400")
    
    def test_bulk_update_invalid_fields(self, admin_session):
        """Bulk update with non-allowed fields returns 400"""
        payload = {"ids": ["000000000000000000000000"], "update": {"country": "Hacked"}}
        response = admin_session.post(f"{BASE_URL}/api/anabin/bulk-update", json=payload)
        assert response.status_code == 400
        print("✓ Invalid update fields returns 400")


class TestAnabinAuthRequirements:
    """Authentication and authorization tests"""
    
    def test_entries_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/anabin/entries")
        assert response.status_code in [401, 403]
        print("✓ Entries requires auth")
    
    def test_review_queue_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/anabin/review-queue")
        assert response.status_code in [401, 403]
        print("✓ Review queue requires auth")
    
    def test_knowledge_gaps_requires_auth(self):
        response = requests.get(f"{BASE_URL}/api/anabin/knowledge-gaps")
        assert response.status_code in [401, 403]
        print("✓ Knowledge gaps requires auth")
    
    def test_staff_can_access_entries(self, staff_session):
        """Staff role can access entries"""
        response = staff_session.get(f"{BASE_URL}/api/anabin/entries?limit=1")
        assert response.status_code == 200
        print("✓ Staff can access entries")
    
    def test_staff_can_create_entry(self, staff_session):
        """Staff role can create entries"""
        payload = {
            "country": f"TEST_StaffEntry_{uuid.uuid4().hex[:4]}",
            "category": "pruefen"
        }
        response = staff_session.post(f"{BASE_URL}/api/anabin/entries", json=payload)
        assert response.status_code == 200
        
        # Cleanup
        entry_id = response.json()["id"]
        # Staff cannot delete, so we use admin session for cleanup
        admin_session = requests.Session()
        admin_session.headers.update({"Content-Type": "application/json"})
        admin_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
        })
        admin_session.delete(f"{BASE_URL}/api/anabin/entries/{entry_id}")
        print("✓ Staff can create entries")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
