import requests
import sys
import time

BASE_URL = "http://127.0.0.1:5000/api/v1"

def print_step(msg):
    time.sleep(2.5) # Increased delay to avoid rate limits
    print(f"\n[STEP] {msg}")

def get_unique_email(prefix):
    return f"{prefix}_{int(time.time())}@example.com"

def verify():
    # 1. Register User (Admin) - Now testing direct role registration
    print_step("Registering Admin User directly...")
    admin_email = get_unique_email("admin")
    admin_data = {
        "name": "Admin User", 
        "email": admin_email, 
        "password": "Password123",
        "role": "admin"
    }
    resp = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    # 1.5 Register User (Default Role) - Testing that default is 'user'
    print_step("Registering Default User (No role specified)...")
    default_email = get_unique_email("default")
    default_user_data = {
        "name": "Default User", 
        "email": default_email, 
        "password": "Password123"
    }
    # Note: NOT sending 'role' field here
    resp = requests.post(f"{BASE_URL}/auth/register", json=default_user_data)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    
    # Verify default user is actually a user by logging in and checking /me
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": default_email, "password": "Password123"})
    if resp.status_code == 200:
       token = resp.json()['access_token']
       me_resp = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
       print(f"Default User Profile: {me_resp.json()}") # Should show role: user

    # 2. Login Admin
    print_step("Logging in Admin...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": admin_email, "password": "Password123"})
    if resp.status_code != 200:
        print("Login failed!")
        return
    admin_tokens = resp.json()
    admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    print("Login successful.")

    # 3. Create Normal User for Task testing
    print_step("Registering Normal User...")
    user_email = get_unique_email("user")
    user_data = {"name": "Test User", "email": user_email, "password": "Password123"}
    resp = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    print_step("Logging in Normal User...")
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": user_email, "password": "Password123"})
    user_tokens = resp.json()
    user_headers = {"Authorization": f"Bearer {user_tokens['access_token']}"}
    
    # 4. Create Task (User)
    print_step("Creating Task (User)...")
    task_data = {"title": "User Task", "description": "Do something", "priority": "high", "due_date": "2023-12-31T00:00:00"}
    resp = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=user_headers)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")
    task_id = resp.json().get('task_id')

    # 5. Get Tasks (User)
    print_step("Getting Tasks (User)...")
    resp = requests.get(f"{BASE_URL}/tasks", headers=user_headers)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    # 6. Admin Logic - Testing Admin Features
    print_step("Accessing Admin Route with User Token (Expect 403)...")
    resp = requests.get(f"{BASE_URL}/admin/users", headers=user_headers)
    print(f"Status: {resp.status_code}, Body: {resp.json()}")

    print_step("Accessing Admin Route with ADMIN Token (Expect 200)...")
    resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
    print(f"Status: {resp.status_code}")
    users = resp.json()
    print(f"Found {len(users)} users.")
    
    # Verify no password in response
    if users and 'password' in users[0]:
        print("FAILED: Password field found in user response!")
        return
    else:
        print("SUCCESS: Password field not present in response.")

    # Find the Normal User ID to test modification
    # We used 'user_email' variable earlier
    target_user = next((u for u in users if u['email'] == user_email), None)
    if target_user:
        target_user_id = target_user['id']
        print(f"Target User ID for Update/Delete: {target_user_id}")
        
        # 7. Update User Role
        print_step(f"Updating User {target_user_id} Role to 'admin'...")
        resp = requests.patch(f"{BASE_URL}/admin/users/{target_user_id}/role", 
                              json={"role": "admin"}, 
                              headers=admin_headers)
        print(f"Status: {resp.status_code}, Body: {resp.json()}")
        
        # Verify update
        resp = requests.get(f"{BASE_URL}/admin/users", headers=admin_headers)
        updated_user = next((u for u in resp.json() if u['id'] == target_user_id), None)
        print(f"User Role after update: {updated_user['role']}")

        # 8. Delete User
        print_step(f"Deleting User {target_user_id}...")
        resp = requests.delete(f"{BASE_URL}/admin/users/{target_user_id}", headers=admin_headers)
        print(f"Status: {resp.status_code}, Body: {resp.json()}")

        # Verify deletion (Login should fail)
        print_step("Attempting login with deleted user (Expect 401)...")
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": user_email, "password": "Password123"})
        print(f"Status: {resp.status_code}, Body: {resp.json()}")

    else:
        print("Could not find the Normal User in the list to test Update/Delete.")

    print("\nVerification script finished.")

if __name__ == "__main__":
    verify()
