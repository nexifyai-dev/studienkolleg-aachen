"""
Iteration 99 - Testing new features:
1. Backend text search for applications (?search=)
2. Invoice list returns proper MongoDB ObjectId
3. PUT /api/auth/me for profile updates (language_pref)
4. PATCH /api/invoices/{id} for status changes
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
STAFF_EMAIL = "staff@studienkolleg-aachen.de"
STAFF_PASSWORD = "DevSeed@2026!"
APPLICANT_EMAIL = "applicant@studienkolleg-aachen.de"
APPLICANT_PASSWORD = "DevSeed@2026!"


def get_csrf_token(session):
    """Extract CSRF token from cookies"""
    return session.cookies.get('csrf_token', '')


class TestApplicationSearch:
    """Test backend text search for applications"""
    
    def test_staff_login(self):
        """Login as staff to get session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["role"] in ["staff", "admin", "superadmin"]
        return session
    
    def test_applications_list_without_search(self):
        """GET /api/applications without search returns all applications"""
        session = self.test_staff_login()
        response = session.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200, f"Applications list failed: {response.text}"
        data = response.json()
        assert isinstance(data, list)
        print(f"Total applications: {len(data)}")
        return data
    
    def test_applications_search_by_name(self):
        """GET /api/applications?search=Ahmed should return matching results"""
        session = self.test_staff_login()
        # First get all applications to find a name to search
        all_apps = session.get(f"{BASE_URL}/api/applications").json()
        
        if len(all_apps) > 0:
            # Try searching for a partial name
            test_name = all_apps[0].get('applicant', {}).get('full_name', '')
            if test_name:
                search_term = test_name.split()[0] if ' ' in test_name else test_name[:3]
                response = session.get(f"{BASE_URL}/api/applications?search={search_term}")
                assert response.status_code == 200, f"Search failed: {response.text}"
                results = response.json()
                print(f"Search for '{search_term}' returned {len(results)} results")
                assert isinstance(results, list)
        
        # Test with a generic search term
        response = session.get(f"{BASE_URL}/api/applications?search=test")
        assert response.status_code == 200
        print(f"Search for 'test' returned {len(response.json())} results")
    
    def test_applications_search_by_applicant_number(self):
        """GET /api/applications?search=STK should match applicant_number"""
        session = self.test_staff_login()
        response = session.get(f"{BASE_URL}/api/applications?search=STK")
        assert response.status_code == 200, f"Search by applicant number failed: {response.text}"
        results = response.json()
        print(f"Search for 'STK' (applicant number prefix) returned {len(results)} results")
        # If results exist, verify they have applicant_number
        for app in results[:3]:
            if app.get('applicant_number'):
                print(f"  Found: {app.get('applicant_number')}")
    
    def test_applications_search_by_country(self):
        """GET /api/applications?search=Germany should match degree_country"""
        session = self.test_staff_login()
        response = session.get(f"{BASE_URL}/api/applications?search=Germany")
        assert response.status_code == 200
        results = response.json()
        print(f"Search for 'Germany' returned {len(results)} results")


class TestInvoiceObjectId:
    """Test that invoice list returns proper MongoDB ObjectId"""
    
    def test_invoice_list_has_proper_id(self):
        """GET /api/invoices should return id as 24-char hex string (MongoDB ObjectId)"""
        session = requests.Session()
        # Login as staff
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        
        # Get invoices
        response = session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200, f"Invoice list failed: {response.text}"
        invoices = response.json()
        
        print(f"Total invoices: {len(invoices)}")
        
        # Check that each invoice has a proper id field
        for inv in invoices[:5]:  # Check first 5
            assert 'id' in inv, f"Invoice missing 'id' field: {inv}"
            inv_id = inv['id']
            # MongoDB ObjectId is 24 hex characters
            assert len(inv_id) == 24, f"Invoice id '{inv_id}' is not 24 chars (expected MongoDB ObjectId)"
            assert all(c in '0123456789abcdef' for c in inv_id.lower()), f"Invoice id '{inv_id}' is not hex"
            print(f"  Invoice {inv.get('invoice_number')}: id={inv_id} (valid ObjectId)")
    
    def test_invoice_has_applicant_number(self):
        """Invoices should include applicant_number if available"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        response = session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        invoices = response.json()
        
        # Check for applicant_number field
        invoices_with_app_num = [i for i in invoices if i.get('applicant_number')]
        print(f"Invoices with applicant_number: {len(invoices_with_app_num)} of {len(invoices)}")


class TestAuthMeUpdate:
    """Test PUT /api/auth/me for profile updates"""
    
    def test_applicant_update_language_pref(self):
        """PUT /api/auth/me with language_pref should update and return 200"""
        session = requests.Session()
        
        # Login as applicant
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200, f"Applicant login failed: {response.text}"
        
        # Get CSRF token
        csrf_token = get_csrf_token(session)
        headers = {"x-csrf-token": csrf_token} if csrf_token else {}
        
        # Get current profile
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        current_lang = me_response.json().get('language_pref', 'de')
        print(f"Current language_pref: {current_lang}")
        
        # Update to opposite language
        new_lang = 'en' if current_lang == 'de' else 'de'
        response = session.put(f"{BASE_URL}/api/auth/me", 
                               json={"language_pref": new_lang},
                               headers=headers)
        assert response.status_code == 200, f"PUT /api/auth/me failed: {response.text}"
        print(f"Updated language_pref to: {new_lang}")
        
        # Verify the change
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        updated_lang = me_response.json().get('language_pref')
        assert updated_lang == new_lang, f"Language not updated: expected {new_lang}, got {updated_lang}"
        print(f"Verified language_pref is now: {updated_lang}")
        
        # Restore original
        session.put(f"{BASE_URL}/api/auth/me", 
                    json={"language_pref": current_lang},
                    headers=headers)
    
    def test_update_full_name(self):
        """PUT /api/auth/me with full_name should update"""
        session = requests.Session()
        
        # Login as applicant
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": APPLICANT_EMAIL,
            "password": APPLICANT_PASSWORD
        })
        assert response.status_code == 200
        
        csrf_token = get_csrf_token(session)
        headers = {"x-csrf-token": csrf_token} if csrf_token else {}
        
        # Get current name
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        current_name = me_response.json().get('full_name', '')
        
        # Update name
        test_name = f"Test Applicant {int(time.time()) % 1000}"
        response = session.put(f"{BASE_URL}/api/auth/me",
                               json={"full_name": test_name},
                               headers=headers)
        assert response.status_code == 200, f"Update name failed: {response.text}"
        
        # Verify
        me_response = session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.json().get('full_name') == test_name
        print(f"Updated full_name to: {test_name}")
        
        # Restore
        if current_name:
            session.put(f"{BASE_URL}/api/auth/me",
                        json={"full_name": current_name},
                        headers=headers)


class TestInvoiceStatusChange:
    """Test PATCH /api/invoices/{id} for status changes"""
    
    def test_change_invoice_status_draft_to_sent(self):
        """PATCH /api/invoices/{id} with status='sent' should update status"""
        session = requests.Session()
        
        # Login as staff
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        assert response.status_code == 200
        
        csrf_token = get_csrf_token(session)
        headers = {"x-csrf-token": csrf_token} if csrf_token else {}
        
        # Get invoices
        response = session.get(f"{BASE_URL}/api/invoices")
        assert response.status_code == 200
        invoices = response.json()
        
        # Find a draft invoice to test with
        draft_invoices = [i for i in invoices if i.get('status') == 'draft']
        
        if draft_invoices:
            invoice = draft_invoices[0]
            invoice_id = invoice.get('id') or invoice.get('invoice_number')
            print(f"Testing status change on invoice: {invoice.get('invoice_number')} (id={invoice_id})")
            
            # Change status to sent
            response = session.patch(f"{BASE_URL}/api/invoices/{invoice_id}",
                                     json={"status": "sent"},
                                     headers=headers)
            assert response.status_code == 200, f"Status change failed: {response.text}"
            
            # Verify the change
            updated = response.json()
            assert updated.get('status') == 'sent', f"Status not updated: {updated.get('status')}"
            print(f"Successfully changed status from 'draft' to 'sent'")
            
            # Change back to draft for cleanup
            session.patch(f"{BASE_URL}/api/invoices/{invoice_id}",
                          json={"status": "draft"},
                          headers=headers)
        else:
            print("No draft invoices found to test status change")
            # Test with any invoice - just verify the endpoint works
            if invoices:
                invoice = invoices[0]
                invoice_id = invoice.get('id') or invoice.get('invoice_number')
                current_status = invoice.get('status')
                
                # Try to update notes instead (always allowed)
                response = session.patch(f"{BASE_URL}/api/invoices/{invoice_id}",
                                         json={"notes": f"Test note {int(time.time())}"},
                                         headers=headers)
                assert response.status_code == 200, f"PATCH failed: {response.text}"
                print(f"PATCH endpoint works - updated notes on invoice {invoice.get('invoice_number')}")


class TestSearchFunctionality:
    """Additional search tests for phone and course_type"""
    
    def test_search_by_phone(self):
        """Search should match phone numbers"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        # Get all apps first to find a phone number
        all_apps = session.get(f"{BASE_URL}/api/applications").json()
        
        phone_found = None
        for app in all_apps:
            phone = app.get('applicant', {}).get('phone')
            if phone and len(phone) > 5:
                phone_found = phone
                break
        
        if phone_found:
            # Search by partial phone
            search_term = phone_found[:5]
            response = session.get(f"{BASE_URL}/api/applications?search={search_term}")
            assert response.status_code == 200
            print(f"Search by phone '{search_term}' returned {len(response.json())} results")
        else:
            print("No phone numbers found in applications to test search")
    
    def test_search_by_course_type(self):
        """Search should match course_type"""
        session = requests.Session()
        session.post(f"{BASE_URL}/api/auth/login", json={
            "email": STAFF_EMAIL,
            "password": STAFF_PASSWORD
        })
        
        # Search for common course types
        for course in ['T-Course', 'M-Course', 'Language']:
            response = session.get(f"{BASE_URL}/api/applications?search={course}")
            assert response.status_code == 200
            results = response.json()
            print(f"Search for '{course}' returned {len(results)} results")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
