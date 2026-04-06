import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000/api'

def run_test(name, user_profile, expected_scheme_id, expect_present=True):
    print(f"\n--- Test: {name} ---")
    
    # Register/Login with unique email
    timestamp = int(datetime.now().timestamp())
    email = f"gap_test_{timestamp}@example.com"
    password = "Password123"
    
    profile = {
        'name': 'Gap Tester',
        'email': email,
        'password': password,
        'state': 'Delhi',
        # Defaults, overridden by user_profile
        'age': 25,
        'gender': 'Male',
        'income': 100000,
        'category': 'General'
    }
    profile.update(user_profile)
    
    print(f"Registering user with profile: {json.dumps(user_profile, indent=2)}")
    requests.post(f'{BASE_URL}/register', json=profile)
    
    resp = requests.post(f'{BASE_URL}/login', json={'email': email, 'password': password})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return False
        
    token = resp.json()['token']
    
    # Get Recommendations
    print("Fetching recommendations...")
    headers = {'Authorization': f'Bearer {token}'}
    rec_resp = requests.get(f'{BASE_URL}/schemes/recommended?limit=50', headers=headers)
    
    if rec_resp.status_code != 200:
        print(f"Failed to get recommendations: {rec_resp.text}")
        return False
        
    data = rec_resp.json()
    almost_eligible = data.get('almost_eligible', [])
    
    print(f"Almost Eligible Count: {len(almost_eligible)}")
    
    found = False
    for item in almost_eligible:
        s = item # The item IS the scheme dict
        if s['id'] == expected_scheme_id:
            found = True
            print(f"✅ Found Expected Scheme: {s['name']}")
            print(f"   Gap Reason: {s['gap_reason']}")
            if s.get('alternative'):
                print(f"   Alternative Suggested: {s['alternative']['name']}")
            break
            
    if expect_present:
        if found:
            print("✅ TEST PASSED (Scheme Found)")
            return True
        else:
            print("❌ TEST FAILED (Scheme NOT Found)")
            return False
    else:
        if not found:
            print("✅ TEST PASSED (Scheme NOT Found as expected)")
            return True
        else:
            print("❌ TEST FAILED (Scheme Found but should not be)")
            return False

# Test 1: Income Gap (Scheme 4, Max Income 200k, User 220k)
run_test(
    "Income Gap (Within 30%)",
    {'category': 'Minority', 'income': 220000},
    4,
    expect_present=True
)

# Test 2: Income Too High (Scheme 4, Max Income 200k, User 300k)
run_test(
    "Income Gap (Too High)",
    {'category': 'Minority', 'income': 300000},
    4,
    expect_present=False
)

# Test 3: Age Gap (Scheme 5, Max Age 10, User 11)
run_test(
    "Age Gap (Within 2 Years)",
    {'gender': 'Female', 'age': 11, 'category': 'General'},
    5,
    expect_present=True
)
