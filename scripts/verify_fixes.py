import os
import sys
import json
import logging

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import db, User, Scheme
from backend.ml_engine import MLRecommendationEngine
from backend.security import hash_password
from sqlalchemy import func

def verify_fixes():
    app = create_app('development')
    
    with app.app_context():
        print("=== 1. Verifying Scheme Deduplication ===")
        # Check for duplicates by name
        duplicates = db.session.query(Scheme.name, func.count(Scheme.id))\
            .group_by(Scheme.name)\
            .having(func.count(Scheme.id) > 1)\
            .all()
        
        if duplicates:
            print(f"❌ FAIL: Found {len(duplicates)} duplicates:")
            for name, count in duplicates:
                print(f"  - {name}: {count} copies")
        else:
            print("✅ PASS: No duplicate schemes found.")

        print("\n=== 2. Verifying Recommender ===")
        # Create a dummy user
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            user = User(name="Test User", email="test@example.com", income=50000, age=25, gender="Male", state="Delhi", category="General", password_hash=hash_password("password"))
            db.session.add(user)
            db.session.commit()
            print("Created test user.")
        
        ml_engine = MLRecommendationEngine()
        recommendations = ml_engine.recommend_schemes(user, limit=5)
        
        print(f"Top 5 Recommendations for {user.name} ({user.gender}, {user.state}):")
        seen_names = set()
        has_dupes = False
        for scheme, score in recommendations:
            print(f"  - {scheme.name} (Score: {score:.4f})")
            if scheme.name in seen_names:
                has_dupes = True
            seen_names.add(scheme.name)
        
        if has_dupes:
            print("❌ FAIL: Recommender returned duplicates.")
        else:
            print("✅ PASS: Recommender results are unique.")

        print("\n=== 3. Verifying Chat Endpoint ===")
        # Simulate chat request
        with app.test_client() as client:
            # Login to get token
            login_resp = client.post('/api/login', json={
                'email': 'test@example.com',
                'password': 'password'
            })
            if login_resp.status_code == 200:
                token = login_resp.json['token']
                headers = {'Authorization': f'Bearer {token}'}
                
                # Chat message
                chat_resp = client.post('/api/chat', json={'message': 'Hello Aditi'}, headers=headers)
                if chat_resp.status_code == 200:
                    print(f"✅ PASS: Chat response: {chat_resp.json['response']}")
                else:
                    print(f"❌ FAIL: Chat endpoint failed: {chat_resp.status_code} - {chat_resp.data}")
            else:
                print(f"❌ FAIL: Login failed: {login_resp.status_code} - {login_resp.data}")

        print("\n=== 4. Verifying Profile Logic ===")
        # Check if user profile can be fetched
        with app.test_client() as client:
             # Login to get token (reuse if possible, but simpler to login again)
            login_resp = client.post('/api/login', json={
                'email': 'test@example.com',
                'password': 'password'
            })
            token = login_resp.json['token']
            headers = {'Authorization': f'Bearer {token}'}
            
            profile_resp = client.get('/api/profile', headers=headers)
            if profile_resp.status_code == 200:
                print("✅ PASS: Profile fetched successfully.")
            else:
                print(f"❌ FAIL: Profile fetch failed: {profile_resp.status_code}")

if __name__ == "__main__":
    verify_fixes()
