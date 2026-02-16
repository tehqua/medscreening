import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_health():
    print("1. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Health: {response.json()}")
    print()

def test_login():
    print("2. Testing login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"patient_id": "Adam631_Cronin387_aff8f143-2375-416f-901d-b0e4c73e3e58"}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Session: {data['session_id']}")
    print(f"   Token: {data['access_token'][:50]}...")
    print()
    return data["access_token"]

def test_chat(token):
    print("3. Testing chat...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/chat/message",
        headers=headers,
        json={"message": "I have a headache for 2 days"}
    )
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Response: {data['response'][:100]}...")
    print(f"   Emergency: {data['metadata'].get('emergency_detected')}")
    print()

def test_history(token):
    print("4. Testing conversation history...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/chat/history", headers=headers)
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total messages: {data['total_messages']}")
    print()

def test_upload_limits():
    print("5. Testing upload limits...")
    response = requests.get(f"{BASE_URL}/upload/limits")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Image max: {data['image']['max_size_mb']}MB")
    print(f"   Audio max: {data['audio']['max_size_mb']}MB")
    print()

if __name__ == "__main__":
    print("Starting Backend Tests...\n")
    print("=" * 60)
    
    try:
        test_health()
        token = test_login()
        test_chat(token)
        test_history(token)
        test_upload_limits()
        
        print("=" * 60)
        print("\nAll tests PASSED!")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to backend!")
        print("Make sure server is running: python main.py")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()