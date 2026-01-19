import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000/api/v1"

def print_step(msg):
    time.sleep(1) 
    print(f"\n[STEP] {msg}")

def verify_logout():
    print("Starting Logout Verification...")

    # 1. Login to get token
    print_step("Logging in...")
    # Use existing admin or create a temp one
    # For simplicity, let's try a known user if possible, or just register a temp one
    email = f"logout_test_{int(time.time())}@example.com"
    requests.post(f"{BASE_URL}/auth/register", json={"name": "Logout Tester", "email": email, "password": "Password123"})
    
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "Password123"})
    if resp.status_code != 200:
        print("Login failed")
        return
    token = resp.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Call Logout
    print_step("Calling Logout endpoint...")
    resp = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    if resp.status_code == 200:
        print("SUCCESS: Logout endpoint works.")
    else:
        print("FAILED: Logout endpoint failed.")

if __name__ == "__main__":
    verify_logout()
