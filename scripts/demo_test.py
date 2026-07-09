"""
PayGuard Crew Demo 测试脚本

演示所有核心功能：
1. 健康检查
2. 用户登录（JWT）
3. 单笔交易审计
4. 批量交易审计
5. 审核工作流
"""
import json
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "demo-test-key-12345"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.END}")

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

# 测试数据
DEMO_TRANSACTIONS = {
    "normal": {
        "transaction_id": "TXN_DEMO_001",
        "amount": 1000.00,
        "currency": "USD",
        "sender": {
            "user_id": "user_alice_001",
            "account": "alice@example.com",
            "country": "US",
            "ip": "192.168.1.100"
        },
        "receiver": {
            "user_id": "user_bob_001",
            "account": "bob@example.com",
            "country": "US",
            "ip": "192.168.1.101"
        },
        "metadata": {
            "device": "mobile",
            "source": "app"
        }
    },
    "high_risk": {
        "transaction_id": "TXN_DEMO_002",
        "amount": 50000.00,
        "currency": "USD",
        "sender": {
            "user_id": "user_charlie_002",
            "account": "charlie@example.com",
            "country": "NG",
            "ip": "41.203.72.1"
        },
        "receiver": {
            "user_id": "user_david_002",
            "account": "david@example.com",
            "country": "CN",
            "ip": "220.181.38.148"
        },
        "metadata": {
            "device": "desktop",
            "source": "web"
        }
    },
    "suspicious": {
        "transaction_id": "TXN_DEMO_003",
        "amount": 9999.00,
        "currency": "USD",
        "sender": {
            "user_id": "user_eve_003",
            "account": "eve@tempmail.com",
            "country": "RU",
            "ip": "95.142.192.1"
        },
        "receiver": {
            "user_id": "user_mallory_003",
            "account": "mallory@anonymail.org",
            "country": "KP",
            "ip": "175.45.176.1"
        },
        "metadata": {
            "device": "mobile",
            "source": "api"
        }
    }
}

def test_health():
    """Test health check"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health/health")
        if response.status_code == 200:
            print_success("Health check passed")
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Version: {data.get('version')}")
            print(f"Environment: {data.get('environment')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def test_login():
    """Test user login"""
    print_section("2. User Login (JWT)")
    try:
        # Note: routes have double prefix issue
        response = requests.post(
            f"{BASE_URL}/api/auth/auth/login",
            json={"username": "demo", "password": "demo123"}
        )
        if response.status_code == 200:
            print_success("Login successful")
            data = response.json()
            print(f"Access Token: {data.get('access_token', '')[:50]}...")
            return data.get('access_token')
        else:
            print_error(f"Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"Login request failed: {e}")
        return None

def test_single_audit(transaction_data, label):
    """Test single transaction audit"""
    print_section(f"3. Single Transaction Audit - {label}")
    try:
        headers = {"x-api-key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/audit/transaction",
            json=transaction_data,
            headers=headers
        )

        if response.status_code == 200:
            print_success(f"Audit completed: {transaction_data['transaction_id']}")
            data = response.json()
            print(f"Amount: {transaction_data['amount']} {transaction_data['currency']}")
            print(f"Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"Total Score: {data.get('total_score', 'N/A')}")
            print(f"Recommendation: {data.get('recommendation', 'N/A')}")

            # Show matched rules
            rules = data.get('matched_rules', [])
            if rules:
                print(f"\nMatched Rules: {len(rules)}")
                for rule in rules[:3]:  # Show first 3
                    print(f"  - {rule.get('rule_name')}: {rule.get('description', '')[:50]}")

            return data
        else:
            print_error(f"Audit failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"Audit request failed: {e}")
        return None

def test_batch_audit():
    """Test batch audit"""
    print_section("4. Batch Transaction Audit")
    try:
        batch_data = {
            "batch_id": f"BATCH_DEMO_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "transactions": list(DEMO_TRANSACTIONS.values())
        }

        headers = {"x-api-key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/audit/batch",
            json=batch_data,
            headers=headers
        )

        if response.status_code == 200:
            print_success(f"Batch audit completed")
            data = response.json()
            print(f"Batch ID: {data.get('batch_id')}")
            print(f"Total Transactions: {data.get('total_transactions', 0)}")
            print(f"Completed: {data.get('completed', 0)}")
            print(f"Failed: {data.get('failed', 0)}")

            # Risk distribution
            summary = data.get('summary', {})
            if summary:
                print(f"\nRisk Distribution:")
                for level, count in summary.items():
                    print(f"  {level}: {count}")

            return data
        else:
            print_error(f"Batch audit failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"Batch audit request failed: {e}")
        return None

def test_review_workflow():
    """Test review workflow"""
    print_section("5. Review Workflow")
    try:
        review_data = {
            "transaction_id": "TXN_DEMO_002",  # Use high-risk transaction
            "reviewer": "reviewer_alice",
            "priority": "high",
            "notes": "High amount cross-border transaction requiring manual review"
        }

        headers = {"x-api-key": API_KEY}
        response = requests.post(
            f"{BASE_URL}/api/review/create",
            json=review_data,
            headers=headers
        )

        if response.status_code == 200:
            print_success("Review task created successfully")
            data = response.json()
            print(f"Review ID: {data.get('review_id')}")
            print(f"Status: {data.get('status')}")
            print(f"Priority: {data.get('priority')}")
            return data
        else:
            print_error(f"Create review failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print_error(f"Review request failed: {e}")
        return None

def main():
    """Main demo function"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("PayGuard Crew - Demo Test")
    print(f"{'='*60}{Colors.END}\n")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")

    # 1. Health check
    if not test_health():
        print_error("\nServer not running. Please start the server:")
        print("python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        return

    # 2. Login test
    token = test_login()

    # 3. Single transaction audits (different risk levels)
    test_single_audit(DEMO_TRANSACTIONS["normal"], "Normal Transaction")
    test_single_audit(DEMO_TRANSACTIONS["high_risk"], "High Risk Transaction")
    test_single_audit(DEMO_TRANSACTIONS["suspicious"], "Suspicious Transaction")

    # 4. Batch audit
    test_batch_audit()

    # 5. Review workflow
    test_review_workflow()

    print_section("Demo Completed")
    print_success("All tests completed!")
    print(f"\nVisit Swagger docs for more APIs: {BASE_URL}/docs")

if __name__ == "__main__":
    main()
