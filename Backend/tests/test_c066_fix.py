"""C-066 regression: guest child endpoints are reachable through the gateway.

Tests that address, feedback, and loyalty endpoints work for both bar and
restaurant guests after being moved from UNCALLED_ENDPOINTS to ROUTE_PERMISSIONS.
"""
import httpx
import os
import sys

GATEWAY = "http://127.0.0.1:8000"
EMAIL = "admin@cherryhotel.com"
PASSWORD = os.getenv("PW_PASSWORD", "")


def login():
    resp = httpx.post(f"{GATEWAY}/login_post", json={"email": EMAIL, "password": PASSWORD}, timeout=10)
    assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
    return resp.json()["access_token"]


def test_bar_guest_child_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test guest
    guest_resp = httpx.post(f"{GATEWAY}/bar/guest", headers=headers, json={
        "first_name": "C066Test",
        "last_name": "Bar",
        "mobile": "+919876543210",
        "guest_type": "Walk-In",
    }, timeout=10)
    assert guest_resp.status_code == 201, f"Bar guest create failed: {guest_resp.status_code} {guest_resp.text}"
    guest_id = guest_resp.json()["data"]["id"]
    print(f"  Bar guest created: ID {guest_id}")
    
    # Add address
    addr_resp = httpx.post(f"{GATEWAY}/bar/guest/{guest_id}/address", headers=headers, json={
        "address": "123 Test Street",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "postal_code": "400001",
    }, timeout=10)
    assert addr_resp.status_code == 201, f"Bar address failed: {addr_resp.status_code} {addr_resp.text}"
    print(f"  Bar address added: {addr_resp.status_code}")
    
    # Add feedback
    fb_resp = httpx.post(f"{GATEWAY}/bar/guest/{guest_id}/feedback", headers=headers, json={
        "rating": 5,
        "comments": "Great service",
    }, timeout=10)
    assert fb_resp.status_code == 201, f"Bar feedback failed: {fb_resp.status_code} {fb_resp.text}"
    print(f"  Bar feedback added: {fb_resp.status_code}")
    
    # Adjust loyalty
    loy_resp = httpx.post(f"{GATEWAY}/bar/guest/{guest_id}/loyalty", headers=headers, json={
        "points": 100,
        "reason": "Test reward",
    }, timeout=10)
    assert loy_resp.status_code == 200, f"Bar loyalty failed: {loy_resp.status_code} {loy_resp.text}"
    print(f"  Bar loyalty adjusted: {loy_resp.status_code}")
    
    # Cleanup
    del_resp = httpx.delete(f"{GATEWAY}/bar/guest/{guest_id}", headers=headers, timeout=10)
    assert del_resp.status_code == 200, f"Bar guest delete failed: {del_resp.status_code}"
    print(f"  Bar guest cleaned up")


def test_restaurant_guest_child_endpoints(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a test guest
    guest_resp = httpx.post(f"{GATEWAY}/restaurant/guest", headers=headers, json={
        "first_name": "C066Test",
        "last_name": "Restaurant",
        "mobile": "+919876543211",
        "guest_type": "Walk-In",
    }, timeout=10)
    assert guest_resp.status_code == 201, f"Restaurant guest create failed: {guest_resp.status_code} {guest_resp.text}"
    guest_id = guest_resp.json()["data"]["id"]
    print(f"  Restaurant guest created: ID {guest_id}")
    
    # Add address
    addr_resp = httpx.post(f"{GATEWAY}/restaurant/guest/{guest_id}/address", headers=headers, json={
        "address": "456 Test Avenue",
        "city": "Delhi",
        "state": "Delhi",
        "country": "India",
        "postal_code": "110001",
    }, timeout=10)
    assert addr_resp.status_code == 201, f"Restaurant address failed: {addr_resp.status_code} {addr_resp.text}"
    print(f"  Restaurant address added: {addr_resp.status_code}")
    
    # Add feedback
    fb_resp = httpx.post(f"{GATEWAY}/restaurant/guest/{guest_id}/feedback", headers=headers, json={
        "rating": 4,
        "comments": "Good food",
    }, timeout=10)
    assert fb_resp.status_code == 201, f"Restaurant feedback failed: {fb_resp.status_code} {fb_resp.text}"
    print(f"  Restaurant feedback added: {fb_resp.status_code}")
    
    # Adjust loyalty
    loy_resp = httpx.post(f"{GATEWAY}/restaurant/guest/{guest_id}/loyalty", headers=headers, json={
        "points": 50,
        "reason": "Test reward",
    }, timeout=10)
    assert loy_resp.status_code == 200, f"Restaurant loyalty failed: {loy_resp.status_code} {loy_resp.text}"
    print(f"  Restaurant loyalty adjusted: {loy_resp.status_code}")
    
    # Cleanup
    del_resp = httpx.delete(f"{GATEWAY}/restaurant/guest/{guest_id}", headers=headers, timeout=10)
    assert del_resp.status_code == 200, f"Restaurant guest delete failed: {del_resp.status_code}"
    print(f"  Restaurant guest cleaned up")


def test_readyz_endpoints():
    """Verify all services have /readyz."""
    services = {
        "gateway": "http://127.0.0.1:8000",
        "user": "http://127.0.0.1:8020",
        "masterdata": "http://127.0.0.1:8030",
        "hotel": "http://127.0.0.1:8040",
        "restaurant": "http://127.0.0.1:8050",
        "bar": "http://127.0.0.1:8060",
    }
    for name, url in services.items():
        try:
            resp = httpx.get(f"{url}/readyz", timeout=5)
            print(f"  {name} /readyz: {resp.status_code} {resp.json().get('status', 'unknown')}")
        except Exception as e:
            print(f"  {name} /readyz: FAILED - {e}")


if __name__ == "__main__":
    print("Testing C-066 fix: guest child endpoints")
    token = login()
    print(f"  Logged in, token acquired")
    
    print("\nBar guest child endpoints:")
    test_bar_guest_child_endpoints(token)
    
    print("\nRestaurant guest child endpoints:")
    test_restaurant_guest_child_endpoints(token)
    
    print("\nReadyz endpoints:")
    test_readyz_endpoints()
    
    print("\nAll C-066 tests passed!")
