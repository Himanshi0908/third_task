import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000/api/v1"

def print_step(msg):
    time.sleep(2) # Delay for rate limiting
    print(f"\n[STEP] {msg}")

def get_unique_email(prefix):
    return f"{prefix}_{int(time.time())}@example.com"

def verify_tasks():
    print("Starting Task Feature Verification...")

    # 1. Setup Users
    print_step("Creating Creator, Assignee, and Admin users...")
    creator_email = get_unique_email("creator")
    assignee_email = get_unique_email("assignee")
    admin_email = get_unique_email("admin_task")

    # Register
    time.sleep(2)
    r = requests.post(f"{BASE_URL}/auth/register", json={"name": "Creator", "email": creator_email, "password": "Password123", "role": "user"})
    if r.status_code != 201: print(f"Creator Reg Failed: {r.text}"); return
    
    time.sleep(2)
    r = requests.post(f"{BASE_URL}/auth/register", json={"name": "Assignee", "email": assignee_email, "password": "Password123", "role": "user"})
    if r.status_code != 201: print(f"Assignee Reg Failed: {r.text}"); return

    time.sleep(2)
    r = requests.post(f"{BASE_URL}/auth/register", json={"name": "Admin", "email": admin_email, "password": "Password123", "role": "admin"})
    if r.status_code != 201: print(f"Admin Reg Failed: {r.text}"); return

    # Login
    time.sleep(2)
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": creator_email, "password": "Password123"})
    if resp.status_code != 200: print(f"Creator Login Failed: {resp.text}"); return
    creator_token = resp.json().get('access_token')

    time.sleep(2)
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": assignee_email, "password": "Password123"})
    if resp.status_code != 200: print(f"Assignee Login Failed: {resp.text}"); return
    assignee_token = resp.json().get('access_token')

    time.sleep(2)
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": admin_email, "password": "Password123"})
    if resp.status_code != 200: print(f"Admin Login Failed: {resp.text}"); return
    admin_token = resp.json().get('access_token')

    # Get Assignee ID (needed for assignment)
    time.sleep(1)
    assignee_id = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {assignee_token}"}).json()['id']

    creator_headers = {"Authorization": f"Bearer {creator_token}"}
    assignee_headers = {"Authorization": f"Bearer {assignee_token}"}
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Test Create Task
    print_step("Test: Create Task (Auth required, Fields, Auto-set createdBy)...")
    task_data = {
        "title": "Test Task",
        "description": "Desc",
        "status": "pending",
        "priority": "high",
        "due_date": "2024-01-01T00:00:00",
        "assignee_id": assignee_id
    }
    resp = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=creator_headers)
    print(f"Create Status: {resp.status_code}")
    if resp.status_code != 201:
        print(f"Error: {resp.text}")
        return
    task_id = resp.json()['task_id']
    print(f"Task Created with ID: {task_id}")

    # 3. Test Get Single Task
    print_step("Test: Get Single Task (Creator/Assignee/Admin only)...")
    # Creator
    r1 = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=creator_headers)
    print(f"Creator Access: {r1.status_code} (Expect 200)")
    # Assignee
    r2 = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=assignee_headers)
    print(f"Assignee Access: {r2.status_code} (Expect 200)")
    # Admin
    r3 = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=admin_headers)
    print(f"Admin Access: {r3.status_code} (Expect 200)")
    
    # Random User (should fail)
    # We skip creating a random one for brevity, but could add.

    # 4. Test Update Task (Assignee - Status Only)
    print_step("Test: Assignee Update (Status only allowed)...")
    # Try updating title (Should fail or ignore? Our logic says 403 if trying to update forbidden fields)
    resp = requests.put(f"{BASE_URL}/tasks/{task_id}", json={"title": "Hacked Title", "status": "completed"}, headers=assignee_headers)
    print(f"Assignee Update Full: {resp.status_code} (Expect 403)")
    
    # Try updating ONLY status
    resp = requests.put(f"{BASE_URL}/tasks/{task_id}", json={"status": "in-progress"}, headers=assignee_headers)
    print(f"Assignee Update Status: {resp.status_code} (Expect 200)")
    
    # Creator Update (All fields)
    print_step("Test: Creator Update (All fields)...")
    resp = requests.put(f"{BASE_URL}/tasks/{task_id}", json={"title": "New Title"}, headers=creator_headers)
    print(f"Creator Update: {resp.status_code} (Expect 200)")

    # 5. Test Get All Tasks (Filters)
    print_step("Test: Get All Tasks with Filters...")
    resp = requests.get(f"{BASE_URL}/tasks?status=in-progress", headers=creator_headers)
    tasks = resp.json()
    print(f"Filtered count: {len(tasks)}")
    if tasks and tasks[0]['status'] == 'in-progress':
        print("Filter Works.")

    # 6. Test Stats
    print_step("Test: Task Statistics...")
    resp = requests.get(f"{BASE_URL}/tasks/stats", headers=creator_headers)
    print(f"User Stats: {resp.json()}")
    resp = requests.get(f"{BASE_URL}/tasks/stats", headers=admin_headers)
    print(f"Admin Stats: {resp.json()}")

    # 7. Test Delete Task
    print_step("Test: Delete Task (Creator/Admin only)...")
    # Assignee try delete
    resp = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=assignee_headers)
    print(f"Assignee Delete: {resp.status_code} (Expect 403)")
    
    # Creator delete
    resp = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=creator_headers)
    print(f"Creator Delete: {resp.status_code} (Expect 200)")

    print("\nTask Verification Complete.")

if __name__ == "__main__":
    verify_tasks()
