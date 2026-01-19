import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000/api/v1"

def print_step(msg):
    time.sleep(2) 
    print(f"\n[STEP] {msg}")

def get_unique_email(prefix):
    return f"{prefix}_{int(time.time())}@example.com"

def verify_admin():
    print("Starting Admin Feature Verification...")

    # 1. Create & Login Admin
    print_step("Setting up Admin...")
    admin_email = get_unique_email("admin_test")
    requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Admin Tester", "email": admin_email, "password": "Password123", "role": "admin"
    })
    
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": admin_email, "password": "Password123"})
    if resp.status_code != 200:
        print(f"Admin Login Failed: {resp.text}")
        return
    admin_token = resp.json()['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("Admin logged in.")

    # 2. Create Target User
    print_step("Setting up Target User...")
    user_email = get_unique_email("target_user")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Target User", "email": user_email, "password": "Password123"
    })
    
    # We need the User ID. Since we are admin, we can get it from the list.
    print_step("Getting User List (Admin)...")
    resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    print(f"Status: {resp.status_code}")
    users = resp.json()
    
    # Verify Password Exclusion
    if users and 'password' in users[0]:
        print("FAILED: Password field exposed in API!")
    else:
        print("SUCCESS: Password field check passed.")

    target_user = next((u for u in users if u['email'] == user_email), None)
    if not target_user:
        print("FAILED: Could not find created target user.")
        return
    
    target_id = target_user['id']
    print(f"Target User ID: {target_id}, Role: {target_user['role']}")

    # 3. Test Update Role
    print_step(f"Updating ID {target_id} role to 'admin'...")
    resp = requests.patch(f"{BASE_URL}/admin/users/{target_id}/role", 
                          json={"role": "admin"}, 
                          headers=admin_headers)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    
    # Verify Update
    resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    updated_user = next((u for u in resp.json() if u['id'] == target_id), None)
    if updated_user['role'] == 'admin':
        print("SUCCESS: Role updated to admin.")
    else:
        print(f"FAILED: Role update failed. Current: {updated_user['role']}")

    # 4. Test Delete User
    print_step(f"Deleting ID {target_id}...")
    resp = requests.delete(f"{BASE_URL}/admin/users/{target_id}", headers=admin_headers)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    # Verify Deletion
    resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    deleted_user = next((u for u in resp.json() if u['id'] == target_id), None)
    if deleted_user is None:
        print("SUCCESS: User deleted.")
    else:
        print("FAILED: User still exists in list.")

if __name__ == "__main__":
    verify_admin()
