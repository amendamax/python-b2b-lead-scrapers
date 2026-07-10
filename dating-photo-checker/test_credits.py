import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_credits_flow():
    print("[1] Creating first scan via /api/scan-url...")
    r = requests.post(f"{BASE_URL}/api/scan-url", json={"url": "https://example.com/portrait1.jpg"})
    if r.status_code != 200:
        print(f"FAILED: Scan URL creation failed: {r.text}")
        sys.exit(1)
    
    scan_data1 = r.json()
    scan_id1 = scan_data1["scan_id"]
    print(f"    First scan created. Scan ID: {scan_id1}")
    
    print("\n[2] Paying for first scan via /api/pay-card (which adds 5 credits and consumes 1)...")
    payload = {
        "scan_id": scan_id1,
        "email": "vasile@test.com",
        "token_id": "tok_bypass_admin"
    }
    r = requests.post(f"{BASE_URL}/api/pay-card", json=payload)
    if r.status_code != 200:
        print(f"FAILED: Payment failed: {r.text}")
        sys.exit(1)
        
    pay_data = r.json()
    print(f"    Payment response: {pay_data}")
    if not pay_data.get("success") or pay_data.get("credits_remaining") != 4:
        print("FAILED: Expected success and 4 remaining credits.")
        sys.exit(1)
        
    print("\n[3] Checking /api/credits/vasile@test.com...")
    r = requests.get(f"{BASE_URL}/api/credits/vasile@test.com")
    if r.status_code != 200:
        print(f"FAILED: Get credits failed: {r.text}")
        sys.exit(1)
        
    credits_data = r.json()
    print(f"    Credits response: {credits_data}")
    if credits_data.get("credits_remaining") != 4:
        print("FAILED: Expected remaining credits to be 4.")
        sys.exit(1)
        
    print("\n[4] Creating second scan via /api/scan-url...")
    r = requests.post(f"{BASE_URL}/api/scan-url", json={"url": "https://example.com/portrait2.jpg"})
    scan_data2 = r.json()
    scan_id2 = scan_data2["scan_id"]
    print(f"    Second scan created. Scan ID: {scan_id2}")
    
    print("\n[5] Unlocking second scan using credit via /api/use-credit...")
    payload = {
        "scan_id": scan_id2,
        "email": "vasile@test.com"
    }
    r = requests.post(f"{BASE_URL}/api/use-credit", json=payload)
    if r.status_code != 200:
        print(f"FAILED: Use credit failed: {r.text}")
        sys.exit(1)
        
    use_credit_data = r.json()
    print(f"    Use credit response: {use_credit_data}")
    if not use_credit_data.get("success") or use_credit_data.get("credits_remaining") != 3:
        print("FAILED: Expected success and 3 remaining credits.")
        sys.exit(1)
        
    print("\n[6] Checking /api/credits/vasile@test.com again...")
    r = requests.get(f"{BASE_URL}/api/credits/vasile@test.com")
    credits_data2 = r.json()
    print(f"    Credits response: {credits_data2}")
    if credits_data2.get("credits_remaining") != 3:
        print("FAILED: Expected remaining credits to be 3.")
        sys.exit(1)
        
    print("\n[7] Verifying that get_results for unlocked scan returns credit balance...")
    r = requests.get(f"{BASE_URL}/api/results/{scan_id2}")
    results_data = r.json()
    print(f"    Results response: {results_data}")
    if results_data.get("credits_remaining") != 3 or results_data.get("email") != "vasile@test.com":
        print("FAILED: Expected email and remaining credits to match.")
        sys.exit(1)

    print("\n[8] Verifying that user with no credits fails to unlock...")
    r = requests.post(f"{BASE_URL}/api/scan-url", json={"url": "https://example.com/portrait3.jpg"})
    scan_id3 = r.json()["scan_id"]
    
    payload = {
        "scan_id": scan_id3,
        "email": "unknown@test.com"
    }
    r = requests.post(f"{BASE_URL}/api/use-credit", json=payload)
    print(f"    Failed request response: status_code={r.status_code}, body={r.text}")
    if r.status_code != 400:
        print("FAILED: Expected HTTP 400 Bad Request.")
        sys.exit(1)
        
    print("\nALL TESTS PASSED SUCCESSFULLY! [OK]")

if __name__ == "__main__":
    test_credits_flow()
