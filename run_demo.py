"""
PayGuard Crew - Complete Demo (Windows Compatible)
Includes correct data format and complete test workflow
"""
import json
import requests
import sys
from datetime import datetime, timedelta

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "demo-test-key-12345"

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_result(success, message):
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {message}")

# Use past timestamp to avoid validation error (use yesterday)
past_time = "2026-07-07T10:00:00"

# Complete test data (matches schema requirements)
DEMO_TRANSACTIONS = {
    "low_risk": {
        "transaction_id": "TXN_LOW_001",
        "user_id": "USER_ALICE",
        "merchant_id": "MERCHANT_001",
        "amount": 100.00,
        "currency": "USD",
        "account_age_days": 365,
        "transaction_frequency_1h": 1,
        "ip_location_status": "normal",
        "device_status": "normal",
        "kyc_status": "verified",
        "merchant_risk_level": "low",
        "is_blacklisted": False,
        "timestamp": past_time
    },
    "medium_risk": {
        "transaction_id": "TXN_MED_002",
        "user_id": "USER_BOB",
        "merchant_id": "MERCHANT_002",
        "amount": 5000.00,
        "currency": "USD",
        "account_age_days": 30,
        "transaction_frequency_1h": 5,
        "ip_location_status": "abnormal",
        "device_status": "normal",
        "kyc_status": "basic_verified",
        "merchant_risk_level": "medium",
        "is_blacklisted": False,
        "timestamp": past_time
    },
    "high_risk": {
        "transaction_id": "TXN_HIGH_003",
        "user_id": "USER_CHARLIE",
        "merchant_id": "MERCHANT_003",
        "amount": 25000.00,
        "currency": "USD",
        "account_age_days": 3,
        "transaction_frequency_1h": 15,
        "ip_location_status": "abnormal",
        "device_status": "abnormal",
        "kyc_status": "unverified",
        "merchant_risk_level": "high",
        "is_blacklisted": False,
        "timestamp": past_time
    }
}

def test_health():
    """Test 1: Health Check"""
    print_header("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Health check passed - Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Environment: {data.get('environment')}")
            return True
        else:
            print_result(False, f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Cannot connect to server: {e}")
        print("\nPlease start the server first:")
        print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        return False

def test_audit_transaction(tx_data, label):
    """Test transaction audit"""
    print_header(f"Test: {label}")
    try:
        headers = {"x-api-key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/audit/transaction",
            json=tx_data,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Audit completed for {tx_data['transaction_id']}")
            print(f"  Amount: ${tx_data['amount']:.2f} {tx_data['currency']}")
            print(f"  Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"  Risk Score: {data.get('total_score', 0)}")
            print(f"  Recommendation: {data.get('recommendation', 'N/A')}")

            rules = data.get('matched_rules', [])
            if rules:
                print(f"\n  Matched {len(rules)} rule(s):")
                for rule in rules[:3]:
                    print(f"    - {rule.get('rule_name')}: {rule.get('description', '')[:60]}")

            return data
        else:
            print_result(False, f"Audit failed: {response.status_code}")
            try:
                error_text = response.text.encode('ascii', 'ignore').decode('ascii')
                print(f"  Error: {error_text[:200]}")
            except:
                print(f"  Error: (encoding issue)")
            return None
    except requests.exceptions.RequestException as e:
        print_result(False, f"Request failed: {str(e)[:100]}")
        return None

def test_batch_audit():
    """Test batch audit"""
    print_header("Test: Batch Audit (3 transactions)")
    try:
        # Use unique IDs for batch to avoid conflicts
        batch_txns = []
        for i, (key, tx) in enumerate(DEMO_TRANSACTIONS.items()):
            tx_copy = tx.copy()
            tx_copy['transaction_id'] = f"BATCH_{tx['transaction_id']}_{i}"
            batch_txns.append(tx_copy)

        batch_data = {
            "batch_id": f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "transactions": batch_txns
        }

        headers = {"x-api-key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/audit/batch",
            json=batch_data,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            print_result(True, "Batch audit completed")
            print(f"  Batch ID: {data.get('batch_id')}")
            print(f"  Total: {data.get('total_transactions', 0)}")
            print(f"  Completed: {data.get('completed', 0)}")
            print(f"  Failed: {data.get('failed', 0)}")

            summary = data.get('summary', {})
            if summary:
                print(f"\n  Risk Distribution:")
                for level, count in summary.items():
                    print(f"    {level}: {count}")

            return data
        else:
            print_result(False, f"Batch audit failed: {response.status_code}")
            try:
                error_text = response.text.encode('ascii', 'ignore').decode('ascii')
                print(f"  Error: {error_text[:200]}")
            except:
                print(f"  Error: (encoding issue)")
            return None
    except requests.exceptions.RequestException as e:
        print_result(False, f"Request failed: {str(e)[:100]}")
        return None

def test_audit_list():
    """Test audit list"""
    print_header("Test: Query Audit History")
    try:
        headers = {"x-api-key": API_KEY}
        response = requests.get(
            f"{BASE_URL}/api/audit/list?limit=5",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            items = data.get('items', [])
            print_result(True, f"Found {total} audit records")

            if items:
                print(f"\n  Recent audits:")
                for item in items[:3]:
                    print(f"    - {item.get('transaction_id')}: {item.get('risk_level')} risk")

            return data
        else:
            print_result(False, f"Query failed: {response.status_code}")
            return None
    except Exception as e:
        print_result(False, f"Request failed: {e}")
        return None

def test_review_workflow():
    """Test review workflow"""
    print_header("Test: Create Review Task")
    try:
        review_data = {
            "transaction_id": "TXN_HIGH_003",
            "reviewer": "analyst_alice",
            "priority": "high",
            "notes": "High-risk transaction requires manual review"
        }

        headers = {"x-api-key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/review/create",
            json=review_data,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print_result(True, "Review task created")
            print(f"  Review ID: {data.get('review_id', 'N/A')}")
            print(f"  Transaction: {review_data['transaction_id']}")
            print(f"  Assigned to: {review_data['reviewer']}")
            print(f"  Priority: {review_data['priority']}")
            return data
        else:
            print_result(False, f"Create review failed: {response.status_code}")
            try:
                error_text = response.text.encode('ascii', 'ignore').decode('ascii')
                print(f"  Error: {error_text[:200]}")
            except:
                print(f"  Error: (encoding issue)")
            return None
    except requests.exceptions.RequestException as e:
        print_result(False, f"Request failed: {str(e)[:100]}")
        return None

def main():
    """Run complete demo"""
    print("\n" + "="*70)
    print("  PayGuard Crew - Complete Demo")
    print("="*70)
    print(f"\nBase URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Health Check
    if not test_health():
        print("\n[STOP] Server is not running. Please start it first.")
        return

    # Test 2: Low Risk Transaction
    test_audit_transaction(DEMO_TRANSACTIONS["low_risk"], "Low Risk Transaction")

    # Test 3: Medium Risk Transaction
    test_audit_transaction(DEMO_TRANSACTIONS["medium_risk"], "Medium Risk Transaction")

    # Test 4: High Risk Transaction
    test_audit_transaction(DEMO_TRANSACTIONS["high_risk"], "High Risk Transaction")

    # Test 5: Batch Audit
    test_batch_audit()

    # Test 6: Query History
    test_audit_list()

    # Test 7: Review Workflow
    test_review_workflow()

    # Summary
    print_header("Demo Completed")
    print_result(True, "All tests completed!")
    print(f"\nNext steps:")
    print(f"  1. View API docs: {BASE_URL}/docs")
    print(f"  2. Check database: payguard_crew.db")
    print(f"  3. Export reports via API")

if __name__ == "__main__":
    main()
