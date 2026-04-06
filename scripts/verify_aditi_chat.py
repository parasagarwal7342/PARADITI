import requests
import json
import sys

from datetime import datetime

# Define base URL
BASE_URL = 'http://localhost:5000/api'

def get_auth_token():
    # Login to get token
    try:
        # Create a temp user if needed or just use one
        # Use timestamp to ensure uniqueness
        timestamp = int(datetime.now().timestamp())
        email = f"chat_test_{timestamp}@example.com"
        password = "Password123" # Strong password for validation
        
        print(f"Attempting to register user: {email}")
        
        # Register
        reg_response = requests.post(f'{BASE_URL}/register', json={
            'name': 'Chat Tester',
            'email': email,
            'password': password,
            'age': 25,
            'state': 'Delhi',
            'gender': 'Male',
            'income': 100000,
            'category': 'General'
        })
        
        if reg_response.status_code not in [201, 200]: 
            # If 400, it might be user exists or validation error.
            # But we generated a unique email, so it's likely validation.
            print(f"Registration failed: {reg_response.status_code} - {reg_response.text}")
            if reg_response.status_code != 400: # Proceed only if it's potentially "user exists" which we handled poorly before
                 return None
            # If 400, check if it's "Email already registered"
            if "already registered" not in reg_response.text:
                 return None
            
        print("Registration successful or user exists. Attempting login...")
        
        # Login
        response = requests.post(f'{BASE_URL}/login', json={
            'email': email,
            'password': password
        })
        
        if response.status_code == 200:
            print("Login successful!")
            return response.json()['token']
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def test_chat(token):
    headers = {'Authorization': f'Bearer {token}'}
    
    test_cases = [
        {
            "message": "I am a student looking for scholarship",
            "expected_intent": "education",
            "expected_lang": "en",
            "desc": "English Education Intent"
        },
        {
            "message": "Mujhe kheti ke liye scheme chahiye",
            "expected_intent": "agriculture",
            "expected_lang": "hi",
            "desc": "Hindi Agriculture Intent"
        },
        {
            "message": "Main business shuru karna chahta hu, mujhe loan chahiye",
            "expected_intent": "business",
            "expected_lang": "hi",
            "desc": "Hinglish Business Intent"
        },
        {
            "message": "Vanakkam enaku veedu kattavum",
            "expected_intent": "housing",
            "expected_lang": "ta",
            "desc": "Tamil Housing Intent"
        },
        {
            "message": "Nomoshkar ami byabsha shuru korbo",
            "expected_intent": "business",
            "expected_lang": "bn",
            "desc": "Bengali Business Intent"
        },
        {
            "message": "Hello Aditi",
            "expected_intent": None,
            "expected_lang": "en", # Default
            "desc": "Greeting / No Intent"
        }
    ]
    
    print("\n--- Testing Aditi Chatbot ---")
    
    for case in test_cases:
        print(f"\nTesting: {case['desc']}")
        print(f"Input: {case['message']}")
        
        try:
            response = requests.post(
                f'{BASE_URL}/chat',
                headers=headers,
                json={'message': case['message']}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data['response']}")
                print(f"Detected Intent: {data.get('intent')}")
                print(f"Detected Lang: {data.get('lang')}")
                
                # Verification
                if data.get('intent') == case['expected_intent']:
                    print("✅ Intent Match")
                else:
                    print(f"❌ Intent Mismatch (Expected: {case['expected_intent']})")
                    
                if data.get('lang') == case['expected_lang']:
                    print("✅ Lang Match")
                else:
                    print(f"❌ Lang Mismatch (Expected: {case['expected_lang']})")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    token = get_auth_token()
    if token:
        test_chat(token)
    else:
        print("Could not get auth token, skipping chat tests.")
