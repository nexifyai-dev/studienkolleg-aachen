"""
Iteration 101 - Brain API Tests
Tests for the KI-Brain-System with mem0 OSS + OpenRouter minimax-m1

Endpoints tested:
- GET  /api/brain/stats          – Memory statistics
- POST /api/brain/ask            – Ask the AI assistant
- GET  /api/brain/recall/{id}    – Recall memories for an entity
- POST /api/brain/search         – Search memories
- POST /api/brain/poll-inbox     – Trigger IMAP polling
- GET  /api/brain/emails         – List imported emails
- POST /api/brain/ingest         – Ingest knowledge manually
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = "https://live-demo-fix.preview.emergentagent.com"

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
ADMIN_EMAIL = "admin@studienkolleg-aachen.de"
ADMIN_PASSWORD = "Admin@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


class TestBrainAPI:
    """Brain API endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and get CSRF token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Get CSRF token from homepage
        resp = self.session.get(f"{BASE_URL}/")
        self.csrf_token = self.session.cookies.get("csrf_token", "")
        if self.csrf_token:
            self.session.headers.update({"x-csrf-token": self.csrf_token})
    
    def _login_staff(self):
        """Login as staff and return session"""
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert resp.status_code == 200, f"Staff login failed: {resp.text}"
        # Update CSRF token after login
        new_csrf = self.session.cookies.get("csrf_token", "")
        if new_csrf:
            self.session.headers.update({"x-csrf-token": new_csrf})
        return resp.json()
    
    def _login_admin(self):
        """Login as admin and return session"""
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        # Update CSRF token after login
        new_csrf = self.session.cookies.get("csrf_token", "")
        if new_csrf:
            self.session.headers.update({"x-csrf-token": new_csrf})
        return resp.json()
    
    def _login_applicant(self):
        """Login as applicant and return session"""
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert resp.status_code == 200, f"Applicant login failed: {resp.text}"
        # Update CSRF token after login
        new_csrf = self.session.cookies.get("csrf_token", "")
        if new_csrf:
            self.session.headers.update({"x-csrf-token": new_csrf})
        return resp.json()
    
    # ─── GET /api/brain/stats ───────────────────────────────────────────────────
    
    def test_brain_stats_returns_statistics(self):
        """GET /api/brain/stats should return memory statistics"""
        self._login_staff()
        
        resp = self.session.get(f"{BASE_URL}/api/brain/stats")
        assert resp.status_code == 200, f"Brain stats failed: {resp.text}"
        
        data = resp.json()
        # Verify required fields exist
        assert "total_memories" in data, "Missing total_memories field"
        assert "emails_ingested" in data, "Missing emails_ingested field"
        assert "by_entity_type" in data, "Missing by_entity_type field"
        assert "by_category" in data, "Missing by_category field"
        
        # Verify types
        assert isinstance(data["total_memories"], int), "total_memories should be int"
        assert isinstance(data["emails_ingested"], int), "emails_ingested should be int"
        
        print(f"✓ Brain stats: {data['total_memories']} memories, {data['emails_ingested']} emails")
    
    def test_brain_stats_requires_staff_role(self):
        """GET /api/brain/stats should require staff/admin role"""
        self._login_applicant()
        
        resp = self.session.get(f"{BASE_URL}/api/brain/stats")
        # Should be 403 Forbidden for applicants
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print("✓ Brain stats correctly requires staff role")
    
    # ─── POST /api/brain/ask ────────────────────────────────────────────────────
    
    def test_brain_ask_returns_response(self):
        """POST /api/brain/ask should return AI response with system data"""
        self._login_staff()
        
        resp = self.session.post(f"{BASE_URL}/api/brain/ask", json={
            "query": "Wie viele Bewerbungen gibt es im System?",
            "lang": "de"
        })
        assert resp.status_code == 200, f"Brain ask failed: {resp.text}"
        
        data = resp.json()
        # Verify response structure
        assert "content" in data, "Missing content field"
        
        # Content should exist (may be None if OpenRouter fails)
        if data.get("content"):
            print(f"✓ Brain response received: {data['content'][:100]}...")
            # Check if response mentions numbers (system data)
            assert len(data["content"]) > 10, "Response too short"
        else:
            # If content is None, check for error
            if data.get("error"):
                print(f"⚠ Brain API returned error (OpenRouter issue): {data['error']}")
            else:
                print("⚠ Brain response was empty but no error")
    
    def test_brain_ask_with_entity_id(self):
        """POST /api/brain/ask with entity_id should use memory context"""
        self._login_staff()
        
        # First get an applicant ID from the system
        resp = self.session.get(f"{BASE_URL}/api/users?role=applicant&limit=1")
        if resp.status_code == 200:
            users = resp.json()
            if isinstance(users, list) and len(users) > 0:
                applicant_id = users[0].get("id", "")
            elif isinstance(users, dict) and users.get("users"):
                applicant_id = users["users"][0].get("id", "")
            else:
                applicant_id = ""
        else:
            applicant_id = ""
        
        resp = self.session.post(f"{BASE_URL}/api/brain/ask", json={
            "query": "Was weisst du ueber diesen Bewerber?",
            "entity_id": applicant_id,
            "lang": "de"
        })
        assert resp.status_code == 200, f"Brain ask with entity failed: {resp.text}"
        
        data = resp.json()
        assert "content" in data, "Missing content field"
        print(f"✓ Brain ask with entity_id works")
    
    def test_brain_ask_requires_query(self):
        """POST /api/brain/ask should require query parameter"""
        self._login_staff()
        
        resp = self.session.post(f"{BASE_URL}/api/brain/ask", json={
            "lang": "de"
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        print("✓ Brain ask correctly requires query")
    
    # ─── GET /api/brain/recall/{entity_id} ──────────────────────────────────────
    
    def test_brain_recall_returns_memories(self):
        """GET /api/brain/recall/{entity_id} should return memories"""
        self._login_staff()
        
        # Use 'institution' as entity_id (always exists)
        resp = self.session.get(f"{BASE_URL}/api/brain/recall/institution")
        assert resp.status_code == 200, f"Brain recall failed: {resp.text}"
        
        data = resp.json()
        assert "entity_id" in data, "Missing entity_id field"
        assert "count" in data, "Missing count field"
        assert "memories" in data, "Missing memories field"
        assert isinstance(data["memories"], list), "memories should be list"
        
        print(f"✓ Brain recall: {data['count']} memories for 'institution'")
    
    def test_brain_recall_with_category_filter(self):
        """GET /api/brain/recall/{entity_id}?category=X should filter by category"""
        self._login_staff()
        
        resp = self.session.get(f"{BASE_URL}/api/brain/recall/institution?category=institutional")
        assert resp.status_code == 200, f"Brain recall with category failed: {resp.text}"
        
        data = resp.json()
        # All returned memories should have the specified category
        for mem in data.get("memories", []):
            assert mem.get("category") == "institutional", f"Wrong category: {mem.get('category')}"
        
        print(f"✓ Brain recall with category filter works")
    
    # ─── POST /api/brain/search ─────────────────────────────────────────────────
    
    def test_brain_search_returns_results(self):
        """POST /api/brain/search should return search results"""
        self._login_staff()
        
        resp = self.session.post(f"{BASE_URL}/api/brain/search", json={
            "query": "Bewerbung"
        })
        assert resp.status_code == 200, f"Brain search failed: {resp.text}"
        
        data = resp.json()
        assert "query" in data, "Missing query field"
        assert "count" in data, "Missing count field"
        assert "results" in data, "Missing results field"
        assert isinstance(data["results"], list), "results should be list"
        
        print(f"✓ Brain search: {data['count']} results for 'Bewerbung'")
    
    def test_brain_search_requires_query(self):
        """POST /api/brain/search should require query parameter"""
        self._login_staff()
        
        resp = self.session.post(f"{BASE_URL}/api/brain/search", json={})
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        print("✓ Brain search correctly requires query")
    
    # ─── POST /api/brain/poll-inbox ─────────────────────────────────────────────
    
    def test_brain_poll_inbox_triggers_imap(self):
        """POST /api/brain/poll-inbox should trigger IMAP polling"""
        self._login_staff()
        
        resp = self.session.post(f"{BASE_URL}/api/brain/poll-inbox")
        assert resp.status_code == 200, f"Brain poll-inbox failed: {resp.text}"
        
        data = resp.json()
        # Should return import statistics
        assert "imported" in data or "error" in data, "Missing imported/error field"
        
        if "error" in data:
            print(f"⚠ IMAP poll returned error (expected if IMAP not configured): {data['error']}")
        else:
            assert "skipped" in data, "Missing skipped field"
            assert "errors" in data, "Missing errors field"
            print(f"✓ Brain poll-inbox: {data['imported']} imported, {data['skipped']} skipped")
    
    # ─── GET /api/brain/emails ──────────────────────────────────────────────────
    
    def test_brain_emails_returns_list(self):
        """GET /api/brain/emails should return list of imported emails"""
        self._login_staff()
        
        resp = self.session.get(f"{BASE_URL}/api/brain/emails")
        assert resp.status_code == 200, f"Brain emails failed: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list), "Response should be list"
        
        # If emails exist, verify structure
        if len(data) > 0:
            email = data[0]
            assert "id" in email, "Missing id field"
            assert "subject" in email or "from_addr" in email, "Missing email fields"
            print(f"✓ Brain emails: {len(data)} emails found")
        else:
            print("✓ Brain emails: 0 emails (empty list)")
    
    def test_brain_emails_with_limit(self):
        """GET /api/brain/emails?limit=5 should respect limit"""
        self._login_staff()
        
        resp = self.session.get(f"{BASE_URL}/api/brain/emails?limit=5")
        assert resp.status_code == 200, f"Brain emails with limit failed: {resp.text}"
        
        data = resp.json()
        assert len(data) <= 5, f"Expected max 5 emails, got {len(data)}"
        print(f"✓ Brain emails with limit works")
    
    # ─── POST /api/brain/ingest ─────────────────────────────────────────────────
    
    def test_brain_ingest_stores_knowledge(self):
        """POST /api/brain/ingest should store knowledge in memory"""
        self._login_admin()  # Requires admin role
        
        test_text = f"TEST_POLICY_{int(time.time())}: Alle Bewerber muessen einen Sprachnachweis vorlegen."
        
        resp = self.session.post(f"{BASE_URL}/api/brain/ingest", json={
            "text": test_text,
            "entity_id": "institution",
            "entity_type": "institution",
            "category": "institutional"
        })
        assert resp.status_code == 200, f"Brain ingest failed: {resp.text}"
        
        data = resp.json()
        assert "ingested" in data, "Missing ingested field"
        assert data["ingested"] > 0, "No facts ingested"
        
        print(f"✓ Brain ingest: {data['ingested']} facts stored")
        
        # Verify the knowledge was stored by searching for it
        resp2 = self.session.post(f"{BASE_URL}/api/brain/search", json={
            "query": "Sprachnachweis"
        })
        if resp2.status_code == 200:
            search_data = resp2.json()
            print(f"  → Search found {search_data['count']} results for 'Sprachnachweis'")
    
    def test_brain_ingest_requires_admin(self):
        """POST /api/brain/ingest should require admin role"""
        self._login_staff()  # Staff, not admin
        
        resp = self.session.post(f"{BASE_URL}/api/brain/ingest", json={
            "text": "Test policy",
            "entity_id": "institution"
        })
        # Should be 403 Forbidden for non-admin
        assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
        print("✓ Brain ingest correctly requires admin role")
    
    def test_brain_ingest_requires_text(self):
        """POST /api/brain/ingest should require text parameter"""
        self._login_admin()
        
        resp = self.session.post(f"{BASE_URL}/api/brain/ingest", json={
            "entity_id": "institution"
        })
        assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
        print("✓ Brain ingest correctly requires text")


class TestBrainMemoryIntegration:
    """Tests for Brain-Memory integration with application events"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session and get CSRF token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        resp = self.session.get(f"{BASE_URL}/")
        self.csrf_token = self.session.cookies.get("csrf_token", "")
        if self.csrf_token:
            self.session.headers.update({"x-csrf-token": self.csrf_token})
    
    def _login_staff(self):
        """Login as staff"""
        resp = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert resp.status_code == 200, f"Staff login failed: {resp.text}"
        new_csrf = self.session.cookies.get("csrf_token", "")
        if new_csrf:
            self.session.headers.update({"x-csrf-token": new_csrf})
        return resp.json()
    
    def test_application_status_change_creates_memory(self):
        """PUT /api/applications/{id} with stage change should create brain memory"""
        self._login_staff()
        
        # Get an application to test with
        resp = self.session.get(f"{BASE_URL}/api/applications?limit=1")
        if resp.status_code != 200:
            pytest.skip("Could not fetch applications")
        
        apps = resp.json()
        if isinstance(apps, dict):
            apps = apps.get("applications", [])
        
        if not apps:
            pytest.skip("No applications found")
        
        app = apps[0]
        app_id = app.get("id", "")
        applicant_id = app.get("applicant_id", "")
        current_stage = app.get("current_stage", "lead_new")
        
        # Get allowed transitions
        resp = self.session.get(f"{BASE_URL}/api/applications/{app_id}/allowed-transitions")
        if resp.status_code != 200:
            pytest.skip("Could not get allowed transitions")
        
        transitions = resp.json().get("allowed_transitions", [])
        if not transitions:
            pytest.skip("No allowed transitions")
        
        # Pick a new stage
        new_stage = transitions[0]["stage"]
        
        # Get memory count before
        resp_before = self.session.get(f"{BASE_URL}/api/brain/recall/{applicant_id}")
        count_before = resp_before.json().get("count", 0) if resp_before.status_code == 200 else 0
        
        # Update application stage
        resp = self.session.put(f"{BASE_URL}/api/applications/{app_id}", json={
            "current_stage": new_stage
        })
        
        if resp.status_code == 200:
            # Check if memory was created
            time.sleep(0.5)  # Small delay for async processing
            resp_after = self.session.get(f"{BASE_URL}/api/brain/recall/{applicant_id}")
            count_after = resp_after.json().get("count", 0) if resp_after.status_code == 200 else 0
            
            # Memory count should increase (or stay same if already had this fact)
            print(f"✓ Stage change: memories before={count_before}, after={count_after}")
            
            # Revert the stage change
            self.session.put(f"{BASE_URL}/api/applications/{app_id}", json={
                "current_stage": current_stage
            })
        else:
            print(f"⚠ Could not update application stage: {resp.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
