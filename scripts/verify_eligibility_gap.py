import sys
import os
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import User, Scheme, db
from backend.security import hash_password

def verify_gap_analysis():
    app = create_app()
    
    with app.app_context():
        # 1. Find a target scheme to test against
        # Look for a scheme with age or income limit
        target_scheme = Scheme.query.filter(Scheme.max_age.isnot(None)).first()
        if not target_scheme:
            print("No suitable scheme found for testing age gap.")
            return
            
        print(f"Target Scheme: {target_scheme.name} (Max Age: {target_scheme.max_age})")
        
        # 2. Create a user who is SLIGHTLY over the age limit
        # Gap should be <= 2 years
        test_age = target_scheme.max_age + 1
        
        email = f"gap_test_{int(datetime.now().timestamp())}@example.com"
        user = User(
            name="Gap Tester",
            email=email,
            password_hash=hash_password("password123"),
            age=test_age,
            gender="Male", # Assume scheme allows Male or All, if not we might fail eligibility on gender
            state="Central", # Assume Central or matching state
            income=50000,
            category="General"
        )
        
        # Adjust user to match scheme hard criteria if needed
        if target_scheme.gender_specific and target_scheme.gender_specific != "All":
            user.gender = target_scheme.gender_specific
        if target_scheme.state and target_scheme.state != "Central":
            user.state = target_scheme.state
        if target_scheme.category_specific and "General" not in target_scheme.category_specific:
             # Just pick the first category allowed
             import re
             cats = re.findall(r"['\"](.*?)['\"]", target_scheme.category_specific)
             if cats:
                 user.category = cats[0]
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Created Test User: {user.email} (Age: {user.age})")
        
        # 3. Login to get token
        response = requests.post('http://localhost:5000/api/login', json={
            'email': email,
            'password': 'password123'
        })
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
            
        token = response.json()['token']
        
        # 4. Fetch Recommendations
        print("Fetching recommendations...")
        response = requests.get('http://localhost:5000/api/schemes/recommended', headers={
            'Authorization': f'Bearer {token}'
        })
        
        if response.status_code != 200:
            print(f"Recommendations failed: {response.text}")
            return
            
        data = response.json()
        
        # 5. Verify Results
        print("\n--- Verification Results ---")
        eligible_count = len(data.get('schemes', []))
        almost_count = len(data.get('almost_eligible', []))
        
        print(f"Eligible Schemes: {eligible_count}")
        print(f"Almost Eligible Schemes: {almost_count}")
        
        found_target = False
        for item in data.get('almost_eligible', []):
            print(f"\nScheme: {item['name']}")
            print(f"Score: {item['similarity_score']}")
            print(f"Gap Reason: {item.get('gap_reason')}")
            
            if 'alternative' in item:
                print(f"Alternative Suggested: {item['alternative']['name']}")
            else:
                print("No alternative suggested.")
                
            if item['name'] == target_scheme.name:
                found_target = True
                
        if found_target:
            print("\nSUCCESS: Target scheme found in almost eligible list with correct gap!")
        else:
            print("\nWARNING: Target scheme not found in almost eligible list. Check ML threshold or gap logic.")
            
        # Cleanup
        db.session.delete(user)
        db.session.commit()

if __name__ == "__main__":
    verify_gap_analysis()
