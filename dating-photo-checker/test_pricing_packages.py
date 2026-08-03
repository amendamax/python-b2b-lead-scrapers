import requests
import sys
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_pricing_packages():
    # Generate unique test emails to avoid conflicts with previous test runs
    test_id = str(uuid.uuid4())[:8]
    single_email = f"amendamax_single_{test_id}@test.com"
    bundle_email = f"amendamax_bundle_{test_id}@test.com"
    
    print("=== STARTING PRICING PACKAGE VALIDATION TESTS ===")
    
    # -------------------------------------------------------------
    # 1. TEST SINGLE SCAN PACKAGE ($1.99 / 1 CREDIT)
    # -------------------------------------------------------------
    print(f"\n[1] Testing SINGLE scan package for email: {single_email}")
    print("    Creating scan via /api/scan-url...")
    r = requests.post(f"{BASE_URL}/api/scan-url", json={"url": "https://example.com/single_test.jpg"})
    if r.status_code != 200:
        print(f"FAILED: Scan URL creation failed: {r.text}")
        sys.exit(1)
        
    scan_id1 = r.json()["scan_id"]
    print(f"    Scan created. Scan ID: {scan_id1}")
    
    print("    Paying via /api/pay-card with package='single'...")
    payload = {
        "scan_id": scan_id1,
        "email": single_email,
        "token_id": "tok_bypass_admin",
        "package": "single"
    }
    r = requests.post(f"{BASE_URL}/api/pay-card", json=payload)
    if r.status_code != 200:
        print(f"FAILED: Payment request failed: {r.text}")
        sys.exit(1)
        
    pay_data = r.json()
    print(f"    Response: {pay_data}")
    # 1 credit added, 1 credit used, remaining should be 0
    if not pay_data.get("success") or pay_data.get("credits_remaining") != 0:
        print("FAILED: Expected success and 0 remaining credits.")
        sys.exit(1)
        
    # Check credit endpoint
    r = requests.get(f"{BASE_URL}/api/credits/{single_email}")
    if r.status_code != 200 or r.json().get("credits_remaining") != 0:
        print(f"FAILED: Expected 0 remaining credits on credits endpoint. Response: {r.text}")
        sys.exit(1)
    print("    [OK] Single scan test passed (1 credit added, 1 consumed, 0 remaining).")
    
    # -------------------------------------------------------------
    # 2. TEST BUNDLE SCAN PACKAGE ($4.99 / 5 CREDITS)
    # -------------------------------------------------------------
    print(f"\n[2] Testing BUNDLE scan package for email: {bundle_email}")
    print("    Creating scan via /api/scan-url...")
    r = requests.post(f"{BASE_URL}/api/scan-url", json={"url": "https://example.com/bundle_test.jpg"})
    if r.status_code != 200:
        print(f"FAILED: Scan URL creation failed: {r.text}")
        sys.exit(1)
        
    scan_id2 = r.json()["scan_id"]
    print(f"    Scan created. Scan ID: {scan_id2}")
    
    print("    Paying via /api/pay-card with package='bundle'...")
    payload = {
        "scan_id": scan_id2,
        "email": bundle_email,
        "token_id": "tok_bypass_admin",
        "package": "bundle"
    }
    r = requests.post(f"{BASE_URL}/api/pay-card", json=payload)
    if r.status_code != 200:
        print(f"FAILED: Payment request failed: {r.text}")
        sys.exit(1)
        
    pay_data2 = r.json()
    print(f"    Response: {pay_data2}")
    # 5 credits added, 1 credit used, remaining should be 4
    if not pay_data2.get("success") or pay_data2.get("credits_remaining") != 4:
        print("FAILED: Expected success and 4 remaining credits.")
        sys.exit(1)
        
    # Check credit endpoint
    r = requests.get(f"{BASE_URL}/api/credits/{bundle_email}")
    if r.status_code != 200 or r.json().get("credits_remaining") != 4:
        print(f"FAILED: Expected 4 remaining credits on credits endpoint. Response: {r.text}")
        sys.exit(1)
    print("    [OK] Bundle scan test passed (5 credits added, 1 consumed, 4 remaining).")
    
    print("\n=== ALL TESTS PASSED SUCCESSFULLY! [OK] ===")

if __name__ == "__main__":
    test_pricing_packages()
