"""
Example 1: Quickstart audit script using IsBrokerSafe SDK.
"""

from isbrokersafe import Client

def main():
    # Initialize client (uses anonymous tier if no key provided)
    client = Client()

    test_domains = [
        "interactivebrokers.com",
        "exness.com",
        "etoro.com",
        "fake-crypto-broker-example.xyz"
    ]

    print("=== ISBROKERSAFE REAL-TIME FORENSIC SCAN ===")
    for d in test_domains:
        try:
            res = client.check(d)
            status_icon = "🟢" if res.status == "SAFE" else "🔴"
            print(f"{status_icon} [{res.status}] {d.ljust(32)} Score: {str(res.safety_score).rjust(3)}/100 | Regulated: {res.is_regulated}")
            if res.warnings:
                for w in res.warnings:
                    print(f"   ⚠️ WARNING: {w.regulator.upper()} - {w.reason}")
        except Exception as e:
            print(f"❌ Error checking {d}: {e}")

if __name__ == "__main__":
    main()
